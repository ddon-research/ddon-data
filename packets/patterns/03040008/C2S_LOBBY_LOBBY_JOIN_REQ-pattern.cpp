// 3.0.1 C2S_LOBBY_LOBBY_JOIN_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 2.1.
// PC writer 0x82ede0 (undefined code, read linearly): WritePacket(p, 3, 0, 1, -1) at 0x82ee53, then
// Write_u32, Write_u32 (V). PS4 Send_C2S_LOBBY_JOIN_REQ 0x19b0ec0: u32 in_CharacterID,
// u32 in_UserListMaxNum (V). No Season 3 change. The id 3.0.1 is also the login server's
// C2L_GET_ERROR_MESSAGE_LIST_REQ (41 files): packet-select keeps the LOBBY files.
// Walk: 41/41 fit, slack 15.
// Body: u32 CharacterID, u32 UserListMaxNum (8 bytes).
// packet-id: 3.0.1
// packet-select: C2S_LOBBY_LOBBY_JOIN_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_LOBBY_LOBBY_JOIN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 CharacterID;
    u32 UserListMaxNum;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_LOBBY_LOBBY_JOIN_REQ packet @ 0x00;
