"""Residual/statistical experiments built on the deterministic and graph layers."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import orjson

from ._paths import DDON_DATA_ROOT, DEFAULT_UPSTREAM_ROOT, GENERATED_DIR
from .benchmark_gap_harness import BENCHMARK_CASES
from .candidate_finder import collect_candidate_json_hits
from .catalog_loader import load_known_targets
from .corpus_index import build_corpus_index
from .investigate_flags import build_payload, collect_direct_hits, resolve_targets
from .json_cache import JsonCache
from .source_metadata import enrich_hit_with_npc_ledger


OUTPUT_JSON = GENERATED_DIR / "graph_residual_experiments.json"
OUTPUT_ADOC = GENERATED_DIR / "graph_residual_experiments.adoc"


def _build_case_payload(
    quest_id: int,
    *,
    catalog: list[Any],
    corpus_index: Any,
    json_cache: JsonCache,
    shared_hits_by_value: dict[int, list[dict[str, Any]]],
    shared_candidate_hits_by_value: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    targets, documented_targets = resolve_targets(catalog, "quest", quest_id)
    target_values = {target.flag_value for target in targets}
    hits_by_value = {value: shared_hits_by_value.get(value, []) for value in target_values}
    candidate_hits_by_value = {value: shared_candidate_hits_by_value.get(value, []) for value in target_values}
    return build_payload(
        "quest",
        quest_id,
        documented_targets,
        targets,
        hits_by_value=hits_by_value,
        candidate_hits_by_value=candidate_hits_by_value,
        exe_results={},
        corpus_index=corpus_index,
        json_cache=json_cache,
    )


def build_experiment_payload() -> dict[str, Any]:
    catalog = load_known_targets(DEFAULT_UPSTREAM_ROOT)
    corpus_index = build_corpus_index(DDON_DATA_ROOT)
    json_cache = JsonCache()

    case_targets: dict[int, tuple[list[Any], list[Any]]] = {}
    all_target_values: set[int] = set()
    for case in BENCHMARK_CASES:
        quest_id = int(case["quest_id"])
        targets, documented_targets = resolve_targets(catalog, "quest", quest_id)
        case_targets[quest_id] = (targets, documented_targets)
        all_target_values.update(target.flag_value for target in targets)

    _all_hits, shared_hits_by_value = collect_direct_hits(
        DDON_DATA_ROOT,
        all_target_values,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )

    unresolved_target_kinds: dict[int, str] = {}
    for targets, _documented_targets in case_targets.values():
        for target in targets:
            if target.flag_value not in shared_hits_by_value:
                unresolved_target_kinds[target.flag_value] = target.flag_type or "quest_flag"

    shared_candidate_hits_by_value = collect_candidate_json_hits(
        DDON_DATA_ROOT,
        unresolved_target_kinds,
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    for flag_value, hits in shared_candidate_hits_by_value.items():
        shared_candidate_hits_by_value[flag_value] = [enrich_hit_with_npc_ledger(hit) for hit in hits]

    cases: list[dict[str, Any]] = []
    aggregate_candidate_tiers: Counter[str] = Counter()
    aggregate_derivation: Counter[str] = Counter()
    for case in BENCHMARK_CASES:
        quest_id = int(case["quest_id"])
        payload = _build_case_payload(
            quest_id,
            catalog=catalog,
            corpus_index=corpus_index,
            json_cache=json_cache,
            shared_hits_by_value=shared_hits_by_value,
            shared_candidate_hits_by_value=shared_candidate_hits_by_value,
        )

        direct_hit_count = sum(len(target.get("hits", [])) for target in payload.get("targets", []))
        candidate_hit_count = sum(len(target.get("candidate_hits", [])) for target in payload.get("targets", []))
        candidate_tiers = Counter(
            str(hit.get("evidence_tier") or "candidate")
            for target in payload.get("targets", [])
            for hit in target.get("candidate_hits", [])
        )
        derivation_counts = Counter(payload.get("quest_graph_expansion", {}).get("derivation_counts") or {})

        aggregate_candidate_tiers.update(candidate_tiers)
        aggregate_derivation.update(derivation_counts)

        cases.append(
            {
                "case_id": str(case["case_id"]),
                "quest_id": quest_id,
                "graph_node_count": int(payload.get("quest_graph_expansion", {}).get("node_count") or 0),
                "graph_edge_count": int(payload.get("quest_graph_expansion", {}).get("edge_count") or 0),
                "owner_index_count": len(payload.get("quest_owner_indexes") or []),
                "dependency_target_count": len(payload.get("quest_dependency_targets") or []),
                "direct_hit_count": direct_hit_count,
                "candidate_hit_count": candidate_hit_count,
                "candidate_tiers": dict(sorted(candidate_tiers.items())),
                "graph_derivation_counts": dict(sorted(derivation_counts.items())),
            }
        )

    return {
        "format": "graph_residual_experiments.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "case_count": len(cases),
            "aggregate_candidate_tiers": dict(sorted(aggregate_candidate_tiers.items())),
            "aggregate_graph_derivation": dict(sorted(aggregate_derivation.items())),
        },
        "cases": cases,
    }


def write_experiment_reports(payload: dict[str, Any]) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
    summary = payload["summary"]
    lines = [
        "= Graph Residual Experiments",
        ":toc: macro",
        ":toclevels: 2",
        ":toc-title: Contents",
        "",
        f"Generated at:: {payload['generated_at']}",
        f"Cases:: {summary['case_count']}",
        "",
        "toc::[]",
        "",
        "== Aggregate Candidate Tiers",
        "",
    ]
    candidate_tiers = summary.get("aggregate_candidate_tiers") or {}
    if candidate_tiers:
        lines.append('[cols="2,1",options="header"]')
        lines.append("|===")
        lines.append("| Tier | Count")
        lines.append("")
        for tier, count in candidate_tiers.items():
            lines.append(f"| {tier} | {count}")
        lines.append("|===")
        lines.append("")
    else:
        lines.append("_No candidate hits were produced for the experiment set._")
        lines.append("")

    lines.append("== Aggregate Graph Derivation")
    lines.append("")
    graph_derivation = summary.get("aggregate_graph_derivation") or {}
    if graph_derivation:
        lines.append('[cols="2,1",options="header"]')
        lines.append("|===")
        lines.append("| Derivation | Count")
        lines.append("")
        for derivation, count in graph_derivation.items():
            lines.append(f"| {derivation} | {count}")
        lines.append("|===")
        lines.append("")
    else:
        lines.append("_No graph derivation counts were produced._")
        lines.append("")

    lines.append("== Cases")
    lines.append("")
    for case in payload["cases"]:
        lines.append(f"=== {case['case_id']} / quest {case['quest_id']}")
        lines.append("")
        lines.append(f"* graph nodes: {case['graph_node_count']}")
        lines.append(f"* graph edges: {case['graph_edge_count']}")
        lines.append(f"* owner indexes: {case['owner_index_count']}")
        lines.append(f"* dependency targets: {case['dependency_target_count']}")
        lines.append(f"* direct hits: {case['direct_hit_count']}")
        lines.append(f"* candidate hits: {case['candidate_hit_count']}")
        lines.append("")

    OUTPUT_ADOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_experiment_payload()
    write_experiment_reports(payload)
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_ADOC}")


if __name__ == "__main__":
    main()