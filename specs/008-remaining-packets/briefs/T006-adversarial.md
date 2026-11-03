008 T006: adversarial review: are any 008 layouts, marks or names wrong?

Claim to falsify (client 03040008): the 115 patterns of spec 008 (T003-T005; reports `specs/008-remaining-packets/research/T00[345]-*.md`)
decode every capture correctly, follow the PC readers/writers, and carry marks that do not overstate their basis:
`V` only where PC code was read, `I (<basis>)` only where the stated basis leads to the name (value counts that rule
out coincidence: not 0/1 flags, not small enums), `G` for guesses. A JSON that "fits" can still be misdecoded
(e.g. a u16+u16 read as u32, a list count read as a field) and a G name can be presented as fact.

Sample (fixed RNG seed in the report): 20 ids stratified by batch and direction, plus every id whose layout differs
from the Arrowgene structure (T001 `ag_vs_pc`), every renamed packet (11.7.16, 72.1.16, ...), and every `I (value: ...)`
mark. Per id, independently of the pattern: decode 2 captures from the raw bytes with the PC reader's codec
sequence (T001 TSV `width_seq`, re-read in IDA for 5 of them), compare with the JSON; check that each `V` cites a
PC VA that reads that field; re-run each sampled `I (value)` correlation and check its counts and that coincidence
is ruled out; check the packet renames against their stated evidence.

Tools: stdlib Python over raws/JSON; IDA read-only by headless batch on a `cp` of the wave-2 database in
`PC_DDON_03040008/ddon-data-t006r/` (`DBFL_KILL` + `qexit`; deleted after); never `ddon-data-007work` or the
original/accepted databases. Report only reproduced findings (id, field, what the bytes/code show, the fix), then
what was checked and found right per stratum. Canaries under `.agent-ledger/canaries/008-T006/`; the report is your
final message (the coordinator files it as `specs/008-remaining-packets/research/T006-adversarial.md`).
Stop: budget 120 min of work time. Base: the head when you start.
