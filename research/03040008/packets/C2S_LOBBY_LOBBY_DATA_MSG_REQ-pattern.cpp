// 3.3.16 C2S_LOBBY_LOBBY_DATA_MSG_REQ (client 03040008). Body: P1 1.1, P2 5
// (writer PC 0x841b60, sender PC 0x82ed10).
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

struct C2S_LOBBY_LOBBY_DATA_MSG_REQ : CPacket {
    LOBBY_PACKET_TYPE Type;
    u32 CharacterId;
    s32 len;
    LobbyDataMessage<len> Data;
    bool msgFits = Data.fits [[export]];  // the NetMsg ended exactly at len
    str msgId = Data.msgIdFull [[export]];  // Head.mMsgIdFull ("LOBBY_DUMMY", "SHORT" otherwise)
    // Block padding of the decrypted packet (inferred), not fields.
    u128 paddingSize = std::mem::size() - $ [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_LOBBY_LOBBY_DATA_MSG_REQ packet @ 0x00;
