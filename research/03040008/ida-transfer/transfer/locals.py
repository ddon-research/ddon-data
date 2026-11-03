"""Wave 2 locals (007 T013c, T010 § 5): PC stack locals named after PS4 DWARF locals, by operation.

- **R1 paired callee**: an accepted pair's PC and PS4 functions call a paired callee exactly once each; an
  argument slot of that call carries a stack address on PC (``stack``, frame below the return address) and, on
  PS4, the register DWARF says holds a local's address at the call (``DW_OP_breg<N> 0`` covering the call site).
- **R2 codec anchor**: the same at a rule-3 codec call site pair (``callsites.tsv`` ``pc_site`` <-> ``ps4_site``),
  destination slot (PC stack slot 1, PS4 ``rsi``).
- **R3 handler packet object**: a handler pair whose PC handler calls the PC reader of a rule-1 reader pair once
  with ``this`` = a stack local, and whose PS4 handler calls that PS4 reader once with ``rdi`` = a stack address,
  or inlines it (DWARF inline record); the PS4 handler's one DWARF local of the reader's class names it. R3
  retypes the local to the class's partial (or wave-1) PC type; without one it is refused (size unverifiable).

Gates (T010 § 5): the PC location is a local (frame < 0: never an incoming argument), the width is the DWARF
type's 32-bit size (R1/R2: scalars, pointers, enums, arrays of them, wave-1 types; R3: the retyped type's
size), and per function no location gets two names, no name two locations, and no named local lies inside a
retyped object; every row involved in such a clash is refused. "No user name" and "not an argument" on the
Hex-Rays side, and the lvar's width, are checked when applying (the dumps carry no Hex-Rays lvars).
The PC lvar is recorded by location (entry-relative stack frame) and the defining ``lea`` (``pc_def``); the
apply resolves it to an ``lvar_locator_t``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace

from matcher import gates

from .layout import LayoutError, Layouts, TypeInfo, strip
from .typecheck import class_of
from .wave2 import DWARF_REG, Arg, CallsiteRow, DwLocal, Partial, Wave2Inputs, pc_slots, ps4_reg


@dataclass(frozen=True)
class LocalRow:
    pc_va: int
    ps4_va: int
    rule: str  # R1 | R2 | R3
    pc_call: int
    ps4_call: int  # 0: inlined on PS4
    callee: int  # PC callee (R2: the codec)
    slot: str  # PC argument slot
    name: str
    dwarf_type: str
    dwarf_die: int
    ps4_bind: str
    pc_frame: int
    pc_def: int | None
    size: int | None
    retype: str  # "-" or the PC type name
    status: str  # accepted | refused
    why: str

    @property
    def key(self) -> tuple[int, int, str]:
        return self.pc_va, self.pc_frame, self.name


def _size32(inp: Wave2Inputs, layouts: Layouts, t: str) -> int | None:
    try:
        info = layouts.resolve(t)
    except LayoutError:
        return None

    def ok(i: TypeInfo) -> bool:
        if i.kind == "array":
            return i.elem is not None and ok(i.elem)
        if i.kind == "struct":
            return inp.wave1.get(i.name) == i.size
        return True

    return info.size if ok(info) else None


def bind_breg(locals_: tuple[DwLocal, ...], site: int, reg: str) -> list[DwLocal]:
    """DWARF locals whose location at ``site`` is ``DW_OP_breg<reg> 0``: the register holds the local's address."""
    want = f"DW_OP_breg{DWARF_REG[reg]} 0"
    return [x for x in locals_ if any(lo <= site < hi and e == want for lo, hi, e in x.location)]


def _pc_local(a: Arg | None, slot: str = "ecx", arg_bytes: int | None = 1) -> str | None:
    if a is None and slot != "ecx" and not arg_bytes:
        return "PC call without stack argument values (arg_bytes 0 or unknown)"
    if a is None:
        return "PC argument value not recorded"
    if a.kind != "stack" or a.frame is None:
        return f"PC argument is {a.kind}, not a stack address"
    if a.frame >= 0:
        return "PC stack address is an incoming argument slot"
    return None


