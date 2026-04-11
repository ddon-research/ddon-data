# Client Flag and Quest Investigation

Tooling for investigating quest, layout, NPC, marker, evidence, and related state associations from decoded Dragon's Dogma Online client resources.

## Scope

- Corpus: `client/03040008` (decoded JSON files)
- Optional executable fallback: `DDO.exe` immediate-operand scan
- Output: `generated/` (JSON + AsciiDoc per query)
- Upstream Arrowgene docs are used only for target labels and seed targets, not as primary evidence

Generic for any decoded client quest. Not limited to world-manage quests.

## Architecture

Entry point: `investigate_flags.py`. Orchestrates corpus indexing, structured scanning, candidate search, enrichment, and report generation.

### Module Map

| Module | Role |
|---|---|
| `investigate_flags.py` | CLI entry point. Single-quest, batch, and full-corpus modes. |
| `corpus_index.py` | Single-pass file index classifying ~173K JSON files by scanner suffix. |
| `json_cache.py` | In-memory cache for ~40K parsed JSON payloads (orjson). |
| `client_scanner.py` | Structured scan dispatcher. Routes files to handlers via `SCANNER_MAP`. |
| `handlers/` | Scanner sub-package. 7 modules, 18 scan functions, re-exported via `__init__.py`. |
| `handlers/_helpers.py` | Shared private helpers (context builders, field extractors). |
| `handlers/quest_handlers.py` | QST scanner (`scan_qst_file`). |
| `handlers/layout_handlers.py` | GPL + LOT scanners. |
| `handlers/fsm_handlers.py` | FSM scanner with recursive process iterator. |
| `handlers/marker_handlers.py` | EVSI + QMI/FMI scanners. |
| `handlers/npc_handlers.py` | NLL + NPC/SMC situation data scanners. |
| `handlers/special_handlers.py` | FAA, EVP, EVD, CSI, ESI, JTQ, TQG, JMC, AMS scanners. |
| `candidate_finder.py` | Deep recursive JSON walk for unresolved targets. |
| `scan_models.py` | `FlagHit` frozen dataclass and scanner type aliases. |
| `scan_utils.py` | JSON loading, path utilities, pattern constants. |
| `catalog_loader.py` | Target catalog from upstream docs, NPC ledger, world-manage tables. |
| `source_metadata.py` | Stage names, event names, item names, ARC context, special-resource lookups. |
| `mss_enrichment.py` | MSS message-set NPC name and excerpt resolution. |
| `manifest.py` | Authoritative q7 world-manage quest/flag target set. |
| `report_writer.py` | JSON + AsciiDoc report generation. |
| `executable_scanner.py` | Optional `DDO.exe` immediate-operand scan. |
| `validate_targets.py` | Manifest validation: reports targets with zero hits. |
| `triage_residuals.py` | Candidate triage for zero-hit targets. |

### Data Flow

```
corpus_index  ->  client_scanner  ->  handlers/*  ->  FlagHit[]
                        |
json_cache  -----------+
                        |
candidate_finder  <-----+  (unresolved targets only)
                        |
mss_enrichment  --------+
                        |
report_writer  ---------+->  .json + .adoc
```

In batch mode (`--all-client-quests`), the corpus index and cache are built once, all quests share a single structured scan pass, and unresolved targets across all quests are batched into one candidate search.

## Query Modes

| Mode | Behavior |
|---|---|
| `--flag <value>` | Scan one numeric flag value across the corpus. |
| `--quest <quest_id>` | Investigate one quest: resolve targets, scan, report. |
| `--all-quests` | Batch the curated q7 world-manage set from `manifest.py`. |
| `--all-client-quests` | Batch every `q########` folder under `client/03040008/quest/`. |

## Evidence Model

Priority order:

1. Decoded client JSON under `client/03040008`
2. Optional executable immediate-operand scan
3. Upstream docs for target selection and interpretation context only

Container and sequencing resources are not direct evidence unless they expose authored quest, flag, or layout fields.

## Quest-Family Semantics

| Family | Source | Behavior |
|---|---|---|
| q5 repeatable sorties | `*.esi.json`, `*.csi.json` | Derive sortie gate flags and `CycleSubNo` targets. |
| q6 tutorial quests | `*.jtq.json`, `*.tqg.json`, `*.jmc.json` | Quest-wide tutorial association scan + job-master context. |
| q7 world-manage | `manifest.py` + upstream catalog | Authoritative quest/layout targets merged with decoded evidence. |
| Evidence-backed | `evidence.evd.json` | Evidence-step quest flags for season 3 investigation substory. |
| AMS-blocked | `am_spot_*.ams.json` | Quest-id target when a map spot is gated by that quest. |
| Other | generic `--quest` | Direct authored references + special-resource fallbacks. |

## Client File Families

