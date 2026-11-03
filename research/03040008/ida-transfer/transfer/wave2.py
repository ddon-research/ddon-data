"""Wave 2 (007 T013c): member links, partial PC layouts and local names from the v6 call argument values.

Inputs (all offline): the matcher's accepted pairs and rule-3 call sites (``callsites.tsv`` rows with
``ps4_site``), the v6 ``args`` of both IDA dumps, the PS4 DWARF (types, parameters, locals with location lists)
and the wave-1 types (``manifest/transfer/types.tsv``: the types already in the work copy).

1. **Member links**: an aligned codec call site pair whose destination arguments are ``obj+X`` (PC) and
   ``obj+Y`` (PS4) off the same object parameter of the owners (an accepted pair; class from the PS4 owner's
   DWARF parameter) links PC offset X of that class to the DWARF member at Y (through bases and embedded
   structs) with the codec width. Element-reader call anchors: a paired callee called exactly once in each owner,
   whose argument is ``obj+X`` / ``obj+Y`` off the owners' object parameter, links X to the member that starts
   at Y and has the callee parameter's pointee type (a typed ``lea``); its width is the member type's wave-1 PC
   size (types without an accepted wave-1 layout give no link). Array-element links are not derived (T013b:
   the ``element`` base does not fire).
2. **Partial layouts**: a class with links and no conflict (one offset -> two members, one member -> two
   offsets, a width other than the member's leaf width, overlapping links) gets the linked members, gaps
   elsewhere; then every width access of the paired PC functions through that class must not overlap a linked
   member other than on a leaf start of it with the leaf's width (``layout.land``), else the class is refused.
3. **Locals**: R1 paired callee ``&var``, R2 codec anchor ``&var``, R3 handler packet object (see
   :func:`locals_rows`).

Own code: everything here (no library models these joins); stdlib only.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from matcher import gates, tier0
from matcher.model import Facts

from .inputs import Ps4Fn
from .layout import LayoutError, Layouts, TypeInfo, land, strip
from .typecheck import class_of

PS4_REGS = ("rdi", "rsi", "rdx", "rcx", "r8", "r9")
DWARF_REG = {"rdi": 5, "rsi": 4, "rdx": 1, "rcx": 2, "r8": 8, "r9": 9}
FLOAT_TYPES = {"float", "double", "f32", "f64", "long double"}
PARTIAL_COMMENT = ("Partial: {n} members linked by codec position (PS4 02020005 names); gaps are unknown "
                   "Season 3 fields.")


# --- inputs ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Arg:
    slot: str  # PC "ecx" / "0".. (stack slot); PS4 register
    kind: str  # obj | const | stack | element
    arg: int | None = None  # obj: the owner's argument (PC stack slot index or ecx 0; PS4 register index)
    arg_loc: str | None = None  # obj: PC "ecx"/"stack", PS4 the register
    disp: int = 0
    frame: int | None = None  # stack: relative to the entry stack pointer (return address at 0)
    def_ea: int | None = None


@dataclass(frozen=True)
class Site:
    site: int
    owner: int
    target: int | None
    args: dict[str, Arg]
    arg_bytes: int | None = None  # PC: the callee's stack bytes (0 or None: no stack slot values, T013b)


@dataclass
class SideArgs:
    sites: dict[int, Site] = field(default_factory=dict)
    by_owner: dict[int, list[Site]] = field(default_factory=dict)

    def add(self, s: Site) -> None:
        self.sites[s.site] = s
        self.by_owner.setdefault(s.owner, []).append(s)

    def calls_to(self, owner: int, target: int) -> list[Site]:
        return [s for s in self.by_owner.get(owner, []) if s.target == target]


@dataclass(frozen=True)
class DwLocal:
    name: str
    type: str
    die: int
    location: tuple[tuple[int, int, str], ...]  # (lo, hi, expr); a single expression covers everything


@dataclass(frozen=True)
class DwFn:
    va: int
    locals: tuple[DwLocal, ...]
    inlined: frozenset[str]


@dataclass(frozen=True)
class CallsiteRow:
    pc_site: int
    pc_function: int
    width: str
    ps4_overload: str
    status: str
    ps4: tuple[tuple[int, int], ...]  # (ps4_site, ps4_owner)


def parse_arg(a: dict) -> Arg:
    return Arg(str(a["slot"]), a["kind"], a.get("arg"), a.get("arg_loc"), int(a.get("disp") or 0), a.get("frame"),
               a.get("def"))


def load_args(path: Path) -> SideArgs:
    out = SideArgs()
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["kind"] != "function":
                continue
            for c in r["calls"]:
                tgt = None if c["target"] == "indirect" else int(c["target"])
                args = {str(a["slot"]): parse_arg(a) for a in c.get("args") or ()}
                out.add(Site(int(c["site"]), r["va"], tgt, args, c.get("arg_bytes")))
    return out


def _location(loc: dict | None) -> tuple[tuple[int, int, str], ...]:
    if not loc:
        return ()
    if loc.get("list") is not None:
        return tuple((int(lo), int(hi), str(e)) for lo, hi, e in loc["list"])
    if loc.get("expr"):
        return ((0, 1 << 64, str(loc["expr"])),)
    return ()


def load_dwarf_fns(path: Path) -> dict[int, DwFn]:
    out: dict[int, DwFn] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["kind"] != "function":
                continue
            locs = tuple(DwLocal(x.get("name") or "", x.get("type") or "", int(x["die"]), _location(x.get("location")))
                         for x in r.get("locals") or ())
            inl = frozenset(i["callee"] for i in r.get("inlined") or () if i.get("callee"))
            out[r["va"]] = DwFn(r["va"], locs, inl)
    return out


def callsite_rows(rows: list[list[str]]) -> list[CallsiteRow]:
    """``callsites.tsv`` rows (or ``RoleResult.callsites``) as records."""
    out = []
    for r in rows:
        sites = [int(x, 16) for x in r[7].split()] if len(r) > 7 and r[7] else []
        owners = [int(x, 16) for x in r[8].split()] if len(r) > 8 and r[8] else []
        out.append(CallsiteRow(int(r[0], 16), int(r[1], 16), r[3], r[4], r[6], tuple(zip(sites, owners,
                                                                                         strict=True))))
    return out


def read_callsites(path: Path) -> list[CallsiteRow]:
    with path.open(encoding="utf-8", newline="") as fh:
        fh.readline()
        rd = csv.reader(fh, delimiter="\t")
        next(rd)
        return callsite_rows(list(rd))


def read_wave1_types(path: Path) -> tuple[dict[str, int], set[str]]:
    """Wave 1's ``types.tsv``: {accepted or embedded struct: PC size}, and the forward-declared (opaque) names."""
    full: dict[str, int] = {}
    opaque: set[str] = set()
    with path.open(encoding="utf-8", newline="") as fh:
        fh.readline()
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["kind"] in ("struct", "union") and r["status"] in ("accepted", "embedded"):
                full[r["type"]] = int(r["pc_size"], 16)
            elif r["kind"] == "opaque":
                opaque.add(r["type"])
    return full, opaque


