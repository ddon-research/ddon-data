006 T001b (pattern): decode the whole 9.1.1 / 9.0.2 save blob in the patterns

Objective (build 03040008): implement `research/T001b-save-blob.md` (read it whole: the bit writer
§, the 170-write field table, the walk script in its appendix, the 9.0.2 §, the pattern sketch) in
`research/03040008/packets/C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ-pattern.cpp` and the 9.0.2
`S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES` pattern, with the shared blob in an include
(`include/CharacterData.hexpat`). The whole blob is in scope: every one of the 170 writes decodes
to a named (or `unk_*`, with the report's V/I marks in comments) field; no "undecoded" bytes left
except bytes 522..1023, which the serializer never writes (exported as `unused_tail`, with the
report's note that they are leftover memory).

How: the first 304 bytes decode byte-aligned as today; from bit 2432 an LSB-first bit reader
(ImHex `bitfield` with `#pragma bitfield_order` / `std::mem` bit reads, whichever produces correct
values in plbatch), each u32/u64 assembled from big-endian bytes as the report says; bools 1 bit; no
alignment. Validate in plbatch, not only by reading: the decoded values of all 47 captures must
equal the report's walk script output (run the script from the report appendix on the same files,
compare field by field in a scratch check; every field, every file). 9.0.2 has no captures: check it
on a synthetic file built from a 9.1.1 blob.

Then re-export 9.1.1 with `packets/imhex-export.sh @ C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ`
(plbatch); counts; receipt section "For Sam's inspection" (the new JSON fields, one example file
with a few decoded values such as the "pawn" chat channel name the report mentions).
Owns: those two patterns, the new include, `research/03040008/packets/README.md` (the blob rows of
its table and the removed open item), `packets/decrypted_json/**` for 9.1.1. Never touch other
patterns, raws, client/. Commit with `git commit -m <msg> -- <paths>`.
Libraries: ImHex std, plbatch; the report's stdlib script for the cross-check.
Done: signed commits; 47/47 files equal the script field by field; check.sh; receipt from
`receipt.py --print`. Stop: budget 90 min of work time; finish the scope.
Base: b603e7af1b.
