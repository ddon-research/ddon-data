// 6.26.16 S2C_PARTY_RECV_BINARY_MSG_NTC (client 03040008). Body: P1 1.1 (PS4 ReadPacket 0x19d5290), P2 5 (PC handler
// 0x7e9880, reader 0x811600): u32 CharacterID, s32 len, u8[len] Data, u8 OnlineStatus; the client hands Data
// to receiveNetwork with session 0, so Data is one NetMsg (no lobby dummy).
// No capture of this packet: validated only on a synthetic file built from a 6.25.16 payload.
// packet-id: 6.26.16
// Payload decoders: include/nNetMsg.hexpat (spec 005).
#pragma endian big

#include "nNetMsg.hexpat"

// Packet header of the decrypted_raw files (9 bytes).
struct CPacket {
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct S2C_PARTY_RECV_BINARY_MSG_NTC : CPacket {
    u32 CharacterId;
    s32 len;
    NetMsg<len> Data;
    bool msgFits = Data.fits [[export]];  // the NetMsg ended exactly at len
    str msgId = Data.msgIdFull [[export]];  // Head.mMsgIdFull ("SHORT" when len < 20)
    ONLINE_STATUS OnlineStatus;
    // Block padding of the decrypted packet (inferred), not fields.
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];  // the body ended within the last 15 bytes
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTY_RECV_BINARY_MSG_NTC packet @ 0x00;
