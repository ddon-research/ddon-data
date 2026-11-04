// 18.0.2 S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 18. PC handler 0x7d8d40
// (string 0x1bd08e0; 18, 0, 2), reader 0x809d80: s32 Error; if non-zero it copies Error to Result
// and stops; else s32 Result and the list 0x75cbd0 of CDataCharacterListElement 0x75ccf0 (V). PS4
// OnPacket_S2C_GROUP_CHAT_GET_MEMBER_LIST_RES 0x2fb0d0: u16, s32, Read_CDataCharacterListElement;
// the PS4 element ends at the MtString (V PS4). The PS4 recompilation has no class for the packet.
// All 41 captures are Error 0xb79b (PS4 nError GROUP_CHAT_NOT_IN_GROUP); no member element has a
// capture.
// Body: s32 Error [, s32 Result, list CDataCharacterListElement] (P11a G1).
// packet-id: 18.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCharacterListElement> GroupMemberList;   // PC 0x75cbd0
    } else if (std::mem::size() - $ > 15) {
        // The client stops after a non-zero Error (PC 0x809d80), but the server writes Result and
        // an empty list after it (P11b G2b, PC-cap 41/41: slack 19). More than 15 bytes left
        // cannot be cipher padding, so they are decoded as that server tail; the client never
        // reads them. PS4 framing (I): the recompiled ACTIVATE_JOB_ORDER_RES::ReadPacket (S2C.cpp
        // 188-206) reads Result after any Error and accepts a short packet.
        // T014b open (never read by the client), kept unk: the field exists only after a non-zero
        // Error; the reader 0x809d80 stops after a non-zero Error (copies Error to Result) and the
        // handler 0x7d8d40 uses only Error/Result and the member list (0x84cef0 to conn +41640)
        // (...)
        s32 unk_serverResult;
        // T014b open (never read by the client), kept unk: as unk_serverResult: after a non-zero
        // Error the reader 0x809d80 reads nothing more
        u32 unk_serverListCount;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES packet @ 0x00;
