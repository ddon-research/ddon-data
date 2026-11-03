"""007 T006 transfer rules: one test group per rule, with near misses (synthetic DWARF records and facts)."""

from __future__ import annotations

import pytest

from matcher.model import Access, Call, DwarfType, Facts, Func, Param
from transfer import comments, names, prototypes, render, run, typecheck
from transfer.inputs import PairRow, PcExtra, Ps4Fn, pairs_sources_match, t002_rating
from transfer.layout import LayoutError, Layouts, land

# --- synthetic DWARF type records ---------------------------------------------------------------------------


def m(name, type_, **kw):
    return {"name": name, "type": type_, "offset": kw.pop("offset", 0), "size": kw.pop("size", 0), **kw}


def cls(name, members=(), bases=(), size=8, tag="class", **kw):
    return {"name": name, "tag": tag, "size": size, "members": list(members),
            "bases": [{"name": b, "offset": 0, "virtual": False} for b in bases], **kw}


VPTR = m("_vptr$X", "int()**", artificial=True)
BASE_TYPES = {
    "u8": {"name": "u8", "tag": "typedef", "target": "unsigned char"},
    "u16": {"name": "u16", "tag": "typedef", "target": "unsigned short"},
    "u32": {"name": "u32", "tag": "typedef", "target": "unsigned int"},
    "u64": {"name": "u64", "tag": "typedef", "target": "long unsigned int"},
    "f64": {"name": "f64", "tag": "typedef", "target": "double"},
}


def layouts(*recs):
    t = dict(BASE_TYPES)
    t.update({r["name"]: r for r in recs})
    return Layouts(t)


def offsets(info):
    return [(x.name, x.offset, x.size) for x in info.members]


# --- layout rules (README "Layout rules") --------------------------------------------------------------------


def test_l1_scalars_fixed_typedef_and_abi_dependent_long():
    lay = layouts(cls("A", [m("a", "u8"), m("b", "u64"), m("c", "u16")]))
    assert offsets(lay.layout("A")) == [("a", 0, 1), ("b", 8, 8), ("c", 16, 2)]
    lay = layouts(cls("B", [m("x", "long int")]))
    with pytest.raises(LayoutError, match="differs"):
        lay.layout("B")


def test_l2_pointers_are_four_bytes_and_member_pointers_refused():
    lay = layouts(cls("A", [m("p", "u8*"), m("q", "u32"), m("r", "void(int)*"), m("s", "size_t")]))
    assert offsets(lay.layout("A")) == [("p", 0, 4), ("q", 4, 4), ("r", 8, 4), ("s", 12, 4)]
    assert lay.layout("A").size == 16
    with pytest.raises(LayoutError, match="pointer to member"):
        layouts(cls("B", [m("f", "void(MtObject*) MtObject::*")])).layout("B")


def test_l3_alignment_capped_at_eight_and_size_rounded():
    lay = layouts(cls("A", [m("a", "u8"), m("d", "f64"), m("e", "u8")]))
    info = lay.layout("A")
    assert offsets(info) == [("a", 0, 1), ("d", 8, 8), ("e", 16, 1)]
    assert (info.size, info.align) == (24, 8)


def test_l4_vptr_own_and_shared_with_dynamic_base():
    lay = layouts(cls("Base", [VPTR, m("x", "u32")]), cls("Der", [m("y", "u32")], bases=["Base"]))
    assert offsets(lay.layout("Base")) == [("vptr", 0, 4), ("x", 4, 4)]
    assert offsets(lay.layout("Der")) == [("Base", 0, 8), ("y", 8, 4)]
    assert lay.layout("Der").dynamic
    # a dynamic class over a non-dynamic base: vptr first, then the base
    lay = layouts(cls("Plain", [m("x", "u32")]), cls("Dyn", [VPTR, m("y", "u8")], bases=["Plain"]))
    assert offsets(lay.layout("Dyn")) == [("vptr", 0, 4), ("Plain", 4, 4), ("y", 8, 1)]


