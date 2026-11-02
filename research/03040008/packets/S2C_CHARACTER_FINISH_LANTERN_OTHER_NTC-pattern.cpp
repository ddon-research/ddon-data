// 2.30.16 S2C_CHARACTER_FINISH_LANTERN_OTHER_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 11.
// Code name: FINISH_LANTERN_OTHER_NTC (I: ordering only; the OTHER family is V).
// PC handler 0x7c8f40: u32, no error header, nothing else (V). The four PS4 *_OTHER_NOTICE handlers
// (0x32a660, 0x32a6f0, 0x32aaa0, 0x32ab30) read u32 m_unCharacterID and do nothing else (V): the
// member and layout are V for any of them. Which one: FINISH_LANTERN_OTHER (0x32a6f0) (I by ordering: the PC ids 2.27-2.34
// follow PS4 source order, T009 11).
// The PS4 u16 framing also fits (the window cannot tell): the framing rests on the PC handler.
// Walk: 1/1 fit, slack 3.
// Body: u32 CharacterID (4 bytes).
// packet-id: 2.30.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CHARACTER_FINISH_LANTERN_OTHER_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_FINISH_LANTERN_OTHER_NTC packet @ 0x00;
