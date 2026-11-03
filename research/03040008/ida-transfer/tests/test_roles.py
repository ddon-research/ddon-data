"""007 T005e role anchors: one test group per rule, near misses included, on synthetic facts."""

from __future__ import annotations

from matcher import checks, codecs, gates, roles
from matcher.model import Call, Facts, Func, Param

GAME = "cSeedGameSvConnection::"
THIS = Param("this", "X*", None, True)
PKT = Param("pPacket", "CPacket*", None)
ARR = Param("ar", "MtTypedArray<X>*", None)

# PC codecs (T005b § 2.1 VAs) and helpers
PC_R1, PC_R2, PC_R4, PC_R8 = 0x8BC410, 0x8BC440, 0x8BC4D0, 0x8BC6A0
PC_W4 = 0x8BC920
COP, WP, RESERVE_PC = 0x878860, 0x8BCBB0, 0xBB39D0
# PS4 codecs (T005b § 2.2)
PS4_CODECS = {0x3B6140: "nPacket::Read_u8", 0x3B6160: "nPacket::Read_u16", 0x3B6190: "nPacket::Read_u32",
              0x3B6280: "nPacket::Read_s32", 0x3B61B0: "nPacket::Read_u64", 0x3B6660: "nPacket::Write_u16",
              0x3B6690: "nPacket::Write_u32", 0x3B6640: "nPacket::Write_u8"}
P_U8, P_U16, P_U32, P_S32 = 0x3B6140, 0x3B6160, 0x3B6190, 0x3B6280
P_W16, P_W32, P_W8 = 0x3B6660, 0x3B6690, 0x3B6640
RESERVE_PS4 = 0x7EDF80


class W:
    """A small two-sided world."""

    def __init__(self) -> None:
        self.pc: dict[int, Func] = {}
        self.ps4: dict[int, Func] = {}
        self.params: dict[int, list[Param]] = {}
        for va, w in ((PC_R1, 1), (PC_R2, 2), (PC_R4, 4), (PC_R8, 8)):
            self.pc[va] = Func(va, f"Read_{w}", "pc", 30, 10, [], callers_count=500, caller_sites=500,
                               ecx_read_before_write=False, ret_imm=(), codec=("read", w))
        self.pc[PC_W4] = Func(PC_W4, "Write_u32", "pc", 30, 10, [], callers_count=500, caller_sites=500,
                              codec=("write", 4))
        self.pc[COP] = Func(COP, "cSeedGameSvConnection::callOnPacketFunc", "pc", 100, 40, [], callers_count=600)
        self.pc[WP] = Func(WP, "nUserSession::CPacket::WritePacket", "pc", 100, 40, [], callers_count=600)
        self.pc[RESERVE_PC] = Func(RESERVE_PC, roles.RESERVE, "pc", 37, 11, [], callers_count=500)
        for va, nm in PS4_CODECS.items():
            self.ps4[va] = Func(va, nm, "ps4", 30, 10, [], callers_count=500)
        self.ps4[RESERVE_PS4] = Func(RESERVE_PS4, roles.RESERVE, "ps4", 51, 17, [], callers_count=500)
        self.callbacks: dict[int, str] = {}
        self.keys: dict[int, tuple[int, int, int]] = {}
        self.slots: dict[int, int] = {}

    def pcf(self, va, targets, *, name=None, ecx=True, ret=(4,), callers=1, consts=None, ins=20):
        calls = []
        for i, t in enumerate(targets):
            cs = (consts or {}).get(i, ())
            g = self.pc.get(t)
            cdecl = g is not None and g.codec is None and g.ecx_read_before_write is False
            calls.append(Call(va + 1 + i, t, 4, 8 if cdecl else 4, tuple(cs), (), not cdecl))
        self.pc[va] = Func(va, name or f"sub_{va:X}", "pc", va % 997 + 40, ins, calls, callers_count=callers,
                           caller_sites=callers, ecx_read_before_write=ecx, ret_imm=tuple(ret))
        return va

    def ps4f(self, va, targets, *, name=None, params=None, callers=1, regs=None):
        calls = [Call(va + 1 + i, t, None, None, (), tuple((regs or {}).get(i, ()))) for i, t in enumerate(targets)]
        self.ps4[va] = Func(va, name or f"f_{va:X}", "ps4", 100, 20, calls, callers_count=callers,
                            caller_sites=callers)
        self.params[va] = params if params is not None else [THIS, PKT]
        return va

    def facts(self) -> Facts:
        f = Facts(pc=dict(self.pc), ps4=dict(self.ps4), table_callbacks=set(self.callbacks),
                  table_group={c: i for i, c in enumerate(sorted(self.callbacks))}, dwarf_params=dict(self.params),
                  table_key=dict(self.keys), ps4_handler_slot=dict(self.slots))
        # caller sites of PC functions with no ret N: the callers' arg_bytes give the stack bytes
        for g in f.pc.values():
            n = len(f.pc_callsites.get(g.va, []))
            if n and g.codec is None:
                g.caller_sites = n
        return f

    def handler(self, pc_va, ps4_va, name, pc_reader, ps4_body, *, read_packet=True, slot=None):
        """PC handler -> its reader; PS4 handler -> CPacket_S2C_<name>::ReadPacket (or inlined body)."""
        self.callbacks[pc_va] = GAME + f"OnPacket_A_{name}"
        self.keys[pc_va] = (1, pc_va & 0xFF, 2)
        cop_consts = {1: ((0, slot),)} if slot is not None else {}
        self.pcf(pc_va, [pc_reader, COP], consts=cop_consts, callers=0)
        self.pc[pc_va].strings = frozenset([GAME + f"OnPacket_A_{name}"])
        if read_packet:
            rp = self.ps4f(ps4_va + 0x10, ps4_body, name=f"CPacket_S2C_{name}::ReadPacket")
            self.ps4f(ps4_va, [rp], name=GAME + f"OnPacket_S2C_{name}")
        else:
            self.ps4f(ps4_va, ps4_body, name=GAME + f"OnPacket_S2C_{name}")
        return pc_va, ps4_va


