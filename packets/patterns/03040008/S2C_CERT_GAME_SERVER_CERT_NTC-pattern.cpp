// 44.1.16 S2C_CERT_GAME_SERVER_CERT_NTC (client 03040008), the game server's first packet.
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md sections 1
// and 15; T002c-challenge-decrypt.md sections 3 and 4 (fixed key, 304-byte files, SHA-1 check).
// Errata R1 of both reports: T002c 3's "unknown[12]" is cipher padding; T003 15's packet-size
// selector advice is superseded by T002e (files renamed); T003 1(b) cites section 15, not 27.
// PC receive 0x9d6d20 decrypts the first packet with the fixed client key and synthesises the
// header group 0x2c, id 1, sub 0x10 (game vtable +0x60/+0x68) (V); handler 0x7c7250, reader
// 0x801a80 (V). Arrowgene PacketId.cs:1737; PS4 S2C_GAME_SERVER_CERT_NOTICE
// (OnPacket 0x330310, ReadPacket 0x19defe0).
// NO HEADER: the wire carries none, and the patched CLI (docs/reference/arrowgene-cli-patches.md, T002e)
// writes the raw without one. The body starts at offset 0; PC reads no u16 error (V, T003 15).
// Body: u8 OpenModulo[256], u8 OpenExpo[16], u32 OpenHash[5] (292 B) + 12 bytes of cipher padding
// (304 B); the client reads only the 292 bytes (T003 1).
// packet-id: 44.1.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Cert.hexpat"

struct S2C_CERT_GAME_SERVER_CERT_NTC {
    CDataServerCert Cert;
    // Fit: the decode ends within the last 15 bytes (cipher block padding).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CERT_GAME_SERVER_CERT_NTC packet @ 0x00;
