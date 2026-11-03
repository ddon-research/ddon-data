"""007 T006: transfer rules (names, prototypes, types, comments) for the matcher's accepted pairs.

    uv run python transfer.py [--dumps dumps] [--pairs manifest/pairs.tsv] [--out manifest/transfer]

Reads the three dumps (sha256-checked against dumps/MANIFEST.tsv), the accepted rows of pairs.tsv (which must
equal the matcher's run on these dumps) and the T002 audit; writes manifest/transfer/{names,prototypes,types,
type_members,comments,skipped,precision,summary}.tsv and types.h. Output is identical on rerun.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from matcher import tier0
from matcher.model import load_facts
from transfer import run
from transfer.inputs import load_dumps, pairs_sources_match, read_pairs, read_t002
from transfer.layout import Layouts

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dumps", type=Path, default=HERE / "dumps")
    ap.add_argument("--pairs", type=Path, default=HERE / "manifest" / "pairs.tsv")
    ap.add_argument("--out", type=Path, default=HERE / "manifest" / "transfer")
    ap.add_argument("--prior", type=Path,
                    default=REPO / "specs/007-pc-handler-annotation/research/T002-prior-annotations.tsv")
    ap.add_argument("--no-holdout", action="store_true", help="skip rule 6 (tests)")
    a = ap.parse_args(argv)
    facts, headers = load_facts(a.dumps)
    pairs, head = read_pairs(a.pairs)
    if not pairs_sources_match(head, headers):
        print("pairs.tsv was built from other dumps", file=sys.stderr)
        return 2
    t0, _ = tier0.tier0(facts)
    why = run.full_pairs_check(facts, t0, pairs)
    if why:
        print(why, file=sys.stderr)
        return 2
    pc, ps4fn, types = load_dumps(a.dumps)
    srcs = "; ".join(f"{n} source {h.get('input_sha256') or h.get('elf_sha256')}" for n, h in sorted(headers.items()))
    title = f"007 T006 transfer, PC 03040008 <- PS4 02020005; {len(pairs)} accepted pairs; inputs: {srcs}"
    res = run.build(facts, pairs, pc, ps4fn, types, read_t002(a.prior), t0, title)
    if not a.no_holdout:
        run.holdout(facts, t0, types, ps4fn, pairs, res)
    counts = run.write_all(a.out, res, Layouts(types), "# " + title)
    for k, v in counts.items():
        print(f"{k}\t{v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
