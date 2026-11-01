// 13.0.2 S2C_INSTANCE_GET_ENEMY_SET_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 2 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7db4c0, reader 0x80b300: RES header, LayoutId (0x77a330), u8, u32, u32, list
// 0x76ca20, list 0x764400, list 0x76f450 (V). PS4 CPacket_S2C_GET_ENEMY_SET_LIST_RES::ReadPacket
// 0x19d7000 (V), the same members. Season 3: the enemy info gains a sixth bool
// (include/Instance.hexpat). Walk: 667/667 fit, slack 1-15; enemy list up to 10, drop list up to
// 3, NamedParamList never non-empty (code-only); no captured RES has Error != 0.
// Body: s32 Error [, s32 Result, LayoutId, u8 SubGroupId, u32 RandomSeed, u32 QuestId,
// MtTypedArray<CDataLayoutEnemyData> EnemyList, MtTypedArray<CDataDropItemSetInfo>
// DropItemSetList, MtTypedArray<CDataNamedEnemyParamClient> NamedParamList] (38 + 32a + 22b +
// 49c bytes).
// packet-id: 13.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_GET_ENEMY_SET_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataStageLayoutId LayoutId;
        u8 SubGroupId;
        u32 RandomSeed;
        u32 QuestId;
        MtTypedArray<CDataLayoutEnemyData> EnemyList;
        MtTypedArray<CDataDropItemSetInfo> DropItemSetList;
        MtTypedArray<CDataNamedEnemyParamClient> NamedParamList;   // never non-empty in captures (code-only)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_GET_ENEMY_SET_LIST_RES packet @ 0x00;
