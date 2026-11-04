// 2.0.2 S2C_CHARACTER_DECIDE_CHARACTER_ID_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// sections 1.3 and 2.
// PC handler 0x7c7f20, reader 0x802060: RES header, u32, CDataCharacterInfo 0x75c2a0, bool,
// u8[1024] by 0x757de0 (the save-blob reader of 9.0.2), u8 (V). PS4
// CPacket_S2C_DECIDE_CHARACTER_ID_RES::ReadPacket 0x19d4760: u32 m_unCharacterID, CCharacterInfo
// m_CharacterInfo, b8 m_bIsReturnPrepare, u8[1024] m_ucBin (V). Season 3: CharacterInfo item 15
// (include/CharacterInfo.hexpat) and the trailing u8 (no PS4 member; 1 in 42/42 captures). The PS4
// body fails 22/42. Walk: 42/42 fit, slack 0-12.
// Body: s32 Error [, s32 Result, u32 CharacterID, CDataCharacterInfo, bool IsReturnPrepare, u8[1024]
// save blob, u8] (variable).
// packet-id: 2.0.2
// packet-select: S2C_CHARACTER_DECIDE_CHARACTER_ID_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "CharacterData.hexpat"
#include "CharacterInfo.hexpat"

// cCharacterData save blob (include/CharacterData.hexpat): read by 0x757de0, the reader of 9.0.2,
// which tests the blob's mVersion before each field (T001b 4): g_cdGated applies those gates.
g_cdGated = true;

struct S2C_CHARACTER_DECIDE_CHARACTER_ID_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 CharacterID;
        CDataCharacterInfo CharacterInfo;                   // PC 0x75c2a0
        bool IsReturnPrepare;
        CharacterBinSaveData Bin;                           // PC 0x757de0 (CharacterData.hexpat)
        // T014b V (store); I (name): PC handler 0x7c7f20 (reader 0x802060): when IsReturnPrepare !=
        // 0 the trailing u8 goes to sGame+0x39F8 and +0x39FC and conn dword 10428 (...)
        u8 GameMode;                                          // Season 3, no PS4 member; server: Unk1 (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_DECIDE_CHARACTER_ID_RES packet @ 0x00;
