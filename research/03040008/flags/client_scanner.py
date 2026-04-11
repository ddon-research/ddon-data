"""Decoded client JSON traversal and scanner dispatch."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, cast

from client_scan_handlers import (
    scan_ams_file,
    scan_csi_file,
    scan_evd_file,
    scan_esi_file,
    scan_evsi_file,
    scan_evp_file,
    scan_faa_file,
    scan_fsm_file,
    scan_gpl_file,
    scan_jmc_file,
    scan_jtq_file,
    scan_lot_file,
    scan_nll_file,
    scan_npc_situation_data,
    scan_qmi_fmi_file,
    scan_qst_file,
    scan_tqg_file,
)
from scan_models import FlagHit
from scan_utils import load_json, relative_path


SCANNER_MAP = {
    ".qst.json": scan_qst_file,
    ".gpl.json": scan_gpl_file,
    ".lot.json": scan_lot_file,
    ".fsm.json": scan_fsm_file,
    ".csi.json": scan_csi_file,
    ".esi.json": scan_esi_file,
    ".evsi.json": scan_evsi_file,
    ".qmi.json": scan_qmi_fmi_file,
    ".fmi.json": scan_qmi_fmi_file,
    ".jtq.json": scan_jtq_file,
    ".tqg.json": scan_tqg_file,
    ".jmc.json": scan_jmc_file,
    ".nll.json": scan_nll_file,
    ".faa.json": scan_faa_file,
    ".evp.json": scan_evp_file,
    ".evd.json": scan_evd_file,
    ".ams.json": scan_ams_file,
    ".smc.json": scan_npc_situation_data,
}

SITUATION_KEYWORDS = {"GroupSerial", "StartQuestId", "RangeStartQuestFlag"}


def get_scanner_key(filename: str) -> str | None:
    for suffix in SCANNER_MAP:
        if filename.endswith(suffix):
            return suffix
    return None


def collect_client_json_hits(ddon_data_root: Path, target_values: set[int] | None = None) -> list[FlagHit]:
    hits: list[FlagHit] = []
    client_root = ddon_data_root / "client" / "03040008"
    if not client_root.exists():
        return hits

    for json_path in client_root.rglob("*.json"):
        scanner_key = get_scanner_key(json_path.name)
        if scanner_key is not None:
            payload = load_json(json_path)
            if not isinstance(payload, dict):
                continue
            rel = relative_path(json_path, ddon_data_root)
            scanner = SCANNER_MAP[scanner_key]
            hits.extend(cast(Iterable[FlagHit], scanner(json_path, payload, rel, target_values)))
            continue

        try:
            head = json_path.read_text(encoding="utf-8", errors="replace")[:2000]
        except OSError:
            continue
        if not all(keyword in head for keyword in SITUATION_KEYWORDS):
            continue
        payload = load_json(json_path)
        if payload is None:
            continue
        rel = relative_path(json_path, ddon_data_root)
        hits.extend(cast(Iterable[FlagHit], scan_npc_situation_data(json_path, payload, rel, target_values)))

    return hits