def test_l5_empty_base_takes_no_space_and_multiple_bases_refused():
    lay = layouts(cls("Empty", [], size=1), cls("D", [m("x", "u32")], bases=["Empty"]))
    assert offsets(lay.layout("D")) == [("x", 0, 4)]
    assert lay.layout("Empty").size == 1
    lay = layouts(cls("E1", [m("a", "u8")]), cls("E2", [m("b", "u8")]), cls("M", [], bases=["E1", "E2"]))
    with pytest.raises(LayoutError, match="multiple inheritance"):
        lay.layout("M")


def test_l6_no_tail_padding_reuse_and_union():
    # Itanium may put `c` at 5 (inside Base's tail padding); MSVC puts it after the base's size
    lay = layouts(cls("Base", [VPTR, m("x", "u8")]), cls("Der", [m("c", "u8")], bases=["Base"]))
    assert lay.layout("Base").size == 8
    assert offsets(lay.layout("Der")) == [("Base", 0, 8), ("c", 8, 1)]
    lay = layouts(cls("U", [m("w", "u32"), m("b", "u8[4]"), m("q", "u64")], tag="union"))
    info = lay.layout("U")
    assert [x.offset for x in info.members] == [0, 0, 0] and info.size == 8


def test_l7_bitfield_and_virtual_base_and_declaration_refused():
    with pytest.raises(LayoutError, match="bitfield"):
        layouts(cls("Bits", [m("f", "u32", bit_size=3, bit_offset=0)])).layout("Bits")
    rec = cls("V", [m("x", "u32")], bases=["B"])
    rec["bases"][0]["virtual"] = True
    with pytest.raises(LayoutError, match="virtual base"):
        layouts(rec, cls("B", [m("y", "u32")])).layout("V")
    with pytest.raises(LayoutError, match="declaration"):
        layouts(cls("Fwd", [], size=None, declaration=True)).layout("Fwd")
    # a bitfield anywhere inside an embedded member refuses the outer type too
    with pytest.raises(LayoutError, match="bitfield"):
        layouts(cls("Bits", [m("f", "u32", bit_size=3)]), cls("Out", [m("b", "Bits")])).layout("Out")


def test_arrays_multi_dimensional():
    lay = layouts(cls("A", [m("a", "u16[2][3]"), m("b", "u32")]))
    info = lay.layout("A")
    assert offsets(info) == [("a", 0, 12), ("b", 12, 4)]
    assert info.members[0].info.count == 2 and info.members[0].info.elem.count == 3


# --- landing ----------------------------------------------------------------------------------------------


def test_land_member_start_width_and_near_misses():
    lay = layouts(cls("In", [m("p", "u16"), m("q", "u16")]),
                  cls("A", [VPTR, m("x", "u32"), m("arr", "In[2]"), m("b", "u8")]))
    info = lay.layout("A")
    assert land(info, 0, 4).ok and land(info, 0, 4).where == "vptr"
    assert land(info, 4, 4).ok
    assert land(info, 4, None).ok  # lea on a member start
    miss = land(info, 6, 2)  # 2 bytes into a 4-byte member
    assert not miss.ok and "+2 into a 4-byte member" in miss.where
    assert not land(info, 4, 1).ok  # width 1 on a 4-byte member
    assert land(info, 14, 2).ok and land(info, 14, 2).where == "arr[1].q"
    assert ("In", "q") in land(info, 14, 2).hits
    assert not land(info, 8, 4).ok  # a whole 4-byte element is no leaf (T006b)
    assert not land(info, 17, 1).ok  # padding
    assert not land(info, info.size, None).ok  # beyond the size


# --- T006b access check: leaf starts with the leaf's width, lea on own members, indexed scale ----------------


