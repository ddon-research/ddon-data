"""007 T005 matcher: one test group per rule and gate, on synthetic facts (no dumps needed)."""

from __future__ import annotations

import hashlib
import json

import pytest

from matcher import checks, engine, gates, propagate, tier0
from matcher.model import Call, DumpIdentityError, DwarfType, Facts, Func, Param, read_manifest, verify_dump

GAME = "cSeedGameSvConnection::"
THIS = Param("this", "X*", None, True)
PKT = Param("pPacket", "CPacket*", None)


def pc(va, calls=(), *, strings=(), ins=20, callers=0, ecx=True, ret=(4,), size=None, consts=()):
    return Func(va=va, name=f"sub_{va:X}", side="pc", size=size or va % 997 + 40, instructions=ins,
                calls=[Call(va + 1 + i, t, 4) for i, t in enumerate(calls)], strings=frozenset(strings),
                constants=frozenset(consts), callers_count=callers, caller_sites=callers,
                ecx_read_before_write=ecx, ret_imm=tuple(ret))


def ps4(va, calls=(), *, name=None, strings=(), ins=20, callers=0, consts=()):
    return Func(va=va, name=name or f"f_{va:X}", side="ps4", size=100, instructions=ins,
                calls=[Call(va + 1 + i, t) for i, t in enumerate(calls)], strings=frozenset(strings),
                constants=frozenset(consts), callers_count=callers, caller_sites=callers)


def facts(pcs, ps4s, *, callbacks=(), group=None, params=None, inlines=None, types=None, orphan=()):
    pcd = {f.va: f for f in pcs}
    psd = {f.va: f for f in ps4s}
    prm = {f.va: [THIS, PKT] for f in ps4s}
    prm.update(params or {})
    return Facts(pc=pcd, ps4=psd, table_callbacks=set(callbacks), table_group=group or {c: 1 for c in callbacks},
                 onpacket_orphan_strings=set(orphan), dwarf_params=prm, dwarf_inlines=inlines or {},
                 types=types or {})


# --- rule 1: tier 0 -------------------------------------------------------------------------------

def test_tier0_names_and_lists():
    f = facts([pc(0x10, strings=[GAME + "OnPacket_A_X_RES"]),
               pc(0x20, strings=[GAME + "OnPacket_A_Y_RES", GAME + "OnPacket_A_Z_RES"]),
               pc(0x30, strings=[GAME + "OnPacket_A_W_RES"]), pc(0x31, strings=[GAME + "OnPacket_A_W_RES"]),
               pc(0x40, strings=[GAME + "OnPacket_A_V_RES"]),
               pc(0x50, strings=[GAME + "OnPacket_A_U_RES"]), pc(0x60, strings=["%d"])],
              [], callbacks=[0x10, 0x20, 0x30, 0x40, 0x60, 0x70], orphan=[GAME + "OnPacket_A_V_RES"])
    named, listed = tier0.tier0(f)
    assert named == {0x10: GAME + "OnPacket_A_X_RES"}
    why = {x.candidate: x.detail for x in listed}
    assert "several" in why["pc:0x20"]
    assert "shared string" in why["pc:0x30"] and "0x31" in why["pc:0x30"]
    assert "outside any function" in why["pc:0x40"]
    assert "no OnPacket_" in why["pc:0x60"]
    assert "no function record" in why["pc:0x70"]
    assert "outside a callback" in why[f"string:{GAME}OnPacket_A_U_RES"]


# --- rule 2: seeds --------------------------------------------------------------------------------

def _seed_facts(ps4_names):
    pcs = [pc(0x10, strings=[GAME + "OnPacket_PAWN_LOST_PAWN_POINT_REVIVE_RES"]),
           pc(0x20, strings=[GAME + "OnPacket_PAWN_GET_X_RES"])]
    ps4s = [ps4(0x1000 + i, name=n) for i, n in enumerate(ps4_names)]
    return facts(pcs, ps4s, callbacks=[0x10, 0x20])


