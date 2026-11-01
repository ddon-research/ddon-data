006 T001b: decode the 9.1.1 character save blob bit by bit (evidence)

Objective (build 03040008, seed PS4 02020005): `C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ`
(9.1.1, 47 captures) carries a fixed u8[1024] bit stream written by `cCharacterData::serialize`; the
pattern decodes only its two version fields. Produce everything a pattern author needs to decode the
whole stream, and prove it on captures. This is the whole scope: finish it (no "if time allows").

Read first: spec 005 `research/P4-context-binary-character.md` § 3 and § 3.1 (writer VAs, field
list: PC `sub_467790` called from `0x87edd0`; PS4 `cCharacterData::serialize` `0x49740`), and
`research/03040008/packets/C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ-pattern.cpp` and its S2C
twin (9.0.2).

1. `BitWriter` on PC and PS4: every write method the serializer calls (`writeU32(val, nBits)`,
   `writeU64`, bool, arrays, strings if any): bit order inside a byte (MSB- or LSB-first), byte
   order of multi-byte values, how a value wider than the remaining bits in a byte is split, bool
   width, any alignment or flush, where the stream starts in the 1024 bytes and how the end is
   padded. Cite each from code (VA, the instructions or pseudocode lines that show it).
2. The PC serializer: every call in order with its bit width and the field it writes (DWARF names
   from the PS4 `cCharacterData` and its nested classes; the PC additions P4 found: one bit after
   `mIsAppraiseTalked`, 4 bits + one u8 in the options block, two u32[16] arrays at the end).
   Loops and conditionals (counts, presence bits) with their bounds. IDA can misread stack
   arguments: read the bit widths from the disassembly pushes, not only the pseudocode.
3. Walk 3 of the 47 captures (different streams) bit by bit with a stdlib Python script (scratch),
   implementing exactly 1-2: every field decodes to a plausible value (versions match the pattern's,
   ids in range, padding zero) and the stream ends where 2 predicts. Report any field that does not.
4. Note what the 9.0.2 response's blob is (same serializer read side? `cCharacterData::deserialize`
   on PC): read its reader enough to confirm it mirrors 1-2.
5. The PS4 recompilation has only stubs for `cCharacterData::serialize` and `BitWriter`
   (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/cNetSerializer.cpp`, `cCharacterData.cpp`); its
   `cNetSerializer.h` / `cCharacterData.h` declarations may still help with member order.

Owns: only `specs/006-packet-pattern-coverage/research/T001b-save-blob.md` (and your scratch script,
whose final version you paste into the report's appendix). Never touch patterns, packets/, client/.
Source boundary: PC/PS4 IDA 9.5 via ida-mcp on private copies (`bash research/ida/private-copy.sh
<pc|ps4> t001b`); captures via `xxd` (select by the `.9_1_1` suffix). Close each database with
`close_database` when done if your tools allow it; otherwise say so.
Libraries: ida-mcp `execute_python`; stdlib Python for the walk.
Done: § bit writer (with citations), § field table in stream order (bit offset, width, name, PC VA,
PS4 match, V/I), § walks (3 captures, per-field values, end offset), § 9.0.2, § what a pattern needs
(ImHex bitfield order setting, struct layout sketch). Final message: report path + at most 15 lines.
Stop: budget 120 min of work time; stop and report only if ida-mcp will not open the copies.
Base: 2a3408b879.