def _t006b_layout():
    return layouts(cls("In", [m("p", "u16"), m("q", "u16")]),
                   cls("A", [VPTR, m("x", "u32"), m("arr", "In[2]"), m("b", "u8"), m("w", "u32[3]")]))


def test_access_two_bytes_into_a_four_byte_member_contradicts():
    info = _t006b_layout().layout("A")
    r = land(info, 6, 2)
    assert not r.ok and "x: +2 into a 4-byte member" in r.where
    assert not land(info, 6, None).ok  # lea inside a scalar


def test_access_into_padding_contradicts():
    info = _t006b_layout().layout("A")  # b at 0x10 (1 byte), padding 0x11..0x13, w at 0x14
    for rel, width in ((0x11, 1), (0x12, 2), (0x13, None)):
        r = land(info, rel, width)
        assert not r.ok and "padding of A" in r.where


def test_indexed_access_scale_must_equal_element_size():
    info = _t006b_layout().layout("A")
    assert land(info, 0x14, 4, indexed=True, scale=4).ok  # w[i]
    assert land(info, 0x14, None, indexed=True, scale=4).ok  # &w[i]
    r = land(info, 0x14, 4, indexed=True, scale=8)
    assert not r.ok and "scale 8 on 4-byte elements" in r.where
    assert not land(info, 0x14, 4, indexed=True, scale=None).ok
    assert not land(info, 0x4, 4, indexed=True, scale=4).ok  # x is no array
    assert land(info, 0x8, 2, indexed=True, scale=4).ok  # arr[i].p
    assert not land(info, 0xA, 2, indexed=True, scale=4).ok  # arr[i].q: not an element start (brief: strict)


def test_access_at_array_element_start_accepted():
    info = _t006b_layout().layout("A")
    r = land(info, 0x18, 4)
    assert r.ok and r.where == "w[1]"
    assert land(info, 0x18, None).ok  # &w[1]
    assert land(info, 0xC, None).ok and land(info, 0xC, None).where == "arr[1]"  # &arr[1]
    assert land(info, 0xE, 2).ok  # arr[1].q, a leaf start with its width
    assert not land(info, 0xE, None).ok  # &arr[1].q: inside an embedded struct
    assert not land(info, 0x19, 1).ok  # a byte inside w[1]


def test_lea_on_inner_member_of_embedded_struct_contradicts_but_base_members_pass():
    lay = layouts(cls("Base", [VPTR, m("n", "u32")]), cls("In", [m("p", "u32"), m("q", "u32")]),
                  cls("D", [m("in", "In"), m("y", "u32")], bases=["Base"]))
    info = lay.layout("D")  # Base 0..8 (vptr, n), in 8..0x10, y 0x10
    assert land(info, 4, None).ok  # &this->n: a base member is the class's own member
    assert land(info, 8, None).ok  # &this->in
    r = land(info, 0xC, None)
    assert not r.ok and "in: lea +4 inside a 8-byte struct member" in r.where
    assert land(info, 0xC, 4).ok  # this->in.q with its width


def _fixture(name):
    import json
    from pathlib import Path
    return json.loads((Path(__file__).parent / "fixtures" / name).read_text(encoding="utf-8"))