def run(w: W, handlers):
    f = w.facts()
    from matcher import tier0
    t0, _ = tier0.tier0(f)
    pref = tier0.group_prefixes(t0, f)
    hp = {h: frozenset([h]) for h in handlers}
    return f, roles.run(f, hp, set(hp), t0, pref)


def _element_world(*, ps4_inline_element=False, pc_extra_u8=False):
    """Handler X: PC reader 0x200 = 44 + element 0x300 (4 1); PS4 ReadPacket = 2 4 + Read_CDataE_ (4 1)."""
    w = W()
    pc_el = w.pcf(0x300, [PC_R4, PC_R1] + ([PC_R1] if pc_extra_u8 else []), ecx=False, ret=())
    w.pcf(0x200, [PC_R4, PC_R4, pc_el])
    ps4_el = w.ps4f(0x1200, [P_U32, P_U8], name="nPacket::Read_CDataE_", params=[PKT, ARR])
    body = [P_U16, P_S32] + ([P_U32, P_U8] if ps4_inline_element else [ps4_el])
    h = w.handler(0x100, 0x1000, "X_RES", 0x200, body)
    return w, h


# --- codecs ------------------------------------------------------------------------------------------------

def test_flatten_brackets_skip_and_gap():
    w, _ = _element_world()
    f = w.facts()
    fl = codecs.flatten(f, "pc", 0x200)
    assert fl.tokens == ["4", "4", "4", "1"] and not fl.gaps
    assert [(b.va, b.start, b.end, b.depth) for b in fl.brackets] == [(0x300, 2, 4, 1)]
    # callOnPacketFunc is never entered, a callee missing from the dump is a gap
    f.pc[0x200].calls.append(Call(0x2FF, COP))
    f.pc[0x200].calls.append(Call(0x2FE, 0xDEAD))
    assert codecs.flatten(f, "pc", 0x200).gaps == [0xDEAD]
    ps = codecs.flatten(f, "ps4", 0x1010)
    assert ps.tokens == ["2", "4", "4", "1"]
    assert [b.va for b in ps.brackets] == [0x1200]


