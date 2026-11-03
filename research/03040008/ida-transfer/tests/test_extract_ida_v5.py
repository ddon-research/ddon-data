"""extract_ida.py v5 (T005h): memory operands decoded from op_t (SIB/REX), not from operand text; fakes."""

from __future__ import annotations

from types import SimpleNamespace as NS

import pytest

import extract_ida as ex

PC_AUX = 0x1008  # aux_use32 | aux_natad
PS4_AUX = 0x1010  # aux_use64 | aux_natad
_NAMES64 = ("rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi") + tuple(f"r{n}" for n in range(8, 16))
_NAMES32 = ("eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi") + tuple(f"r{n}d" for n in range(8, 16))


def sib(scale_log2: int, index: int, base: int) -> int:
    return (scale_log2 << 6) | ((index & 7) << 3) | (base & 7)


# --- decode_mem (pure) ------------------------------------------------------------------------------

@pytest.mark.parametrize("optype,phrase,has_sib,sibv,rex,aux,mnem,want", [
    # [rdi+rax*4+2ACh]
    ("displ", 4, 1, sib(2, 0, 7), 0, PS4_AUX, "mov", (7, 0, 4)),
    # [esp+10h+var_8]: SIB with index 100b = no index
    ("displ", 4, 1, sib(0, 4, 4), 0, PC_AUX, "mov", (4, None, None)),
    # [ebp+arg_0], [ecx+cFoo.mBar], [this+cArcLoaderBase.mNum] (this = rdi): no SIB, base = phrase
    ("displ", 5, 0, 0, 0, PC_AUX, "mov", (5, None, None)),
    ("displ", 1, 0, 0, 0, PC_AUX, "mov", (1, None, None)),
    ("displ", 7, 0, 0, 0, PS4_AUX, "mov", (7, None, None)),
    # [eax+ecx]
    ("phrase", 4, 1, sib(0, 1, 0), 0, PC_AUX, "mov", (0, 1, 1)),
    # [r13+r9*8]: REX.B and REX.X extend base and index
    ("phrase", 4, 1, sib(3, 1, 5), 0x43, PS4_AUX, "mov", (13, 9, 8)),
    # [rsp+r12]: index 100b with REX.X is r12, not "no index" (near miss of the INDEX_NONE rule)
    ("phrase", 4, 1, sib(0, 4, 4), 0x42, PS4_AUX, "mov", (4, 12, 1)),
    # 32-bit code: REX bits do not exist (insnpref holds other prefixes)
    ("phrase", 4, 1, sib(3, 1, 5), 0x43, PC_AUX, "mov", (5, 1, 8)),
    # ds:dword_1BC780C[eax*4]: o_mem with SIB has an index, no base
    ("mem", 4, 1, sib(2, 0, 5), 0, PC_AUX, "mov", (None, 0, 4)),
    # cs:qword_123 / fs:[0]: o_mem without SIB: nothing
    ("mem", 0, 0, 0, 0, PS4_AUX, "mov", (None, None, None)),
    # 16-bit addressing (address-size prefix in 32-bit code, or 16-bit segment): fail closed
    ("displ", 7, 0, 0, 0, 0x0008, "mov", (None, None, None)),
    ("displ", 7, 0, 0, 0, 0x1000, "mov", (None, None, None)),
    # VSIB (gather/scatter): the SIB index is a vector register: fail closed
    ("displ", 4, 1, sib(2, 1, 7), 0, PS4_AUX, "vpgatherdd", (None, None, None)),
    ("displ", 4, 1, sib(2, 1, 7), 0, PS4_AUX, "vgatherdps", (None, None, None)),
])
def test_decode_mem(optype, phrase, has_sib, sibv, rex, aux, mnem, want):
    d = ex.decode_mem(optype, phrase, has_sib, sibv, rex, aux, mnem)
    assert (d["base"], d["index"], d["scale"]) == want


def test_signed():
    assert ex.signed(0xFFFFFFF8, 32) == -8 and ex.signed(8, 32) == 8 and ex.signed(2**64 - 1, 64) == -1


# --- a fake IDA: op_t / insn_t with real _Db methods -------------------------------------------------

O_VOID, O_REG, O_MEM, O_PHRASE, O_DISPL, O_IMM, O_FAR, O_NEAR = 0, 1, 2, 3, 4, 5, 6, 7
DT = {"byte": 0, "word": 1, "dword": 2, "qword": 7}
DT_SIZE = {0: 1, 1: 2, 2: 4, 7: 8}
CHG1, CHG2, USE1, USE2 = 0x4, 0x8, 0x100, 0x200


def op(type_, dtype="dword", reg=0, phrase=0, addr=0, value=0, has_sib=0, sibv=0):
    return NS(type=type_, dtype=DT[dtype], reg=reg, phrase=phrase, addr=addr, value=value,
              specflag1=has_sib, specflag2=sibv)


