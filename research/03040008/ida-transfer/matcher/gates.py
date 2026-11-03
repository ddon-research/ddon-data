"""Gates (a) witnesses, (c) shape and (d) not trivial; gate (b) lives in the engine (it needs the whole run)."""

from __future__ import annotations

import re

from .model import DwarfType, Facts, Func, Param

MIN_INSTRUCTIONS = 8
MAX_CALLERS = 64
MIN_CONSTANT = 0x10000

# Stack bytes on 32-bit x86 for the DWARF base types and typedefs whose PC width is known. Anything not
# here and not resolvable through the DWARF type records is unknown (gate (c) not met).
_FOUR = {
    "bool", "char", "signed char", "unsigned char", "short", "unsigned short", "short int",
    "short unsigned int", "int", "unsigned int", "float", "wchar_t", "char16_t", "char32_t",
    "u8", "s8", "u16", "s16", "u32", "s32", "b8", "b16", "b32", "f32", "BOOL", "DWORD", "WORD", "BYTE",
    # pointer-sized on PC (8 on PS4)
    "size_t", "ssize_t", "uintptr", "intptr", "uintptr_t", "intptr_t", "ptrdiff_t",
    # MT framework string pointer typedefs (const char* / char*), inferred from the MT naming
    "MT_CTSTR", "MT_STR",
}
_EIGHT = {"long long", "unsigned long long", "long long int", "long long unsigned int", "double",
          "u64", "s64", "f64", "int64_t", "uint64_t", "__int64"}
_QUALIFIER = re.compile(r"^(?:const|volatile)\s+|\s+(?:const|volatile)$")


def _strip(t: str) -> str:
    prev = None
    t = t.strip()
    while prev != t:
        prev, t = t, _QUALIFIER.sub("", t).strip()
    return t


def param_bytes(p: Param, types: dict[int, DwarfType]) -> int | None:
    """Bytes one DWARF parameter needs on the 32-bit x86 stack, or None when unknown."""
    t = _strip(p.type)
    if t.endswith(("*", "&")) or "(*" in t or "(&" in t:
        return 4
    seen: set[int] = set()
    die = p.type_die
    name = t
    while True:
        if name in _EIGHT:
            return 8
        if name in _FOUR:
            return 4
        rec = types.get(die) if die is not None else None
        if rec is None or die in seen:
            return None
        seen.add(die)
        if rec.tag == "enumeration":
            return 4
        if rec.tag == "typedef" and rec.target is not None:
            die, name = rec.target_die, _strip(rec.target)
            if name.endswith(("*", "&")) or "(*" in name or "(&" in name:
                return 4
            continue
        # class/structure/union by value: the 32-bit size is not known from the 64-bit DWARF
        return None


def dwarf_shape(facts: Facts, ps4_va: int) -> tuple[bool, int] | None:
    """(has object parameter, stack bytes of the other parameters) from DWARF, or None when unknown."""
    params = facts.dwarf_params.get(ps4_va)
    if params is None:
        return None
    has_this = bool(params) and params[0].artificial
    total = 0
    for p in params[1:] if has_this else params:
        if p.artificial:
            return None
        b = param_bytes(p, facts.types)
        if b is None:
            return None
        total += b
    return has_this, total


def _all_caller_sites(facts: Facts, f: Func) -> list | None:
    sites = facts.pc_callsites.get(f.va, [])
    if f.caller_sites == 0 or len(sites) != f.caller_sites:
        return None
    return sites


def pc_has_this(facts: Facts, f: Func) -> bool | None:
    """The extractor's ecx read-before-write, except that a function no caller site loads ecx for (every
    caller site in the dump, v3 ``ecx_loaded`` false at each) takes no object (T005e: MSVC's ``push ecx``
    stack reservation reads ecx in cdecl element readers)."""
    sites = _all_caller_sites(facts, f)
    if f.ecx_read_before_write and sites and all(c.ecx_loaded is False for c in sites):
        return False
    return f.ecx_read_before_write


