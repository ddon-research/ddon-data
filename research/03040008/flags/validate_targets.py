"""
Test all user-specified quest/flag combinations and report which ones
produce zero hits from the structured scanner.
"""
import sys, io, orjson
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pathlib import Path
from client_scanner import collect_client_json_hits
from manifest import AUTHORITATIVE_WORLD_MANAGE_TARGETS

DDON_DATA_ROOT = Path(__file__).resolve().parents[3]
GENERATED_DIR = Path(__file__).resolve().parent / "generated"

TARGETS = {
    quest_id: {
        "quest_flags": list(values["quest_flags"]),
        "layout_flags": list(values["layout_flags"]),
    }
    for quest_id, values in AUTHORITATIVE_WORLD_MANAGE_TARGETS.items()
}


def collect_all_values() -> set[int]:
    all_values: set[int] = set()
    for data in TARGETS.values():
        all_values.update(data["quest_flags"])
        all_values.update(data["layout_flags"])
    return all_values


def index_hits_by_value(all_values: set[int]) -> dict[int, list]:
    print(f"Scanning for {len(all_values)} unique flag/quest values...")
    all_hits = collect_client_json_hits(DDON_DATA_ROOT, all_values)
    print(f"Total hits: {len(all_hits)}")
    hits_by_value: dict[int, list] = {}
    for hit in all_hits:
        hits_by_value.setdefault(hit.flag_value, []).append(hit)
    return hits_by_value


def report_quest_targets(quest_id: int, data: dict[str, list[int]], hits_by_value: dict[int, list], empty_flags: list, found_flags: list) -> None:
    print(f"\n{'='*70}")
    print(f"  Quest {quest_id}")
    print(f"{'='*70}")
    for flag_type, flags in (("quest_flag", data["quest_flags"]), ("layout_flag", data["layout_flags"])):
        if not flags:
            continue
        print(f"\n  --- {flag_type}s ---")
        for flag_value in sorted(flags):
            hits = hits_by_value.get(flag_value, [])
            if hits:
                sources = {hit.source_type for hit in hits}
                relationships = {hit.relationship for hit in hits}
                print(
                    f"  {flag_value:>6}  {len(hits):>4} hits  sources={','.join(sorted(sources))}  rels={','.join(sorted(relationships))}"
                )
                found_flags.append((quest_id, flag_type, flag_value, len(hits), sources))
            else:
                print(f"  {flag_value:>6}  ---- EMPTY ----")
                empty_flags.append((quest_id, flag_type, flag_value))


def write_empty_flags(empty_flags: list[tuple[int, str, int]]) -> Path:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    empty_path = GENERATED_DIR / "empty_flags.json"
    empty_path.write_bytes(
        orjson.dumps(
            [{"quest_id": quest_id, "flag_type": flag_type, "flag_value": flag_value} for quest_id, flag_type, flag_value in empty_flags],
            option=orjson.OPT_INDENT_2,
        ),
    )
    return empty_path

def main() -> None:
    all_values = collect_all_values()
    hits_by_value = index_hits_by_value(all_values)
    empty_flags: list[tuple[int, str, int]] = []
    found_flags: list[tuple[int, str, int, int, set[str]]] = []

    for quest_id, data in sorted(TARGETS.items()):
        report_quest_targets(quest_id, data, hits_by_value, empty_flags, found_flags)

    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total unique values tested: {len(all_values)}")
    print(f"  Values with hits: {len(found_flags)}")
    print(f"  Values with ZERO hits: {len(empty_flags)}")

    if empty_flags:
        print("\n  EMPTY FLAGS (zero hits from structured scanner):")
        for quest_id, flag_type, flag_value in empty_flags:
            print(f"    quest={quest_id}  {flag_type}  value={flag_value}")

    empty_path = write_empty_flags(empty_flags)
    print(f"\n  Empty flags written to: {empty_path}")


if __name__ == "__main__":
    main()
