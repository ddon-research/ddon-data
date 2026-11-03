"""extract_ida.py v6 (T013a): argument values per call site, MSVC padding nops; fakes, no IDA."""

from __future__ import annotations

import extract_ida as ex

_EA = [0x1000]
CODEC = 0x8BC4D0
ALLOC = 0x8BC2E0
GETTER = 0x7000


def _i(mnem, *ops, writes=(), call=False, pops=None):
    _EA[0] += 4
    return {"ea": _EA[0], "mnem": mnem, "ops": list(ops), "writes": list(writes), "call": call, "pops": pops}


def r(name, size=4):
    return {"type": "reg", "reg": name, "size": size}


def r8(name):
    return r(name, 8)


def imm(v, size=4):
    return {"type": "imm", "value": v, "size": size}


def m(base, disp=0, size=4, chg=False, use=True, index=None, scale=None):
    return {"type": "displ" if disp else "phrase", "base": base, "reg": base, "addr": disp, "size": size,
            "chg": chg, "use": use, "index": index, "scale": scale}


def mov(dst, src):
    return _i("mov", dst, src, writes=[dst["reg"]] if dst["type"] == "reg" else [])


def lea(dst, src):
    return _i("lea", dst, dict(src, use=False), writes=[dst["reg"]])


def push(op):
    return _i("push", op)


def call(target=CODEC, pops=0):
    return _i("call", {"type": "near", "addr": target, "size": 0}, call=True, pops=pops)


def icall(base, disp):
    return _i("call", m(base, disp), call=True)


def add(dst, src, mnem="add"):
    return _i(mnem, dst, src, writes=[dst["reg"]])


def args(blocks, side="pc", preds=None, arg_bytes=None, **kw):
    if isinstance(blocks[0], dict):
        blocks = [(0, blocks)]
    preds = preds or {b: [] for b, _ in blocks}
    return ex.call_argument_values(blocks, preds, blocks[0][0], side, arg_bytes, **kw)


def only(values, slot):
    hit = [a for recs in values.values() for a in recs if a["slot"] == slot]
    return hit[0] if hit else None


# --- PC ---------------------------------------------------------------------------------------------

def test_pc_codec_destination_is_this_plus_disp():
    le = lea(r("rax"), m("rsi", 0x18))
    c = call()
    v = args([mov(r("rsi"), r("rcx")), le, push(r("rax")), push(r("rdi")), c], arg_bytes={c["ea"]: 8})
    assert v[c["ea"]] == [{"slot": "ecx", "kind": "obj", "arg": 0, "arg_loc": "ecx", "disp": 0, "def": None},
                          {"slot": 1, "kind": "obj", "arg": 0, "arg_loc": "ecx", "disp": 0x18, "def": le["ea"]}]


def test_pc_no_stack_slot_without_arg_bytes():
    c = call()
    v = args([mov(r("rsi"), r("rcx")), lea(r("rax"), m("rsi", 0x18)), push(r("rax")), c], arg_bytes={c["ea"]: None})
    assert only(v, 0) is None


def test_pc_register_overwritten_between_lea_and_push():
    c = call()
    v = args([mov(r("rsi"), r("rcx")), lea(r("rax"), m("rsi", 0x18)), mov(r("rax"), m("rbx", 4)),
              push(r("rax")), push(r("rdi")), c], arg_bytes={c["ea"]: 8})
    assert only(v, 1) is None


def test_pc_push_of_register_loaded_from_memory():
    c = call()
    v = args([mov(r("rsi"), r("rcx")), mov(r("rax"), m("rsi", 4)), push(r("rax")), c], arg_bytes={c["ea"]: 4})
    assert only(v, 0) is None


def test_pc_lea_of_non_argument_base():
    c = call()
    v = args([lea(r("rax"), m("rbx", 8)), push(r("rax")), c], arg_bytes={c["ea"]: 4})
    assert only(v, 0) is None


