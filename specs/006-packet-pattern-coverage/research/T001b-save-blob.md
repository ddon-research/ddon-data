# T001b: the 9.1.1 character save blob, bit by bit

Brief: `specs/006-packet-pattern-coverage/briefs/T001b-save-blob.md` (committed at b50ab5d49e,
base 2a3408b879). Owner: this file only.

- **Builds and databases.** PC 03040008 (Season 3 truth): private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t001b/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (`bash research/ida/private-copy.sh pc t001b`); `idc.get_idb_path()` returned that path,
  `inf_is_64bit()` = False, image base `0x400000`. PS4 02020005 (seed, symbols): private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t001b/DDOORBIS.elf.i64`
  (`... ps4 t001b`); 64-bit, image base `0x0`. Both read through ida-mcp `execute_python`
  (Hex-Rays pseudocode, `idautils.Heads` disassembly, `ida_typeinf` for the DWARF-derived PS4
  types). No renames, comments, retypes, patches or saves. `close_database` is not available to
  this role: both workers were left open (instances `ac1629fb71ee` PC, `8265db981fb7` PS4).
- **Address basis:** IDA VA in each database. PC `sub_*` names are IDA auto names. PS4 names are
  ELF symbols / DWARF.
- **Marks:** **V** = read in code (PC unless "PS4"); **I** = inferred (reason given);
  **PC-cap** = observed in 03040008 captures only; **C** = contradicts a named source.
- Captures: `packets/decrypted_raw/**/*.9_1_1` (47 files), body from file offset 0x09 (P4 § 1).

## 0. Summary

1. The blob is an **LSB-first bit stream**: stream bit *k* is bit `k & 7` (mask `1 << (k & 7)`)
   of byte `k >> 3`. Multi-byte integers are converted to **big-endian bytes** and those bytes are
   pushed through the same bit writer, each byte LSB-first. A 1-bit bool is bit 0 of the value. No
   alignment between fields; the stream is unaligned from bit 2433 on (V, PC and PS4).
2. PC 03040008 writes **4170 bits = 522 bytes** (521 full bytes + 2 bits); the last byte's 6
   high bits are 0. Bytes **522..1023 of the 1024-byte packet field are not written by the
   serializer** and hold stale allocator memory (V: no memset of the 2048-byte buffer; PC-cap:
   201..502 non-zero bytes there in every capture).
3. Elias-delta mode exists in the writer but is **off** for this packet (V: the sender zeroes the
   flag byte).
4. Field list: 170 field writes (98 in the serializer, 72 in the option block) in fixed order; no loops with data-dependent counts, no presence bits,
   no strings with length prefixes (17-byte fixed `MT_CHAR[17]` names only). PC additions over PS4
   (version 19 -> 25), each identified by the PC reader's version gate: 1 bit after
   `mIsAppraiseTalked` (v >= 0x19), 4 option bits (option +9 v >= 0x15, +96 v >= 0x17, +97/+98
   v >= 0x18), 1 option u8 (+37 v >= 0x14), two u32[16] arrays at the end (v >= 0x16) (V).
5. Walk: all **47/47** captures decode to `mVersion 0x19`, `mReleaseVersion 0x3040`, end at bit
   4170 (byte 522, file offset 531) with zero pad bits; option values are plausible (alphas 100/100/50,
   chat filter colours 0, 9, 1..8, 0, 1; a custom chat channel named `pawn` read from bit 2810,
   i.e. at a non-byte-aligned offset, which only decodes as ASCII under the LSB-first rule). Only 6
   distinct blobs exist among the 47 (PC-cap).
6. The 9.0.2 response carries the same format: the handler reads it with the mirrored
   `BitReader` (LSB-first, BE bytes) in `sub_466560`, which is **version-gated**; at version 0x19
   it reads exactly the writer's sequence (V).

## 1. The bit writer

PC `BitWriter` object (stack object in the sender `sub_87EDD0`, `int v8[18]` + `char v9`): +0
`MtStream *`, +4 `u32 mBitPos`, +8 `u8 mBits[64]`, +0x48 `bool mIsEliasDelta`. PS4 (recompilation
`cNetSerializer.h` 151-153 and the 64-bit code): +0 stream, +8 `mBitPos`, +0xC `mBits[64]`, +0x4C
`mIsEliasDelta`. Same object, 32/64-bit layout.

| Method (PC VA / PS4 symbol VA) | Behaviour | Evidence | Mark |
| --- | --- | --- | --- |
| `sub_8970D0(this, val, nBits)` / `BitWriter::writeU32(val, nBits)` `0x38bf40` | Writes `nBits` bits of `val`, **least significant first** (`v10 = 1; ... v10 *= 2`), each into `mBits[pos >> 3] |= 1 << (pos & 7)`, `++pos`. If `pos + nBits` reaches 512 it fills the buffer to bit 512, writes the 64 bytes to the stream (vtable +64 on PC, +17*8 on PS4), clears the buffer, `pos = 0`, and writes the remaining bits (split across the flush, still LSB-first). Bool = `nBits` 1, value `(byte != 0)`. | PC pseudocode of `sub_8970D0`; PS4 pseudocode of `writeU32` (`if ((v11 & val) != 0) this->mBits[mBitPos >> 3] |= 1 << (mBitPos & 7)`; threshold `mBitPos + nBits <= 0x1FF`, PC `< 0x200`) | V both |
| `sub_896E00(this, src, nBytes)` / `BitWriter::writeBytes` `0x38c1e0` | Byte array: source bit *j* (byte `j >> 3`, bit `j & 7`) goes to the next stream bit. Unaligned head: bit loop until `pos & 7 == 0` (mask `__ROL4__(v5,1)`); aligned middle: one byte per step `(src[j>>3] >> (j&7)) | (src[(j>>3)+1] << (8-(j&7)))`; tail: bit loop. Flushes 64 bytes whenever `pos == 512`. Net effect: bytes are kept in order; each byte's bits enter LSB-first. | PC pseudocode of `sub_896E00`; PS4 `writeBytes` shows the same three expressions | V both |
| `sub_897080(this, u32)` / `BitWriter::writeU32_0(u32)` `0x38c480` | If `mIsEliasDelta`: Elias-delta (`sub_8962A0` / `deltaEncode_unsigned_long_`). Else byte-swap to **big-endian** (`shr 18h`, `shr 10h`, `shr 8`, `cl` into 4 stack bytes) and `writeBytes(.., 4)` (`push 4` at `0x8970b5`). | PC disassembly `0x897082..0x8970c2`; PS4 `packed[0] = HIBYTE(n) ... packed[3] = n` | V both |
| `sub_8971D0(this, u64)` / `BitWriter::writeU64` `0x38c130` | Same, 8 bytes big-endian (`push 8` at `0x897240`); the u64 is passed as two dwords (`push [edi+0Ch]`, `push [edi+8]` at `0x4677c9`/`0x4677ce`). | PC disassembly; PS4 `packed[0] = HIBYTE(n) ... packed[7] = n` | V both |
| `sub_897270(this, u8)` / `BitWriter::writeU8` `0x38c580` | Elias branch `sub_896230`, else `writeBytes(&v, 1)` (`push 1` at `0x897284`). | PC disassembly | V both |
| `sub_896A40(this)` / `BitWriter::flushBits` `0x38c0c0` | Writes `(pos + 7) >> 3` bytes of the buffer to the stream, zeroes the 64-byte buffer and `pos`. The partial last byte goes out with its unwritten high bits **zero** (buffer was zeroed at construction and after every flush). | PC and PS4 pseudocode | V both |
| `sub_8962A0` (Elias-delta, PC) | Encodes `v + 1`: `floor(log2(L))` zero bits, a 1 bit, then the length and value bits (`sub_8967A0`, `sub_8968A0`). Not used here. | PC pseudocode | V (not exercised) |

Stream start and end:

- Sender PC `sub_87EDD0` (`0x87edd0`): allocates 2048 bytes (allocator vtable +36, alignment 16),
  `MtMemoryStream(&self, buf, 0x800, 2)`, `v8[0] = &self; memset(&v8[1], 0, 68); v9 = 0;`, i.e.
  `mBitPos = 0`, buffer zero, **`mIsEliasDelta = 0`**; calls `sub_467790(*(this + 3948), v8)`,
  `sub_896A40(v8)` (a second flush, writes 0 bytes because `sub_467790` already flushed), then
  `sub_820360(conn, buf)` which sends the first 1024 bytes (P4 § 3: `0x77d020`, 1024 x u8) (V).
  PS4 `cNetGameServer::sendSetCharacterInfo` `0x342950`: `MtMemoryStream_0(&v9, v5, 0x800, 2)`,
  `memset(&w.mBitPos, 0, 69)` (covers `mBitPos`, `mBits[64]`, `mIsEliasDelta`), `serialize`,
  `flushBits`, `Send_C2S_SET_CHARACTER_BIN_SAVEDATA_REQ(conn, (const u8 (*)[1024])v6)` (V PS4).
- The stream starts at byte 0 of the blob (memory stream opened at the buffer start) (V).
- Neither sender clears the 2048-byte buffer, so bytes after the flushed length are whatever the
  allocator returned (I from the absence of a memset; PC-cap: non-zero in 47/47).

## 2. Field table in stream order (PC 03040008)

PC `this` = the character data object (`*(sender + 3948)`); PS4 offsets are DWARF offsets in
`cCharacterData` (= 8 + offset in `stCharacterData`). Bit offsets are stream bit offsets from the
blob start (V by summing the widths; PC-cap by the walk). Widths come from the disassembly pushes
(`push 1` before every `sub_8970D0`, `push 11h` before `sub_896E00`, single `push dword` for u32,
two `push dword` for u64), not only the pseudocode.

### 2.1 cCharacterData::serialize (PC `sub_467790` `0x467790`, PS4 `0x49740`)

| Bit | Width | Field (PS4 DWARF name) | PC VA (call) | PC offset | PS4 offset | PS4 match | Mark |
| ---: | ---: | --- | --- | --- | --- | --- | --- |
| 0 | 32 | mVersion (PC writes 0x19 = 25; PS4 19) | `0x46779f` | +8 | +8 | same | V |
| 32 | 32 | mReleaseVersion | `0x4677a9` | +12 | +12 | same | V |
| 64 + 96i | 32 | mCheckPawnHistory[i].mPawnId, i = 0..15 (loop `ebx = 10h`) | `0x4677c4` | +13152 + 16i | +12728 + 16i | same | V |
| 96 + 96i | 64 | mCheckPawnHistory[i].mCheckDate | `0x4677d1` | +13160 + 16i | +12736 + 16i | same | V |
| 1600 | 32 | mQuestEtcF | `0x4677e4` | +12348 | +11960 | same | V |
| 1632 + 32i | 32 | mTutorialGuide.mFinishTutorial[i], i = 0..15 (loop `cmp edi, 10h`) | `0x4677f9` | +13408 + 4i | +12984 + 4i | same (PS4 `stTutorialGuide::writeData` `0x1960080`, no version test inside although it takes SaveVersion) | V |
| 2144 + 32i | 32 | mTutorialGuide.mLatestTutorial[i], i = 0..4 (loop `ebx = 5`) | `0x467814` | +13472 + 4i | +13048 + 4i | same | V |
| 2304 | 32 | mJobMasterInfo.mJobMasterTalked[0] | `0x467827` | +13492 | +13068 | same | V |
| 2336 | 32 | mJobMasterInfo.mJobMasterSkillTalked[0] | `0x467834` | +13496 | +13072 | same | V |
| 2368 | 32 | mAreaMasterInfo.mAreaMasterTalked[0] | `0x467841` | +13500 | +13076 | same | V |
| 2400 | 32 | mEnteredLandInfo.mEnteredLand[0] | `0x46784e` | +13504 | +13080 | same | V |
| 2432 | 1 | mIsAppraiseTalked | `0x467863` (`push 1`) | +13636 | +13084 | same | V |
| 2433 | 1 | **PC new bool** (reader gate v >= 0x19) | `0x467878` (`push 1`) | +13637 | — | PC only | V |
| 2434 | 376 | mOption (§ 2.2) | `0x467884` (`sub_4678F0(this + 8968, w)`) | +8968 | +8832 | PS4 = 364 bits | V |
| 2810 + 168i | 136 | mChatCstmCh[i].mName `MT_CHAR[17]`, i = 0..1 (loop `ebx = 2`) | `0x467899` (`push 11h`) | +12352 + 24i | +11964 + 24i | same | V |
| 2946 + 168i | 32 | mChatCstmCh[i].mBit | `0x4678a3` | +12372 + 24i | +11984 + 24i | same | V |
| 3146 + 32i | 32 | **PC new u32[16]** A[i] (reader gate v >= 0x16) | `0x4678b9` | +13508 + 4i | — | PC only | V |
| 3658 + 32i | 32 | **PC new u32[16]** B[i] (reader gate v >= 0x16) | `0x4678d4` | +13572 + 4i | — | PC only | V |
| 4170 | — | end; `flushBits` | `0x4678e1` (`sub_896A40`) | | | same | V |

PC layout note (I, from the offsets): the two new arrays sit between `mEnteredLandInfo`
(+13504) and `mIsAppraiseTalked` (+13636 = 13508 + 128), and the new bool follows it at +13637.
Meaning of the new fields (I, weak, PC-cap): in `stream60` A[1..3] = `0xda5d4e`, `0xda668d`,
`0xdab2f3`, the same pawn ids as `mCheckPawnHistory`, and B[1..3] = 0x11, 0x21, 0x0f; so A looks
like a pawn id list and B a per-pawn small value. Names unknown.

### 2.2 stOptionData::serialize (PC `sub_4678F0` `0x4678F0`, PS4 `0x1960180`)

PC offsets are relative to the option object (`this + 8968`). The PS4 member for each PC offset
was matched by (a) identical write order and kind, (b) a constant +1 layout shift where PC
inserted a byte (+9 and +37), and (c) **identical version gates** in both readers: PC `sub_466740`
vs PS4 `stOptionData::deserialize` `0x19605b0` gate CamDrama (>= 0xB), CamRangeMagic/Bow (>= 0x11),
DefaultRimWarpTabPos (>= 0x13), Tutorial/MatchingAnnounce (>= 0xC), QuestActiveAuto (>= 8),
HeaderDispType (release < 2 and value 1 -> 4) and MiniMapAutoScale (>= 0x12) at the same PC
offsets. The PC-only fields are those gated above PS4's version 19 (0x13). So the mapping is V
for the gated anchors and I (order + offsets) for the rest.

| Bit | Width | PS4 field | PC VA | PC off | PS4 off | Mark |
| ---: | ---: | --- | --- | ---: | ---: | --- |
| 2434 | 1 | mIsCamRevise | `0x467907` | 4 | 4 | V |
| 2435 | 1 | mIsCamDrama | `0x467919` | 5 | 5 | V |
| 2436 | 8 | mCamRangeMagic | `0x467925` | 6 | 6 | V |
| 2444 | 8 | mCamRangeBow | `0x467931` | 7 | 7 | V |
| 2452 | 8 | mCamPosType | `0x46793d` | 8 | 8 | V |
| 2460 | 1 | **PC new bool** (gate >= 0x15) | `0x46794f` | 9 | — | V |
| 2461 | 1 | mIsMenuWindowOffAuto | `0x467961` | 12 | 11 | V/I |
| 2462 | 8 | mDefaultRimWarpTabPos | `0x46796d` | 13 | 12 | V (gate 0x13) |
| 2470 | 1 | mIsPartyBattleBGM | `0x46797f` | 18 | 17 | V/I |
| 2471 | 32 | mPlayerIdlingEmotion | `0x467989` | 24 | 24 | V |
| 2503 | 8 | mPlayerIdlingEmotionTime | `0x467995` | 28 | 28 | V |
| 2511 | 1 | mIsRotMiniMap | `0x4679a7` | 31 | 31 | V |
| 2512 | 8 | mAlphaMiniMap | `0x4679b3` | 32 | 32 | V |
| 2520 | 1 | mIsMapDispName | `0x4679c5` | 35 | 35 | V |
| 2521 | 1 | mIsDispCharges | `0x4679d7` | 38 | 37 | V/I |
| 2522 | 1 | mIsTutorialAnnounce | `0x4679e9` | 39 | 38 | V (gate 0xC) |
| 2523 | 1 | mIsMatchingAnnounce | `0x4679fb` | 40 | 39 | V (gate 0xC) |
| 2524 | 8 | mAlphaHUDCmn | `0x467a07` | 41 | 40 | V/I |
| 2532 | 1 | mIsQuestActiveAuto | `0x467a19` | 42 | 41 | V (gate 8) |
| 2533 | 1 | mIsDispQuestGuide | `0x467a2b` | 43 | 42 | V/I |
| 2534 | 1 | mIsQuestGuideAuto | `0x467a3d` | 44 | 43 | V/I |
| 2535 | 8 | mQuestGuidePrio | `0x467a49` | 45 | 44 | V/I |
| 2543 | 1 | mIsDyingFilterDisp | `0x467a5b` | 46 | 45 | V/I |
| 2544 | 1 | mIsMailBoxDispWarning | `0x467a6d` | 47 | 46 | V/I |
| 2545 | 8 | mHeaderDispType | `0x467a79` | 48 | 47 | V (release rule) |
| 2553 | 8 | mHeaderNameDispParty.mType | `0x467a85` | 51 | 50 | V/I |
| 2561 | 1 | mHeaderNameDispParty.mClanName | `0x467a97` | 52 | 51 | V/I |
| 2562 | 8 | mHeaderNameDispOther.mType | `0x467aa3` | 53 | 52 | V/I |
| 2570 | 1 | mHeaderNameDispOther.mClanName | `0x467ab5` | 54 | 53 | V/I |
| 2571 | 1 | mIsHeaderNameNpcName | `0x467ac7` | 55 | 54 | V/I |
| 2572 | 1 | mIsHeaderNameNpcClass | `0x467ad9` | 56 | 55 | V/I |
| 2573 | 1 | mIsHeaderNameOmName | `0x467aeb` | 57 | 56 | V/I |
| 2574 | 8 | mChatLogNameDisp.mType | `0x467af7` | 58 | 57 | V/I |
| 2582 | 1 | mChatLogNameDisp.mClanName | `0x467b09` | 59 | 58 | V/I |
| 2583 | 1 | mIsChatLogTimeStamp | `0x467b1b` | 60 | 59 | V/I |
| 2584 | 8 | mAlphaChat | `0x467b27` | 61 | 60 | V/I |
| 2592 + 16i | 8 | mChatChFilterColor[i], i = 0..11 (loop `ebp = 0Ch`, `[edi-0Ch]`) | `0x467b3b` | 62 + i | 61 + i | V/I |
| 2600 + 16i | 8 | mChatChFilterSE[i] (same loop, `[edi]`) | `0x467b46` | 74 + i | 73 + i | V/I |
| 2784 | 1 | mIsClockDispPing | `0x467b5e` | 86 | 85 | V/I |
| 2785 | 1 | mIsClockDispTime | `0x467b70` | 87 | 86 | V/I |
| 2786 | 8 | mClockDispType | `0x467b7c` | 88 | 87 | V/I |
| 2794 | 1 | mIsClockDispCh | `0x467b8e` | 89 | 88 | V/I |
| 2795 | 1 | mIsEngageDisp | `0x467ba0` | 90 | 89 | V/I |
| 2796 | 1 | mIsAchievementDispAnnounce | `0x467bb2` | 91 | 90 | V/I |
| 2797 | 1 | mIsRewardBoxDispWarning | `0x467bc4` | 92 | 91 | V/I |
| 2798 | 1 | mIsMiniMapAutoScale | `0x467bd6` | 36 | 36 | V (gate 0x12) |
| 2799 | 8 | **PC new u8** (gate >= 0x14) | `0x467be2` | 37 | — | V |
| 2807 | 1 | **PC new bool** (gate >= 0x17) | `0x467bf4` | 96 | — | V |
| 2808 | 1 | **PC new bool** (gate >= 0x18) | `0x467c06` | 97 | — | V |
| 2809 | 1 | **PC new bool** (gate >= 0x18) | `0x467c18` | 98 | — | V |

Counts (V): PC 32 one-bit writes, 15 u8 + 24 u8 in the loop, 1 u32 = 32 + 312 + 32 = 376 bits;
PS4 28 one-bit writes, 14 u8 + 24 u8, 1 u32 = 28 + 304 + 32 = **364 bits** (P4 § 3.1 row 8
counted the loop body as 2 writes: 16 u8 writes PS4, 17 PC; consistent). PS4 stream total: 64 +
1536 + 32 + 672 + 128 + 1 + 364 + 336 = 3133 bits (I, arithmetic; PS4 captures not examined).

PS4 members that are in `stOptionData` but **not serialized** on either platform: mOnlineStatus,
mIsCamHRevPad, mIsCamVRevKeyboard, mIsCamHRevKeyboard, mCamSpdPad, mCamSpdKeyboard,
mDefaultMenuWindowSize, mIsEnableChgMenuWindowSize, mIsDirectChat, mIsDispTelop,
mIsDispHeadArmor{Pl,Pawn}, mIsDispLantern{Pl,Pawn}, mIsDialogSell{,CraftItem}, mIsMap{V,H}Rev,
mHeaderNameDispMine, mPlCardOnView, mPawnCardOnView, mIsClanNtc (V PS4 by absence from
`serialize`; PC equivalents absent by the same comparison, I).

## 3. Walks

Script: Appendix A (stdlib, implements exactly § 1 and § 2). Command, from
`packets/decrypted_raw`:
`fd -t f -e 9_1_1 . -0 | xargs -0 python -X utf8 -I <scratch>/walk_savebin.py`.

All 47 files (PC-cap): each holds the full 1024-byte blob (script assert; the three below are 1040 B); `mVersion` 0x19 and `mReleaseVersion` 0x3040 in 47/47;
end bit **4170** in 47/47 (byte 522, file offset 531, as § 2 predicts); pad bits 4170..4175 zero
in 47/47; bytes 522..1023 non-zero in 47/47 (201..502 non-zero bytes per file; § 1 explains why).
The only "issue" the script flags is that tail, which is expected. The SHA-256 of the 522
encoded bytes gives 6 distinct blobs (20 + 19 + 5 + 1 + 1 + 1 files).

Three captures from different streams and distinct blobs, walked field by field
(`--detail`):

| Label | File (under `packets/decrypted_raw/`) | SHA-256 (whole file) |
| --- | --- | --- |
| stream1-35 | `stream1-marked.pcapng_tcp-stream-35/26530_C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ_2019-07-06T11_09_43.1916220-07_00.9_1_1` | `053a8ebfc2648bdfe1cb1d5862a5224d245bedf7c82a650e442fa859c310e49b` |
| stream60-11 | `stream60-exchange-apprasial-cashshop-treasurelot-marked.pcapng_tcp-stream-11/11509_C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ_2019-10-04T12_45_22.7703781-07_00.9_1_1` | `0a253d38fa177e0f306e664d5667359ccfa72a57560b536bf1bdaa980069bcc0` |
| stream86-9 | `stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/4801_C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ_2019-12-03T13_13_28.9442780-08_00.9_1_1` | `d0065e0c5b2fb9b9d4a5e21e67f394be2186f3b2e1bdaf902c16b4016aeaf79d` |

Each ends at bit 4170 with tail bits 0; non-zero bytes after the end: 291, 498, 318.

Plausibility (PC-cap, I for meanings): versions as the pattern; pawn ids `0xda5d4e`..`0xdb3bcf`
(~14.3 M, the range of other pawn ids in these captures is not checked here); `mCheckDate`
`0x5d238daf` = 2019-07-08 and `0x5ce56d7b` = 2019-05-22 (Unix seconds, before the 2019-10-04
capture); `mLatestTutorial` behaves as a most-recent-first list (stream86 = `0x51` followed by
stream1's first four); alphas 0x64/0x64/0x32; filter colours 0, 9, 1..8, 0, 1; booleans 0/1 only
by construction; custom chat channel `pawn` + 13 NUL bytes at bit 2810 with `mBit 0x3ffffe`.
`mFinishTutorial[0..13]` and `mQuestEtcF` are bit sets (dense values). No field decodes to an
implausible value. No field contradicts § 2.

Per-field values:

| bit | w | field | stream1-35 | stream60-11 | stream86-9 |
| ---: | ---: | --- | --- | --- | --- |
| 0 | 32 | mVersion | 0x19 | 0x19 | 0x19 |
| 32 | 32 | mReleaseVersion | 0x3040 | 0x3040 | 0x3040 |
| 64 | 32 | mCheckPawnHistory[0].mPawnId | 0x0 | 0xda5d4e | 0xdb3bcf |
| 96 | 64 | mCheckPawnHistory[0].mCheckDate | 0x0 | 0x0 | 0x0 |
| 160 | 32 | mCheckPawnHistory[1].mPawnId | 0x0 | 0xdab2f3 | 0x0 |
| 192 | 64 | mCheckPawnHistory[1].mCheckDate | 0x0 | 0x5d238daf | 0x0 |
| 256 | 32 | mCheckPawnHistory[2].mPawnId | 0x0 | 0xda668d | 0x0 |
| 288 | 64 | mCheckPawnHistory[2].mCheckDate | 0x0 | 0x5ce56d7b | 0x0 |
| 352 | 32 | mCheckPawnHistory[3].mPawnId | 0x0 | 0x0 | 0x0 |
| 384 | 64 | mCheckPawnHistory[3].mCheckDate | 0x0 | 0x0 | 0x0 |
| 448 | 32 | mCheckPawnHistory[4].mPawnId | 0x0 | 0x0 | 0x0 |
| 480 | 64 | mCheckPawnHistory[4].mCheckDate | 0x0 | 0x0 | 0x0 |
| 544 | 32 | mCheckPawnHistory[5].mPawnId | 0x0 | 0x0 | 0x0 |
| 576 | 64 | mCheckPawnHistory[5].mCheckDate | 0x0 | 0x0 | 0x0 |
| 640 | 32 | mCheckPawnHistory[6].mPawnId | 0x0 | 0x0 | 0x0 |
| 672 | 64 | mCheckPawnHistory[6].mCheckDate | 0x0 | 0x0 | 0x0 |
| 736 | 32 | mCheckPawnHistory[7].mPawnId | 0x0 | 0x0 | 0x0 |
| 768 | 64 | mCheckPawnHistory[7].mCheckDate | 0x0 | 0x0 | 0x0 |
| 832 | 32 | mCheckPawnHistory[8].mPawnId | 0x0 | 0x0 | 0x0 |
| 864 | 64 | mCheckPawnHistory[8].mCheckDate | 0x0 | 0x0 | 0x0 |
| 928 | 32 | mCheckPawnHistory[9].mPawnId | 0x0 | 0x0 | 0x0 |
| 960 | 64 | mCheckPawnHistory[9].mCheckDate | 0x0 | 0x0 | 0x0 |
| 1024 | 32 | mCheckPawnHistory[10].mPawnId | 0x0 | 0x0 | 0x0 |
| 1056 | 64 | mCheckPawnHistory[10].mCheckDate | 0x0 | 0x0 | 0x0 |
| 1120 | 32 | mCheckPawnHistory[11].mPawnId | 0x0 | 0x0 | 0x0 |
| 1152 | 64 | mCheckPawnHistory[11].mCheckDate | 0x0 | 0x0 | 0x0 |
| 1216 | 32 | mCheckPawnHistory[12].mPawnId | 0x0 | 0x0 | 0x0 |
| 1248 | 64 | mCheckPawnHistory[12].mCheckDate | 0x0 | 0x0 | 0x0 |
| 1312 | 32 | mCheckPawnHistory[13].mPawnId | 0x0 | 0x0 | 0x0 |
| 1344 | 64 | mCheckPawnHistory[13].mCheckDate | 0x0 | 0x0 | 0x0 |
| 1408 | 32 | mCheckPawnHistory[14].mPawnId | 0x0 | 0x0 | 0x0 |
| 1440 | 64 | mCheckPawnHistory[14].mCheckDate | 0x0 | 0x0 | 0x0 |
| 1504 | 32 | mCheckPawnHistory[15].mPawnId | 0x0 | 0x0 | 0x0 |
| 1536 | 64 | mCheckPawnHistory[15].mCheckDate | 0x0 | 0x0 | 0x0 |
| 1600 | 32 | mQuestEtcF | 0x109d1d70 | 0x30002 | 0x109d1d70 |
| 1632 | 32 | mTutorialGuide.mFinishTutorial[0] | 0x9000100 | 0xa9000100 | 0x9000100 |
| 1664 | 32 | mTutorialGuide.mFinishTutorial[1] | 0x824d9b | 0x3a24ddb | 0x824d9b |
| 1696 | 32 | mTutorialGuide.mFinishTutorial[2] | 0x29002800 | 0x39c3f72c | 0x29022800 |
| 1728 | 32 | mTutorialGuide.mFinishTutorial[3] | 0x7a844042 | 0x7e8c6852 | 0x7a844042 |
| 1760 | 32 | mTutorialGuide.mFinishTutorial[4] | 0xc3008998 | 0xcb018999 | 0xc3008998 |
| 1792 | 32 | mTutorialGuide.mFinishTutorial[5] | 0x228118 | 0x7dd3fa | 0x228118 |
| 1824 | 32 | mTutorialGuide.mFinishTutorial[6] | 0x40030008 | 0x40530008 | 0x40030008 |
| 1856 | 32 | mTutorialGuide.mFinishTutorial[7] | 0x8002c181 | 0xb6abdfed | 0x8002c181 |
| 1888 | 32 | mTutorialGuide.mFinishTutorial[8] | 0xb024 | 0x40881d26 | 0xb024 |
| 1920 | 32 | mTutorialGuide.mFinishTutorial[9] | 0x20004800 | 0x300deae1 | 0x20004800 |
| 1952 | 32 | mTutorialGuide.mFinishTutorial[10] | 0x30403 | 0xb00337cf | 0x30403 |
| 1984 | 32 | mTutorialGuide.mFinishTutorial[11] | 0x10000 | 0xe01fbdff | 0x10000 |
| 2016 | 32 | mTutorialGuide.mFinishTutorial[12] | 0x2100604 | 0x2ffff97 | 0x2100604 |
| 2048 | 32 | mTutorialGuide.mFinishTutorial[13] | 0x10004000 | 0x7b6fde5e | 0x10004000 |
| 2080 | 32 | mTutorialGuide.mFinishTutorial[14] | 0x0 | 0x0 | 0x0 |
| 2112 | 32 | mTutorialGuide.mFinishTutorial[15] | 0x0 | 0x0 | 0x0 |
| 2144 | 32 | mTutorialGuide.mLatestTutorial[0] | 0x105 | 0x196 | 0x51 |
| 2176 | 32 | mTutorialGuide.mLatestTutorial[1] | 0x14a | 0x18b | 0x105 |
| 2208 | 32 | mTutorialGuide.mLatestTutorial[2] | 0x140 | 0x18c | 0x14a |
| 2240 | 32 | mTutorialGuide.mLatestTutorial[3] | 0xff | 0x117 | 0x140 |
| 2272 | 32 | mTutorialGuide.mLatestTutorial[4] | 0x12b | 0x1a9 | 0xff |
| 2304 | 32 | mJobMasterTalked[0] | 0x0 | 0x0 | 0x0 |
| 2336 | 32 | mJobMasterSkillTalked[0] | 0x0 | 0x160 | 0x0 |
| 2368 | 32 | mAreaMasterTalked[0] | 0x2 | 0x3ffffe | 0x2 |
| 2400 | 32 | mEnteredLand[0] | 0x3 | 0x7f | 0x3 |
| 2432 | 1 | mIsAppraiseTalked | 1 | 1 | 1 |
| 2433 | 1 | pc_new_bit_13637 (v>=0x19) | 0 | 1 | 0 |
| 2434 | 1 | mOption.mIsCamRevise | 1 | 1 | 1 |
| 2435 | 1 | mOption.mIsCamDrama | 1 | 0 | 1 |
| 2436 | 8 | mOption.mCamRangeMagic | 0x1 | 0x1 | 0x1 |
| 2444 | 8 | mOption.mCamRangeBow | 0x0 | 0x0 | 0x0 |
| 2452 | 8 | mOption.mCamPosType | 0x0 | 0x0 | 0x0 |
| 2460 | 1 | mOption.pc_new_opt_bit_09 (v>=0x15) | 1 | 1 | 1 |
| 2461 | 1 | mOption.mIsMenuWindowOffAuto | 1 | 1 | 1 |
| 2462 | 8 | mOption.mDefaultRimWarpTabPos | 0x0 | 0x0 | 0x0 |
| 2470 | 1 | mOption.mIsPartyBattleBGM | 1 | 1 | 1 |
| 2471 | 32 | mOption.mPlayerIdlingEmotion | 0x0 | 0x0 | 0x0 |
| 2503 | 8 | mOption.mPlayerIdlingEmotionTime | 0x0 | 0x0 | 0x0 |
| 2511 | 1 | mOption.mIsRotMiniMap | 0 | 0 | 0 |
| 2512 | 8 | mOption.mAlphaMiniMap | 0x64 | 0x64 | 0x64 |
| 2520 | 1 | mOption.mIsMapDispName | 1 | 1 | 1 |
| 2521 | 1 | mOption.mIsDispCharges | 1 | 1 | 1 |
| 2522 | 1 | mOption.mIsTutorialAnnounce | 1 | 1 | 1 |
| 2523 | 1 | mOption.mIsMatchingAnnounce | 1 | 1 | 1 |
| 2524 | 8 | mOption.mAlphaHUDCmn | 0x64 | 0x64 | 0x64 |
| 2532 | 1 | mOption.mIsQuestActiveAuto | 1 | 1 | 1 |
| 2533 | 1 | mOption.mIsDispQuestGuide | 1 | 1 | 1 |
| 2534 | 1 | mOption.mIsQuestGuideAuto | 1 | 1 | 1 |
| 2535 | 8 | mOption.mQuestGuidePrio | 0x0 | 0x0 | 0x0 |
| 2543 | 1 | mOption.mIsDyingFilterDisp | 1 | 1 | 1 |
| 2544 | 1 | mOption.mIsMailBoxDispWarning | 0 | 0 | 0 |
| 2545 | 8 | mOption.mHeaderDispType | 0x0 | 0x0 | 0x0 |
| 2553 | 8 | mOption.mHeaderNameDispParty.mType | 0x0 | 0x0 | 0x0 |
| 2561 | 1 | mOption.mHeaderNameDispParty.mClanName | 1 | 1 | 1 |
| 2562 | 8 | mOption.mHeaderNameDispOther.mType | 0x0 | 0x0 | 0x0 |
| 2570 | 1 | mOption.mHeaderNameDispOther.mClanName | 1 | 1 | 1 |
| 2571 | 1 | mOption.mIsHeaderNameNpcName | 1 | 1 | 1 |
| 2572 | 1 | mOption.mIsHeaderNameNpcClass | 1 | 1 | 1 |
| 2573 | 1 | mOption.mIsHeaderNameOmName | 1 | 1 | 1 |
| 2574 | 8 | mOption.mChatLogNameDisp.mType | 0x0 | 0x0 | 0x0 |
| 2582 | 1 | mOption.mChatLogNameDisp.mClanName | 0 | 1 | 0 |
| 2583 | 1 | mOption.mIsChatLogTimeStamp | 0 | 1 | 0 |
| 2584 | 8 | mOption.mAlphaChat | 0x32 | 0x32 | 0x32 |
| 2592 | 8 | mOption.mChatChFilterColor[0] | 0x0 | 0x0 | 0x0 |
| 2600 | 8 | mOption.mChatChFilterSE[0] | 0x0 | 0x0 | 0x0 |
| 2608 | 8 | mOption.mChatChFilterColor[1] | 0x9 | 0x9 | 0x9 |
| 2616 | 8 | mOption.mChatChFilterSE[1] | 0x0 | 0x0 | 0x0 |
| 2624 | 8 | mOption.mChatChFilterColor[2] | 0x1 | 0x1 | 0x1 |
| 2632 | 8 | mOption.mChatChFilterSE[2] | 0x0 | 0x0 | 0x0 |
| 2640 | 8 | mOption.mChatChFilterColor[3] | 0x2 | 0x2 | 0x2 |
| 2648 | 8 | mOption.mChatChFilterSE[3] | 0x1 | 0x1 | 0x1 |
| 2656 | 8 | mOption.mChatChFilterColor[4] | 0x3 | 0x3 | 0x3 |
| 2664 | 8 | mOption.mChatChFilterSE[4] | 0x0 | 0x0 | 0x0 |
| 2672 | 8 | mOption.mChatChFilterColor[5] | 0x4 | 0x4 | 0x4 |
| 2680 | 8 | mOption.mChatChFilterSE[5] | 0x0 | 0x0 | 0x0 |
| 2688 | 8 | mOption.mChatChFilterColor[6] | 0x5 | 0x5 | 0x5 |
| 2696 | 8 | mOption.mChatChFilterSE[6] | 0x0 | 0x0 | 0x0 |
| 2704 | 8 | mOption.mChatChFilterColor[7] | 0x6 | 0x6 | 0x6 |
| 2712 | 8 | mOption.mChatChFilterSE[7] | 0x0 | 0x0 | 0x0 |
| 2720 | 8 | mOption.mChatChFilterColor[8] | 0x7 | 0x7 | 0x7 |
| 2728 | 8 | mOption.mChatChFilterSE[8] | 0x0 | 0x0 | 0x0 |
| 2736 | 8 | mOption.mChatChFilterColor[9] | 0x8 | 0x8 | 0x8 |
| 2744 | 8 | mOption.mChatChFilterSE[9] | 0x0 | 0x0 | 0x0 |
| 2752 | 8 | mOption.mChatChFilterColor[10] | 0x0 | 0x0 | 0x0 |
| 2760 | 8 | mOption.mChatChFilterSE[10] | 0x0 | 0x0 | 0x0 |
| 2768 | 8 | mOption.mChatChFilterColor[11] | 0x1 | 0x1 | 0x1 |
| 2776 | 8 | mOption.mChatChFilterSE[11] | 0x0 | 0x0 | 0x0 |
| 2784 | 1 | mOption.mIsClockDispPing | 1 | 1 | 1 |
| 2785 | 1 | mOption.mIsClockDispTime | 1 | 1 | 1 |
| 2786 | 8 | mOption.mClockDispType | 0x0 | 0x0 | 0x0 |
| 2794 | 1 | mOption.mIsClockDispCh | 1 | 1 | 1 |
| 2795 | 1 | mOption.mIsEngageDisp | 1 | 1 | 1 |
| 2796 | 1 | mOption.mIsAchievementDispAnnounce | 1 | 1 | 1 |
| 2797 | 1 | mOption.mIsRewardBoxDispWarning | 1 | 1 | 1 |
| 2798 | 1 | mOption.mIsMiniMapAutoScale | 0 | 0 | 0 |
| 2799 | 8 | mOption.pc_new_opt_u8_37 (v>=0x14) | 0x0 | 0x0 | 0x0 |
| 2807 | 1 | mOption.pc_new_opt_bit_96 (v>=0x17) | 1 | 1 | 1 |
| 2808 | 1 | mOption.pc_new_opt_bit_97 (v>=0x18) | 1 | 1 | 1 |
| 2809 | 1 | mOption.pc_new_opt_bit_98 (v>=0x18) | 1 | 1 | 1 |
| 2810 | 136 | mChatCstmCh[0].mName | 0000000000000000000000000000000000 '' | 7061776e00000000000000000000000000 'pawn' | 0000000000000000000000000000000000 '' |
| 2946 | 32 | mChatCstmCh[0].mBit | 0x0 | 0x3ffffe | 0x0 |
| 2978 | 136 | mChatCstmCh[1].mName | 0000000000000000000000000000000000 '' | 0000000000000000000000000000000000 '' | 0000000000000000000000000000000000 '' |
| 3114 | 32 | mChatCstmCh[1].mBit | 0x0 | 0x0 | 0x0 |
| 3146 | 32 | pc_new_u32_13508[0] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3178 | 32 | pc_new_u32_13508[1] (v>=0x16) | 0x0 | 0xda5d4e | 0x0 |
| 3210 | 32 | pc_new_u32_13508[2] (v>=0x16) | 0x0 | 0xda668d | 0x0 |
| 3242 | 32 | pc_new_u32_13508[3] (v>=0x16) | 0x0 | 0xdab2f3 | 0x0 |
| 3274 | 32 | pc_new_u32_13508[4] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3306 | 32 | pc_new_u32_13508[5] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3338 | 32 | pc_new_u32_13508[6] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3370 | 32 | pc_new_u32_13508[7] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3402 | 32 | pc_new_u32_13508[8] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3434 | 32 | pc_new_u32_13508[9] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3466 | 32 | pc_new_u32_13508[10] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3498 | 32 | pc_new_u32_13508[11] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3530 | 32 | pc_new_u32_13508[12] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3562 | 32 | pc_new_u32_13508[13] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3594 | 32 | pc_new_u32_13508[14] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3626 | 32 | pc_new_u32_13508[15] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3658 | 32 | pc_new_u32_13572[0] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3690 | 32 | pc_new_u32_13572[1] (v>=0x16) | 0x0 | 0x11 | 0x0 |
| 3722 | 32 | pc_new_u32_13572[2] (v>=0x16) | 0x0 | 0x21 | 0x0 |
| 3754 | 32 | pc_new_u32_13572[3] (v>=0x16) | 0x0 | 0xf | 0x0 |
| 3786 | 32 | pc_new_u32_13572[4] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3818 | 32 | pc_new_u32_13572[5] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3850 | 32 | pc_new_u32_13572[6] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3882 | 32 | pc_new_u32_13572[7] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3914 | 32 | pc_new_u32_13572[8] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3946 | 32 | pc_new_u32_13572[9] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 3978 | 32 | pc_new_u32_13572[10] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 4010 | 32 | pc_new_u32_13572[11] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 4042 | 32 | pc_new_u32_13572[12] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 4074 | 32 | pc_new_u32_13572[13] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 4106 | 32 | pc_new_u32_13572[14] (v>=0x16) | 0x0 | 0x0 | 0x0 |
| 4138 | 32 | pc_new_u32_13572[15] (v>=0x16) | 0x0 | 0x0 | 0x0 |

## 4. The 9.0.2 response blob

`S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES` carries the same bit stream (V):

- Handler PC `sub_7C68DE` (`0x7c68de`, name string
  "cSeedGameSvConnection::OnPacket_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES"): `memset(v18, 0,
  1025)`, `sub_801530` reads the packet into it, then (when the second header field `v17` is 0)
  `MtMemoryStream(v10, v18, 1024, 1)`, a `BitReader` `{stream, mBitPos = 64, ..., +16 Elias = 0}`,
  `sub_8969C0` (fill), **`sub_466560`** on the same character data object (`*(conn + 15792)`), then
  seeks the stream back by the unread whole bytes. `sub_466560` is also called from `sub_465700`
  (`0x4657a5`) and `sub_7C7F20` (`0x7c80b8`) (V; those callers not read).
- PC `BitReader` (8-byte buffer, 64 bits): `sub_896BE0(r, nBits)` reads bit `1 << (pos & 7)` of
  byte `pos >> 3`, value bits LSB first (`v4 |= v5; v5 *= 2`), refilling via `sub_8969C0` at 64;
  `sub_896CE0` u32 = 4 bytes via `sub_896A70` reassembled big-endian; `sub_896D20` u64 = 8 bytes
  big-endian; `sub_896DD0` u8; `sub_896A70(r, dst, 17)` the names. Mirror of § 1 (V). PS4 has the
  matching `BitReader::readU32/readU8/readU64/readBytes` (`0x38c880`..`0x38cf70`) (V PS4, names).
- `sub_466560` is **version-gated** on `mVersion` (first u32); at `mVersion = 0x19` every gate is
  open and the sequence equals § 2 exactly, then it sets `mVersion = 25` (V). PS4
  `cCharacterData::deserialize` `0x49880` has the same gates up to 0x13 and sets 19 (V PS4).

Reader gates (PC, V). A pattern for 9.0.2 must apply them if it wants to decode older blobs:

| Field(s) | Read when mVersion | Notes |
| --- | --- | --- |
| mVersion | always | |
| mReleaseVersion | >= 9 | |
| mCheckPawnHistory[16] | >= 2 | |
| mQuestEtcF, mFinishTutorial[16], mLatestTutorial[5] | >= 5 | |
| mJobMasterTalked | >= 6 | |
| mJobMasterSkillTalked | >= 0xD | |
| mAreaMasterTalked | >= 0xE | below 0xE it is filled from a global table, not read |
| mEnteredLand | >= 0x10 | |
| mIsAppraiseTalked | >= 0xF | |
| PC new bool (+13637) | >= 0x19 | |
| mOption | >= 7 | inside: CamDrama >= 0xB; CamRangeMagic, CamRangeBow >= 0x11; new bit +9 >= 0x15; DefaultRimWarpTabPos >= 0x13; Tutorial/MatchingAnnounce >= 0xC; QuestActiveAuto >= 8; MiniMapAutoScale >= 0x12; new u8 +37 >= 0x14; new bit +96 >= 0x17; new bits +97, +98 >= 0x18; the rest always |
| mChatCstmCh[2] | >= 0xA | |
| new u32[16] x 2 | >= 0x16 | |

No 9.0.2 capture exists (P4 § 3), so the response side is code-only.

## 5. What a pattern needs

1. **Bit order:** least-significant-bit first within each byte, bytes in increasing address
   order: stream bit *k* = `(blob[k >> 3] >> (k & 7)) & 1`. In ImHex that is a little-endian
   bitfield with `BitfieldOrder::LeastToMostSignificant` (I; ImHex CLI is not on `PATH`, nothing
   below was validated).
2. **Multi-byte values are not little-endian bit fields.** A u32 is four 8-bit fields in stream
   order whose values form the integer big-endian: `value = b0 << 24 | b1 << 16 | b2 << 8 | b3`,
   each `bN` being 8 stream bits read LSB-first. Same for the u64 (8 bytes). Reading a u32 as one
   32-bit little-endian bitfield gives the byte-swapped value; reading it big-endian with a
   most-to-least order gives the wrong bits once the stream is unaligned (from bit 2433).
3. **Byte-aligned prefix:** bits 0..2431 (bytes 0..303) are byte aligned, so the existing
   `#pragma endian big` u32/u64 declarations decode them directly: `u32 mVersion; u32
   mReleaseVersion; {u32 mPawnId; u64 mCheckDate;}[16]; u32 mQuestEtcF; u32 mFinishTutorial[16];
   u32 mLatestTutorial[5]; u32 talked[4];` = 304 bytes (V by § 2; PC-cap by the walk).
4. **Unaligned tail:** bits 2432..4169 (from byte 304) need the bit reader: 2 bools, the 376-bit
   option block, 2 x (17-byte name + u32), 32 x u32. Then 6 zero pad bits; the blob ends at
   byte 522; **bytes 522..1023 are stale memory** and should be declared as an opaque
   `u8 unwritten[502]` (not "padding must be zero").
5. Sketch (I, unvalidated):

```cpp
// After the 304 aligned bytes, at blob offset 304 (bit 2432):
bitfield BeU32 { b0 : 8; b1 : 8; b2 : 8; b3 : 8; };   // value = b0<<24 | b1<<16 | b2<<8 | b3
bitfield NameDisp { mType : 8; mClanName : 1; };
bitfield OptionData {                                   // 376 bits, PC 03040008 order (§ 2.2)
    mIsCamRevise : 1; mIsCamDrama : 1; mCamRangeMagic : 8; mCamRangeBow : 8; mCamPosType : 8;
    pcNewBit09 : 1; mIsMenuWindowOffAuto : 1; mDefaultRimWarpTabPos : 8; mIsPartyBattleBGM : 1;
    BeU32 mPlayerIdlingEmotion; mPlayerIdlingEmotionTime : 8; mIsRotMiniMap : 1;
    mAlphaMiniMap : 8; mIsMapDispName : 1; mIsDispCharges : 1; mIsTutorialAnnounce : 1;
    mIsMatchingAnnounce : 1; mAlphaHUDCmn : 8; mIsQuestActiveAuto : 1; mIsDispQuestGuide : 1;
    mIsQuestGuideAuto : 1; mQuestGuidePrio : 8; mIsDyingFilterDisp : 1;
    mIsMailBoxDispWarning : 1; mHeaderDispType : 8; NameDisp mHeaderNameDispParty;
    NameDisp mHeaderNameDispOther; mIsHeaderNameNpcName : 1; mIsHeaderNameNpcClass : 1;
    mIsHeaderNameOmName : 1; NameDisp mChatLogNameDisp; mIsChatLogTimeStamp : 1;
    mAlphaChat : 8;
    // 12 x (mChatChFilterColor[i] : 8, mChatChFilterSE[i] : 8), interleaved
    mIsClockDispPing : 1; mIsClockDispTime : 1; mClockDispType : 8; mIsClockDispCh : 1;
    mIsEngageDisp : 1; mIsAchievementDispAnnounce : 1; mIsRewardBoxDispWarning : 1;
    mIsMiniMapAutoScale : 1; pcNewU8_37 : 8; pcNewBit96 : 1; pcNewBit97 : 1; pcNewBit98 : 1;
};
bitfield ChatCstmCh { mName0 : 8; /* ... */ mName16 : 8; BeU32 mBit; };   // 17 bytes + u32
bitfield SaveTail {                                     // 1738 bits = 2 + 376 + 336 + 1024
    mIsAppraiseTalked : 1; pcNewBit13637 : 1;
    OptionData mOption;
    ChatCstmCh mChatCstmCh[2];
    BeU32 pcNewA[16]; BeU32 pcNewB[16];
    pad : 6;                                            // zero (flushBits)
} [[bitfield_order(std::core::BitfieldOrder::LeastToMostSignificant, 1744)]];
le SaveTail tail @ blobStart + 304;                     // 218 bytes -> blob byte 522
u8 unwritten[502] @ blobStart + 522;                    // stale allocator memory
```

   If the ImHex version in use cannot nest bitfields or arrays inside a bitfield, the fallback is
   a computed decode: read the 218 tail bytes and extract each field with
   `(byte >> (k & 7)) & 1` arithmetic in pattern functions, in § 2 order.
6. Fit check: the decode ends at blob byte 522 (body offset 522, file offset 531); the packet
   field is still 1024 bytes, so the packet-level fit (file end at 1033 + cipher padding) is
   unchanged.

## 6. Open

- Names and meaning of the PC-only fields (+13637 bool, option +9/+96/+97/+98 bools, option +37
  u8, the two u32[16] arrays). The PC has no symbols; a name needs PC-side evidence (UI code that
  reads these offsets, option menu strings), not tried here.
- `sub_466560`'s other callers `sub_465700`, `sub_7C7F20` (local save? other packet?) not read.
- The allocator behind vtable +36 of `src` was not read; "stale memory" in bytes 522..1023 is
  inferred from the absent memset plus the non-zero captures.
- The ImHex sketch is unvalidated (no ImHex CLI on `PATH`).
- Databases not closed: `close_database` is not available to this role.

## Appendix A: walk script (final version, stdlib only)

Run as `python -X utf8 -I walk_savebin.py [--detail] FILE...` (scratch copy, not committed).
`merge.py` (scratch) only joined three `--detail` outputs into the table in § 3.

```python
"""Walk the 9.1.1 cCharacterData bit stream (PC 03040008 sub_467790 / sub_4678F0).

Usage: python -X utf8 -I walk_savebin.py [--detail] FILE...
Bit order: LSB-first inside each byte (bit k = byte k>>3, mask 1<<(k&7)).
writeBits(v, n): bit i of v (LSB first) -> next stream bit.
writeBytes(p, n): byte j bit i -> next stream bit (byte order kept).
u32/u64: big-endian bytes through writeBytes. u8: writeBytes(&v, 1). Elias-delta off.
"""
import hashlib
import sys

