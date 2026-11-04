// 44.0.1 C2S_CERT_CLIENT_CHALLENGE_REQ (client 03040008), the client's first packet to the game server.
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// sections 1 and 15 (T003 Errata R1: the packet-size advice is superseded by T002e); the login
// twin 1.0.1 C2L_CLIENT_CHALLENGE_REQ (T002 section 3 layout, superseded walk per T002 Errata R1; T002c).
// PC writer 0x840630: WritePacket(p, 0x2c, 0, 1, -1), Write_u8, loop Write_u8 x 0x103 (0x77cfa0),
// Write_u8, Write_u8, loop Write_u8 x 0x3e (0x77cfe0) (V): the body of login 1.0.1 (writer
// 0x88a900), only group and id differ. PS4 CPacket_C2S_CLIENT_CHALLENGE_REQ::WritePacket 0x1a3aaf0
// (u8 in_CommonKeySrcSize, const u8 (*in_CommonKeyEnc)[259], u8 in_PasswordSrcSize,
// u8 in_PasswordEncSize, const u8 (*in_PasswordEnc)[62]); DWARF the same members (V).
// Server lead misplacements: CommonKeyEnc is 259 bytes, not 256 + 3 padding; PasswordEnc is a
// fixed 62 bytes (T003 section 19 item 4).
// NO HEADER: cSeedServerConnection::Send 0x9d6a20 recognises the handshake send command (game
// vtable +0x5c/+0x64 = group 0x2c, id 0, sub 1), drops the 9 header bytes and encrypts only the
// body with the fixed client key (V, T003 1). The raw carries no header either: the body starts at
// offset 0 (CommonKeySrcSize = 0x30), so the pattern does not use CPacket or `sourceOk`.
// Every `.44_0_1` raw is this 336-byte challenge since T002e filed the server's 304-byte notice as
// 44.1.16 S2C_CERT_GAME_SERVER_CERT_NTC, so no packet-size selector.
// Walk: 83/83 fit, slack 12.
// Body: u8 CommonKeySrcSize, u8 CommonKeyEnc[259], u8 PasswordSrcSize, u8 PasswordEncSize,
// u8 PasswordEnc[62] (324 B), then 12 bytes of cipher block padding (336 B).
// packet-id: 44.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

struct C2S_CERT_CLIENT_CHALLENGE_REQ {
    u8 CommonKeySrcSize;      // 48 in the captures (session key length, I)
    u8 CommonKeyEnc[259];     // RSA-PKCS#1 session key (256 B) + 3 zero bytes in the captures
    u8 PasswordSrcSize;       // 0x10 in the captures
    u8 PasswordEncSize;       // 0x10 in the captures
    u8 PasswordEnc[62];       // Blowfish-ECB of the fixed password, 16 B + zeros (T002c 1)
    // Fit: the decode ends within the last 15 bytes (cipher block padding).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CERT_CLIENT_CHALLENGE_REQ packet @ 0x00;
