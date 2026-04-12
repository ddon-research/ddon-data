"""Decoded client JSON traversal and scanner dispatch."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterable, cast

from .client_scan_handlers import (
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
from .scan_models import FlagHit
from .scan_utils import relative_path

if TYPE_CHECKING:
    from .corpus_index import CorpusIndex
    from .json_cache import JsonCache


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


def get_scanner_key(filename: str) -> str | None:
    for suffix in SCANNER_MAP:
        if filename.endswith(suffix):
            return suffix
    return None


def collect_client_json_hits(
    ddon_data_root: Path,
    target_values: set[int] | None = None,
    *,
    corpus_index: "CorpusIndex | None" = None,
    json_cache: "JsonCache | None" = None,
) -> list[FlagHit]:
    """Scan decoded client JSON for target flag/quest values.

    When *corpus_index* and *json_cache* are provided the scan avoids
    repeated ``rglob`` traversals and disk I/O — critical for batch mode.
    """
    hits: list[FlagHit] = []

    if corpus_index is not None:
        return _scan_indexed(ddon_data_root, target_values, corpus_index, json_cache)

    # Legacy path — full rglob walk (single-quest ad-hoc runs)
    client_root = ddon_data_root / "client" / "03040008"
    if not client_root.exists():
        return hits

    for json_path in client_root.rglob("*.json"):
        scanner_key = get_scanner_key(json_path.name)
        if scanner_key is None:
            continue
        payload = _load(json_path, json_cache)
        if not isinstance(payload, dict):
            continue
        rel = relative_path(json_path, ddon_data_root)
        scanner = SCANNER_MAP[scanner_key]
        hits.extend(cast(Iterable[FlagHit], scanner(json_path, payload, rel, target_values)))

    return hits


def _scan_indexed(
    ddon_data_root: Path,
    target_values: set[int] | None,
    corpus_index: "CorpusIndex",
    json_cache: "JsonCache | None",
) -> list[FlagHit]:
    """Scan using a pre-built corpus index (fast path)."""
    hits: list[FlagHit] = []
    for suffix, json_path in corpus_index.all_scanner_paths():
        payload = _load(json_path, json_cache)
        if not isinstance(payload, dict):
            continue
        rel = relative_path(json_path, ddon_data_root)
        scanner = SCANNER_MAP[suffix]
        hits.extend(cast(Iterable[FlagHit], scanner(json_path, payload, rel, target_values)))
    return hits


def _load(path: Path, cache: "JsonCache | None") -> dict | list | None:
    if cache is not None:
        return cache.load(path)
    from .scan_utils import load_json
    return load_json(path)