def test_pc_padding_nop_is_no_operation():
    # lea ecx,[ecx+0] between the definition and the call: ecx stays `this` (def None), and no lea access
    c = call()
    v = args([lea(r("rcx"), m("rcx", 0)), c], arg_bytes={c["ea"]: 0})
    assert v[c["ea"]] == [{"slot": "ecx", "kind": "obj", "arg": 0, "arg_loc": "ecx", "disp": 0, "def": None}]
    acc = ex.object_accesses([(0, [mov(r("rsi"), r("rcx")), lea(r("rsi"), m("rsi", 0))])], {0: []}, 0, "pc")
    assert acc == []
    acc = ex.object_accesses([(0, [lea(r("rax"), m("rcx", 0))])], {0: []}, 0, "pc")
    assert [(a["access"], a["disp"]) for a in acc] == [("lea", 0)]  # another register: a real lea


def test_padding_nop_rule():
    assert ex.is_padding_nop({"mnem": "lea", "ops": [r("rsi"), m("rsi", 0)]})
    assert not ex.is_padding_nop({"mnem": "lea", "ops": [r("rsi"), m("rsi", 4)]})
    assert not ex.is_padding_nop({"mnem": "lea", "ops": [r("rsi"), m("rsi", 0, index="rax", scale=1)]})
    assert not ex.is_padding_nop({"mnem": "lea", "ops": [r("rsi"), m("rsi", 0)]}, ptr=8)  # lea esi,[rsi]


def test_pc_stack_argument_base_and_stack_local():
    le = lea(r("rax"), m("rsi", 4))
    sl = lea(r("rdx"), m("rsp", 0x10))
    c = call()
    v = args([_i("sub", r("rsp"), imm(0x20), writes=["rsp"]), mov(r("rsi"), m("rsp", 0x28)), le, sl,
              push(r("rdx")), push(r("rax")), c], arg_bytes={c["ea"]: 8})
    # [esp+0x28] after sub esp,0x20 = entry esp+8 = stack argument 1
    assert v[c["ea"]][1:] == [
        {"slot": 0, "kind": "obj", "arg": 1, "arg_loc": "stack", "disp": 4, "def": le["ea"]},
        {"slot": 1, "kind": "stack", "frame": -0x10, "def": sl["ea"]}]


def test_pc_mov_store_into_argument_area():
    c = call()
    v = args([_i("sub", r("rsp"), imm(8), writes=["rsp"]), mov(m("rsp", 4, chg=True, use=False), imm(7)),
              mov(m("rsp", 0, chg=True, use=False), r("rcx")), c], arg_bytes={c["ea"]: 8})
    assert v[c["ea"]][1:] == [{"slot": 0, "kind": "obj", "arg": 0, "arg_loc": "ecx", "disp": 0, "def": None},
                              {"slot": 1, "kind": "const", "value": 7}]


def test_pc_allocator_result_is_element():
    a = call(ALLOC)
    le = lea(r("rax"), m("rsi", 4))
    c = call()
    v = args([push(imm(0x10)), push(imm(0x40)), a, add(r("rsp"), imm(8)), mov(r("rsi"), r("rax")), le,
              push(r("rax")), push(r("rdi")), c], arg_bytes={a["ea"]: 8, c["ea"]: 8}, allocators=[ALLOC])
    assert v[a["ea"]][1:] == [{"slot": 0, "kind": "const", "value": 0x40}, {"slot": 1, "kind": "const", "value": 0x10}]
    assert only({c["ea"]: v[c["ea"]]}, 1) == {"slot": 1, "kind": "element", "from": "result", "site": a["ea"],
                                               "callee": ALLOC, "disp": 4, "def": le["ea"]}


def test_pc_other_call_result_is_no_element():
    a = call(0x5000)
    c = call()
    v = args([a, mov(r("rsi"), r("rax")), lea(r("rax"), m("rsi", 4)), push(r("rax")), c],
             arg_bytes={c["ea"]: 4}, allocators=[ALLOC])
    assert only({c["ea"]: v.get(c["ea"], [])}, 0) is None


