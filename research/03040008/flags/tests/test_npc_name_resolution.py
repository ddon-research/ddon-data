from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ddon_flags._paths import DDON_DATA_ROOT
from ddon_flags.mss_enrichment import enrich_hit_dicts_with_mss
from ddon_flags.source_metadata import enrich_hit_with_npc_ledger, resolve_npc_name



class NpcNameResolutionTests(unittest.TestCase):
    def test_resolve_npc_name_from_nll(self) -> None:
        self.assertEqual(resolve_npc_name(30), ("Gillian", "ジリアン"))
        self.assertEqual(resolve_npc_name(4760), ("Blair", "ブレア"))

    def test_enrich_hit_with_npc_ledger_from_fsm_asset_path(self) -> None:
        hit = {
            "source_type": "fsm",
            "file_path": "client/03040008/quest/q00030260/quest/00030260/npc/n0030.fsm.json",
            "context": "quest 30260 (Hopes' Bitter End) | checkMyQuestFlag | NPCFSM=n0030",
            "flag_value": 4830,
        }

        enriched = enrich_hit_with_npc_ledger(hit)

        self.assertEqual(enriched.get("npc_id"), 30)
        self.assertEqual(enriched.get("npc_name"), "Gillian")
        self.assertEqual(enriched.get("npc_name_jp"), "ジリアン")

    def test_mss_enrichment_still_falls_back_to_npc_ledger_without_mss_keys(self) -> None:
        hit = {
            "source_type": "fsm",
            "file_path": "client/03040008/quest/q00020170/quest/00020170/npc/n4760.fsm.json",
            "context": "quest 20170 (The Village of Soldiers) | checkMyQuestFlag | NPCFSM=n4760 | QuestLocalNPCFSM",
            "flag_value": 20170,
        }

        enriched = enrich_hit_dicts_with_mss(DDON_DATA_ROOT, [hit])

        self.assertEqual(len(enriched), 1)
        self.assertEqual(enriched[0].get("npc_id"), 4760)
        self.assertEqual(enriched[0].get("npc_name"), "Blair")
        self.assertEqual(enriched[0].get("npc_name_jp"), "ブレア")


if __name__ == "__main__":
    unittest.main()