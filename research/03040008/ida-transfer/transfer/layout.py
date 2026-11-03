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


def deref(t: str) -> str:
    """``t`` with one pointer or reference level removed (``T**`` -> ``T*``, ``T*&`` -> ``T*``), qualifiers stripped."""
    t = strip(t)
    return strip(t[:-1]) if t.endswith(("*", "&")) else t


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
            return TypeInfo("pointer", 4, 4, name=t, pointee=deref(t))
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
#
# T006b (README "Access check"): an access with a width must land on the start of a leaf member (scalar,
# pointer, enum, vptr) with exactly the leaf's width, recursing through bases, embedded structs and array
# elements; a whole aggregate read at once does not count. A ``lea`` (no width) must land on the object start,
# on the start of one of the object's own members (bases included), or on an element start of such an array
# member: never inside an embedded struct, because a ``lea`` names the address of a whole sub-object (an inner
# reader's ``this``), so an inner member start proves nothing. An indexed access must have a scale equal to
# the element size of an array member its displacement starts an element of. Anything else contradicts:
# padding, a byte inside a member, another width.


@dataclass(frozen=True)
class Landing:
    ok: bool
    path: tuple[str, ...]  # struct/union type names traversed, outermost first
    where: str  # member path or the reason
    hits: tuple[tuple[str, str], ...] = ()  # (type, member) at each level the access entered a member
    offs: tuple[int, ...] = ()  # the access's offset inside each type of ``path``


def land(info: TypeInfo, rel: int, width: int | None, indexed: bool = False, scale: int | None = None) -> Landing:
    """Does an access at ``rel`` of ``width`` bytes (None: ``lea``) fit the layout (rules above)?"""
    if rel < 0 or rel + (width or 0) > info.size or (width is None and rel >= info.size):
        return Landing(False, (info.name,), f"+{rel:#x} w{width} beyond size {info.size:#x}", (), (rel,))
    if indexed:
        return _indexed(info, rel, width, scale, (), (), "")
    if width is None:
        return _lea(info, rel, (), (), "")
    return _leaf(info, rel, width, (), (), "")


def _join(where: str, name: str) -> str:
    return f"{where}.{name}" if where else name


def _with_hit(t: str, m: str, r: Landing) -> Landing:
    return Landing(r.ok, r.path, r.where, ((t, m),) + r.hits, r.offs)


def _first(results: list[Landing]) -> Landing:
    for r in results:
        if r.ok:
            return r
    return results[0]


def _containing(info: TypeInfo, rel: int) -> list[Member]:
    return [m for m in info.members if m.offset <= rel < m.offset + m.size]


def _leaf(info: TypeInfo, rel: int, width: int, path: tuple[str, ...], offs: tuple[int, ...],
          where: str) -> Landing:
    if info.kind == "struct":
        path, offs = path + (info.name,), offs + (rel,)
        cands = _containing(info, rel)
        if not cands:
            return Landing(False, path, f"{where}+{rel:#x} in padding of {info.name}", (), offs)
        out = []
        for m in cands:
            r = rel - m.offset
            if m.kind == "vptr":
                ok = r == 0 and width == 4
                out.append(Landing(ok, path, "vptr" if ok else f"vptr: +{r} w{width}", (), offs))
            else:
                assert m.info is not None
                out.append(_leaf(m.info, r, width, path, offs, _join(where, m.name)))
            out[-1] = _with_hit(info.name, m.name, out[-1])
        return _first(out)
    if info.kind == "array":
        assert info.elem is not None
        i, r = divmod(rel, info.elem.size)
        return _leaf(info.elem, r, width, path, offs, f"{where}[{i}]")
    if rel != 0:
        return Landing(False, path, f"{where}: +{rel} into a {info.size}-byte member", (), offs)
    if width != info.size:
        return Landing(False, path, f"{where}: width {width} on a {info.size}-byte member", (), offs)
    return Landing(True, path, where, (), offs)


def _lea(info: TypeInfo, rel: int, path: tuple[str, ...], offs: tuple[int, ...], where: str) -> Landing:
    if info.kind == "array":
        assert info.elem is not None
        i, r = divmod(rel, info.elem.size)
        if r == 0:
            return Landing(True, path, f"{where}[{i}]", (), offs)
        if info.elem.kind == "array":
            return _lea(info.elem, r, path, offs, f"{where}[{i}]")
        return Landing(False, path, f"{where}[{i}]: lea +{r} inside a {info.elem.size}-byte element", (), offs)
    path, offs = path + (info.name,), offs + (rel,)
    if rel == 0:
        return Landing(True, path, where or "+0", (), offs)
    cands = _containing(info, rel)
    if not cands:
        return Landing(False, path, f"{where}+{rel:#x} in padding of {info.name}", (), offs)
    out = []
    for m in cands:
        r = rel - m.offset
        name = _join(where, m.name)
        if r == 0:
            res = Landing(True, path, name, (), offs)
        elif m.kind == "base":
            assert m.info is not None
            res = _lea(m.info, r, path, offs, name)
        elif m.kind == "array":
            assert m.info is not None
            res = _lea(m.info, r, path, offs, name)
        else:
            res = Landing(False, path, f"{name}: lea +{r} inside a {m.size}-byte {m.kind} member", (), offs)
        out.append(_with_hit(info.name, m.name, res))
    return _first(out)


def _indexed(info: TypeInfo, rel: int, width: int | None, scale: int | None, path: tuple[str, ...],
             offs: tuple[int, ...], where: str) -> Landing:
    if info.kind == "array":
        assert info.elem is not None
        i, r = divmod(rel, info.elem.size)
        if r == 0 and scale == info.elem.size:
            if width is None:
                return Landing(True, path, f"{where}[{i}]", (), offs)
            return _leaf(info.elem, 0, width, path, offs, f"{where}[{i}]")
        if info.elem.kind in ("array", "struct"):
            return _indexed(info.elem, r, width, scale, path, offs, f"{where}[{i}]")
        return Landing(False, path, f"{where}[{i}]+{r}: indexed, scale {scale} on {info.elem.size}-byte elements",
                       (), offs)
    if info.kind != "struct":
        return Landing(False, path, f"{where}: indexed access on a {info.size}-byte {info.kind}", (), offs)
    path, offs = path + (info.name,), offs + (rel,)
    cands = _containing(info, rel)
    if not cands:
        return Landing(False, path, f"{where}+{rel:#x} in padding of {info.name}", (), offs)
    out = []
    for m in cands:
        name = _join(where, m.name)
        if m.info is None or m.kind not in ("array", "struct", "base"):
            res = Landing(False, path, f"{name}: indexed access on a {m.size}-byte {m.kind} member", (), offs)
        else:
            res = _indexed(m.info, rel - m.offset, width, scale, path, offs, name)
        out.append(_with_hit(info.name, m.name, res))
    return _first(out)


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
