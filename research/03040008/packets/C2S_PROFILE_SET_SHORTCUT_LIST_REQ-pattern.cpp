// 26.12.1 C2S_PROFILE_SET_SHORTCUT_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 15.
// PC writer 0x835fa0 (26, 12, 1): list via 0x780f20 = count + {u32 x5, u8} (CDataShortCut) (V). PS4
// CPacket_C2S_SET_SHORTCUT_LIST_REQ::WritePacket 0x1a3a0b0 writes m_ShortcutList: same (V). The
// recompilation writer is a DDON_STUB.
// Walk: 42/42 fit, slack 7; the list always holds 12.
// Body: list CDataShortCut.
// packet-id: 26.12.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct C2S_PROFILE_SET_SHORTCUT_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataShortCut> ShortcutList;  // PC writer 0x780f20
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PROFILE_SET_SHORTCUT_LIST_REQ packet @ 0x00;
