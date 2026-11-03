"""007 T005e/T005h: pair PC 03040008 functions with PS4 02020005 functions from the v3+ dumps.

    uv run python match.py [--dumps dumps] [--out manifest]

Seeds and propagation (T005), then the role anchors (T005e: reader, element reader, codec positions,
listener slot). Writes manifest/{pairs,callsites,rejected,conflicts,precision,control,crosscheck,summary}.tsv;
output is identical on rerun. Exits 1 when the precision check finds a wrong pair or the negative control
accepts a pair.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from matcher import checks, report, tier0
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
    prefixes = tier0.group_prefixes(t0, facts)
    full = checks.pipeline(facts, seeds, t0, prefixes)
    precision = [checks.precision_run(facts, seeds, s) for s in checks.RNG_SEEDS]
    role_prec = [checks.role_precision(facts, seeds, t0, prefixes, full, s) for s in checks.RNG_SEEDS]
    control = [checks.negative_control(facts, seeds, t0, prefixes, full, s) for s in checks.RNG_SEEDS]
    names = {pc: nm for pc, (nm, _) in report.pc_names(facts, full.engine, t0, full.roles).items()}
    cross = checks.crosscheck(facts, names, set(full.pairs()), a.triage, a.prior)
    cross += checks.crosscheck_t005b(facts, full)
    counts = report.write_all(a.out, facts, headers, t0, t0_listed, seeds, seed_listed, full, precision,
                              role_prec, control, cross)
    for k, v in counts.items():
        print(f"{k}\t{v}")
    for r, q in zip(precision, role_prec, strict=True):
        print(f"precision rng {r.rng_seed}: withheld {r.withheld}; seeds recovered {r.recovered} "
              f"(wrong {r.recovered_wrongly}); role pairs dependent {q.dependent} absent {q.dependent_absent} "
              f"same {q.dependent_same} wrong {q.wrong} new {q.new}")
    for c in control:
        print(f"control rng {c.rng_seed}: proposals {c.proposals} accepted {c.accepted} "
              f"(= real run {c.accepted_agree_real}, not in real run {c.accepted_wrong})")
    bad = (any(r.recovered_wrongly for r in precision) or any(q.wrong for q in role_prec)
           or any(c.accepted_agree_real + c.accepted_wrong for c in control))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
