// 2.0.1 C2S_CHARACTER_DECIDE_CHARACTER_ID_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 2.
// PC writer 0x821360 (2, 0, 1): u32 (V). PS4 Send_C2S_DECIDE_CHARACTER_ID_REQ 0x19b0510: u32
// m_unCharacterID (V). Walk: 42/42 fit, slack 3.
// Body: u32 CharacterID (4 bytes).
// packet-id: 2.0.1
// packet-select: C2S_CHARACTER_DECIDE_CHARACTER_ID_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CHARACTER_DECIDE_CHARACTER_ID_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 CharacterID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_DECIDE_CHARACTER_ID_REQ packet @ 0x00;
