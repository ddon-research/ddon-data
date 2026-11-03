// 61.2.2 S2C_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 61.2.2.
// PC handler 0x7ed380 cSeedGameSvConnection::OnPacket_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_RES (V
// name), reader 0x8138e0: RES header, u32, list 0x772d70 {u32, u32, u32} (V widths). On Result == 0 the
// handler rebuilds a list at (sArea[3597] +600) +1912 from the elements (V; consumers not traced). PS4
// counterpart: none found (008 T001).
// Walk: 20/20 fit, slack 3; 3 elements each.
// Body: s32 Error [, s32 Result, u32, list {u32 x3}].
// packet-id: 61.2.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list 0x772d70 {u32, u32, u32} (V widths). No PS4 type. Struct name: server (lead).
struct CDataPawnTrainingPreparationInfoToAdvice {
    // T003 G (lead; value consistent: 3 distinct; 60/60 equal a PawnId of the 8.2.2 pawn list (CDataPawnList.PawnId, Pawn.hexpat)
    // in the same stream; lead agrees)
    u32 PawnId;
    // T003 G (lead; value consistent: 2 distinct; 60/60 equal CDataPawnList.unk_u32_2 of the same pawn in 8.2.2; values 3, 0);
    // name open, kept unk; server: Unk0 "CDataPawnList.Unk2" (lead agrees)
    u32 unk_u32_1;
    u32 unk_u32_2;   // T003 open, kept unk: values 0, 1, 6; server: Unk1 (lead)
};

struct S2C_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 open, kept unk: 6 in 20/20; server: Unk0 (lead)
        u32 unk_u32;
        // T003 G (lead): server PawnTrainingPreparationInfoToAdvices
        MtTypedArray<CDataPawnTrainingPreparationInfoToAdvice> PreparationInfoList;   // PC 0x772d70 (V)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_RES packet @ 0x00;
