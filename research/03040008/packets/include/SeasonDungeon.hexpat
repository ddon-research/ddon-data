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
    // T004 I (same structure: inline {u32, u8, u32} = CDataStageLayoutId; value: StageId 558, 559,
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
    // T004 I (value: in 243/243 objectives the label text names the server enum value: 1 "defeat 20
    // enemies", 4 "must not die once or more", 5 "must not be afflicted 3 times", 7 "must not use an
    // item", 8 "annihilate the enemies", 10 "achieve within the time limit"; lead agrees): server
    // Type (SoulOrdealObjective)
    u8 Type;
    // T004 I (value: 1 on the first objective of every list (types 1, 8), 2 on the others; lead
    // agrees): server Priority (1 primary, 2 secondary)
    u8 Priority;
    // T004 G (lead): server Param1 ("Amount"; time in seconds for type 10); captured: the running
    // count for type 1 (label "n/20" agrees), 150-300 for type 10, else 0-3
    u32 Param1;
    u32 Param2;     // T004 G (lead): server Param2; captured 1 or 0
    MtString ObjectiveLabel;    // T004 I (value: Japanese objective texts); server: ObjectiveLabel (lead agrees)
};

// CDataSoulOrdealRewardItem: PC list reader 0x769240 {u32, u32} (62.34.2, V) and list writer
// 0x77f9d0 {Write_u32 +4, Write_u32 +8} (62.34.1, V, 008 T002). Struct name: server (lead).
struct CDataSoulOrdealRewardItem {
    // T004 I (value: 52/52 62.34.1 pairs equal (Id, Num) of an ItemRewards element of the preceding
    // 62.33.2; lead agrees): server RewardIndex
    u32 RewardIndex;
    // T004 I (value: 62.34.1 = the reward's Num, 52/52; 62.34.2 returns 0 in 52/52); server: Amount (lead)
    u32 Amount;
};
