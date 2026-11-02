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
    u32 unk_u32_0;
    u32 unk_u32_1;
    bool unk_bool_0;
    u32 unk_u32_2;
    bool unk_bool_1;
    u32 unk_u32_3;
    u32 unk_u32_4;
    u32 unk_u32_5;
    u32 unk_u32_6;
    u32 unk_u32_7;
    s64 unk_s64_0;
    s64 unk_s64_1;
};

// CDataGoodsParam (Season 3): PC list reader 0x769330 (loc), element 0x769450 {u32, u32, u32, u8
// (1-byte read 0x8bc3e0), bool, s64, s64, list 0x778770} (V widths and order). PS4 CDataGoodsParam
// 0x1a085c0 {u32 x6} does not fit (T012 6).
struct CDataGoodsParam {
    u32 Index;                                     // I: every 20.1.1 GoodsIndex is one of these (17/17); 0, 1, 2, ..., bit 15 set on some
    u32 unk_u32;                                   // 18828-18832 in captures (item-id range)
    u32 Price;                                     // I: unit price; this Price x 20.1.1 Num = 20.1.1 Price (17/17)
    u8 unk_u8;                                     // 255 or small counts (1-99); 1-byte read 0x8bc3e0
    bool unk_bool;
    s64 unk_s64_0;                                 // always 0 in captures; server: SalesPeriodStart (lead)
    s64 unk_s64_1;                                 // always 0 in captures; server: SalesPeriodEnd (lead)
    MtTypedArray<CDataGoodsRequirement> unk_RequirementList;   // 0 or 1 entries in captures
};
