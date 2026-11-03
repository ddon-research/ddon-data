"""extract_ida.py v3 (T005c): constant call arguments, codec shapes, extern targets; fakes, no IDA."""

from __future__ import annotations

import pytest

import extract_ida as ex


def _ins(mnem, *ops, **kw):
    return {"mnem": mnem, "ops": list(ops), **kw}


def _reg(r, size=4):
    return {"type": "reg", "reg": r, "size": size}


def _imm(v, size=4):
    return {"type": "imm", "value": v, "size": size}


def _displ(r, addr, size=4):
    return {"type": "displ", "reg": r, "addr": addr, "size": size}


def _phrase(r, size=4):
    return {"type": "phrase", "reg": r, "addr": 0, "size": size}


def _mem(addr, size=4):
    return {"type": "mem", "addr": addr, "size": size}


def _push(v):
    return _ins("push", _imm(v) if isinstance(v, int) else _reg(v))


def test_script_version_bumped():
    assert ex.SCRIPT_VERSION == "3"


# --- implicit writes and argument bytes --------------------------------------------------------------

@pytest.mark.parametrize(
    ("mnem", "n_ops", "rep", "regs"),
    [("movs", 0, True, ("rsi", "rdi", "rcx")), ("stos", 0, False, ("rdi",)), ("loop", 1, False, ("rcx",)),
     ("imul", 1, False, ("rax", "rdx")), ("imul", 2, False, ()), ("cdq", 0, False, ("rdx",)),
     ("mov", 2, False, ())],
)
def test_implicit_writes(mnem, n_ops, rep, regs):
    assert ex.implicit_writes(mnem, n_ops, rep) == regs


_ADD_ESP_8 = _ins("add", _reg("rsp"), _imm(8))


@pytest.mark.parametrize(
    ("rets", "after", "n"),
    [([0x14], None, 0x14),  # callOnPacketFunc: ret 14h
     ([4, 4], _ins("mov", _reg("rax"), _reg("rcx")), 4),
     ([0], _ADD_ESP_8, 8),  # cdecl: caller cleans
     (None, _ADD_ESP_8, 8),
     ([0], _ins("pop", _reg("rcx")), 0),  # known callee, plain retn, no add: no stack arguments
     (None, None, None),  # indirect call, no cleanup: unknown
     ([4, 8], None, None)],  # mixed ret immediates prove nothing
)
def test_call_arg_bytes(rets, after, n):
    assert ex.call_arg_bytes(rets, after) == n


# --- PC constant arguments ----------------------------------------------------------------------------

def test_pc_write_packet_key_by_slot():
    # T005b § 4, 0x833670: push 0FFFFFFFFh; push 1; push 1Ch; push 8; push eax; call WritePacket (cdecl)
    win = [_push(0xFFFFFFFF), _push(1), _push(0x1C), _push(8), _push("rax")]
    r = ex.pc_const_args(win, 20)
    assert r == {"stack": [[1, 8], [2, 0x1C], [3, 1], [4, 0xFFFFFFFF]], "ecx": None}


def test_pc_call_on_packet_func_slot_index():
    # T005b § 1.1 pair 1: callOnPacketFunc(mgr=[this+13Ch], 91, "...", dword, result, 1), ret 14h
    win = [_push(1), _push("rax"), _ins("push", _mem(0x1BC780C)), _push(0x1A00000), _push(91),
           _ins("mov", _reg("rcx"), _displ("rsi", 0x13C), writes_ecx=True)]
    r = ex.pc_const_args(win, 0x14)
    assert r["stack"] == [[0, 91], [1, 0x1A00000], [4, 1]]
    assert r["ecx"] is None  # loaded from a member, not an immediate or an absolute address


def test_pc_push_beyond_the_argument_window_is_not_an_argument():
    # push 7 belongs to an enclosing (later) call; the inner callee takes 4 bytes (ret 4)
    win = [_push(7), _push(9)]
    assert ex.pc_const_args(win, 4)["stack"] == [[0, 9]]


def test_pc_push_of_an_earlier_call_is_outside_the_window():
    # push 5; call a; push 9; call b(8 bytes): b's window starts after `call a`, so slot 1 is unknown
    win_b = [_push(9)]
    assert ex.pc_const_args(win_b, 8)["stack"] == [[0, 9]]