def test_change_job_res_refused_by_the_pc_reader_accesses():
    """T007b run 3: PC 0x80cf80 contradicts the PS4 layout of CHANGE_JOB_RES (job data at PC +0x18, not +0xc)."""
    from matcher.model import _access
    fx = _fixture("change_job_res.json")
    lay = Layouts(fx["types"])
    name = "nUserSession::CPacket_S2C_CHANGE_JOB_RES"
    info = lay.layout(name)
    assert info.size == 0x118
    bad = {a["va"]: land(info, a["disp"], a.get("width")) for a in fx["accesses"]}
    bad = {va: r for va, r in bad.items() if not r.ok}
    # every lea into an MtTypedArray or into the job data is the address of a PC sub-object at another offset
    assert sorted(bad) == [0x80CF89, 0x80CFBC, 0x80CFCD, 0x80CFDE, 0x80CFEF, 0x80D000, 0x80D014, 0x80D02C,
                           0x80D044, 0x80D05C]
    assert "m_CharacterJobData: lea +4 inside a 72-byte struct member" in bad[0x80CF89].where
    accesses = [_access(a) for a in fx["accesses"]]
    f = pcf(fx["pc_va"], accesses)
    facts = facts_for([f], {fx["ps4_va"]: fx["ps4_params"]})
    v = run.type_verdicts(facts, lay, [PairRow(f.va, fx["ps4_va"], "", "", "", "reader", "-")],
                          {fx["ps4_va"]: Ps4Fn(fx["ps4_va"], name + "::ReadPacket", "", fx["ps4_params"], "void")})
    assert v[name].status == "refused" and v[name].reason == "contradiction"
    assert typecheck.contradiction_text(v[name]).startswith("m_CharacterJobData: lea +4 inside")
    assert all(x.status != "embedded" for x in v.values())


def test_pointer_to_pointer_is_no_class_pointer():
    lay = layouts(cls("A", [VPTR, m("x", "u32")]), cls("Arr", [m("p", "A**")]))
    assert typecheck.class_of("A*", lay) == "A" and typecheck.class_of("A&", lay) == "A"
    assert typecheck.class_of("A**", lay) is None and typecheck.class_of("A*&", lay) is None
    # mpArray[i] = p through a T** member: nothing is laid on A
    v = verdicts(lay, [pcf(0x10, [acc(0, va=0x1100), acc(0, 4, "store", via=0)])], {0x900: [
        {"name": "this", "type": "Arr*", "artificial": True}]})
    assert "A" not in v or v["A"].checked == 0


def test_coverage_counts_leaf_bytes_of_fixed_width_accesses():
    lay = layouts(cls("A", [VPTR, m("x", "u32"), m("y", "u8"), m("z", "u32[2]")]))
    v = verdicts(lay, [pcf(0x10, [acc(4), acc(8, 1, "store"), acc(4, access="lea"), acc(4, 4, va=0x2000),
                                  acc(12, va=0x3000)])], {0x900: [THIS_P]})
    assert v["A"].status == "accepted" and sorted(v["A"].covered) == [4, 5, 6, 7, 8, 12, 13, 14, 15]
    assert typecheck.coverage_text(v["A"]) == "9/20 45.0%"
    # fail closed: a load without a width checks nothing and contradicts
    v = verdicts(lay, [pcf(0x10, [acc(4), Access(0x1100, "ecx", 0, 4, None, "load")])], {0x900: [THIS_P]})
    assert v["A"].status == "refused" and "load without a width" in typecheck.contradiction_text(v["A"])


# --- rule 3: type acceptance -------------------------------------------------------------------------------


def pcf(va, accesses=(), *, ecx=True, ret=(4,), callers=0, calls=()):
    return Func(va=va, name=f"sub_{va:X}", side="pc", size=100, instructions=20, calls=list(calls),
                callers_count=callers, caller_sites=callers, ecx_read_before_write=ecx, ret_imm=tuple(ret),
                accesses=tuple(accesses))


def acc(disp, width=4, access="load", loc="ecx", arg=0, via=None, va=None):
    return Access(va or 0x1000 + disp, loc, arg, disp, None if access == "lea" else width, access, via)


def ps4fn(va, params, ret="s32"):
    return Ps4Fn(va, f"X::f{va:x}", f"_Z{va:x}", params, ret)


THIS_P = {"name": "this", "type": "A*", "artificial": True}


