// Shared framing of the packets/decrypted_raw files of client 03040008 (PC, Season 3), for the
// packet patterns that carry no nNetMsg.
//
// Framing (P4 1, = P2): u8 group, u16 id, u8 sub, u8 source (0x00 client, 0x34 server), u32
// counter, then the body from file offset 0x09. The raw files store no body length and are padded
// to a multiple of 16 bytes with non-zero bytes (cipher block padding).
//
// Fit flag: a decode "fits" when it ends within the last 15 bytes of the file
// (std::mem::size() - $ <= 15); reading past the end fails the decode. This is weaker than the
// nNetMsg `len` check: a width error smaller than the padding can still fit (P4 0.5).
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
// 0x8015b0, 0x801530).
struct ResHeader {
    s32 Error;
    if (Error == 0) s32 Result;
};

// u16 BE length (<= 0x800) + bytes (nPacket::Read_MtString, P4 header).
struct MtString {
    u16 length;
    char value[length];
};