def test_seed_group_prefix_decides():
    f = _seed_facts([GAME + "OnPacket_S2C_LOST_PAWN_POINT_REVIVE_RES", GAME + "OnPacket_S2C_PAWN_POINT_REVIVE_RES",
                     GAME + "OnPacket_S2C_GET_X_RES"])
    named, _ = tier0.tier0(f)
    seeds, listed = tier0.seed_candidates(f, named)
    assert seeds == {0x10: 0x1000, 0x20: 0x1002}
    assert listed == []


def test_seed_several_candidates_listed():
    f = _seed_facts([GAME + "OnPacket_S2C_GET_X_RES", "cSeedLoginSvConnection::OnPacket_L2C_GET_X_RES"])
    named, _ = tier0.tier0(f)
    seeds, listed = tier0.seed_candidates(f, named)
    assert 0x20 not in seeds
    assert any("several PS4" in x.detail for x in listed)


def test_seed_other_connection_class_refused():
    """Reproduces the first full run's wrong seed: game BAZAAR_GET_CHARACTER_LIST_RES took the login
    L2C_GET_CHARACTER_LIST_RES (006 cross-check disagreement)."""
    f = facts([pc(0x10, strings=[GAME + "OnPacket_BAZAAR_GET_CHARACTER_LIST_RES"]),
               pc(0x11, strings=[GAME + "OnPacket_BAZAAR_GET_ITEM_RES"])],
              [ps4(0x1000, name="cSeedLoginSvConnection::OnPacket_L2C_GET_CHARACTER_LIST_RES")],
              callbacks=[0x10, 0x11])
    named, _ = tier0.tier0(f)
    seeds, listed = tier0.seed_candidates(f, named)
    assert seeds == {}
    assert any("another connection class" in x.detail for x in listed)


def test_seed_ps4_claimed_twice_listed():
    f = facts([pc(0x10, strings=[GAME + "OnPacket_A_X_RES"]), pc(0x20, strings=[GAME + "OnPacket_B_X_RES"])],
              [ps4(0x1000, name=GAME + "OnPacket_S2C_X_RES")], callbacks=[0x10, 0x20], group={0x10: 1, 0x20: 2})
    named, _ = tier0.tier0(f)
    seeds, listed = tier0.seed_candidates(f, named)
    assert seeds == {}
    assert sum("also the candidate" in x.detail for x in listed) == 2


def test_seed_needs_gate_c():
    f = facts([pc(0x10, strings=[GAME + "OnPacket_A_X_RES"], ret=(8,))],
              [ps4(0x1000, name=GAME + "OnPacket_S2C_X_RES")], callbacks=[0x10])
    res = engine.run(f, {0x10: 0x1000})
    assert res.accepted == {}
    assert "stack bytes" in res.seed_failed[(0x10, 0x1000)]


# --- rule 3: propagation --------------------------------------------------------------------------

def test_align_equal_and_unique_anchors():
    assert propagate.align([None, 1, None, 2], [1, None, 2]) == [(1, 0), (3, 2)]
    # 3 and 2 are unique on both sides and do not cross: they align; the 1s between differ in count
    assert propagate.align([3, 1, 1, 2], [3, 1, 2]) == [(0, 0), (3, 2)]
    # crossing unique anchors align nothing
    assert propagate.align([3, 2], [2, 3]) == []
    got = propagate.align([5, 1, 1, 7], [5, 1, 7])
    assert (0, 0) in got and (3, 2) in got and all(i not in (1, 2) for i, _ in got)


def test_gap_one_to_one_proposes():
    p, s = pc(0x100, [0xA, 0x10, 0xB]), ps4(0x1100, [0xAA, 0x1010, 0xBB, 0xCC])
    # 0x10 <-> 0x1010 already paired; gap before: 1/1 -> (A, AA); gap after: 1/2 -> nothing
    props, st = propagate.gap_proposals(p, s, {0x10: 0x10}, {0x1010: 0x10})
    assert props == [(0xA, 0xAA)]
    assert st.even_one == 1 and st.uneven[(1, 2)] == 1