BODY = 9          # decrypted_raw header: u8 group, u16 id, u8 sub, u8 source, u32 counter
BLOB = 1024


class Bits:
    def __init__(self, buf):
        self.buf = buf
        self.pos = 0

    def bits(self, n):
        v = 0
        for i in range(n):
            k = self.pos
            if (self.buf[k >> 3] >> (k & 7)) & 1:
                v |= 1 << i
            self.pos += 1
        return v

    def bytes_(self, n):
        return bytes(self.bits(8) for _ in range(n))

    def u8(self):
        return self.bits(8)

    def u32(self):
        return int.from_bytes(self.bytes_(4), "big")

    def u64(self):
        return int.from_bytes(self.bytes_(8), "big")


# (name, kind) in PC write order; kind: b=1 bit, B=u8, W=u32, Q=u64, S17=17 raw bytes
OPTION = [
    ("mIsCamRevise", "b"), ("mIsCamDrama", "b"), ("mCamRangeMagic", "B"),
    ("mCamRangeBow", "B"), ("mCamPosType", "B"), ("pc_new_opt_bit_09 (v>=0x15)", "b"),
    ("mIsMenuWindowOffAuto", "b"), ("mDefaultRimWarpTabPos", "B"),
    ("mIsPartyBattleBGM", "b"), ("mPlayerIdlingEmotion", "W"),
    ("mPlayerIdlingEmotionTime", "B"), ("mIsRotMiniMap", "b"), ("mAlphaMiniMap", "B"),
    ("mIsMapDispName", "b"), ("mIsDispCharges", "b"), ("mIsTutorialAnnounce", "b"),
    ("mIsMatchingAnnounce", "b"), ("mAlphaHUDCmn", "B"), ("mIsQuestActiveAuto", "b"),
    ("mIsDispQuestGuide", "b"), ("mIsQuestGuideAuto", "b"), ("mQuestGuidePrio", "B"),
    ("mIsDyingFilterDisp", "b"), ("mIsMailBoxDispWarning", "b"), ("mHeaderDispType", "B"),
    ("mHeaderNameDispParty.mType", "B"), ("mHeaderNameDispParty.mClanName", "b"),
    ("mHeaderNameDispOther.mType", "B"), ("mHeaderNameDispOther.mClanName", "b"),
    ("mIsHeaderNameNpcName", "b"), ("mIsHeaderNameNpcClass", "b"),
    ("mIsHeaderNameOmName", "b"), ("mChatLogNameDisp.mType", "B"),
    ("mChatLogNameDisp.mClanName", "b"), ("mIsChatLogTimeStamp", "b"), ("mAlphaChat", "B"),
] + [
    item for i in range(12)
    for item in ((f"mChatChFilterColor[{i}]", "B"), (f"mChatChFilterSE[{i}]", "B"))
] + [
    ("mIsClockDispPing", "b"), ("mIsClockDispTime", "b"), ("mClockDispType", "B"),
    ("mIsClockDispCh", "b"), ("mIsEngageDisp", "b"), ("mIsAchievementDispAnnounce", "b"),
    ("mIsRewardBoxDispWarning", "b"), ("mIsMiniMapAutoScale", "b"),
    ("pc_new_opt_u8_37 (v>=0x14)", "B"), ("pc_new_opt_bit_96 (v>=0x17)", "b"),
    ("pc_new_opt_bit_97 (v>=0x18)", "b"), ("pc_new_opt_bit_98 (v>=0x18)", "b"),
]

