// 16.0.2 S2C_FRIEND_GET_FRIEND_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 10 (1, 18 for the types).
// PC handler 0x7d6750, reader 0x808900: header, list 0x766e20 (CDataFriendInfo), list 0x75ebc0, list
// 0x75ebc0 (CDataCommunityCharacterBaseInfo) (V). PS4 CPacket_S2C_GET_FRIEND_LIST_RES::ReadPacket
// 0x19d9a60 {m_FriendInfoList, m_ApplyingCharacterList, m_ApprovingCharacterList}: same except the
// Season 3 trailing u8 of the list element (V; the PS4 CDataFriendInfo fails 20/41).
// Walk: 41/41 fit, slack 3-15; friend lists 0, 1 or 7 entries; both community lists always empty (code-only).
// Body: s32 Error [, s32 Result, list CDataFriendInfo, 2 x list CDataCommunityCharacterBaseInfo].
// packet-id: 16.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_FRIEND_GET_FRIEND_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataFriendInfo> FriendInfoList;  // PC 0x766e20
        MtTypedArray<CDataCommunityCharacterBaseInfo> ApplyingCharacterList;   // PC 0x75ebc0
        MtTypedArray<CDataCommunityCharacterBaseInfo> ApprovingCharacterList;  // PC 0x75ebc0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_FRIEND_GET_FRIEND_LIST_RES packet @ 0x00;
