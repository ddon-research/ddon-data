# Client Flag and Quest Investigation

Technical tooling for resolving quest, layout, marker, NPC, evidence,
and related state associations from decoded Dragon's Dogma Online client
resources.

## Business Logic

### Investigation Model

- Primary evidence comes from decoded client JSON under `client/03040008`.
- A query resolves target values, scans structured resource families,
  enriches matching hits, ranks unresolved candidates, and writes JSON plus
  AsciiDoc reports.
- Direct authored hits remain separate from reusable owner catalogs,
  promoted dependency targets, bounded graph context, and lower-confidence
  candidate matches.
- Optional `DDO.exe` immediate-operand scanning is a fallback layer, not the
  primary discovery path.

### Family-Specific Rules

| Family | Current handling |
|---|---|
| `q0` | Main-quest investigations add quest-sequence context in addition to shared stage topology and direct authored references. |
| `q4` | Light and board quests are treated as local quest-packaging problems, using archive topology and quest text/message resources. |
| `q5` | Repeatable sortie logic is derived from `ESI` and `CSI`, including sortie flags and `CycleSubNo` associations. |
| `q6` | Tutorial, unlock, and area-trial quests add `JTQ`, `TQG`, and `JMC` scaffolding and can surface conservative q6 owner dependencies. |
| `q7` | World-manage queries use curated direct targets plus client-derived owner state from self-owned QST, EVSI, and GPL evidence. |
| `q8` | Partner Pawn Personal Quest handling recognizes `PQT` packaging and keeps these quests distinct from q6 tutorial logic. |
| Other families | Use the shared direct-scan, stage-topology, candidate, and graph paths without extra family-specific tables. |

### Query Modes

| Mode | Purpose |
|---|---|
| `--flag <value>` | Scan one numeric value across the decoded client corpus. |
| `--quest <quest_id>` | Resolve one quest's target set and generate reports. |
| `--all-quests` | Batch the curated q7 world-manage set from `manifest.py`. |
| `--all-client-quests` | Batch every decoded client quest archive under `client/03040008/quest/`. |

### Evidence and Derivation

- `targets[].hits` contains direct decoded matches for resolved quest or flag
  targets.
- `targets[].candidate_hits` contains lower-confidence decoded matches for
  unresolved targets.
- `quest_owner_indexes` contains reusable external owner catalogs discovered
  from stage-neighborhood cues.
- `quest_dependency_targets` contains the promoted subset of owner data that
  passes current family-specific dependency rules.
- `quest_graph_expansion` contains bounded graph context across quest, stage,
  owner, dependency, event-viewer, GPL, LOT, and family-table edges.
- `derivation_class` records whether a result is direct, owner-index,
  dependency-inferred, graph-expanded, lower-confidence, or binary-auxiliary.

## Technical Setup

### Inputs and Outputs

- Decoded corpus: `client/03040008`
- Optional executable scan target: `D:\DDON_03040008\DDO.exe`
- Generated reports: `generated/`
- Upstream Arrowgene docs: seed targets and labels only

### Project Layout

```text
flags/
  .python-version
  pyproject.toml
  requirements.txt
  uv.lock
  build_mypyc.py
  clean_artifacts.py
  investigate_flags.py
  validate_targets.py
  triage_residuals.py
  benchmark_gap_harness.py
  graph_residual_experiments.py
  src/ddon_flags/
  tests/
  generated/
  test_baselines/
```

- Implementation code lives under `src/ddon_flags`.
- Root-level Python scripts are compatibility wrappers that preserve the old
  command surface.
- `requirements.txt` exists as a compatibility export. `pyproject.toml` plus
  `uv.lock` are the primary project definition.

### Prerequisites

- CPython 3.14 only
- `uv` for environment and dependency management
- `orjson` for runtime JSON parsing and report serialization
- Optional C compiler plus `mypy`, `setuptools`, and `wheel` for `mypyc`
  acceleration
- Optional `objdump` if executable fallback scanning is enabled

### Environment Setup

Bootstrap the local project environment with `uv`:

```sh
uv venv --python 3.14 .venv-cpython314
uv lock
uv pip install -e ".[dev,mypyc]" --python .venv-cpython314/Scripts/python.exe
```

Notes:

- `.python-version` pins the project to Python 3.14.
- The package performs a runtime guard and will refuse non-CPython or non-3.14
  interpreters.
- The root `d:/ddon-data/.venv` environment is not used for this subproject.

### Common Commands

Use the project environment directly:

```sh
# Single quest via the preserved root wrapper
.venv-cpython314/Scripts/python.exe investigate_flags.py --quest 70032001 --skip-executable-scan

# Single flag
.venv-cpython314/Scripts/python.exe investigate_flags.py --flag 1109 --skip-executable-scan

# Curated q7 world-manage batch
.venv-cpython314/Scripts/python.exe investigate_flags.py --all-quests --skip-executable-scan

# Full client-quest batch
.venv-cpython314/Scripts/python.exe investigate_flags.py --all-client-quests --skip-executable-scan

# Validation and analysis
.venv-cpython314/Scripts/python.exe validate_targets.py
.venv-cpython314/Scripts/python.exe triage_residuals.py
.venv-cpython314/Scripts/python.exe benchmark_gap_harness.py
.venv-cpython314/Scripts/python.exe graph_residual_experiments.py

# Unit tests
.venv-cpython314/Scripts/python.exe -m unittest discover -s tests -v

# Cleanup stale native and cache artifacts
.venv-cpython314/Scripts/python.exe clean_artifacts.py
```

