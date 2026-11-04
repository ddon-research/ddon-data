// 1.0.1 C2L_CLIENT_CHALLENGE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 3 (layout; its walk,
// 336 = 9 + 324 + 3 and header statements are superseded, T002 Errata R1),
// T002c-challenge-decrypt.md sections 1-4 (key, no header, 304/336 split; T002c Errata R1).
// PC writer 0x88a900: WritePacket(p, 1, 0, 1, -1), Write_u8, loop Write_u8 x 0x103 (0x77cfa0),
// Write_u8, Write_u8, loop Write_u8 x 0x3e (0x77cfe0) (V, disassembly pushes). PS4
// nLoginSession::CPacket_C2L_CLIENT_CHALLENGE_REQ::WritePacket 0x1a409b0 (u8 in_CommonKeySrcSize,
// const u8 (*in_CommonKeyEnc)[259], u8 in_PasswordSrcSize, u8 in_PasswordEncSize,
// const u8 (*in_PasswordEnc)[62]): the same five fields and array lengths (V by body).
// Server lead misplacements: CommonKeyEnc is 259 bytes, not 256 + 3 padding; PasswordEnc is a
// fixed 62 bytes, not zero-terminated (T002 section 16).
// NO HEADER: this is the client's first packet, encrypted with the fixed client key (T002c 1).
// The CLI writes it without the 9-byte header (Packet.cs GetHeaderBytes() is empty for this id),
// and on the wire the body starts at byte 0 (CommonKeySrcSize = 0x30 in 42/42, T002c 3, 4).
// The pattern therefore reads the body at offset 0 and does not use CPacket or `sourceOk`.
// Raws re-decrypted with the fixed key in T002d (patched CLI, docs/reference/arrowgene-cli-patches.md).
// The server's first packet (its certificate notice, 304 bytes) shared this file name and id until
// T002e, which files it as 1.1.16 L2C_LOGIN_SERVER_CERT_NTC (L2C_LOGIN_SERVER_CERT_NTC-pattern.cpp);
// every `.1_0_1` file of this name is now the client's 336-byte challenge, so no size selector.
// Body: u8 CommonKeySrcSize, u8 CommonKeyEnc[259], u8 PasswordSrcSize, u8 PasswordEncSize,
// u8 PasswordEnc[62] (324 B), then 12 bytes of cipher block padding (336 B).
// packet-id: 1.0.1
// packet-select: C2L_CLIENT_CHALLENGE_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

struct C2L_CLIENT_CHALLENGE_REQ {
    u8 CommonKeySrcSize;      // 48 in 42/42 captures (T002c 1; session key length, I)
    u8 CommonKeyEnc[259];     // RSA-PKCS#1 session key (256 B) + 3 zero bytes in 42/42
    u8 PasswordSrcSize;       // 0x10 in 42/42
    u8 PasswordEncSize;       // 0x10 in 42/42
    u8 PasswordEnc[62];       // Blowfish-ECB of the fixed password, 16 B + zeros (T002c 1)
    // Fit: the decode ends within the last 15 bytes (cipher block padding).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2L_CLIENT_CHALLENGE_REQ packet @ 0x00;