def facts_for(pc_funcs, ps4_params):
    ps4 = {va: Func(va=va, name=f"f{va:x}", side="ps4", size=10, instructions=10, calls=[]) for va in ps4_params}
    f = Facts(pc={x.va: x for x in pc_funcs}, ps4=ps4, table_callbacks=set(), table_group={})
    f.dwarf_params = {va: [Param(p["name"], p["type"], p.get("type_die"), bool(p.get("artificial"))) for p in ps]
                      for va, ps in ps4_params.items()}
    f.types = {1: DwarfType(1, "enumeration", "E", 4)}
    return f


def verdicts(lay, pc_funcs, params_by_ps4):
    pairs = [PairRow(f.va, ps4, "", "", "", "seed", "-") for f, ps4 in zip(pc_funcs, params_by_ps4, strict=True)]
    facts = facts_for(pc_funcs, params_by_ps4)
    fns = {va: ps4fn(va, ps) for va, ps in params_by_ps4.items()}
    return run.type_verdicts(facts, lay, pairs, fns)


def test_type_accepted_with_checked_access_and_refused_on_two_bytes_into_member():
    lay = layouts(cls("A", [VPTR, m("x", "u32"), m("y", "u8")]))
    v = verdicts(lay, [pcf(0x10, [acc(4), acc(8, 1, "store")])], {0x900: [THIS_P]})
    assert v["A"].status == "accepted" and v["A"].checked == 2 and set(v["A"].checked_members) == {"x", "y"}
    v = verdicts(lay, [pcf(0x10, [acc(4), acc(6, 2)])], {0x900: [THIS_P]})
    assert v["A"].status == "refused" and "+2 into a 4-byte member" in typecheck.contradiction_text(v["A"])


def test_type_without_access_is_not_accepted_and_bitfield_class_refused():
    lay = layouts(cls("A", [m("x", "u32")]))
    v = verdicts(lay, [pcf(0x10, [])], {0x900: [THIS_P]})
    assert v["A"].status == "unchecked"
    lay = layouts(cls("A", [m("x", "u32", bit_size=4)]))
    v = verdicts(lay, [pcf(0x10, [acc(0)])], {0x900: [THIS_P]})
    assert v["A"].status == "refused" and "bitfield" in v["A"].reason


def test_stack_argument_slots_follow_parameter_widths():
    lay = layouts(cls("A", [m("x", "u32")]))
    params = [{"name": "k", "type": "u64"}, {"name": "a", "type": "A*"}]  # a is stack slot 2
    v = verdicts(lay, [pcf(0x10, [acc(0, loc="stack", arg=2)], ecx=False, ret=(12,))], {0x900: params})
    assert v["A"].status == "accepted"
    v = verdicts(lay, [pcf(0x10, [acc(2, 2, loc="stack", arg=2)], ecx=False, ret=(12,))], {0x900: params})
    assert v["A"].status == "refused"
    v = verdicts(lay, [pcf(0x10, [acc(2, 2, loc="stack", arg=1)], ecx=False, ret=(12,))], {0x900: params})
    assert v["A"].status == "unchecked"  # slot 1 is the high half of k: not an object argument


def test_embedded_type_refused_refuses_outer_and_refused_root_gives_no_credit():
    lay = layouts(cls("In", [m("p", "u32")]), cls("A", [m("i", "In"), m("z", "u32")]),
                  cls("B", [m("i", "In")]))
    p_b = {"name": "this", "type": "B*", "artificial": True}
    p_in = {"name": "this", "type": "In*", "artificial": True}
    # In contradicted through its own argument -> A (embeds In) refused as well
    v = verdicts(lay, [pcf(0x10, [acc(4)]), pcf(0x20, [acc(1, 1)])], {0x900: [THIS_P], 0x901: [p_in]})
    assert v["In"].status == "refused" and v["A"].reason == "embeds refused In"
    # B contradicted: its access landing in In does not count for In
    v = verdicts(lay, [pcf(0x10, [acc(0), acc(4)])], {0x900: [p_b]})
    assert v["B"].status == "refused" and v["In"].checked == 0