def ins(ea, mnem, ops, feat, aux, rex=0):
    full = list(ops) + [op(O_VOID)] * (8 - len(ops))
    return NS(ea=ea, mnem=mnem, ops=full, insnpref=rex, auxpref=aux, size=4,
              get_canon_feature=lambda: feat, get_canon_mnem=lambda: mnem)


def fake_db(side: str):
    bits = 32 if side == "pc" else 64

    def get_reg_name(n, size):
        return (_NAMES64 if size == 8 else _NAMES32)[n]

    def no_text(*_):
        raise AssertionError("operand text must not be read")

    ua = NS(o_void=O_VOID, o_reg=O_REG, o_mem=O_MEM, o_phrase=O_PHRASE, o_displ=O_DISPL, o_imm=O_IMM,
            o_near=O_NEAR, o_far=O_FAR, dt_dword=DT["dword"], dt_qword=DT["qword"],
            get_dtype_size=lambda dt: DT_SIZE.get(dt, -1))
    idp = NS(CF_CHG1=CHG1, CF_CHG2=CHG2, CF_USE1=USE1, CF_USE2=USE2, CF_USE3=0x400, get_reg_name=get_reg_name,
             is_call_insn=lambda i: i.mnem == "call")
    db = object.__new__(ex._Db)
    db.side, db.bits, db.ptr = side, bits, bits // 8
    db.m = {"ida_ua": ua, "ida_idp": idp, "idc": NS(print_operand=no_text, GetDisasm=no_text)}
    db.optype = {O_REG: "reg", O_MEM: "mem", O_PHRASE: "phrase", O_DISPL: "displ", O_IMM: "imm",
                 O_NEAR: "near", O_FAR: "far"}
    db.ret_values = lambda va: [8, 8]
    return db


def run(db, insns):
    return ex.object_accesses([(0, [db.v4_insn(i) for i in insns])], {0: []}, 0, db.side)


def test_v5_insn_decodes_sib_without_text():
    db = fake_db("pc")
    # mov [ecx+eax*4-8], 3
    store = ins(0x10, "mov", [op(O_DISPL, phrase=4, addr=0xFFFFFFF8, has_sib=1, sibv=sib(2, 0, 1)),
                              op(O_IMM, value=3)], CHG1 | USE2, PC_AUX)
    o = db.v4_insn(store)["ops"][0]
    assert (o["base"], o["index"], o["scale"], o["addr"], o["chg"], o["use"]) == ("rcx", "rax", 4, -8, True, False)
    c = db.v4_insn(ins(0x20, "call", [op(O_NEAR, addr=0x9000)], USE1, PC_AUX))
    assert c["call"] is True and c["pops"] == 8
    db.ret_values = lambda va: [0, 4]  # mixed ret immediates prove nothing
    assert db.v4_insn(ins(0x20, "call", [op(O_NEAR, addr=0x9000)], USE1, PC_AUX))["pops"] is None


def test_ps4_renamed_register_operand():
    """``mov r15, this; movzx r14d, [this+cArcLoaderBase.mNum]; mov [this+cArcLoaderBase.mNum], 0``
    (cArcLoaderBase::clear 0x241E0, T005g § 4): IDA prints the regvar name ``this`` for rdi; the
    decoded phrase is rdi (7) all the same, so both accesses are recorded (v4: none)."""
    db = fake_db("ps4")
    body = [
        ins(0x241EA, "mov", [op(O_REG, "qword", reg=15), op(O_REG, "qword", reg=7)], CHG1 | USE2, PS4_AUX),
        ins(0x24204, "movzx", [op(O_REG, "dword", reg=14), op(O_DISPL, "byte", phrase=7, addr=0x2C)],
            CHG1 | USE2, PS4_AUX),
        ins(0x24236, "mov", [op(O_DISPL, "byte", phrase=7, addr=0x2C), op(O_IMM, "byte", value=0)],
            CHG1 | USE2, PS4_AUX),
        # the same through the copy r15 (REX.B phrase 15)
        ins(0x24240, "mov", [op(O_DISPL, "dword", phrase=15, addr=0x30), op(O_IMM, value=1)],
            CHG1 | USE2, PS4_AUX, rex=0x41),
    ]
    got = [(r["va"], r["arg_loc"], r["disp"], r["width"], r["access"], r.get("value")) for r in run(db, body)]
    assert got == [(0x24204, "rdi", 0x2C, 1, "load", None), (0x24236, "rdi", 0x2C, 1, "store", 0),
                   (0x24240, "rdi", 0x30, 4, "store", 1)]


