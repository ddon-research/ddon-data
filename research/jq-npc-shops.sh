#!/bin/bash

# Unique shop IDs
jq '.npcLedgerList[] | select(.InstitutionList[] | .FunctionName == "Shop") | .InstitutionList[].FunctionParam' client/03040008/npc/npc_common/etc/npc/npc.nll.json

# Unique shop IDs
jq '.npcLedgerList[] | select(.InstitutionList[] | .FunctionName == "Shop") | .InstitutionList[].FunctionParam' client/03040008/npc/npc_common/etc/npc/npc.nll.json | sort -n | uniq
