// 33.0.2 S2C_JOB_GET_JOB_CHANGE_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 1.1 (section 6 for the shared types).
// PC handler 0x7e05e0, reader 0x80d9b0: RES header, list 0x76b1d0, list 0x76b1d0, list 0x77246d,
// list 0x76c670 (V). PS4 CPacket_S2C_GET_JOB_CHANGE_LIST_RES::ReadPacket 0x19dc300: m_JobChangeInfo,
// m_JobReleaseInfo, m_PawnJobChangeInfoList, m_PlayPointList (V). Season 3: only CDataEquipItemInfo
// (include/Login.hexpat) differs (the PS4 element body fails 42/42). Walk: 42/42 fit, slack 0-12.
// Body: s32 Error [, s32 Result, four lists] (include/Job.hexpat).
// packet-id: 33.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Job.hexpat"

struct S2C_JOB_GET_JOB_CHANGE_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataJobChangeInfo> JobChangeInfo;
        MtTypedArray<CDataJobChangeInfo> JobReleaseInfo;
        MtTypedArray<CDataPawnJobChangeInfo> PawnJobChangeInfoList;
        MtTypedArray<CDataJobPlayPoint> PlayPointList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_JOB_GET_JOB_CHANGE_LIST_RES packet @ 0x00;
