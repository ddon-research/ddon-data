# Season 3 Client Flag and Quest Investigation

This folder contains the active tooling for investigating quest, layout, NPC, marker, evidence, and related state associations from decoded Dragon's Dogma Online Season 3 client resources.

## Scope

- Primary corpus: `d:/ddon-data/client/03040008`
- Optional fallback corpus: `D:/DDON_03040008/DDO.exe`
- Output location: `d:/ddon-data/research/03040008/flags/generated`
- Upstream Arrowgene quest docs are used only for target labels, curated seed targets, and review context

The tooling is generic for decoded client quest analysis. It is not limited to q7 world-manage quests.

## Evidence Model

Evidence priority is:

1. Decoded client JSON under `client/03040008`
2. Optional executable immediate-operand scan from `DDO.exe`
3. Upstream quest docs and manifests only for target selection or interpretation context

Container and sequencing resources are not treated as direct world-state evidence unless they expose an authored quest, flag, or layout field with useful semantics.

## Query Modes

| Mode | Behavior |
|---|---|
| `--flag <value>` | Scan one numeric flag value across the decoded client corpus. |
| `--quest <quest_id>` | Run a generic quest investigation for any quest family. |
| `--all-quests` | Batch only the curated authoritative q7 world-manage quest set from `manifest.py`. |

Key rules:

- Only q7-prefixed quests are treated as world-manage quests in this workflow.
- Main quests such as `q20200` are generic quest investigations, not world-manage investigations.
- The built-in batch mode is intentionally limited to the manifest-backed q7 set.
- Running every `q########` client quest folder is external orchestration over repeated `--quest` runs, not the meaning of `--all-quests`.

## Quest-Family Semantics

| Quest family | Detection / source | Query behavior |
|---|---|---|
| q5 repeatable sorties | `rEndContentsSortieInfo.esi.json`, `rCycleContentsSortieInfo.csi.json` | Derive repeatable sortie gate flags and `CycleSubNo` targets. |
| q6 tutorial quests | `jobTutorialQuestList.jtq.json`, `tutorialQuestGroup.tqg.json`, `jobMasterCtrl.jmc.json` | Fall back to quest-wide tutorial association scans and job-master context even without manual catalog entries. |
| q7 world-manage quests | `manifest.py` plus upstream catalog/docs | Pull authoritative quest and layout targets first, then merge decoded evidence. |
| Evidence-backed quests | `ui/menu_evidence_list/ui/00_common/evidence/evidence.evd.json` | Derive evidence-step quest flags and treat the quest as an evidence-flow investigation. |
| AMS-blocked quests | `ui/uGUIAreaMaster/ui/00_param/master/am_spot_*.ams.json` | Derive a quest-id target when a map spot is blocked or withheld by that quest. |
| Main quests and other non-q7 quests | generic `--quest` path | Resolve direct authored references and special-resource fallbacks without world-manage assumptions. |

## Client File Associations

| Family | Typical files | Association semantics |
|---|---|---|
| QST | `quest/q########/**/*.qst.json` | Authored quest-stage behavior. `Condition`, `EraseCondition`, `TextQuestNo`, and `QuestSetInfo*` fields drive quest-group activation, OM text, door/warp gating, and OM control chains. |
| GPL | `stage/**/etc/*.gpl.json` | Layout-group guards. `QuestNo` plus `LayoutFlagNo` usually indicate whether a stage group loads or becomes visible. |
| LOT | `stage/**/etc/*.lot.json` | Concrete placed NPC, enemy, warp, door, and interactable layout data. Used to turn GPL or marker hits into concrete object context. |
| QMI / FMI | `quest/**/*.qmi.json`, `quest/**/*.fmi.json` | Quest and field marker authored data. Marker asset names classify NPC, OM, scene, and objective markers; `GroupNo` often links back to LOT placements. |
| FSM | `npc/**/*.fsm.json`, `quest/**/npc/*.fsm.json`, other authored FSM assets | Quest or flag checks inside state machines. NPC FSM assets are useful for visibility, behavior, and MyQuest gating. Quest-local NPC FSM assets often describe the same quest they ship with. |
| EVSI | `EventViewRoom/**/ev*.evsi.json` | Event viewer replay or cinematic state references with stage and event identifiers. |
| EVP | `event/**/*.evp.json` | Event parameter associations where authored quest or flag fields survive decoding. |
| SMC | `npc/**/ui/00_message/**/.smc.json` | NPC or pawn chatter windows. `StartQuestId` and `EndQuestId` define the quest window where a `GroupSerial` dialogue set is available. These windows often span a short run of follow-up quests in a series. |
| MSS | `**/*.mss.json` | Message-set groups and message text. Used to resolve `GroupSerial`, `MsgSerial`, NPC names, and message excerpts for chatter and related hits. |
| NLL | `npc/npc_common/etc/npc/npc.nll.json` | Authoritative NPC ledger. Supplies NPC names, NPC function metadata, and fallback name resolution for `npc_id` values or `n####` asset references. |
| FAA | `field_area/**/*.faa.json` | Area-adjoin and stage-transition gating data. |
| ESI / CSI | `game_common/quest/*.esi.json`, `game_common/quest/*.csi.json` | Special q5 repeatable sortie registry and cycle-routing metadata. |
| JTQ / TQG / JMC | `game_common/quest/*.jtq.json`, `game_common/quest/*.tqg.json`, `game_common/etc/jobMasterCtrl.jmc.json` | q6 tutorial quest registry, grouping, and job-master onboarding associations. |
| EVD | `ui/menu_evidence_list/ui/00_common/evidence/evidence.evd.json` | Season 3 evidence-chain registry tying evidence items and steps to quests and the flags they unlock. |
| AMS | `ui/uGUIAreaMaster/ui/00_param/master/am_spot_*.ams.json` | Map-spot gating. `QuestId` here means a spot is blocked or withheld by that quest. |

