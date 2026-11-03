"""Rule 1: function names.

Tier-0 callbacks take their PC ``OnPacket_`` string (V, PC alone), paired or not; every other accepted pair takes
the PS4 symbol's IDA name. Against the PC function's current name: default -> set; equal -> nothing; another
non-default name -> conflict, unless T002 rates it wrong / no source, or it is the PS4-form spelling of the PC
string (then ``correct``). A name proposed for two PC functions (MSVC folding) sets neither.
"""

from __future__ import annotations

from dataclasses import dataclass

from .inputs import DEFAULT_NAME, PairRow, PcExtra, t002_rating

# T004f: OnPacket_ labels left at the old (pre-repair) starts of three callbacks; T007 removes them before it
# names the function at its new start (research/T004f-repair-batch.md, table "names left").
OLD_LABELS = (
    (0x7C5C8D, 0x7C5C90, "cSeedGameSvConnection::OnPacket_BATTLE_CONTENT_PHASE_ENTRY_READY_RES"),
    (0x7D714C, 0x7D7150, "cSeedGameSvConnection::OnPacket_GP_GET_CAP_TO_GP_CHANGE_LIST_RES"),
    (0x7D858F, 0x7D8590, "cSeedGameSvConnection::OnPacket_GP_GP_SHOP_DISPLAY_BUY_RES"),
)


@dataclass(frozen=True)
class NameRow:
    pc_va: int
    name: str
    current: str
    action: str  # set | correct | remove-label | equal | conflict | folded
    source: str  # pc-string | ps4-symbol | T004f
    basis: str
    reason: str


def is_default(name: str, default_flag: bool) -> bool:
    return default_flag or bool(DEFAULT_NAME.match(name))


def ps4_form(current: str, pc_string: str) -> bool:
    """``cX::OnPacket_S2C_<N>`` / ``OnPacket_L2C_<N>`` for the PC string ``cX::OnPacket_<N>``."""
    if "::OnPacket_" not in pc_string:
        return False
    return current in (pc_string.replace("::OnPacket_", "::OnPacket_S2C_", 1),
                       pc_string.replace("::OnPacket_", "::OnPacket_L2C_", 1))


def name_rows(tier0: dict[int, str], pairs: list[PairRow], pc: dict[int, PcExtra],
              t002: dict[int, list[str]], old_labels=OLD_LABELS) -> list[NameRow]:
    by_pc = {p.pc_va: p for p in pairs}
    cands: dict[int, tuple[str, str, str]] = {}
    for va, s in tier0.items():
        p = by_pc.get(va)
        cands[va] = (s, "pc-string", f"tier0; paired by {p.rule}" if p else "tier0; no PS4 pair")
    for p in pairs:
        if p.pc_va not in cands:
            cands[p.pc_va] = (p.ps4_symbol, "ps4-symbol", f"paired by {p.rule}")
    users: dict[str, list[int]] = {}
    for va, (nm, _, _) in cands.items():
        users.setdefault(nm, []).append(va)
    holders: dict[str, list[int]] = {}
    for va, x in pc.items():
        if not is_default(x.name, x.default_name):
            holders.setdefault(x.name, []).append(va)
    rows: list[NameRow] = []
    for va in sorted(cands):
        nm, src, basis = cands[va]
        x = pc.get(va)
        cur = x.name if x else ""
        if len(users[nm]) > 1:
            others = " ".join(f"{v:#x}" for v in sorted(users[nm]) if v != va)
            rows.append(NameRow(va, nm, cur, "folded", src, basis, f"name proposed also for {others}"))
            continue
        if x is None:
            rows.append(NameRow(va, nm, cur, "conflict", src, basis, "no PC function record"))
            continue
        if cur == nm:
            rows.append(NameRow(va, nm, cur, "equal", src, basis, "already named so"))
            continue
        clash = [v for v in holders.get(nm, ()) if v != va]
        if clash:
            rows.append(NameRow(va, nm, cur, "conflict", src, basis,
                                "name held by " + " ".join(f"{v:#x}" for v in clash)))
            continue
        if is_default(cur, x.default_name):
            rows.append(NameRow(va, nm, cur, "set", src, basis, "default name"))
            continue
        if src == "pc-string" and ps4_form(cur, nm):
            rows.append(NameRow(va, nm, cur, "correct", src, basis,
                                f'current "{cur}" is the PS4-form spelling of the PC string "{nm}"'))
            continue
        rating = t002_rating(t002.get(va, []))
        if rating:
            verdict = next(v for v in t002[va] if v.startswith("wrong") or "name source not code" in v)
            rows.append(NameRow(va, nm, cur, "correct", src, basis, f'T002 rates "{cur}" {rating}: "{verdict}"'))
            continue
        rows.append(NameRow(va, nm, cur, "conflict", src, basis, f'current non-default name "{cur}"'))
    for label, start, s in old_labels:
        rows.append(NameRow(label, "", s, "remove-label", "T004f", f"stale label of the callback {start:#x}",
                            f"T004f: label left at the old start; remove before naming {start:#x}"))
    return rows


WRITTEN = ("set", "correct")
