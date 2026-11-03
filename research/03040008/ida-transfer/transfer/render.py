"""types.h and the member rows of types.tsv for the transferred types.

Every struct is written packed (``#pragma pack(push, 1)``) with explicit ``gap`` members, so IDA lays it out at
exactly the computed PC offsets whatever its own alignment rules. A member whose type is not transferred is
written as bytes (``unsigned __int8 name[size]``) with the DWARF type in the comment; a pointer to a class that is
not transferred points to an opaque ``struct X;``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .layout import Layouts, Member, TypeInfo
from .prototypes import ctype


@dataclass(frozen=True)
class MemberRow:
    type: str
    member: str
    offset: int
    size: int
    decl: str
    dwarf_type: str
    checked: str  # VAs or "-"


@dataclass
class Rendered:
    header: str
    members: list[MemberRow]
    opaque: set[str] = field(default_factory=set)
    enums: set[str] = field(default_factory=set)


def anon(name: str) -> bool:
    return "<anon" in name or not name


def _decl(m: Member, emitted: set[str], enums: set[str], layouts: Layouts, opaque: set[str],
          used_enums: set[str]) -> tuple[str, str]:
    """(declarator text without ';', comment) for one member."""
    name = m.name if not anon(m.name) else f"anon_{m.offset:X}"
    if m.kind == "vptr":
        return "void *__vftable", "vptr"
    info = m.info
    assert info is not None
    if m.kind == "base":
        if info.name in emitted:
            return f"{info.name} baseclass_{m.offset:X}", f"base {info.name}"
        return f"unsigned __int8 baseclass_{m.offset:X}[{m.size}]", f"base {info.name} (not transferred)"
    dims = ""
    t = info
    while t.kind == "array":
        dims += f"[{t.count}]"
        assert t.elem is not None
        t = t.elem
    if t.kind == "struct":
        if t.name in emitted:
            return f"{t.name} {name}{dims}", ""
        return f"unsigned __int8 {name}[{m.size}]", f"{m.type} (not transferred)"
    if t.kind == "enum":
        if t.name in enums and t.size == 4:
            used_enums.add(t.name)
            return f"{t.name} {name}{dims}", ""
        return f"{_int(t.size)} {name}{dims}", f"enum {t.name}"
    if t.kind == "scalar":
        return f"{t.name} {name}{dims}", ""
    # pointer
    c = ctype(t.name, layouts)
    for x in c.classes:
        if x not in emitted:
            opaque.add(x)
    used_enums |= c.enums & enums
    if c.enums - enums:
        return f"void *{name}{dims}", t.name
    sep = "" if c.text.endswith("*") else " "
    return f"{c.text}{sep}{name}{dims}", (c.note or "")


def _int(size: int) -> str:
    return {1: "unsigned __int8", 2: "unsigned __int16", 4: "unsigned int", 8: "unsigned __int64"}.get(size, "int")


def order(names: set[str], layouts: Layouts) -> list[str]:
    """Emitted types, each after the types it embeds (bases, members, array elements)."""
    out: list[str] = []
    done: set[str] = set()

    def deps(info: TypeInfo) -> list[str]:
        res = []
        for m in info.members:
            t = m.info
            while t is not None and t.kind == "array":
                t = t.elem
            if t is not None and t.kind == "struct" and t.name in names:
                res.append(t.name)
        return res

    def visit(n: str) -> None:
        if n in done:
            return
        done.add(n)
        for d in deps(layouts.layout(n)):
            visit(d)
        out.append(n)

    for n in sorted(names):
        visit(n)
    return out


def render(emitted: set[str], enums: dict[str, dict], layouts: Layouts, checked: dict[str, dict[str, set[int]]],
           proto_classes: set[str], title: str) -> Rendered:
    opaque: set[str] = set()
    used_enums: set[str] = set()
    rows: list[MemberRow] = []
    bodies: list[str] = []
    for name in order(emitted, layouts):
        info = layouts.layout(name)
        kw = "union" if info.union else "struct"
        lines = [f"{kw} {name} // PC size {info.size:#x}"]
        lines.append("{")
        pos = 0
        for m in sorted(info.members, key=lambda m: (m.offset, m.name)) if not info.union else info.members:
            if not info.union and m.offset > pos:
                lines.append(f"  unsigned __int8 gap{pos:X}[{m.offset - pos}];")
            d, note = _decl(m, emitted, set(enums), layouts, opaque, used_enums)
            lines.append(f"  {d}; // +{m.offset:#x} {m.size}" + (f" {note}" if note else ""))
            vas = checked.get(name, {}).get(m.name if m.kind != "vptr" else "vptr", set())
            rows.append(MemberRow(name, m.name, m.offset, m.size, d, m.type,
                                  " ".join(f"{v:#x}" for v in sorted(vas)[:8]) + (" ..." if len(vas) > 8 else "")
                                  or "-"))
            pos = max(pos, m.offset + m.size) if info.union else m.offset + m.size
        if info.union and pos < info.size:
            lines.append(f"  unsigned __int8 whole[{info.size}];")
        elif not info.union and pos < info.size:
            lines.append(f"  unsigned __int8 gap{pos:X}[{info.size - pos}];")
        lines.append("};")
        bodies.append("\n".join(lines))
    opaque |= {c for c in proto_classes if c not in emitted}
    parts = [f"// {title}", "// Generated by transfer.py; PC 03040008 layouts computed from PS4 02020005 DWARF.", ""]
    for e in sorted(set(enums)):
        rec = enums[e]
        vals = ",\n".join(f"  {_enum_name(n)} = {v}" for n, v in rec["enumerators"])
        parts.append(f"enum {e} // DWARF size {rec['size']}\n{{\n{vals}\n}};\n")
    for o in sorted(opaque):
        parts.append(f"struct {o};")
    parts.append("")
    parts.append("#pragma pack(push, 1)")
    parts.extend(b + "\n" for b in bodies)
    parts.append("#pragma pack(pop)")
    return Rendered("\n".join(parts) + "\n", rows, opaque, used_enums)


def _enum_name(n: str) -> str:
    return n


def member_enums(emitted: set[str], layouts: Layouts) -> set[str]:
    """4-byte enums that members of the emitted types use by value or through a pointer."""
    out: set[str] = set()
    for name in emitted:
        for m in layouts.layout(name).members:
            t = m.info
            while t is not None and t.kind == "array":
                t = t.elem
            if t is None:
                continue
            if t.kind == "enum" and t.size == 4:
                out.add(t.name)
            elif t.kind == "pointer":
                out |= ctype(t.name, layouts).enums
    return out


def enum_collisions(enums: dict[str, dict]) -> dict[str, str]:
    """{enum: reason} for enums whose enumerator names another emitted enum already uses (IDA keeps enumerator
    names unique); the first enum by name keeps them."""
    seen: dict[str, str] = {}
    out: dict[str, str] = {}
    for e in sorted(enums):
        names = [n for n, _ in enums[e]["enumerators"]]
        clash = sorted({seen[n] for n in names if n in seen})
        if clash:
            out[e] = "enumerator names also in " + ", ".join(clash)
            continue
        for n in names:
            seen[n] = e
    return out
