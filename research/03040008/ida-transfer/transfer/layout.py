"""PC (MSVC x86, 32-bit) layout of a PS4 02020005 DWARF type, computed from its declared members.

Rules (README "Layout rules"; one test each in tests/test_transfer_layout.py):

- L1 scalars: fixed-width typedefs and base types by their PC size; ``long`` / ``wchar_t`` / ``long double``
  differ between the PS4 ABI and MSVC and are refused unless reached through a fixed-width typedef.
- L2 pointers, references and function pointers: 4 bytes, align 4; pointer-sized typedefs (``size_t``,
  ``uintptr_t``, ...) likewise. Pointers to members are refused (MSVC size depends on the class).
- L3 alignment: natural, capped at 8 (``/Zp8``): ``double`` and 64-bit integers align to 8.
- L4 dynamic classes: a class that declares the vptr (DWARF artificial ``_vptr$`` member) and has no dynamic
  base gets a 4-byte vptr at offset 0; a class with a dynamic base shares the base's vptr.
- L5 base classes come first, at their own alignment; an empty base (no data, no vptr) takes no space.
  Only single non-virtual inheritance is modelled; several bases are refused.
- L6 members follow in declaration order, each at the next offset aligned to its alignment; a union puts every
  member at 0. The size is rounded up to the alignment; an empty class has size 1. MSVC never reuses a base's
  tail padding (Itanium may), which this computes by construction.
- L7 refusals: bitfields, virtual bases, declaration-only types, types that cannot be resolved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

QUALIFIER = re.compile(r"^(?:const|volatile)\s+|\s+(?:const|volatile)$")
ARRAY = re.compile(r"^(.*?)((?:\[\d+\])+)$")

# (size, C type for IDA) of the base types whose size is the same under MSVC x86
BASE = {
    "bool": (1, "bool"), "char": (1, "char"), "signed char": (1, "signed __int8"),
    "unsigned char": (1, "unsigned __int8"), "short": (2, "__int16"), "short int": (2, "__int16"),
    "unsigned short": (2, "unsigned __int16"), "short unsigned int": (2, "unsigned __int16"),
    "int": (4, "int"), "unsigned int": (4, "unsigned int"), "long long": (8, "__int64"),
    "long long int": (8, "__int64"), "unsigned long long": (8, "unsigned __int64"),
    "long long unsigned int": (8, "unsigned __int64"), "float": (4, "float"), "double": (8, "double"),
    "char16_t": (2, "unsigned __int16"), "char32_t": (4, "unsigned int"),
}
# typedef names whose width is fixed by name on every MT platform, checked before the typedef chain
FIXED = {"u64": (8, "unsigned __int64"), "uint64_t": (8, "unsigned __int64"), "__uint64_t": (8, "unsigned __int64"),
         "s64": (8, "__int64"), "int64_t": (8, "__int64"), "__int64_t": (8, "__int64")}
# pointer-sized integer typedefs: 4 bytes on PC (8 on PS4)
POINTER_SIZED = {"size_t": "unsigned int", "uintptr_t": "unsigned int", "uintptr": "unsigned int",
                 "ssize_t": "int", "intptr_t": "int", "intptr": "int", "ptrdiff_t": "int"}
ABI_DEPENDENT = {"long", "long int", "unsigned long", "long unsigned int", "wchar_t", "long double"}


class LayoutError(Exception):
    pass


def strip(t: str) -> str:
    prev = None
    t = t.strip()
    while prev != t:
        prev, t = t, QUALIFIER.sub("", t).strip()
    return t


@dataclass
class Member:
    name: str
    offset: int
    size: int
    kind: str  # scalar | pointer | enum | struct | array | vptr | base
    type: str  # DWARF type string (vptr: "vptr")
    info: TypeInfo | None = None


@dataclass
class TypeInfo:
    kind: str  # scalar | pointer | enum | struct | array
    size: int
    align: int
    name: str = ""  # scalar: C type; enum/struct: DWARF name; pointer: pointee string
    elem: TypeInfo | None = None
    count: int = 0
    members: list[Member] = field(default_factory=list)
    dynamic: bool = False
    empty: bool = False
    union: bool = False
    pointee: str | None = None


def align_up(n: int, a: int) -> int:
    return (n + a - 1) // a * a


class Layouts:
    """Resolve DWARF type strings to PC layouts; ``types`` maps a DWARF type name to its record."""

    def __init__(self, types: dict[str, dict]) -> None:
        self.types = types
        self.cache: dict[str, TypeInfo | LayoutError] = {}

    def record(self, name: str) -> dict | None:
        return self.types.get(name)

    def resolve(self, t: str, _seen: frozenset[str] = frozenset()) -> TypeInfo:
        t = strip(t)
        if "::*" in t:
            raise LayoutError(f"pointer to member {t}")
        m = ARRAY.match(t)
        if m:
            dims = [int(d) for d in re.findall(r"\[(\d+)\]", m.group(2))]
            info = self.resolve(m.group(1), _seen)
            for n in reversed(dims):
                info = TypeInfo("array", info.size * n, info.align, elem=info, count=n)
            return info
        if t.endswith(("*", "&")):
            return TypeInfo("pointer", 4, 4, name=t, pointee=strip(t.rstrip("&").rstrip("*").rstrip("&")))
        if t in FIXED:
            s, c = FIXED[t]
            return TypeInfo("scalar", s, s, name=c)
        if t in POINTER_SIZED:
            return TypeInfo("scalar", 4, 4, name=POINTER_SIZED[t])
        if t in BASE:
            s, c = BASE[t]
            return TypeInfo("scalar", s, s, name=c)
        if t in ABI_DEPENDENT:
            raise LayoutError(f"{t}: size differs between the PS4 ABI and MSVC x86")
        if t in _seen:
            raise LayoutError(f"{t}: recursive by value")
        rec = self.types.get(t)
        if rec is None:
            raise LayoutError(f"{t}: no DWARF type record")
        tag = rec["tag"]
        if tag == "typedef":
            if rec.get("other_definitions"):
                raise LayoutError(f"{t}: typedef with several definitions")
            return self.resolve(rec["target"], _seen | {t})
        if tag == "enumeration":
            if not rec.get("size"):
                raise LayoutError(f"{t}: enum without size")
            return TypeInfo("enum", rec["size"], rec["size"], name=t)
        return self.layout(t, _seen | {t})

    def layout(self, name: str, _seen: frozenset[str] = frozenset()) -> TypeInfo:
        hit = self.cache.get(name)
        if isinstance(hit, LayoutError):
            raise hit
        if hit is not None:
            return hit
        try:
            info = self._layout(name, _seen | {name})
        except LayoutError as e:
            self.cache[name] = e
            raise
        self.cache[name] = info
        return info

    def _layout(self, name: str, seen: frozenset[str]) -> TypeInfo:
        rec = self.types.get(name)
        if rec is None or rec["tag"] not in ("class", "structure", "union"):
            raise LayoutError(f"{name}: no class/structure/union record")
        if rec.get("declaration") or rec.get("size") is None:
            raise LayoutError(f"{name}: declaration only")
        if rec.get("other_definitions"):
            raise LayoutError(f"{name}: several definitions")
        members = rec.get("members") or []
        for m in members:
            if m.get("bit_size") is not None:
                raise LayoutError(f"{name}: bitfield {m['name']}")
        bases = rec.get("bases") or []
        if any(b.get("virtual") for b in bases):
            raise LayoutError(f"{name}: virtual base")
        if len(bases) > 1:
            raise LayoutError(f"{name}: {len(bases)} bases (multiple inheritance not modelled)")
        union = rec["tag"] == "union"
        own_vptr = any(m.get("artificial") and m["name"].startswith("_vptr") for m in members)
        out: list[Member] = []
        offset, align = 0, 1
        base_info = None
        if bases:
            try:
                base_info = self.layout(bases[0]["name"], seen)
            except LayoutError as e:
                raise LayoutError(f"{name}: base {bases[0]['name']}: {e}") from None
        dynamic = own_vptr or bool(base_info and base_info.dynamic)
        if own_vptr and not (base_info and base_info.dynamic):
            out.append(Member("vptr", 0, 4, "vptr", "vptr"))
            offset, align = 4, 4
        if base_info is not None and not base_info.empty:
            off = align_up(offset, base_info.align)
            out.append(Member(bases[0]["name"], off, base_info.size, "base", bases[0]["name"], base_info))
            offset, align = off + base_info.size, max(align, base_info.align)
        data = 0
        for m in members:
            if m.get("static") or m.get("artificial"):
                continue
            try:
                info = self.resolve(m["type"], seen)
            except LayoutError as e:
                raise LayoutError(f"{name}: member {m['name']}: {e}") from None
            a = min(info.align, 8)
            off = 0 if union else align_up(offset, a)
            out.append(Member(m["name"] or f"anon{off:X}", off, info.size,
                              "struct" if info.kind == "struct" else info.kind, m["type"], info))
            offset = max(offset, off + info.size) if union else off + info.size
            align = max(align, a)
            data += 1
        empty = not dynamic and data == 0 and (base_info is None or base_info.empty)
        size = 1 if empty else align_up(offset, align)
        return TypeInfo("struct", size, align, name=name, members=out, dynamic=dynamic, empty=empty, union=union)


# --- landing an access on a layout -------------------------------------------------------------------------


@dataclass(frozen=True)
class Landing:
    ok: bool
    path: tuple[str, ...]  # struct/union type names traversed, outermost first
    where: str  # member path or the reason
    hits: tuple[tuple[str, str], ...] = ()  # (type, member) at each level the access entered a member


def land(info: TypeInfo, rel: int, width: int | None) -> Landing:
    """Does an access at ``rel`` of ``width`` bytes (None: ``lea``) land on a member start of that size?"""
    if rel < 0 or rel + (width or 0) > info.size or (width is None and rel >= info.size):
        return Landing(False, (info.name,), f"+{rel:#x} w{width} beyond size {info.size:#x}")
    return _land(info, rel, width, (), "")


def _land(info: TypeInfo, rel: int, width: int | None, path: tuple[str, ...], where: str) -> Landing:
    if info.kind == "struct":
        path = path + (info.name,)
        if rel == 0 and (width is None or width == info.size):
            return Landing(True, path, where or "+0")
        cands = [m for m in info.members if m.offset <= rel < m.offset + m.size]
        if not cands:
            return Landing(False, path, f"{where}+{rel:#x} in padding of {info.name}")
        best = None
        for m in cands:
            r = _member(m, rel - m.offset, width, path, f"{where}.{m.name}" if where else m.name)
            r = Landing(r.ok, r.path, r.where, ((info.name, m.name),) + r.hits)
            if r.ok:
                return r
            best = best or r
        return best
    if info.kind == "array":
        assert info.elem is not None
        if rel == 0 and (width is None or width == info.size):
            return Landing(True, path, where)
        i, r = divmod(rel, info.elem.size)
        return _land(info.elem, r, width, path, f"{where}[{i}]")
    # scalar / pointer / enum
    if rel != 0:
        return Landing(False, path, f"{where}: +{rel} into a {info.size}-byte member")
    if width is not None and width != info.size:
        return Landing(False, path, f"{where}: width {width} on a {info.size}-byte member")
    return Landing(True, path, where)


def _member(m: Member, rel: int, width: int | None, path: tuple[str, ...], where: str) -> Landing:
    if m.kind == "vptr":
        if rel == 0 and width in (None, 4):
            return Landing(True, path, "vptr")
        return Landing(False, path, f"vptr: +{rel} w{width}")
    assert m.info is not None
    return _land(m.info, rel, width, path, where)


def member_at(info: TypeInfo, rel: int) -> Member | None:
    """The innermost non-aggregate member starting at ``rel`` (for ``via`` loads), else None."""
    if info.kind == "array" and info.elem is not None:
        return member_at(info.elem, rel % info.elem.size)
    if info.kind != "struct":
        return None
    for m in info.members:
        if m.offset <= rel < m.offset + m.size:
            if m.kind in ("struct", "base", "array"):
                assert m.info is not None
                return member_at(m.info, rel - m.offset)
            return m if rel == m.offset else None
    return None


def declarable(name: str) -> bool:
    """A type name T007 can declare: any DWARF name except anonymous ones (``<anon@...>``). Template names
    (``MtTypedArray<CDataX>``) are kept verbatim; IDA's tinfo API takes them (README, T007 note)."""
    return bool(name) and "<anon" not in name