def test_ps4_structure_offset_slot_store_via_mpmanager():
    """``mov rax, [rdi+cX.mpManager]; mov dword ptr [rax+cNetGameServer.mErrorCode+2ACh], 4``: a
    structure-offset operand is still o_displ with the numeric addr; the store carries via = 0x118."""
    db = fake_db("ps4")
    body = [
        ins(0x100, "mov", [op(O_REG, "qword", reg=0), op(O_DISPL, "qword", phrase=7, addr=0x118)],
            CHG1 | USE2, PS4_AUX),
        ins(0x104, "mov", [op(O_DISPL, "dword", phrase=0, addr=0x2AC), op(O_IMM, value=4)], CHG1 | USE2, PS4_AUX),
        # indexed through the same field pointer: [rax+rcx*4+10h]
        ins(0x108, "mov", [op(O_DISPL, "dword", phrase=4, addr=0x10, has_sib=1, sibv=sib(2, 1, 0)),
                           op(O_IMM, value=0)], CHG1 | USE2, PS4_AUX),
    ]
    recs = run(db, body)
    assert [(r["va"], r["disp"], r.get("via"), r.get("value"), r.get("index")) for r in recs] == [
        (0x100, 0x118, None, None, None), (0x104, 0x2AC, 0x118, 4, None), (0x108, 0x10, 0x118, 0, "rcx")]


def test_pc_records_unchanged_on_fixture():
    """PC ``sub_4169B0`` 0x4169B0 (T005g § 5 spot table): the v5 decoding gives the records of the v4
    PC dump (`dumps/pc-ida.jsonl`, sha256 4b307aee...), which the text parse produced."""
    db = fake_db("pc")
    a = PC_AUX
    body = [
        ins(0x4169B0, "push", [op(O_REG, reg=3)], USE1, a),
        ins(0x4169B1, "mov", [op(O_REG, reg=3), op(O_DISPL, phrase=4, addr=8, has_sib=1, sibv=sib(0, 4, 4))],
            CHG1 | USE2, a),  # mov ebx, [esp+4+arg_0]
        ins(0x4169B5, "mov", [op(O_REG, reg=7), op(O_REG, reg=1)], CHG1 | USE2, a),  # mov edi, ecx
        ins(0x4169BA, "mov", [op(O_REG, reg=2), op(O_DISPL, phrase=3, addr=4)], CHG1 | USE2, a),
        ins(0x4169C7, "mov", [op(O_DISPL, phrase=7, addr=0x8E0), op(O_REG, reg=2)], CHG1 | USE2, a),
        ins(0x4169D2, "mov", [op(O_REG, reg=1), op(O_DISPL, phrase=3, addr=0x10)], CHG1 | USE2, a),
        ins(0x4169D5, "mov", [op(O_REG, reg=6), op(O_PHRASE, phrase=4, has_sib=1, sibv=sib(2, 0, 1))],
            CHG1 | USE2, a),  # mov esi, [ecx+eax*4]
        ins(0x4169E6, "lea", [op(O_REG, reg=2), op(O_PHRASE, phrase=4, has_sib=1, sibv=sib(2, 1, 7))],
            CHG1 | USE2, a),  # lea edx, [edi+ecx*4]
        ins(0x416A07, "cmp", [op(O_REG, reg=0), op(O_DISPL, phrase=7, addr=0x8E0)], USE1 | USE2, a),
    ]
    want = [
        {"access": "load", "arg": 0, "arg_loc": "stack", "disp": 4, "op": 1, "va": 4286906, "width": 4},
        {"access": "store", "arg": 0, "arg_loc": "ecx", "disp": 2272, "op": 0, "va": 4286919, "width": 4},
        {"access": "load", "arg": 0, "arg_loc": "stack", "disp": 16, "op": 1, "va": 4286930, "width": 4},
        {"access": "load", "arg": 0, "arg_loc": "stack", "disp": 0, "index": "rax", "indexed": True, "op": 1,
         "scale": 4, "va": 4286933, "via": 16, "width": 4},
        {"access": "lea", "arg": 0, "arg_loc": "ecx", "disp": 0, "index": "rcx", "indexed": True, "op": 1,
         "scale": 4, "va": 4286950, "width": None},
        {"access": "load", "arg": 0, "arg_loc": "ecx", "disp": 2272, "op": 1, "va": 4286983, "width": 4},
    ]
    assert run(db, body) == want


def test_reads_reg_uses_decoded_registers():
    db = fake_db("ps4")
    # mov eax, [this+8] with this = rcx (renamed): reads rcx; [rdi+rcx*2] reads rcx through the index
    a = ins(0x10, "mov", [op(O_REG, reg=0), op(O_DISPL, phrase=1, addr=8)], CHG1 | USE2, PS4_AUX)
    b = ins(0x14, "mov", [op(O_REG, reg=0), op(O_PHRASE, phrase=4, has_sib=1, sibv=sib(1, 1, 7))],
            CHG1 | USE2, PS4_AUX)
    c = ins(0x18, "mov", [op(O_REG, reg=0), op(O_DISPL, phrase=7, addr=8)], CHG1 | USE2, PS4_AUX)
    assert [db.reads_reg(i, db.ops(i), "rcx") for i in (a, b, c)] == [True, True, False]