def test_uneven_gap_and_no_raw_position():
    p, s = pc(0x100, [0xA, 0xB]), ps4(0x1100, [0xAA, 0xBB])
    props, st = propagate.gap_proposals(p, s, {}, {})
    assert props == []  # a 2/2 gap is never split by position
    assert st.even_other[2] == 1
    p, s = pc(0x100, [0xA, 0xB]), ps4(0x1100, [0xAA])
    props, st = propagate.gap_proposals(p, s, {}, {}, ps4_inlines=[0x1100 + 5])
    assert props == [] and st.uneven[(2, 1)] == 1 and st.uneven_by_inline == 1


def test_unaligned_anchor_blocks_gap():
    p, s = pc(0x100, [0xA, 0x10]), ps4(0x1100, [0xAA])
    props, st = propagate.gap_proposals(p, s, {0x10: 0x10}, {0x1010: 0x10})
    assert props == [] and st.blocked == 1


def test_indirect_calls_count_but_never_propose():
    p, s = pc(0x100, [None]), ps4(0x1100, [0xAA])
    props, st = propagate.gap_proposals(p, s, {}, {})
    assert props == [] and st.even_one == 1


# --- gates ----------------------------------------------------------------------------------------

def _two_witness_world(*, wrong_c=False, fold=False, ins=20, callers=1, strings=()):
    """Seeds (1,101) and (2,102) both call 9 <-> 109 as their only call."""
    pcs = [pc(1, [9]), pc(2, [9]), pc(9, ins=ins, callers=callers, ret=(0,) if wrong_c else (4,),
                                     strings=strings)]
    if fold:
        pcs.append(pc(8, ins=ins, callers=callers, size=pcs[2].size, strings=strings))
        pcs[-1].calls, pcs[-1].ret_imm = pcs[2].calls, pcs[2].ret_imm
    return facts(pcs, [ps4(101, [109]), ps4(102, [109]), ps4(109, ins=ins, callers=callers, strings=strings)])


def test_gate_a_two_witnesses_accept():
    res = engine.run(_two_witness_world(), {1: 101, 2: 102})
    a = res.accepted[(9, 109)]
    assert a.source == "propagation" and a.iteration == 1 and a.witnesses == ((1, 101), (2, 102))


def test_gate_a_one_witness_needs_fingerprint():
    f = facts([pc(1, [9]), pc(9, callers=1)], [ps4(101, [109]), ps4(109, callers=1)])
    res = engine.run(f, {1: 101})
    assert (9, 109) not in res.accepted and res.failed[(9, 109)] == [("a", "1 witness, no fingerprint")]
    f.pc[9].strings = f.ps4[109].strings = frozenset(["rom\\%s"])
    assert (9, 109) in engine.run(f, {1: 101}).accepted
    f.pc[9].strings = frozenset()
    f.pc[9].constants = f.ps4[109].constants = frozenset([0x10000, 0x20000])
    assert (9, 109) in engine.run(f, {1: 101}).accepted
    f.pc[9].constants = f.ps4[109].constants = frozenset([0x20000, 0xFFFF])
    assert (9, 109) not in engine.run(f, {1: 101}).accepted


def test_gate_c_blocks_propagation():
    res = engine.run(_two_witness_world(wrong_c=True), {1: 101, 2: 102})
    assert (9, 109) not in res.accepted
    assert res.failed[(9, 109)][0][0] == "c"


def test_gate_d_folded_trivial_shared():
    res = engine.run(_two_witness_world(fold=True), {1: 101, 2: 102})
    assert dict(res.failed[(9, 109)])["d"].startswith("pc folded: code-identical to 0x8")
    res = engine.run(_two_witness_world(ins=7), {1: 101, 2: 102})
    assert "7 instructions" in dict(res.failed[(9, 109)])["d"]
    res = engine.run(_two_witness_world(callers=65), {1: 101, 2: 102})
    assert "65 callers" in dict(res.failed[(9, 109)])["d"]
    assert engine.run(_two_witness_world(callers=64), {1: 101, 2: 102}).accepted.get((9, 109))


