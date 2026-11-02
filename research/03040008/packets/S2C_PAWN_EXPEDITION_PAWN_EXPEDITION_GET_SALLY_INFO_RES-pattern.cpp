// 58.0.2 S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_INFO_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 4.1.
// PC handler 0x7ea0a0 (data in the database, read linearly), reader 0x811c80: RES header, u8, list
// 0x75e8e0 (CDataCommonU32), list 0x7594b0 {u32, u32}, list 0x75e8e0, list 0x771d70 {u32, u32, u32} (V).
// PS4 CPacket_S2C_PAWN_EXPEDITION_GET_SALLY_INFO_RES::ReadPacket 0x19e0200: u8 m_ucSallyCount,
// m_AreaIdList, m_HotSpotInfoList, m_ActiveBuffLineupList, m_ClanSallySpotInfoList (V). No Season 3
// change. Walk: 30/30 fit, slack 2-10; ActiveBuffLineupList and ClanSallySpotInfoList never non-empty.
// Body: s32 Error [, s32 Result, u8 SallyCount, 4 lists].
// packet-id: 58.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "PawnExpedition.hexpat"

struct S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u8 SallyCount;
        MtTypedArray<CDataCommonU32> AreaIdList;               // PC 0x75e8e0
        MtTypedArray<CDataAreaSpotSet> HotSpotInfoList;        // PC 0x7594b0
        MtTypedArray<CDataCommonU32> ActiveBuffLineupList;     // PC 0x75e8e0
        MtTypedArray<CDataPawnExpeditionClanSallySpotInfo> ClanSallySpotInfoList;  // PC 0x771d70
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_INFO_RES packet @ 0x00;