def _bind_row(inp: Wave2Inputs, layouts: Layouts, rule: str, pc_va: int, ps4_va: int, pc_call: int, ps4_call: int,
              callee: int, slot: str, pa: Arg | None, reg: str, qa: Arg | None, arg_bytes: int | None
              ) -> LocalRow | None:
    """R1/R2 for one argument slot; None when neither side passes a stack address (nothing to report)."""
    if (pa is None or pa.kind != "stack") and (qa is None or qa.kind != "stack"):
        return None
    dw = inp.dwfn.get(ps4_va)
    cands = bind_breg(dw.locals, ps4_call, reg) if dw else []

    def row(status: str, why: str, loc: DwLocal | None = None, size: int | None = None) -> LocalRow:
        return LocalRow(pc_va, ps4_va, rule, pc_call, ps4_call, callee, slot, loc.name if loc else "-",
                        loc.type if loc else "-", loc.die if loc else 0,
                        f"breg {reg} at {ps4_call:#x}" if loc else "-",
                        pa.frame if pa is not None and pa.frame is not None else 0,
                        pa.def_ea if pa is not None else None, size, "-", status, why)

    why = _pc_local(pa, slot, arg_bytes)
    if why:
        return row("refused", why)
    if qa is not None and qa.kind not in ("stack",):
        return row("refused", f"PS4 argument is {qa.kind}, not a stack address")
    if len(cands) != 1:
        return row("refused", f"{len(cands)} DWARF locals bound to {reg} at the PS4 call")
    loc = cands[0]
    if not loc.name:
        return row("refused", "DWARF local without a name", loc)
    size = _size32(inp, layouts, loc.type)
    if size is None:
        return row("refused", f"size of {loc.type} on PC unverifiable", loc)
    return row("accepted", "", loc, size)


def r1_rows(inp: Wave2Inputs, layouts: Layouts, pairs: set[tuple[int, int]]) -> list[LocalRow]:
    out: list[LocalRow] = []
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
            cfn, cf = inp.ps4fn.get(t4), inp.facts.pc.get(s.target)
            if cfn is None or cf is None:
                continue
            this = gates.pc_has_this(inp.facts, cf)
            slots = pc_slots(cfn, bool(this), layouts) if this is not None else None
            if slots is None:
                continue
            for slot, i in slots.items():
                reg = ps4_reg(cfn, i)
                if reg is None:
                    continue
                r = _bind_row(inp, layouts, "R1", pc_owner, ps4_owner, s.site, q.site, s.target, slot,
                              s.args.get(slot), reg, q.args.get(reg), s.arg_bytes)
                if r is not None:
                    out.append(r)
    return out


def r2_rows(inp: Wave2Inputs, layouts: Layouts, pairs: set[tuple[int, int]], rows: list[CallsiteRow]
            ) -> list[LocalRow]:
    out: list[LocalRow] = []
    for c in rows:
        if c.status != "agree":
            continue
        pcs = inp.pc_args.sites.get(c.pc_site)
        if pcs is None:
            continue
        for ps4_site, ps4_owner in c.ps4:
            if (c.pc_function, ps4_owner) not in pairs:
                continue
            q = inp.ps4_args.sites.get(ps4_site)
            r = _bind_row(inp, layouts, "R2", c.pc_function, ps4_owner, c.pc_site, ps4_site, pcs.target or 0, "1",
                          pcs.args.get("1"), "rsi", q.args.get("rsi") if q else None, pcs.arg_bytes)
            if r is not None:
                out.append(r)
    return out


