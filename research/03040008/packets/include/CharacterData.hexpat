// cCharacterData save blob of client 03040008 (PC, Season 3): the 1024-byte body field of
// 9.1.1 C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ and of the 9.0.2
// S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES. Source: specs/006-packet-pattern-coverage/
// research/T001b-save-blob.md (cited "T001b"). Writer PC sub_467790 (cCharacterData::serialize,
// PS4 0x49740) + sub_4678F0 (stOptionData::serialize, PS4 0x1960180); reader PC sub_466560.
//
// Encoding (T001b 1, V PC and PS4): one LSB-first bit stream from blob byte 0. Stream bit k is
// bit (k & 7) of byte (k >> 3). A u32/u64 is converted to big-endian bytes, each byte pushed
// LSB-first; a u8 is one byte; a bool is 1 bit; no alignment between fields; Elias-delta off.
// - Bits 0..2431 (bytes 0..303) hold only u32/u64 and are byte aligned: they decode as plain
//   big-endian fields (struct below).
// - From bit 2432 the stream is unaligned: one little-endian bitfield (`bitStream`), whose
//   default bit order in PatternLanguage is least to most significant = the writer's order. A
//   u32 inside it is `CdBeU32`: four 8-bit fields b0..b3 (hidden), value = b0<<24|b1<<16|b2<<8|b3.
// - At version 0x19 the stream is 4170 bits; the 6 high bits of byte 521 are the flush padding
//   (`flushPad`, zero: flushBits writes a zeroed buffer). Bytes 522..1023 are never written by
//   the serializer: `unused_tail` is leftover allocator memory (T001b 1: no memset of the
//   2048-byte buffer, I; non-zero in 47/47 captures, PC-cap). Not padding, not data.
//
// Names: PS4 02020005 DWARF (cCharacterData::stCharacterData, stOptionData, stNameDisp,
// stCheckPawnHistoryData, stTutorialGuide, stJobMasterInfo, stAreaMasterInfo,
// stEnteredLandInfo, nCharacterData::stChatCstmCh). No member is an enum in DWARF (u8/bool/u32).
// PC-only fields (PC reader gates above PS4's version 0x13) are unk_<kind>_<PC offset>. Marks
// per T001b 2: V = read in PC code; V/I = write order V, PS4 member matched by order and the +1
// layout shift (I); I = inferred.
//
// Version gates: the writer is ungated (it always writes version 0x19). The PC reader sub_466560
// tests mVersion before each field (T001b 4, V). `g_cdVersion` is the version the gates test:
// 0x19 (all open) for the writer side; the 9.0.2 pattern sets `g_cdGated = true`, so the gates
// test the blob's own mVersion. Not applied: the reader's HeaderDispType rule (release < 2 and
// value 1 -> 4) changes the value after the read, not the stream.
// Include after `#pragma endian big`.

#pragma once

import std.mem;
import std.string;

bool g_cdGated = false;   // true: apply the PC reader's version gates (9.0.2)
u32 g_cdVersion = 0x19;

fn cd_open(u32 min) {
    return g_cdVersion >= min;
};

// Stream bits the unaligned part holds at g_cdVersion (T001b 2 widths; the gated widths per
// T001b 4). Used for the flush padding only.
fn cd_tail_bits() {
    u32 n = 0;
    if (cd_open(0x0F)) n += 1;                    // mIsAppraiseTalked
    if (cd_open(0x19)) n += 1;                    // unk_bit_13637
    if (cd_open(0x07)) {                          // mOption: 335 ungated bits + gated ones
        n += 335;
        if (cd_open(0x0B)) n += 1;                // mIsCamDrama
        if (cd_open(0x11)) n += 16;               // mCamRangeMagic, mCamRangeBow
        if (cd_open(0x15)) n += 1;                // unk_bit_09
        if (cd_open(0x13)) n += 8;                // mDefaultRimWarpTabPos
        if (cd_open(0x0C)) n += 2;                // mIsTutorialAnnounce, mIsMatchingAnnounce
        if (cd_open(0x08)) n += 1;                // mIsQuestActiveAuto
        if (cd_open(0x12)) n += 1;                // mIsMiniMapAutoScale
        if (cd_open(0x14)) n += 8;                // unk_u8_37
        if (cd_open(0x17)) n += 1;                // unk_bit_96
        if (cd_open(0x18)) n += 2;                // unk_bit_97, unk_bit_98
    }
    if (cd_open(0x0A)) n += 2 * (136 + 32);       // mChatCstmCh[2]
    if (cd_open(0x16)) n += 2 * 16 * 32;          // unk_u32_13508[16], unk_u32_13572[16]
    return n;
};

