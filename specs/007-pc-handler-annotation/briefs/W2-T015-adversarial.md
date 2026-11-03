007 W2 T015: adversarial review: are any wave-2 partial types or local names wrong?

Claim to falsify (PC 03040008 <- PS4 02020005): every wave-2 row written by T013d is true on PC: each partial
packet type's members sit at the PC offsets given with the PS4 member's width and meaning, and each renamed local
is the variable the PS4 DWARF local names. Wave 1's review (T008) found two tooling defects the gates missed, and
the wave-2 control first let wrong single-member types through. Find the next error.

Sample (fixed RNG seed in the report): 16 of the 48 partial types (incl. `CHANGE_JOB_RES`, 4 `CData*`, and every
type with a single member), all 24 locals (`manifest/transfer/wave2/`). Per item, derive from the disassembly
before reading the row's evidence: PC: which instruction writes the member (codec destination `lea`, store), its
offset and width, in which paired reader; PS4: the same codec position's destination member (DWARF) in the paired
PS4 reader; for a `packet` local, the PC handler's stack object passed to the reader and the PS4 DWARF `packet`
local; for R1, the paired callee's argument. Then compare with the row. Also try two attacks: (1) a member link
that comes from a codec call whose PC and PS4 positions were aligned only because the width sequence is ambiguous
(check `callsites.tsv` alignment status), (2) a partial type whose lower-bound size cuts a member that PC code
accesses beyond the bound.

Tools: read-only headless batch scripts (`idat -A -S<script>`, `DBFL_KILL` + `qexit`) on private copies
(`bash research/ida/private-copy.sh pc-accepted w2r`, `... ps4 w2r`; delete after) and the dumps; the applied state
is the published wave-2 database (read it only through a batch on a `cp` of it in
`PC_DDON_03040008/ddon-data-w2r-applied/`, deleted after). Never open `ddon-data-007work`.
Report only reproduced findings (VAs, what the code shows, the fix), then what was checked and found right per
stratum. Write the report as your final message (your role's hook allows writes only to
`.agent-ledger/canaries/`; put canaries there, `007-W2/`); the coordinator files it as
`specs/007-pc-handler-annotation/research/W2-T015-adversarial.md`.
Stop: budget 120 min of work time. Base: the head when you start.