def test_pc_unknown_arity_records_no_stack():
    assert ex.pc_const_args([_push(9)], None)["stack"] == []
    assert ex.pc_const_args([_push(9)], 0)["stack"] == []


def test_pc_seh_prologue_pushes_are_not_arguments():
    win = [_push("rbp"), _ins("mov", _reg("rbp"), _reg("rsp")), _push(0xFFFFFFFF), _push(0x1A12345),
           _ins("sub", _reg("rsp"), _imm(0x10)), _push(5)]
    assert ex.pc_const_args(win, 4)["stack"] == [[0, 5]]


def test_pc_mov_esp_slots_and_overwrite():
    win = [_ins("sub", _reg("rsp"), _imm(8)), _ins("mov", _displ("rsp", 4), _imm(3)),
           _ins("mov", _phrase("rsp"), _imm(2))]
    assert ex.pc_const_args(win, 8)["stack"] == [[0, 2], [1, 3]]
    overwritten = [*win, _ins("mov", _phrase("rsp"), _reg("rax"))]
    assert ex.pc_const_args(overwritten, 8)["stack"] == [[1, 3]]
    double = [*win, _ins("movsd", _phrase("rsp", 8), _reg("xmm0", 8))]  # an 8-byte store covers both
    assert ex.pc_const_args(double, 8)["stack"] == []


def test_pc_pop_drops_pushed_constant():
    win = [_push(5), _ins("pop", _reg("rcx"))]
    assert ex.pc_const_args(win, 4)["stack"] == []


def test_pc_unmodelled_esp_change_drops_the_stack_picture():
    win = [_push(5), _ins("mov", _reg("rsp"), _reg("rbp"))]
    assert ex.pc_const_args(win, 4)["stack"] == []
    assert ex.pc_const_args([_push(5), _ins("pushad")], 4)["stack"] == []


@pytest.mark.parametrize(
    ("ins", "ecx"),
    [(_ins("mov", _reg("rcx"), _imm(0x1D2E0F0), writes_ecx=True), {"kind": "imm", "value": 0x1D2E0F0}),
     (_ins("xor", _reg("rcx"), _reg("rcx"), writes_ecx=True), {"kind": "imm", "value": 0}),
     (_ins("lea", _reg("rcx"), _mem(0x1D2E0F0), writes_ecx=True), {"kind": "addr", "value": 0x1D2E0F0}),
     (_ins("mov", _reg("rcx"), _mem(0x1D2E0F0), writes_ecx=True), {"kind": "load", "addr": 0x1D2E0F0}),
     (_ins("lea", _reg("rcx"), _displ("rsp", 0x10), writes_ecx=True), None),
     (_ins("mov", _reg("rcx", 2), _imm(5, 2), writes_ecx=True), None)],
)
def test_pc_ecx_constant(ins, ecx):
    assert ex.pc_const_args([ins], 0)["ecx"] == ecx


def test_pc_ecx_overwritten_before_the_call():
    load = _ins("mov", _reg("rcx"), _imm(10), writes_ecx=True)
    # `rep movsd` writes ecx implicitly (implicit_writes gives rcx; the IDA side sets writes_ecx)
    rep = _ins("movs", writes_ecx="rcx" in ex.implicit_writes("movs", 0, True))
    assert ex.pc_const_args([load, rep], 0)["ecx"] is None
    assert ex.pc_const_args([load, _ins("inc", _reg("rcx"), writes_ecx=True)], 0)["ecx"] is None
    assert ex.pc_const_args([load, _ins("mov", _reg("rax"), _reg("rcx"))], 0)["ecx"] == {"kind": "imm", "value": 10}


# --- PS4 constant arguments ---------------------------------------------------------------------------

def _w(mnem, dst, src, writes=None):
    return {"mnem": mnem, "ops": [dst, src], "writes": [dst["reg"]] if writes is None else writes}


