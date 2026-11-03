// 12.5.1 C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 12.5.1.
// PC writer 0x842930: WritePacket(0x0c, 5, 1), Write_u32, list writer 0x77fd30 {Write_MtString +4,
// Write_u32 +8}, Write_u32, Write_cstr (V; 008 T002). Write_cstr's wire form is a u16 length plus the
// bytes, no terminator (I: 008 T001, from the captures), i.e. an MtString on the wire.
// PS4 counterpart: none matched (spec 006 T006 § 3).
// Walk: 3/3 fit, slack 15 (the limit); EntryFeeList empty in 3/3.
// Body: u32, list CDataItemUIDList, u32, cstr.
// packet-id: 12.5.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

struct C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T005 I (value: the following 12.9.16 carries it back as ContentId, 3/3; 19); server: ContentId (lead agrees)
    u32 ContentId;
    // T005 I (same structure: writer 0x77fd30 = Quest.hexpat CDataItemUIDList); list name G (lead: server
    // EntryFeeList); empty in 3/3
    MtTypedArray<CDataItemUIDList> EntryFeeList;
    u32 EntranceId;     // T005 G (lead): server EntranceId; 1111 in 3/3
    // T005 I (value: "第4区画 メガドシスの記憶 山道" 3/3 = a 62.1.2 SectionName); server: Unk2String (lead)
    MtString SectionName;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ packet @ 0x00;
