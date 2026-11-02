// 28.9.2 S2C_GP_GP_SHOP_DISPLAY_BUY_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 8.
// PC handler 0x7d8590 (not a function in the PC database), reader 0x8098d0: u32, list
// CDataCommonU32, u32, MtString (V). PS4 CPacket_S2C_GP_SHOP_DISPLAY_BUY_RES::ReadPacket 0x19d7ed0
// {u32 m_unLineupId, m_CommonIdList, u32 m_unBalance, MtString m_wstrLineupName}: same (V).
// CommonIdList is empty in every capture (its element is code-only).
// Walk: 9/9 fit.
// Body: s32 Error [, s32 Result, u32 LineupId, list CDataCommonU32 CommonIdList, u32 Balance,
// MtString LineupName].
// packet-id: 28.9.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_GP_GP_SHOP_DISPLAY_BUY_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 LineupId;
        MtTypedArray<CDataCommonU32> CommonIdList;     // PC 0x75e8e0
        u32 Balance;
        MtString LineupName;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_GP_SHOP_DISPLAY_BUY_RES packet @ 0x00;
