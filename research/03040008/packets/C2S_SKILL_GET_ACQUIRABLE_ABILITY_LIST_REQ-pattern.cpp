// 19.2.1 C2S_SKILL_GET_ACQUIRABLE_ABILITY_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 2.
// PC writer 0x83cc00 (19, 2, 1): Write_u32, Write_u8 (V); the u8 is a job id (caller 0x868350).
// PS4 Send_C2S_GET_ACQUIRABLE_ABILITY_LIST_REQ 0x19bf5c0(u8 in_Job) (V).
// Season 3: + leading u32 (the PS4 body fits too, slack 2 + 4 < 15: the PC writer decides).
// Walk: 16/16 fit, slack 2; first u32 2144504, Job 0/2/3/10.
// Body: u32 unk_u32, u8 Job (5 bytes).
// packet-id: 19.2.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_SKILL_GET_ACQUIRABLE_ABILITY_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 unk_u32;        // Season 3, no PS4 member; 2144504 in 16/16 = the player's CharacterID in the same stream (T011 7, one value; TC1); server: CharacterId (lead)
    u8 Job;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_SKILL_GET_ACQUIRABLE_ABILITY_LIST_REQ packet @ 0x00;