// u32 in the unaligned stream: 4 big-endian bytes, each 8 stream bits (T001b 1, V).
bitfield CdBeU32 {
    b0 : 8 [[hidden]];
    b1 : 8 [[hidden]];
    b2 : 8 [[hidden]];
    b3 : 8 [[hidden]];
    u32 value = (u32(b0) << 24) | (u32(b1) << 16) | (u32(b2) << 8) | u32(b3) [[export]];
};

bitfield CdByte {
    v : 8;
};

// Printable view of an MT_CHAR[17]: up to the first NUL; bytes outside 0x20..0x7E and the
// JSON-special '"' and '\' become '.'.
fn cd_text(ref auto bytes) {
    str s = "";
    for (u8 i = 0, i < 17, i += 1) {
        u8 c = bytes[i].v;
        if (c == 0) break;
        if (c < 0x20 || c > 0x7E || c == 0x22 || c == 0x5C) s = s + ".";
        else s = s + char(c);
    }
    return s;
};

fn cd_hex(ref auto bytes) {
    str s = "";
    for (u8 i = 0, i < 17, i += 1)
        s = s + std::format("{:02x}", bytes[i].v);
    return s;
};

// MT_CHAR[17] through writeBytes(.., 0x11) (T001b 2.1, V). `text` and `hex` are views of the
// 17 bytes (hex = all 17, stale bytes after the NUL included).
bitfield CdChar17 {
    CdByte bytes[17] [[hidden]];
    str text = cd_text(bytes) [[export]];
    str hex = cd_hex(bytes) [[export]];
};

// cCharacterData::stOptionData::stNameDisp {u8 mType; bool mClanName;}
bitfield CdNameDisp {
    mType : 8;
    bool mClanName : 1;
};

// nCharacterData::stChatCstmCh {MT_CHAR mName[17]; u32 mBit;}
bitfield CdChatCstmCh {
    CdChar17 mName;
    CdBeU32 mBit;
};

// mChatChFilterColor[i], mChatChFilterSE[i] (u8 each).
bitfield CdChatChFilter {
    mChatChFilterColor : 8;
    mChatChFilterSE : 8;
};

// stOptionData::serialize, PC sub_4678F0 order (T001b 2.2): 376 bits at version 0x19.
bitfield CdOptionData {
    bool mIsCamRevise : 1;                         // V
    if (cd_open(0x0B)) bool mIsCamDrama : 1;       // V (gate 0xB)
    if (cd_open(0x11)) {
        mCamRangeMagic : 8;                        // V (gate 0x11)
        mCamRangeBow : 8;                          // V (gate 0x11)
    }
    mCamPosType : 8;                               // V
    if (cd_open(0x15)) bool unk_bit_09 : 1;        // PC new, option +9, reader gate >= 0x15 (V)
    bool mIsMenuWindowOffAuto : 1;                 // V/I
    if (cd_open(0x13)) mDefaultRimWarpTabPos : 8;  // V (gate 0x13)
    bool mIsPartyBattleBGM : 1;                    // V/I
    CdBeU32 mPlayerIdlingEmotion;                  // V
    mPlayerIdlingEmotionTime : 8;                  // V
    bool mIsRotMiniMap : 1;                        // V
    mAlphaMiniMap : 8;                             // V
    bool mIsMapDispName : 1;                       // V
    bool mIsDispCharges : 1;                       // V/I
    if (cd_open(0x0C)) {
        bool mIsTutorialAnnounce : 1;              // V (gate 0xC)
        bool mIsMatchingAnnounce : 1;              // V (gate 0xC)
    }
    mAlphaHUDCmn : 8;                              // V/I
    if (cd_open(0x08)) bool mIsQuestActiveAuto : 1; // V (gate 8)
    bool mIsDispQuestGuide : 1;                    // V/I
    bool mIsQuestGuideAuto : 1;                    // V/I
    mQuestGuidePrio : 8;                           // V/I
    bool mIsDyingFilterDisp : 1;                   // V/I
    bool mIsMailBoxDispWarning : 1;                // V/I
    mHeaderDispType : 8;                           // V (reader's release rule, see header)
    CdNameDisp mHeaderNameDispParty;               // V/I (mHeaderNameDispMine is not written)
    CdNameDisp mHeaderNameDispOther;               // V/I
    bool mIsHeaderNameNpcName : 1;                 // V/I
    bool mIsHeaderNameNpcClass : 1;                // V/I
    bool mIsHeaderNameOmName : 1;                  // V/I
    CdNameDisp mChatLogNameDisp;                   // V/I
    bool mIsChatLogTimeStamp : 1;                  // V/I
    mAlphaChat : 8;                                // V/I
    // One loop of 12 writes Color[i] then SE[i] (PC loop ebp = 0Ch); the two DWARF arrays are
    // interleaved in the stream, so each element pairs them (V/I).
    CdChatChFilter mChatChFilter[12];
    bool mIsClockDispPing : 1;                     // V/I
    bool mIsClockDispTime : 1;                     // V/I
    mClockDispType : 8;                            // V/I
    bool mIsClockDispCh : 1;                       // V/I
    bool mIsEngageDisp : 1;                        // V/I
    bool mIsAchievementDispAnnounce : 1;           // V/I
    bool mIsRewardBoxDispWarning : 1;              // V/I
    if (cd_open(0x12)) bool mIsMiniMapAutoScale : 1; // V (gate 0x12), written after the clock bits
    if (cd_open(0x14)) unk_u8_37 : 8;              // PC new u8, option +37, gate >= 0x14 (V)
    if (cd_open(0x17)) bool unk_bit_96 : 1;        // PC new, option +96, gate >= 0x17 (V)
    if (cd_open(0x18)) {
        bool unk_bit_97 : 1;                       // PC new, option +97, gate >= 0x18 (V)
        bool unk_bit_98 : 1;                       // PC new, option +98, gate >= 0x18 (V)
    }
};

