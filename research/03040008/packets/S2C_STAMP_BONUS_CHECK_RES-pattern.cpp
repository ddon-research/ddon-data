// 45.1.2 S2C_STAMP_BONUS_CHECK_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// sections 1.2 and 19.
// PC handler 0x7fe070 (not a function in the database; read linearly), reader 0x81d0d0: RES header,
// list 0x77a5c0 {u32, u32}, u8, u8 (V). PS4 CPacket_S2C_STAMP_BONUS_CHECK_RES::ReadPacket 0x19df230
// (and recompilation S2C.cpp:11561): u16 m_usTotalStampNum, u8 m_ucisRecieveBonusDaily,
// u8 m_ucisRecieveBonusTotal (V). Season 3 replaces the u16 by the list (V by code); the two u8 keep
// the PS4 names by position (I). The PS4 body also fits 84/84: the list rests on the PC reader.
// Walk: 84/84 fit, slack 1-9, at most 1 element.
// Body: s32 Error [, s32 Result, list {u32, u32}, u8, u8] (variable).
// packet-id: 45.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Stamp.hexpat"

struct S2C_STAMP_BONUS_CHECK_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataStampBonusCheckRes_unk_0> unk_List;      // PC 0x77a5c0; Season 3; server: StampCheck (lead)
        u8 IsRecieveBonusDaily;                                     // I (PS4 member, position)
        u8 IsRecieveBonusTotal;                                     // I (PS4 member, position)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_STAMP_BONUS_CHECK_RES packet @ 0x00;
