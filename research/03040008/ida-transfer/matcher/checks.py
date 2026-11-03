"""Rule 5 (precision check by withheld seeds) and rule 6 (cross-checks against 006 T001 and 007 T002)."""

from __future__ import annotations

import csv
import random
import re
from dataclasses import dataclass
from pathlib import Path

from . import engine
from .model import Facts

HOLDOUT_FRACTION = 0.2
RNG_SEEDS = (1, 2, 3, 4, 5)


@dataclass(frozen=True)
class PrecisionRow:
    rng_seed: int
    seeds: int
    withheld: int
    recovered: int
    recovered_correctly: int
    recovered_wrongly: int
    accepted_pairs: int
    wrong: tuple[str, ...] = ()


def holdout(seeds: dict[int, int], rng_seed: int, fraction: float = HOLDOUT_FRACTION) -> set[int]:
    keys = sorted(seeds)
    return set(random.Random(rng_seed).sample(keys, round(len(keys) * fraction)))


def precision_run(facts: Facts, seeds: dict[int, int], rng_seed: int,
                  withheld: set[int] | None = None) -> PrecisionRow:
    """Run without the withheld seeds (20% by the fixed RNG seed unless given) and check each one the
    run pairs, from either side, against its seed partner."""
    if withheld is None:
        withheld = holdout(seeds, rng_seed)
    res = engine.run(facts, {k: v for k, v in seeds.items() if k not in withheld})
    by_pc = {p[0]: p[1] for p in res.accepted}
    by_ps4 = {p[1]: p[0] for p in res.accepted}
    rec = good = 0
    wrong: list[str] = []
    for pc_va in sorted(withheld):
        ps4_va = seeds[pc_va]
        got_ps4, got_pc = by_pc.get(pc_va), by_ps4.get(ps4_va)
        if got_ps4 is None and got_pc is None:
            continue
        rec += 1
        if got_ps4 == ps4_va and got_pc == pc_va:
            good += 1
        else:
            wrong.append(f"{pc_va:#x}->{got_ps4 and hex(got_ps4)} / {ps4_va:#x}<-{got_pc and hex(got_pc)}")
    return PrecisionRow(rng_seed, len(seeds), len(withheld), rec, good, rec - good, len(res.accepted), tuple(wrong))


def _hex(s: str) -> int | None:
    m = re.search(r"0x[0-9a-fA-F]+", s or "")
    return int(m.group(0), 16) if m else None


@dataclass(frozen=True)
class CrossRow:
    source: str
    key: str
    pc_va: int | None
    expected: str
    paired: str
    result: str


def crosscheck(facts: Facts, names: dict[int, str], pairs: set[tuple[int, int]],
               triage: Path, prior: Path) -> list[CrossRow]:
    """`names`: the PC name the run gives each paired PC va."""
    by_pc = {p[0]: p[1] for p in pairs}
    by_ps4 = {p[1]: p[0] for p in pairs}
    ps4_by_name: dict[str, list[int]] = {}
    for f in facts.ps4.values():
        ps4_by_name.setdefault(f.name, []).append(f.va)

    def link(source: str, key: str, pc_va: int | None, ps4_va: int | None, expected: str) -> CrossRow:
        got = by_pc.get(pc_va) if pc_va is not None else None
        paired = f"{got:#x} {facts.ps4[got].name}" if got is not None else "-"
        if ps4_va is None:
            result = "expected PS4 symbol not in the dump"
        elif got is None:
            other = by_ps4.get(ps4_va)
            result = f"disagree: PS4 side paired with PC {other:#x}" if other is not None else "not paired"
        else:
            result = "agree" if got == ps4_va else "disagree"
        return CrossRow(source, key, pc_va, expected, paired, result)

    rows: list[CrossRow] = []
    with triage.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["mark"] != "matched":
                continue
            rows.append(link("006-T001 matched", r["id"], _hex(r["pc_va"]), _hex(r["ps4_symbol"].split("@")[-1]),
                             r["ps4_symbol"]))
    with prior.open(encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    for r in csv.DictReader(lines, delimiter="\t"):
        if r["kind"] != "name":
            continue
        verdict, pc_va = r["verdict"], _hex(r["pc_va"])
        if verdict.startswith("holds") and "PS4 link unproved" not in verdict:
            m = re.search(r"PS4 (OnPacket_\w+) unique", verdict)
            sym = None
            if m:
                sym = "cSeedGameSvConnection::" + m.group(1)
            elif "unique tier-0 PS4 partner" in verdict:
                sym = r["value"]
            if sym is None:
                continue
            cands = ps4_by_name.get(sym, [])
            rows.append(link("T002 holds", r["role"], pc_va, cands[0] if len(cands) == 1 else None, sym))
        elif verdict.startswith("wrong"):
            ours = names.get(pc_va, "-")
            rows.append(CrossRow("T002 wrong", r["role"], pc_va, r["value"], ours,
                                 "reproduced" if ours == r["value"] else "not reproduced"))
    return rows
