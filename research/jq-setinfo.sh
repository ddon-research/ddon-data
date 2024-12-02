#!/bin/bash

# All quest sets with doors
jq '.QuestStageList[] | .QuestGrp[] | .QuestSet[] | select(.SetInfo | (.["@class"] | contains("QuestSetInfoOmDoor")))' client/03040008/quest/q00000021/quest/00000021/q00000021_st0572.qst.json

# Get door OM IDs
jq '.QuestStageList[] | .QuestGrp[] | .QuestSet[] | select(.SetInfo | (.["@class"] | contains("QuestSetInfoOmDoor"))).OmID' client/03040008/quest/q00000021/quest/00000021/q00000021_st0572.qst.json
find client/03040008/quest -type f -name "*.qst.json" -exec jq '.QuestStageList[] | .QuestGrp[] | .QuestSet[] | select(.SetInfo | (.["@class"] | contains("QuestSetInfoOmDoor"))).OmID' {} +
find client/03040008/stage -type f -name "*.lot.json" -exec jq '.Array[] | select(.Info | (.["@class"] | contains("SetInfoOmDoor"))).Info.InfoOm.InfoCoord.UnitID' {} +