def test_derived_values_stay_in_their_block():
    # this copy crosses blocks (must-analysis); the allocator result and the lea do not
    a = call(ALLOC)
    c1 = call()
    c2 = call()
    b0 = [mov(r("rsi"), r("rcx")), a, mov(r("rdi"), r("rax"))]
    b1 = [lea(r("rax"), m("rsi", 8)), push(r("rax")), c1]
    b2 = [lea(r("rax"), m("rdi", 8)), push(r("rax")), c2]
    v = args([(0, b0), (1, b1), (2, b2)], preds={0: [], 1: [0], 2: [1]},
             arg_bytes={c1["ea"]: 4, c2["ea"]: 4}, allocators=[ALLOC])
    assert only({c1["ea"]: v[c1["ea"]]}, 0)["disp"] == 8
    assert only({c2["ea"]: v.get(c2["ea"], [])}, 0) is None


# --- PS4 --------------------------------------------------------------------------------------------

def test_ps4_lea_through_callee_saved_copy_and_sub_negative():
    le = lea(r8("rsi"), m("r15", 0x20, size=8))
    c1 = call()
    sb = add(r8("rsi"), imm(0xFFFFFFFFFFFFFF80, 8), mnem="sub")
    c2 = call()
    v = args([mov(r8("r15"), r8("rdi")), mov(r8("rbx"), r8("rsi")), le, mov(r8("rdi"), r8("rbx")), c1,
              mov(r8("rsi"), r8("r15")), sb, c2], side="ps4")
    assert v[c1["ea"]] == [{"slot": "rdi", "kind": "obj", "arg": 1, "arg_loc": "rsi", "disp": 0, "def": None},
                           {"slot": "rsi", "kind": "obj", "arg": 0, "arg_loc": "rdi", "disp": 0x20,
                            "def": le["ea"]},
                           {"slot": "rdx", "kind": "obj", "arg": 2, "arg_loc": "rdx", "disp": 0, "def": None},
                           {"slot": "rcx", "kind": "obj", "arg": 3, "arg_loc": "rcx", "disp": 0, "def": None},
                           {"slot": "r8", "kind": "obj", "arg": 4, "arg_loc": "r8", "disp": 0, "def": None},
                           {"slot": "r9", "kind": "obj", "arg": 5, "arg_loc": "r9", "disp": 0, "def": None}]
    assert v[c2["ea"]] == [{"slot": "rsi", "kind": "obj", "arg": 0, "arg_loc": "rdi", "disp": 0x80, "def": sb["ea"]}]


def test_ps4_stack_local_through_rbp_and_constant():
    le = lea(r8("rsi"), m("rbp", -0x38, size=8))
    c = call()
    v = args([push(r8("rbp")), mov(r8("rbp"), r8("rsp")), add(r8("rsp"), imm(0x40), mnem="sub"),
              mov(r8("rdi"), m("rbx", 0, size=8)), le, mov(r("rdx"), imm(5)), _i("xor", r("rcx"), r("rcx"),
                                                                                 writes=["rcx"]), c], side="ps4")
    got = {a["slot"]: a for a in v[c["ea"]]}
    assert "rdi" not in got
    assert got["rsi"] == {"slot": "rsi", "kind": "stack", "frame": -0x40, "def": le["ea"]}
    assert got["rdx"] == {"slot": "rdx", "kind": "const", "value": 5}
    assert got["rcx"] == {"slot": "rcx", "kind": "const", "value": 0}


def test_ps4_element_from_array_data_index():
    le = lea(r8("rbx"), m("rax", 0, size=8, index="rcx", scale=8))
    l2 = lea(r8("rsi"), m("rbx", 8, size=8))
    c = call()
    v = args([mov(r8("rax"), m("rdi", 0x10, size=8)), le, l2, c], side="ps4")
    got = {a["slot"]: a for a in v[c["ea"]]}
    assert got["rsi"] == {"slot": "rsi", "kind": "element", "from": "index", "arg": 0, "arg_loc": "rdi",
                          "via": 0x10, "index": "rcx", "scale": 8, "index_def": le["ea"], "disp": 8,
                          "def": l2["ea"]}


