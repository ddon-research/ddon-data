#!/bin/bash

# All NPCs with shops
jq '.npcLedgerList[] | select(.InstitutionList[] | (.FunctionName | contains("Shop")))' client/03040008/npc/npc_common/etc/npc/npc.nll.json

# All NPCs with general shops
jq '.npcLedgerList[] | select(.NpcClassName == "General Shop")' client/03040008/npc/npc_common/etc/npc/npc.nll.json

# TODO: FUNC_ID_ORB_MATERIAL, FUNC_ID_ORB_CREST
# Unique shop IDs
jq '.npcLedgerList[].InstitutionList[] | (select(.FunctionName | contains("Shop"))).FunctionParam' client/03040008/npc/npc_common/etc/npc/npc.nll.json | sort -n | uniq

# Unique function shop names
jq '.npcLedgerList[].InstitutionList[] | (select(.FunctionName | contains("Shop"))).FunctionName' client/03040008/npc/npc_common/etc/npc/npc.nll.json | sort | uniq

# Find specific NPC
jq '.npcLedgerList[] | select(. | .NpcName == "Sebastian")' client/03040008/npc/npc_common/etc/npc/npc.nll.json

# Find specific shop ID
jq '.npcLedgerList[] | select(.InstitutionList[] | .FunctionName == "Shop" and .FunctionParam == 230)' client/02030004/npc/npc_common/etc/npc/npc.nll.json
jq '.npcLedgerList[] | select(.InstitutionList[] | (.FunctionName | contains("Shop")) and .FunctionParam == 230)' client/03040008/npc/npc_common/etc/npc/npc.nll.json
