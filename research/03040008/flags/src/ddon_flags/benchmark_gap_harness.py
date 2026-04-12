"""Benchmark the current owner/dependency layer against representative quest expectations."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import orjson

from ._paths import DDON_DATA_ROOT, DEFAULT_UPSTREAM_ROOT, GENERATED_DIR
from .catalog_loader import load_known_targets
from .corpus_index import build_corpus_index
from .investigate_flags import build_payload, resolve_targets
from .json_cache import JsonCache


OUTPUT_JSON = GENERATED_DIR / "benchmark_gap_harness.json"
OUTPUT_ADOC = GENERATED_DIR / "benchmark_gap_harness.adoc"

MISS_MISSING_OWNER_INDEX = "missing_owner_index"
MISS_MISSING_OWNER_FLAG = "missing_owner_flag"
MISS_MISSING_DEPENDENCY_OWNER = "missing_dependency_owner"
MISS_MISSING_DEPENDENCY_FLAG = "missing_dependency_flag"
MISS_UNEXPECTED_DEPENDENCY = "unexpected_dependency"
MISS_MISSING_RELATIONSHIP_CONTEXT = "missing_relationship_context"

BENCHMARK_CASES: tuple[dict[str, Any], ...] = (
    {
        "case_id": "q0-q7-dependency",
        "quest_id": 5,
        "expect_owner_index": {"owner_quest_id": 70032001, "owner_family": "q7", "flag_values": [7390]},
        "expect_dependency": {"owner_quest_id": 70032001, "owner_family": "q7", "flag_values": [7390, 7496]},
        "expect_relationship_keys": ["quest_sequence"],
    },
    {
        "case_id": "q2-q6-dependency",
        "quest_id": 20090,
        "expect_owner_index": {"owner_quest_id": 60310000, "owner_family": "q6", "flag_values": [6972]},
        "expect_dependency": {"owner_quest_id": 60310000, "owner_family": "q6", "flag_values": [6972]},
        "expect_relationship_keys": [],
    },
    {
        "case_id": "q5-repeatable-sortie",
        "quest_id": 50300000,
        "expect_no_dependencies": True,
        "expect_relationship_keys": ["repeatable_sortie"],
    },
    {
        "case_id": "q6-tutorial-owner",
        "quest_id": 60000003,
        "expect_owner_index": {"owner_quest_id": 60310000, "owner_family": "q6", "flag_values": [6972]},
        "expect_dependency": {"owner_quest_id": 60310000, "owner_family": "q6", "flag_values": [6972]},
        "expect_relationship_keys": ["tutorial_scaffolding"],
    },
    {
        "case_id": "q7-no-external-dependency",
        "quest_id": 70032001,
        "expect_no_dependencies": True,
        "expect_relationship_keys": [],
    },
)


def _build_quest_payload(quest_id: int, *, catalog: list[Any], corpus_index: Any, json_cache: JsonCache) -> dict[str, Any]:
    targets, documented_targets = resolve_targets(catalog, "quest", quest_id)
    return build_payload(
        "quest",
        quest_id,
        documented_targets,
        targets,
        hits_by_value={},
        candidate_hits_by_value={},
        exe_results={},
        corpus_index=corpus_index,
        json_cache=json_cache,
    )


def _owner_map(entries: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {
        int(entry.get("owner_quest_id") or 0): entry
        for entry in entries
        if isinstance(entry, dict) and int(entry.get("owner_quest_id") or 0) > 0
    }


def _evaluate_owner_requirement(
    *,
    case_id: str,
    requirement: dict[str, Any],
    owner_entries: dict[int, dict[str, Any]],
    miss_owner_kind: str,
    miss_flag_kind: str,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    owner_quest_id = int(requirement.get("owner_quest_id") or 0)
    owner_family = str(requirement.get("owner_family") or "")
    owner_entry = owner_entries.get(owner_quest_id)
    if owner_entry is None:
        gaps.append(
            {
                "taxonomy": miss_owner_kind,
                "case_id": case_id,
                "owner_quest_id": owner_quest_id,
                "owner_family": owner_family,
                "details": f"Expected owner {owner_quest_id}/{owner_family} was missing.",
            }
        )
        return gaps

    actual_family = str(owner_entry.get("owner_family") or "")
    if owner_family and actual_family != owner_family:
        gaps.append(
            {
                "taxonomy": miss_owner_kind,
                "case_id": case_id,
                "owner_quest_id": owner_quest_id,
                "owner_family": actual_family,
                "details": f"Expected owner family {owner_family} but saw {actual_family}.",
            }
        )

    actual_flags = {int(value) for value in (owner_entry.get("flag_values") or []) if int(value) > 0}
    for flag_value in (requirement.get("flag_values") or []):
        flag_value = int(flag_value)
        if flag_value not in actual_flags:
            gaps.append(
                {
                    "taxonomy": miss_flag_kind,
                    "case_id": case_id,
                    "owner_quest_id": owner_quest_id,
                    "flag_value": flag_value,
                    "details": f"Expected flag {flag_value} was missing from owner {owner_quest_id}.",
                }
            )
    return gaps


def evaluate_case(case: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case["case_id"])
    quest_id = int(case["quest_id"])
    owner_indexes = _owner_map(payload.get("quest_owner_indexes") or [])
    dependency_targets = _owner_map(payload.get("quest_dependency_targets") or [])
    relationship_context = payload.get("quest_family_relationships") or {}

    gaps: list[dict[str, Any]] = []

    if case.get("expect_owner_index"):
        gaps.extend(
            _evaluate_owner_requirement(
                case_id=case_id,
                requirement=case["expect_owner_index"],
                owner_entries=owner_indexes,
                miss_owner_kind=MISS_MISSING_OWNER_INDEX,
                miss_flag_kind=MISS_MISSING_OWNER_FLAG,
            )
        )

    if case.get("expect_dependency"):
        gaps.extend(
            _evaluate_owner_requirement(
                case_id=case_id,
                requirement=case["expect_dependency"],
                owner_entries=dependency_targets,
                miss_owner_kind=MISS_MISSING_DEPENDENCY_OWNER,
                miss_flag_kind=MISS_MISSING_DEPENDENCY_FLAG,
            )
        )

    if case.get("expect_no_dependencies") and dependency_targets:
        gaps.append(
            {
                "taxonomy": MISS_UNEXPECTED_DEPENDENCY,
                "case_id": case_id,
                "details": f"Expected no dependency targets, but found owners {sorted(dependency_targets)}.",
            }
        )

    for key in case.get("expect_relationship_keys") or []:
        if relationship_context.get(key) is None:
            gaps.append(
                {
                    "taxonomy": MISS_MISSING_RELATIONSHIP_CONTEXT,
                    "case_id": case_id,
                    "details": f"Expected relationship context key '{key}' was missing.",
                }
            )

    return {
        "case_id": case_id,
        "quest_id": quest_id,
        "passed": not gaps,
        "gap_count": len(gaps),
        "owner_index_count": len(owner_indexes),
        "dependency_target_count": len(dependency_targets),
        "gaps": gaps,
    }


def build_benchmark_payload() -> dict[str, Any]:
    catalog = load_known_targets(DEFAULT_UPSTREAM_ROOT)
    corpus_index = build_corpus_index(DDON_DATA_ROOT)
    json_cache = JsonCache()

    case_results: list[dict[str, Any]] = []
    for case in BENCHMARK_CASES:
        payload = _build_quest_payload(int(case["quest_id"]), catalog=catalog, corpus_index=corpus_index, json_cache=json_cache)
        case_results.append(evaluate_case(case, payload))

    taxonomy_counts = Counter(
        gap["taxonomy"]
        for case in case_results
        for gap in case["gaps"]
    )
    return {
        "format": "benchmark_gap_harness.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "case_count": len(case_results),
            "passed_case_count": sum(1 for case in case_results if case["passed"]),
            "failed_case_count": sum(1 for case in case_results if not case["passed"]),
            "gap_count": sum(case["gap_count"] for case in case_results),
            "taxonomy_counts": dict(sorted(taxonomy_counts.items())),
        },
        "cases": case_results,
    }


def write_benchmark_reports(payload: dict[str, Any]) -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))

    summary = payload["summary"]
    lines = [
        "= Benchmark Gap Harness",
        ":toc: macro",
        ":toclevels: 2",
        ":toc-title: Contents",
        "",
        f"Generated at:: {payload['generated_at']}",
        f"Cases:: {summary['case_count']}",
        f"Passed:: {summary['passed_case_count']}",
        f"Failed:: {summary['failed_case_count']}",
        f"Gaps:: {summary['gap_count']}",
        "",
        "toc::[]",
        "",
        "== Miss Taxonomy",
        "",
    ]

    taxonomy_counts = summary.get("taxonomy_counts") or {}
    if taxonomy_counts:
        lines.append('[cols="2,1",options="header"]')
        lines.append("|===")
        lines.append("| Taxonomy | Count")
        lines.append("")
        for taxonomy, count in taxonomy_counts.items():
            lines.append(f"| {taxonomy} | {count}")
        lines.append("|===")
        lines.append("")
    else:
        lines.append("_No benchmark gaps detected._")
        lines.append("")

    lines.append("== Cases")
    lines.append("")
    for case in payload["cases"]:
        lines.append(f"=== {case['case_id']} / quest {case['quest_id']}")
        lines.append("")
        lines.append(f"* passed: {case['passed']}")
        lines.append(f"* owner indexes: {case['owner_index_count']}")
        lines.append(f"* dependency targets: {case['dependency_target_count']}")
        if not case["gaps"]:
            lines.append("* gaps: none")
            lines.append("")
            continue
        lines.append('[cols="2,4",options="header"]')
        lines.append("|===")
        lines.append("| Taxonomy | Details")
        lines.append("")
        for gap in case["gaps"]:
            lines.append(f"| {gap['taxonomy']} | {gap['details']}")
        lines.append("|===")
        lines.append("")

    OUTPUT_ADOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_benchmark_payload()
    write_benchmark_reports(payload)
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_ADOC}")
    print(f"Benchmark failed cases: {payload['summary']['failed_case_count']}")


if __name__ == "__main__":
    main()