// 34.0.2 S2C_ENTRY_BOARD_ENTRY_BOARD_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 34.0.2.
// PC handler 0x7d3f10 cSeedGameSvConnection::OnPacket_ENTRY_BOARD_ENTRY_BOARD_LIST_RES (V name), reader
// 0x8075a0: RES header, list 0x7651d0 (element 0x7652c0 {u64, u16 x5, bool, u32}) (V).
// PS4 counterpart: none matched (spec 006 T013 § 5).
// Walk: 1/1 fit, slack 4.
// Body: s32 Error [, s32 Result, list CDataEntryBoardListParam].
// packet-id: 34.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list reader 0x7651d0, reader 0x7652c0 {u64 +8, u16 +16 .. +24, bool +26, u32 +28} (V).
// Struct name: server (lead).
struct CDataEntryBoardListParam {
    u64 BoardId;        // T005 G (lead; value consistent: 1 distinct; 1/1 = the 34.0.1 BoardIdList id); server: BoardId (lead agrees)
    u16 SortieMin;      // T005 G (lead): server SortieMin; 1 in 1/1
    u16 NoPartyMembers; // T005 G (lead): server NoPartyMembers; 4 in 1/1
    u16 unk_u16_0;      // T005 open: 0 in 1/1; server: Unk3 (lead)
    u16 TimeOut;        // T005 G (lead): server TimeOut ("maximum time in seconds"); 3600 in 1/1
    u16 unk_u16_1;      // T005 open: 120 in 1/1; server: Unk5 (lead)
    bool unk_bool;      // T005 open: true in 1/1; server: Unk6 (lead)
    u32 unk_u32;        // T005 open: 0 in 1/1; server: Unk7 (lead)
};

struct S2C_ENTRY_BOARD_ENTRY_BOARD_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataEntryBoardListParam> EntryList;   // PC 0x7651d0; T005 G (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ENTRY_BOARD_ENTRY_BOARD_LIST_RES packet @ 0x00;
