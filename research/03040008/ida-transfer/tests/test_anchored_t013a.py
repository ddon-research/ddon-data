"""007 T013a: rule-3 codec sites as gap anchors (matcher.anchored), on synthetic facts."""

from __future__ import annotations

from matcher import anchored, checks, engine, propagate, roles
from matcher.model import Call, Facts, Func, Param

THIS = Param("this", "X*", None, True)
PKT = Param("pPacket", "CPacket*", None)
PC_R4, PC_R1 = 0x8BC4D0, 0x8BC410
P_U32, P_U8 = 0x3B6190, 0x3B6140


def pc(va, calls=(), *, strings=(), callers=1, codec=None):
    return Func(va=va, name=f"sub_{va:X}", side="pc", size=va % 997 + 40, instructions=20,
                calls=[Call(va + 1 + i, t, 4) for i, t in enumerate(calls)], strings=frozenset(strings),
                callers_count=callers, caller_sites=callers, ecx_read_before_write=True, ret_imm=(4,), codec=codec)


def ps4(va, calls=(), *, name=None, strings=(), callers=1):
    return Func(va=va, name=name or f"f_{va:X}", side="ps4", size=100, instructions=20,
                calls=[Call(va + 1 + i, t) for i, t in enumerate(calls)], strings=frozenset(strings),
                callers_count=callers, caller_sites=callers)


def world(pc_calls, ps4_calls, *, strings=("rom\\x",), extra_ps4=()):
    pcs = [pc(1, pc_calls), pc(9, strings=strings),
           pc(PC_R4, callers=500, codec=("read", 4)), pc(PC_R1, callers=500, codec=("read", 1))]
    ps4s = [ps4(101, ps4_calls), ps4(109, strings=strings),
            ps4(P_U32, name="nPacket::Read_u32", callers=500), ps4(P_U8, name="nPacket::Read_u8", callers=500),
            *extra_ps4]
    return Facts(pc={f.va: f for f in pcs}, ps4={f.va: f for f in ps4s}, table_callbacks=set(), table_group={},
                 dwarf_params={f.va: [THIS, PKT] for f in ps4s})


def test_codec_tokens_aligned_and_blocking():
    f = world([PC_R4, 9, PC_R1], [P_U32, 109, P_U8])
    pc_tok, ps4_tok = anchored.codec_tokens(f, {2: frozenset([102])})
    assert pc_tok[2] == ps4_tok[102] == -2  # PC site 2 (R4) aligned with PS4 site 102 (U32)
    assert pc_tok[4] < -(1 << 60) and ps4_tok[104] < -(1 << 60) and pc_tok[4] != ps4_tok[104]  # blockers


def test_gap_between_aligned_codec_sites_proposes():
    f = world([PC_R4, 9, PC_R1], [P_U32, 109, P_U8])
    p, s = f.pc[1], f.ps4[101]
    props, st = propagate.gap_proposals(p, s, {}, {})
    assert props == [] and st.even_other[3] == 1  # without codec anchors: a 3/3 gap, never split
    pc_tok, ps4_tok = anchored.codec_tokens(f, {2: frozenset([102]), 4: frozenset([104])})
    props, st = propagate.gap_proposals(p, s, {}, {}, None, pc_tok, ps4_tok)
    assert props == [(9, 109)] and st.even_one == 1


def test_unaligned_codec_call_blocks_its_gap():
    f = world([PC_R4, 9], [P_U32, 109, P_U8])  # PS4's u8 has no aligned PC site
    pc_tok, ps4_tok = anchored.codec_tokens(f, {2: frozenset([102])})
    props, st = propagate.gap_proposals(f.pc[1], f.ps4[101], {}, {}, None, pc_tok, ps4_tok)
    assert props == [] and st.blocked == 1


def test_run_accepts_under_gates_and_only_with_anchors():
    f = world([PC_R4, 9], [P_U32, 109])
    res = anchored.run(f, {(1, 101)}, {2: frozenset([102])})
    assert list(res.accepted) == [(9, 109)]
    ws, why, it = res.accepted[(9, 109)]
    assert ws == ((1, 101),) and why.startswith("a=") and why.endswith("d=ok") and it == 1
    assert anchored.run(f, {(1, 101)}, {}).accepted == {}  # codec calls unaligned: blocked
    # gate (a): one witness and no fingerprint
    f2 = world([PC_R4, 9], [P_U32, 109], strings=())
    r2 = anchored.run(f2, {(1, 101)}, {2: frozenset([102])})
    assert r2.accepted == {} and r2.failed[(9, 109)][0][0] == "a"


def test_run_conflict_rejects_both():
    # two parents propose 9 <-> 109 and 9 <-> 108
    f = world([PC_R4, 9], [P_U32, 109], extra_ps4=[ps4(200, [P_U32, 108]), ps4(108, strings=("rom\\x",))])
    f.pc[20] = pc(20, [PC_R4, 9])
    res = anchored.run(f, {(1, 101), (20, 200)}, {2: frozenset([102]), 21: frozenset([201])})
    assert res.accepted == {} and {(9, 109), (9, 108)} <= res.rejected_b


def test_codec_site_map_fails_closed():
    ctx = roles.Context(1, 101, True, frozenset(), "x")
    calls = [((10, 1, PC_R4, "4", "nPacket::Read_u32", 110, 101), ctx),
             ((11, 1, PC_R4, "4", "nPacket::Read_u32", 111, 101), ctx),
             ((11, 1, PC_R4, "4", "nPacket::Read_s32", 112, 101), ctx),  # 11: two overloads -> ambiguous
             ((12, 1, PC_R4, "4", "nPacket::Read_u32", 113, 101), ctx),
             ((13, 1, PC_R4, "4", "nPacket::Read_u32", 113, 101), ctx)]  # 113 aligned with 12 and 13
    assert roles.codec_site_map(calls) == {10: frozenset([110])}


def test_add_anchored_joins_role_pairs_with_roots():
    f = world([PC_R4, 9], [P_U32, 109])
    res = engine.run(f, {})
    res.accepted[(1, 101)] = engine.Accepted(1, 101, "seed", 0, (), "c=ok")
    rr = roles.RoleResult(codec_sites={2: frozenset([102])})
    checks.add_anchored(f, res, rr)
    rp = rr.pairs[(9, 109)]
    assert rp.rule == "anchored-gap" and rp.roots == frozenset([(1, 101)]) and rp.witnesses == ("0x1:0x65",)
    assert rr.proposals["anchored-gap"] == 1 and rr.anchored.accepted
