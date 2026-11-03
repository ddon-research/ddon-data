007 T005: the pair matcher with false-positive gates, the precision check and the pairs manifest

Objective (PC 03040008 <-> PS4 02020005): an offline, deterministic matcher over the T004 dumps that
pairs PC functions with PS4 functions and admits no false positives. Read
`specs/007-pc-handler-annotation/spec.md` § Method step 2, `research/T002-audit.md` (tier-0 counts, the
codec pairs, the wrong and unsourced earlier names) and `research/T004b-extract-run.md` (dump facts).

Inputs: `research/03040008/ida-transfer/dumps/{pc-ida,ps4-ida,ps4-dwarf}.jsonl` (check each header's
sha256 against `dumps/MANIFEST.tsv`), `specs/006-packet-pattern-coverage/research/T001-triage.tsv`,
`specs/007-pc-handler-annotation/research/T002-prior-annotations.tsv`.

Rules (each a function with its own tests):
1. **Tier 0 (PC alone)**: a table callback that references exactly one `cSeed*Connection::OnPacket_*`
   string, a string referenced by no other function, takes that string as its PC name. Anything else
   (several strings, a shared string, a string outside a callback) is listed with the reason.
2. **Seeds**: a tier-0 function and the one PS4 `OnPacket_{S2C,L2C}_<NAME>` symbol whose `<NAME>` is
   the PC string's suffix after the group token(s), exactly one candidate (17 PC strings had several:
   list them, no seed). Seeds also need gate (c).
3. **Propagation** from every accepted pair (P, S): align the ordered call sites of P and S on the call
   sites whose targets are already a pair with each other (anchors; also identical import/extern
   targets). Between two consecutive anchors (or the body ends), a gap with exactly one unpaired call on
   each side proposes that callee pair, with (P, S) as its witness. Never by raw position across gaps
   of any other size. PS4 inlined calls (`ps4-dwarf` inlined subroutines) are not call sites; report how
   often a gap is uneven only because of a PS4 inline, as data for a later relaxation, without using it.
4. **Gates**, all required for acceptance:
   (a) witnesses: at least 2 distinct witness pairs, or 1 witness plus a fingerprint agreement: both
       reference the same non-empty set of strings, or the same set of at least 2 constants >= 0x10000;
   (b) uniqueness: across all proposals in the run, the PC function is proposed with exactly one PS4
       function and that one with exactly one PC function; any conflict rejects every pair involved,
       now and in later iterations (record the conflict set);
   (c) shape: PC `this` (ecx read before write) iff the DWARF prototype has an object parameter; the PC
       stack argument bytes (`ret N`, else the callers' push bytes when all callers agree) equal the bytes
       the DWARF parameters need on 32-bit x86 (each parameter rounded up to 4; 64-bit integers and
       doubles 8; by-value structs their 32-bit size: unknown size = gate not met). Unknown on either side
       = not met;
   (d) not trivial: fewer than 8 instructions, or more than 64 callers on either side, or a PC function
       whose body is byte-identical to another PC function (MSVC folding), is not accepted by
       propagation; list it with the reason. (T002's codec pairs: list both, accepted only if a tier-0 or
       string fingerprint pairs them, which is not expected.)
   Iterate propagation to a fixed point; a pair once rejected by (b) stays rejected.
5. **Precision check**: rerun with 20% of the seeds withheld (fixed RNG seed, 5 different seeds). For
   every withheld seed that the run pairs, the partner must be its seed partner. Report, per run,
   withheld / recovered / recovered-correctly / recovered-wrongly, and the accepted-pair count. Any
   wrong recovery is a failure: tighten the gate that let it through, with a test reproducing it, and
   rerun; never relax a gate to raise coverage in this package.
6. **Cross-checks**: every 006 `T001-triage.tsv` `matched` row and every T002 `holds` PS4 link must agree
   with the pairs (a disagreement is listed, not resolved by preference); T002 `wrong` rows must not be
   reproduced.

Outputs in `research/03040008/ida-transfer/manifest/` (committed, TSV, deterministic order):
`pairs.tsv` (pc_va, ps4_va, ps4_symbol, pc_name_source (pc-string | ps4-symbol), tier, witnesses, gate
results, status), `rejected.tsv` (candidate, gate failed, detail), `conflicts.tsv`, `precision.tsv`,
`crosscheck.tsv`. A `match.py` CLI (`uv run python match.py`) regenerates them; output identical on rerun.

Owns: `research/03040008/ida-transfer/{match.py,matcher/**,tests/**,manifest/**}` and its README section.
Never touch the extractors' behaviour (report a defect instead), the dumps, the databases, ddon-hook,
client/, packets/, other specs.
Libraries: stdlib (`difflib` is not suited to anchored gaps; say what you used), pytest, ruff; networkx only
if a graph algorithm is needed.
Done: tests for each rule and gate, including a synthetic folded-function case, a conflict case, an uneven
gap, and a holdout case that would mis-pair without gate (b) or (c); `uv run pytest`, ruff,
`bash tools/check.sh --since <base>`; the manifest with counts (tier 0, seeds, accepted by iteration,
rejected by gate, conflicts) and the precision table in the receipt; signed commits with
`git commit -m <msg> -- <paths>`. Stop: budget 180 min of work time; stop and ask if the precision check
fails twice after tightening.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
