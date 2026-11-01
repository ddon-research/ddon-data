"""Tests for guard_ida.py: python -m unittest discover -s tools/hooks"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard_ida  # noqa: E402

PS4 = "D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21"
PC = "D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008"


def call(**inp):
    return {"tool_name": "mcp__ida__open_database", "session_id": "s", "tool_input": inp}


class GuardIdaTest(unittest.TestCase):
    def test_private_copies_pass(self):
        self.assertIsNone(guard_ida.verdict(call(path=f"{PS4}/ddon-data-p1/DDOORBIS.elf.i64")))
        self.assertIsNone(guard_ida.verdict(call(path=f"{PC}/ddon-data-p2/2022_01_29_DDO_DUMP_FIX.exe.i64")))
        self.assertIsNone(guard_ida.verdict(call(
            path="D:\\research\\DDON-binaries\\IDA9.5\\PC_DDON_03040008\\ddon-data-x\\2022_01_29_DDO_DUMP_FIX.exe.i64")))
        self.assertIsNone(guard_ida.verdict(call(path="/d/research/DDON-binaries/IDA9.5/"
                                                  "PS4_DDON_02020005_2016_12_21/ddon-data-a_b/DDOORBIS.elf.i64")))

    def test_originals_and_other_paths_are_refused(self):
        for path in (f"{PS4}/DDOORBIS.elf.i64",
                     f"{PC}/2022_01_29_DDO_DUMP_FIX.exe.i64",
                     f"{PC}/feature008-arrays-20261018T095130Z/2022_01_29_DDO_DUMP_FIX.exe.i64",
                     f"{PS4}/ddon-data-p1/../DDOORBIS.elf.i64",
                     f"{PS4}/ddon-data-p1/DDOORBIS.elf",
                     "D:/research/DDON-binaries/IDA9.3/PS4_DDON_02020005_2016_12_21/ddon-data-p1/DDOORBIS.elf.i64",
                     "C:/tmp/ddon-data-p1/DDOORBIS.elf.i64"):
            self.assertIsNotNone(guard_ida.verdict(call(path=path)), path)

    def test_missing_path_is_refused(self):
        self.assertIsNotNone(guard_ida.verdict(call()))


if __name__ == "__main__":
    unittest.main()
