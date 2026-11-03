"""Rule 3: structure types, accepted by the PC access check.

Candidates: the class of ``this`` and of each pointer-to-class argument of the accepted pairs, the pointee
classes of pointer members they load through (v4 ``via``), and recursively the embedded member and base types.
Every object-relative access a paired PC function makes through such an argument must fit the computed PC
layout by the access rules of ``layout`` (T006b, README "Access check"): a width access on the start of a
leaf member with the leaf's width or on the vptr; a ``lea`` on the start of one of the object's own members
or array elements, never inside an embedded struct; an indexed access with the element size as its scale on
an element start; nothing beyond the size. Contradictions count against the argument's class (the root); an
access counts for an embedded type, or a ``via`` pointee, only while the root is not refused. A type that
embeds a refused type is refused. Accepted: no contradiction, at least one checked width access (a load or
store on a leaf start: a ``lea`` may contradict a type but never accept one, T006c), a size equal to any known
size; a type checked by ``lea`` records alone stays ``unchecked`` with reason ``lea-only``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from matcher import gates
from matcher.model import Facts, Param

from .inputs import PairRow, Ps4Fn
from .layout import Landing, LayoutError, Layouts, TypeInfo, land, member_at, strip

# Sizes proved on PC by the T002 audit (§ 3.3): DTI registration + allocation, and a stack object.
KNOWN_SIZES = {
    "cSeedGameSvConnection": (0x540, "T002: PC DTI 0x1A2B1B0 size 0x540, allocation 0x877840 alloc(0x540)"),
    "nUserSession::CPacket_S2C_GET_STAGE_LIST_RES": (0x30, "T002: stack object 0x30 built in 0x7FD9E0"),
}


@dataclass(frozen=True)
class Evidence:
    root: str  # the type the access is laid on
    pc_func: int
    va: int
    disp: int
    width: int | None
    access: str
    landing: Landing
    parent: str | None = None  # via: the argument's class whose pointer member was dereferenced
    indexed: bool = False


@dataclass
class TypeVerdict:
    name: str
    status: str  # accepted | embedded | refused | unchecked
    size: int | None
    reason: str
    checked: int = 0
    width_checked: int = 0  # T006c: checked accesses that carry a width (loads and stores on a leaf start)
    contradictions: list[Evidence] = field(default_factory=list)
    checked_members: dict[str, set[int]] = field(default_factory=dict)  # member -> insn VAs
    evidence_vas: set[int] = field(default_factory=set)
    covered: set[int] = field(default_factory=set)  # byte offsets of leaves checked by fixed-offset width accesses
    functions: set[int] = field(default_factory=set)
    size_evidence: str = ""


def class_of(t: str, layouts: Layouts) -> str | None:
    """The class/structure/union a pointer or reference type string points to (through typedefs)."""
    s = strip(t)
    if not s.endswith(("*", "&")) or "(" in s:
        return None
    inner = strip(s[:-1])
    if inner.endswith(("*", "&")):  # T006b: ``T**`` points to a pointer (``MtArray::mpArray``), not to a T
        return None
    seen: set[str] = set()
    while inner not in seen:
        seen.add(inner)
        rec = layouts.record(inner)
        if rec is None:
            return None
        if rec["tag"] == "typedef":
            inner = strip(rec["target"])
            continue
        return inner if rec["tag"] in ("class", "structure", "union") else None
    return None


def arg_roots(facts: Facts, layouts: Layouts, pc_va: int, fn: Ps4Fn) -> dict[tuple[str, int], str]:
    """{(arg_loc, arg index): class name} for the pair's object arguments, PC locations from gate (c)'s widths."""
    out: dict[tuple[str, int], str] = {}
    params = fn.params
    has_this = bool(params) and bool(params[0].get("artificial"))
    if has_this and gates.pc_has_this(facts, facts.pc[pc_va]):
        c = class_of(params[0]["type"], layouts)
        if c:
            out[("ecx", 0)] = c
    slot = 0
    for p in params[1:] if has_this else params:
        w = gates.param_bytes(Param(p["name"], p["type"], p.get("type_die")), facts.types)
        if w is None:
            break
        c = class_of(p["type"], layouts)
        if c:
            out[("stack", slot)] = c
        slot += w // 4
    return out


def collect(facts: Facts, layouts: Layouts, pairs: list[PairRow], ps4fn: dict[int, Ps4Fn]
            ) -> tuple[list[Evidence], dict[str, str], set[str]]:
    """Evidence per access, layout refusals {type: reason}, and every root candidate."""
    ev: list[Evidence] = []
    bad_layout: dict[str, str] = {}
    roots: set[str] = set()
    for p in pairs:
        fn = ps4fn.get(p.ps4_va)
        f = facts.pc.get(p.pc_va)
        if fn is None or f is None:
            continue
        args = arg_roots(facts, layouts, p.pc_va, fn)
        roots.update(args.values())
        for a in f.accesses:
            cls = args.get((a.arg_loc, a.arg))
            if cls is None:
                continue
            try:
                info = layouts.layout(cls)
            except LayoutError as e:
                bad_layout[cls] = str(e)
                continue
            width = None if a.access == "lea" else a.width
            if a.via is None:
                ev.append(Evidence(cls, p.pc_va, a.va, a.disp, width, a.access,
                                   _landing(info, a.disp, width, a.access, a.indexed, a.scale), indexed=a.indexed))
                continue
            m = member_at(info, a.via)
            if m is None or m.kind != "pointer":
                ev.append(Evidence(cls, p.pc_va, a.va, a.via, 4, "via", Landing(
                    False, (cls,), f"+{a.via:#x} (dereferenced) is not a pointer member")))
                continue
            assert m.info is not None
            pointee = class_of(m.info.name, layouts)
            if pointee is None:
                continue
            roots.add(pointee)
            try:
                pinfo = layouts.layout(pointee)
            except LayoutError as e:
                bad_layout[pointee] = str(e)
                continue
            ev.append(Evidence(pointee, p.pc_va, a.va, a.disp, width, a.access,
                               _landing(pinfo, a.disp, width, a.access, a.indexed, a.scale), cls, a.indexed))
    return ev, bad_layout, roots


def _landing(info: TypeInfo, disp: int, width: int | None, access: str, indexed: bool, scale: int | None
             ) -> Landing:
    if access != "lea" and width is None:  # fail closed: a load or store without a width checks nothing
        return Landing(False, (info.name,), f"+{disp:#x}: {access} without a width")
    return land(info, disp, width, indexed, scale)


def embedded(info: TypeInfo) -> set[str]:
    """Struct types laid out inside ``info`` (bases, members, array elements), recursively."""
    out: set[str] = set()
    stack = [info]
    while stack:
        t = stack.pop()
        if t.kind == "array" and t.elem is not None:
            stack.append(t.elem)
        elif t.kind == "struct":
            for m in t.members:
                if m.info is not None and m.kind in ("struct", "base", "array"):
                    if m.info.kind == "struct":
                        out.add(m.info.name)
                    stack.append(m.info)
    return out


def decide(layouts: Layouts, ev: list[Evidence], bad_layout: dict[str, str], roots: set[str]) -> dict[str, TypeVerdict]:
    refused: dict[str, str] = dict(bad_layout)
    universe = set(roots)
    for name in list(roots):
        if name not in refused:
            universe |= embedded(layouts.layout(name))
    while True:
        before = len(refused)
        for e in ev:
            if e.root in refused or e.landing.ok:
                continue
            if e.parent is not None and e.parent in refused:
                continue
            refused[e.root] = "contradiction"
        for name in sorted(universe - set(refused)):
            emb = sorted(x for x in embedded(layouts.layout(name)) if x in refused)
            if emb:
                refused[name] = "embeds refused " + ", ".join(emb)
        for name, (size, _) in KNOWN_SIZES.items():
            if name in universe and name not in refused and layouts.layout(name).size != size:
                refused[name] = f"size {layouts.layout(name).size:#x} != known {size:#x}"
        if len(refused) == before:
            break
    out: dict[str, TypeVerdict] = {}
    for name in sorted(universe | set(refused)):
        size = None
        try:
            size = layouts.layout(name).size
        except LayoutError:
            pass
        out[name] = TypeVerdict(name, "refused" if name in refused else "unchecked", size, refused.get(name, ""))
        if name in KNOWN_SIZES:
            out[name].size_evidence = KNOWN_SIZES[name][1]
    for e in ev:
        if e.parent is not None and e.parent in refused:
            continue
        if not e.landing.ok:
            if e.root in out:
                out[e.root].contradictions.append(e)
            continue
        if e.root in refused:
            continue
        for k, t in enumerate(e.landing.path):
            v = out.get(t)
            if v is None:
                continue
            v.checked += 1
            if e.width is not None and e.access != "lea":
                v.width_checked += 1
            v.evidence_vas.add(e.va)
            v.functions.add(e.pc_func)
            if e.width and not e.indexed and k < len(e.landing.offs):
                v.covered.update(range(e.landing.offs[k], e.landing.offs[k] + e.width))
        for t, m in e.landing.hits:
            if t in out:
                out[t].checked_members.setdefault(m, set()).add(e.va)
        if not e.landing.hits:
            out[e.root].checked_members.setdefault("(whole)", set()).add(e.va)
    for name, v in out.items():
        if v.status == "refused":
            continue
        if name in roots and v.width_checked:
            v.status, v.reason = "accepted", "no contradiction"
        elif v.checked and not v.width_checked:
            v.reason = "lea-only"  # T006c: a lea may contradict a type but never accept one
        elif not v.checked:
            v.reason = "no checked access"
    # embedded types of accepted types: emitted as part of their outer type when themselves checked
    accepted = {n for n, v in out.items() if v.status == "accepted"}
    for name in sorted(accepted):
        for x in embedded(layouts.layout(name)):
            v = out[x]
            if v.status == "unchecked" and v.width_checked:
                v.status, v.reason = "embedded", f"laid out inside {name}; checked through it"
    return out


def coverage_text(v: TypeVerdict) -> str:
    """Checked member bytes / size: the bytes of leaves hit by fixed-offset loads and stores."""
    if not v.size:
        return "-"
    return f"{len(v.covered)}/{v.size} {100 * len(v.covered) / v.size:.1f}%"


def contradiction_text(v: TypeVerdict, limit: int = 6) -> str:
    seen: list[str] = []
    for e in sorted(v.contradictions, key=lambda e: (e.disp, e.va)):
        s = f"{e.landing.where} @{e.va:#x}"
        if s not in seen:
            seen.append(s)
    more = f" (+{len(seen) - limit} more)" if len(seen) > limit else ""
    return "; ".join(seen[:limit]) + more
