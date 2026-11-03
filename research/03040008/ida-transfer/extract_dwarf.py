"""PS4 02020005 DWARF facts for the in-scope packet functions (spec 007 T004).

    uv run python extract_dwarf.py [--elf ELF] [--out dumps/ps4-dwarf.jsonl]
                                   [--ida-dump dumps/ps4-ida.jsonl] [--depth 3]

Scope: by default the ELF symbols ``cSeed*Connection::{OnPacket_,Send_}*`` and
``CPacket_*::{ReadPacket,WritePacket}`` plus their callees to ``--depth`` (direct ``call``/``jmp``
targets decoded with capstone); with ``--ida-dump`` every function VA of a PS4 ``extract_ida.py``
dump instead (its input sha256 must equal the ELF's).

Per function (by address): qualified name, linkage name, prototype, parameters, locals with their
lexical block and DWARF location expression (``exprloc`` or ``.debug_loc`` list), the frame base,
and the inlined subroutine calls (callee, call file/line, ranges, nesting). Per type reached from
those (through pointers, typedefs, arrays, members and bases): the definition with members
(offset, size, type), bases, vtable pointer members and virtual slots, enumerators, or the typedef
target. Library: pyelftools (DWARF), capstone (call targets). The ELF must be the staged copy
whose sha256 equals ``elf_sha256`` in ``inline-chains.orbis-addr2line.tsv``.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import sys
import time
from pathlib import Path

from extract_ida import scope_closure, write_jsonl

SCRIPT_VERSION = "1"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ELF_DIR = REPO / "binaries/PS4_02020005/elf-dumps"
DEFAULT_ELF = ELF_DIR / ".staging/input/DDOORBIS.elf"
DEFAULT_CHAINS = ELF_DIR / "dwarf/inline-chains.orbis-addr2line.tsv"

ROOT_SYMBOL_PATTERNS = (
    r"^_ZN\d+cSeed\w*?Connection\d+(?:OnPacket_|Send_)",
    r"\d+CPacket_\w+?\d+(?:Read|Write)PacketE",
)
_MODIFIERS = {
    "DW_TAG_pointer_type": "*", "DW_TAG_reference_type": "&", "DW_TAG_rvalue_reference_type": "&&",
    "DW_TAG_const_type": "const", "DW_TAG_volatile_type": "volatile", "DW_TAG_restrict_type": "restrict",
}
_RECORDS = ("DW_TAG_structure_type", "DW_TAG_class_type", "DW_TAG_union_type")
_SCOPES = _RECORDS + ("DW_TAG_namespace", "DW_TAG_enumeration_type")


# --- pure helpers -------------------------------------------------------------------------------

def is_root_symbol(mangled: str, patterns=ROOT_SYMBOL_PATTERNS) -> bool:
    return any(re.search(p, mangled) for p in patterns)


def read_chains_sha(path: Path) -> str:
    """``elf_sha256`` from the inline-chains TSV header."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith(("#", "format", "elf_sha256", "tool", "flags", "run", "addresses",
                                    "records_sha256")):
                break
            parts = line.rstrip("\n").split("\t")
            if parts[0] == "elf_sha256":
                return parts[1]
    raise ValueError(f"{path}: no elf_sha256 header line")


def render_expr(ops) -> str:
    """``[(name, args)...]`` -> ``"DW_OP_fbreg -24; DW_OP_deref"``."""
    return "; ".join(" ".join([name, *(str(a) for a in args)]) for name, args in ops)


