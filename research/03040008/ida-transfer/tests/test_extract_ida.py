"""Pure parts of extract_ida.py, with fakes (no IDA)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import extract_ida as ex


def test_module_import_does_not_run_main():
    assert "_SUMMARY" not in vars(ex)


def test_exec_without_out_defines_helpers_only():
    src = Path(ex.__file__).read_text(encoding="utf-8")
    g: dict = {}
    exec(compile(src, "extract_ida.py", "exec"), g)
    assert "main" in g and "_SUMMARY" not in g


@pytest.mark.parametrize(
    ("name", "full"),
    [("edi", "rdi"), ("dil", "rdi"), ("r8d", "r8"), ("r9", "r9"), ("ecx", "rcx"), ("cl", "rcx"),
     ("xmm3", "xmm3"), ("ymm1", "xmm1"), ("esp", "rsp"), ("r15w", "r15"), (None, None)],
)
def test_canon_reg(name, full):
    assert ex.canon_reg(name) == full


def test_default_name():
    assert ex.is_default_name("sub_8BCBB0")
    assert not ex.is_default_name("Read_u32")
    assert not ex.is_default_name("sub_8BCBB0_0")


@pytest.mark.parametrize(
    ("value", "bits", "addr", "keep"),
    [(0, 32, False, False), (255, 32, False, False), (256, 32, False, True),
     (0xFFFFFFFF, 32, False, True), (-1, 32, False, True), (0x1BC0110, 32, True, False),
     (0x10000, 64, False, True), (0x100, 64, True, False)],
)
def test_interesting_constant(value, bits, addr, keep):
    assert ex.interesting_constant(value, bits, addr) is keep


@pytest.mark.parametrize(
    ("text", "q"),
    [("cSeedGameSvConnection::OnPacket_S2C_X(CPacket *)", "cSeedGameSvConnection::OnPacket_S2C_X"),
     ("nPacket::Read(CPacket &, unsigned short &)", "nPacket::Read"),
     ("A<B(int)>::f(void) const", "A<B(int)>::f"),
     ("Functor::operator()(int)", "Functor::operator()"),
     ("plain_symbol", "plain_symbol")],
)
def test_qualified_from_demangled(text, q):
    assert ex.qualified_from_demangled(text) == q


def test_match_roots_ps4_patterns():
    names = {
        1: "cSeedGameSvConnection::OnPacket_S2C_ACHIEVEMENT_COMPLETE_NTC",
        2: "cSeedLoginSvConnection::Send_C2L_LOGIN_REQ",
        3: "nUserSession::CPacket_S2C_GET_GP_RES::ReadPacket",
        4: "nUserSession::CPacket_C2S_WARP_REQ::WritePacket",
        5: "cNetGameServer::OnPacket_S2C_FOO_NTC",  # another class: not a root
        6: "nPacket::Read_CDataFoo",
        7: "nUserSession::CPacket_S2C_GET_GP_RES::ReadPacketHelper",
    }
    assert ex.match_roots(names, ex.PS4_ROOT_PATTERNS) == [1, 2, 3, 4]


def test_scope_closure_depth_and_distance():
    graph = {1: [2, 3], 2: [4], 3: [4, 1], 4: [5], 5: [6], 6: []}
    calls = []

    def callees(va):
        calls.append(va)
        return graph[va]

    assert ex.scope_closure([1], callees, 3) == {1: 0, 2: 1, 3: 1, 4: 2, 5: 3}
    assert sorted(calls) == [1, 2, 3, 4]  # each reached function expanded once, none at the limit
    assert ex.scope_closure([1, 4], lambda va: graph[va], 1) == {1: 0, 4: 0, 2: 1, 3: 1, 5: 1}
    assert ex.scope_closure([1], lambda va: graph[va], 0) == {1: 0}


def _ins(mnem, *ops, **kw):
    return {"mnem": mnem, "ops": list(ops), **kw}


def _reg(r):
    return {"type": "reg", "reg": r}


def _imm(v):
    return {"type": "imm", "value": v}


def test_pc_call_arguments():
    win = [_ins("push", _imm(5)), _ins("push", _reg("rax")),
           _ins("sub", _reg("rsp"), _imm(8)), _ins("mov", _reg("rcx"), _reg("rsi"), writes_ecx=True)]
    assert ex.pc_call_arguments(win) == {"pushed_bytes": 16, "pushes": 2, "ecx_loaded": True}
    assert ex.pc_call_arguments([]) == {"pushed_bytes": 0, "pushes": 0, "ecx_loaded": False}


def test_ps4_call_arguments_abi_order():
    win = [{"mnem": "mov", "writes": ["esi"]}, {"mnem": "lea", "writes": ["rdi"]},
           {"mnem": "mov", "writes": ["eax"]}, {"mnem": "movss", "writes": ["xmm0"]}, {"mnem": "x", "writes": ["r8d"]}]
    assert ex.ps4_call_arguments(win) == ["rdi", "rsi", "r8", "xmm0"]


def test_reads_before_write():
    effects = {"A": [None, "write"], "B": ["read"], "C": [None], "D": ["clobber", "read"], "E": ["readwrite"]}
    succ = {"A": ["B"], "C": ["D"], "D": ["B"], "E": []}
    assert ex.reads_before_write("A", succ.get, effects.get) is False  # written before B reads
    assert ex.reads_before_write("C", succ.get, effects.get) is False  # call clobbers first
    assert ex.reads_before_write("E", succ.get, effects.get) is True
    effects2 = {"A": [None], "B": ["write"], "C": ["read"]}
    assert ex.reads_before_write("A", {"A": ["B", "C"], "B": [], "C": []}.get, effects2.get) is True


def _phrase_esp():
    return {"type": "phrase", "reg": "rsp", "addr": 0}


def _store_window(literal, record=0x2000, clobber=False):
    win = [
        {"ea": 1, "mnem": "mov", "ops": [_phrase_esp(), _imm(literal)]},
        {"ea": 2, "mnem": "movq", "ops": [_reg("xmm0"), _phrase_esp()]},
    ]
    if clobber:
        win.append({"ea": 3, "mnem": "pxor", "ops": [_reg("xmm0"), _reg("xmm0")]})
    win.append({"ea": 4, "mnem": "movq", "ops": [{"type": "mem", "addr": record}, _reg("xmm0")]})
    return win


def test_resolve_callback_proved():
    r = ex.resolve_callback(_store_window(0x7E2CE0), 0x2000)
    assert r == {"callback": 0x7E2CE0, "store_ea": 1, "proved": True, "literal": 0x7E2CE0}


def test_resolve_callback_null_record():
    r = ex.resolve_callback(_store_window(0), 0x2000)
    assert r["proved"] and r["callback"] is None and r["literal"] == 0


@pytest.mark.parametrize(
    "window",
    [_store_window(0x7E2CE0, clobber=True),  # xmm overwritten between copy and store
     _store_window(0x7E2CE0, record=0x3000),  # store goes to another record
     _store_window(0x12345),  # literal outside code
     _store_window(0x7E2CE0)[1:]],  # no literal store
)
def test_resolve_callback_fails_closed(window):
    r = ex.resolve_callback(window, 0x2000)
    assert not r["proved"] and r["callback"] is None


def test_table_key():
    raw = bytes(16) + (0x1234).to_bytes(2, "little") + bytes([7]) + bytes(5)
    assert ex.table_key(raw) == (0x1234, 7)


def test_write_jsonl_header_first_and_atomic(tmp_path):
    out = tmp_path / "d.jsonl"
    n = ex.write_jsonl(str(out), {"kind": "header", "v": 1}, iter([{"kind": "function", "va": 2, "s": "é"}]))
    assert n == 2
    lines = out.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0])["kind"] == "header"
    assert json.loads(lines[1]) == {"kind": "function", "s": "é", "va": 2}
    assert not (tmp_path / "d.jsonl.tmp").exists()
    assert ex.write_jsonl(str(out), {"kind": "header"}, []) == 1
