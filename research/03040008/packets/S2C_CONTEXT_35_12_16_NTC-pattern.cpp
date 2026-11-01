// 35.12.16 S2C_CONTEXT_35_12_16_NTC (client 03040008).
// Body: CDataContextSetBase, then CDataContextEnemyStatus, the 200-byte structure PC 0x760480 reads
// (Context.hexpat). P4 2.3, P5 7, T001c 1 (handler 0x7d0060, reader 0x8054d0; name unresolved, no
// PC string). An enemy status snapshot keyed by SetBase.m_unUniqueID: 0x843990 caches it, 0x850b30
// applies it when that enemy initializes (V for the data flow; "snapshot for an enemy spawned
// later" is I). Body size 28 + 159 + 2 x (OcdActive n + OcdImmuneLv n). No capture: checked on a
// synthetic file built from T001c's field table only.
// packet-id: 35.12.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_35_12_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataContextSetBase m_Base;
    CDataContextEnemyStatus m_EnemyStatus;      // name I (T001c 1)
    bool decoded = true [[export]];
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONTEXT_35_12_16_NTC packet @ 0x00;