@dataclass
class Wave2Inputs:
    facts: Facts
    pc_args: SideArgs
    ps4_args: SideArgs
    ps4fn: dict[int, Ps4Fn]
    dwfn: dict[int, DwFn]
    types: dict[str, dict]
    wave1: dict[str, int]  # wave-1 accepted/embedded struct -> PC size
    wave1_opaque: set[str] = field(default_factory=set)
    pc_strings: dict[int, str] = field(default_factory=dict)  # tier-0 PC handler -> OnPacket_ string
    prefixes: dict[int, list[str]] = field(default_factory=dict)  # table group -> common token prefix
    witness_gate: bool = True  # False only in the control's ungated variant


# --- parameter positions ------------------------------------------------------------------------------

def _is_float(t: str) -> bool:
    return strip(t) in FLOAT_TYPES


def ps4_param(fn: Ps4Fn, reg_index: int) -> int | None:
    """DWARF parameter index held in the ``reg_index``-th integer argument register (None if a float or a
    class by value comes before it, or there is no such parameter)."""
    if reg_index >= len(fn.params):
        return None
    for p in fn.params[:reg_index + 1]:
        if _is_float(p["type"]):
            return None
    return reg_index


def ps4_reg(fn: Ps4Fn, param: int) -> str | None:
    if param >= len(PS4_REGS) or ps4_param(fn, param) != param:
        return None
    return PS4_REGS[param]


