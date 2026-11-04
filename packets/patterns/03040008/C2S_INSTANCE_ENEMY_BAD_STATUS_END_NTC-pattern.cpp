// 13.47.16 C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC (client 03040008).
// Body: u32, u8, u32, u32, u32, u32. P4 4, P5 7, T001c 3 (PC writer 0x841170 / 0x82b650, sender
// 0x604d80 from 0x96d5a0). Status end: sent from cOcdBase::final (PC 0x8a1c80 = PS4 0x39a690,
// matched by code) for an enemy (mIsEnemy or mIsHumanEnemy) the client is master of, when the uid
// satisfies (uid & 0xF000) == 0x1000 (V). This corrects P5 7 ("player character", C). Widths from
// the pushes at the call site. The client name is unresolved (no PC string, no PS4 sender); the
// raw-file name is the server's.
// packet-id: 13.47.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // CDataStageLayoutId (T001c 3, V): StageId = convertStageNoToId(sGame stageNo) (PC 0xa29c30),
    // LayerNo = obj+0x80, GroupId = obj+0x1C & 0x1FF; obj from 0x4d9e70 (model+6992), I: the
    // enemy's set-group record.
    u32 StageId;
    u8 LayerNo;
    u32 GroupId;
    // T014b open (record not identified), kept unk: same record field as START (+0x30 of
    // 0x4d9e70(enemy)); see C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC.unk_u32
    u32 unk_u32;     // obj+0x30, unresolved (getter 0x4d9e70 is a protected thunk); server: PosId (lead)
    // T014b V (source: constant 0): sender pushes 0 for this field (0x604dea), as START
    u32 unk_zero;    // always 0: client constant (`push 0` at 0x604dea); captures 61/61 zero
    u32 m_unOcdUID;  // PS4 cOcdBase::mOcdUID (T001c 3, V)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC packet @ 0x00;
