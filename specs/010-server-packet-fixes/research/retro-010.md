# Efficiency retrospective: 010

Window: 2026-11-04T11:24+01:00 to now.

## Headline

- calls: 1,074
- failed_pct: 1.27
- refused_pct: 2.81
- result_tokens_est: 4,453,000
- sessions: 1
- subagents: 12
- turns: 640
- tokens_input: 134,295,998
- tokens_output: 1,150,263
- main_peak_context: 511,604
- subagent_peak_median: 292,392
- agent_hours: 4.06
- cost.total_usd: 76.03
- cost.coordinator_usd: 10.01
- cost.coordinator_share_pct: 13.2
- instructions.agents_md_tokens: 3,670
- instructions.claude_md_tokens: 833
- instructions.roles_tokens: 5,757
- instructions.skill_tokens: 2,008
- waste.budget_overruns_1x: 0
- waste.budget_overruns_2x: 0

## Cost per agent (list $)

- $8.40 implementer: implementer · 010 T005b: live smoke with real client
- $7.91 evidence-researcher-ida: evidence-researcher-ida · 010 T003: PC evidence per can
- $7.64 implementer: implementer · 010 T004a: framework and robustness patch
- $6.78 implementer: implementer · 010 T004b: wire layout patch
- $6.73 repository-researcher: repository-researcher · 010 T001: baseline and error inve
- $6.20 implementer: implementer · 010 T005a: fix key check and fixtures
- $5.15 implementer: implementer · 010 T002: baseline and differential harness
- $4.74 adversarial-reviewer: adversarial-reviewer · 010 T005: would a fix break a clien
- $4.61 implementer: implementer · 010 T006: impact outline and PR body
- $2.78 implementer: implementer · 010 T007c: review fixes and F04 lock
- $2.76 reviewer: reviewer · 010 T007b: whole-spec and docs audit
- $2.32 implementer: implementer · 010 T006a: make the branch fit to publish

## Unavailable

- none

## Calls per tool

- Bash: 477
- Read: 249
- Write: 142
- mcp__ida__execute_python: 86
- Edit: 60
- Grep: 23
- Agent: 12
- mcp__ccd_turn__update_plan: 12
- ToolSearch: 4
- Glob: 3
- mcp__ida__open_database: 2
- mcp__ccd_turn__wrap_up: 1

## Refusals (guard: reason)

