007 T006: transfer rules: names, prototypes and structure types for the accepted pairs (wave 1)

Objective (PC 03040008 <- PS4 02020005): from the matcher's accepted pairs and the dumps, the rows T007 will
write, each with its basis, and the list of what is not written and why (spec 007 § Method step 3). Wave 1:
names, prototypes (argument names and types), structure/enum types. Local variable names are wave 2.
Read `specs/007-pc-handler-annotation/spec.md` § 3-4, `research/T002-audit.md` (earlier names: holds /
wrong / unsourced), the T005e receipt in `tasks.md`, and the v4 dump fields (T005f README).

Inputs: `research/03040008/ida-transfer/manifest/pairs.tsv` (rerun `match.py` first on the current dumps),
`dumps/{pc-ida,ps4-ida,ps4-dwarf}.jsonl`, `specs/007-pc-handler-annotation/research/T002-prior-annotations.tsv`.

Rules (`transfer/` package, each a function with tests):
1. **Names** (`names.tsv`): tier-0 callbacks take their PC string (V, PC alone), whether or not paired;
   other accepted pairs take the demangled qualified PS4 symbol. Against the PC function's current name:
   default name -> set; equal -> nothing; different non-default -> `conflict` unless T002 rates it `wrong` or
   `no source`, or it is a PS4-form spelling of the PC string (`correct`, reason quoted). A name may not be
   used twice (MSVC folding): a second use -> both listed, neither set. The 3 labels left at old starts
   (T004f: 0x7C5C8D, 0x7D714C, 0x7D858F) -> `remove-label` rows.
2. **Prototypes** (`prototypes.tsv`, C declaration strings for IDA): calling convention from PC code (`this`
   in ecx -> `__thiscall`; else `ret N` -> `__stdcall`, plain `ret` -> `__cdecl`); argument count and widths
   from gate (c); names from DWARF parameters. Types: DWARF base types mapped by size and encoding (bool,
   char, signed/unsigned 8/16/32/64, float, double; DWARF typedef names such as `u32` only if the typedef is
   transferred too); pointers/references to a class -> pointer to that class, declared opaque
   (`struct X;`) unless rule 3 transfers its layout (naming a pointee by its source class adds no layout
   claim); anything else (function pointers, by-value class arguments, unknown) -> the width-sized integer
   with the DWARF type in the comment. Tier-0 handlers without a PS4 pair: `int __thiscall
   <name>(cSeedGameSvConnection *this, void *packet)` only if the dump proves ecx this, one stack argument
   (`ret 4`) and the class from the string (check how T002 verified it); the login class likewise.
3. **Types** (`types.tsv` + `types.h`): candidates are the class types of `this` and of pointer arguments
   of accepted pairs, and their member and base types, recursively. Compute the PC 32-bit layout from the
   DWARF members (MSVC x86: vptr 4 at 0 for dynamic classes, pointers 4, natural alignment capped at 8,
   base classes first, empty-base rules; give the rules in the README with a test per rule). Refuse a type
   with bitfields, virtual bases, or members whose type cannot be laid out. **Access check**: every v4
   object-relative access (argument index, disp, width) that a paired PC function makes through an argument
   of that type must land on a member start with a matching size (recursing into embedded structs/arrays),
   or the vptr; no access beyond the computed size. Accept a type only with zero contradictions over all
   paired functions and at least one checked access, and when the size agrees with any constant allocation
   size or `ret`-checked constructor that the dumps show; record checked / unchecked members and the
   evidence (insn VAs). A contradiction (Season 3 growth) -> refused with the offsets. Enums referenced by
   accepted members or prototypes: DWARF enum as is (values do not depend on layout).
4. **Comments** (`comments.tsv`): one function comment per written function: "PS4 02020005: <symbol>; paired
   by <rule>." or "PC name from string at <va>." plus Season 3 notes from the pair row; never overwrite a
   non-empty existing comment: append below a separator line.
5. **Not written** (`skipped.tsv`): every candidate not written, with the rule and reason.
6. A precision note: re-run T005e's holdout for the transfer: types accepted with a withheld seed must
   stay accepted from the remaining witnesses, or be listed as depending on it.

Outputs `research/03040008/ida-transfer/manifest/transfer/`, deterministic; a `transfer.py` CLI.
Owns: `research/03040008/ida-transfer/{transfer.py,transfer/**,tests/**,manifest/transfer/**,README.md}`;
re-running `match.py` updates `manifest/*.tsv` (commit them if they change, say why). Never touch the
extractors, dumps, databases, ddon-hook, client/, packets/.
Libraries: stdlib, pytest, ruff.
Done: tests per rule with near-misses (a bitfield class, an access 2 bytes into a 4-byte member, a folded
name, a T002-wrong name corrected, an existing comment kept); `uv run pytest`, ruff, `bash tools/check.sh
--since <base>`; counts per file in the receipt; signed commits with `git commit -m <msg> -- <paths>`.
Stop: budget 180 min of work time; stop and ask if fewer than 20 types pass the access check.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