| Family | Files | Semantics |
|---|---|---|
| QST | `quest/q*/**/*.qst.json` | Quest-stage behavior: conditions, erase conditions, text quest refs, OM control chains. |
| GPL | `stage/**/etc/*.gpl.json` | Layout-group guards: `QuestNo` + `LayoutFlagNo`. |
| LOT | `stage/**/etc/*.lot.json` | Placed objects: NPCs, enemies, warps, doors, interactables. Turns GPL/marker hits into concrete context. |
| QMI/FMI | `quest/**/*.qmi.json`, `*.fmi.json` | Quest/field marker data. `GroupNo` links to LOT placements. |
| FSM | `npc/**/*.fsm.json`, `quest/**/npc/*.fsm.json` | State machine flag checks/sets. NPC visibility, behavior, MyQuest gating. |
| EVSI | `EventViewRoom/**/ev*.evsi.json` | Event viewer replay/cinematic state references. |
| EVP | `event/**/*.evp.json` | Event parameter quest/flag associations. |
| SMC | `npc/**/ui/00_message/**/*.smc.json` | NPC chatter windows: `StartQuestId`/`EndQuestId` + `GroupSerial`. |
| MSS | `**/*.mss.json` | Message-set text. Resolves `GroupSerial`, NPC names, message excerpts. |
| NLL | `npc/npc_common/etc/npc/npc.nll.json` | NPC ledger: names, function metadata, fallback name resolution. |
| FAA | `field_area/**/*.faa.json` | Area-adjoin/stage-transition gating. |
| ESI/CSI | `game_common/quest/*.esi.json`, `*.csi.json` | Repeatable sortie registry and cycle routing. |
| JTQ/TQG/JMC | `game_common/quest/*.jtq.json`, `*.tqg.json`, `etc/jobMasterCtrl.jmc.json` | Tutorial quest registry, grouping, job-master onboarding. |
| EVD | `ui/menu_evidence_list/**/evidence.evd.json` | Evidence-chain registry: items, steps, quest/flag associations. |
| AMS | `ui/uGUIAreaMaster/**/am_spot_*.ams.json` | Map-spot quest gating. |

## Enrichment

- Stage names: `base/scr/stage_list.slt.json`
- Event names: `EventViewRoom/ui/00_message/event/event_name.gmd.json`
- Item names: `base/etc/itemlist.ipa.json`
- ARC context: `quest/q<id>.arc.json` (bundle association, not direct evidence)
- NPC names: MSS match first, then NLL fallback by `npc_id` or `n####` asset ID

## Generated Outputs

| File | Format |
|---|---|
| `generated/client_investigation_quest_<id>.json` | Structured JSON report |
| `generated/client_investigation_quest_<id>.adoc` | AsciiDoc report with auto-generated TOC |
| `generated/client_investigation_flag_<value>.json` | Single-flag JSON report |
| `generated/client_investigation_flag_<value>.adoc` | Single-flag AsciiDoc report |
| `generated/empty_flags.json` | Zero-hit targets from validation |
| `generated/residual_empty_triage.json` | Candidate triage for zero-hit targets |
| `generated/residual_empty_triage.adoc` | Candidate triage AsciiDoc report |

AsciiDoc reports use `:toc: macro` for automatic table-of-contents generation. Static family interpretations live in this README, not in per-report output.

## Interpretation Notes

- QST OM-control patterns (`ENEMY -> OM`, `OM -> OM`, `ENEMY -> ENEMY -> OM`) indicate key-enemy doors, lever chains, multi-object control logic.
- GPL-to-LOT association classifies guarded groups as warp, door, or object groups.
- AMS hits are spot-availability gates, not flavor references.
- EVD rows are evidence-flow progression data for the season 3 substory system.
- SMC rows are quest-gated chatter availability, not generic NPC state.
- QSQ is omitted: drives quest ordering/UI sequencing, not world-state gating.

## Performance

### Dependencies

- [orjson](https://github.com/ijl/orjson) for JSON parsing/serialization (required)

### mypyc Compilation

The hot-path modules compile to C extensions with [mypyc](https://mypyc.readthedocs.io/) for ~30% speedup. Requires a C compiler (MSVC on Windows).

Setup:

```sh
uv venv --python 3.14 .venv
uv pip install mypy setuptools orjson --python .venv/Scripts/python.exe
```

Compile:

```sh
.venv/Scripts/python.exe -m mypyc \
    scan_utils.py scan_models.py client_scanner.py \
    corpus_index.py json_cache.py candidate_finder.py \
    handlers/_helpers.py handlers/quest_handlers.py handlers/layout_handlers.py \
    handlers/fsm_handlers.py handlers/marker_handlers.py handlers/npc_handlers.py \
    handlers/special_handlers.py
```

Produces `.pyd` (Windows) or `.so` (Linux) files. CPython prefers compiled extensions at import time. Recompile after modifying any of the above files. Delete `.pyd`/`.so` and `build/` to revert to interpreted mode.

Verify:

```sh
.venv/Scripts/python.exe -m unittest test_regression -v
```

## Commands

```sh
# Single quest
python investigate_flags.py --quest 70032001 --skip-executable-scan

# Single flag
python investigate_flags.py --flag 1109 --skip-executable-scan

# Curated q7 world-manage batch
python investigate_flags.py --all-quests --skip-executable-scan

# All client quests
python investigate_flags.py --all-client-quests --skip-executable-scan

# Validation and triage
python validate_targets.py
python triage_residuals.py
```