- 10 x guard_bash: `cat FILE | head/tail` is not used here: use the Read tool with offset/limit, `rg -n -m N 
- 3 x guard_bash: `sed -i` strips the CRs of CRLF files: use the Edit tool, or `sd -F 'old' 'new' FILE` for 
- 3 x guard_bash: `git diff` without a pathspec or over client/ or packets/ can print hundreds of thousands 
- 3 x guard_bash: `git log` without a pathspec or over client/ or packets/ can print hundreds of thousands o
- 2 x guard_bash: `git ls-files` over client/ or packets/ is unbounded: pipe it to `wc -l`, or use `fd -d 2`
- 2 x guard_bash: `fd` over client/ or packets/ needs a depth (`-d 2`) or a count (`| wc -l`).
- 2 x guard_bash: `sd` matches line by line: a pattern with a newline matches nothing unless you pass `-A`. 
- 1 x guard_bash: `rg` over client/ or packets/ (~173k files) needs a bound: `-c`, `-l`, `-m N`, or `| wc -l
- 1 x guard_bash: `git checkout` over . reverts or deletes many files in a checkout that holds other work (A
- 1 x guard_bash: `git checkout` over Arrowgene.Ddon.Differential reverts or deletes many files in a checkou

## Failures (tool: error)

- 1 x Bash: Exit code 2
/usr/bin/bash: -c: line 116: unexpected EOF while looking for matching `''
- 1 x mcp__ida__execute_python: unsupported operand type(s) for +: 'NoneType' and 'str'

traceback:
Traceback (most recent
- 1 x mcp__ida__execute_python: list index out of range

stdout:
23 []

traceback:
Traceback (most recent call last):
  Fi
- 1 x Bash: Exit code 1
asset rows 9222 RepopNum [(0, 9221), (2, 1)] RepopCount [(0, 9209), (1, 12), (
- 1 x Bash: Exit code 2
/usr/bin/bash: -c: line 115: unexpected EOF while looking for matching `''
- 1 x Bash: Exit code 2
Add T002 differential harness and proof tests (scratch, never pushed)

 .../Ar
- 1 x Bash: Exit code 1
On branch fix/packet-handling
nothing to commit, working tree clean
924094e0 L
- 1 x Bash: Exit code 2
/usr/bin/bash: -c: line 101: unexpected EOF while looking for matching `''
- 1 x Bash: Exit code 1
25
0
Traceback (most recent call last):
  File "C:\Users\morph\AppData\Local\
- 1 x Bash: Exit code 2
/usr/bin/bash: -c: line 69: unexpected EOF while looking for matching `''

## Repeated commands (same agent, 3 or more)

- 7 x [a01c2ade2cb97c593] `SP="C:/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad"; cd /d/Gi`
- 4 x [a01c2ade2cb97c593] `SP="C:/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad"; cd /d/Gi`
- 3 x [a2051314d5fd4a328] `cd /d/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean && for c in Debug Release; do echo "=== $c"; dotnet build Arrowge`
- 3 x [afc636f2454be31c4] `cd /d/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean && SP="C:/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/`

## Slowest calls

- 87.9 s Bash `cd /c/ddon-automation/t005b/driver; D="python -X utf8 -I scripts/automation/drive.py"; G="bash /c/ddon-automation/t005b/`
- 84.5 s Bash `SP=/c/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad; cd /d/GitH`
- 81.8 s Bash `S="C:/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad"; python -X`
- 74.6 s Bash `cd /d/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean && SP="C:/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/`
- 74.2 s Bash `cd /tmp 2>/dev/null; radare2 -q -e bin.relocs.apply=true -e scr.color=0 -e io.cache=true -c "s 0x4d0240; pd 34" "D:/rese`
- 70.3 s Bash `SP=/c/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad; cd /d/GitH`
- 57.5 s Bash `G="bash /c/ddon-automation/t005b/go.sh"; $G start; python -X utf8 -I - <<'EOF' import time; time.sleep(0) EOF cd /c/ddon`
- 53.4 s Bash `cd /d/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean && SP="C:/Users/morph/AppData/Local/Temp/claude/95c4aea5e0b9789a/`

## Largest results (each re-read on every later turn)

- ~158k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T144016\093-c7.png`
- ~158k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T144016\099-z0.png`
- ~156k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T142657\046-party.png`
- ~155k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T144016\095-c8.png`
- ~154k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T142657\043-party.png`
- ~144k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T144016\006-w.png`
- ~143k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T140312\009-world1.png`
- ~140k tokens Read `C:\ddon-automation\t005b\driver\build\automation-drive\20261104T144016\022-after-DIK_E-28182.png`

## Sessions and agents by input tokens

| kind | name | turns | input+cache (k) | output (k) | peak (k) | wall (h) | $ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| main | 584d9d84-927d-466f-adf6-d1c15549c007 | 88 | 27,675 | 95 | 511 | 4.35 | 10.01 |
| subagent | implementer: implementer · 010 T005b: live smoke with real c | 109 | 22,283 | 92 | 292 | 0.92 | 8.40 |
| subagent | evidence-researcher-ida: evidence-researcher-ida · 010 T003: | 92 | 16,931 | 98 | 325 | 0.32 | 7.91 |
| subagent | implementer: implementer · 010 T004a: framework and robustne | 48 | 12,103 | 133 | 351 | 0.43 | 7.64 |
| subagent | implementer: implementer · 010 T004b: wire layout patch | 46 | 10,695 | 115 | 322 | 0.40 | 6.78 |
| subagent | implementer: implementer · 010 T005a: fix key check and fixt | 49 | 10,501 | 100 | 292 | 0.36 | 6.20 |
| subagent | repository-researcher: repository-researcher · 010 T001: bas | 41 | 8,204 | 121 | 339 | 0.32 | 6.73 |
| subagent | adversarial-reviewer: adversarial-reviewer · 010 T005: would | 31 | 6,318 | 70 | 287 | 0.27 | 4.74 |
| subagent | implementer: implementer · 010 T006: impact outline and PR b | 31 | 6,207 | 72 | 270 | 0.21 | 4.61 |
| subagent | implementer: implementer · 010 T002: baseline and differenti | 37 | 5,897 | 108 | 255 | 0.33 | 5.15 |