def pc_slots(fn: Ps4Fn, has_this: bool, layouts: Layouts) -> dict[str, int] | None:
    """PC argument slot -> DWARF parameter index: ``ecx`` = ``this`` for thiscall, then stack slots of 4 bytes
    in order (a parameter of 8 bytes takes two). None when a parameter's PC size is unknown or a class is passed
    by value."""
    out: dict[str, int] = {}
    params = list(enumerate(fn.params))
    if has_this:
        if not params or not params[0][1].get("artificial"):
            return None
        out["ecx"] = 0
        params = params[1:]
    slot = 0
    for i, p in params:
        try:
            info = layouts.resolve(p["type"])
        except LayoutError:
            return None
        if info.kind == "struct":
            return None
        out[str(slot)] = i
        slot += (info.size + 3) // 4
    return out


def pc_obj_param(a: Arg, slots: dict[str, int]) -> int | None:
    """The DWARF parameter index of a PC ``obj`` value's base argument."""
    if a.kind != "obj" or a.arg is None:
        return None
    key = "ecx" if a.arg_loc == "ecx" else str(a.arg)
    return slots.get(key)


# --- member lookup in the PS4 DWARF (64-bit offsets) -------------------------------------------------

@dataclass(frozen=True)
class Ps4Member:
    path: str  # dotted names from the class (bases are entered silently)
    type: str
    offset: int  # PS4 offset in the class


def _record(types: dict[str, dict], t: str) -> dict | None:
    seen: set[str] = set()
    t = strip(t)
    while t not in seen:
        seen.add(t)
        rec = types.get(t)
        if rec is None:
            return None
        if rec["tag"] == "typedef":
            t = strip(rec["target"])
            continue
        return rec if rec["tag"] in ("class", "structure") else None
    return None


def ps4_members_at(types: dict[str, dict], cls: str, y: int, prefix: str = "", base_off: int = 0
                   ) -> list[Ps4Member]:
    """Every data member (outermost first, then the members of an embedded struct) that starts at PS4 offset
    ``y`` of ``cls``; bases are entered at their offsets."""
    rec = _record(types, cls)
    if rec is None:
        return []
    out: list[Ps4Member] = []
    for b in rec.get("bases") or ():
        if b.get("virtual") or b.get("offset") is None:
            continue
        out += ps4_members_at(types, b["name"], y, prefix, base_off + int(b["offset"]))
    for m in rec.get("members") or ():
        if m.get("static") or m.get("artificial") or m.get("offset") is None or m.get("bit_size") is not None:
            continue
        off = base_off + int(m["offset"])
        size = m.get("size") or 0
        if not off <= y < off + max(size, 1):
            continue
        path = f"{prefix}{m['name']}"
        if off == y:
            out.append(Ps4Member(path, m["type"], off))
        if _record(types, m["type"]) is not None:
            out += ps4_members_at(types, m["type"], y, path + ".", off)
    return out


# --- 1. member links ----------------------------------------------------------------------------------

@dataclass(frozen=True)
class Link:
    cls: str
    pc_off: int
    width: int
    member: str  # PS4 member path
    dwarf_type: str
    ps4_off: int
    kind: str  # codec | anchor
    pc_site: int
    ps4_site: int
    pc_owner: int
    ps4_owner: int


@dataclass(frozen=True)
class NoLink:
    pc_site: int
    ps4_site: int
    why: str


def _leaf_width(layouts: Layouts, t: str) -> int | None:
    try:
        info = layouts.resolve(t)
    except LayoutError:
        return None
    return info.size if info.kind in ("scalar", "enum", "pointer") else None


def _owner_class(inp: Wave2Inputs, layouts: Layouts, pc_owner: int, ps4_owner: int, pc_a: Arg, ps4_a: Arg
                 ) -> tuple[str | None, str]:
    fn = inp.ps4fn.get(ps4_owner)
    f = inp.facts.pc.get(pc_owner)
    if fn is None or f is None:
        return None, "owner without DWARF or PC record"
    this = gates.pc_has_this(inp.facts, f)
    slots = pc_slots(fn, bool(this), layouts) if this is not None else None
    if slots is None:
        return None, "PC argument slots unknown"
    p_pc = pc_obj_param(pc_a, slots)
    p_ps4 = ps4_param(fn, ps4_a.arg) if ps4_a.arg is not None else None
    if p_pc is None or p_ps4 is None:
        return None, "object argument not a parameter"
    if p_pc != p_ps4:
        return None, f"object parameters differ (PC {p_pc}, PS4 {p_ps4})"
    cls = class_of(fn.params[p_pc]["type"], layouts)
    if cls is None:
        return None, f"parameter {p_pc} is not a pointer to a class"
    why = packet_witness(inp, pc_owner, cls)
    if why:
        return None, why
    return cls, ""


