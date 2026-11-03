007 T010: local variable names: feasibility and rules (evidence, wave 2)

Question (PC 03040008 <- PS4 02020005): Sam asked for local variable names as well. Spec 007 § 3: "only a PC
variable defined by a paired operation (the result of a paired callee, the address passed as a paired callee's
argument) takes the PS4 DWARF local name of that operation's counterpart. Never by declaration order or
position." How many locals can be named that way, and how exactly, without false positives?

Inputs: accepted pairs `research/03040008/ida-transfer/manifest/pairs.tsv` (972), DWARF locals in
`dumps/ps4-dwarf.jsonl` (name, type, lexical block, location expression/list), call sites in the dumps,
`manifest/callsites.tsv`. The PS4 IDA database has no DWARF locals (T002 § 5); the PC work copy has the wave-1
names and prototypes.

Work on 12 pairs (3 handlers, 3 readers, 3 element readers, 3 senders/requesters):
1. **PS4 binding**: for each DWARF local, the PS4 Hex-Rays lvar it is (stack locals: DWARF `fbreg`/`breg` offset
   to the lvar's stack location, mind the frame base; register locals: location list range and register at the
   lvar's definition), or "unbindable" with why. Measure how many bind uniquely.
2. **Operation link**: for each bound PS4 local, the paired operation that defines it: assigned from the return
   of a call to a callee that is itself paired (so the PC side has the counterpart callee), or whose address is
   passed at argument position k to a paired callee. Then the PC Hex-Rays lvar defined by the counterpart
   operation (PC call to the paired callee, same argument position). Require that the paired callee is called
   exactly once in each function, or that the call sites are already aligned by the matcher's anchors; else no
   link.
3. **Type check**: the PC lvar's size equals the DWARF local's 32-bit size (pointers 4); a mismatch refuses.
4. Count over all 972 pairs (a read-only batch script may decompile them all, both sides): bindable PS4 locals,
   linked ones, PC lvars that would be named, refusals by reason, and any PC lvar that two rules would name
   differently (must be zero, else describe).
5. Propose the rule set and its near-misses for an implementer (extractor additions or a separate batch
   script that writes `manifest/transfer/locals.tsv`; the apply step renames Hex-Rays lvars via
   `ida_hexrays.rename_lvar` / user lvar settings).

Databases: private copies only (`bash research/ida/private-copy.sh pc-accepted t010`, `... ps4 t010`; the
accepted PC copy lacks the 248 repairs, so use pairs whose PC function exists there, or a read-only batch on the
work copy `ddon-data-007work` ending with `DBFL_KILL`, checking its sha256 is unchanged); never open the work copy
in ida-mcp; delete private copies at the end.
Output: `specs/007-pc-handler-annotation/research/T010-locals.md` (+ a TSV of the 12-pair walk). Owns only those.
Never touch scripts, manifest, dumps, ddon-hook, client/, packets/.
Libraries: ida_hexrays (lvars, ctree), pyelftools data via the DWARF dump; stdlib.
Done: the report with counts and the proposal; final message with the path and at most 15 lines. Past 300k
context: write what is settled, end `cut short:`.
Stop: budget 150 min of work time. Base: the head when you start.
