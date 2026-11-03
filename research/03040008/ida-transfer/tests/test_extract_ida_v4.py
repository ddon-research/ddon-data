"""extract_ida.py v4 (T005f): object-relative accesses, requester roots, codec-path depth; fakes, no IDA."""

from __future__ import annotations

import pytest

import extract_ida as ex

_EA = [0x1000]


def _i(mnem, *ops, writes=(), call=False, pops=None):
    _EA[0] += 4
    return {"ea": _EA[0], "mnem": mnem, "ops": list(ops), "writes": list(writes), "call": call, "pops": pops}


def r(name, size=4):
    return {"type": "reg", "reg": name, "size": size}


def imm(v, size=4):
    return {"type": "imm", "value": v, "size": size}


def m(base, disp=0, size=4, chg=False, use=True, index=None, scale=None):
    return {"type": "displ" if disp else "phrase", "base": base, "reg": base, "addr": disp, "size": size,
            "chg": chg, "use": use, "index": index, "scale": scale}


def st(base, disp=0, size=4, **kw):
    return m(base, disp, size, chg=True, use=False, **kw)


def mov(dst, src):
    w = [dst["reg"]] if dst["type"] == "reg" else []
    return _i("mov", dst, src, writes=w)


def call(pops=None):
    return _i("call", {"type": "near", "addr": 0x9000, "size": 0}, call=True, pops=pops)


def run(insns, side="pc"):
    return ex.object_accesses([(0, insns)], {0: []}, 0, side)


def key(a):
    return (a["arg_loc"], a["arg"], a["disp"], a["access"])


# --- PC object accesses ---------------------------------------------------------------------------

def test_pc_this_store_immediate_and_load():
    acc = run([mov(st("rcx", 0x0C), imm(5)), mov(r("rax"), m("rcx", 0x10))])
    assert acc[0] == {"va": acc[0]["va"], "op": 0, "arg_loc": "ecx", "arg": 0, "disp": 0x0C, "width": 4,
                      "access": "store", "value": 5}
    assert key(acc[1]) == ("ecx", 0, 0x10, "load")


def test_store_immediate_masked_to_width():
    acc = run([mov(st("rcx", 4, size=1), imm(0x1FF))])
    assert acc[0]["value"] == 0xFF and acc[0]["width"] == 1


def test_callee_saved_copy_survives_call_caller_saved_does_not():
    acc = run([mov(r("rsi"), r("rcx")), mov(r("rax"), r("rcx")), call(0),
               mov(r("rdx"), m("rsi", 8)), mov(r("rdx"), m("rax", 12)), mov(r("rdx"), m("rcx", 16))])
    assert [key(a) for a in acc] == [("ecx", 0, 8, "load")]


def test_overwrite_ends_tracking_and_field_pointer():
    acc = run([mov(r("rcx"), m("rcx", 0x13C)), mov(st("rcx", 4), imm(1)),
               mov(r("rcx"), r("rdx")), mov(st("rcx", 0), imm(0))])
    assert [key(a) for a in acc] == [("ecx", 0, 0x13C, "load"), ("ecx", 0, 4, "store")]
    assert "via" not in acc[0] and acc[1]["via"] == 0x13C


def test_narrow_write_kills_register():
    acc = run([_i("mov", r("cl", 1), imm(1), writes=["rcx"]), mov(st("rcx", 4), imm(1))])
    assert acc == []


def test_field_of_field_is_not_tracked():
    acc = run([mov(r("rax"), m("rcx", 4)), mov(r("rax"), m("rax", 8)), mov(st("rax", 12), imm(1))])
    assert [(key(a), a.get("via")) for a in acc] == [(("ecx", 0, 4, "load"), None), (("ecx", 0, 8, "load"), 4)]


def test_stack_argument_ebp_frame():
    acc = run([_i("push", r("rbp")), mov(r("rbp"), r("rsp")), mov(r("rax"), m("rbp", 8)),
               mov(r("rdx"), m("rbp", 0x0C)), mov(st("rax", 4), imm(0)), mov(st("rdx", 0), imm(7))])
    assert [key(a) for a in acc] == [("stack", 0, 4, "store"), ("stack", 1, 0, "store")]


def test_stack_argument_frameless_after_push_and_known_call():
    acc = run([_i("push", r("rsi")), mov(r("rsi"), m("rsp", 8)),  # esp = entry-4: [esp+8] = slot 0
               _i("push", imm(1)), call(pops=4), mov(r("rax"), m("rsp", 0x0C)),  # back to entry-4: slot 1
               mov(st("rsi", 4), imm(0)), mov(st("rax", 8), imm(0))])
    assert [key(a) for a in acc] == [("stack", 0, 4, "store"), ("stack", 1, 8, "store")]


def test_unknown_call_pops_drops_stack_picture():
    acc = run([_i("push", imm(1)), call(pops=None), mov(r("rax"), m("rsp", 8)), mov(st("rax", 4), imm(0))])
    assert acc == []


