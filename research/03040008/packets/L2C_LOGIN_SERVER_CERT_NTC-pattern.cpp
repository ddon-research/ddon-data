// 1.1.16 L2C_LOGIN_SERVER_CERT_NTC (client 03040008), the login server's first packet.
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md sections 1
// and 15; T002c-challenge-decrypt.md sections 3 and 4 (fixed key, 304-byte files, SHA-1 check).
// PC receive 0x9d6d20 decrypts the first packet with the fixed client key and synthesises the
// header group 1, id 1, sub 0x10 (login vtable 0x1bd6af8 +0x60/+0x68) (V); handler 0x886b00 (T002
// handler table; its reader is not decoded, T003 section 20). Arrowgene PacketId.cs:162; PS4
// OnPacket_L2C_LOGIN_SERVER_CERT_NOTICE 0x37ceb0. The body is the game notice's (include/Cert.hexpat:
// the game reader 0x801a80 is V; for login the layout rests on the capture SHA-1 check, T002c 4, I).
// NO HEADER: the wire carries none, and the patched CLI (packets README arrowgene-patches, T002e)
// writes the raw without one. The body starts at offset 0; PC reads no u16 error (V, T003 15).
// Body: u8 OpenModulo[256], u8 OpenExpo[16], u32 OpenHash[5] (292 B) + 12 bytes of cipher padding
// (304 B); the client reads only the 292 bytes (T003 1).
// packet-id: 1.1.16
// packet-select: L2C_LOGIN_SERVER_CERT_NTC
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Cert.hexpat"

struct L2C_LOGIN_SERVER_CERT_NTC {
    CDataServerCert Cert;
    // Fit: the decode ends within the last 15 bytes (cipher block padding).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

L2C_LOGIN_SERVER_CERT_NTC packet @ 0x00;
