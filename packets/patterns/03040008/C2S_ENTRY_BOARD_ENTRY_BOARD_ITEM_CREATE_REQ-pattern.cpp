// 34.2.1 C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 6 (1 and 16 for the types).
// PC writer 0x826ae0 (34, 2, 1): u64, Write_cstr (MtString on the wire), 0x77f260 (CDataEntryItemParam,
// Season 3 recruit) (V). PS4 CPacket_C2S_ENTRY_BOARD_ITEM_CREATE_REQ::WritePacket 0x1a34310
// {u64 m_ullBoardID, MT_CSTR in_strPassword, m_Param}: match V; the PS4 body fails 1/1.
// Walk: 1/1 fit; 4 recruit entries of 11 jobs.
// Body: u64 BoardID, MtString Password, CDataEntryItemParam Param.
// packet-id: 34.2.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "EntryBoard.hexpat"

struct C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u64 BoardID;
    MtString Password;
    CDataEntryItemParam Param;   // PC 0x77f260
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_REQ packet @ 0x00;
