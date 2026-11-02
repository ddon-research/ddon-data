// 26.14.1 C2S_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 16.
// PC writer 0x835b00 (26, 14, 1): list via 0x77e0b0 = count + {u32, u32, u8, u8, u32}
// (CDataCommunicationShortCut) (V). PS4 0x1a39f70 writes m_ShortcutList: same (V). The
// recompilation writer is a DDON_STUB.
// Walk: 41/41 fit, slack 3; the list always holds 40.
// Body: list CDataCommunicationShortCut.
// packet-id: 26.14.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct C2S_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataCommunicationShortCut> ShortcutList;  // PC writer 0x77e0b0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_REQ packet @ 0x00;
