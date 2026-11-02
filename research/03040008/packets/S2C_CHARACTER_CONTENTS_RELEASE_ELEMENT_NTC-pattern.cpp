// 2.6.16 S2C_CHARACTER_CONTENTS_RELEASE_ELEMENT_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 4.
// Code name: CONTENTS_RELEASE_ELEMENT_NTC (V by behaviour).
// PC handler 0x7c7400: list 0x75d050 of {u32}, no error header; each value v < 0x5e sets bit v of
// the bitset at sQuestManagerExt + 0x34 (V). PS4 OnPacket_S2C_CHARACTER_CONTENTS_RELEASE_ELEMENT_NOTICE
// 0x2ea0c0: u16 error, list {u32 m_unReleaseElementNo}, sets mReleaseContents.mBit for v <= 0x3a (V).
// The PS4 u16 framing fails 41/41. Walk: 41/41 fit, slack 7-15, up to 59 elements.
// Body: list CDataCharacterReleaseElement (4 + 4n bytes).
// packet-id: 2.6.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_CHARACTER_CONTENTS_RELEASE_ELEMENT_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataCharacterReleaseElement> ReleaseElementList;   // PC 0x75d050
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_CONTENTS_RELEASE_ELEMENT_NTC packet @ 0x00;
