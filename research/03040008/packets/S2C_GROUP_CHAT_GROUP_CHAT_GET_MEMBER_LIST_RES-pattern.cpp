// S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES (18.0.2), client 03040008.
//
// Evidence:
// - PC 03040008 (2022_01_29_DDO_DUMP_FIX.exe; IDA 9.3 .c export, re-verified by Hex-Rays in the
//   live IDA 9.5 database on 2026-10-11):
//   - 0x809D80, called by cSeedGameSvConnection::OnPacket_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES:
//     reads s32 Error; when Error != 0 it copies Error into Result and STOPS reading.
//     Only when Error == 0 does it read s32 Result and the member array (0x75CBD0).
//   - 0x75CCF0 nPacket::Read_CDataCharacterListElement_: u32, 3x MtString, u16, u8,
//     2x CDataJobBaseInfo (u8, u8), MtString, u8.
// - PS4 02020005 DWARF: CDataCharacterListElement has no trailing u8 (added after Season 2).
// - Captures: all 31 annotated samples (e.g. stream85 tcp-stream-11, pcap 10290) are error
//   responses with Error = Result = 0xB79B (ERROR_CODE_GROUP_CHAT_NOT_IN_GROUP, "Already left
//   the group chat.") and an empty array. The server still sends Result and the array on error;
//   the client ignores them. No capture contains a member element yet.
//
// Payloads are padded to the 16-byte Camellia block size; the padding holds stale buffer bytes.

#pragma endian big

import std.mem;

#define CDataCharacterListElement CCharacterListElement
#define CDataJobBaseInfo CJobBaseInfo
#define CDataCommunityCharacterBaseInfo CCommunityCharacterBaseInfo
#define CDataCharacterName CCharacterName

struct MtString
{
    u16 strLen;
    char string[strLen];
};

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct CDataJobBaseInfo
{
    u8 Job;
    u8 Lv;
};

struct CDataCharacterName
{
    MtString FirstName;
    MtString LastName;
};

struct CDataCommunityCharacterBaseInfo
{
    u32 CharacterID;
    CCharacterName CharacterName;
    MtString ClanName;
};

struct CDataCharacterListElement
{
    CCommunityCharacterBaseInfo BaseInfo;
    u16 ServerID;
    u8 OnlineStatus;
    CJobBaseInfo CurrentJobInfo;
    CJobBaseInfo EntryJobInfo;
    MtString MatchingPlofile;
    u8 unknown; // Season 3 only (PC 0x75CCF0 offset 52); meaning unknown, C# guesses party type
};

struct MtTypedArray<T>
{
    u32 num;
    T array[num];
};

struct CPacket_S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES : CPacket
{
    s32 Error;
    // The client stops after Error when it is non-zero; the server still writes the rest.
    s32 Result;
    MtTypedArray<CCharacterListElement> GroupMemberList;
    u8 BlockPadding[std::mem::size() - $];
};

CPacket_S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES @0x00;
