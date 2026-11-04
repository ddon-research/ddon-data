// 5.5.16 L2C_LOGIN_WAIT_NUM_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 13.
// PC: no separate reader; handler 0x887670 (key 0x100005) calls Read_u32 directly and stores it
// to [mgr+0x1294] with the current time (V). PS4 OnPacket_L2C_LOGIN_WAIT_NUM_NTC 0x37d930 makes
// the same two stores (mLoginWaitNum, mCreateCharacterUpdateTime) (V by behaviour); PS4 reads a
// u16 Error first, PC does not (Season 3 difference, V).
// Walk: 9/9 fit, slack 3.
// Body: u32 WaitNum.
// packet-id: 5.5.16
// packet-select: L2C_LOGIN_WAIT_NUM_NTC
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct L2C_LOGIN_WAIT_NUM_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 WaitNum;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

L2C_LOGIN_WAIT_NUM_NTC packet @ 0x00;
