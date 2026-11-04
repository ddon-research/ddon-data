// 4.0.2 L2C_GP_COURSE_GET_INFO_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 10.
// PC reader 0x889bc0 via handler 0x8870b0 (key 0x20000): header, list 0x767340 of
// CDataGPCourseInfo, list 0x767220 of CDataGPCourseEffectParam, Read_u32 (V): s32 Error; Result and the body only when Error == 0 (T002
// section 0.2).
// PS4 CPacket_L2C_GP_COURSE_GET_INFO_RES::ReadPacket 0x1a3d430, slot 11; DWARF {u16 m_usError,
// u32 m_unResult, MtTypedArray<CDataGPCourseInfo> m_CourseInfo,
// MtTypedArray<CDataGPCourseEffectParam> m_Effects, u32 m_unVersion}; PC reads Result as s32 (V).
// Types: include/GP.hexpat.
// Walk: 41/41 fit, slack 6-14; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, CourseInfo list, Effects list, u32 Version].
// packet-id: 4.0.2
// packet-select: L2C_GP_COURSE_GET_INFO_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "GP.hexpat"

struct L2C_GP_COURSE_GET_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataGPCourseInfo> CourseInfo;
        MtTypedArray<CDataGPCourseEffectParam> Effects;
        u32 Version;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

L2C_GP_COURSE_GET_INFO_RES packet @ 0x00;
