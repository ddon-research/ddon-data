// 13.39.16 S2C_INSTANCE_POP_DROP_ITEM_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 16 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7dbe30, reader 0x80b8c0: LayoutId, u32, u8, f64, f32, f64, no error header (V).
// PS4 CPacket_S2C_POP_DROP_ITEM_NOTICE::ReadPacket 0x19d7870 {m_LayoutId, u32 m_unId, u8
// m_ucMdlType, f64 m_dPosX, f32 m_fPosY, f64 m_dPosZ} (V). Season 3: none. Walk: 74/74 fit,
// slack 5.
// Body: LayoutId, u32 Id, u8 MdlType, double PosX, float PosY, double PosZ (34 bytes).
// packet-id: 13.39.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_POP_DROP_ITEM_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    u32 Id;
    u8 MdlType;
    double PosX;
    float PosY;
    double PosZ;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_POP_DROP_ITEM_NTC packet @ 0x00;
