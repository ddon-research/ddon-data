// 3.4.16 S2C_LOBBY_LOBBY_DATA_MSG_NTC (client 03040008). Body: P1 1.1, P2 5
// (handler PC 0x7e2ad0, reader PC 0x80e970).
// packet-id: 3.4.16
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

struct S2C_LOBBY_LOBBY_DATA_MSG_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    LOBBY_PACKET_TYPE Type;
    u32 CharacterId;
    s32 len;
    LobbyDataMessage<len> Data;
    bool msgFits = Data.fits [[export]];  // the NetMsg ended exactly at len
    str msgId = Data.msgIdFull [[export]];  // Head.mMsgIdFull ("LOBBY_DUMMY", "SHORT" otherwise)
    ONLINE_STATUS OnlineStatus;
    // Block padding of the decrypted packet (inferred), not fields.
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];  // the body ended within the last 15 bytes
    if (paddingSize > 0) padding[paddingSize];
};

S2C_LOBBY_LOBBY_DATA_MSG_NTC packet @ 0x00;
