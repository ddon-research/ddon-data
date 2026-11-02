// Group 33 JOB CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T006-job-lobby-area-stage.md sections 1.1 and 6. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the
// fields carry (m_ prefix dropped). Marks: V = read in IDA, I = inferred. Server C# names are leads
// only. The Season 3 difference of these lists lies in CDataEquipItemInfo (include/Login.hexpat, PC
// 0x766070); this file includes Login.hexpat, and nothing it includes includes this one.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Login.hexpat"

// CDataJobChangeInfo: PC list reader 0x76b1d0, element {u8, list 0x765fb0 of CDataEquipItemInfo
// (0x766070)} (V); PS4 Read_CDataJobChangeInfo_ 0x19fe620, CDataJobChangeInfo {u8 m_ucJobID,
// MtTypedArray<CDataEquipItemInfo> m_EquipItemList} (V).
struct CDataJobChangeInfo {
    u8 JobID;
    MtTypedArray<CDataEquipItemInfo> EquipItemList;
};

// CDataPawnJobChangeInfo: PC list reader 0x77246d (read linearly; IDA's function starts at 0x77246c),
// element {u8, u32, list 0x76b1d0, list 0x76b1d0} (V); PS4 Read_CDataPawnJobChangeInfo_ 0x19fe870,
// {u8 m_ucSlotNo, u32 m_unPawnId, m_JobChangeInfoList, m_JobReleaseInfoList} (V).
struct CDataPawnJobChangeInfo {
    u8 SlotNo;
    u32 PawnId;
    MtTypedArray<CDataJobChangeInfo> JobChangeInfoList;
    MtTypedArray<CDataJobChangeInfo> JobReleaseInfoList;
};

// CDataPlayPointData: read inline by PC 0x76c670 {u8, u32} (V); PS4 DWARF type CPlayPointData
// {u8 m_ucExpMode, u32 m_unPlayPoint} (V).
struct CDataPlayPointData {
    u8 ExpMode;
    u32 PlayPoint;
};

// CDataJobPlayPoint: PC list reader 0x76c670, element {u8, u8, u32} (V); PS4 Read_CDataJobPlayPoint_
// 0x19e4880, CDataJobPlayPoint {u8 m_ucJob, CPlayPointData m_Data} (V).
struct CDataJobPlayPoint {
    u8 Job;
    CDataPlayPointData Data;
};
