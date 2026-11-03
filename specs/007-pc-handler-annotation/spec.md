# 007 PC packet handler annotation (exact transfer from PS4)

**Status: open** (opened 2026-11-03; follows spec 006)

## Goal

Annotate the PC **03040008** IDA database's packet subsystem from the PS4 **02020005** database
(symbols + DWARF): function names, prototypes, structure and enum types, argument and local variable
names. Only facts proved to hold on PC are written; everything else stays as it is, listed with the
reason. Sam, 2026-11-03: "Anything that we can for sure tell is still the same in the PC binary is
what we should start with"; "the focus should be on the packet handlers"; the earlier agent (GPT,
ddon-hook specs 006-008) may have made mistakes, and its scripts may be unnecessary or wrong; "come up
with a new clean and efficient approach that avoids false positives".

Scope, in order: the S2C/L2C handlers of the PC handler table (`0x1bc0110`, 74 groups) and the login
handlers; the C2S/C2L send functions; the packet read/write functions and the `CData*` element
readers/writers they call; their direct helpers. Resources and other subsystems only where they are
helpers of these.

## Inputs

- PC base: ddon-hook's accepted database `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/feature008-field-map-property-working-20261029T161123Z/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (sha256 `382e346e...c58c0f`, `CURRENT-RECOVERY.json`). Work happens on a private copy of it; the
  result is published as a new folder beside it, never over it or the original.
- PS4: `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf.i64` (private copy),
  DWARF authority `binaries/PS4_02020005/elf-dumps/`, recompilation C++ for argument order.
- Seed pairs: `specs/006-packet-pattern-coverage/research/T001-triage.tsv` (PC handler VA -> PS4
  symbol, matched by code) and the 005/006 batch reports; wire layouts in `research/03040008/packets/`.
- The PC binary has no RTTI (2 `.?AV` strings) but carries its own handler names: 675 diagnostic
  strings `cSeed{Game,Login}SvConnection::OnPacket_<GROUP>_<NAME>` (T001 survey; counted 2026-11-03).
  PS4 names the same handlers `OnPacket_S2C_<NAME>` / `OnPacket_L2C_<NAME>` (802 symbols); by the
  `<NAME>` suffix 460 PC strings have exactly one PS4 symbol, 17 several, 198 none (mostly Season 3
  handlers, e.g. `ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES`). Other names come only from PS4
  through a proved pairing.
- The earlier work (survey `research/T001-prior-method.md`): 50 of 1,040 table handlers and one sender
  annotated, named from those PC strings; PS4 links by name similarity, all marked inferred; three
  pairs of byte-identical read helpers given different signed/bool names; 629 caller prototypes
  propagated by IDA unreviewed. Reused: its table reader logic (`ida_packet_dispatch.py`) and the
  1,041-entry catalog; nothing else is taken as evidence.

## Method: extract, match, apply, verify

1. **Extract** (IDA, read-only): one script per database dumps the facts the matcher needs to JSONL:
   per function its VA, size, instruction count, ordered call sites (target, argument count pushed),
   referenced strings and non-trivial constants, `this` use (ecx), stack cleanup (`ret N`), callers;
   per PS4 function also its symbol, DWARF prototype, parameter and local names/types, and per type its
   DWARF members. Dumps carry the database sha256 and the script version.
2. **Match** (offline Python over the dumps, tested): function pairs PC VA <-> PS4 symbol.
   - Tier 0 (PC alone, V): a handler-table entry whose function references exactly one
     `OnPacket_` diagnostic string takes that string as its name (the PC's own name); a string
     referenced from several functions or a function referencing several strings is listed, not named.
   - Seeds (PC <-> PS4): a tier-0 handler and the one PS4 `OnPacket_` symbol with the same `<NAME>`,
     passing gate (c) below and a body check (same reader/sender call shape); 006 matched handlers
     (must agree with these, a disagreement is a finding); functions sharing a string or constant set
     found in exactly one function on each side; vtable slots of a class named on both sides (MT DTI
     name string) when slot counts agree.
   - Propagation from a matched pair aligns the two ordered call sequences on calls already paired
     (never by raw position: the compilers inline differently) and proposes the callees between.
   - A pair is accepted only when **all** gates pass: (a) witnesses: two independent matched parents
     propose it, or one parent plus a non-trivial fingerprint agreement (strings/constants); (b)
     uniqueness: the PC function is proposed with only that PS4 function and vice versa, anywhere; a
     conflict rejects every pair involved; (c) shape: PC argument count and `this` use equal the
     DWARF parameter count (with `this`), no fingerprint contradiction; (d) not trivial: thunks,
     very short functions and widely shared helpers are not named by propagation (MSVC folds identical
     functions, so one PC address can stand for several PS4 functions: such a PC function gets no
     PS4 name, it is listed).
   - Precision check: rerun with 20% of the seeds withheld; every withheld seed the matcher pairs must
     come back with its own partner, else the gates are tightened before anything is applied.
3. **Transfer rules** per accepted pair:
   - Name: the PS4 symbol (demangled, qualified).
   - Prototype: calling convention and argument count/widths read from PC code; DWARF names for the
     arguments. A pointer argument gets a structure type only if that structure is transferred.
   - Structures: the PC 32-bit layout is computed from the DWARF members (pointer and vptr 4 bytes,
     MSVC x86 alignment) and accepted only if every member access the paired PC functions make lands
     on a predicted member start with its width, and the size agrees with an allocation or constructor
     where one exists. Layouts with no pointer-size-dependent member are still checked by access. A
     Season 3 difference makes the type partial (named members only where accesses agree) or leaves
     it out; never a 64-bit layout on PC. Enums transfer where the member or argument is transferred.
   - Locals: only a PC variable defined by a paired operation (the result of a paired callee, the
     address passed as a paired callee's argument) takes the PS4 DWARF local name of that operation's
     counterpart. Never by declaration order or position.
4. **Apply** (IDA, on the private copy): one idempotent script reads the accepted rows of the manifest,
   records each item's before-state (name, type, comment, locals) in an undo log, and writes. It never
   overwrites a non-default name or type (anything but `sub_`, `dword_`, ... ) of the earlier work; those
   conflicts are listed and settled one by one as corrections with a reason. Function comment:
   "PS4 02020005: <symbol>; paired by <basis>." Provenance stays in the manifest.
5. **Verify**: re-extract the applied database and compare with the manifest (every row written,
   nothing else changed: name/type counts before and after); decompile a stratified sample and check it
   reads correctly; an adversarial review re-derives a sample of pairs and types independently.

## Outputs

- `research/03040008/ida-transfer/`: the extract and apply scripts, the matcher (with tests), the
  manifest (`pairs.tsv`, `types.tsv`, `locals.tsv` with basis and gates) and the list of what was not
  transferred and why.
- The annotated database copy, published as `PC_DDON_03040008/spec007-packet-handlers-<date>/`.
- `research/` here: the survey of the earlier work, the audit of its packet annotations, the
  precision check, and the reviews.

## Evidence rules (binding)

- A pairing is proved by code (gates above); never by packet number, by name similarity, or by the
  server's (Arrowgene) names. PS4 flat packet numbers never name PC packets.
- IDA can misorder stack arguments: the PS4 recompilation C++ settles argument order where it has a body.
- Every row states its basis; anything not proved stays unwritten and listed. A check that did not run
  is "not run".