def pc_stack_bytes(facts: Facts, f: Func) -> int | None:
    """`ret N` when every ret agrees; else the callers' v3 ``arg_bytes`` (``add esp, N`` after the call)
    when every caller site is in the dump and all agree; else their pushed bytes likewise; else None."""
    if f.ret_imm:
        vals = set(f.ret_imm)
        return vals.pop() if len(vals) == 1 else None
    sites = _all_caller_sites(facts, f)
    if sites is None:
        return None
    argb = {c.arg_bytes for c in sites}
    if len(argb) == 1 and None not in argb:
        return argb.pop()
    pushed = {c.pushed_bytes for c in sites}
    if len(pushed) != 1 or None in pushed:
        return None
    return pushed.pop()


def gate_c(facts: Facts, pc_va: int, ps4_va: int) -> tuple[bool, str]:
    f = facts.pc.get(pc_va)
    if f is None or ps4_va not in facts.ps4:
        return False, "no function record"
    d = dwarf_shape(facts, ps4_va)
    if d is None:
        return False, "DWARF parameter bytes unknown"
    this = pc_has_this(facts, f)
    if this is None:
        return False, "PC this unknown"
    pc_bytes = pc_stack_bytes(facts, f)
    if pc_bytes is None:
        return False, "PC stack bytes unknown"
    if this != d[0]:
        return False, f"this: PC ecx {this} DWARF {d[0]}"
    if pc_bytes != d[1]:
        return False, f"stack bytes: PC {pc_bytes} DWARF {d[1]}"
    return True, f"this={d[0]} bytes={d[1]}"


def big_constants(f: Func) -> frozenset[int]:
    return frozenset(c for c in f.constants if c >= MIN_CONSTANT)


def fingerprint(pc: Func, ps4: Func) -> str | None:
    """Reason the two agree (same non-empty string set, or same set of >= 2 constants >= 0x10000), or None."""
    if pc.strings and pc.strings == ps4.strings:
        return "strings"
    a, b = big_constants(pc), big_constants(ps4)
    if len(a) >= 2 and a == b:
        return "constants"
    return None


def gate_a(pc: Func, ps4: Func, witnesses: set) -> tuple[bool, str]:
    n = len(witnesses)
    if n >= 2:
        return True, f"{n} witnesses"
    if n == 1:
        fp = fingerprint(pc, ps4)
        if fp:
            return True, f"1 witness + {fp}"
        return False, "1 witness, no fingerprint"
    return False, "no witness"


def fold_key(f: Func) -> tuple:
    """Code identity proxy. The dumps carry no body bytes, so two PC functions count as folded copies when
    size, instruction count, ordered call targets, constants, strings, data refs, ret immediates and ecx use
    all agree. This over-approximates byte identity (which also never holds with rel32 calls), so gate (d)
    rejects at least every byte-identical function."""
    return (f.size, f.instructions, tuple(c.target for c in f.calls), tuple(sorted(f.constants)),
            tuple(sorted(f.strings)), tuple(sorted(f.data_refs)), tuple(sorted(f.ret_imm)), f.ecx_read_before_write)


def fold_groups(pc: dict[int, Func]) -> dict[int, list[int]]:
    """{pc va: the other PC functions with the same fold key} for every function in a group of 2+."""
    by: dict[tuple, list[int]] = {}
    for f in pc.values():
        by.setdefault(fold_key(f), []).append(f.va)
    out: dict[int, list[int]] = {}
    for vas in by.values():
        if len(vas) > 1:
            for v in vas:
                out[v] = sorted(x for x in vas if x != v)
    return out


def trivial_reasons(f: Func, folded: dict[int, list[int]] | None = None) -> list[str]:
    """Why one side's function may not be named by propagation (empty: not trivial)."""
    out = []
    if f.instructions < MIN_INSTRUCTIONS:
        out.append(f"{f.side} trivial: {f.instructions} instructions")
    if f.callers_count > MAX_CALLERS:
        out.append(f"{f.side} widely shared: {f.callers_count} callers")
    if folded is not None and f.va in folded:
        out.append(f"{f.side} folded: code-identical to " + " ".join(f"{v:#x}" for v in folded[f.va]))
    return out


def gate_d(pc: Func, ps4: Func, folded: dict[int, list[int]]) -> tuple[bool, str]:
    why = trivial_reasons(pc, folded) + trivial_reasons(ps4)
    return (False, "; ".join(why)) if why else (True, "ok")
