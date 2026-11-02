"""Tests of unk_correlate.py on a synthetic pattern and JSON tree (stdlib unittest).

Run: python -X utf8 -I -m unittest discover -s research/03040008/packets/tools -p "test_*.py" -v
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import unk_correlate as u  # noqa: E402

INCLUDE = """
#pragma once
struct MtTypedArray<T> { u32 count; T entries[count]; };
struct CDataCommonU32 { u32 m_unValue; };
struct CDataMember {
    u32 CharacterId;      // named
    u32 unk_u32;          // equals CharacterId of the session
    MtTypedArray<CDataCommonU32> unk_list;
};
"""

PATTERN_A = """
// packet-id: 1.0.2
#include "Packet.hexpat"
struct S2C_A_RES : CPacket {
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataMember> Members;
        u8 unk_flag;          // 0/1
        u32 unk_time;         // epoch seconds
        u32 unk_none;         // nothing matches
        (0x3): u32 unk_0x3[4];
    }
};
"""

PATTERN_B = """
// packet-id: 1.1.2
struct S2C_B_RES : CPacket {
    u32 ItemId;
    u32 unk_never;
};
"""

TS = "2019-07-06T11_05_41.5025699-07_00"
EPOCH = 1562436341  # 2019-07-06T18:05:41Z


def packet_a(char_ids, unk_ids, flag, none):
    return {"packet": {
        "group": 1, "id": 0, "subId": 2, "source": 52, "packetcounter": 0, "Error": 0, "Result": 0,
        "Members": {"count": len(char_ids), "entries": [
            {"CharacterId": c, "unk_u32": x, "unk_list": {"count": 1, "entries": [{"m_unValue": 7}]}}
            for c, x in zip(char_ids, unk_ids)]},
        "unk_flag": flag, "unk_time": EPOCH + 100, "unk_none": none, "unk_0x3": [1, 2, 3, 4],
        "paddingSize": 3, "fits": True}}


class CorrelateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.pat = root / "pat"
        (self.pat / "include").mkdir(parents=True)
        (self.pat / "include" / "Packet.hexpat").write_text(INCLUDE, encoding="utf-8")
        (self.pat / "S2C_A_RES-pattern.cpp").write_text(PATTERN_A, encoding="utf-8")
        (self.pat / "S2C_B_RES-pattern.cpp").write_text(PATTERN_B, encoding="utf-8")
        self.json = root / "json"
        # Two captures, each with two TCP streams; session-specific character ids.
        sessions = {"cap1.pcapng": ([1001, 1002, 1003], 90001), "cap2.pcapng": ([2001, 2002, 2003], 90002)}
        n = 0
        for cap, (ids, none) in sessions.items():
            for stream in (1, 2):
                d = self.json / f"{cap}_tcp-stream-{stream}"
                d.mkdir(parents=True)
                n += 1
                (d / f"{n}_S2C_A_RES_{TS}.1_0_2.json").write_text(
                    json.dumps(packet_a(ids, ids[::-1], n % 2, none + stream * 7)), encoding="utf-8")
                (d / f"{n}_S2C_UNPATTERNED_NTC_{TS}_1.9_9_16.json").write_text("{}", encoding="utf-8")
        self.ps, self.c, self.rows, self.nodata = u.run(self.pat, self.json, "capture")
        self.by = {r.path: r for r in self.rows}

    def tearDown(self):
        self.tmp.cleanup()

    def test_inputs_are_bounded_to_patterned_packets(self):
        self.assertEqual(len(self.c.files), 4)
        self.assertEqual(self.c.skipped_unpatterned, 4)
        self.assertEqual(self.c.streams, 4)
        self.assertEqual(len(self.c.leaves), 2)  # sessions = captures

    def test_unknown_detection_and_resolution(self):
        r = self.by["packet.Members.entries[].unk_u32"]
        self.assertEqual((r.defined_in, r.struct, r.field_name), ("include/Packet.hexpat", "CDataMember", "unk_u32"))
        r = self.by["packet.Members.entries[].unk_list.entries[].m_unValue"]
        self.assertEqual((r.struct, r.field_name), ("CDataMember", "unk_list"))
        r = self.by["packet.unk_0x3[]"]
        self.assertEqual((r.defined_in, r.struct, r.field_name), ("S2C_A_RES-pattern.cpp", "S2C_A_RES", "unk_0x3"))
        self.assertNotIn("packet.Members.entries[].CharacterId", self.by)
        self.assertFalse(any(p.endswith(("paddingSize", "count", "Error")) for p in self.by))

    def test_session_specific_id_is_strong(self):
        r = self.by["packet.Members.entries[].unk_u32"]
        m = r.matches[0]
        self.assertEqual(m.leaf, "CharacterId")
        self.assertEqual((m.matched, m.total, m.agree, m.sessions), (6, 6, 2, 2))
        self.assertEqual(m.other_share, 0.0)
        self.assertEqual(r.tier, "strong")
        self.assertEqual(len(m.examples), 2)

    def test_single_session_or_flags_cannot_be_strong(self):
        r = self.by["packet.unk_flag"]
        self.assertIn("0-1", r.flags)
        self.assertNotEqual(r.tier, "strong")
        self.assertEqual(self.by["packet.unk_none"].tier, "unexplained")

    def test_timestamp_pseudo_reference(self):
        r = self.by["packet.unk_time"]
        self.assertEqual(r.matches[0].leaf, "epoch_s")
        self.assertEqual(r.matches[0].share, 1.0)

    def test_dense_reference_cannot_be_strong(self):
        m = u.Match("r", "StageNo", 5, 5, 2, 2, 0, chance=0.9)
        self.assertEqual(u.tier_of(m, 5, "informative"), "weak")
        m.chance = 0.1
        self.assertEqual(u.tier_of(m, 5, "informative"), "strong")

    def test_declared_without_data(self):
        self.assertIn(("S2C_B_RES-pattern.cpp", "S2C_B_RES", "unk_never"), self.nodata)

    def test_strong_tier_needs_agreeing_sessions(self):
        m = u.Match("r", "CharacterId", 5, 5, 1, 1, 0)
        self.assertEqual(u.tier_of(m, 5, "informative"), "medium")
        m.agree = m.sessions = 2
        self.assertEqual(u.tier_of(m, 5, "informative"), "strong")
        self.assertEqual(u.tier_of(m, 2, "informative"), "weak")
        self.assertEqual(u.tier_of(m, 5, "all-nonbinary"), "weak")

    def test_refuses_empty_input(self):
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        with self.assertRaises(SystemExit):
            u.run(self.pat, empty, "capture")
        with self.assertRaises(SystemExit):
            u.run(empty, self.json, "capture")

    def test_outputs_write(self):
        tsv = Path(self.tmp.name) / "o.tsv"
        md = Path(self.tmp.name) / "o.md"
        u.write_tsv(self.rows, self.nodata, tsv)
        u.write_md(self.rows, self.nodata, {"runtime": "0 s"}, md)
        lines = tsv.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0].split("\t"), u.TSV_HEADER)
        self.assertEqual(len(lines), 1 + len(self.rows) + len(self.nodata))
        self.assertTrue(lines[1].startswith("strong\t"))
        self.assertIn("CharacterId", md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
