// 10.13.16 S2C_SWITCH_STORAGE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.9.
// PC handler 0x7ddcc0, reader 0x80cb10: s32, bool, list 0x75c570 {u8, u16}, no error header (V);
// on s32 == 0 it passes the bool and the list to sItemManager 0xb9f560. PS4
// OnPacket_S2C_SWITCH_STORAGE_NTC 0x3374a0 (unique shape): s32 m_nResult, b8 m_bIsStart,
// m_ChangeList {u8, u8}, and on result 0 sItemManager::setSwitchStorage (V by behaviour). Season 3
// widens the element's second field to u16 (V width; the PS4 u8 element fits 2/2 inside the slack,
// so the width is code-only; the PS4 framing fails 2/2). Walk: 2/2 fit, slack 11.
// Body: s32 Result, bool IsStart, list CDataSwitchStorage (9 + 3n bytes).
// packet-id: 10.13.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct S2C_SWITCH_STORAGE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Result;
    bool IsStart;
    MtTypedArray<CDataSwitchStorage> ChangeList;           // PC 0x75c570
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SWITCH_STORAGE_NTC packet @ 0x00;