PACKET_CLASS = re.compile(r"(?:\w+::)*CPacket_(?:S2C|L2C|C2S|C2L)_(\w+)$")


def packet_witness(inp: Wave2Inputs, pc_owner: int, cls: str) -> str | None:
    """Independent PC evidence of a packet class (the control's discriminator): some PC handler that calls the
    owner has a tier-0 ``OnPacket_`` string whose names (``tier0.candidate_names``, rule 1) include the class's
    packet name. Classes that are not ``CPacket_*`` pass (no PC string names them)."""
    m = PACKET_CLASS.fullmatch(cls)
    if m is None or not inp.witness_gate:
        return None
    names: set[str] = set()
    for s in inp.pc_args.sites.values():
        if s.target == pc_owner and s.owner in inp.pc_strings:
            g = inp.facts.table_group.get(s.owner)
            names.update(tier0.candidate_names(inp.pc_strings[s.owner], inp.prefixes.get(g, []) if g is not None
                                               else []))
    if m.group(1) in names:
        return None
    return f"no PC handler string of the owner names {cls}"


def codec_links(inp: Wave2Inputs, layouts: Layouts, pairs: set[tuple[int, int]], rows: list[CallsiteRow]
                ) -> tuple[list[Link], list[NoLink]]:
    links: list[Link] = []
    no: list[NoLink] = []
    for r in rows:
        if r.status != "agree":
            continue
        for ps4_site, ps4_owner in r.ps4:
            def miss(why: str, _s: int = ps4_site, _p: int = r.pc_site) -> None:
                no.append(NoLink(_p, _s, why))
            if (r.pc_function, ps4_owner) not in pairs:
                miss("owners not an accepted pair")
                continue
            if not r.width.isdigit():
                miss("variable width")
                continue
            pcs, ps4s = inp.pc_args.sites.get(r.pc_site), inp.ps4_args.sites.get(ps4_site)
            pa = pcs.args.get("1") if pcs else None
            qa = ps4s.args.get("rsi") if ps4s else None
            if pa is None or qa is None or pa.kind != "obj" or qa.kind != "obj":
                kinds = f"{pa.kind if pa else 'none'}/{qa.kind if qa else 'none'}"
                miss(f"destination not obj+X on both sides ({kinds})")
                continue
            cls, why = _owner_class(inp, layouts, r.pc_function, ps4_owner, pa, qa)
            if cls is None:
                miss(why)
                continue
            width = int(r.width)
            leaves = [m for m in ps4_members_at(inp.types, cls, qa.disp) if _record(inp.types, m.type) is None]
            if not leaves:
                miss(f"no leaf member at PS4 {cls}+{qa.disp:#x}")
                continue
            m = leaves[-1]  # innermost leaf starting there
            links.append(Link(cls, pa.disp, width, m.path, m.type, m.offset, "codec", r.pc_site, ps4_site,
                              r.pc_function, ps4_owner))
    return links, no


