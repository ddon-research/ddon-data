007 W2 T013c: partial packet layouts from member links; local names by operation; apply support

Objective (PC 03040008 <- PS4 02020005): wave 2's transfer rows (spec 007 § 3, Sam: types and local names) from
the v6 dumps and manifest (T013b). Read `research/W2-T012-evidence.md`, `research/T010-locals.md` § 2-5, the
README (wave-1 rules, lea rule, apply), `tasks.md` § Close.

1. **Member links** (`transfer/`): for every aligned codec call site pair (`callsites.tsv` with `ps4_site`) whose
   destination arguments are `obj+X` (PC) and `obj+Y` (PS4) off the owners' object arguments (or `element`
   bases in array readers, element-reader call anchors as T012), link PC offset X of the PC class to the PS4
   DWARF member at Y (recursing into embedded structs), with the codec width. Class identity: the class of the
   owner's object argument from the pair's prototype (DWARF), the same on both sides.
2. **Partial layouts**: a PC class gets a type when it has at least one link and zero conflicts (one offset ->
   two members, one member -> two offsets, width differs from the member's leaf width, links overlapping):
   members exactly at the linked offsets with the PS4 member names and leaf types; everything else gap bytes;
   size = the proved size (constant allocation size / constructor) if any, else the end of the last linked
   member, marked `size: lower bound` in the comment. Then the access check of wave 1 against all v5 width
   accesses of paired functions on that class: a width access that overlaps a linked member other than exactly
   at its start with its width contradicts (refuse the class); accesses in gaps are allowed (unmodelled
   fields) and counted. Never derive members from a shift, from PS4 offsets alone, or from lea alone. The wave-1
   types (90 `MtTypedArray<X>`) are unchanged. Comment per type: "Partial: N members linked by codec position
   (PS4 02020005 names); gaps are unknown Season 3 fields."
3. **Locals** (`locals.tsv`): rules, each with the gates of T010 § 5 (not an argument, no user name, width =
   DWARF 32-bit size or the partial type's size when retyped, 0 conflicts / duplicates per function):
   R1 paired callee (T010), R2 codec anchor with `ps4_site` (T010 § 4), R3 handler packet object: the PC
   handler's stack local whose address is passed to the paired reader (rule-1 pair) <-> the PS4 handler's DWARF
   local that is the `obj` base of that reader's codec destinations (inlined) or the object argument passed to
   the out-of-line reader. R3 also retypes the local to the partial packet type when one is accepted. Record the
   PC lvar by stack/register location and `defea` (`lvar_locator_t`), never by index or name.
4. **Apply** (`apply_transfer.py`): partial types like other types (forward-declared rows become defined:
   a forward declaration written by wave 1 is filled in, not refused); a `locals` step after prototypes:
   decompile, find the lvar by locator, `before` = name/type, rename via `ida_hexrays.rename_lvar` or
   `modify_user_lvar_info` (`MLI_NAME`, `MLI_TYPE` for R3), read back by re-decompiling; dry run / verify /
   undo as for the other kinds. Prototypes and comments that referenced a now-defined type need no change.
5. Precision: the holdout of T005e applied to member links and locals (rows depending on a withheld seed),
   and a control: shuffle the PS4 side of the reader pairs; member links and R3 locals must then show
   conflicts or vanish; report counts.
Tests per rule incl. near-misses: a linked offset with a width mismatch, two members to one offset, an access
straddling a linked member, a shift-only class (no links: no type), R3 with two stack objects passed, an lvar
with a user name, a forward declaration filled in.

Owns: `research/03040008/ida-transfer/{transfer/**,transfer.py,apply_transfer.py,tests/**,manifest/transfer/**,README.md}`.
Never touch the extractor, matcher, dumps, databases, ddon-hook, client/, packets/.
Libraries: stdlib, IDAPython `ida_hexrays`/`ida_typeinf` (apply), pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; counts per rule and the precision tables in
the receipt; signed commits with `git commit -m <msg> -- <paths>`. Then, in the same package, a **smoke test on a
scratch copy** (T011 retro): `cp` the work copy's `.i64` to `PC_DDON_03040008/ddon-data-007smoke/` and run the apply
there by headless batch on 5 types and 10 locals (a filter option), check the read-back, delete the scratch copy.
Stop: budget 240 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