def member_offset(value) -> int | None:
    """``DW_AT_data_member_location``: a constant, or the DWARF 2 ``[DW_OP_plus_uconst, n]`` form."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, list) and len(value) >= 2 and value[0] == 0x23:  # DW_OP_plus_uconst
        n, shift = 0, 0
        for b in value[1:]:
            n |= (b & 0x7F) << shift
            shift += 7
            if not b & 0x80:
                break
        return n
    return None


def cu_index(intervals) -> tuple[list[int], list[tuple[int, int, int]]]:
    """Sort ``(low, high, cu_offset)`` for :func:`cu_for`."""
    rows = sorted(i for i in intervals if i[1] > i[0])
    return [r[0] for r in rows], rows


def cus_containing(index, va: int) -> list[int]:
    """Every CU whose ranges contain ``va`` (ranges of different CUs can overlap)."""
    return sorted({cu for lo, hi, cu in index[1] if lo <= va < hi})


def cu_for(index, va: int) -> int | None:
    lows, rows = index
    i = bisect.bisect_right(lows, va) - 1
    for j in range(i, max(i - 8, -1), -1):  # ranges are disjoint; look back a little for nesting
        lo, hi, cu = rows[j]
        if lo <= va < hi:
            return cu
    return None


def shape_member(name, offset, size, type_name, type_die, bit_size=None, bit_offset=None,
                 static=False, artificial=False) -> dict:
    rec = {"name": name, "offset": offset, "size": size, "type": type_name, "type_die": type_die}
    if bit_size is not None:
        rec["bit_size"] = bit_size
        rec["bit_offset"] = bit_offset
    if static:
        rec["static"] = True
    if artificial:
        rec["artificial"] = True
    return rec


def prototype_text(ret: str | None, qualified: str, params: list[dict]) -> str:
    args = ", ".join(f"{p['type']} {p['name']}".strip() for p in params if not p.get("artificial"))
    return f"{ret or 'void'} {qualified}({args})"


# --- DWARF walking -------------------------------------------------------------------------------

def _attr(die, name, default=None):
    a = die.attributes.get(name)
    return default if a is None else a.value


def _str(v):
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else v


class Dwarf:
    def __init__(self, elf):
        from elftools.dwarf.descriptions import set_global_machine_arch
        from elftools.dwarf.dwarf_expr import DWARFExprParser
        from elftools.dwarf.locationlists import LocationParser

        self.elf = elf
        self.dw = elf.get_dwarf_info()
        set_global_machine_arch(elf.get_machine_arch())
        self.loc = LocationParser(self.dw.location_lists())
        self.rangelists = self.dw.range_lists()
        self._expr_parser = {}
        self._DWARFExprParser = DWARFExprParser
        self._names: dict[int, str] = {}
        self.types: dict[str, dict] = {}  # qualified type key -> record
        self._type_seen: set[int] = set()
        self.type_depth = None

    # names
    def ref(self, die, attr):
        if attr not in die.attributes:
            return None
        return die.get_DIE_from_attribute(attr)

    def origin(self, die):
        for a in ("DW_AT_abstract_origin", "DW_AT_specification"):
            t = self.ref(die, a)
            if t is not None:
                return t
        return None

    def name_of(self, die) -> str | None:
        seen = 0
        while die is not None and seen < 8:
            n = _attr(die, "DW_AT_name")
            if n is not None:
                return _str(n)
            die = self.origin(die)
            seen += 1
        return None

    def linkage_of(self, die) -> str | None:
        seen = 0
        while die is not None and seen < 8:
            n = _attr(die, "DW_AT_linkage_name") or _attr(die, "DW_AT_MIPS_linkage_name")
            if n is not None:
                return _str(n)
            die = self.origin(die)
            seen += 1
        return None

    def decl_die(self, die):
        """The declaration DIE (end of the abstract_origin/specification chain)."""
        seen = 0
        while seen < 8:
            nxt = self.origin(die)
            if nxt is None:
                return die
            die = nxt
            seen += 1
        return die

    def qualified(self, die) -> str:
        if die.offset in self._names:
            return self._names[die.offset]
        d = self.decl_die(die)
        parts = [self.name_of(die) or f"<anon@{die.offset:#x}>"]
        p = d.get_parent()
        while p is not None and p.tag in _SCOPES:
            parts.append(_str(_attr(p, "DW_AT_name")) or "(anonymous namespace)" if p.tag == "DW_TAG_namespace"
                         else _str(_attr(p, "DW_AT_name")) or f"<anon@{p.offset:#x}>")
            p = p.get_parent()
        q = "::".join(reversed(parts))
        self._names[die.offset] = q
        return q

    def type_name(self, die) -> str:
        if die is None:
            return "void"
        key = ("t", die.offset)
        if key in self._names:
            return self._names[key]
        tag = die.tag
        inner = self.ref(die, "DW_AT_type")
        if tag in _MODIFIERS:
            mod = _MODIFIERS[tag]
            base = self.type_name(inner)
            name = f"{mod} {base}" if mod in ("const", "volatile", "restrict") else f"{base}{mod}"
        elif tag == "DW_TAG_array_type":
            dims = []
            for c in die.iter_children():
                if c.tag == "DW_TAG_subrange_type":
                    cnt = _attr(c, "DW_AT_count")
                    if cnt is None and _attr(c, "DW_AT_upper_bound") is not None:
                        cnt = _attr(c, "DW_AT_upper_bound") + 1
                    dims.append(f"[{'' if cnt is None else cnt}]")
            name = self.type_name(inner) + "".join(dims)
        elif tag == "DW_TAG_subroutine_type":
            args = [self.type_name(self.ref(c, "DW_AT_type")) for c in die.iter_children()
                    if c.tag == "DW_TAG_formal_parameter"]
            name = f"{self.type_name(inner)}({', '.join(args)})"
        elif tag == "DW_TAG_ptr_to_member_type":
            cls = self.ref(die, "DW_AT_containing_type")
            name = f"{self.type_name(inner)} {self.type_name(cls)}::*"
        elif tag in ("DW_TAG_base_type", "DW_TAG_unspecified_type"):
            name = _str(_attr(die, "DW_AT_name")) or "?"
        else:
            name = self.qualified(die)
        self._names[key] = name
        return name

    def byte_size(self, die) -> int | None:
        seen = 0
        while die is not None and seen < 16:
            s = _attr(die, "DW_AT_byte_size")
            if s is not None:
                return s
            if die.tag in ("DW_TAG_pointer_type", "DW_TAG_reference_type", "DW_TAG_rvalue_reference_type"):
                return die.cu["address_size"]
            if die.tag == "DW_TAG_array_type":
                el = self.byte_size(self.ref(die, "DW_AT_type"))
                n = 1
                for c in die.iter_children():
                    if c.tag == "DW_TAG_subrange_type":
                        cnt = _attr(c, "DW_AT_count")
                        if cnt is None and _attr(c, "DW_AT_upper_bound") is not None:
                            cnt = _attr(c, "DW_AT_upper_bound") + 1
                        if cnt is None:
                            return None
                        n *= cnt
                return None if el is None else el * n
            die = self.ref(die, "DW_AT_type")
            seen += 1
        return None

    # locations
    def expr(self, die, raw) -> str:
        cu = die.cu
        p = self._expr_parser.get(id(cu.structs))
        if p is None:
            p = self._expr_parser[id(cu.structs)] = self._DWARFExprParser(cu.structs)
        return render_expr([(op.op_name, op.args) for op in p.parse_expr(raw)])

    def location(self, die, attr_name="DW_AT_location", cu_base=0):
        attr = die.attributes.get(attr_name)
        if attr is None:
            return None
        from elftools.dwarf.locationlists import BaseAddressEntry, LocationEntry, LocationExpr

        try:
            parsed = self.loc.parse_from_attribute(attr, die.cu["version"], die=die)
        except Exception as exc:  # noqa: BLE001 - recorded, never guessed
            return {"error": repr(exc)}
        if isinstance(parsed, LocationExpr):
            return {"expr": self.expr(die, parsed.loc_expr)}
        entries, base = [], cu_base
        for e in parsed:
            if isinstance(e, BaseAddressEntry):
                base = e.base_address
            elif isinstance(e, LocationEntry):
                off = 0 if getattr(e, "is_absolute", False) else base
                entries.append([e.begin_offset + off, e.end_offset + off, self.expr(die, e.loc_expr)])
        return {"list": entries}

    def ranges(self, die, cu_base=0) -> list[list[int]]:
        lo = _attr(die, "DW_AT_low_pc")
        hi_attr = die.attributes.get("DW_AT_high_pc")
        if lo is not None and hi_attr is not None:
            hi = hi_attr.value if hi_attr.form == "DW_FORM_addr" else lo + hi_attr.value
            return [[lo, hi]]
        if "DW_AT_ranges" in die.attributes:
            out, base = [], cu_base
            for r in self.rangelists.get_range_list_at_offset(_attr(die, "DW_AT_ranges"), cu=die.cu):
                if hasattr(r, "base_address"):
                    base = r.base_address
                else:
                    off = 0 if getattr(r, "is_absolute", False) else base
                    out.append([r.begin_offset + off, r.end_offset + off])
            return out
        return []

    # types
    def reach(self, die, depth: int = 0):
        """Record the named types reachable from ``die`` (a type DIE)."""
        seen = 0
        while die is not None and seen < 32:
            if die.offset in self._type_seen:
                return
            tag = die.tag
            if tag in _RECORDS or tag == "DW_TAG_enumeration_type" or tag == "DW_TAG_typedef":
                self._type_seen.add(die.offset)
                self._record_type(die, depth)
                return
            if tag == "DW_TAG_subroutine_type":
                self._type_seen.add(die.offset)
                for c in die.iter_children():
                    if c.tag == "DW_TAG_formal_parameter":
                        self.reach(self.ref(c, "DW_AT_type"), depth)
            elif tag == "DW_TAG_ptr_to_member_type":
                self.reach(self.ref(die, "DW_AT_containing_type"), depth)
            die = self.ref(die, "DW_AT_type")
            seen += 1

    def _record_type(self, die, depth):
        name = self.type_name(die)
        tag = die.tag.removeprefix("DW_TAG_").removesuffix("_type")
        declaration = bool(_attr(die, "DW_AT_declaration"))
        prior = self.types.get(name)
        if prior is not None and (declaration or not prior.get("declaration")):
            if not declaration and prior.get("size") != _attr(die, "DW_AT_byte_size"):
                prior.setdefault("other_definitions", []).append(
                    {"die": die.offset, "size": _attr(die, "DW_AT_byte_size")})
            return
        rec = {"kind": "type", "name": name, "tag": tag, "die": die.offset, "cu": die.cu.cu_offset,
               "size": _attr(die, "DW_AT_byte_size")}
        if declaration:
            rec["declaration"] = True
        nxt = depth + 1
        follow = self.type_depth is None or depth < self.type_depth
        if tag == "typedef":
            t = self.ref(die, "DW_AT_type")
            rec["target"] = self.type_name(t)
            rec["target_die"] = None if t is None else t.offset
            self.types[name] = rec
            if follow:
                self.reach(t, nxt)
            return
        if tag == "enumeration":
            t = self.ref(die, "DW_AT_type")
            rec["underlying"] = None if t is None else self.type_name(t)
            rec["enumerators"] = [[_str(_attr(c, "DW_AT_name")), _attr(c, "DW_AT_const_value")]
                                  for c in die.iter_children() if c.tag == "DW_TAG_enumerator"]
            self.types[name] = rec
            return
        members, bases, vptrs, virtuals, todo = [], [], [], [], []
        for c in die.iter_children():
            if c.tag == "DW_TAG_member" or (c.tag == "DW_TAG_variable" and _attr(c, "DW_AT_external")):
                t = self.ref(c, "DW_AT_type")
                static = c.tag == "DW_TAG_variable" or bool(_attr(c, "DW_AT_external"))
                bit_off = _attr(c, "DW_AT_data_bit_offset", _attr(c, "DW_AT_bit_offset"))
                m = shape_member(_str(_attr(c, "DW_AT_name")), member_offset(_attr(c, "DW_AT_data_member_location")),
                                 self.byte_size(t), self.type_name(t), None if t is None else t.offset,
                                 _attr(c, "DW_AT_bit_size"), bit_off, static, bool(_attr(c, "DW_AT_artificial")))
                members.append(m)
                if (m["name"] or "").startswith("_vptr"):
                    vptrs.append({"name": m["name"], "offset": m["offset"]})
                todo.append(t)
            elif c.tag == "DW_TAG_inheritance":
                t = self.ref(c, "DW_AT_type")
                bases.append({"name": self.type_name(t), "die": None if t is None else t.offset,
                              "offset": member_offset(_attr(c, "DW_AT_data_member_location")),
                              "virtual": bool(_attr(c, "DW_AT_virtuality"))})
                todo.append(t)
            elif c.tag == "DW_TAG_subprogram" and "DW_AT_vtable_elem_location" in c.attributes:
                loc = _attr(c, "DW_AT_vtable_elem_location")
                slot = None
                if isinstance(loc, list) and loc and loc[0] == 0x10:  # DW_OP_constu
                    slot = member_offset([0x23, *loc[1:]])
                virtuals.append({"name": _str(_attr(c, "DW_AT_name")), "slot": slot,
                                 "linkage": _str(_attr(c, "DW_AT_linkage_name"))})
        rec.update({"members": members, "bases": bases})
        if vptrs or virtuals:
            rec["vtable"] = {"vptr_members": vptrs, "virtual_methods": virtuals}
        holder = _attr(die, "DW_AT_containing_type") and self.ref(die, "DW_AT_containing_type")
        if holder is not None and holder is not False:
            rec["vtable_holder"] = self.type_name(holder)
        self.types[name] = rec
        if follow:
            for t in todo:
                self.reach(t, nxt)

    # functions
    def function(self, die, cu_base) -> dict:
        decl = self.decl_die(die)
        q = self.qualified(die)
        ret_die = self.ref(die, "DW_AT_type") or self.ref(decl, "DW_AT_type")
        rec = {"kind": "function", "va": _attr(die, "DW_AT_low_pc"), "name": q,
               "linkage_name": self.linkage_of(die), "die": die.offset, "decl_die": decl.offset,
               "cu": die.cu.cu_offset, "ranges": self.ranges(die, cu_base),
               "decl_file_index": _attr(decl, "DW_AT_decl_file"), "decl_line": _attr(decl, "DW_AT_decl_line"),
               "return_type": None if ret_die is None else self.type_name(ret_die),
               "frame_base": self.location(die, "DW_AT_frame_base", cu_base)}
        self.reach(ret_die)
        params, locals_, blocks, inlined = [], [], [], []

        def var(c, block):
            t = self.ref(c, "DW_AT_type") or self.ref(self.decl_die(c), "DW_AT_type")
            self.reach(t)
            row = {"name": self.name_of(c), "type": self.type_name(t), "type_die": None if t is None else t.offset,
                   "die": c.offset, "location": self.location(c, cu_base=cu_base)}
            if _attr(c, "DW_AT_artificial") or _attr(self.decl_die(c), "DW_AT_artificial"):
                row["artificial"] = True
            if block is not None:
                row["block"] = block
            cv = _attr(c, "DW_AT_const_value")
            if cv is not None:
                row["const_value"] = cv if isinstance(cv, int) else list(cv)
            return row

        def walk(parent, block, inl_parent, in_inline):
            for c in parent.iter_children():
                if c.tag == "DW_TAG_formal_parameter" and parent is die:
                    params.append(var(c, None))
                elif c.tag == "DW_TAG_variable" and not in_inline:
                    locals_.append(var(c, block))
                elif c.tag == "DW_TAG_lexical_block":
                    bid = len(blocks)
                    blocks.append({"id": bid, "parent": block, "ranges": self.ranges(c, cu_base), "die": c.offset})
                    walk(c, bid, inl_parent, in_inline)
                elif c.tag == "DW_TAG_inlined_subroutine":
                    callee = self.origin(c)
                    iid = len(inlined)
                    inlined.append({"id": iid, "parent": inl_parent, "block": block,
                                    "callee": None if callee is None else self.qualified(callee),
                                    "callee_linkage": None if callee is None else self.linkage_of(callee),
                                    "callee_die": None if callee is None else self.decl_die(callee).offset,
                                    "call_file_index": _attr(c, "DW_AT_call_file"),
                                    "call_line": _attr(c, "DW_AT_call_line"),
                                    "ranges": self.ranges(c, cu_base), "die": c.offset})
                    walk(c, block, iid, True)

        walk(die, None, None, False)
        rec.update({"params": params, "locals": locals_, "blocks": blocks, "inlined": inlined,
                    "prototype": prototype_text(rec["return_type"], q, params)})
        return rec


def _symbols(elf) -> dict[int, tuple[str, int]]:
    out: dict[int, tuple[str, int]] = {}
    for s in elf.get_section_by_name(".symtab").iter_symbols():
        if s["st_info"]["type"] == "STT_FUNC" and s["st_value"]:
            va = s["st_value"]
            if va not in out or (s["st_size"] and not out[va][1]):
                out[va] = (s.name, s["st_size"])
    return out


def _callee_fn(elf, syms):
    import capstone

    text = elf.get_section_by_name(".text")
    base, data = text["sh_addr"], text.data()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.skipdata = True

    def callees(va):
        size = syms.get(va, ("", 0))[1]
        if not size or not base <= va < base + len(data):
            return []
        out = set()
        for _addr, _size, mnem, op in md.disasm_lite(data[va - base: va - base + size], va):
            if mnem in ("call", "jmp") and op.startswith("0x"):
                t = int(op, 16)
                if t in syms and t != va:
                    out.add(t)
        return sorted(out)

    return callees


def _cu_intervals(dwarf: Dwarf):
    rows, bases = [], {}
    for cu in dwarf.dw.iter_CUs():
        top = cu.get_top_DIE()
        base = _attr(top, "DW_AT_low_pc", 0) or 0
        bases[cu.cu_offset] = (cu, base)
        for lo, hi in dwarf.ranges(top, base):
            rows.append((lo, hi, cu.cu_offset))
    return rows, bases


def run(args) -> dict:
    from elftools.elf.elffile import ELFFile

    t0 = time.time()
    elf_path = Path(args.elf)
    sha = hashlib.sha256()
    with open(elf_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            sha.update(chunk)
    elf_sha = sha.hexdigest()
    want = read_chains_sha(Path(args.chains))
    if elf_sha != want:
        raise SystemExit(f"refused: {elf_path} sha256 {elf_sha} != inline-chains elf_sha256 {want}")
    fh = open(elf_path, "rb")
    elf = ELFFile(fh)
    syms = _symbols(elf)
    roots: list[int]
    if args.ida_dump:
        with open(args.ida_dump, encoding="utf-8") as d:
            hdr = json.loads(d.readline())
            if hdr.get("input_sha256") != elf_sha or hdr.get("side") != "ps4":
                raise SystemExit(f"refused: {args.ida_dump} is not a PS4 dump of this ELF")
            scope = {json.loads(line)["va"]: 0 for line in d if '"kind":"function"' in line}
        roots = sorted(scope)
        source = f"ida-dump {args.ida_dump}"
    else:
        roots = sorted(va for va, (n, _s) in syms.items() if is_root_symbol(n))
        scope = scope_closure(roots, _callee_fn(elf, syms), args.depth)
        source = f"symbols+capstone depth {args.depth}"
    t_scope = time.time() - t0
    dwarf = Dwarf(elf)
    dwarf.type_depth = args.type_depth
    intervals, bases = _cu_intervals(dwarf)
    index = cu_index(intervals)
    by_cu: dict[int, set[int]] = {}
    no_cu = []
    for va in scope:
        cu = cu_for(index, va)
        if cu is None:
            no_cu.append(va)
        else:
            by_cu.setdefault(cu, set()).add(va)
    funcs, found = [], set()
    for cu_off in sorted(by_cu):
        cu, base = bases[cu_off]
        want_vas = by_cu[cu_off]
        for die in cu.iter_DIEs():
            if die.tag != "DW_TAG_subprogram":
                continue
            lo = _attr(die, "DW_AT_low_pc")
            if lo in want_vas and lo not in found:
                found.add(lo)
                rec = dwarf.function(die, base)
                rec["scope_depth"] = scope[lo]
                rec["symbol"] = syms.get(lo, (None, 0))[0]
                funcs.append(rec)
    retry: dict[int, set[int]] = {}
    for va in set(scope) - found:  # overlapping CU ranges: try every other CU that contains it
        for cu_off in cus_containing(index, va):
            if va not in by_cu.get(cu_off, ()):
                retry.setdefault(cu_off, set()).add(va)
    for cu_off in sorted(retry):
        cu, base = bases[cu_off]
        for die in cu.iter_DIEs():
            if die.tag == "DW_TAG_subprogram":
                lo = _attr(die, "DW_AT_low_pc")
                if lo in retry[cu_off] and lo not in found:
                    found.add(lo)
                    rec = dwarf.function(die, base)
                    rec["scope_depth"] = scope[lo]
                    rec["symbol"] = syms.get(lo, (None, 0))[0]
                    funcs.append(rec)
    funcs.sort(key=lambda r: r["va"])
    missing = sorted(set(scope) - found)
    types = sorted(dwarf.types.values(), key=lambda r: r["name"])
    summary = {
        "kind": "summary", "functions": len(funcs), "scope": len(scope), "roots": len(roots),
        "scope_without_dwarf": len(missing), "scope_without_cu": len(no_cu),
        "params": sum(len(f["params"]) for f in funcs), "locals": sum(len(f["locals"]) for f in funcs),
        "locals_named": sum(1 for f in funcs for v in f["locals"] if v["name"]),
        "locals_with_location": sum(1 for f in funcs for v in f["locals"] if v["location"]),
        "inlined": sum(len(f["inlined"]) for f in funcs), "blocks": sum(len(f["blocks"]) for f in funcs),
        "types": len(types), "types_by_tag": {}, "cus_parsed": len(set(by_cu) | set(retry)),
        "missing_sample": [[va, syms.get(va, (None,))[0]] for va in missing[:20]],
        "seconds": None,
    }
    for t in types:
        summary["types_by_tag"][t["tag"]] = summary["types_by_tag"].get(t["tag"], 0) + 1
    header = {"kind": "header", "script": "extract_dwarf", "script_version": SCRIPT_VERSION,
              "side": "ps4", "elf_path": str(elf_path), "elf_sha256": elf_sha,
              "inline_chains": str(args.chains), "inline_chains_elf_sha256": want,
              "tool": "pyelftools " + _version("pyelftools") + ", capstone " + _version("capstone"),
              "python": sys.version.split()[0], "scope_source": source, "depth": args.depth,
              "type_depth": args.type_depth}
    summary["seconds"] = round(time.time() - t0, 1)
    summary["scope_seconds"] = round(t_scope, 1)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(str(out), header, [*funcs, *types, summary])
    fh.close()
    return summary


def _version(dist: str) -> str:
    from importlib.metadata import version

    try:
        return version(dist)
    except Exception:  # noqa: BLE001
        return "?"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--elf", default=str(DEFAULT_ELF))
    ap.add_argument("--chains", default=str(DEFAULT_CHAINS), help="inline-chains TSV (its elf_sha256 gates the ELF)")
    ap.add_argument("--out", default=str(HERE / "dumps/ps4-dwarf.jsonl"))
    ap.add_argument("--ida-dump", help="PS4 extract_ida.py dump: use its functions as the scope")
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--type-depth", type=int, default=None, help="member/base recursion limit (default: none)")
    args = ap.parse_args(argv)
    summary = run(args)
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