def test_ps4_walk_enters_only_packet_readers():
    w = W()
    other = w.ps4f(0x1300, [P_U32], name="cNetGameServer::setX")
    w.ps4f(0x1400, [P_U16, other])
    assert codecs.flatten(w.facts(), "ps4", 0x1400).tokens == ["2"]


def test_codec_tokens_and_crosscheck():
    assert codecs.ps4_codec("nPacket::Read_f32") == ("read", "4")
    assert codecs.ps4_codec("nPacket::Write_MtString") == ("write", "S")
    assert codecs.ps4_codec("nPacket::Read_CDataX_") is None
    w = W()
    w.ps4[P_U32].codec = ("read", 2)  # a wrong classification is listed, the symbol wins
    rows = codecs.ps4_codec_crosscheck(w.facts())
    assert rows == [(P_U32, "nPacket::Read_u32", "read/4", "read/2")]


def test_count_embeddings():
    assert codecs.count_embeddings(list("41"), list("4411")) == 2
    assert codecs.count_embeddings(list("41"), list("481")) == 1
    assert codecs.count_embeddings(list("42"), list("481")) == 0
    assert codecs.leftmost_embedding(list("41"), list("481")) == [0, 2]


# --- rule 1: reader anchor ------------------------------------------------------------------------------

def test_reader_anchor_pairs_reader_with_readpacket():
    w, h = _element_world()
    f, res = run(w, [h])
    r = res.pairs[(0x200, 0x1010)]
    assert r.rule == "reader" and r.witnesses == ("0x100:0x1000",) and r.roots == {h}


def test_reader_anchor_inlined_on_ps4_lists():
    w = W()
    w.pcf(0x200, [PC_R4, PC_R4])
    h = w.handler(0x100, 0x1000, "X_RES", 0x200, [P_U16, P_S32], read_packet=False)
    f, res = run(w, [h])
    assert not any(p.rule == "reader" for p in res.pairs.values())
    assert any("inlined on PS4" in x.detail for x in res.listed)
    assert res.inlined_on_ps4 == [h]


def test_reader_anchor_refuses_other_packet_name():
    """Negative control in miniature: a PS4 handler of another packet gives no reader pair."""
    w, h = _element_world()
    w.callbacks[0x100] = GAME + "OnPacket_A_Y_RES"
    w.pc[0x100].strings = frozenset([GAME + "OnPacket_A_Y_RES"])
    f, res = run(w, [h])
    assert (0x200, 0x1010) not in res.pairs
    assert any("is not a name of the PC string" in x.detail for x in res.listed)


def test_reader_anchor_refuses_two_codec_callees():
    w, h = _element_world()
    w.pcf(0x210, [PC_R4])
    w.pc[0x100].calls.append(Call(0x150, 0x210))
    f, res = run(w, [h])
    assert (0x200, 0x1010) not in res.pairs
    assert any("several callees reach codecs" in x.detail for x in res.listed)


def test_reader_anchor_shared_pc_reader_conflicts():
    w, h = _element_world()
    h2 = w.handler(0x101, 0x2000, "Y_RES", 0x200, [P_U16, P_S32])  # the same PC reader 0x200
    f, res = run(w, [h, h2])
    assert not any(p.rule == "reader" for p in res.pairs.values())
    assert ("pc", 0x200) in res.conflicts


# --- rule 2: element-reader anchor --------------------------------------------------------------------

