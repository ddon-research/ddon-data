007 T001: survey the earlier PC packet-annotation work (method, outputs, likely errors)

Question (PC 03040008, seed PS4 02020005): an earlier agent (GPT, ddon-hook specs 006-008) annotated the
PC IDA database `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/feature008-field-map-property-working-20261029T161123Z/2022_01_29_DDO_DUMP_FIX.exe.i64`
from the PS4 one. Spec 007 will annotate the PC **packet handlers** (handler table at PC `0x1bc0110`, the
Send/Read/Write functions and their helpers) with names, prototypes, types and local names from PS4,
with a new method that admits no false positives. Before designing it we need to know what exists.

Report, packet subsystem first (resources only where they share helpers with packets):
1. **Method**: how it decided that a PC function is a given PS4 function (anchors, matching evidence,
   acceptance gates), how it chose prototypes, types, struct layouts and local names, and how it wrote
   and saved the database. Quote the rule and its file:line; keep it short.
2. **Outputs**: what it annotated in the database for packets (counts by kind: function names,
   prototypes, struct/enum types, locals, comments), where those lists live (receipts, catalogs,
   manifests, `ida_packet_*.py`), and which PC VAs / PS4 symbols each covers. Give the paths of any
   machine-readable PC VA <-> PS4 symbol list. Does it cover the handler table entries?
3. **Weak points**: claims whose stated evidence does not support them (e.g. a name from the community
   server, a match by packet number, by byte similarity alone, by position without a code check, a
   64-bit PS4 layout used on 32-bit PC, locals renamed by position), contradictions between its docs,
   and anything its own reviews or receipts flagged and did not fix. Each with file:line.
4. **Scripts**: for each `scripts/ida_packet_*.py`, `scripts/packet_*.py`, `recovery_bindings.py`,
   `verify_packet*.py`: one line on what it does, whether a clean method needs it, and any defect seen.
5. **Reusable**: facts and tables spec 007 can start from (with the evidence quality of each), and
   overlap with ddon-data's own matches: `specs/006-packet-pattern-coverage/research/T001-triage.tsv`
   (PC handler VA -> PS4 symbol, mark), and the 005/006 batch reports.

Source boundary: `C:/Users/morph/CLionProjects/ddon-hook/` (docs/investigations, notably 06, 08, 11, 12,
13, 14, 16, 32; scripts/; specs/006-recover-pc-packets, 007-harden-recovery-confidence,
008-recover-pc-resources incl. receipts, sample them, there are 5,560), `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/CURRENT-RECOVERY.json`.
Read large files by section (`rg -n` the headings first). No IDA: a later package checks the database.
Owns: `specs/007-pc-handler-annotation/research/T001-prior-method.md` only. Never touch ddon-hook, the
databases, client/, packets/.
Libraries: rg, jq, stdlib Python if a count needs it.
Done: the report with the five sections, every claim with file:line; a final message with the path and at
most 15 lines. Stop: budget 60 min of work time.
Base: 834c45de0e.
