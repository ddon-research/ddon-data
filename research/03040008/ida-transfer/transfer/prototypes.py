"""Rule 2: prototypes (IDA declaration strings, printed form without a name).

Convention from PC code: ``this`` in ecx -> ``__thiscall``; else ``ret N`` -> ``__stdcall``; plain ``ret`` ->
``__cdecl``. Argument count and widths are gate (c)'s (the pair passed it); names come from the DWARF parameters.
Types: base types by size and encoding; pointers/references to a class -> pointer to that class (opaque unless rule
3 transfers it); enums by value as the DWARF enum (4-byte ones); anything else -> the width-sized integer with the
DWARF type in the comment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from matcher import gates
from matcher.model import Facts, Param

from .inputs import PcExtra, Ps4Fn
from .layout import BASE, FIXED, POINTER_SIZED, Layouts, declarable, deref, strip

WIDTH_INT = {1: "unsigned __int8", 2: "unsigned __int16", 4: "int", 8: "__int64"}
TIER0_CLASSES = ("cSeedGameSvConnection", "cSeedLoginSvConnection")
_REG_ARG = re.compile(r"@<(\w+)>")
_IDENT = re.compile(r"[^A-Za-z0-9_]")


@dataclass
class CType:
    text: str
    note: str | None = None  # DWARF type when the C type is a fallback
    classes: set[str] = field(default_factory=set)  # pointee classes (declared opaque unless transferred)
    enums: set[str] = field(default_factory=set)


def _scalar(t: str, layouts: Layouts) -> str | None:
    """C type of a scalar DWARF type string (following typedefs), or None."""
    seen: set[str] = set()
    while True:
        t = strip(t)
        if t in FIXED:
            return FIXED[t][1]
        if t in POINTER_SIZED:
            return POINTER_SIZED[t]
        if t in BASE:
            return BASE[t][1]
        rec = layouts.record(t)
        if rec is None or rec["tag"] != "typedef" or t in seen:
            return None
        seen.add(t)
        t = rec["target"]


def _named(t: str, layouts: Layouts) -> tuple[str, dict] | None:
    """(name, record) of the class/structure/union/enumeration a type string names, through typedefs."""
    seen: set[str] = set()
    while True:
        t = strip(t)
        rec = layouts.record(t)
        if rec is None or t in seen:
            return None
        if rec["tag"] != "typedef":
            return t, rec
        seen.add(t)
        t = rec["target"]


def ctype(t: str, layouts: Layouts, width: int | None = None) -> CType:
    """C type for IDA of one DWARF parameter / return type; ``width`` is the PC stack width (for fallbacks)."""
    s = strip(t)
    if s == "void":
        return CType("void")
    if s.endswith(("*", "&")) and "(" not in s and "::*" not in s:
        inner = deref(s)
        if inner == "void":
            return CType("void *")
        sc = _scalar(inner, layouts)
        if sc is not None:
            return CType(sc + " *")
        if inner.endswith(("*", "&")):
            sub = ctype(inner, layouts)
            if sub.note is None:
                return CType(sub.text + "*" if sub.text.endswith("*") else sub.text + " *", None, sub.classes,
                             sub.enums)
        named = _named(inner, layouts)
        if named and declarable(named[0]):
            name, rec = named
            if rec["tag"] == "enumeration":
                return CType(name + " *", None, set(), {name}) if rec.get("size") == 4 else CType("void *", t)
            return CType(name + " *", None, {name})
        return CType("void *", t)
    sc = _scalar(s, layouts)
    if sc is not None:
        return CType(sc)
    named = _named(s, layouts)
    if named and named[1]["tag"] == "enumeration" and named[1].get("size") == 4 and declarable(named[0]):
        return CType(named[0], None, set(), {named[0]})
    return CType(WIDTH_INT.get(width or 4, "int"), t)


@dataclass(frozen=True)
class ProtoRow:
    pc_va: int
    decl: str
    current: str
    action: str  # set | equal | conflict | skip
    basis: str
    notes: str
    classes: tuple[str, ...]
    enums: tuple[str, ...]


def convention(facts: Facts, pc_va: int) -> tuple[str | None, str]:
    f = facts.pc[pc_va]
    this = gates.pc_has_this(facts, f)
    if this is None:
        return None, "PC this unknown"
    if this:
        return "__thiscall", "ecx this"
    if f.ret_imm:
        vals = set(f.ret_imm)
        if len(vals) != 1:
            return None, "several ret N"
        n = vals.pop()
        return ("__stdcall", f"ret {n}") if n else ("__cdecl", "ret")
    return "__cdecl", "plain ret"


def register_args(current: str | None) -> list[str]:
    """Registers IDA's current prototype takes arguments in, other than ecx (``__usercall``/``__userpurge``)."""
    if not current or "(" not in current:
        return []
    args = current[current.index("("):]
    return sorted({r for r in _REG_ARG.findall(args) if r != "ecx"})