// Unaligned part, from blob bit 2432 at version 0x19 (T001b 2.1).
bitfield CdBitStream {
    if (cd_open(0x0F)) bool mIsAppraiseTalked : 1;  // V
    // PC new bool at +13637, reader gate >= 0x19 (V); meaning unknown.
    if (cd_open(0x19)) bool unk_bit_13637 : 1;
    if (cd_open(0x07)) CdOptionData mOption;        // V (sub_4678F0(this + 8968))
    if (cd_open(0x0A)) CdChatCstmCh mChatCstmCh[2]; // V
    if (cd_open(0x16)) {
        // Two PC-only u32[16] at +13508 and +13572, reader gate >= 0x16 (V). Meaning (I, weak,
        // PC-cap): the first repeats mCheckPawnHistory pawn ids, the second holds small values.
        CdBeU32 unk_u32_13508[16];
        CdBeU32 unk_u32_13572[16];
    }
    // flushBits: the rest of the last byte, zero (T001b 1, V).
    u8 flushPadBits = (8 - (cd_tail_bits() % 8)) % 8;
    if (flushPadBits > 0) flushPad : flushPadBits;
};

struct CdCheckPawnHistoryData {
    u32 mPawnId;
    u64 mCheckDate;   // Unix seconds in the captures (I, PC-cap)
};

struct CdTutorialGuide {
    u32 mFinishTutorial[16];
    u32 mLatestTutorial[5];
};

// stJobMasterInfo, stAreaMasterInfo, stEnteredLandInfo: u32[1] each in DWARF; the writer
// writes element 0 (V).
struct CdJobMasterInfo {
    if (cd_open(0x06)) u32 mJobMasterTalked[1];       // V
    if (cd_open(0x0D)) u32 mJobMasterSkillTalked[1];  // V
};

struct CdAreaMasterInfo {
    if (cd_open(0x0E)) u32 mAreaMasterTalked[1];      // V; below 0xE the reader fills it from a table
};

struct CdEnteredLandInfo {
    if (cd_open(0x10)) u32 mEnteredLand[1];           // V
};

// The 1024-byte blob field. Byte-aligned prefix (304 bytes at version 0x19), then the bit
// stream, then the unwritten rest of the 1024 bytes.
struct CharacterBinSaveData {
    u32 mVersion;                                  // V; captures 0x19
    g_cdVersion = g_cdGated ? mVersion : 0x19;
    if (cd_open(0x09)) u32 mReleaseVersion;        // V; captures 0x3040
    if (cd_open(0x02)) CdCheckPawnHistoryData mCheckPawnHistory[16]; // V
    if (cd_open(0x05)) {
        u32 mQuestEtcF;                            // V
        CdTutorialGuide mTutorialGuide;            // V
    }
    CdJobMasterInfo mJobMasterInfo;
    CdAreaMasterInfo mAreaMasterInfo;
    CdEnteredLandInfo mEnteredLandInfo;
    le CdBitStream bitStream;
    bool flushPadZero = true [[export]];
    if (bitStream.flushPadBits > 0) flushPadZero = bitStream.flushPad == 0;
    u32 streamBytes = $ - addressof(this) [[export]];   // 522 at version 0x19
    // Never written by the serializer: leftover allocator memory (see header).
    u8 unused_tail[1024 - streamBytes];
};
