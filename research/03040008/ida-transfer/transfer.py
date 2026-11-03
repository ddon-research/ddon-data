"""007 T006: transfer rules (names, prototypes, types, comments) for the matcher's accepted pairs.

    uv run python transfer.py [--dumps dumps] [--pairs manifest/pairs.tsv] [--out manifest/transfer]
    uv run python transfer.py --wave2 [--out manifest/transfer/wave2]   # 007 T013c: partial types, locals

Reads the three dumps (sha256-checked against dumps/MANIFEST.tsv), the accepted rows of pairs.tsv (which must
equal the matcher's run on these dumps), the T002 audit and the T009 decisions (settled conflicts, T009b; path and
sha256 in the header); writes manifest/transfer/{names,prototypes,types,type_members,comments,skipped,precision,
summary}.tsv and types.h. Output is identical on rerun.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from matcher import checks, tier0
from matcher.model import load_facts
from transfer import decisions, run
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
    ap.add_argument("--decisions", type=Path,
                    default=REPO / "specs/007-pc-handler-annotation/research/T009-decisions.tsv")
    ap.add_argument("--no-holdout", action="store_true", help="skip rule 6 (tests)")
    ap.add_argument("--wave2", action="store_true", help="007 T013c: member links, partial types, locals")
    ap.add_argument("--wave1", type=Path, default=HERE / "manifest" / "transfer",
                    help="--wave2: wave 1's output (types.tsv, types.h: the types already in the work copy)")
    ap.add_argument("--callsites", type=Path, default=HERE / "manifest" / "callsites.tsv")
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
    if a.wave2:
        return wave2_main(a, facts, headers, pairs, t0, ps4fn, types)
    srcs = "; ".join(f"{n} source {h.get('input_sha256') or h.get('elf_sha256')}" for n, h in sorted(headers.items()))
    dec_path = a.decisions.resolve()
    dec_name = dec_path.relative_to(REPO).as_posix() if dec_path.is_relative_to(REPO) else dec_path.as_posix()
    srcs += f"; decisions {dec_name} {decisions.sha256(dec_path)}"
    title = f"007 T006 transfer, PC 03040008 <- PS4 02020005; {len(pairs)} accepted pairs; inputs: {srcs}"
    try:
        settled = decisions.read_decisions(dec_path)
        res = run.build(facts, pairs, pc, ps4fn, types, read_t002(a.prior), t0, title, settled)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    if not a.no_holdout:
        run.holdout(facts, t0, types, ps4fn, pairs, res)
    counts = run.write_all(a.out, res, Layouts(types), "# " + title)
    for k, v in counts.items():
        print(f"{k}\t{v}")
    return 0


def wave2_main(a, facts, headers, pairs, t0, ps4fn, types) -> int:
    """007 T013c: member links, partial types, locals, holdout and the reader-shuffle control
    (``manifest/transfer/wave2/``); the rule-3 call sites must equal the matcher's run (fail closed)."""
    from transfer import wave2, wave2_run

    out = a.out if a.out != HERE / "manifest" / "transfer" else HERE / "manifest" / "transfer" / "wave2"
    rows = wave2.read_callsites(a.callsites)
    seeds, _ = tier0.seed_candidates(facts, t0)
    full = checks.pipeline(facts, seeds, t0, tier0.group_prefixes(t0, facts))
    if wave2.callsite_rows(full.roles.callsites) != rows:
        print("callsites.tsv differs from the matcher run on these dumps", file=sys.stderr)
        return 2
    w1, w1_opaque = wave2.read_wave1_types(a.wave1 / "types.tsv")
    inp = wave2.Wave2Inputs(facts, wave2.load_args(a.dumps / "pc-ida.jsonl"),
                            wave2.load_args(a.dumps / "ps4-ida.jsonl"), ps4fn,
                            wave2.load_dwarf_fns(a.dumps / "ps4-dwarf.jsonl"), types, w1, w1_opaque,
                            t0, tier0.group_prefixes(t0, facts))
    pr = {(p.pc_va, p.ps4_va): p.rule for p in pairs}
    res = wave2_run.build(inp, pr, rows)
    if not a.no_holdout:
        wave2_run.holdout(inp, t0, res)
        wave2_run.control(inp, pr, rows, res)
    srcs = "; ".join(f"{n} source {h.get('input_sha256') or h.get('elf_sha256')}" for n, h in sorted(headers.items()))
    w1h = (a.wave1 / "types.h").read_text(encoding="utf-8")
    title = (f"007 T013c transfer wave 2, PC 03040008 <- PS4 02020005; {len(pairs)} accepted pairs; inputs: {srcs}; "
             f"wave 1 types.tsv {decisions.sha256(a.wave1 / 'types.tsv')}")
    counts = wave2_run.write_all(out, res, inp, w1h, "# " + title)
    for k, v in counts.items():
        print(f"{k}\t{v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