def anchor_links(inp: Wave2Inputs, layouts: Layouts, pairs: set[tuple[int, int]]) -> tuple[list[Link], list[NoLink]]:
    """Element-reader call anchors (T012 § 1.5): a paired callee called once in each owner of an accepted pair."""
    links: list[Link] = []
    no: list[NoLink] = []
    callee = dict(pairs)
    for pc_owner, ps4_owner in sorted(pairs):
        pc_sites = inp.pc_args.by_owner.get(pc_owner, [])
        ps4_sites = inp.ps4_args.by_owner.get(ps4_owner, [])
        pc_count = Counter(s.target for s in pc_sites)
        ps4_count = Counter(s.target for s in ps4_sites)
        for s in pc_sites:
            if s.target is None or s.target not in callee or pc_count[s.target] != 1:
                continue
            t4 = callee[s.target]
            if ps4_count[t4] != 1:
                continue
            q = next(x for x in ps4_sites if x.target == t4)
            cfn = inp.ps4fn.get(t4)
            cf = inp.facts.pc.get(s.target)
            if cfn is None or cf is None:
                continue
            this = gates.pc_has_this(inp.facts, cf)
            slots = pc_slots(cfn, bool(this), layouts) if this is not None else None
            if slots is None:
                continue
            for slot, i in slots.items():
                pa = s.args.get(slot)
                reg = ps4_reg(cfn, i)
                qa = q.args.get(reg) if reg else None
                if pa is None or qa is None or pa.kind != "obj" or qa.kind != "obj":
                    continue
                if pa.def_ea is None and pa.disp == 0 and qa.disp == 0:
                    continue  # the owner's object passed on as is: no member
                cls, why = _owner_class(inp, layouts, pc_owner, ps4_owner, pa, qa)
                if cls is None:
                    no.append(NoLink(s.site, q.site, why))
                    continue
                want = class_of(cfn.params[i]["type"], layouts)
                if want is None:
                    no.append(NoLink(s.site, q.site, f"callee parameter {i} is not a pointer to a class"))
                    continue
                ms = [m for m in ps4_members_at(inp.types, cls, qa.disp) if strip(m.type) == want]
                if not ms:
                    no.append(NoLink(s.site, q.site, f"no member of type {want} at PS4 {cls}+{qa.disp:#x}"))
                    continue
                if want not in inp.wave1:
                    no.append(NoLink(s.site, q.site, f"member type {want} has no accepted wave-1 PC layout"))
                    continue
                m = ms[0]
                links.append(Link(cls, pa.disp, inp.wave1[want], m.path, m.type, m.offset, "anchor", s.site, q.site,
                                  pc_owner, ps4_owner))
    return links, no


# --- 2. partial layouts --------------------------------------------------------------------------------

@dataclass(frozen=True)
class PMember:
    offset: int
    size: int
    name: str  # C identifier (path dots -> "__")
    path: str
    dwarf_type: str
    links: int


@dataclass
class Partial:
    cls: str
    status: str  # accepted | refused | wave-1
    members: list[PMember] = field(default_factory=list)
    size: int = 0
    size_proved: bool = False
    size_evidence: str = ""
    conflicts: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    width_checked: int = 0
    gap_accesses: int = 0
    indexed_unplaced: int = 0
    evidence: set[int] = field(default_factory=set)
    functions: set[int] = field(default_factory=set)

    @property
    def reason(self) -> str:
        if self.status == "wave-1":
            return "wave-1 type, unchanged"
        if self.conflicts:
            return "conflict: " + "; ".join(self.conflicts[:5])
        if self.contradictions:
            return "access contradicts: " + "; ".join(self.contradictions[:5])
        return "links agree; no access contradicts"

    @property
    def comment(self) -> str:
        c = PARTIAL_COMMENT.format(n=len(self.members))
        return c if self.size_proved else c + " size: lower bound"


