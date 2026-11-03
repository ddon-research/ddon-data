"""extract_dwarf.py: pure helpers, and a fixture check of two functions against llvm-dwarfdump.

The fixture texts are ``llvm-dwarfdump --debug-info=<die> -c`` (LLVM 23.1.4) of the staged
PS4 02020005 ELF (sha256 4236f598...63c0). ``dwarf_two_functions.jsonl`` holds the extractor's
records for the same two functions; the always-run test checks those against the llvm text, and
the dump test (skipped when ``dumps/ps4-dwarf.jsonl`` is absent) checks the dump against them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import extract_dwarf as xd

FIX = Path(__file__).parent / "fixtures"
DUMP = Path(__file__).parents[1] / "dumps" / "ps4-dwarf.jsonl"
FUNCS = {
    "cSeedGameSvConnection::OnPacket_S2C_ACHIEVEMENT_COMPLETE_NTC": "achievement_complete_ntc.dwarfdump.txt",
    "nUserSession::CPacket_S2C_GET_GP_RES::ReadPacket": "get_gp_res_readpacket.dwarfdump.txt",
}


# --- pure helpers ---------------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("sym", "root"),
    [("_ZN21cSeedGameSvConnection37OnPacket_S2C_ACHIEVEMENT_COMPLETE_NTCEP7CPacket", True),
     ("_ZN22cSeedLoginSvConnection18Send_C2L_LOGIN_REQEv", True),
     ("_ZN12nUserSession22CPacket_S2C_GET_GP_RES10ReadPacketEP7CPacket", True),
     ("_ZN12nUserSession20CPacket_C2S_WARP_REQ11WritePacketEP7CPacketjjj", True),
     ("_ZN14cNetGameServer20OnPacket_S2C_FOO_NTCEv", False),
     ("_ZN7nPacket4ReadI13CDataEditInfoEEiR7CPacketRT_", False)],
)
def test_is_root_symbol(sym, root):
    assert xd.is_root_symbol(sym) is root


def test_read_chains_sha(tmp_path):
    p = tmp_path / "c.tsv"
    p.write_text("# x\nformat\t2\nelf_sha256\tabc\ntool\tt\n0x1\tf\n", encoding="utf-8")
    assert xd.read_chains_sha(p) == "abc"
    p.write_text("# x\nformat\t2\n0x1\tf\n", encoding="utf-8")
    with pytest.raises(ValueError):
        xd.read_chains_sha(p)


def test_render_expr():
    assert xd.render_expr([("DW_OP_fbreg", [-24]), ("DW_OP_deref", [])]) == "DW_OP_fbreg -24; DW_OP_deref"


@pytest.mark.parametrize(("v", "off"), [(8, 8), (None, None), ([0x23, 0x90, 0x01], 144), ([0x10, 1], None)])
def test_member_offset(v, off):
    assert xd.member_offset(v) == off


def test_cu_lookup():
    idx = xd.cu_index([(0x100, 0x200, 1), (0x200, 0x280, 2), (0x300, 0x300, 9), (0x150, 0x160, 3)])
    assert xd.cu_for(idx, 0x100) == 1
    assert xd.cu_for(idx, 0x27F) == 2
    assert xd.cu_for(idx, 0x155) == 3
    assert xd.cu_for(idx, 0x180) == 1  # back past a nested range
    assert xd.cu_for(idx, 0x300) is None  # empty range dropped
    assert xd.cu_for(idx, 0x50) is None
    assert xd.cus_containing(idx, 0x155) == [1, 3]


def test_shape_member_and_prototype():
    m = xd.shape_member("mA", 8, 4, "u32", 0x10, bit_size=3, bit_offset=5, static=False)
    assert m == {"name": "mA", "offset": 8, "size": 4, "type": "u32", "type_die": 0x10, "bit_size": 3, "bit_offset": 5}
    assert "static" in xd.shape_member("s", None, 4, "u32", 1, static=True)
    params = [{"name": "this", "type": "A*", "artificial": True}, {"name": "pPacket", "type": "CPacket*"}]
    assert xd.prototype_text("s32", "A::ReadPacket", params) == "s32 A::ReadPacket(CPacket* pPacket)"


# --- llvm-dwarfdump fixture --------------------------------------------------------------------------

_DIE = re.compile(r"^(0x[0-9a-f]+):( *)(DW_TAG_\w+|NULL)")
_ATTR = re.compile(r"^\s+(DW_AT_\w+)\s+\((.*)$")


def parse_dwarfdump(text: str) -> list[dict]:
    """DIEs of an ``llvm-dwarfdump -c`` subtree: offset, tag, depth, parent, raw attribute text."""
    dies, stack = [], []
    cur = None
    for line in text.splitlines():
        m = _DIE.match(line)
        if m:
            depth = (len(m.group(2)) - 1) // 2
            if m.group(3) == "NULL":
                cur = None
                continue
            while len(stack) > depth:
                stack.pop()
            cur = {"off": int(m.group(1), 16), "tag": m.group(3), "depth": depth,
                   "parent": stack[-1]["off"] if stack else None, "attrs": {}}
            dies.append(cur)
            stack.append(cur)
            continue
        a = _ATTR.match(line)
        if a and cur is not None:
            cur["attrs"][a.group(1)] = a.group(2)
            last = a.group(1)
        elif cur is not None and line.strip().startswith("["):
            cur["attrs"][last] += "\n" + line.strip()
    return dies


def _ref(text: str | None) -> int | None:
    m = re.match(r"(0x[0-9a-f]+)", text or "")
    return int(m.group(1), 16) if m else None


def _name(text: str | None) -> str | None:
    m = re.match(r'"(.*)"\)$', text or "")
    return m.group(1) if m else None


def _expected(dies):
    by = {d["off"]: d for d in dies}
    root = dies[0]

    def inside_inline(d):
        p = d["parent"]
        while p is not None and p != root["off"]:
            if by[p]["tag"] == "DW_TAG_inlined_subroutine":
                return True
            p = by[p]["parent"]
        return False

    params = [d for d in dies if d["tag"] == "DW_TAG_formal_parameter" and d["parent"] == root["off"]]
    local = [d for d in dies if d["tag"] == "DW_TAG_variable" and not inside_inline(d)]
    blocks = [d for d in dies if d["tag"] == "DW_TAG_lexical_block"]
    inl = [d for d in dies if d["tag"] == "DW_TAG_inlined_subroutine"]
    return root, params, local, blocks, inl


def _fixture_records() -> dict[str, dict]:
    recs = {}
    for line in (FIX / "dwarf_two_functions.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        recs[r["name"]] = r
    return recs


@pytest.mark.parametrize("name", sorted(FUNCS))
def test_fixture_records_match_llvm_dwarfdump(name):
    rec = _fixture_records()[name]
    dies = parse_dwarfdump((FIX / FUNCS[name]).read_text(encoding="utf-8"))
    root, params, local, blocks, inl = _expected(dies)
    assert rec["die"] == root["off"]
    lo = int(re.match(r"(0x[0-9a-f]+)", root["attrs"]["DW_AT_low_pc"]).group(1), 16)
    assert rec["va"] == lo
    assert [p["die"] for p in rec["params"]] == [d["off"] for d in params]
    for p, d in zip(rec["params"], params, strict=True):
        if "DW_AT_name" in d["attrs"]:
            assert p["name"] == _name(d["attrs"]["DW_AT_name"])
        assert p["type_die"] == _ref(d["attrs"].get("DW_AT_type"))
        ranges = re.findall(r"\[(0x[0-9a-f]+), (0x[0-9a-f]+)\): (DW_OP_\w+)", d["attrs"].get("DW_AT_location", ""))
        if ranges:
            got = [[a, b, e.split(";")[0].split()[0]] for a, b, e in p["location"]["list"]]
            assert got == [[int(a, 16), int(b, 16), op] for a, b, op in ranges]
    assert [v["die"] for v in rec["locals"]] == [d["off"] for d in local]
    for v, d in zip(rec["locals"], local, strict=True):
        if "DW_AT_name" in d["attrs"]:
            assert v["name"] == _name(d["attrs"]["DW_AT_name"])
        if "DW_AT_type" in d["attrs"]:
            assert v["type_die"] == _ref(d["attrs"]["DW_AT_type"])
    assert [b["die"] for b in rec["blocks"]] == [d["off"] for d in blocks]
    assert [i["die"] for i in rec["inlined"]] == [d["off"] for d in inl]
    for i, d in zip(rec["inlined"], inl, strict=True):
        line = d["attrs"].get("DW_AT_call_line")
        assert i["call_line"] == (int(line.rstrip(")")) if line else None)


def test_fixture_records_have_expected_names():
    recs = _fixture_records()
    ach = recs["cSeedGameSvConnection::OnPacket_S2C_ACHIEVEMENT_COMPLETE_NTC"]
    assert [p["name"] for p in ach["params"]] == ["this", "pPacket"]
    gp = recs["nUserSession::CPacket_S2C_GET_GP_RES::ReadPacket"]
    assert gp["prototype"] == "s32 nUserSession::CPacket_S2C_GET_GP_RES::ReadPacket(CPacket* pPacket)"


@pytest.mark.skipif(not DUMP.exists(), reason="dumps/ps4-dwarf.jsonl not built (run extract_dwarf.py)")
def test_dump_agrees_with_fixture_records():
    want = _fixture_records()
    got = {}
    with open(DUMP, encoding="utf-8") as fh:
        header = json.loads(fh.readline())
        for line in fh:
            if '"kind":"function"' in line:
                r = json.loads(line)
                if r["name"] in want:
                    got[r["name"]] = r
    assert header["elf_sha256"] == header["inline_chains_elf_sha256"]
    assert got == want


def test_run_refuses_elf_not_matching_inline_chains(tmp_path):
    elf = tmp_path / "x.elf"
    elf.write_bytes(b"not the staged elf")
    chains = tmp_path / "c.tsv"
    chains.write_text("format\t2\nelf_sha256\t" + "0" * 64 + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="refused"):
        xd.main(["--elf", str(elf), "--chains", str(chains), "--out", str(tmp_path / "o.jsonl")])
    assert not (tmp_path / "o.jsonl").exists()
