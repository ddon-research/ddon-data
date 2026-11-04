// 6.25.16 C2S_PARTY_SEND_BINARY_MSG_NTC (client 03040008). Body: P1 1.1, P2 5
// (writer PC 0x841d20, list writer PC 0x77df90, sender PC 0x832360).
// packet-id: 6.25.16
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

struct C2S_PARTY_SEND_BINARY_MSG_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 count;
    u32 CharacterIds[count];
    s32 len;
    // T014b V (flow); I (role): Data.ctrlAction.unk_0x3C[] is the cContext +0xC48 4-slot array
    // (setter 0x479fd0, getter 0x475520); see nNetMsg.hexpat CtrlAction 0x3C.
    NetMsg<len> Data;
    bool msgFits = Data.fits [[export]];  // the NetMsg ended exactly at len
    str msgId = Data.msgIdFull [[export]];  // Head.mMsgIdFull ("SHORT" when len < 20)
    // Block padding of the decrypted packet (inferred), not fields.
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];  // the body ended within the last 15 bytes
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PARTY_SEND_BINARY_MSG_NTC packet @ 0x00;
