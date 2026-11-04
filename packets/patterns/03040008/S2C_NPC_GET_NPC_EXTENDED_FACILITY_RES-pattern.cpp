// 60.0.2 S2C_NPC_GET_NPC_EXTENDED_FACILITY_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 60.0.2.
// PC handler 0x7e62d0 cSeedGameSvConnection::OnPacket_NPC_GET_NPC_EXTENDED_FACILITY_RES (V name), reader
// 0x80ff90: RES header, then 0x76f940 {u32, 0x76f980 list of 0x76fa80 {u32 x6, u8, MtString, u8}} (V widths
// and order). PS4 counterpart: none (60.0.1 pattern, P11b § 12).
// Walk: 219/219 fit, slack 7 or 11; the list holds 1 element in 4 files, else 0.
// Body: s32 Error [, s32 Result, u32, list].
// packet-id: 60.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list 0x76f980, reader 0x76fa80 {u32 x6, u8, MtString, u8} (V widths). No PS4 type.
// Names: server CDataNpcExtendedFacilityMenuItem (lead); the only captured element (4 files) is
// {69, 67, 4452, 0, 0, 0, 0, "", 0}.
struct CDataNpcExtendedFacilityMenuItem {
    u32 FunctionClass;      // T003 G (lead): server FunctionClass (NpcFunction); captured 69
    u32 FunctionSelect;     // T003 G (lead): server FunctionSelect (NpcFunction, FUNC_SELECT_NAME_); captured 67
    // T003 open, kept unk: captured 4452; server: WorldManageQuestFlag (lead, "used in epitaph road")
    u32 unk_u32_2;
    u32 unk_u32_3;          // T003 open, kept unk: captured 0; server: Unk3 (lead)
    // T003 G (lead): server ShopId ("shows up as ShopId in S2CShopGetGoodsListRes"); captured 0
    u32 ShopId;
    u32 unk_u32_5;          // T003 open, kept unk: captured 0; server: Unk5 (lead)
    bool unk_bool;          // T003 open, kept unk: captured 0; server: Unk6 (lead)
    MtString CustomLabel;   // T003 G (lead): server CustomLabel; captured empty
    u8 unk_u8;              // T003 open, kept unk: captured 0; server: Unk7 (lead)
};

struct S2C_NPC_GET_NPC_EXTENDED_FACILITY_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 G (lead; value consistent: 3 distinct; 7/7 nonzero values equal the NpcID of the preceding 60.0.1 request in the same
        // stream; 212/219 are 0); server: NpcId (lead agrees)
        u32 NpcId;
        // T003 G (lead): server: ExtendedMenuItemList
        MtTypedArray<CDataNpcExtendedFacilityMenuItem> ExtendedMenuItemList;   // PC 0x76f980 (V)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_NPC_GET_NPC_EXTENDED_FACILITY_RES packet @ 0x00;