def test_via_access_checks_the_pointee_and_known_size():
    lay = layouts(cls("P", [m("a", "u32"), m("b", "u32")]), cls("A", [m("pp", "P*")]))
    v = verdicts(lay, [pcf(0x10, [acc(0), acc(4, via=0, va=0x2000)])], {0x900: [THIS_P]})
    assert v["P"].status == "accepted" and v["P"].evidence_vas == {0x2000}
    v = verdicts(lay, [pcf(0x10, [acc(0), acc(5, 1, via=0)])], {0x900: [THIS_P]})
    assert v["P"].status == "refused"
    lay = layouts(cls("cSeedGameSvConnection", [m("x", "u32")]))
    v = verdicts(lay, [pcf(0x10, [acc(0)])], {0x900: [{"name": "this", "type": "cSeedGameSvConnection*",
                                                       "artificial": True}]})
    assert v["cSeedGameSvConnection"].status == "refused" and "known" in v["cSeedGameSvConnection"].reason


def test_lea_only_type_stays_unchecked_and_one_width_access_accepts():
    # T006c: a lea may contradict a type but never accept one
    lay = layouts(cls("A", [m("x", "u32"), m("y", "u32")]))
    v = verdicts(lay, [pcf(0x10, [acc(0, access="lea"), acc(4, access="lea")])], {0x900: [THIS_P]})
    assert v["A"].status == "unchecked" and v["A"].reason == "lea-only" and v["A"].checked == 2
    v = verdicts(lay, [pcf(0x10, [acc(0, access="lea"), acc(4, access="lea"), acc(4)])], {0x900: [THIS_P]})
    assert v["A"].status == "accepted" and v["A"].width_checked == 1
    # a lea that contradicts still refuses, width access or not
    v = verdicts(lay, [pcf(0x10, [acc(2, access="lea"), acc(4)])], {0x900: [THIS_P]})
    assert v["A"].status == "refused" and "lea +2" in typecheck.contradiction_text(v["A"])


def test_embedded_type_checked_by_leas_alone_is_not_written():
    lay = layouts(cls("In", [m("p", "u32"), m("q", "u32")]), cls("A", [m("i", "In"), m("z", "u32")]))
    v = verdicts(lay, [pcf(0x10, [acc(0, access="lea"), acc(8)])], {0x900: [THIS_P]})
    assert v["A"].status == "accepted" and v["In"].status == "unchecked"
    v = verdicts(lay, [pcf(0x10, [acc(4), acc(8)])], {0x900: [THIS_P]})
    assert v["In"].status == "embedded"


# --- rule 1: names ----------------------------------------------------------------------------------------


def extra(name, default=False, proto=None, user=False, comment=None, strings=None):
    return PcExtra(name, default, proto, user, comment, strings or {})


S = "cSeedGameSvConnection::OnPacket_BAZAAR_X_RES"


def test_names_set_equal_conflict_and_ps4_form():
    pc = {1: extra("sub_1", True), 2: extra(S + "2"), 3: extra("myname"),
          4: extra("cSeedGameSvConnection::OnPacket_S2C_BAZAAR_X_RES")}
    rows = {r.pc_va: r for r in names.name_rows({1: S + "1", 2: S + "2", 3: S + "3", 4: S}, [], pc, {}, ())}
    assert rows[1].action == "set" and rows[2].action == "equal" and rows[3].action == "conflict"
    assert rows[4].action == "correct" and "PS4-form spelling" in rows[4].reason
    pc[4] = extra("cSeedGameSvConnection::OnPacket_S2C_X_RES")  # group prefix dropped: not the PS4 form
    rows = {r.pc_va: r for r in names.name_rows({4: S}, [], pc, {}, ())}
    assert rows[4].action == "conflict"


