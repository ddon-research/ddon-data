// 45.0.2 S2C_STAMP_BONUS_GET_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// sections 1.2 and 18.
// PC handler 0x7fe140 (not a function in the database; read linearly), reader 0x81d170: RES header,
// list 0x77a490 (daily group), then 0x77a7d0 {u16, list 0x77a6b0} (V). PS4
// CPacket_S2C_STAMP_BONUS_GET_LIST_RES::ReadPacket 0x19df1a0: u16 m_usTotalStampNum,
// MtTypedArray<CDataStampBonusDaily> m_StampBonusDaily, MtTypedArray<CDataStampBonusTotal>
// m_StampBonusTotal (V). Season 3 (V by code): the daily list is wrapped in groups {u32, u32, list},
// the u16 moved behind them (TotalStampNum there: I, position + PS4 member), and CDataStampBonus has
// 3 u32. The PS4 body fails 81/81. Walk: 81/81 fit, slack 3 (1 daily group (1, 77) with 8 dailies,
// 10 totals).
// Body: s32 Error [, s32 Result, list CDataStampBonusDailyGroup, u16 TotalStampNum, list
// CDataStampBonusTotal] (variable).
// packet-id: 45.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Stamp.hexpat"

struct S2C_STAMP_BONUS_GET_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataStampBonusDailyGroup> DailyGroupList;    // PC 0x77a490; Season 3, field name I (Stamp.hexpat)
        u16 TotalStampNum;                                          // PC 0x77a7d0; I (position, PS4 member)
        MtTypedArray<CDataStampBonusTotal> StampBonusTotal;         // PC 0x77a6b0 (inside 0x77a7d0)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_STAMP_BONUS_GET_LIST_RES packet @ 0x00;
