"""Seeds + propagation to a fixed point under gates (a)-(d)."""

from __future__ import annotations

from dataclasses import dataclass, field

from . import gates
from .model import Facts
from .propagate import GapStats, Pair, gap_proposals


@dataclass
class Accepted:
    pc: int
    ps4: int
    source: str  # "seed" | "propagation"
    iteration: int
    witnesses: tuple[Pair, ...]
    gate_results: str


@dataclass
class Result:
    accepted: dict[Pair, Accepted]
    proposals: dict[Pair, set[Pair]]  # every proposal of the final pass -> witnesses
    failed: dict[Pair, list[tuple[str, str]]]  # proposals never accepted -> [(gate, detail)]
    rejected_b: set[Pair]
    conflicts: dict[tuple[str, int], set[Pair]]  # (side, va) -> the pairs that conflict there
    seed_failed: dict[Pair, str]  # seed candidates refused by gate (c)
    gap_stats: GapStats
    restarts: int
    by_iteration: dict[int, int] = field(default_factory=dict)


def find_conflicts(pairs: set[Pair]) -> dict[tuple[str, int], set[Pair]]:
    by_pc: dict[int, set[Pair]] = {}
    by_ps4: dict[int, set[Pair]] = {}
    for p in pairs:
        by_pc.setdefault(p[0], set()).add(p)
        by_ps4.setdefault(p[1], set()).add(p)
    out: dict[tuple[str, int], set[Pair]] = {}
    for va, ps in by_pc.items():
        if len(ps) > 1:
            out[("pc", va)] = ps
    for va, ps in by_ps4.items():
        if len(ps) > 1:
            out[("ps4", va)] = ps
    return out


def run(facts: Facts, seed_candidates: dict[int, int], max_iterations: int = 1000) -> Result:
    folded = gates.fold_groups(facts.pc)
    seed_ok: dict[Pair, str] = {}
    seed_failed: dict[Pair, str] = {}
    for pc_va, ps4_va in sorted(seed_candidates.items()):
        ok, why = gates.gate_c(facts, pc_va, ps4_va)
        (seed_ok if ok else seed_failed)[(pc_va, ps4_va)] = why
    rejected_b: set[Pair] = set()
    conflicts: dict[tuple[str, int], set[Pair]] = {}
    restarts = 0
    while True:
        res = _pass(facts, seed_ok, folded, rejected_b, conflicts, max_iterations)
        if res is not None:
            accepted, proposals, failed, stats, by_it = res
            return Result(accepted, proposals, failed, rejected_b, conflicts, seed_failed, stats, restarts, by_it)
        restarts += 1


def _pass(facts, seed_ok, folded, rejected_b, conflicts, max_iterations):
    accepted: dict[Pair, Accepted] = {}
    for p, why in seed_ok.items():
        if p not in rejected_b:
            accepted[p] = Accepted(p[0], p[1], "seed", 0, (), f"c={why}")
    ledger: dict[Pair, set[Pair]] = {}
    failed: dict[Pair, list[tuple[str, str]]] = {}
    stats = GapStats()
    by_it: dict[int, int] = {0: len(accepted)}
    for it in range(1, max_iterations + 1):
        pc_side = {p[0]: p[0] for p in accepted}
        ps4_side = {p[1]: p[0] for p in accepted}
        stats = GapStats()
        for w in sorted(accepted):
            props, st = gap_proposals(facts.pc[w[0]], facts.ps4[w[1]], pc_side, ps4_side,
                                      facts.dwarf_inlines.get(w[1]))
            stats.merge(st)
            for p in props:
                ledger.setdefault(p, set()).add(w)
        new_conf = find_conflicts(set(ledger) | set(accepted))
        for k, ps in new_conf.items():
            conflicts.setdefault(k, set()).update(ps)
            rejected_b.update(ps)
        if any(p in rejected_b for p in accepted):
            return None  # an accepted pair lost uniqueness: restart without it
        new: list[Pair] = []
        failed = {}
        for p in sorted(ledger):
            if p in accepted:
                continue
            why = _evaluate(facts, p, ledger[p], folded, rejected_b)
            if why is None:
                new.append(p)
            else:
                failed[p] = why
        if not new:
            return accepted, ledger, failed, stats, by_it
        for p in new:
            pc, ps4 = facts.pc[p[0]], facts.ps4[p[1]]
            _, wa = gates.gate_a(pc, ps4, ledger[p])
            _, wc = gates.gate_c(facts, *p)
            accepted[p] = Accepted(p[0], p[1], "propagation", it, tuple(sorted(ledger[p])),
                                   f"a={wa}; b=unique; c={wc}; d=ok")
        by_it[it] = len(new)
    raise RuntimeError("propagation did not reach a fixed point")


def _evaluate(facts, p, witnesses, folded, rejected_b) -> list[tuple[str, str]] | None:
    pc, ps4 = facts.pc.get(p[0]), facts.ps4.get(p[1])
    if pc is None or ps4 is None:
        side = "PC" if pc is None else "PS4"
        return [("record", f"{side} callee not in the dump")]
    fails: list[tuple[str, str]] = []
    ok, why = gates.gate_a(pc, ps4, witnesses)
    if not ok:
        fails.append(("a", why))
    if p in rejected_b:
        fails.append(("b", "conflict"))
    ok, why = gates.gate_c(facts, *p)
    if not ok:
        fails.append(("c", why))
    ok, why = gates.gate_d(pc, ps4, folded)
    if not ok:
        fails.append(("d", why))
    return fails or None
