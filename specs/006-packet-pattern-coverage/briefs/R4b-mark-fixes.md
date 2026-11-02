006 R4b: apply the R4 adversarial findings to the marks and names

Objective: fix the four findings of `specs/006-packet-pattern-coverage/research/R4-adversarial-marks.md`
(read it) in `research/03040008/packets/` and in the T014b TSV/md:

- F1: `EnhanceType` and `EnhanceId` (`include/Context.hexpat`, 12 TSV rows each): mark
  `V (consumer); I (name; lead agrees)`; `SlotNo` keeps V (PS4 DWARF `m_ucSlotNo`).
- F2: `CDataGameSetting_unk_1.Type` (`include/Server.hexpat`) -> `GameMode` (V role, I name: compared with
  sGame+0x39FC at `0xb5f420`, as `CDataCharacterListElement.GameMode`); re-export the patterns that use it.
- F3: `DistributionStartDate` (CDataQuestList, CDataQuestOrderList): raise to `V (consumer); I (name)`
  citing getter `0x64d260` (the distribution window test); drop "(proposed)" in the TSV.
- F4: LOBBY_CHAT_MSG REQ/NTC `MessageFlavor`, `PhrasesCategory`, `PhrasesIndex`: keep the I marks; the
  comments must say the names come from the lead and what the code shows (a message kind, category+1,
  a table entry id; `0xb79b80` returns a u16 from the entry). If the spec rule (`spec.md` § "Naming
  unknown fields by inference", basis 4) is not met by that, use neutral names instead; say which.

TSV/md: update the rows R4 names (mark, basis) and add a dated "Errata (R4, <date>)" line in the md's
Part where each was settled; never rewrite the original text. Re-export every pattern whose JSON keys
change (`packets/imhex-export.sh --force @ <name>`, `</dev/null` in loops); 2-file sample: only renamed
keys differ; every file fits.
Owns: the named includes/patterns, the packets README if it lists these names, the re-exported JSON,
the named TSV rows and md errata. Never touch raws, client/, other specs; `tasks.md` is the
coordinator's. Commit with `git commit -m <msg> -- <paths>`.
Libraries: plbatch; jq / stdlib Python.
Done: signed commits; re-export counts and fit; sample result; `bash tools/check.sh --since <base>`;
receipt with "For Sam's inspection" (old -> new key and mark). Stop: budget 45 min of work time.
Base: the head when you start.