FIELDS = (
    [("mVersion", "W"), ("mReleaseVersion", "W")]
    + [item for i in range(16) for item in
       ((f"mCheckPawnHistory[{i}].mPawnId", "W"), (f"mCheckPawnHistory[{i}].mCheckDate", "Q"))]
    + [("mQuestEtcF", "W")]
    + [(f"mTutorialGuide.mFinishTutorial[{i}]", "W") for i in range(16)]
    + [(f"mTutorialGuide.mLatestTutorial[{i}]", "W") for i in range(5)]
    + [("mJobMasterTalked[0]", "W"), ("mJobMasterSkillTalked[0]", "W"),
       ("mAreaMasterTalked[0]", "W"), ("mEnteredLand[0]", "W"),
       ("mIsAppraiseTalked", "b"), ("pc_new_bit_13637 (v>=0x19)", "b")]
    + [("mOption." + n, k) for n, k in OPTION]
    + [item for i in range(2) for item in
       ((f"mChatCstmCh[{i}].mName", "S17"), (f"mChatCstmCh[{i}].mBit", "W"))]
    + [(f"pc_new_u32_13508[{i}] (v>=0x16)", "W") for i in range(16)]
    + [(f"pc_new_u32_13572[{i}] (v>=0x16)", "W") for i in range(16)]
)

