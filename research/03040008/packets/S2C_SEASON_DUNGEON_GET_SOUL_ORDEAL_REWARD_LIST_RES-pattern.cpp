// 62.33.2 S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 62.33.2.
// PC handler 0x7f7bb0 cSeedGameSvConnection::OnPacket_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES
// (V name), reader 0x819e70: RES header, list 0x769100 (CDataGatheringItemElement, Instance.hexpat),
// list 0x779420 {u32, u32, MtString, u32} (V). PS4 counterpart: none (Season 3 group).
// Walk: 21/21 fit, slack 0-13; 2-3 item rewards and 5 buff rewards per list.
// Body: s32 Error [, s32 Result, list, list].
// packet-id: 62.33.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

// Element of PC list 0x779420 {u32 +4, u32 +8, MtString +12, u32 +16} (V). Struct name: server
// CDataSeasonDungeonBuffEffectReward (lead).
struct CDataSeasonDungeonBuffEffectReward {
    u32 BuffEffect;     // T004 G (lead): server BuffEffect; captured 13-177
    // T004 I (value: the 62.35.1 request names one of these BuffIds in 21/21); server: BuffId (lead agrees)
    u32 BuffId;
    MtString BuffName;  // T004 I (value: buff texts ending "+Lv.1" or "Lv.Max"); server: BuffName (lead agrees)
    // T004 I (value: 1 with names ending "+Lv.1" (68/68), 4 with "Lv.Max" (35/37)); server: Level (lead;
    // the server serializer writes BuffId here)
    u32 Level;
};

struct S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T004 I (same structure: PC 0x769100 is the gathering item element reader; value: 52/52 item ids
        // in base/etc/itemlist.ipa.json); server: ItemRewards (lead)
        MtTypedArray<CDataGatheringItemElement> ItemRewards;      // PC 0x769100
        MtTypedArray<CDataSeasonDungeonBuffEffectReward> BuffRewards;   // PC 0x779420; server name (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES packet @ 0x00;
