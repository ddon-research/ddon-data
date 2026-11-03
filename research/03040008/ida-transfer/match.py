"""007 T005: pair PC 03040008 functions with PS4 02020005 functions from the T004 dumps.

    uv run python match.py [--dumps dumps] [--out manifest]

Writes manifest/{pairs,rejected,conflicts,precision,crosscheck,summary}.tsv; output is identical on rerun.
Exits 1 when the precision check recovers a withheld seed with the wrong partner.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from matcher import checks, engine, report, tier0
from matcher.model import load_facts

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dumps", type=Path, default=HERE / "dumps")
    ap.add_argument("--out", type=Path, default=HERE / "manifest")
    ap.add_argument("--triage", type=Path,
                    default=REPO / "specs/006-packet-pattern-coverage/research/T001-triage.tsv")
    ap.add_argument("--prior", type=Path,
                    default=REPO / "specs/007-pc-handler-annotation/research/T002-prior-annotations.tsv")
    a = ap.parse_args(argv)
    facts, headers = load_facts(a.dumps)
    t0, t0_listed = tier0.tier0(facts)
    seeds, seed_listed = tier0.seed_candidates(facts, t0)
    res = engine.run(facts, seeds)
    precision = [checks.precision_run(facts, seeds, s) for s in checks.RNG_SEEDS]
    names = {pc: nm for pc, (nm, _) in report.pc_names(facts, res, t0).items()}
    cross = checks.crosscheck(facts, names, set(res.accepted), a.triage, a.prior)
    counts = report.write_all(a.out, facts, headers, t0, t0_listed, seeds, seed_listed, res, precision, cross)
    for k, v in counts.items():
        print(f"{k}\t{v}")
    for r in precision:
        print(f"precision rng {r.rng_seed}: withheld {r.withheld} recovered {r.recovered} "
              f"correct {r.recovered_correctly} wrong {r.recovered_wrongly} accepted {r.accepted_pairs}")
    return 1 if any(r.recovered_wrongly for r in precision) else 0


if __name__ == "__main__":
    sys.exit(main())