WIDTH = {"b": 1, "B": 8, "W": 32, "Q": 64, "S17": 136}


def walk(path, detail):
    raw = open(path, "rb").read()
    blob = raw[BODY:BODY + BLOB]
    assert len(blob) == BLOB, (path, len(raw))
    r = Bits(blob)
    rows = []
    for name, kind in FIELDS:
        off = r.pos
        if kind == "b":
            v = r.bits(1)
        elif kind == "B":
            v = r.u8()
        elif kind == "W":
            v = r.u32()
        elif kind == "Q":
            v = r.u64()
        else:
            v = r.bytes_(17)
        rows.append((off, WIDTH[kind], name, v))
    end_bits = r.pos
    end_byte = (end_bits + 7) // 8
    tail_bits = r.bits(end_byte * 8 - end_bits)
    rest = blob[end_byte:]
    nz_rest = sum(1 for x in rest if x)
    issues = []
    v = rows[0][3]
    rv = rows[1][3]
    if v != 0x19:
        issues.append(f"mVersion {v:#x}")
    if rv != 0x3040:
        issues.append(f"mReleaseVersion {rv:#x}")
    if tail_bits:
        issues.append(f"pad bits in last byte = {tail_bits:#x}")
    if nz_rest:
        issues.append(f"{nz_rest} non-zero bytes after end")
    sha = hashlib.sha256(raw).hexdigest()
    print(f"{path}\n  sha256 {sha} size {len(raw)} end_bit {end_bits} end_byte {end_byte} "
          f"(file offset {BODY + end_byte}) tail_bits {tail_bits} nonzero_after_end {nz_rest} "
          f"issues {issues or 'none'}")
    if detail:
        for off, w, name, val in rows:
            if isinstance(val, bytes):
                s = val.hex() + " " + repr(val.split(b"\0")[0].decode("utf-8", "replace"))
            else:
                s = f"{val:#x}" if w > 1 else str(val)
            print(f"    {off:5d} {w:3d} {name} = {s}")
    return not issues


def main():
    args = sys.argv[1:]
    detail = "--detail" in args
    files = [a for a in args if a != "--detail"]
    ok = sum(walk(f, detail) for f in files)
    print(f"files {len(files)} clean {ok} with_issues {len(files) - ok}")


main()
```
