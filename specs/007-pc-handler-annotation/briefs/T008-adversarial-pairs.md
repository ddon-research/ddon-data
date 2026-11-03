007 T008: adversarial review: are any applied pairs, names, prototypes or types wrong?

Claim to falsify (PC 03040008 <- PS4 02020005): every row written to the work copy by T007e is true on PC: each
pair is the same source function, each name and prototype follows from it, and the `MtTypedArray<X>` layout
(20 bytes, the one accepted struct layout) matches PC code. The matcher and transfer passed a precision holdout
and a shuffled control, but T007b's spot checks still found one contradicted type the gates had accepted
(`CHANGE_JOB_RES`, fixed in T006b/c). Find the next such error.

Sample (stratified, fixed RNG seed stated in the report), from
`research/03040008/ida-transfer/manifest/pairs.tsv` and `manifest/transfer/*.tsv`:
- 8 pairs per rule: seeds (handlers), rule 1 readers, rule 2 element readers, rule 4 requesters, rule 4 senders;
  plus every pair whose gate (a) had exactly one witness, up to 10.
- 10 prototypes (at least 3 `__stdcall`/`__cdecl`, 3 with a 64-bit or float argument).
- The `MtTypedArray<X>` layout: 5 different X, each with one PC reader that touches it.
- 5 tier-0 handlers without a PS4 pair (name from the PC string only).
Per item, derive independently from the disassembly, without reading the matcher's witnesses first: the PC
function's role and body (callees, codec width sequence, constants), the PS4 function's (symbol, DWARF
prototype, body), and decide same function / not / undecidable; for prototypes, argument count and widths from
PC stack use and callers; for the layout, each access offset/width. Only then compare with the row.

Tools: read-only headless batch scripts (`idat -A -S<script>`) on private copies you make
(`bash research/ida/private-copy.sh pc-accepted t008`, `... ps4 t008`; delete them after) and the dumps in
`research/03040008/ida-transfer/dumps/` (`pc-ida-applied.jsonl` is the applied state); never open
`ddon-data-007work`. Report only reproduced findings, each with VAs, what the code shows and the fix; then
what was checked and found right, with counts per stratum.
Owns: `specs/007-pc-handler-annotation/research/T008-adversarial.md` and your scratchpad. Never edit tracked
files other than that report, the databases, ddon-hook, client/, packets/.
Stop: budget 120 min of work time. Base: the head when you start.
