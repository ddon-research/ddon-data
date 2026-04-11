"""Triage residual empty targets against decoded JSON candidate fields."""
from __future__ import annotations

import json
from pathlib import Path

from candidate_finder import collect_candidate_json_hits


DDON_DATA_ROOT = Path(r"D:\ddon-data")
FLAGS_DIR = Path(__file__).resolve().parent
GENERATED_DIR = FLAGS_DIR / "generated"
EMPTY_PATH = GENERATED_DIR / "empty_flags.json"
OUTPUT_JSON = GENERATED_DIR / "residual_empty_triage.json"
OUTPUT_MD = GENERATED_DIR / "residual_empty_triage.md"


def main() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    empty_targets = json.loads(EMPTY_PATH.read_text(encoding="utf-8")) if EMPTY_PATH.exists() else []
    target_kinds = {int(row["flag_value"]): str(row["flag_type"]) for row in empty_targets}
    candidates = collect_candidate_json_hits(DDON_DATA_ROOT, target_kinds)

    payload = {
        "targets": empty_targets,
        "candidate_hits": {str(value): hits[:50] for value, hits in candidates.items()},
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Residual Empty Target Triage",
        "",
        f"- targets: {len(empty_targets)}",
        "",
    ]
    for row in empty_targets:
        value = int(row["flag_value"])
        hits = candidates.get(value, [])
        lines.append(f"## {row['quest_id']} / {row['flag_type']} / {value}")
        lines.append("")
        if not hits:
            lines.append("_No decoded candidate fields found._")
            lines.append("")
            continue
        lines.append("| Tier | Confidence | Field | File | Why | Context |")
        lines.append("|------|------------|-------|------|-----|---------|")
        for hit in hits[:20]:
            context_parts = [
                hit.get("quest_name") or "",
                hit.get("stage_name") or "",
                hit.get("npc_name") or "",
                hit.get("function_name") or "",
                hit.get("message_excerpt") or "",
                hit.get("comment") or "",
            ]
            context = " | ".join(part for part in context_parts if part)
            lines.append(
                f"| {hit['evidence_tier']} | {hit['confidence']} | {hit['field_name']} | {hit['file_path']} | {hit['why']} | {context} |"
            )
        lines.append("")

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()
