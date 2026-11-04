// Server certificate notice body of client 03040008 (PC, Season 3), shared by the two patterns of
// the server's first packet on each connection: 1.1.16 L2C_LOGIN_SERVER_CERT_NTC (login) and
// 44.1.16 S2C_CERT_GAME_SERVER_CERT_NTC (game).
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T003-connection-server-cert.md sections 1 and 15. "PC 0x..." is a VA in the PC 03040008 database
// (image base 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the fields
// carry. Marks: V = read in IDA, I = inferred.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

// CDataServerCert (pattern-local name, I; the PS4 class is the packet itself).
// PC game reader 0x801a80 (handler 0x7c7250): loop Read_u8 x 0x100 (+16), 0x757d20 loop Read_u8
// x 0x10 (+272), 0x757ea0 loop Read_u32 x 5 (+288) (V). The handler hashes the 272 key bytes
// (0x13ee820(..., 272)) and compares the result with the five u32 (V; "SHA-1" I), then installs the
// key (0x13ec6d0(buf, modulus, 256), (..., expo, 16)) (V). The captures confirm SHA-1 (T002c 4).
// PS4 CPacket_S2C_GAME_SERVER_CERT_NOTICE::ReadPacket 0x19defe0 {u16 m_usError, u8
// m_ucOpenModulo[256], u8 m_ucOpenExpo[16], u32 m_unOpenHash[5]} (V). Season 3 / platform
// difference (V): PC reads no u16 error, because the client synthesises the header (receive
// 0x9d6d20, T003 section 1) and the body starts at offset 0.
// The login connection runs the same receive path (recv group 1, id 1; handler 0x886b00); its body
// layout is the game one by capture check (T002c 3-4: 42/42 SHA-1 match); the login reader behind
// 0x886b00 is not decoded (T003 section 20), so the shared layout is I for login.
struct CDataServerCert {
    u8 OpenModulo[256];       // RSA modulus
    u8 OpenExpo[16];          // RSA public exponent, 0x11 in the low byte in every capture
    u32 OpenHash[5];          // SHA-1 of modulus and exponent (T002c: matches 42/42 login, 83/83 game)
};