def test_names_t002_wrong_corrected_and_unproved_kept():
    pc = {7: extra("cNetGameServer::OnPacket_S2C_Y"), 8: extra("Send_Z")}
    t002 = {7: ["wrong: class cNetGameServer is not the dispatch class"], 8: ["unproved: named from the response"]}
    pairs = [PairRow(8, 0x80, "cSeedGameSvConnection::Send_C2S_Z", "", "ps4-symbol", "listener-sender", "-")]
    rows = {r.pc_va: r for r in names.name_rows({7: S}, pairs, pc, t002, ())}
    assert rows[7].action == "correct" and "T002 rates" in rows[7].reason
    assert rows[8].action == "conflict"
    assert t002_rating(["unproved: no PC string (name source not code)"]) == "no source"


def test_names_folded_name_sets_neither_and_held_name_conflicts():
    pc = {1: extra("sub_1", True), 2: extra("sub_2", True), 3: extra("sub_3", True), 9: extra("Foo::bar")}
    pairs = [PairRow(1, 0x10, "Foo::read", "", "", "propagation", "-"),
             PairRow(2, 0x20, "Foo::read", "", "", "propagation", "-"),
             PairRow(3, 0x30, "Foo::bar", "", "", "propagation", "-")]
    rows = {r.pc_va: r for r in names.name_rows({}, pairs, pc, {}, ())}
    assert rows[1].action == rows[2].action == "folded"
    assert rows[3].action == "conflict" and "held by 0x9" in rows[3].reason


def test_names_remove_label_rows():
    rows = names.name_rows({}, [], {}, {})
    labels = [r for r in rows if r.action == "remove-label"]
    assert [r.pc_va for r in labels] == [0x7C5C8D, 0x7D714C, 0x7D858F]


# --- rule 2: prototypes -----------------------------------------------------------------------------------


def test_prototype_conventions_and_types():
    lay = layouts(cls("A", [m("x", "u32")]), {"name": "E", "tag": "enumeration", "size": 4, "enumerators": []})
    f_this = pcf(0x10, ret=(8,))
    f_std = pcf(0x20, ecx=False, ret=(8,))
    f_cdecl = pcf(0x30, ecx=False, ret=(), callers=1)
    caller = pcf(0x40, calls=[Call(0x41, 0x30, 8, 8)])
    params = {0x900: [THIS_P, {"name": "e", "type": "E", "type_die": 1}, {"name": "o", "type": "const A&"}],
              0x901: [{"name": "n", "type": "u32"}, {"name": "", "type": "u8*"}],
              0x902: [{"name": "f", "type": "void(int)*"}, {"name": "b", "type": "bool"}]}
    facts = facts_for([f_this, f_std, f_cdecl, caller], params)
    r = prototypes.pair_prototype(facts, lay, 0x10, ps4fn(0x900, params[0x900]), None, "seed")
    assert r.action == "set" and r.decl == "int __thiscall(A *this, E e, A *o)"
    assert r.classes == ("A",) and r.enums == ("E",)
    r = prototypes.pair_prototype(facts, lay, 0x20, ps4fn(0x901, params[0x901], "void"), None, "seed")
    assert r.decl == "void __stdcall(unsigned int n, unsigned __int8 *a1)"
    r = prototypes.pair_prototype(facts, lay, 0x30, ps4fn(0x902, params[0x902], "bool"), None, "seed")
    assert r.decl == "bool __cdecl(int f, bool b)" and "DWARF void(int)*" in r.notes


def test_prototype_near_misses_register_args_user_set_and_class_return():
    lay = layouts(cls("A", [m("x", "u32")]))
    facts = facts_for([pcf(0x10, ret=(4,))], {0x900: [THIS_P, {"name": "n", "type": "u32"}]})
    fn = ps4fn(0x900, [THIS_P, {"name": "n", "type": "u32"}])
    r = prototypes.pair_prototype(facts, lay, 0x10, fn, extra("x", proto="char __userpurge@<al>(int@<ecx>, "
                                                                        "int@<edi>, int)"), "s")
    assert r.action == "skip" and "edi" in r.notes
    r = prototypes.pair_prototype(facts, lay, 0x10, fn, extra("x", proto="int __thiscall(int this, int)",
                                                              user=True), "s")
    assert r.action == "conflict"
    r = prototypes.pair_prototype(facts, lay, 0x10, ps4fn(0x900, fn.params, "A"), None, "s")
    assert r.action == "skip" and "by value" in r.notes


