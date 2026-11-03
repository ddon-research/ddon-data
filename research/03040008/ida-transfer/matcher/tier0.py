"""Rule 1 (tier 0, PC alone) and rule 2 (seeds by the PS4 OnPacket_ symbol name)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .model import Facts

ONPACKET_STRING = re.compile(r"^cSeed\w*Connection::OnPacket_(\w+)$")
PS4_ONPACKET = re.compile(r"^cSeed\w*Connection::OnPacket_(?:S2C|L2C)_(\w+)$")


@dataclass(frozen=True)
class Listed:
    candidate: str
    gate: str
    detail: str


def tier0(facts: Facts) -> tuple[dict[int, str], list[Listed]]:
    """Return {callback va: PC string} for the table callbacks that take their string as name, plus the rest."""
    referrers: dict[str, set[int]] = {}
    for f in facts.pc.values():
        for s in f.strings:
            if ONPACKET_STRING.match(s):
                referrers.setdefault(s, set()).add(f.va)
    named: dict[int, str] = {}
    listed: list[Listed] = []
    for cb in sorted(facts.table_callbacks):
        f = facts.pc.get(cb)
        if f is None:
            listed.append(Listed(f"pc:{cb:#x}", "tier0", "table callback has no function record"))
            continue
        strs = sorted(s for s in f.strings if ONPACKET_STRING.match(s))
        if not strs:
            listed.append(Listed(f"pc:{cb:#x}", "tier0", "references no OnPacket_ string"))
        elif len(strs) > 1:
            listed.append(Listed(f"pc:{cb:#x}", "tier0", "references several OnPacket_ strings: " + " ".join(strs)))
        elif len(referrers[strs[0]]) > 1:
            others = " ".join(f"{v:#x}" for v in sorted(referrers[strs[0]] - {cb}))
            listed.append(Listed(f"pc:{cb:#x}", "tier0", f"shared string {strs[0]} (also referenced by {others})"))
        elif strs[0] in facts.onpacket_orphan_strings:
            listed.append(Listed(f"pc:{cb:#x}", "tier0",
                                 f"shared string {strs[0]} (also referenced from outside any function)"))
        else:
            named[cb] = strs[0]
    for s in sorted(referrers):
        outside = sorted(referrers[s] - facts.table_callbacks)
        if outside:
            listed.append(Listed(f"string:{s}", "tier0",
                                 "string referenced outside a callback by " + " ".join(f"{v:#x}" for v in outside)))
    return named, listed


def group_prefixes(tier0_names: dict[int, str], facts: Facts) -> dict[int, list[str]]:
    """Common token prefix of the tier-0 strings of each table group (tokens of the text after OnPacket_)."""
    by_group: dict[int, list[list[str]]] = {}
    for cb, s in tier0_names.items():
        by_group.setdefault(facts.table_group[cb], []).append(ONPACKET_STRING.match(s).group(1).split("_"))
    out: dict[int, list[str]] = {}
    for g, toks in by_group.items():
        common: list[str] = []
        for column in zip(*toks, strict=False):
            if len(set(column)) != 1:
                break
            common.append(column[0])
        out[g] = common
    return out


def candidate_names(pc_string: str, prefix: list[str]) -> list[str]:
    """PS4 <NAME>s for a PC string: the suffix after 1..len(prefix) group tokens, keeping a non-empty name."""
    toks = ONPACKET_STRING.match(pc_string).group(1).split("_")
    limit = min(len(prefix), len(toks) - 1)
    return ["_".join(toks[k:]) for k in range(1, limit + 1) if toks[:k] == prefix[:k]]


def ps4_onpacket_index(facts: Facts) -> dict[str, list[int]]:
    idx: dict[str, list[int]] = {}
    for f in facts.ps4.values():
        m = PS4_ONPACKET.match(f.name)
        if m:
            idx.setdefault(m.group(1), []).append(f.va)
    return {k: sorted(v) for k, v in idx.items()}


def seed_candidates(facts: Facts, tier0_names: dict[int, str]) -> tuple[dict[int, int], list[Listed]]:
    """Rule 2 without gate (c): {pc va: ps4 va} where the name rule gives exactly one PS4 function (searched
    in every cSeed*Connection class), of the PC string's own connection class, and that PS4 function is
    the candidate of no other PC string."""
    prefixes = group_prefixes(tier0_names, facts)
    idx = ps4_onpacket_index(facts)
    single: dict[int, int] = {}
    listed: list[Listed] = []
    for cb in sorted(tier0_names):
        s = tier0_names[cb]
        names = candidate_names(s, prefixes[facts.table_group[cb]])
        cands = sorted({v for n in names for v in idx.get(n, [])})
        if not cands:
            listed.append(Listed(f"pc:{cb:#x}", "seed", f"{s}: no PS4 OnPacket_ symbol for {' / '.join(names) or '-'}"))
        elif len(cands) > 1:
            listed.append(Listed(f"pc:{cb:#x}", "seed", f"{s}: several PS4 candidates "
                                 + " ".join(f"{facts.ps4[v].name}@{v:#x}" for v in cands)))
        elif facts.ps4[cands[0]].name.split("::")[0] != s.split("::")[0]:
            # 006 cross-check: BAZAAR_GET_CHARACTER_LIST_RES (game) found only the login
            # GET_CHARACTER_LIST_RES; a candidate of another connection class is no seed.
            listed.append(Listed(f"pc:{cb:#x}", "seed", f"{s}: the only PS4 candidate "
                                 f"{facts.ps4[cands[0]].name}@{cands[0]:#x} is of another connection class"))
        else:
            single[cb] = cands[0]
    claims: dict[int, list[int]] = {}
    for cb, v in single.items():
        claims.setdefault(v, []).append(cb)
    out: dict[int, int] = {}
    for cb, v in sorted(single.items()):
        if len(claims[v]) > 1:
            listed.append(Listed(f"pc:{cb:#x}", "seed", f"PS4 {facts.ps4[v].name}@{v:#x} is also the candidate of "
                                 + " ".join(f"{c:#x}" for c in claims[v] if c != cb)))
        else:
            out[cb] = v
    return out, listed
