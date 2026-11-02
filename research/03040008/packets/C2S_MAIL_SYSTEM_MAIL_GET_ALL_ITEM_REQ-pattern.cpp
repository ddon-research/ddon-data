// 37.11.1 C2S_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 16.
// PC writer 0x82f590 (37, 11, 1): u64, u8 (V; caller 0x872050 forwards both from UI state). PS4
// 0x19c9530: u64 m_ullId only (V): Season 3 adds the u8 (13 in 5/5 captures). The PS4 body also
// fits 5/5 (1 byte inside the window): the u8 rests on the PC writer. Walk: 5/5 fit, slack 14.
// Body: u64 Id, u8 (9 bytes).
// packet-id: 37.11.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u64 Id;
    // T014b V (role); name I (lead agrees): writer 0x82f590 <- 0x872050 <- mail UI 0x54cbd0 /
    // 0x54d360. 0x54cbd0 opens the dialog 0x525b20 -> 0x67eb00 with options in order common_dialog
    // 0x1F8 'Receive in Post', 0x1F9 'Receive in item bag' (disabled outside the lobby, (...)
    u8 StorageType;                  // Season 3, no PS4 member; server: StorageType (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_REQ packet @ 0x00;