def test_tier0_prototype_needs_ecx_and_ret4():
    facts = facts_for([pcf(0x10, ret=(4,)), pcf(0x20, ret=(8,)), pcf(0x30, ecx=False)], {})
    r = prototypes.tier0_prototype(facts, 0x10, S, None)
    assert r.action == "set" and r.decl == "int __thiscall(cSeedGameSvConnection *this, void *packet)"
    assert prototypes.tier0_prototype(facts, 0x20, S, None).action == "skip"
    assert prototypes.tier0_prototype(facts, 0x30, S, None).action == "skip"
    assert prototypes.tier0_prototype(facts, 0x10, "cOther::OnPacket_X", None).action == "skip"


# --- rule 4: comments -------------------------------------------------------------------------------------


def test_comment_existing_kept_and_appended_once():
    ours = comments.text(0x1234, ("A::f", "_ZN1A1fEv", "seed"), "season3-extended")
    assert ours == "PC name from string at 0x1234. PS4 02020005: A::f (_ZN1A1fEv); paired by seed. " \
                   "Season 3: season3-extended."
    r = comments.comment_row(1, ours, "earlier note")
    assert r.action == "append" and r.comment.startswith("earlier note\n----\n") and r.comment.endswith(ours)
    assert comments.comment_row(1, ours, r.comment).action == "equal"
    assert comments.comment_row(1, ours, "  ").action == "set"


# --- types.h -----------------------------------------------------------------------------------------------


def test_render_packs_with_gaps_and_blobs_untransferred_members():
    lay = layouts(cls("In", [m("p", "u32")]), cls("Other", [m("q", "u32")]),
                  cls("A", [VPTR, m("b", "u8"), m("i", "In"), m("o", "Other"), m("ptr", "Other*")]))
    out = render.render({"A", "In"}, {}, lay, {}, set(), "t")
    h = out.header
    assert "#pragma pack(push, 1)" in h and "struct Other;" in h
    assert "  void *__vftable; // +0x0 4 vptr" in h
    assert "  unsigned __int8 gap5[3];" in h
    assert "  In i; // +0x8 4" in h
    assert "  unsigned __int8 o[4]; // +0xc 4 Other (not transferred)" in h
    assert h.index("struct In ") < h.index("struct A ")


def test_enum_collisions_keep_the_first():
    e = {"E1": {"enumerators": [["MAX", 1]]}, "E2": {"enumerators": [["MAX", 2]]}, "E3": {"enumerators": [["Z", 0]]}}
    assert render.enum_collisions(e) == {"E2": "enumerator names also in E1"}


# --- fail closed ------------------------------------------------------------------------------------------


def test_pairs_tsv_from_other_dumps_is_refused():
    headers = {"pc-ida.jsonl": {"input_sha256": "aa"}, "ps4-dwarf.jsonl": {"elf_sha256": "bb"}}
    good = "# pc-ida.jsonl source aa; ps4-dwarf.jsonl source bb"
    assert pairs_sources_match(good, headers)
    assert not pairs_sources_match("# pc-ida.jsonl source aa; ps4-dwarf.jsonl source cc", headers)


def test_pairs_tsv_that_differs_from_the_matcher_run_is_refused():
    facts = facts_for([pcf(0x10)], {0x900: [THIS_P]})
    assert run.full_pairs_check(facts, {}, []) is None
    why = run.full_pairs_check(facts, {}, [PairRow(0x10, 0x900, "", "", "", "seed", "-")])
    assert why is not None and "1 pairs" in why
