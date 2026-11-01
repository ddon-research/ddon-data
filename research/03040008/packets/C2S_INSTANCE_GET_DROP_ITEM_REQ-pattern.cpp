// 13.11.1 C2S_INSTANCE_GET_DROP_ITEM_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 9 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x841560 (13, 11, 1): LayoutId, u32, Write_bool, list 0x77f9d0 {u32, u32} (V). PS4
// CPacket_C2S_GET_DROP_ITEM_REQ::WritePacket 0x1a36660 {m_LayoutId, u32 m_unId,
// MtTypedArray<CDataGatheringItemGetRequest>} (V). Season 3: the bool after Id (V width, name
// unknown). Walk: 44/44 fit, slack 5-13; the PS4 layout fits 0/44.
// Body: LayoutId, u32 Id, bool unk_bool, MtTypedArray<CDataGatheringItemGetRequest>
// GatheringItemGetRequestList (18 + 8n bytes).
// packet-id: 13.11.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_INSTANCE_GET_DROP_ITEM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    u32 Id;
    bool unk_bool;   // Season 3, no PS4 member (PC Write_bool, V width); server: Unk0 (lead)
    MtTypedArray<CDataGatheringItemGetRequest> GatheringItemGetRequestList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_GET_DROP_ITEM_REQ packet @ 0x00;