def test_element_reader_equal_widths_pair():
    w, h = _element_world()
    f, res = run(w, [h])
    r = res.pairs[(0x300, 0x1200)]
    assert r.rule == "element-reader" and r.flags == "-" and r.roots == {h}
    assert "c=this=False bytes=8" in r.gate_results


def test_element_reader_ps4_inlined_no_pair():
    w, h = _element_world(ps4_inline_element=True)
    f, res = run(w, [h])
    assert not any(p.rule == "element-reader" for p in res.pairs.values())


def test_element_reader_inconsistent_occurrences_refused():
    """The PS4 element reader meets PC 0x300 in one handler and PC 0x310 in another: neither pairs."""
    w, h = _element_world()
    w.pcf(0x310, [PC_R4, PC_R1], ecx=False, ret=())
    w.pcf(0x220, [PC_R4, PC_R4, PC_R2, 0x310])
    h2 = w.handler(0x102, 0x3000, "Z_RES", 0x220, [P_U16, P_S32, P_U16, 0x1200])
    f, res = run(w, [h, h2])
    assert (0x300, 0x1200) not in res.pairs and (0x310, 0x1200) not in res.pairs
    assert any("pairs differently" in x.detail for x in res.listed)


def test_element_reader_needs_identifying_widths(monkeypatch):
    """Fail closed: a second PS4 reader with the same widths but another element reader makes the pair
    unidentified by widths alone. Without the check the pair is accepted."""
    w, h = _element_world()
    other = w.ps4f(0x1700, [P_U32, P_U8], name="nPacket::Read_CDataOther_", params=[PKT, ARR])
    w.ps4f(0x4010, [P_U16, P_S32, other], name="CPacket_S2C_W_RES::ReadPacket")
    w.ps4f(0x4000, [0x4010], name=GAME + "OnPacket_S2C_W_RES")
    f, res = run(w, [h])
    assert (0x300, 0x1200) not in res.pairs
    assert any("do not identify" in x.detail for x in res.listed)
    monkeypatch.setattr(roles, "unidentified", lambda *a, **k: set())
    f, res = run(w, [h])
    assert (0x300, 0x1200) in res.pairs


def test_element_reader_same_element_elsewhere_still_identified():
    """Another PS4 reader with equal widths that calls the same element reader does not block it."""
    w, h = _element_world()
    w.ps4f(0x4010, [P_U16, P_S32, 0x1200], name="CPacket_S2C_W_RES::ReadPacket")
    w.ps4f(0x4000, [0x4010], name=GAME + "OnPacket_S2C_W_RES")
    f, res = run(w, [h])
    assert (0x300, 0x1200) in res.pairs


def test_element_reader_unique_embedding_is_season3_extended():
    w, h = _element_world(pc_extra_u8=True)  # PC element 4 1 1, PS4 4 1: PC body 411 vs PS4 41 -> 2 ways
    f, res = run(w, [h])
    assert (0x300, 0x1200) not in res.pairs  # ambiguous embedding
    w2 = W()
    pc_el = w2.pcf(0x300, [PC_R4, PC_R8, PC_R1], ecx=False, ret=())  # 4 8 1 vs 4 1: one embedding
    w2.pcf(0x200, [PC_R4, PC_R4, pc_el])
    ps4_el = w2.ps4f(0x1200, [P_U32, P_U8], name="nPacket::Read_CDataE_", params=[PKT, ARR])
    h2 = w2.handler(0x100, 0x1000, "X_RES", 0x200, [P_U16, P_S32, ps4_el])
    f, res = run(w2, [h2])
    assert res.pairs[(0x300, 0x1200)].flags == "season3-extended"


def test_element_reader_gate_c_refuses():
    w, h = _element_world()
    w.params[0x1200] = [THIS, PKT, ARR]  # PS4 takes an object, the PC element reader does not
    f, res = run(w, [h])
    assert (0x300, 0x1200) not in res.pairs
    assert any(x.rule == "element-reader" and "c=this" in x.detail for x in res.listed)


