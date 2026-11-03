// Group 62 SEASON_DUNGEON CData of client 03040008 (PC, Season 3), shared by the season dungeon
// (soul ordeal / trial) packet patterns.
//
// Source: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 3 and § 4. "PC 0x..." is the
// reader or writer VA in the PC 03040008 database (image base 0x400000). No PS4 02020005 type exists
// (Season 3 group). Marks (spec 008): V = read in the PC code, I (basis) = inferred, G (basis) =
// guess; server C# (Arrowgene) names are leads, "server: <name> (lead)". Comments read
// `// T004 <mark>: <basis>`.
// Includes Packet.hexpat and Instance.hexpat (CDataStageLayoutId); neither includes this file.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Instance.hexpat"

// CDataSeasonDungeonOmState: PC reader 0x766790 {u32 +12, u8 +16, u32 +20, u32 +24, u8 +28} (V
// widths and order); the first three are the CDataStageLayoutId triplet every OM packet carries
// (I, same structure). Struct name G (context: an OM's layout id, position and state; server has no
// class, it writes the fields flat). Users: 62.26.16 (whole body, handler 0x7f8970), 62.15.16
// (reader 0x81a3c0).
struct CDataSeasonDungeonOmState {
    // T004 I (same structure: inline {u32, u8, u32} = CDataStageLayoutId; value, 32 distinct, chance 0.29: StageId 558, 559,
    // 560, 655 and GroupIds that the 62.12.16/18.1/33.1/40.16 requests name again, 344/344); server:
    // LayoutId (lead agrees)
    CDataStageLayoutId LayoutId;
    u32 PosId;      // T004 G (lead): server PosId; captured 0 in 456/456
    // T004 G (lead): server State (SoulOrdealOmState: 0 locked, 1 area unlocked, 3 trial complete,
    // 4 blue, 5 reward available, 6 reward received, 7 scatter powers, 10 trial available); captured
    // 10, 0, 6, 4, 9, 73, 74, 75, 5 (62.26.16) and 5, 0 (62.15.16)
    u8 State;
};

// CDataSoulOrdealObjective: PC list reader 0x779090 {u8 +4, u8 +5, u32 +8, u32 +12, MtString +16}
// (V). Users: 62.14.16 (reader 0x81a2c0), 62.16.16 (reader 0x81a530). Struct name: server
// CDataSoulOrdealObjective (lead).
struct CDataSoulOrdealObjective {
    // T004 I (value, 6 distinct: in 243/243 objectives the label text names the server enum value: 1 "defeat 20
    // enemies", 4 "must not die once or more", 5 "must not be afflicted 3 times", 7 "must not use an
    // item", 8 "annihilate the enemies", 10 "achieve within the time limit"; lead agrees): server
    // Type (SoulOrdealObjective)
    u8 Type;
    // T004 G (lead; value consistent: 2 distinct; 1 on the first objective of every list (types 1, 8), 2 on the others; lead
    // agrees): server Priority (1 primary, 2 secondary)
    u8 Priority;
    // T004 G (lead): server Param1 ("Amount"; time in seconds for type 10); captured: the running
    // count for type 1 (label "n/20" agrees), 150-300 for type 10, else 0-3
    u32 Param1;
    u32 Param2;     // T004 G (lead): server Param2; captured 1 or 0
    MtString ObjectiveLabel;    // T004 I (value, 31 distinct: Japanese objective texts); server: ObjectiveLabel (lead agrees)
};

// CDataSoulOrdealRewardItem: PC list reader 0x769240 {u32, u32} (62.34.2, V) and list writer
// 0x77f9d0 {Write_u32 +4, Write_u32 +8} (62.34.1, V, 008 T002). Struct name: server (lead).
struct CDataSoulOrdealRewardItem {
    // T004 G (lead; value consistent: 3 distinct; 52/52 62.34.1 pairs equal (Id, Num) of an ItemRewards element of the preceding
    // 62.33.2; lead agrees): server RewardIndex
    u32 RewardIndex;
    // T004 I (value, 6 distinct: 62.34.1 = the reward's Num, 52/52; 62.34.2 returns 0 in 52/52); server: Amount (lead)
    u32 Amount;
};

// ---- 008 T005 additions (batch B3; comments read `// T005 <mark>: <basis>`, report
// specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 3, § 4) ----

// CDataSeasonDungeonBuffEffect: PC reader 0x779540 {u32 +4, MtString +8, u32 +12, u32 +16, u32 +20,
// u32 +24, u32 +28} (V). Users: 62.38.16 through CDataSeasonDungeonBuffEffectParam. Struct name G
// (context; server: CDataSeasonDungeonUnk2, lead). Client data: contents_buff_info.abl
// (client/03040008/contents_buff/obj/pl/pl000000/param/etc/contents_buff_info.abl.json).
struct CDataSeasonDungeonBuffEffect {
    // T005 I (value, 5 distinct: 85/85 an AbilityId of contents_buff_info.abl; 62.39.16 repeats it in 27 non-empty of 148 lists); server:
    // BuffId (lead agrees)
    u32 BuffId;
    // T005 I (value, 11 distinct: buff texts, e.g. "攻撃力アップ Lv. 1", whose "Lv. n" suffix is Level 85/85); server:
    // Label (lead)
    MtString BuffName;
    // T005 G (value: 4 in 85/85, the level count (ParamDataArrayNum 4) of every ability in
    // contents_buff_info.abl; one value only, coincidence not ruled out); server: Unk2 (lead)
    u32 MaxLv;
    u32 unk_u32_0;      // T005 open: 0 in 85/85; server: Unk3 (lead)
    u32 unk_u32_1;      // T005 open: 0 in 85/85; server: Unk4 (lead)
    u32 unk_u32_2;      // T005 open: 1 in 85/85 (not the CorrectType: ability 4 is RATE); server: Unk5 (lead)
    // T005 I (value, 5 distinct: 85/85 equal the ParamType (200 + AbilityId: 203-209 captured) of the ability BuffId
    // in contents_buff_info.abl); server: Unk6 (lead)
    u32 ParamType;
};

