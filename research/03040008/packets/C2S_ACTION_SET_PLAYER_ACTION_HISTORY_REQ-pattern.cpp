// 70.0.1 C2S_ACTION_SET_PLAYER_ACTION_HISTORY_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 70.0.1.
// PC sender 0x81e150 cSeedGameSvConnection::Send_C2S_ACTION_SET_PLAYER_ACTION_HISTORY_REQ (V name):
// WritePacket(0x46, 0, 1), then list writer 0x77d1e0 only: u32 count, count x {Write_u8 [e+4], Write_u32
// [e+8]} (V, 008 T002 § 1-2).
// PS4 counterpart: none (no ACTION_SET_PLAYER_ACTION_HISTORY symbol or type; 008 T001).
// Walk: 312/312 fit, slack 4-15, 1-6 elements.
// Body: u32 count + count x {u8, u32}.
// packet-id: 70.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list writer 0x77d1e0 {u8 [e+4], u32 [e+8]} (V widths, 008 T002). No PS4 type.
// server: CDataC2SActionSetPlayerActionHistoryReqElement {Unk0, Unk1} (lead). Struct name G (context).
struct CDataPlayerActionHistoryElement {
    // T003 G (context): 13 distinct values in 764 elements (5 x243, 1 x113, 8 x105, 2 x91, 7 x76,
    // 9 x61, ...): a small enum, read as the kind of action; server: Unk0 (lead)
    u8 ActionType;
    // T003 G (context): values 1 x361, 2 x161, 3 x94, ... up to 20 distinct small counts: read as
    // how often the action happened; server: Unk1 (lead)
    u32 Num;
};

struct C2S_ACTION_SET_PLAYER_ACTION_HISTORY_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T003 G (context): packet name "player action history"; server: Unk0 (lead)
    MtTypedArray<CDataPlayerActionHistoryElement> ActionHistoryList;   // PC 0x77d1e0 (V)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ACTION_SET_PLAYER_ACTION_HISTORY_REQ packet @ 0x00;
