// 6.23.16 C2S_PARTY_SEND_BINARY_MSG_ALL_NTC (client 03040008). Body: P1 1.1, P2 5
// (writer PC 0x832260).
// packet-id: 6.23.16
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

struct C2S_PARTY_SEND_BINARY_MSG_ALL_NTC : CPacket {
    s32 len;
    NetMsg<len> Data;
    bool msgFits = Data.fits [[export]];  // the NetMsg ended exactly at len
    str msgId = Data.msgIdFull [[export]];  // Head.mMsgIdFull ("LOBBY_DUMMY", "SHORT" otherwise)
    // Block padding of the decrypted packet (inferred), not fields.
    u128 paddingSize = std::mem::size() - $ [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PARTY_SEND_BINARY_MSG_ALL_NTC packet @ 0x00;