def _pname(p: dict, i: int) -> str:
    n = _IDENT.sub("_", p.get("name") or "") or f"a{i}"
    return n if not n[0].isdigit() else f"a{n}"


def pair_prototype(facts: Facts, layouts: Layouts, pc_va: int, fn: Ps4Fn, extra: PcExtra | None,
                   basis: str) -> ProtoRow:
    cur = (extra.prototype if extra else None) or ""
    regs = register_args(cur)
    if regs:
        return ProtoRow(pc_va, "", cur, "skip", basis, "IDA sees register argument(s) " + ",".join(regs)
                        + "; convention not provable from the dump", (), ())
    cc, why = convention(facts, pc_va)
    if cc is None:
        return ProtoRow(pc_va, "", cur, "skip", basis, why, (), ())
    params = fn.params
    has_this = bool(params) and bool(params[0].get("artificial"))
    if has_this != (cc == "__thiscall"):
        return ProtoRow(pc_va, "", cur, "skip", basis, f"this: PC {cc} DWARF {has_this}", (), ())
    ok, gate = gates.gate_c(facts, pc_va, fn.va)
    if not ok:
        return ProtoRow(pc_va, "", cur, "skip", basis, "gate c: " + gate, (), ())
    ret = strip(fn.return_type or "void")
    rnamed = _named(ret, layouts)
    if rnamed and rnamed[1]["tag"] in ("class", "structure", "union"):
        return ProtoRow(pc_va, "", cur, "skip", basis, f"returns {ret} by value (hidden pointer not modelled)",
                        (), ())
    rt = ctype(ret, layouts)
    notes = [why]
    classes, enums = set(rt.classes), set(rt.enums)
    if rt.note:
        notes.append(f"return: DWARF {rt.note}")
    args = []
    for i, p in enumerate(params):
        if i == 0 and has_this:
            c = ctype(p["type"], layouts)
            args.append(f"{c.text}this" if c.text.endswith("*") else f"{c.text} *this")
        else:
            w = gates.param_bytes(Param(p["name"], p["type"], p.get("type_die")), facts.types)
            c = ctype(p["type"], layouts, w)
            args.append(f"{c.text}{'' if c.text.endswith('*') else ' '}{_pname(p, i)}")
        if c.note:
            notes.append(f"{_pname(p, i)}: DWARF {c.note}")
        classes |= c.classes
        enums |= c.enums
    rtext = rt.text if rt.text.endswith("*") else rt.text + " "
    decl = f"{rtext}{cc}({', '.join(args)})"
    if cur == decl:
        action = "equal"
    elif extra is not None and extra.prototype_user:
        action = "conflict"
        notes.append("current prototype is user-set")
    else:
        action = "set"
    return ProtoRow(pc_va, decl, cur, action, basis, "; ".join(notes), tuple(sorted(classes)), tuple(sorted(enums)))


def tier0_prototype(facts: Facts, pc_va: int, pc_string: str, extra: PcExtra | None) -> ProtoRow:
    """``int __thiscall(<class> *this, void *packet)`` for a tier-0 handler without a PS4 pair, only when the dump
    proves ecx this and ``ret 4`` and the string names a connection class (T002 § 3.1: the 50 handlers)."""
    cur = (extra.prototype if extra else None) or ""
    basis = "tier0 handler, no PS4 pair"
    cls = pc_string.split("::")[0]
    f = facts.pc.get(pc_va)
    if f is None:
        return ProtoRow(pc_va, "", cur, "skip", basis, "no PC function record", (), ())
    if cls not in TIER0_CLASSES:
        return ProtoRow(pc_va, "", cur, "skip", basis, f"string class {cls}", (), ())
    regs = register_args(cur)
    if regs:
        return ProtoRow(pc_va, "", cur, "skip", basis, "IDA sees register argument(s) " + ",".join(regs), (), ())
    if gates.pc_has_this(facts, f) is not True:
        return ProtoRow(pc_va, "", cur, "skip", basis, "ecx this not proved", (), ())
    if set(f.ret_imm) != {4}:
        return ProtoRow(pc_va, "", cur, "skip", basis, f"ret {sorted(set(f.ret_imm))} is not ret 4", (), ())
    decl = f"int __thiscall({cls} *this, void *packet)"
    action = "equal" if cur == decl else ("conflict" if extra is not None and extra.prototype_user else "set")
    notes = "ecx this; ret 4; class from the PC string" + ("; current prototype is user-set"
                                                          if action == "conflict" else "")
    return ProtoRow(pc_va, decl, cur, action, basis, notes, (cls,), ())