def _ident(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", path.replace(".", "__"))


def partial_layouts(inp: Wave2Inputs, layouts: Layouts, links: list[Link], known_sizes: dict[str, tuple[int, str]],
                    cparams: dict[str, list[tuple[int, str, int]]]) -> dict[str, Partial]:
    by_cls: dict[str, list[Link]] = {}
    for lk in links:
        by_cls.setdefault(lk.cls, []).append(lk)
    out: dict[str, Partial] = {}
    for cls, ls in sorted(by_cls.items()):
        p = Partial(cls, "accepted")
        out[cls] = p
        if cls in inp.wave1:
            p.status = "wave-1"
            continue
        by_off: dict[int, set[tuple[str, int]]] = {}
        by_mem: dict[str, set[int]] = {}
        for lk in ls:
            by_off.setdefault(lk.pc_off, set()).add((lk.member, lk.width))
            by_mem.setdefault(lk.member, set()).add(lk.pc_off)
            p.evidence.add(lk.pc_site)
        for off, ms in sorted(by_off.items()):
            if len({m for m, _ in ms}) > 1:
                p.conflicts.append(f"+{off:#x} -> {' / '.join(sorted(m for m, _ in ms))}")
            if len({w for _, w in ms}) > 1:
                p.conflicts.append(f"+{off:#x} widths {sorted({w for _, w in ms})}")
        for m, offs in sorted(by_mem.items()):
            if len(offs) > 1:
                p.conflicts.append(f"{m} -> {' / '.join(f'+{o:#x}' for o in sorted(offs))}")
        members: list[PMember] = []
        infos: dict[int, TypeInfo] = {}
        for off in sorted(by_off):
            (member, width), *_ = sorted(by_off[off])
            lk = next(x for x in ls if x.pc_off == off and x.member == member)
            try:
                info = layouts.resolve(lk.dwarf_type)
            except LayoutError as e:
                p.conflicts.append(f"{member}: {e}")
                continue
            leaf = info.size if info.kind != "struct" else inp.wave1.get(info.name)
            if leaf != width:
                p.conflicts.append(f"{member} at +{off:#x}: width {width}, member {leaf}")
                continue
            if off < 0:
                p.conflicts.append(f"{member} at negative offset {off}")
                continue
            infos[off] = info
            members.append(PMember(off, width, _ident(member), member, lk.dwarf_type,
                                   sum(1 for x in ls if x.pc_off == off)))
        for a, b in zip(members, members[1:], strict=False):
            if a.offset + a.size > b.offset:
                p.conflicts.append(f"{a.path} +{a.offset:#x}..{a.offset + a.size:#x} overlaps {b.path} "
                                   f"+{b.offset:#x}")
        p.members = members
        end = max((m.offset + m.size for m in members), default=0)
        if cls in known_sizes:
            p.size, p.size_proved, p.size_evidence = known_sizes[cls][0], True, known_sizes[cls][1]
            if end > p.size:
                p.conflicts.append(f"members end at {end:#x}, proved size {p.size:#x}")
        else:
            p.size, p.size_evidence = end, "lower bound: end of the last linked member"
        if p.conflicts or not members:
            p.status = "refused"
            if not members and not p.conflicts:
                p.conflicts.append("no member survives")
            continue
        _access_check(inp, cparams.get(cls, []), p, infos)
        if p.contradictions:
            p.status = "refused"
    return out


def class_params(inp: Wave2Inputs, layouts: Layouts, pairs: set[tuple[int, int]]
                 ) -> dict[str, list[tuple[int, str, int]]]:
    """class -> [(PC function, PC arg_loc, arg)] for every accepted pair parameter that points to the class."""
    out: dict[str, list[tuple[int, str, int]]] = {}
    for pc_va, ps4_va in sorted(pairs):
        fn, f = inp.ps4fn.get(ps4_va), inp.facts.pc.get(pc_va)
        if fn is None or f is None:
            continue
        this = gates.pc_has_this(inp.facts, f)
        if this is None:
            continue
        slots = pc_slots(fn, this, layouts)
        if slots is None:
            continue
        for slot, i in slots.items():
            cls = class_of(fn.params[i]["type"], layouts)
            if cls is None:
                continue
            loc, arg = ("ecx", 0) if slot == "ecx" else ("stack", int(slot))
            out.setdefault(cls, []).append((pc_va, loc, arg))
    return out


def _access_check(inp: Wave2Inputs, params: list[tuple[int, str, int]], p: Partial, infos: dict[int, TypeInfo]
                  ) -> None:
    """Every width access of the paired PC functions through a parameter of this class: one overlapping a linked
    member must land on a leaf start of it with the leaf's width (``layout.land``); gaps are allowed."""
    for pc_va, loc, arg in params:
        f = inp.facts.pc[pc_va]
        for a in f.accesses:
            if a.arg_loc != loc or a.arg != arg or a.via is not None or a.width is None:
                continue
            p.functions.add(pc_va)
            if a.indexed:
                p.indexed_unplaced += 1
                continue
            hit = [m for m in p.members if a.disp < m.offset + m.size and m.offset < a.disp + a.width]
            if not hit:
                p.gap_accesses += 1
                continue
            m = hit[0]
            ok = len(hit) == 1 and land(infos[m.offset], a.disp - m.offset, a.width).ok
            if ok:
                p.width_checked += 1
                p.evidence.add(a.va)
            else:
                p.contradictions.append(f"{a.va:#x} {a.access} +{a.disp:#x} w{a.width} on {m.path} "
                                        f"+{m.offset:#x} ({m.size})")
