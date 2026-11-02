// 41.3.1 C2S_CHARACTER_EDIT_UPDATE_PAWN_EDIT_PARAM_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 9 (1 and 16 for the types).
// PC writer 0x840840 (41, 3, 1): u8, u8, writer 0x7812a0 {u8, u32}, Write_CDataEditInfo_ 0x77eb40 (V).
// PS4 CPacket_C2S_UPDATE_PAWN_EDIT_PARAM_REQ::WritePacket 0x1a3a200 {u8 in_SlotNo, u8 in_UpdateType,
// CEditInfo}: match V; Season 3 inserts {u8, u32}. The PS4 body fits 1/1 too (slack): the PC writer
// decides. Walk: 1/1 fit; SlotNo 1, UpdateType 1, price (4, 200).
// Body: u8 SlotNo, u8 UpdateType, CDataWalletPoint unk_Price, CDataEditInfo EditInfo (129 bytes).
// packet-id: 41.3.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Context.hexpat"

struct C2S_CHARACTER_EDIT_UPDATE_PAWN_EDIT_PARAM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 SlotNo;
    u8 UpdateType;
    CDataWalletPoint unk_Price;   // Season 3, PC 0x7812a0 {u8, u32}; I: (4, 200) = the 41.8.2 price entry of UpdateType 1 sent earlier; server: EditPrice (lead)
    CDataEditInfo EditInfo;       // PC 0x77eb40, 122 bytes
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_EDIT_UPDATE_PAWN_EDIT_PARAM_REQ packet @ 0x00;