def r3_rows(inp: Wave2Inputs, layouts: Layouts, pairs: dict[tuple[int, int], str], partial: dict[str, Partial]
            ) -> list[LocalRow]:
    out: list[LocalRow] = []
    readers = {pc: ps4 for (pc, ps4), rule in pairs.items() if rule == "reader"}
    for h, h4 in sorted(pairs):
        if readers.get(h) == h4:
            continue
        pc_sites = inp.pc_args.by_owner.get(h, [])
        ps4_sites = inp.ps4_args.by_owner.get(h4, [])
        dw = inp.dwfn.get(h4)
        for r in sorted({s.target for s in pc_sites if s.target in readers}):
            r4 = readers[r]
            fn4, f = inp.ps4fn.get(r4), inp.facts.pc.get(r)
            calls = [s for s in pc_sites if s.target == r]
            q_calls = [s for s in ps4_sites if s.target == r4]
            s = calls[0]

            def row(status: str, why: str, loc: DwLocal | None = None, size: int | None = None, retype: str = "-",
                    q: int = 0, bind: str = "-", _s=s, _r=r, _h=h, _h4=h4) -> LocalRow:
                a = _s.args.get("ecx")
                return LocalRow(_h, _h4, "R3", _s.site, q, _r, "ecx", loc.name if loc else "-",
                                loc.type if loc else "-", loc.die if loc else 0, bind,
                                a.frame if a is not None and a.frame is not None else 0,
                                a.def_ea if a is not None else None, size, retype, status, why)

            if fn4 is None or f is None or dw is None:
                out.append(row("refused", "reader or handler without a DWARF or PC record"))
                continue
            if len(calls) != 1:
                out.append(row("refused", f"PC handler calls the reader {len(calls)} times"))
                continue
            if not gates.pc_has_this(inp.facts, f):
                out.append(row("refused", "PC reader takes no this"))
                continue
            why = _pc_local(s.args.get("ecx"))
            if why:
                out.append(row("refused", why))
                continue
            slots = pc_slots(fn4, True, layouts) or {}
            extra = [k for k in slots if k != "ecx" and (a := s.args.get(k)) is not None and a.kind == "stack"]
            if extra:
                out.append(row("refused", f"two stack objects passed (PC slots ecx, {' '.join(extra)})"))
                continue
            if len(q_calls) > 1:
                out.append(row("refused", f"PS4 handler calls the reader {len(q_calls)} times"))
                continue
            if q_calls:
                q = q_calls[0]
                qa = q.args.get("rdi")
                if qa is None or qa.kind != "stack":
                    out.append(row("refused", "PS4 reader object is not a stack address", q=q.site))
                    continue
                more = [g for i, g in enumerate(("rsi", "rdx", "rcx", "r8", "r9"), start=1)
                        if i < len(fn4.params) and (b := q.args.get(g)) is not None and b.kind == "stack"]
                if more:
                    out.append(row("refused", f"two stack objects passed (PS4 rdi, {' '.join(more)})", q=q.site))
                    continue
                qsite, how = q.site, f"object passed to the reader at {q.site:#x}"
            elif fn4.name in dw.inlined:
                qsite, how = 0, "reader inlined (DWARF inline record)"
            else:
                out.append(row("refused", "PS4 handler neither calls nor inlines the reader"))
                continue
            cls = class_of(fn4.params[0]["type"], layouts) if fn4.params else None
            if cls is None:
                out.append(row("refused", "PS4 reader this is not a pointer to a class", q=qsite))
                continue
            cands = [x for x in dw.locals if strip(x.type) == cls]
            if len(cands) != 1:
                out.append(row("refused", f"{len(cands)} DWARF locals of class {cls}", q=qsite))
                continue
            loc = cands[0]
            bind = f"type {cls}; {how}"
            p = partial.get(cls)
            if cls in inp.wave1:
                out.append(row("accepted", "wave-1 type", loc, inp.wave1[cls], cls, qsite, bind))
            elif p is not None and p.status == "accepted" and s.args["ecx"].frame + p.size > 0:
                out.append(row("refused", f"{cls} of {p.size:#x} bytes at frame {s.args['ecx'].frame} reaches the "
                               "return address", loc, p.size, "-", qsite, bind))
            elif p is not None and p.status == "accepted":
                out.append(row("accepted", "" if p.size_proved else "size: lower bound", loc, p.size, cls, qsite,
                               bind))
            else:
                out.append(row("refused", f"no accepted PC layout of {cls} (size unverifiable)", loc, None, "-",
                               qsite, bind))
    return out


def gate(rows: list[LocalRow]) -> list[LocalRow]:
    """Per-function clashes refuse every row involved; identical rows from several call sites collapse to the
    first (by rule, call)."""
    rows = sorted(rows, key=lambda r: (r.pc_va, r.pc_frame, r.rule, r.pc_call, r.ps4_call, r.slot))
    acc = [r for r in rows if r.status == "accepted"]
    bad: dict[tuple[int, int, str], str] = {}
    by_loc: dict[tuple[int, int], set[str]] = {}
    by_name: dict[tuple[int, str], set[int]] = {}
    for r in acc:
        by_loc.setdefault((r.pc_va, r.pc_frame), set()).add(r.name)
        by_name.setdefault((r.pc_va, r.name), set()).add(r.pc_frame)
    for r in acc:
        names = by_loc[(r.pc_va, r.pc_frame)]
        frames = by_name[(r.pc_va, r.name)]
        if len(names) > 1:
            bad[r.key] = f"conflict: frame {r.pc_frame} named {' / '.join(sorted(names))}"
        elif len(frames) > 1:
            bad[r.key] = f"duplicate: {r.name} at frames {' '.join(str(f) for f in sorted(frames))}"
    for r in acc:  # a named local inside a retyped object
        for o in acc:
            if (o.retype != "-" and o.pc_va == r.pc_va and o.pc_frame < r.pc_frame < o.pc_frame + (o.size or 0)):
                bad[r.key] = f"inside the retyped {o.name} at frame {o.pc_frame}"
                bad[o.key] = f"holds the named local {r.name} at frame {r.pc_frame}"
    out: list[LocalRow] = []
    seen: set[tuple[int, int, str]] = set()
    for r in rows:
        if r.status == "accepted":
            if r.key in bad:
                r = replace(r, status="refused", why=bad[r.key])
            elif r.key in seen:
                r = replace(r, status="duplicate", why="same name and location as an earlier row")
            seen.add(r.key)
        out.append(r)
    return out


def locals_rows(inp: Wave2Inputs, layouts: Layouts, pairs: dict[tuple[int, int], str], rows: list[CallsiteRow],
                partial: dict[str, Partial]) -> list[LocalRow]:
    ps = set(pairs)
    return gate(r1_rows(inp, layouts, ps) + r2_rows(inp, layouts, ps, rows) + r3_rows(inp, layouts, pairs, partial))