def test_ps4_const_args():
    win = [_w("mov", _reg("rdi"), _imm(5)), _w("mov", _reg("rsi"), _imm(0x46)),
           _w("xor", _reg("rdx"), _reg("rdx")), _w("mov", _reg("r8", 8), _imm(0xFFFFFFFFFFFFFFFF, 8)),
           _w("mov", _reg("r9"), _imm(0xFFFFFFFF)), _w("mov", _reg("rax"), _imm(3))]
    assert ex.ps4_const_args(win) == {"rdi": 5, "rsi": 0x46, "rdx": 0, "r8": 0xFFFFFFFFFFFFFFFF, "r9": 0xFFFFFFFF}


def test_ps4_register_overwritten_before_the_call():
    win = [_w("mov", _reg("rsi"), _imm(7)), _w("mov", _reg("rsi"), _reg("rax")),
           _w("mov", _reg("rdi"), _imm(5)), _w("lea", _reg("rdi", 8), _displ("rsp", 0x20, 8)),
           _w("mov", _reg("rcx"), _imm(1)), _w("mov", _reg("rcx", 2), _imm(2, 2)),  # partial write last
           _w("mov", _reg("rdx"), _imm(4)), {"mnem": "stos", "ops": [], "writes": ["rdi", "rcx", "rdx"]}]
    assert ex.ps4_const_args(win) == {}


# --- codec shapes (T005b § 2.1/2.2 VA tables as the oracle) -------------------------------------------

def _pc_reader(n, swap=(), load=None, call=False, advance=None, ret=None, cursor=0x0C):
    advance = n if advance is None else advance
    ret = n if ret is None else ret
    body = [_ins("mov", _reg("rsi"), _reg("rcx")), _ins("mov", _reg("rcx"), _displ("rsi", 0x0C)),
            _ins("lea", _reg("rax"), _displ("rcx", n)), _ins("cmp", _reg("rax"), _displ("rsi", 0x10)),
            _ins("ja", {"type": "near", "addr": 0x99}),
            _ins(load[0], _reg("rax"), _phrase("rcx", load[1])) if load else _ins("mov", _reg("rax"), _phrase("rcx")),
            *swap]
    if call:
        body += [_push("rdx"), _push("rax"), _ins("call", {"type": "near", "addr": 0x8BC340})]
    body += [_ins("mov", _reg("rdx"), _displ("rsp", 8)), _ins("mov", _phrase("rdx"), _reg("rax")),
             _ins("inc", _displ("rsi", cursor)) if advance == 1 else _ins("add", _displ("rsi", cursor), _imm(advance)),
             _ins("mov", _reg("rax"), _imm(ret)), _ins("retn"), _ins("xor", _reg("rax"), _reg("rax")), _ins("retn")]
    return body


def _pc_writer(n, swap=(), cursor=0x10):
    return [_ins("mov", _reg("rax"), _displ("rsi", 0x14)), _ins("sub", _reg("rax"), _displ("rsi", 0x10)),
            _ins("cmp", _reg("rax"), _imm(n)), _ins("jb", {"type": "near", "addr": 0x99}),
            _ins("mov", _reg("rcx"), _displ("rsi", 0x10)), *swap, _ins("mov", _phrase("rcx"), _reg("rdx")),
            _ins("inc", _displ("rsi", cursor)) if n == 1 else _ins("add", _displ("rsi", cursor), _imm(n)),
            _ins("mov", _reg("rax"), _imm(n)), _ins("retn")]


_SWAP16 = (_ins("shr", _reg("rdx"), _imm(8)), _ins("shl", _reg("rax"), _imm(8)), _ins("xor", _reg("rax"), _reg("rdx")))
_SWAP32 = (_ins("and", _reg("rdx"), _imm(0xFF00)), _ins("shl", _reg("rdx"), _imm(0x10)),
           _ins("shr", _reg("rax"), _imm(0x18)))

# va -> (body, dir, width, swap evidence)
PC_ORACLE = {
    0x8BC410: (_pc_reader(1, load=("movzx", 1)), "read", 1, None),  # Read_u8
    0x8BC6E0: (_pc_reader(1, load=("movzx", 1)), "read", 1, None),  # Read_bool, byte-identical
    0x8BC440: (_pc_reader(2, _SWAP16, ("movzx", 2)), "read", 2, "shift"),  # Read_u16
    0x8BC480: (_pc_reader(4, _SWAP32), "read", 4, "shift"),  # Read_s32 (= u32, f32 bodies)
    0x8BC4D0: (_pc_reader(4, _SWAP32), "read", 4, "shift"),
    0x8BC520: (_pc_reader(4, _SWAP32), "read", 4, "shift"),
    0x8BC660: (_pc_reader(8, call=True), "read", 8, "call"),  # Read_s64 (swap in 0x8BC340)
    0x8BC6A0: (_pc_reader(8, call=True), "read", 8, "call"),  # Read_u64
    0x8BC860: (_pc_writer(1), "write", 1, None),
    0x8BC890: (_pc_writer(2, _SWAP16), "write", 2, "shift"),
    0x8BC920: (_pc_writer(4, _SWAP32), "write", 4, "shift"),
}


