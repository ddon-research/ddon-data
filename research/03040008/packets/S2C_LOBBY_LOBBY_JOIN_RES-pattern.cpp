// 3.0.2 S2C_LOBBY_LOBBY_JOIN_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 2.1 (section 6 for the shared types).
// PC handler 0x7e2ce0, reader 0x80ea20: RES header, u32, list 0x76d6f0 (read linearly) of element
// 0x76d7f0 (V). PS4 OnPacket_S2C_LOBBY_JOIN_RES 0x2de4d0 (inline): u32 m_unCharacterID,
// MtTypedArray<CDataLobbyMemberInfo> (V; list member name not given: LobbyMemberInfoList is I, after the element type).
// Season 3: CDataLobbyMemberInfo has 3 trailing u8, PS4 4 (V by code; include/Character.hexpat).
// The id 3.0.2 is also the login server's L2C_GET_ERROR_MESSAGE_LIST_RES (41 files): packet-select
// keeps the LOBBY files. Walk: 41/41 fit, slack 7-9, one member per capture.
// Body: s32 Error [, s32 Result, u32 CharacterID, list CDataLobbyMemberInfo] (16 + var bytes).
// packet-id: 3.0.2
// packet-select: S2C_LOBBY_LOBBY_JOIN_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Character.hexpat"

struct S2C_LOBBY_LOBBY_JOIN_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 CharacterID;
        MtTypedArray<CDataLobbyMemberInfo> LobbyMemberInfoList;   // name I (element type)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_LOBBY_LOBBY_JOIN_RES packet @ 0x00;
