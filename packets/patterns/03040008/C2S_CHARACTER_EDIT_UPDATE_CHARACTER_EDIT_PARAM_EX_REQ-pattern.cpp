// 41.5.1 C2S_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 41.5.1.
// PC writer 0x8406b0: WritePacket(0x29, 5, 1), Write_u8, Write_u8 +4, Write_u32 +8,
// nPacket::Write_CDataEditInfo_ 0x77eb40, Write_MtString (V). Name: CLI/server (G (lead)).
// PS4 counterpart: none matched (spec 006 T013 § 9); the shape follows 41.3.1 (writer 0x840840).
// Walk: 1/1 fit, slack 5.
// Body: u8, CDataWalletPoint, CDataEditInfo (122 bytes), MtString.
// packet-id: 41.5.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Context.hexpat"

struct C2S_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 UpdateType;      // T005 G (lead): server UpdateType; 3 in 1/1
    // T005 I (same structure: inline {Write_u8 +4, Write_u32 +8} = CDataWalletPoint, as 41.3.1's 0x7812a0;
    // value, 1 distinct: (5, 20) = the UpdateType 2 price of the preceding 41.8.2, 1/1); server: EditPrice (lead agrees)
    CDataWalletPoint EditPrice;
    CDataEditInfo EditInfo;     // T005 V (same writer 0x77eb40 as 41.3.1: Context.hexpat CDataEditInfo)
    MtString FirstName;         // T005 G (lead): server FirstName; empty in 1/1
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_REQ packet @ 0x00;
