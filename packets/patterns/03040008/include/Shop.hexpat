// Shop CData structures of client 03040008 (PC, Season 3) shared by the group 20 SHOP patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T012-achievement-equip-skill.md sections 1, 6 and 19. "PC 0x..." is the reader VA in the PC
// 03040008 database (image base 0x400000). The Season 3 goods element differs from the PS4 02020005
// CDataGoodsParam {u32 x6} (the PS4 body fails 18/18); no field consumer is traced, so the names are
// I (basis stated) or `unk_*`. Server C# (Arrowgene) names are leads only ("server: <name> (lead)").
// Includes Packet.hexpat only. User: 20.0.2.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataGoodsRequirement (struct name I): PC list reader 0x778770, element 0x7788a0 {u32, u32, bool,
// u32, bool, u32 x5, s64, s64} (V widths and order). No PS4 counterpart.
// Server: CDataGoodsParamRequirement (lead).
struct CDataGoodsRequirement {
    // T014b open (no reader found), kept unk: the requirement readers 0xfcc020, 0xf502f0 and
    // 0xf50470 read +8..+56 but not +4; the goods copy 0xfc7960 copies the list whole
    u32 unk_u32_0;
    // T014b V (consumer); I (name; lead agrees): shop requirement text builder 0xf50470 switches on
    // element +8 (cases 2, 3/6, 4, 5) to pick the message and the parameters it formats
    u32 Condition;
    // T014b V (consumer); I (name): 0xfcc020 treats a requirement as met when +12 != 0 (all met ->
    // goods shown); 0xf50470 draws the requirement text greyed (alpha from xmmword_1AE7068) when
    // +12 == 0 (...)
    bool IsCleared;
    // T014b V (consumer); I (name; lead agrees): 0xf50470: case 2 formats +16 with message 0x16
    // when nonzero; cases 3/6 pass +16 beside the target count +24 (current/needed); case 4 formats
    // +16 as a number
    u32 Progress;
    // T014b V (consumer); I (name): 0xf502f0 shows a requirement line only when +20 != 0 (up to 5
    // lines). Server lead HideRequirementDetails has the opposite polarity (contradicted)
    bool IsDisplayed;
    // T014b V (consumer); I (name): 0xf50470: +24 is the count in cases 2 and 3/6 (formatted twice
    // beside Progress) and the second number in case 4
    u32 Param1;
    // T014b V (consumer); I (role): 0xf50470: cases 2, 3 and 4 resolve +28 with sQuestManagerExt
    // 0xbdbaf0, which accepts one of 15 fixed ids (0xa38e20: 1001, 1002, 3002, 3003, 3004, ...) and
    // returns its message; case 6 formats +28 raw
    u32 Param2;
    // T014b V (consumer); I (role): 0xf50470: cases 3/6 resolve +32 with 0xb783f0 (id looked up in
    // the table 0xb55480, then rGUIMessage::getMessage) and format the name
    u32 Param3;
    // T014b open (no reader found), kept unk: 0xf50470 and the other requirement readers do not
    // read +36
    u32 unk_u32_6;
    // T014b open (no reader found), kept unk: 0xf50470 and the other requirement readers do not
    // read +40
    u32 unk_u32_7;
    // T014b V (consumer); I (name; lead agrees): 0xf50470 compares now with +48: before it prints
    // message 0x11 and the time left until +48; case 2 picks message 0x14/0x15 by now < +48
    s64 PeriodStart;
    // T014b V (consumer); I (name; lead agrees): 0xf50470: between +48 and +56 message 0x12 with
    // the time left until +56, after +56 message 0x13; both only when both values > 0
    s64 PeriodEnd;
};

// CDataGoodsParam (Season 3): PC list reader 0x769330 (loc), element 0x769450 {u32, u32, u32, u8
// (1-byte read 0x8bc3e0), bool, s64, s64, list 0x778770} (V widths and order). PS4 CDataGoodsParam
// 0x1a085c0 {u32 x6} does not fit (T012 6).
struct CDataGoodsParam {
    u32 Index;                                     // I: every 20.1.1 GoodsIndex is one of these (17/17); 0, 1, 2, ..., bit 15 set on some
    // T014b V (consumer); I (name; lead agrees): goods array kept at sItemManager +108 (data +124)
    // by 0xb9f0f0 (getter 0x86c800 of conn+972) (...)
    u32 ItemId;                                   // 18828-18832 in captures (item-id range)
    u32 Price;                                     // I: unit price; this Price x 20.1.1 Num = 20.1.1 Price (17/17)
    // T014b V (consumer); I (name; lead agrees): element +16 read as signed char: 0xfcd5a0 passes
    // it (0 when <= 0, so 255 = -1 = unlimited) with Price +12 and Index +4 to the buy dialog
    // 0xfd05a0 (stored +3164); 0xf52d20 prints it with message 0xE '%s%d' and greys it when <= 0
    // (...)
    u8 Stock;                                     // 255 or small counts (1-99); 1-byte read 0x8bc3e0
    // T014b V (consumer); I (name; lead agrees): 0xfccd30 lists the element only when +17 == 0 or
    // 0xfcc020(element) != 0; 0xfcc020 returns 0 for sales state 1/4 (0x5fa060) and otherwise 1
    // only when every requirement element has +12 != 0
    bool HideIfReqsUnmet;
    // T014b V (consumer); I (name; lead agrees): 0x5fa060 compares element +24 with the current
    // time (sGame +2856): now < +24 -> state 1 (not yet on sale); 0xf51ac0 prints +24 as a date
    // with message 0x1B in state 1
    s64 SalesPeriodStart;                                 // always 0 in captures; server: SalesPeriodStart (lead)
    // T014b V (consumer); I (name; lead agrees): 0x5fa060: +32 <= 0 -> state 2 (no end); now > +32
    // -> state 4 (ended, hidden by 0xfcc020); else 3; 0xf51ac0 prints +32 as a date with message
    // 0x10 in state 3
    s64 SalesPeriodEnd;                                 // always 0 in captures; server: SalesPeriodEnd (lead)
    MtTypedArray<CDataGoodsRequirement> unk_RequirementList;   // 0 or 1 entries in captures
};
