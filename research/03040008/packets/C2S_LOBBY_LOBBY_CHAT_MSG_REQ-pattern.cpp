// 3.2.1 C2S_LOBBY_LOBBY_CHAT_MSG_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 2.3.
// PC writer 0x841ad0 (3, 2, 1): u8, u32, u8, u32, u32, Write_cstr (MtString on the wire) (V).
// PS4 CPacket_C2S_LOBBY_CHAT_MSG_REQ::WritePacket 0x1a3a680: u8 in_Type, u32 in_TargetID,
// MT_CSTR in_strMessage (V). Season 3: u8 + u32 + u32 inserted before the message (V; the PS4
// body fails 328/328). Walk: 328/328 fit, slack 3-15.
// Body: u8 Type, u32 TargetID, u8 unk_u8, u32 unk_u32_0, u32 unk_u32_1, MtString Message (14 + var).
// packet-id: 3.2.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_LOBBY_LOBBY_CHAT_MSG_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 Type;
    u32 TargetID;
    // T014b V (role); I (name; lead agrees): 0xb291b0(text, kind, a, b) sends kind/a/b as
    // unk_u8/unk_u32_0/unk_u32_1: typed chat passes 0,0,0 (0xdd5e50, 0xb76030); the preset-phrase
    // path 0xb29160 passes kind 1 with text '%d'; 0x588b80 passes kind 3. A message-kind selector
    u8 MessageFlavor;                  // Season 3; server: MessageFlavor (lead)
    // T014b V (role); I (name; lead agrees): preset path 0xb29160 sends category+1 (from 0xb76030
    // case 4, after the phrase lookup 0xb79b80(category, index)); 0 for typed chat
    u32 PhrasesCategory;              // Season 3; server: PhrasesCategory (lead)
    // T014b V (role); I (name; lead agrees): preset path 0xb29160 sends the index returned by
    // 0xb79b80(category, index); 0 for typed chat; captured 0-150
    u32 PhrasesIndex;              // Season 3; server: PhrasesIndex (lead)
    MtString Message;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_LOBBY_LOBBY_CHAT_MSG_REQ packet @ 0x00;
