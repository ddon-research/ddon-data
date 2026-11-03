"""007 T005h: rule 4 on the v4 facts (PS4 slot from the mpManager stores), the codec walk's null
``codec_distance`` skip, the call-site constants in the fold key, and the all-pairs slot-order check."""

from __future__ import annotations

from test_roles import PC_R4, _element_world, _listener_world, run

from matcher import codecs, gates
from matcher.model import Access, Call, Func, SlotLayout, ps4_slot, slot_layout

LAYOUT = SlotLayout(280, (("mStatus", 8, 4, 563), ("mErrorCode", 2260, 4, 563)))


def _f(*accesses: Access) -> Func:
    return Func(0x2E8620, "cSeedGameSvConnection::OnPacket_S2C_X_RES", "ps4", 100, 20, [],
                accesses=tuple(accesses))


def st(disp, *, via=280, width=4, arg_loc="rdi", arg=0, indexed=False, access="store"):
    return Access(0x10 + disp, arg_loc, arg, disp, width, access, via, indexed)


# --- the PS4 slot ---------------------------------------------------------------------------------------

def test_ps4_slot_from_error_code_and_status_stores():
    # mErrorCode[91] = 2260 + 364, mStatus[91] = 8 + 364 (T005b pair 1: slot 91)
    assert ps4_slot(_f(st(2260 + 364), st(8 + 364)), LAYOUT) == (91, None)
    assert ps4_slot(_f(st(2260 + 364)), LAYOUT) == (91, None)


def test_ps4_slot_near_misses():
    assert ps4_slot(_f(st(2260 + 364), st(8 + 368)), LAYOUT) == (None, "several slot indices 91,92")
    assert ps4_slot(_f(st(2260 + 364, indexed=True)), LAYOUT) == (None, "variable slot index")
    # not via mpManager, not this, a load, a byte store, an offset past the arrays: no slot
    for a in (st(2260 + 364, via=288), st(2260 + 364, via=None), st(2260 + 364, arg_loc="rsi", arg=1),
              st(2260 + 364, access="load"), st(2260 + 364, width=1), st(2260 + 2252)):
        assert ps4_slot(_f(a), LAYOUT) == (None, None), a


def _types(conn_type="cNetGameServer*", dup=False, arr="nError::ERROR_CODE[563]"):
    conn = {"name": "cSeedGameSvConnection", "members": [{"name": "mpManager", "offset": 280, "type": conn_type}]}
    mgr = {"name": "cNetGameServer", "members": [
        {"name": "mStatus", "offset": 8, "size": 2252, "type": "sNetworkExt::NET_STAT[563]"},
        {"name": "mErrorCode", "offset": 2260, "size": 2252, "type": arr}]}
    return [conn, mgr] + ([dict(mgr)] if dup else [])


def test_slot_layout_from_dwarf_fails_closed():
    assert slot_layout(_types()) == LAYOUT
    assert slot_layout(_types(conn_type="cNetLoginServer*")) is None
    assert slot_layout(_types(dup=True)) is None
    assert slot_layout(_types(arr="nError::ERROR_CODE")) is None
    assert slot_layout(_types()[:1]) is None


# --- the codec walk skips callees that reach no codec (v4) --------------------------------------------

def test_flatten_skips_null_codec_distance_only_on_v4():
    w, _ = _element_world()
    w.pcf(0x700, [0xDEAD])  # reaches no codec; its own callee is not in the dump
    f = w.facts()
    f.pc[0x200].calls.append(Call(0x2FD, 0x700))
    assert codecs.flatten(f, "pc", 0x200).gaps == [0xDEAD]  # v3: entered, its missing callee is a gap
    f.pc[0x700].has_codec_distance = True  # v4, codec_distance None
    fl = codecs.flatten(f, "pc", 0x200)
    assert fl.gaps == [] and fl.tokens == ["4", "4", "4", "1"]
    f.pc[0x700].codec_distance = 2  # reaches a codec: entered again
    assert codecs.flatten(f, "pc", 0x200).gaps == [0xDEAD]


# --- fold key: call-site immediates are body bytes ----------------------------------------------------

def test_fold_key_separates_call_site_constants():
    a = Func(0x500, "a", "pc", 80, 20, [Call(0x501, PC_R4, 4, 4, ((1, 8), (2, 28), (3, 1)))])
    b = Func(0x600, "b", "pc", 80, 20, [Call(0x601, PC_R4, 4, 4, ((1, 8), (2, 29), (3, 1)))])
    c = Func(0x700, "c", "pc", 80, 20, [Call(0x701, PC_R4, 4, 4, ((1, 8), (2, 28), (3, 1)))])
    folded = gates.fold_groups({f.va: f for f in (a, b, c)})
    assert folded == {0x500: [0x700], 0x700: [0x500]}


# --- slot order against every handler pair --------------------------------------------------------------

def test_listener_inversion_against_non_candidate_handler_pairs():
    w, h = _listener_world(ps4_slot=7, pc_slot=77)
    f, res = run(w, [h])
    assert (0x500, 0x1500) in res.pairs
    # a second handler pair with slots on both sides but no requester: not a candidate, yet its slots
    # (PS4 3 -> PC 90) cross (7 -> 77), so the candidate is refused
    w, h = _listener_world(ps4_slot=7, pc_slot=77)
    w.slots[0x2000] = 3
    h2 = w.handler(0x101, 0x2000, "Y_RES", 0x200, [0x3B6160, 0x3B6280], slot=90)
    f, res = run(w, [h, h2])
    assert not any(p.rule.startswith("listener") for p in res.pairs.values())
    assert any("slot order inversion" in x.detail for x in res.listed)
