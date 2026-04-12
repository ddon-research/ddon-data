"""Triage residual empty targets against decoded JSON candidate fields."""
from __future__ import annotations

import orjson

from ._paths import DDON_DATA_ROOT as DATA_ROOT
from ._paths import GENERATED_DIR
from .asciidoc_links import build_json_file_link
from .candidate_finder import collect_candidate_json_hits


EMPTY_PATH = GENERATED_DIR / "empty_flags.json"
OUTPUT_JSON = GENERATED_DIR / "residual_empty_triage.json"
OUTPUT_ADOC = GENERATED_DIR / "residual_empty_triage.adoc"


def main() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    empty_targets = orjson.loads(EMPTY_PATH.read_bytes()) if EMPTY_PATH.exists() else []
    target_kinds = {int(row["flag_value"]): str(row["flag_type"]) for row in empty_targets}
    candidates = collect_candidate_json_hits(DATA_ROOT, target_kinds)

    payload = {
        "targets": empty_targets,
        "candidate_hits": {str(value): hits[:50] for value, hits in candidates.items()},
    }
    OUTPUT_JSON.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))

    lines = [
        "= Residual Empty Target Triage",
        ":toc: macro",
        ":toclevels: 2",
        ":toc-title: Contents",
        "",
        f"targets:: {len(empty_targets)}",
        "",
        "toc::[]",
        "",
    ]
    for row in empty_targets:
        value = int(row["flag_value"])
        hits = candidates.get(value, [])
        lines.append(f"== {row['quest_id']} / {row['flag_type']} / {value}")
        lines.append("")
        if not hits:
            lines.append("_No decoded candidate fields found._")
            lines.append("")
            continue
        lines.append('[cols="1,1,2,3,3,3",options="header"]')
        lines.append("|===")
        lines.append("| Tier | Confidence | Field | File | Why | Context")
        lines.append("")
        for hit in hits[:20]:
            context_parts = [
                hit.get("quest_name") or "",
                hit.get("stage_name") or "",
                hit.get("npc_name") or "",
                hit.get("function_name") or "",
                hit.get("message_excerpt") or "",
                hit.get("comment") or "",
            ]
            context = " / ".join(part for part in context_parts if part)
            file_link = build_json_file_link(
                str(hit.get("file_path") or ""),
                report_dir=OUTPUT_ADOC.parent,
                json_path=str(hit.get("json_path") or ""),
            )
            lines.append(
                f"| {hit['evidence_tier']} | {hit['confidence']} | {hit['field_name']} | {file_link} | {hit['why']} | {context}"
            )
        lines.append("|===")
        lines.append("")

    OUTPUT_ADOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_ADOC}")


if __name__ == "__main__":
    main()