def test_ps4_index_element_needs_a_field_base():
    c = call()
    v = args([mov(r8("rax"), m("rbx", 0x10, size=8)), lea(r8("rsi"), m("rax", 0, size=8, index="rcx", scale=8)),
              c], side="ps4")
    assert "rsi" not in {a["slot"] for a in v.get(c["ea"], [])}


def test_ps4_allocator_method_on_getter_result():
    g = call(GETTER)
    a = icall("rax", 0x18)
    le = lea(r8("rsi"), m("rbx", 4, size=8))
    c = call()
    v = args([g, mov(r8("rdi"), r8("rax")), mov(r8("rax"), m("rax", 0, size=8)), mov(r("rsi"), imm(0x40)), a,
              mov(r8("rbx"), r8("rax")), le, c], side="ps4", allocator_getters=[GETTER])
    got = {x["slot"]: x for x in v[c["ea"]]}
    assert got["rsi"] == {"slot": "rsi", "kind": "element", "from": "result", "site": a["ea"], "callee": "indirect",
                          "getter": GETTER, "disp": 4, "def": le["ea"]}
    # an indirect call on some other object's result is no allocation
    g2 = call(0x7100)
    a2 = icall("rax", 0x18)
    c2 = call()
    v2 = args([g2, mov(r8("rdi"), r8("rax")), mov(r8("rax"), m("rax", 0, size=8)), a2, mov(r8("rbx"), r8("rax")),
               lea(r8("rsi"), m("rbx", 4, size=8)), c2], side="ps4", allocator_getters=[GETTER])
    assert "rsi" not in {x["slot"] for x in v2.get(c2["ea"], [])}


def test_ps4_stack_argument_load_is_not_a_pc_slot():
    # mov rax,[rsp+8] on PS4 is no 4-byte PC stack argument
    c = call()
    v = args([mov(r8("rsi"), m("rsp", 8, size=8)), lea(r8("rsi"), m("rsi", 4, size=8)), c], side="ps4")
    assert "rsi" not in {a["slot"] for a in v.get(c["ea"], [])}


def test_ida_call_args_glue_attaches_args_and_allocators():
    from types import SimpleNamespace as NS

    g = call(GETTER)
    a = icall("rax", 0x18)
    le = lea(r8("rsi"), m("rbx", 4, size=8))
    c = call()
    blocks = [(0, [g, mov(r8("rdi"), r8("rax")), mov(r8("rax"), m("rax", 0, size=8)), a,
                   mov(r8("rbx"), r8("rax")), le, c])]
    calls = [{"site": g["ea"], "target": GETTER}, {"site": a["ea"], "target": "indirect"},
             {"site": c["ea"], "target": CODEC}]
    db = NS(side="ps4", demangled=lambda t: {GETTER: "MtMemoryAllocator::getAllocator"}.get(t, "nPacket::Read_u32"))
    ex._ida_call_args(db, NS(start_ea=0), blocks, {0: []}, calls)
    got = {x["slot"]: x for x in calls[2]["args"]}
    assert got["rsi"]["kind"] == "element" and got["rsi"]["getter"] == GETTER
    pc_db = NS(side="pc", demangled=lambda t: None)
    al = call(ALLOC)
    c2 = call()
    pcalls = [{"site": al["ea"], "target": ALLOC, "arg_bytes": 0}, {"site": c2["ea"], "target": CODEC, "arg_bytes": 4}]
    ex._ida_call_args(pc_db, NS(start_ea=0), [(0, [al, lea(r("rax"), m("rax", 8)), push(r("rax")), c2])], {0: []},
                      pcalls)
    assert pcalls[1]["args"][-1] == {"slot": 0, "kind": "element", "from": "result", "site": al["ea"],
                                     "callee": ALLOC, "disp": 8, "def": pcalls[1]["args"][-1]["def"]}