def test_return_address_and_locals_are_not_arguments():
    acc = run([_i("sub", r("rsp"), imm(8), writes=["rsp"]), mov(r("rax"), m("rsp", 8)),  # [esp+8] = entry+0
               mov(st("rax", 4), imm(0)), mov(r("rdx"), m("rsp", 4)), mov(st("rdx", 4), imm(0))])
    assert acc == []


def test_stored_argument_slot_is_not_an_argument_any_more():
    acc = run([mov(st("rsp", 4), r("rcx")), mov(r("rax"), m("rsp", 4)), mov(st("rax", 0), imm(1)),
               mov(r("rdx"), m("rsp", 8)), mov(st("rdx", 0), imm(1))])
    assert [key(a) for a in acc] == [("stack", 1, 0, "store")]


def test_leaked_argument_area_and_unknown_esp_store_dirty_all():
    leak = run([_i("lea", r("rax"), m("rsp", 4, use=False), writes=["rax"]), call(pops=0),
                mov(r("rdx"), m("rsp", 8)), mov(st("rdx", 0), imm(1))])
    assert leak == []
    frame = [_i("push", r("rbp")), mov(r("rbp"), r("rsp")), _i("and", r("rsp"), imm(0xFFFFFFF0), writes=["rsp"])]
    tail = [mov(r("rdx"), m("rbp", 8)), mov(st("rdx", 0), imm(1))]
    assert [key(a) for a in run(frame + tail)] == [("stack", 0, 0, "store")]  # control: ebp frame survives
    assert run(frame + [mov(st("rsp", 0x20), r("rax"))] + tail) == []  # store at an unknown esp offset


def test_indexed_rmw_and_lea():
    acc = run([mov(st("rcx", 0xB9C, index="rax", scale=4), r("rdx")),
               _i("add", m("rcx", 4, chg=True, use=True), imm(1)),
               _i("lea", r("rax"), m("rcx", 0x10, use=False), writes=["rax"])])
    assert acc[0]["indexed"] and acc[0]["scale"] == 4 and acc[0]["index"] == "rax" and acc[0]["disp"] == 0xB9C
    assert acc[1]["access"] == "store" and acc[1]["rmw"] is True and "value" not in acc[1]
    assert acc[2]["access"] == "lea" and acc[2]["width"] is None


def test_blocks_merge_only_when_every_predecessor_agrees():
    a = [_i("test", r("rdx"), r("rdx"))]
    b = [mov(r("rsi"), r("rcx"))]
    c = [mov(st("rsi", 4), imm(0))]
    blocks = [(0, a), (1, b), (2, c)]
    assert ex.object_accesses(blocks, {0: [], 1: [0], 2: [0, 1]}, 0, "pc") == []
    a2 = [mov(r("rsi"), r("rcx")), _i("test", r("rdx"), r("rdx"))]
    acc = ex.object_accesses([(0, a2), (1, [mov(r("rsi"), r("rcx"))]), (2, c)], {0: [], 1: [0], 2: [0, 1]}, 0, "pc")
    assert [key(x) for x in acc] == [("ecx", 0, 4, "store")]


def test_loop_back_edge_fixed_point():
    head = [mov(r("rsi"), r("rcx"))]
    body = [mov(st("rsi", 4), imm(0)), _i("dec", r("rdx"), writes=["rdx"])]
    acc = ex.object_accesses([(0, head), (1, body)], {0: [], 1: [0, 1]}, 0, "pc")
    assert [key(x) for x in acc] == [("ecx", 0, 4, "store")]
    body2 = [mov(st("rsi", 4), imm(0)), mov(r("rsi"), m("rsi", 0))]  # the back edge changes esi
    acc2 = ex.object_accesses([(0, head), (1, body2)], {0: [], 1: [0, 1]}, 0, "pc")
    assert acc2 == []


def test_unreached_block_records_nothing():
    acc = ex.object_accesses([(0, [_i("retn")]), (1, [mov(st("rcx", 4), imm(0))])], {0: [], 1: []}, 0, "pc")
    assert acc == []


# --- PS4 object accesses --------------------------------------------------------------------------

def test_ps4_manager_field_error_code_store():
    # this->mpManager->mErrorCode[171] = errNo; mStatus[idx] with a variable index
    acc = run([mov(r("rax", 8), m("rdi", 0x40, size=8)), mov(st("rax", 0xBA0), r("rcx")),
               mov(st("rax", 0x10, index="rdx", scale=4), imm(4)), mov(st("rsi", 8), imm(2))], side="ps4")
    assert [(key(a), a.get("via"), a.get("indexed")) for a in acc] == [
        (("rdi", 0, 0x40, "load"), None, None), (("rdi", 0, 0xBA0, "store"), 0x40, None),
        (("rdi", 0, 0x10, "store"), 0x40, True), (("rsi", 1, 8, "store"), None, None)]
    assert acc[2]["value"] == 4


