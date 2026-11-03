"""Codec widths and the flattened codec tree of a reader or sender (T005e, role anchors).

Widths (T005b § 2):
- PC 03040008: the v3 dump's ``codec`` field (fixed widths); the four variable-length codecs, which the
  classifier leaves null by design, by their VA from T005b § 2.1 (disassembled there, V).
- PS4 02020005: the DWARF-named ``nPacket::Read_*`` / ``Write_*`` symbols (T005b § 2.2), because the v3
  classifier recognises only 4 of the 22 PS4 codecs (T005d § 3). The PS4 dump's ``codec`` field is only a
  cross-check (:func:`ps4_codec_crosscheck`).

Tokens: ``1 2 4 8`` fixed widths, ``S`` MtString (u16 length + bytes), ``B`` raw bytes, ``C`` C string.
Width carries no signedness or float/int on either side (T005b § 0).

Own code (no library fits): the tree walk over the dump's call lists and the embedding count, a small
dynamic programme over two token lists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .model import Facts, Func

# PC variable-length codecs (T005b § 2.1, V): classifier output is null for them by design.
PC_VARIABLE = {0x8BC5B0: ("read", "S"), 0x8BC710: ("read", "B"), 0x8BC790: ("write", "S"),
               0x8BCA30: ("write", "C")}
# PC helpers the walk never enters (T005b method): callOnPacketFunc, the allocator, the 64-bit swap
# helper inside the 8-byte codecs, WritePacket (header writer of senders).
PC_CALL_ON_PACKET = "cSeedGameSvConnection::callOnPacketFunc"
PC_WRITE_PACKET = "nUserSession::CPacket::WritePacket"
PC_SKIP_VA = {0x878860, 0x8BC2E0, 0x8BC340, 0x8BCBB0}
# getAllocator and the CRT memory/string routines (memcpy reaches the non-function 0x3468A01, T005d § 3)
PC_SKIP_NAME = re.compile(r"getAllocator|^_*(?:mem|str)[a-z_]*$")

PS4_CODEC = re.compile(r"^nPacket::(Read|Write)_(u8|s8|bool|u16|s16|u32|s32|f32|u64|s64|f64|MtString|bytes|MT_CSTR)$")
_PS4_TOKEN = {"u8": "1", "s8": "1", "bool": "1", "u16": "2", "s16": "2", "u32": "4", "s32": "4", "f32": "4",
              "u64": "8", "s64": "8", "f64": "8", "MtString": "S", "bytes": "B", "MT_CSTR": "C"}
PS4_READ_DESCEND = re.compile(r"^nPacket::Read_\w+$|(?:^|::)CPacket_\w+::ReadPacket$")
PS4_WRITE_DESCEND = re.compile(r"^nPacket::Write_\w+$")
PS4_ELEMENT_READER = re.compile(r"^nPacket::Read_CData\w*$")

MAX_DEPTH = 8


def pc_codec(facts: Facts, va: int) -> tuple[str, str] | None:
    """(dir, token) of a PC codec function, or None."""
    if va in PC_VARIABLE:
        return PC_VARIABLE[va]
    f = facts.pc.get(va)
    if f is not None and f.codec is not None:
        return f.codec[0], str(f.codec[1])
    return None


def ps4_codec(name: str) -> tuple[str, str] | None:
    m = PS4_CODEC.match(name)
    if not m:
        return None
    return ("read" if m.group(1) == "Read" else "write"), _PS4_TOKEN[m.group(2)]


def ps4_name(facts: Facts, va: int) -> str | None:
    f = facts.ps4.get(va)
    if f is not None:
        return f.name
    e = facts.externs.get(("ps4", va))
    return e[0] if e else None


def codec_of(facts: Facts, side: str, va: int) -> tuple[str, str] | None:
    if side == "pc":
        return pc_codec(facts, va)
    nm = ps4_name(facts, va)
    return ps4_codec(nm) if nm else None


def ps4_codec_crosscheck(facts: Facts) -> list[tuple[int, str, str, str]]:
    """(va, name, symbol token, dump token) for every PS4 codec symbol the dump classifies; disagreements
    are the rows whose two tokens differ."""
    out = []
    for f in sorted(facts.ps4.values(), key=lambda f: f.va):
        sym = ps4_codec(f.name)
        if sym is None or f.codec is None:
            continue
        out.append((f.va, f.name, f"{sym[0]}/{sym[1]}", f"{f.codec[0]}/{f.codec[1]}"))
    return out


@dataclass(frozen=True)
class Leaf:
    token: str
    dir: str
    codec: int  # codec function va
    site: int
    owner: int  # function holding the call site
    top: int  # the root's own call site under which the leaf lies


@dataclass(frozen=True)
class Bracket:
    va: int  # callee holding codecs
    site: int
    owner: int
    start: int  # first leaf index
    end: int  # one past the last leaf index
    depth: int  # 1 = called by the root


@dataclass
class Flat:
    root: int
    leaves: list[Leaf] = field(default_factory=list)
    brackets: list[Bracket] = field(default_factory=list)
    gaps: list[int] = field(default_factory=list)  # call targets the walk needed but the dump lacks

    @property
    def tokens(self) -> list[str]:
        return [x.token for x in self.leaves]


def _descend(facts: Facts, side: str, f: Func | None, va: int, mode: str) -> str:
    """'codec', 'enter', 'skip' or 'gap' for a call target."""
    if codec_of(facts, side, va) is not None:
        return "codec"
    if side == "pc":
        if va in PC_SKIP_VA:
            return "skip"
        if f is None:
            return "gap"
        if f.name in (PC_CALL_ON_PACKET, PC_WRITE_PACKET) or PC_SKIP_NAME.search(f.name):
            return "skip"
        if f.has_codec_distance and f.codec_distance is None:
            return "skip"  # v4: reaches no codec within 8 levels (T005h), not a coverage gap
        return "enter"
    nm = ps4_name(facts, va) or ""
    pat = PS4_READ_DESCEND if mode == "read" else PS4_WRITE_DESCEND
    if not pat.search(nm):
        return "skip"
    return "enter" if f is not None else "gap"


def flatten(facts: Facts, side: str, root: int, mode: str = "read") -> Flat:
    """Codec leaves of ``root`` in call-site order, recursing into callees (PC: every callee in the dump
    except the skip list and, on a v4 dump, those with a null ``codec_distance``; PS4: only
    ``nPacket::Read_*``/``CPacket_*::ReadPacket``, or ``nPacket::Write_*`` for mode 'write'). A callee
    holding no codec is no bracket. Indirect calls are skipped."""
    funcs = facts.pc if side == "pc" else facts.ps4
    out = Flat(root)

    def walk(va: int, depth: int, stack: tuple[int, ...], top: int | None) -> None:
        f = funcs.get(va)
        if f is None:
            return
        for c in f.calls:
            t = c.target
            if t is None:
                continue
            g = funcs.get(t)
            how = _descend(facts, side, g, t, mode)
            if how == "codec":
                d, tok = codec_of(facts, side, t)  # type: ignore[misc]
                if d == mode:
                    out.leaves.append(Leaf(tok, d, t, c.site, va, c.site if top is None else top))
            elif how == "gap":
                out.gaps.append(t)
            elif how == "enter":
                if t in stack or depth >= MAX_DEPTH:
                    out.gaps.append(t)
                    continue
                start = len(out.leaves)
                walk(t, depth + 1, (*stack, t), c.site if top is None else top)
                if len(out.leaves) > start:
                    out.brackets.append(Bracket(t, c.site, va, start, len(out.leaves), depth + 1))

    walk(root, 0, (root,), None)
    out.brackets.sort(key=lambda b: (b.start, -b.end, b.depth))
    return out


def count_embeddings(small: list[str], big: list[str], cap: int = 2) -> int:
    """Number of ways ``small`` is a subsequence of ``big``, capped at ``cap``."""
    n = len(small)
    ways = [1] + [0] * n
    for x in big:
        for i in range(n, 0, -1):
            if small[i - 1] == x:
                ways[i] = min(cap, ways[i] + ways[i - 1])
    return ways[n]


def leftmost_embedding(small: list[str], big: list[str]) -> list[int] | None:
    out, j = [], 0
    for x in small:
        while j < len(big) and big[j] != x:
            j += 1
        if j == len(big):
            return None
        out.append(j)
        j += 1
    return out
