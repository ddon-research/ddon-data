// 14.10.16 C2S_WARP_WARP_START_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 2.7.
// Code name: C2S_WARP_END_NTC (V by call site). The raws and this pattern keep the CLI name
// WARP_START_NTC, which the PS4 name of the same call contradicts (C).
// PC writer 0x840160 (14, 10, 0x10): no body (V); called once, from aStage::move_menu_warp
// 0x415470 (via 0x8865f0 at 0x4155ff), after `mov [manager+0x9df0], 1`. PS4
// cNetGameServer::warpEndNotice -> Send_C2S_WARP_END_NTC 0x19bf340 (no body) is called once, from
// aStage::move_menu_warp, after `mReqAreaChangeJumpType = 1` (same state 100, same message 0x70).
// PS4 has no WARP_START symbol or type. Walk: 62/62 fit, slack 7.
// Body: none (0 bytes).
// packet-id: 14.10.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_WARP_WARP_START_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_WARP_WARP_START_NTC packet @ 0x00;