def test_gate_b_conflict_rejects_all_and_stays():
    # (1,101) proposes 9<->109 and (2,102) proposes 9<->108: both rejected, even though (3,103) adds a
    # second witness for 9<->109.
    f = facts([pc(1, [9]), pc(2, [9]), pc(3, [9]), pc(9, callers=3)],
              [ps4(101, [109]), ps4(102, [108]), ps4(103, [109]), ps4(109, callers=2), ps4(108, callers=1)])
    res = engine.run(f, {1: 101, 2: 102, 3: 103})
    assert (9, 109) not in res.accepted and (9, 108) not in res.accepted
    assert res.conflicts[("pc", 9)] == {(9, 109), (9, 108)}
    assert {(9, 109), (9, 108)} <= res.rejected_b


def test_gate_b_conflict_with_accepted_pair_restarts(monkeypatch):
    """With the real alignment a proposal never touches an already paired function (it is an anchor, so
    its gap is blocked); the restart path is defensive. Force one: (2,102) proposes 1<->999 against seed
    (1,101): both are rejected, the run restarts without the seed and keeps it rejected."""
    f = facts([pc(1), pc(2)], [ps4(101), ps4(102), ps4(999)])
    real = engine.gap_proposals

    def fake(p, s, *a, **k):
        props, st = real(p, s, *a, **k)
        return ([(1, 999)] if p.va == 2 else props), st

    monkeypatch.setattr(engine, "gap_proposals", fake)
    res = engine.run(f, {1: 101, 2: 102})
    assert res.restarts == 1
    assert (1, 101) not in res.accepted and (1, 101) in res.rejected_b
    assert res.conflicts[("pc", 1)] == {(1, 101), (1, 999)}


def test_proposal_never_touches_a_paired_function():
    p, s = pc(0x100, [0x10]), ps4(0x1100, [0x2222])
    props, st = propagate.gap_proposals(p, s, {0x10: 0x10}, {0x1010: 0x10})
    assert props == [] and st.blocked == 1


# --- gate (c) shape details -------------------------------------------------------------------------

def test_param_bytes():
    types = {1: DwarfType(1, "typedef", "MyId", None, 2, "u64"), 3: DwarfType(3, "enumeration", "E", 4),
             4: DwarfType(4, "class", "CData", 24), 5: DwarfType(5, "typedef", "PFn", None, None, "void (*)(int)")}
    pb = gates.param_bytes
    assert pb(Param("a", "u32", None), types) == 4
    assert pb(Param("a", "const u8", None), types) == 4
    assert pb(Param("a", "size_t", None), types) == 4
    assert pb(Param("a", "f64", None), types) == 8
    assert pb(Param("a", "MyId", 1), types) == 8
    assert pb(Param("a", "E", 3), types) == 4
    assert pb(Param("a", "CData", 4), types) is None  # by-value struct: 32-bit size unknown
    assert pb(Param("a", "PFn", 5), types) == 4
    assert pb(Param("a", "nQuest::SCHEDULE_ID", 99), types) is None
    assert pb(Param("a", "long", None), types) is None


def test_gate_c_cases():
    f = facts([pc(1, ret=(4,)), pc(2, ecx=False, ret=(4,)), pc(3, ret=()), pc(4, ret=(4, 8))],
              [ps4(101), ps4(102)], params={102: [Param("a", "CData", 4, False)]})
    assert gates.gate_c(f, 1, 101)[0]
    assert "this" in gates.gate_c(f, 2, 101)[1]
    assert gates.gate_c(f, 3, 101) == (False, "PC stack bytes unknown")  # no callers to read pushes from
    assert gates.gate_c(f, 4, 101) == (False, "PC stack bytes unknown")
    assert gates.gate_c(f, 1, 102) == (False, "DWARF parameter bytes unknown")
    del f.dwarf_params[101]
    assert gates.gate_c(f, 1, 101) == (False, "DWARF parameter bytes unknown")