def test_element_reader_pc_only_bracket_unpaired():
    """PC wraps two codecs in a callee where PS4 reads them inline: no pair, and the PS4 element still pairs."""
    w = W()
    inner = w.pcf(0x320, [PC_R4, PC_R2], ecx=False, ret=())
    pc_el = w.pcf(0x300, [PC_R4, PC_R1], ecx=False, ret=())
    w.pcf(0x200, [PC_R4, PC_R4, inner, pc_el])
    ps4_el = w.ps4f(0x1200, [P_U32, P_U8], name="nPacket::Read_CDataE_", params=[PKT, ARR])
    h = w.handler(0x100, 0x1000, "X_RES", 0x200, [P_U16, P_S32, P_U32, P_U16, ps4_el])
    f, res = run(w, [h])
    assert (0x300, 0x1200) in res.pairs
    assert not any(p[0] == 0x320 for p in res.pairs)


# --- rule 3: codec positions -----------------------------------------------------------------------------

def test_callsites_name_positions_of_equal_pairs_only():
    w, h = _element_world()
    f, res = run(w, [h])
    rows = {r[0]: r for r in res.callsites}
    # header positions (0x201, 0x202) are left out; the element's two codec sites get the PS4 overloads
    assert set(rows) == {"0x301", "0x302"}
    assert rows["0x301"][4] == "nPacket::Read_u32" and rows["0x302"][4] == "nPacket::Read_u8"
    assert all(r[6] == "agree" for r in res.callsites)
    # T013a: the aligned PS4 call site and its owner (the element reader), and the anchor map
    assert rows["0x301"][7:] == ["0x1201", "0x1200"] and rows["0x302"][7:] == ["0x1202", "0x1200"]
    assert res.codec_sites == {0x301: frozenset([0x1201]), 0x302: frozenset([0x1202])}
    w2, h2 = _element_world(pc_extra_u8=True)
    f, res = run(w2, [h2])
    assert res.callsites == []


# --- rule 4: listener slot -----------------------------------------------------------------------------

def _listener_world(*, ps4_slot=7, pc_slot=77, second_sender=False, ps4_payload=(P_W32,), login=False):
    w, h = _element_world()
    w.slots[0x1000] = ps4_slot
    w.pc[0x100].calls[1] = Call(0x102, COP, 4, 20, ((0, pc_slot),), (), True)
    key = w.keys[0x100]
    sender = w.pcf(0x88A700 if login else 0x500, [WP, PC_W4], consts={0: ((1, key[0]), (2, key[1]), (3, 1))})
    w.pcf(0x600, [RESERVE_PC, sender], consts={0: ((0, pc_slot),)})
    if second_sender:
        w.pcf(0x510, [WP], consts={0: ((1, key[0]), (2, key[1]), (3, 1))})
    s4 = w.ps4f(0x1500, [P_W16, P_W16, P_W16, *ps4_payload], name=GAME + "Send_C2S_X_REQ")
    w.ps4f(0x1600, [RESERVE_PS4, s4], name="cNetGameServer::getX", regs={0: (("rsi", ps4_slot),)})
    return w, h


def test_listener_anchor_pairs_requester_and_sender():
    w, h = _listener_world()
    f, res = run(w, [h])
    assert res.pairs[(0x600, 0x1600)].rule == "listener-requester"
    assert res.pairs[(0x500, 0x1500)].rule == "listener-sender"


def test_listener_anchor_refusals():
    w, h = _listener_world()
    w.slots.clear()  # the v3 dumps carry no PS4 handler slot
    f, res = run(w, [h])
    assert not any(p.rule.startswith("listener") for p in res.pairs.values())
    assert any("PS4 handler slot not in the dump" in x.detail for x in res.listed)
    for kw, why in (({"second_sender": True}, "senders"), ({"ps4_payload": (P_W8,)}, "payload widths"),
                    ({"login": True}, "login manager")):
        w, h = _listener_world(**kw)
        f, res = run(w, [h])
        assert not any(p.rule.startswith("listener") for p in res.pairs.values()), kw
        assert any(why in x.detail for x in res.listed), (kw, [x.detail for x in res.listed])


