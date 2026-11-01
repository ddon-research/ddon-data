// 13.3.1 C2S_INSTANCE_ENEMY_KILL_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 4 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x8413d0 (nUserSession::CPacket_C2S_INSTANCE_ENEMY_KILL_REQ::WritePacket, sender
// 0x82ba40): LayoutId, u32, u32, f64, f32, f64, bool, bool, u32 (V). PS4
// CPacket_C2S_ENEMY_KILL_REQ::WritePacket 0x1a36ee0 has one bool (V). Season 3: the second bool
// is new; that the first is the PS4 IsNoBattleReword slot is I (position). Walk: 391/391 fit,
// slack 12; the PS4 layout fits too (slack 13): the second bool rests on the PC writer.
// Body: LayoutId, u32 SetId, u32 InnerId, double DropPosX, float DropPosY, double DropPosZ, bool
// IsNoBattleReword, bool unk_bool, u32 RegionFlag (43 bytes).
// packet-id: 13.3.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_INSTANCE_ENEMY_KILL_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    u32 SetId;
    u32 InnerId;
    double DropPosX;
    float DropPosY;
    double DropPosZ;
    bool IsNoBattleReword;   // PS4 m_bIsNoBattleReword (DWARF spelling); slot I (position)
    bool unk_bool;           // Season 3, no PS4 member (PC writer 0x8413d0, V width); server: Unk0 (lead)
    u32 RegionFlag;          // 10-region dead mask (isDead loop, V both platforms)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_ENEMY_KILL_REQ packet @ 0x00;
