// 59.0.2 S2C_INFINITY_DELIVERY_GET_CURRENT_EVENT_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 59.0.2.
// PC handler 0x7d9d00 cSeedGameSvConnection::OnPacket_INFINITY_DELIVERY_GET_CURRENT_EVENT_RES (V name),
// reader 0x80a470: RES header, list 0x769ed0 of 0x769fe0 (V). No server structure (lead: PacketId only). PS4 counterpart: none (Season 3 group).
// Walk: 2/2 fit, slack 0-11; EventList empty (2019-07-11) or 1 event (2019-11-18).
// Body: s32 Error [, s32 Result, list CDataInfinityDeliveryEvent].
// packet-id: 59.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "InfinityDelivery.hexpat"

struct S2C_INFINITY_DELIVERY_GET_CURRENT_EVENT_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataInfinityDeliveryEvent> EventList;    // PC 0x769ed0; T004 G (context)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INFINITY_DELIVERY_GET_CURRENT_EVENT_RES packet @ 0x00;