def test_ps4_truncating_copy_and_call_clobber():
    acc = run([_i("mov", r("eax"), r("edi"), writes=["rax"]), mov(st("rax", 4, size=4), imm(0)),
               mov(r("rbx", 8), r("rdi", 8)), mov(r("r12", 8), r("rsi", 8)), call(),
               mov(st("rbx", 8), imm(0)), mov(st("rdi", 8), imm(0)), mov(st("r12", 0), imm(0))], side="ps4")
    assert [key(a) for a in acc] == [("rdi", 0, 8, "store"), ("rsi", 1, 0, "store")]


def test_ps4_has_no_stack_arguments():
    acc = run([mov(r("rax", 8), m("rsp", 8, size=8)), mov(st("rax", 0), imm(0))], side="ps4")
    assert acc == []


# --- slot facts: callOnPacketFunc immediate (v3 const_stack, T005b § 1.1 sequence) -----------------

def test_call_on_packet_slot_is_stack_slot_zero():
    window = [{"mnem": "push", "ops": [{"type": "imm", "value": 1}]},
              {"mnem": "push", "ops": [{"type": "reg", "reg": "rax"}]},
              {"mnem": "push", "ops": [{"type": "imm", "value": 0x1BC780C}]},
              {"mnem": "push", "ops": [{"type": "imm", "value": 0x1BC7800}]},
              {"mnem": "push", "ops": [{"type": "imm", "value": 91}]},
              {"mnem": "mov", "ops": [{"type": "reg", "reg": "rcx", "size": 4},
                                      {"type": "displ", "reg": "rsi", "addr": 0x13C, "size": 4}],
               "writes_ecx": True}]
    out = ex.pc_const_args(window, 0x14)
    assert out["stack"][0] == [0, 91] and [4, 1] in out["stack"]


# --- requester roots and the reserve function -----------------------------------------------------

def test_requester_roots():
    starts = {0x100: 0x100, 0x105: 0x100, 0x210: 0x200, 0xBB39D5: ex.PC_RESERVE_DIALOG}
    roots, orphans = ex.requester_roots([0x105, 0x210, 0x105, 0x999, 0xBB39D5], starts.get, ex.PC_RESERVE_DIALOG)
    assert roots == {0x100: "requester", 0x200: "requester"}
    assert orphans == [{"kind": "requester_site", "va": 0x999, "target": ex.PC_RESERVE_DIALOG,
                        "missing": "no-function"}]


def test_check_reserve_fails_closed():
    ex.check_reserve("pc", 0xBB39D0, 0xBB39D0, ex.RESERVE_DIALOG_NAME)
    ex.check_reserve("pc", 0xBB39D0, 0xBB39D0, "sub_BB39D0")
    ex.check_reserve("ps4", 0x7EDF80, 0x7EDF80, ex.RESERVE_DIALOG_NAME)
    with pytest.raises(ValueError):
        ex.check_reserve("pc", 0xBB39D0, 0xBB3900, ex.RESERVE_DIALOG_NAME)  # inside another function
    with pytest.raises(ValueError):
        ex.check_reserve("pc", 0xBB39D0, None, ex.RESERVE_DIALOG_NAME)
    with pytest.raises(ValueError):
        ex.check_reserve("pc", 0xBB39D0, 0xBB39D0, "sNetworkExt::requestNetworkErrorDialog")
    with pytest.raises(ValueError):
        ex.check_reserve("ps4", None, None, ex.RESERVE_DIALOG_NAME)  # no unique symbol
    with pytest.raises(ValueError):
        ex.check_reserve("ps4", 0x7EDF80, 0x7EDF80, "sub_7EDF80")


# --- codec path depth -----------------------------------------------------------------------------

GRAPH = {
    "R": ["A", "X"], "A": ["B"], "B": ["C"], "C": ["D"], "D": ["E", "N"], "E": ["K"], "N": ["M"],
    "X": ["Y"], "Y": ["Z"], "Z": ["W"], "W": [],
    "L": ["L1"], "L1": ["L2"], "L2": ["L3"], "L3": ["L4"], "L4": ["L5"], "L5": ["L6"], "L6": ["K"],
    "K": [], "M": [],
}


def _scope(**kw):
    return ex.codec_scope(kw, lambda v: GRAPH.get(v, []), lambda v: v == "K", 8)


def test_codec_scope_follows_reader_paths_and_their_direct_callees():
    added = _scope(R=0, A=1, X=1, B=2, Y=2, C=3, Z=3)
    assert added == {"D": 4, "E": 5, "N": 5, "K": 6}  # W (no codec below Z) and M (below N) stay out


def test_codec_scope_depth_bound():
    # L at depth 2: K is 7 calls below, 9 from the root: beyond depth 8
    assert _scope(L=2) == {}
    assert _scope(L=1) == {"L1": 2, "L2": 3, "L3": 4, "L4": 5, "L5": 6, "L6": 7, "K": 8}


def test_codec_distance_cycles_and_budget():
    g = {"a": ["b"], "b": ["a", "c"], "c": ["k"], "k": []}
    d = ex.codec_distance(lambda v: g[v], lambda v: v == "k")
    assert d("a", 8) == 3 and d("a", 2) is None and d("k", 0) == 0 and d("c", 0) is None
