// Shared framing of the packets/decrypted_raw files of client 03040008 (PC, Season 3), for the
// packet patterns that carry no nNetMsg.
//
// Framing (P4 1, = P2): u8 group, u16 id, u8 sub, u8 source (0x00 client, 0x34 server), u32
// counter, then the body from file offset 0x09. The raw files store no body length and are padded
// to a multiple of 16 bytes with non-zero bytes (cipher block padding).
//
// Fit flag: a decode "fits" when it ends within the last 15 bytes of the file
// (std::mem::size() - $ <= 15); reading past the end fails the decode. This is weaker than the
// nNetMsg `len` check: a width error smaller than the padding can still fit (P4 0.5). A fit
// therefore does not prove widths whenever the slack exceeds a field: e.g. a 16-byte packet fits
// any body of 0-7 bytes, and a missing trailing u32 still fits when the padding was 15 (R1 F3).
// Patterns export `paddingSize` (the slack) so counts can show it, and `sourceOk`: the header
// source byte matches the direction their name gives (0x00 client C2S, 0x34 server S2C).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

import std.mem;

// Packet header of the decrypted_raw files (9 bytes).
struct CPacket {
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

// RES header (P4 1): s32 Error; only if Error == 0 an s32 Result follows (PC readers 0x805340,
// 0x8015b0, 0x801530). Convention (spec 005 R2 F3): every RES pattern writes it inline,
// `s32 Error; if (Error == 0) { s32 Result; ... }`, so the JSON holds `packet.Error` and
// `packet.Result` for every RES; there is no shared ResHeader struct.

// MtTypedArray<T> on the wire: u32 count + count elements. Every PC list reader starts with
// nPacket::Read_u32 into the count (P11a G5, V).
struct MtTypedArray<T> {
    u32 count;
    T entries[count];
};

// CDataCommonU32: PC list reader 0x75e8e0 (P11a shared table, V); PS4 DWARF CDataCommonU32
// {u32 m_unvalue}. The field keeps the m_unValue spelling the group 35 patterns export.
struct CDataCommonU32 {
    u32 m_unValue;
};

// CDataCommonU8: PC list reader 0x75e9b0 (P11a 2, V); PS4 DWARF CDataCommonU8 {u8 m_ucvalue}.
struct CDataCommonU8 {
    u8 m_ucValue;
};

// u16 BE length (<= 0x800) + bytes (nPacket::Read_MtString 0x8bc5b0, P4 header).
struct MtString {
    u16 length;
    char value[length];
};
