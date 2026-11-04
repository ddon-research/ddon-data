// 15.0.16 C2S_EVENT_START_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 12.
// PC writer 0x828920 (15, 0, 16): empty (V). PS4 Send_C2S_EVENT_START_NTC 0x19c5da0: empty.
// Identity V by call graph: the one PC caller, wrapper 0x85d620 (connection state 4,
// isLoginSuccessPrivate), is called once each from 0x412d00 and 0x413900, as PS4
// cNetGameServer::eventStartNotice 0x35fb40 (CONN_CONNECTED, mIsLoginSuccess) is called once each
// from aStage::move_event and aStage::move_event_fsm. Client-written notice: no RES header.
// Walk: 8/8 fit (empty).
// Body: none.
// packet-id: 15.0.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_EVENT_START_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_EVENT_START_NTC packet @ 0x00;
