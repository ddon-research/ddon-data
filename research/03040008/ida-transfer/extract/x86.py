"""x86 register names and helpers shared by the extractor modules (pure, no IDA import)."""

from __future__ import annotations

import re

PS4_INT_ARG_REGS = ("rdi", "rsi", "rdx", "rcx", "r8", "r9")
_REG_ALIASES = {
    "rax": ("eax", "ax", "al", "ah"), "rcx": ("ecx", "cx", "cl", "ch"),
    "rdx": ("edx", "dx", "dl", "dh"), "rbx": ("ebx", "bx", "bl", "bh"),
    "rsp": ("esp", "sp", "spl"), "rbp": ("ebp", "bp", "bpl"),
    "rsi": ("esi", "si", "sil"), "rdi": ("edi", "di", "dil"),
}
_CANON = {alias: full for full, aliases in _REG_ALIASES.items() for alias in aliases}


def canon_reg(name: str | None) -> str | None:
    """Full 64-bit register name for any width alias (``edi``/``dil`` -> ``rdi``, ``r8d`` -> ``r8``)."""
    if not name:
        return None
    name = name.lower()
    if name in _CANON:
        return _CANON[name]
    m = re.fullmatch(r"(r(?:8|9|1[0-5]))[dwb]?", name)
    if m:
        return m.group(1)
    m = re.fullmatch(r"[xyz]mm(\d+)", name)
    if m:
        return f"xmm{m.group(1)}"
    return name


def signed(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    return value - (1 << bits) if value >> (bits - 1) else value



# Instructions that move esp in a way pc_const_args does not model (the stack picture is dropped).
_ESP_OPAQUE = {"pusha", "pushad", "popa", "popad", "pushf", "pushfd", "popf", "popfd", "enter", "leave"}


def is_padding_nop(ins: dict, ptr: int | None = None) -> bool:
    """An MSVC padding nop ``lea r, [r+0]`` (``lea ecx,[ecx+0]``, ``lea esi,[esi+0]``): same register,
    no index, displacement 0, pointer width when ``ptr`` is given (a 32-bit ``lea`` of a 64-bit register
    zero-extends: no nop) (v6, T012 § 2 item 2). It changes nothing and is no operation."""
    ops = ins.get("ops", [])
    if ins.get("mnem") != "lea" or len(ops) != 2 or ops[0].get("type") != "reg":
        return False
    src = ops[1]
    return (src.get("type") in ("phrase", "displ") and src.get("index") is None and not src.get("addr")
            and src.get("base") is not None and canon_reg(src.get("base")) == canon_reg(ops[0].get("reg"))
            and ops[0].get("size") == (ptr or ops[0].get("size")) and ops[0].get("size") in (4, 8))
