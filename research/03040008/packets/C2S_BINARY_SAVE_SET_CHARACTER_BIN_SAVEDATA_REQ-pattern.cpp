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
#include "CharacterData.hexpat"

// cCharacterData save blob (include/CharacterData.hexpat; T001b =
// specs/006-packet-pattern-coverage/research/T001b-save-blob.md). The writer is ungated: every
// field is written (version 0x19). 47/47 captures equal T001b's walk script field by field.

struct C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CharacterBinSaveData m_Data;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ packet @ 0x00;
