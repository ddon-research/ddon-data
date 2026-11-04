// 31.31.2 S2C_CLAN_CLAN_BASE_GET_INFO_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 19.
// PC handler 0x7ca610, reader 0x802de0: list U32, list U32, CDataPawnExpeditionInformation
// 0x771e80, CDataClanPartnerPawnInfo 0x75d770, CDataClanConciergeInfo 0x75d120, list
// CDataClanShopLineupName 0x75e2f0, list CDataClanValueInfo 0x75e500, list CDataFurnitureLayout
// 0x766f90 (V). PS4 CPacket_S2C_CLAN_BASE_GET_INFO_RES::ReadPacket 0x19dbe20 reads the first eight
// members in the same order and ends there: Season 3 adds the furniture list, ClanFurnitureList (I:
// element type V, by the PC reader the MY_ROOM furniture list shares; server: ClanFurnitureInfo
// (lead)). The PS4 body fails 27/27.
// Walk: 27/27 fit, slack 0-12 (function list up to 9, lineup names 50, values 2, furniture 8).
// Body: s32 Error [, s32 Result, the eight PS4 members, list CDataFurnitureLayout].
// packet-id: 31.31.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Clan.hexpat"

struct S2C_CLAN_CLAN_BASE_GET_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataClanFunctionInfo FunctionInfo;                         // PC list 0x75e8e0
        CDataClanDungeonInfo DungeonInfo;                           // PC list 0x75e8e0
        CDataPawnExpeditionInformation PawnExpeditionInfo;          // PC 0x771e80
        CDataClanPartnerPawnInfo PartnerPawnInfo;                   // PC 0x75d770
        CDataClanConciergeInfo ConciergeInfo;                       // PC 0x75d120
        MtTypedArray<CDataClanShopLineupName> ShopLineupNameList;   // PC 0x75e2f0
        MtTypedArray<CDataClanValueInfo> ClanValueInfoList;         // PC 0x75e500
        MtTypedArray<CDataFurnitureLayout> ClanFurnitureList;       // Season 3, PC 0x766f90; name I
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CLAN_CLAN_BASE_GET_INFO_RES packet @ 0x00;
