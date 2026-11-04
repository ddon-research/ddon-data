// 3.0.16 L2C_GET_ERROR_MESSAGE_LIST_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 9.
// PC reader 0x889ac0 via handler 0x887070 (key 0x100000): list 0x887990 (u32 count, per
// element u32, u32, MtString, MtString), then Read_u32 (V); no error header. PS4
// OnPacket_L2C_GET_ERROR_MESSAGE_LIST_NTC 0x37d2e0 reads u16 Error and the list, nothing after;
// DWARF {u16 m_usError, MtTypedArray<CDataErrorMessage> m_ErrorMessage}. Season 3 (V): no error
// header, and the trailing u32 is new. Its value runs 950, 850, ..., 50 over a stream's NTCs:
// the messages remaining from this chunk on (V walk); the name RemainingNum is I. The server
// lead omits it (T002 section 16).
// Walk: 410/410 fit, slack 2-13.
// Body: MtTypedArray<CDataErrorMessage> ErrorMessage, u32 RemainingNum (I).
// packet-id: 3.0.16
// packet-select: L2C_GET_ERROR_MESSAGE_LIST_NTC
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Login.hexpat"

struct L2C_GET_ERROR_MESSAGE_LIST_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataErrorMessage> ErrorMessage;
    u32 RemainingNum;           // Season 3, name I
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

L2C_GET_ERROR_MESSAGE_LIST_NTC packet @ 0x00;
