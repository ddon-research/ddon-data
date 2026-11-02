006 R4: adversarial review of one risk: provenance marks that claim more than their evidence

Risk (one, named): spec 006 named 97 previously unknown packet fields (T014c, 58956082fd) and marked
78 of them V (code-backed). A V mark that rests on less than a data flow read in full, a name taken
from the server (Arrowgene) dressed as a code inference, or an I mark whose stated basis does not
lead to the name, would publish an inference as fact in `research/03040008/packets/` and the JSON.

Research question: for a stratified sample of the renamed fields, does the stated basis support the
mark and the name?

Sample: at least 20 fields: every `V (property name)` row, every row whose basis says `lead agrees`
(check the name is not simply the server's with a weak basis), every `I (elimination)` / `I (member
order)` row, plus random V rows from each include (Quest, Shop, Context, Craft, Server, Login, Item,
Character, Gacha, single patterns). Rows: `specs/006-packet-pattern-coverage/research/T014b-consumer-property-names.tsv`
and the md's eight parts; the pattern comments (`// T014b <mark>: <basis>`).

Per sampled field, reproduce the claim: re-read the cited VAs on a private copy (PC 03040008, PS4
02020005; `bash research/ida/private-copy.sh <pc|ps4> r4`, read-only) and check: the reader writes
the field to the cited storage; the cited consumer reads that storage; the name follows from what the
code shows (property string, UI text, PS4 DWARF member on the same path), not from Arrowgene
(`D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline`, lead only). Also check the JSON key in one exported
file per sampled pattern matches the pattern's name.

Report only reproduced findings, each with the field, the claimed mark/basis, what the code shows
(VAs), and the fix (lower the mark, rename, or `unk_*`). Owns nothing in the repository: final message
only (findings, then what was checked and not checked). Stop: budget 90 min of work time.
Base: the head when you start.
