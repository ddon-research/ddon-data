// 9.1.1 C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ (client 03040008).
// Body: u8[1024] save blob, no length prefix. P4 3 (PC writer 0x820360: WritePacket(9,1,1) +
// 0x77d020 writing 1024 x u8; sender 0x87edd0).
// packet-id: 9.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// cCharacterData::serialize bit stream (P4 3.1; PS4 0x49740, PC serializer 0x467790, flush
// 0x896a40). Only the two leading u32 are decoded: they read as plain big-endian values in the
// captures (P4 3.1, PC-cap). The bit-level walk of the rest against P4 3.1's field list was not
// run (no file, SHA-256 or offset is recorded), so whether it is byte-aligned is open.
// TODO: decode the rest per P4 3.1 (mCheckPawnHistory[16], mQuestEtcF, stTutorialGuide, the
// talked flags, mIsAppraiseTalked + 1 new bit, stOptionData (32 bits, 17 u8, 1 u32 on PC),
// mChatCstmCh[2], u32[16] x 2 new) once the BitWriter bit order and Elias-delta use are read.
struct CharacterBinSaveData {
    u32 mVersion;          // captures: 0x19
    u32 mReleaseVersion;   // captures: 0x3040
    u8 undecoded[1016];    // TODO (bit stream, see above)
};

struct C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CharacterBinSaveData m_Data;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ packet @ 0x00;