@pytest.mark.parametrize("va", sorted(PC_ORACLE))
def test_pc_codec_oracle(va):
    body, direction, width, swap = PC_ORACLE[va]
    c = ex.classify_codec(body, ex.PC_CURSOR_DISP, ret_width=True)
    assert c is not None and (c["dir"], c["width"], c["evidence"]["swap"]) == (direction, width, swap)
    assert c["evidence"]["advance"] == c["evidence"]["bounds"] == c["evidence"]["ret"] == width


def _ps4_reader(n, cursor=0x18, ret=1):
    load = _ins("movbe", _reg("rax"), _phrase("rcx", n)) if n == 4 else _ins("movzx", _reg("rax"), _phrase("rcx", n))
    return [_ins("mov", _reg("rcx", 8), _displ("rdi", cursor, 8)), _ins("lea", _reg("rax", 8), _displ("rcx", n, 8)),
            _ins("cmp", _reg("rax", 8), _displ("rdi", cursor + 8, 8)), _ins("ja", {"type": "near", "addr": 0x99}),
            load, _ins("mov", _phrase("rsi"), _reg("rax")), _ins("add", _displ("rdi", cursor, 8), _imm(n)),
            _ins("mov", _reg("rax"), _imm(ret)), _ins("retn")]


@pytest.mark.parametrize(("va", "n", "swap"), [(0x3B6140, 1, None), (0x3B6190, 4, "movbe"), (0x3B6280, 4, "movbe")])
def test_ps4_codec_oracle(va, n, swap):
    # nPacket::Read_u8 / Read_u32 / Read_s32 (movbe, same instructions); no cursor offset or return
    # convention is assumed on PS4
    c = ex.classify_codec(_ps4_reader(n))
    assert c is not None and (c["dir"], c["width"], c["evidence"]["swap"]) == ("read", n, swap)


@pytest.mark.parametrize(
    "body",
    [_pc_reader(4, _SWAP32, advance=2),  # look-alike: bounds and return say 4, the cursor advances 2
     _pc_reader(2, _SWAP16, ret=4),  # return width disagrees (PC returns the width)
     _pc_reader(4, cursor=0x10),  # read shape advancing the writer field
     _pc_writer(4, cursor=0x0C),  # write shape advancing the reader field
     _pc_reader(4) + [_ins("add", _displ("rsi", 0x20), _imm(4))],  # two advances
     [i for i in _pc_reader(4) if i["mnem"] != "lea"],  # no bounds check
     _pc_reader(4) * 5],  # too long for a codec
)
def test_codec_near_misses_refused(body):
    assert ex.classify_codec(body, ex.PC_CURSOR_DISP, ret_width=True) is None


def test_codec_look_alike_refused_without_pc_rules_too():
    assert ex.classify_codec(_ps4_reader(4)[:6] + [_ins("add", _displ("rdi", 0x18, 8), _imm(2))]) is None


# --- extern call targets ------------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("target", "start", "imp", "cls", "reason"),
    [(0x10, 0x10, {"module": "KERNEL32", "name": "Sleep"}, "CODE", "import"),
     (0x10, None, None, "XTRN", "extern_segment"),
     (0x500, 0x500, None, "CODE", None),  # has a function record
     (0x758810, None, None, "CODE", "not_function"),  # T005b: loc_75880E+2
     (0x758810, 0x75880E, None, "CODE", "inside_function"),
     (0x900, 0x900, None, "CODE", "out_of_scope")],
)
def test_extern_reason(target, start, imp, cls, reason):
    assert ex.extern_reason(target, start, {0x500}, imp, cls) == reason