## Enrichment Model

Report enrichment is layered and deterministic:

- Stage names come from `base/scr/stage_list.slt.json`.
- Event viewer names come from `EventViewRoom/ui/00_message/event/event_name.gmd.json`.
- Item names for `KeyNo` and `KeyItemNo` come from `base/etc/itemlist.ipa.json`.
- ARC context comes from `quest/q<quest>.arc.json` and is reported as bundle association only, not direct evidence.
- Marker-to-LOT hints are inferred from marker file naming and nearby LOT placement context.
- NPC names resolve from MSS first when a `GroupSerial` or `MsgSerial` match exists.
- NPC names then fall back to NLL lookup by explicit `npc_id` or inferred `n####` asset ID.

This means NPC names should resolve for both dialogue-driven rows and non-MSS assets such as `npc/n0030.fsm.json`, as long as the NPC exists in `npc.nll.json`.

## Interpretation Notes

Static family interpretations are documented here rather than repeated in every generated Markdown report.

- QST OM-control link patterns such as `ENEMY -> OM`, `OM -> OM`, and `ENEMY -> ENEMY -> OM` are useful clues for identifying key-enemy doors, lever chains, and other multi-object control logic.
- GPL to LOT association is useful when a guarded group can be matched to a concrete `pNN` LOT file and classified as a warp, door, or other object group.
- AMS quest hits are spot-availability gates, not generic flavor references.
- EVD rows are evidence-flow progression data for the investigation-style season 3 substory system.
- SMC rows are quest-gated chatter availability, not generic NPC state.
- QSQ is intentionally omitted from direct evidence because it mainly drives quest ordering and UI sequencing rather than decoded world-state gating.

## Generated Outputs

Canonical output names are:

- `generated/client_investigation_quest_<quest>.json`
- `generated/client_investigation_quest_<quest>.md`
- `generated/client_investigation_flag_<flag>.json`
- `generated/client_investigation_flag_<flag>.md`
- `generated/empty_flags.json`
- `generated/residual_empty_triage.json`
- `generated/residual_empty_triage.md`

Per-report Markdown is intentionally query-specific. Static family guidance lives in this README.

## Commands

Activate the local environment first:

```powershell
& d:/ddon-data/.venv/Scripts/Activate.ps1
```

Generic quest investigation:

```powershell
python d:/ddon-data/research/03040008/flags/investigate_flags.py --quest 20200 --skip-executable-scan
```

World-manage manifest batch:

```powershell
python d:/ddon-data/research/03040008/flags/investigate_flags.py --all-quests --skip-executable-scan
```

Representative special-family spot checks:

```powershell
python d:/ddon-data/research/03040008/flags/investigate_flags.py --quest 50300000 --skip-executable-scan
python d:/ddon-data/research/03040008/flags/investigate_flags.py --quest 60000003 --skip-executable-scan
python d:/ddon-data/research/03040008/flags/investigate_flags.py --quest 60320001 --skip-executable-scan
python d:/ddon-data/research/03040008/flags/investigate_flags.py --quest 70032001 --skip-executable-scan
```

Single-flag investigation:

```powershell
python d:/ddon-data/research/03040008/flags/investigate_flags.py --flag 1109 --skip-executable-scan
```

Manifest validation and residual triage:

```powershell
python d:/ddon-data/research/03040008/flags/validate_targets.py
python d:/ddon-data/research/03040008/flags/triage_residuals.py
```

## Archive Policy

`archive/` is for retained research references, not active script output.

Keep archive files when they preserve unique manual analysis or historical comparison context.
Delete archive files when they are reproducible generated outputs or deprecated helpers that the active tooling fully replaces.

## Non-Goals

- Packaging this folder as an installable Python package
- Adding new third-party dependencies
- Treating upstream Arrowgene quest assets as primary evidence