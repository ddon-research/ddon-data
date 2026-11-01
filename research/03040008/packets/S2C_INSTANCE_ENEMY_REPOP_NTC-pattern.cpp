// 13.40.16 S2C_INSTANCE_ENEMY_REPOP_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 17 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7dad20, reader 0x80ada0: LayoutId, u8, 0x77a1b0 (enemy info, 6 bools), u32, no
// error header (V). PS4 CPacket_S2C_ENEMY_REPOP_NOTICE::ReadPacket 0x19d7950 {m_LayoutId,
// CLayoutEnemyData m_EnemyData (5 bools), u32 m_unWaitSecond} (V). Season 3: the sixth
// enemy-info bool. Walk: 41/41 fit, slack 10; the 5-bool layout fits too (slack 11): the sixth
// bool rests on the PC reader and 13.0.2.
// Body: LayoutId, CDataLayoutEnemyData EnemyData, u32 WaitSecond (45 bytes).
// packet-id: 13.40.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_ENEMY_REPOP_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    CDataLayoutEnemyData EnemyData;
    u32 WaitSecond;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_ENEMY_REPOP_NTC packet @ 0x00;
