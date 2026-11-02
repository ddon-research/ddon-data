// 2.18.1 C2S_CHARACTER_CHARACTER_PENALTY_REVIVE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 8.
// PC writer 0x820e00 (2, 18, 1): u32, u32 (V; caller 0x879940 pushes both). PS4 0x19cbeb0: u32
// m_unHpMax only (V): Season 3 adds a u32. Which of the two is PS4's HpMax is I (position); the
// captures hold 3198/4265 (first < second). The PS4 body fails 2/2. Walk: 2/2 fit, slack 15.
// Body: u32 HpMax, u32 (8 bytes).
// packet-id: 2.18.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CHARACTER_CHARACTER_PENALTY_REVIVE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 HpMax;                  // I (PS4 position); server: Unk0 (lead)
    u32 unk_u32;                // Season 3, no PS4 member; server: Unk1 (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_CHARACTER_PENALTY_REVIVE_REQ packet @ 0x00;
