// 39.1.1 C2S_GACHA_GACHA_BUY_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 16.
// PC writer 0x841020 (39, 1, 1): u32 x4 (V). PS4 CPacket_C2S_GACHA_BUY_REQ::WritePacket 0x1a328b0
// {m_unId, m_unDrawGroupId, m_unSettlementId, m_unPrice}: same (V).
// Walk: 21/21 fit, slack 7.
// Body: u32 Id, u32 DrawGroupId, u32 SettlementId, u32 Price (16 bytes).
// packet-id: 39.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_GACHA_GACHA_BUY_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 Id;
    u32 DrawGroupId;
    u32 SettlementId;
    u32 Price;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_GACHA_GACHA_BUY_REQ packet @ 0x00;
