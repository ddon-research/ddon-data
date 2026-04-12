"""Helpers for enriching hits with context from decoded MSS message sets."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .scan_utils import extract_localized, load_json, relative_path
from .source_metadata import enrich_hit_with_npc_ledger

if TYPE_CHECKING:
    from .corpus_index import CorpusIndex
    from .json_cache import JsonCache


def build_mss_lookup(
    ddon_data_root: Path,
    group_serials: set[int],
    msg_serials: set[int],
    *,
    corpus_index: "CorpusIndex | None" = None,
    json_cache: "JsonCache | None" = None,
) -> tuple[dict[int, list[dict[str, Any]]], dict[int, list[dict[str, Any]]]]:
    client_root = ddon_data_root / "client" / "03040008"
    if not client_root.exists() or (not group_serials and not msg_serials):
        return {}, {}

    by_group_serial: dict[int, list[dict[str, Any]]] = {}
    by_msg_serial: dict[int, list[dict[str, Any]]] = {}

    # Determine which MSS files to scan.
    if corpus_index is not None:
        mss_paths = corpus_index.mss_paths()
    else:
        mss_paths = list(client_root.rglob("*.mss.json"))

    for mss_path in mss_paths:
        if json_cache is not None:
            payload = json_cache.load(mss_path)
        else:
            payload = load_json(mss_path)
        if not isinstance(payload, dict):
            continue
        groups = payload.get("NativeMsgGroupArray", [])
        if not isinstance(groups, list):
            continue

        rel = relative_path(mss_path, ddon_data_root)
        for group in groups:
            if not isinstance(group, dict):
                continue

            group_serial = group.get("GroupSerial")
            if not isinstance(group_serial, int):
                group_serial = 0
            npc_id = group.get("NpcId") if isinstance(group.get("NpcId"), int) else 0
            npc_name_en, npc_name_jp = extract_localized(group.get("NpcName"))

            messages: list[dict[str, Any]] = []
            for msg in group.get("MsgData", []):
                if not isinstance(msg, dict):
                    continue
                msg_serial = msg.get("MsgSerial") if isinstance(msg.get("MsgSerial"), int) else 0
                msg_type = msg.get("MsgType") if isinstance(msg.get("MsgType"), int) else 0
                message_en, message_jp = extract_localized(msg.get("Message"))
                message_text = message_en or message_jp
                if not (group_serial in group_serials or msg_serial in msg_serials):
                    continue
                entry = {
                    "file_path": rel,
                    "group_serial": group_serial,
                    "msg_serial": msg_serial,
                    "msg_type": msg_type,
                    "npc_id": npc_id,
                    "npc_name": npc_name_en,
                    "npc_name_jp": npc_name_jp,
                    "message": message_en,
                    "message_jp": message_jp,
                    "message_excerpt": message_text.splitlines()[0] if message_text else "",
                }
                messages.append(entry)
                if msg_serial in msg_serials:
                    by_msg_serial.setdefault(msg_serial, []).append(entry)

            if group_serial in group_serials:
                if messages:
                    by_group_serial.setdefault(group_serial, []).extend(messages)
                else:
                    by_group_serial.setdefault(group_serial, []).append(
                        {
                            "file_path": rel,
                            "group_serial": group_serial,
                            "msg_serial": 0,
                            "msg_type": 0,
                            "npc_id": npc_id,
                            "npc_name": npc_name_en,
                            "npc_name_jp": npc_name_jp,
                            "message": "",
                            "message_jp": "",
                            "message_excerpt": "",
                        }
                    )

    return by_group_serial, by_msg_serial


def enrich_hit_dicts_with_mss(
    ddon_data_root: Path,
    hit_dicts: list[dict[str, Any]],
    *,
    corpus_index: "CorpusIndex | None" = None,
    json_cache: "JsonCache | None" = None,
) -> list[dict[str, Any]]:
    group_serials = {
        int(hit["group_serial"])
        for hit in hit_dicts
        if isinstance(hit.get("group_serial"), int) and int(hit["group_serial"]) != 0
    }
    msg_serials = {
        int(hit["msg_serial"])
        for hit in hit_dicts
        if isinstance(hit.get("msg_serial"), int) and int(hit["msg_serial"]) != 0
    }
    if not group_serials and not msg_serials:
        return [enrich_hit_with_npc_ledger(hit) for hit in hit_dicts]

    by_group_serial, by_msg_serial = build_mss_lookup(
        ddon_data_root,
        group_serials,
        msg_serials,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )

    enriched: list[dict[str, Any]] = []
    for hit in hit_dicts:
        cloned = dict(hit)
        matches: list[dict[str, Any]] = []

        group_serial = cloned.get("group_serial")
        if isinstance(group_serial, int) and group_serial in by_group_serial:
            matches.extend(by_group_serial[group_serial])

        msg_serial = cloned.get("msg_serial")
        if isinstance(msg_serial, int) and msg_serial in by_msg_serial:
            matches.extend(by_msg_serial[msg_serial])

        if matches:
            deduped = []
            seen: set[tuple[str, int, int]] = set()
            for match in matches:
                key = (str(match["file_path"]), int(match["group_serial"]), int(match["msg_serial"]))
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(match)
            cloned["mss_matches"] = deduped

            first = deduped[0]
            if not cloned.get("npc_id") and first.get("npc_id"):
                cloned["npc_id"] = first["npc_id"]
            if not cloned.get("npc_name") and first.get("npc_name"):
                cloned["npc_name"] = first["npc_name"]
            if not cloned.get("npc_name_jp") and first.get("npc_name_jp"):
                cloned["npc_name_jp"] = first["npc_name_jp"]

        enriched.append(enrich_hit_with_npc_ledger(cloned))

    return enriched
