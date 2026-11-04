// 9.0.2 S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES (client 03040008).
// Body: s32 Error [, s32 Result, u8[1024] save blob]. P4 3 (PC handler 0x7c68de, reader 0x801530,
// blob reader 0x757de0). No capture: not validated on data.
// packet-id: 9.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "CharacterData.hexpat"

// cCharacterData save blob (include/CharacterData.hexpat; T001b =
// specs/006-packet-pattern-coverage/research/T001b-save-blob.md 4). The handler (PC 0x7c68de)
// reads it with the BitReader mirror of the writer through sub_466560, which tests the blob's
// mVersion before each field (V): g_cdGated applies those gates. At version 0x19 the decode
// equals the 9.1.1 one (checked on a synthetic response built from a 9.1.1 blob).
g_cdGated = true;

struct S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CharacterBinSaveData m_Data;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES packet @ 0x00;
