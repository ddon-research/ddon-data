// 12.0.2 S2C_STAGE_GET_STAGE_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 7. PC handler 0x7fd9e0
// (string 0x1bc9a94; on-stack packet 12, 0, 2), reader 0x81cc40 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_STAGE_LIST_RES 0x2f33c0; its CDataStageAttribute has 9 b8, PC reads 11
// (0x779f40): the last two are Season 3.
// Body: s32 Error [, s32 Result, list] (P11a G1).
// packet-id: 12.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC 0x779f40: 11 bools.
struct CDataStageAttribute {
    bool IsSolo;
    bool IsEnablePartyFunc;
    bool IsAdventureCountKeep;
    bool IsEnableCraft;
    bool IsEnableStorage;
    bool IsEnableStorageInCharge;
    bool IsNotSessionReturn;
    bool IsEnableBaggage;
    bool IsClanBase;
    bool unk_bool_0;           // Season 3
    bool unk_bool_1;           // Season 3
};

// PC list 0x77a020.
struct CDataStageInfo {
    u32 ID;
    u32 StageNo;
    u32 RandomStageGroupID;
    u32 Type;
    CDataStageAttribute StageAttribute;
    bool IsAutoSetBloodEnemy;
};

struct S2C_STAGE_GET_STAGE_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataStageInfo> StageInfoList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_STAGE_GET_STAGE_LIST_RES packet @ 0x00;
