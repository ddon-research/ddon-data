# Quest flag sources

Where each flag command of a quest definition can be found in the extracted data of client 03040008, for anyone tracing a flag by hand. The investigation itself is [`ddon-flags`](../../research/03040008/flags/README.md), which keeps its own documents. This is a rough map: `UNKNOWN` is where the note's author found no file. The file examples were checked on 2026-11-04 by searching each named file for its value; the C# lines come from the note and were not compared with a current server source (not run).

## Find a flag

Search the JSON for the flag's number as a value, here 7860:

```bash
rg -l '" : 7860($|,)' client/03040008/quest
```

## Command to file type

| Command | Where |
| --- | --- |
| `QstTalkChg` | `.mss`, with NPC id and condition (the flag) |
| `QstLayoutFlagOn` | `.qst`, with comment, NPC id and condition (the flag) |
| `WorldManageLayoutFlagOn` | unknown; the example below is a `.qst` |
| `MyQstFlagOn` | unknown, partially in NPC `.fsm` |
| `SceHitInWithoutMarker` | no entry |
| `IsLinkageEnemyFlag` | `rLinkageEnemy` is undecoded; maybe, no debug symbols |

## Examples, quest q00030260 and q70033001

A server quest line and the file that holds its value. `<q>` stands for `client/03040008/quest/q00030260/quest/00030260`.

| C# line | Value and comment | File |
| --- | --- | --- |
| `quest.QuestTalkInfoList.Add(new CDataQuestTalkInfo(NpcId.TheWhiteDragon, 22449));`, matching a `QstTalkChg` in `CDataQuestProcessState[0].ResultCommandList` | NpcId 1, GroupSerial 22449 | `client/03040008/quest/q00030260/ui/00_message/quest/q00030260.mss.json` |
| `quest.QuestLayoutFlagList.Add(new CDataQuestLayoutFlag() { FlagId = 7860 });`, which makes Lise, Gurdolin and Elliot appear in the audience chamber | "before and after being injected", NpcId 501, Condition 7860 | `client/03040008/quest/q00030260/quest/00030260/q00030260_st0201.qst.json` |
| `quest.QuestLayoutFlagList.Add(new CDataQuestLayoutFlag() { FlagId = 8013 });` | "Gillian between 5 and 6.", NpcId 30, Condition 8013 | `client/03040008/quest/q00030260/quest/00030260/q00030260_st0139.qst.json` |
| `QuestManager.ResultCommand.WorldManageLayoutFlagOff(8202, 70033001),` | Glitter points (text display), Condition 8202 | `client/03040008/quest/q70033001/quest/70033001/q70033001_st1100.qst.json` |
| `QuestManager.ResultCommand.QstLayoutFlagOn(7904),` | "It could be your last, so I want to tell you everything.", Condition 7904 | `client/03040008/quest/q00030260/quest/00030260/q00030260_st1101.qst.json` |
| `QuestManager.ResultCommand.MyQstFlagOn(4830),` | FlagNo 4830 | `client/03040008/quest/q00030260/quest/00030260/npc/n0030.fsm.json`, `client/03040008/quest/q00030260/quest/00030260/npc/n0031.fsm.json` |
| `QuestManager.ResultCommand.QstLayoutFlagOff(8063),` | エリオット / Eriotto, Condition 8063 | `client/03040008/quest/q00030260/quest/00030260/q00030260_st1100.qst.json` |
| `QuestManager.ResultCommand.QstLayoutFlagOff(8064),` | リズ / Rizu, Condition 8064 | the same file |
| `QuestManager.ResultCommand.QstLayoutFlagOff(8062),` | ガルドリン / Garudorin, Condition 8062 | the same file |
| `QuestManager.ResultCommand.QstLayoutFlagOff(7861),` | メイロワジリアン / Meirowazilian, Condition 7861 | `client/03040008/quest/q00030260/quest/00030260/q00030260_st0451.qst.json` |

Two more references of the same quest, with no flag:

| C# line | Source |
| --- | --- |
| `QuestManager.CheckCommand.EventEnd(StageNo.LookoutCastle1, 20)` | `client/03040008/event/st0451/st0451ev020/event/st0451/ev020/fsm` |
| `quest.QuestEnemyInfoList.Add(new CDataQuestEnemyInfo() { GroupId = 341, Lv = 100, IsPartyRecommend = true });` | enemy group 341: `ENEMY_NAME_341`, "War-Ready Goremanticore" |