### Optional `mypyc` Build

`mypyc` is only needed for performance work on the hot-path modules.

```sh
.venv-cpython314/Scripts/python.exe build_mypyc.py
```

This compiles the maintained hot-path module set under `src/ddon_flags` and
`src/ddon_flags/handlers`.

Return to the interpreted path with:

```sh
.venv-cpython314/Scripts/python.exe clean_artifacts.py
```

### Generated Files

| File | Purpose |
|---|---|
| `generated/client_investigation_quest_<id>.json` | Structured quest report payload |
| `generated/client_investigation_quest_<id>.adoc` | AsciiDoc quest report |
| `generated/client_investigation_flag_<value>.json` | Structured single-flag report |
| `generated/client_investigation_flag_<value>.adoc` | AsciiDoc single-flag report |
| `generated/empty_flags.json` | Zero-hit target summary |
| `generated/residual_empty_triage.json` | Candidate triage payload for zero-hit targets |
| `generated/residual_empty_triage.adoc` | Candidate triage AsciiDoc report |
| `generated/benchmark_gap_harness.json` | Owner/dependency benchmark summary |
| `generated/benchmark_gap_harness.adoc` | Owner/dependency benchmark report |
| `generated/graph_residual_experiments.json` | Graph-backed residual experiment summary |
| `generated/graph_residual_experiments.adoc` | Graph-backed residual experiment report |

## Developer Documentation

### Runtime Architecture

| Module | Responsibility |
|---|---|
| `src/ddon_flags/investigate_flags.py` | Main CLI implementation, target resolution, hit orchestration, payload assembly |
| `src/ddon_flags/corpus_index.py` | Single-pass scanner-oriented index over decoded JSON files |
| `src/ddon_flags/json_cache.py` | Parsed JSON reuse across scans and report generation |
| `src/ddon_flags/client_scanner.py` + `src/ddon_flags/handlers/` | Structured extraction for quest, layout, FSM, marker, NPC, and special resource families |
| `src/ddon_flags/source_metadata.py` | Family context, ARC topology, stage names, owner catalogs, enrichment lookups |
| `src/ddon_flags/reverse_indexes.py` | Deterministic reverse indexes for flag, stage, event-viewer, and GPL or LOT relationships |
| `src/ddon_flags/candidate_finder.py` | Recursive unresolved-value search over decoded JSON |
| `src/ddon_flags/graph_expansion.py` | Bounded graph expansion over direct, owner, dependency, and reverse-index edges |
| `src/ddon_flags/derivation.py` | Shared derivation-class vocabulary and labels |
| `src/ddon_flags/report_writer.py` | JSON and AsciiDoc report rendering, including file links and Mermaid graph slices |
| `src/ddon_flags/clean_artifacts.py` | Removal of stale build products, caches, and old compiled artifacts |
| `tests/` | Regression and focused unit tests |
| Root wrappers (`investigate_flags.py`, `validate_targets.py`, `triage_residuals.py`, `benchmark_gap_harness.py`, `graph_residual_experiments.py`, `clean_artifacts.py`) | Compatibility shims that add `src/` to `sys.path` and call package entrypoints |

### Data Flow

```text
corpus_index -> client_scanner -> handlers/* -> direct hits
      |                               |
      +-> json_cache -----------------+
      |
      +-> candidate_finder -> ranked candidates
      +-> source_metadata -> family, stage, and owner context
      +-> reverse_indexes -> event-viewer and GPL or LOT relationships
      +-> graph_expansion -> bounded quest graph
      +-> report_writer -> JSON and AsciiDoc output
```

### Report Structure

- AsciiDoc reports include a generated table of contents.
- JSON file references in AsciiDoc are emitted as clickable links with line
  anchors when a JSON path can be resolved.
- The bounded graph section includes a sampled Mermaid flowchart slice.
- Graph tables and hit tables use derivation labels consistently.

### Validation Workflow

Use the regression suite before regenerating large output sets:

```sh
.venv-cpython314/Scripts/python.exe -m unittest discover -s tests -v
```

For end-to-end regeneration and verification:

```sh
.venv-cpython314/Scripts/python.exe investigate_flags.py --all-client-quests --skip-executable-scan
.venv-cpython314/Scripts/python.exe validate_targets.py
.venv-cpython314/Scripts/python.exe triage_residuals.py
.venv-cpython314/Scripts/python.exe benchmark_gap_harness.py
.venv-cpython314/Scripts/python.exe graph_residual_experiments.py
```

Regenerate reports whenever you change:

- target resolution rules
- family-specific business logic
- owner or dependency promotion logic
- graph expansion structure
- report schema or AsciiDoc rendering
- package or import layout that affects CLI entrypoints or report output paths
