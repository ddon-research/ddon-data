// 15.1.16 C2S_EVENT_END_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 12.
// PC writer 0x828860 (15, 1, 16): empty (V). PS4 Send_C2S_EVENT_END_NTC 0x19c5ed0: empty.
// Identity V by call graph: PC wrapper 0x85d5e0 is called 3x from 0x412d00, 3x from 0x413900 and
// 1x from 0x40c620; PS4 eventEndNotice 0x35fb80 3x from aStage::move_event, 3x from
// move_event_fsm and 1x from aStage::finishEvent (same guard, same 3+3+1 pattern).
// Walk: 8/8 fit (empty).
// Body: none.
// packet-id: 15.1.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_EVENT_END_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_EVENT_END_NTC packet @ 0x00;
