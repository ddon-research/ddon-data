// 3.2.16 S2C_LOBBY_LOBBY_CHAT_MSG_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 2.4 (section 6 for the shared types).
// PC handler 0x7e29b0 (undefined code, read linearly), reader 0x80e840: u8, u32, 0x75ecf0
// (CDataCommunityCharacterBaseInfo), u8, u32, u32, MtString; no error header (V). PS4
// CPacket_S2C_LOBBY_CHAT_MSG_NOTICE::ReadPacket 0x19d49f0: u8 m_ucType, u32 m_unHandleId,
// m_CharacterBaseInfo, MtString m_wstrMessage (V). Season 3: the u8 + u32 + u32 of 3.2.1 before the
// message (V; the PS4 body fails 463/463, PS4 framing fails 463/463). Walk: 463/463 fit, slack 0-15.
// Body: u8 Type, u32 HandleId, CDataCommunityCharacterBaseInfo, u8, u32, u32, MtString Message (var).
// packet-id: 3.2.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Character.hexpat"

struct S2C_LOBBY_LOBBY_CHAT_MSG_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u8 Type;
    u32 HandleId;
    CDataCommunityCharacterBaseInfo CharacterBaseInfo;
    u8 unk_u8;                  // Season 3; server: MessageFlavor (lead)
    u32 unk_u32_0;              // Season 3; server: PhrasesCategory (lead)
    u32 unk_u32_1;              // Season 3; server: PhrasesIndex (lead)
    MtString Message;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_LOBBY_LOBBY_CHAT_MSG_NTC packet @ 0x00;