// CDataSeasonDungeonBuffEffectParam: PC list reader 0x778e70 element {u32 +4, 0x779540 +8} (V). User:
// 62.38.16. Struct name: server (lead).
struct CDataSeasonDungeonBuffEffectParam {
    // T005 G (lead; value consistent: 3 distinct; 85/85 equal the "Lv. n" suffix of BuffEffect.BuffName; captured 1-3); server: Level
    // (lead agrees)
    u32 Level;
    CDataSeasonDungeonBuffEffect BuffEffect;    // T005 G (context); server: Unk1 (lead)
};

// CDataSeasonDungeonBuffLevel: PC list reader 0x778fa0 element {u32 +4, u32 +8} (V). User: 62.39.16.
// Struct name G (context; server: CDataSeasonDungeonUnk0, lead).
struct CDataSeasonDungeonBuffLevel {
    // T005 I (value, 5 distinct; 121 of the 148 lists are empty: 27 non-empty, 21 distinct: the (BuffId, Level) pairs equal those of the 62.38.16 sent within 3 packets,
    // 148/148 lists); server: BuffId (lead agrees)
    u32 BuffId;
    u32 Level;          // T005 G (lead; value consistent: 3 distinct; as BuffId); server: Level (lead agrees)
};

// CDataSeasonDungeonInfo: PC reader 0x777b00 {u32 +4, MtString +8, u32 +12} (V). User: 62.1.2. Struct
// name: server (lead).
struct CDataSeasonDungeonInfo {
    // T005 G (lead; value consistent: 1 distinct; 4/4 equal the DungeonId of the 62.1.1 request; 3); server: Unk0 (lead; the server
    // names the third u32 DungeonId, which the values contradict)
    u32 DungeonId;
    // T005 I (value, 1 distinct: "メガドシスの記憶" 4/4 = stage_list.slt name of StageId 559 "Memory of Megadosys", the
    // StageId 12.9.16 starts); server: Name (lead agrees)
    MtString Name;
    u32 unk_u32;        // T005 open: 40 in 4/4 (not a dungeon StageId); server: DungeonId (lead)
};

// Element of PC reader 0x777c40 {u32 +4, u32 +8} (V), inside CDataSeasonDungeonSection. Struct name G
// (context); server: CDataSeasonDungeonUnk0 {BuffId, Level} (lead; captured 3 with 7/15/23, which are no
// buff levels: names kept unk).
struct CDataSeasonDungeonSectionParam {
    u32 unk_u32_0;      // T005 open: 3 in 16/16; server: BuffId (lead)
    u32 unk_u32_1;      // T005 open: 7, 15, 23; server: Level (lead)
};

// CDataSeasonDungeonSection: PC list reader 0x777d70, element 0x777e80 {u32 +4, u32 +8, u32 +12, u32 +16,
// 0x777c40 +20, bool +32, MtString +36} (V). User: 62.1.2. Struct name: server (lead).
struct CDataSeasonDungeonSection {
    u32 unk_u32_0;      // T005 open: 9, 10, 11, 12 (one per section, in order); server: Unk0 (lead)
    // T005 G (lead; value consistent: 1 distinct, chance 1; 550 in 16/16 = stage_list.slt StageId 550 "Epitaph Road: Shrine"; role open); server:
    // Unk1 (lead)
    u32 StageId;
    u32 unk_u32_1;      // T005 open: 0 in 16/16; server: Unk2 (lead)
    u32 unk_u32_2;      // T005 open: 7, 17, 18, 19; server: Unk3 (lead)
    CDataSeasonDungeonSectionParam unk_Param;   // T005 open; server: Unk4 (lead)
    bool unk_bool;      // T005 open: true on 1 of the 4 sections; server: Unk5 (lead)
    // T005 I (value, 4 distinct: "第1区画 メガドシスの記憶 城内（開始地点）" .. "第4区画 ..."; 12.5.1 sends one back 3/3);
    // server: SectionName (lead agrees)
    MtString SectionName;
};

// CDataSeasonDungeonBlockadeElement: PC list reader 0x777b50 element {u32 +4, MtString +8} (V). User:
// 62.7.2 (empty in 4/4: code only). Struct name: server (lead).
struct CDataSeasonDungeonBlockadeElement {
    u32 EpitaphId;      // T005 G (lead): server EpitaphId
    MtString Name;      // T005 G (lead): server Name
};

// CDataSoulOrdealItem: PC list reader 0x777c80 element {u32 +4, u16 +8} (V). User: 62.9.2. Struct
// name: server (lead).
struct CDataSoulOrdealItem {
    // T005 G (lead; value consistent: 1 distinct, chance 1; 7/7 in base/etc/itemlist.ipa.json, material 18659); server: ItemId (lead agrees)
    u32 ItemId;
    // T005 G (lead; value consistent: 1 distinct; 240 in 7/7 = the sum of Num the following 62.10.1 delivers, 6/6); server: Num
    // (lead agrees)
    u16 Num;
};
