// 1.0.1 C2L_CLIENT_CHALLENGE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 3.
// PC writer 0x88a900: WritePacket(p, 1, 0, 1, -1), Write_u8, loop Write_u8 x 0x103 (0x77cfa0),
// Write_u8, Write_u8, loop Write_u8 x 0x3e (0x77cfe0) (V, disassembly pushes). PS4
// nLoginSession::CPacket_C2L_CLIENT_CHALLENGE_REQ::WritePacket 0x1a409b0 (u8 in_CommonKeySrcSize,
// const u8 (*in_CommonKeyEnc)[259], u8 in_PasswordSrcSize, u8 in_PasswordEncSize,
// const u8 (*in_PasswordEnc)[62]): the same five fields and array lengths (V by body).
// Server lead misplacements: CommonKeyEnc is 259 bytes, not 256 + 3 padding; PasswordEnc is a
// fixed 62 bytes, not zero-terminated (T002 section 16).
// RAWS NOT DECRYPTED, UNVALIDATED: all 84 raws of 1.0.1 C2L_CLIENT_CHALLENGE_REQ are still
// ciphertext (they fail the header check; the packet precedes the session key), so this
// pattern was never run on a capture. It deliberately declares no `// packet-id:` line, so
// `packets/imhex-export.sh @ C2L_CLIENT_CHALLENGE_REQ` refuses ("declares no '// packet-id:'
// line") instead of publishing JSON decoded from ciphertext. Restore the line
// `// packet-id: 1.0.1` (with the packet-select below) once the raws are re-decrypted.
// Body: u8 CommonKeySrcSize, u8 CommonKeyEnc[259], u8 PasswordSrcSize, u8 PasswordEncSize,
// u8 PasswordEnc[62] (324 B).
// packet-select: C2L_CLIENT_CHALLENGE_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2L_CLIENT_CHALLENGE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 CommonKeySrcSize;
    u8 CommonKeyEnc[259];
    u8 PasswordSrcSize;
    u8 PasswordEncSize;
    u8 PasswordEnc[62];
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2L_CLIENT_CHALLENGE_REQ packet @ 0x00;