def test_pc_stack_bytes_from_callers():
    callee = pc(9, ret=(), callers=2)
    f = facts([pc(1, [9]), pc(2, [9]), callee], [])
    assert gates.pc_stack_bytes(f, callee) == 4
    f.pc[2].calls = [Call(3, 9, 8)]
    f.pc_callsites.clear()
    f.__post_init__()
    assert gates.pc_stack_bytes(f, callee) is None  # callers disagree
    callee.caller_sites = 3
    f.pc[2].calls = [Call(3, 9, 4)]
    f.pc_callsites.clear()
    f.__post_init__()
    assert gates.pc_stack_bytes(f, callee) is None  # a caller site is outside the dump


# --- rule 5: precision (holdout) --------------------------------------------------------------------

def _holdout_world():
    """Seed T=(7,107) is called by three parents. Parent 1 calls 107 on PS4; parents 2 and 3 call the
    decoy 106 (two witnesses for the wrong pair 7<->106)."""
    pcs = [pc(1, [7]), pc(2, [7]), pc(3, [7]), pc(7, callers=3)]
    p4 = [ps4(101, [107]), ps4(102, [106]), ps4(103, [106]), ps4(107, callers=1),
          ps4(106, callers=2)]
    return facts(pcs, p4), {1: 101, 2: 102, 3: 103, 7: 107}


def test_holdout_correct_with_all_gates():
    f, seeds = _holdout_world()
    row = checks.precision_run(f, seeds, rng_seed=0, withheld={7})
    assert row.recovered_wrongly == 0


def test_holdout_mispairs_without_gate_b(monkeypatch):
    f, seeds = _holdout_world()
    monkeypatch.setattr(engine, "find_conflicts", lambda pairs: {})
    row = checks.precision_run(f, seeds, rng_seed=0, withheld={7})
    assert row.recovered_wrongly == 1


def test_holdout_mispairs_without_gate_c(monkeypatch):
    f, seeds = _holdout_world()
    # only the decoy is proposed; gate (c) refuses it (106 takes no packet argument)
    f.ps4[101].calls = [Call(102, 106)]
    f.dwarf_params[106] = [THIS]
    row = checks.precision_run(f, seeds, rng_seed=0, withheld={7})
    assert row.recovered_wrongly == 0
    monkeypatch.setattr(gates, "gate_c", lambda facts, a, b: (True, "off"))
    row = checks.precision_run(f, seeds, rng_seed=0, withheld={7})
    assert row.recovered_wrongly == 1


def test_holdout_sample_is_fixed():
    seeds = {i: i + 100 for i in range(50)}
    assert checks.holdout(seeds, 3) == checks.holdout(seeds, 3)
    assert len(checks.holdout(seeds, 3)) == 10
    assert checks.holdout(seeds, 3) != checks.holdout(seeds, 4)


# --- dump identity (fail closed) ---------------------------------------------------------------------

def test_verify_dump_refuses_changed_file(tmp_path):
    body = json.dumps({"kind": "header", "input_sha256": "src"}) + "\n"
    (tmp_path / "pc-ida.jsonl").write_text(body, encoding="utf-8", newline="\n")
    sha = hashlib.sha256(body.encode()).hexdigest()
    (tmp_path / "MANIFEST.tsv").write_text(f"file\tsha256\tsource_sha256\npc-ida.jsonl\t{sha}\tsrc\n",
                                           encoding="utf-8")
    m = read_manifest(tmp_path)
    assert verify_dump(tmp_path, "pc-ida.jsonl", m)["input_sha256"] == "src"
    (tmp_path / "pc-ida.jsonl").write_text(body + "\n", encoding="utf-8")
    with pytest.raises(DumpIdentityError):
        verify_dump(tmp_path, "pc-ida.jsonl", m)
    (tmp_path / "pc-ida.jsonl").write_text(body, encoding="utf-8", newline="\n")
    m["pc-ida.jsonl"]["source_sha256"] = "other"
    with pytest.raises(DumpIdentityError):
        verify_dump(tmp_path, "pc-ida.jsonl", m)