def test_listener_anchor_shared_slot_and_inversion():
    w, h = _listener_world()
    w.slots[0x2000] = 7  # a second handler on PS4 slot 7
    h2 = w.handler(0x101, 0x2000, "Y_RES", 0x200, [P_U16, P_S32], slot=78)
    f = w.facts()
    cands, listed = roles.listener_anchor(f, [h, h2])
    assert cands == [] and any("shared slot" in x.detail for x in listed)
    # two clean candidates whose slots cross: both refused
    assert roles.inversions([((1, 2), 10, 100), ((7, 8), 20, 90), ((5, 5), 30, 200)]) == {(1, 2), (7, 8)}
    assert roles.inversions([((1, 2), 10, 100), ((7, 8), 20, 190)]) == set()


# --- gate (c) refinements ------------------------------------------------------------------------------

def test_pc_this_from_callers_and_arg_bytes():
    w, h = _element_world()
    f = w.facts()
    el = f.pc[0x300]
    el.ecx_read_before_write = True  # MSVC push ecx in a cdecl function
    assert gates.pc_has_this(f, el) is False  # its one caller does not load ecx
    assert gates.pc_stack_bytes(f, el) == 8  # arg_bytes of the caller site (add esp, 8)
    f.pc[0x200].calls[2] = Call(0x203, 0x300, 4, 8, (), (), True)
    f.pc_callsites.clear()
    f.__post_init__()
    assert gates.pc_has_this(f, el) is True


# --- precision and control -----------------------------------------------------------------------------

def test_role_precision_and_control_on_two_handlers():
    w, h = _element_world()
    pc_el = w.pcf(0x330, [PC_R2, PC_R2, PC_R1], ecx=False, ret=())
    w.pcf(0x230, [PC_R4, PC_R4, pc_el])
    ps4_el = w.ps4f(0x1230, [P_U16, P_U16, P_U8], name="nPacket::Read_CDataF_", params=[PKT, ARR])
    h2 = w.handler(0x103, 0x5000, "V_RES", 0x230, [P_U16, P_S32, ps4_el])
    f = w.facts()
    from matcher import tier0
    t0, _ = tier0.tier0(f)
    pref = tier0.group_prefixes(t0, f)
    seeds = {h[0]: h[1], h2[0]: h2[1]}
    full = checks.pipeline(f, seeds, t0, pref)
    assert {(0x300, 0x1200), (0x330, 0x1230)} <= set(full.roles.pairs)
    row = checks.role_precision(f, seeds, t0, pref, full, 0, withheld={h[0]})
    assert row.wrong == 0 and row.dependent >= 2 and row.dependent_absent >= 2
    assert checks.derangement(seeds, 1) == {h[0]: h2[1], h2[0]: h[1]}
    ctl = checks.negative_control(f, seeds, t0, pref, full, 1)
    assert ctl.accepted == {} and ctl.accepted_wrong == 0


def test_role_precision_flags_a_contradiction(monkeypatch):
    w, h = _element_world()
    f = w.facts()
    from matcher import tier0
    t0, _ = tier0.tier0(f)
    pref = tier0.group_prefixes(t0, f)
    seeds = {h[0]: h[1]}
    full = checks.pipeline(f, seeds, t0, pref)
    real = checks.pipeline

    def fake(facts, sd, t, p):
        r = real(facts, sd, t, p)
        r.roles.pairs[(0x300, 0x9999)] = roles.RolePair(0x300, 0x9999, "element-reader", (), frozenset(), "-")
        return r

    monkeypatch.setattr(checks, "pipeline", fake)
    row = checks.role_precision(f, seeds, t0, pref, full, 0, withheld=set())
    assert row.wrong == 1
