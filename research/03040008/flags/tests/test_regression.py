"""Regression tests for the flags investigation tooling.

These tests compare generated output against known-good baselines to catch
regressions from refactoring.  The baselines live in ``test_baselines/`` and
were captured from a verified run before any structural changes.
"""
from __future__ import annotations

import orjson
import sys
import unittest
from pathlib import Path
from typing import Any

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ddon_flags._paths import DDON_DATA_ROOT, GENERATED_DIR
from ddon_flags._paths import DEFAULT_UPSTREAM_ROOT, TEST_BASELINES_DIR
from ddon_flags.catalog_loader import load_known_targets
from ddon_flags.corpus_index import build_corpus_index
from ddon_flags.investigate_flags import build_payload, resolve_targets
from ddon_flags.json_cache import JsonCache
from ddon_flags.quest_families import classify_quest_family
from ddon_flags.report_writer import build_asciidoc_lines
from ddon_flags.reverse_indexes import build_reverse_indexes
from ddon_flags.source_metadata import (
    build_family_relationship_context,
    build_owner_layout_catalog,
    build_q7_owner_layout_catalog,
    build_quest_archive_context,
    collect_stage_neighborhood_cues,
)

BASELINES_DIR = TEST_BASELINES_DIR


def _strip_volatile(data: dict) -> dict:
    """Return a copy with timestamp and other volatile fields removed."""
    cleaned = dict(data)
    cleaned.pop("generated_at", None)
    return cleaned


def _load_json(path: Path) -> dict:
    return orjson.loads(path.read_bytes())


class RegressionTests(unittest.TestCase):
    """Compare current generated output against committed baselines."""

    catalog: list[Any]
    corpus_index: Any
    json_cache: JsonCache
    _payload_cache: dict[int, dict[str, Any]]
    _target_cache: dict[int, tuple[list[Any], list[Any]]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_known_targets(DEFAULT_UPSTREAM_ROOT)
        cls.corpus_index = build_corpus_index(DDON_DATA_ROOT)
        cls.json_cache = JsonCache()
        cls._payload_cache = {}
        cls._target_cache = {}

    @classmethod
    def _resolve_targets_for_quest(cls, quest_id: int) -> tuple[list[Any], list[Any]]:
        cached = cls._target_cache.get(quest_id)
        if cached is not None:
            return cached

        resolved = resolve_targets(cls.catalog, "quest", quest_id)
        cls._target_cache[quest_id] = resolved
        return resolved

    @classmethod
    def _payload_for_quest(cls, quest_id: int) -> dict[str, Any]:
        cached = cls._payload_cache.get(quest_id)
        if cached is not None:
            return cached

        targets, documented_targets = cls._resolve_targets_for_quest(quest_id)
        payload = build_payload(
            "quest",
            quest_id,
            documented_targets,
            targets,
            hits_by_value={},
            candidate_hits_by_value={},
            exe_results={},
            corpus_index=cls.corpus_index,
            json_cache=cls.json_cache,
        )
        cls._payload_cache[quest_id] = payload
        return payload

    def test_quest_family_classifier_handles_main_world_and_world_manage(self) -> None:
        self.assertEqual(classify_quest_family(5).key, "q0")
        self.assertEqual(classify_quest_family(20090).key, "q2")
        self.assertEqual(classify_quest_family(40000001).key, "q4")
        self.assertEqual(classify_quest_family(40000001).label, "Light / Board Quest")
        self.assertEqual(classify_quest_family(70032001).key, "q7")
        self.assertEqual(classify_quest_family(80200000).key, "q8")
        self.assertEqual(classify_quest_family(80200000).label, "Partner Pawn Personal Quest")

    def test_quest_archive_context_uses_real_zero_padded_client_arc(self) -> None:
        context = build_quest_archive_context(5)

        self.assertIsNotNone(context, "Expected quest 5 archive context to resolve from the client arc file")
        assert context is not None
        self.assertEqual(context["quest_family"]["key"], "q0")
        self.assertTrue(str(context["file_path"]).endswith("client/03040008/quest/q00000005.arc.json"))
        self.assertIn("st0201", context["stage_codes"])
        self.assertIn("st0576", context["stage_codes"])

    def test_quest_payload_includes_family_and_topology_context(self) -> None:
        payload = self._payload_for_quest(5)

        self.assertEqual(payload["quest_family"]["key"], "q0")
        self.assertIn("quest_sequence", payload["quest_family_relationships"])
        self.assertTrue(payload["quest_archive_context"])
        self.assertIn("stage_codes", payload["quest_archive_context"])
        self.assertEqual(payload["quest_stage_neighborhood"]["stage_codes"], payload["quest_archive_context"]["stage_codes"])
        self.assertIsNotNone(payload["quest_stage_cues"])
        self.assertIsInstance(payload["quest_owner_indexes"], list)
        self.assertIsInstance(payload["quest_dependency_targets"], list)
        self.assertIsInstance(payload["quest_graph_expansion"], dict)
        self.assertGreater(payload["quest_graph_expansion"]["node_count"], 0)
        self.assertGreater(payload["quest_graph_expansion"]["edge_count"], 0)

    def test_build_family_relationship_context_includes_main_quest_sequence(self) -> None:
        context = build_family_relationship_context(5)

        sequence = context.get("quest_sequence")
        self.assertIsInstance(sequence, dict)
        assert isinstance(sequence, dict)
        self.assertEqual(sequence["seq_no"], 4)
        self.assertEqual(sequence["previous"]["quest_id"], 4)
        self.assertEqual(sequence["next"]["quest_id"], 6)

    def test_build_family_relationship_context_includes_q5_sortie_metadata(self) -> None:
        context = build_family_relationship_context(50300000)

        repeatable_sortie = context.get("repeatable_sortie")
        self.assertIsInstance(repeatable_sortie, dict)
        assert isinstance(repeatable_sortie, dict)
        self.assertGreaterEqual(repeatable_sortie["esi_count"], 1)
        self.assertIn(1001, repeatable_sortie["cycle_sub_nos"])

    def test_build_family_relationship_context_includes_q6_tutorial_metadata(self) -> None:
        context = build_family_relationship_context(60000003)

        tutorial_scaffolding = context.get("tutorial_scaffolding")
        self.assertIsInstance(tutorial_scaffolding, dict)
        assert isinstance(tutorial_scaffolding, dict)
        self.assertGreaterEqual(tutorial_scaffolding["jtq_count"], 1)
        self.assertGreaterEqual(tutorial_scaffolding["jmc_count"], 1)
        job_links = tutorial_scaffolding["job_links"]
        self.assertTrue(any(link["job_master_tutorial_quest_id"] == 60000050 for link in job_links))

    def test_quest_5_stage_neighborhood_cues_surface_q7_owned_external_flags(self) -> None:
        cues = collect_stage_neighborhood_cues(5, corpus_index=self.corpus_index, json_cache=self.json_cache)

        self.assertIsNotNone(cues)
        assert cues is not None
        by_value = {cue["flag_value"]: cue for cue in cues["cues"]}
        self.assertIn(1215, by_value)
        self.assertIn(7390, by_value)
        self.assertIn(70000001, by_value[1215]["owner_quests"])
        self.assertIn("evsi", by_value[1215]["source_types"])
        self.assertIn(70032001, by_value[7390]["owner_quests"])

    def test_quest_5_dependency_targets_include_expected_q7_owner_flags(self) -> None:
        payload = self._payload_for_quest(5)

        dependency_targets = {entry["owner_quest_id"]: entry for entry in payload["quest_dependency_targets"]}
        self.assertIn(70000001, dependency_targets)
        self.assertIn(70032001, dependency_targets)
        self.assertIn(1215, dependency_targets[70000001]["flag_values"])
        self.assertIn(1218, dependency_targets[70000001]["flag_values"])
        self.assertIn(7390, dependency_targets[70032001]["flag_values"])
        self.assertIn(7496, dependency_targets[70032001]["flag_values"])

    def test_client_derived_q7_owner_catalog_covers_expected_self_cues(self) -> None:
        owner_catalog = build_q7_owner_layout_catalog(70032001, corpus_index=self.corpus_index, json_cache=self.json_cache)

        self.assertIsNotNone(owner_catalog)
        assert owner_catalog is not None
        self.assertIn(7390, owner_catalog["flag_values"])
        self.assertIn(7496, owner_catalog["flag_values"])
        self.assertIn(7512, owner_catalog["flag_values"])

    def test_client_derived_q6_owner_catalog_covers_expected_self_cues(self) -> None:
        owner_catalog = build_owner_layout_catalog(60310000, corpus_index=self.corpus_index, json_cache=self.json_cache)

        self.assertIsNotNone(owner_catalog)
        assert owner_catalog is not None
        self.assertEqual(owner_catalog["owner_family"], "q6")
        self.assertIn(6972, owner_catalog["flag_values"])
        self.assertIn(6974, owner_catalog["flag_values"])

    def test_build_reverse_indexes_includes_flag_stage_and_event_mappings(self) -> None:
        reverse_indexes = build_reverse_indexes(
            quest_ids=(5, 70032001),
            corpus_index=self.corpus_index,
            json_cache=self.json_cache,
        )

        self.assertIn("st0201", reverse_indexes["stage_to_quests"])
        self.assertIn(5, reverse_indexes["stage_to_quests"]["st0201"])
        self.assertIn(70032001, reverse_indexes["stage_to_quests"]["st0201"])
        self.assertIn(7390, reverse_indexes["flag_to_quests"])
        self.assertIn(70032001, reverse_indexes["flag_to_quests"][7390])
        self.assertIn("st0201", reverse_indexes["flag_to_stages"][7390])
        self.assertTrue(
            any(entry["event_code"] == "ev000" for entry in reverse_indexes["stage_to_event_viewers"]["st0201"]),
            "Expected stage st0201 to expose event-viewer reverse references",
        )

    def test_build_reverse_indexes_includes_stage_group_lot_gpl_references(self) -> None:
        reverse_indexes = build_reverse_indexes(
            quest_ids=(70003001,),
            stage_codes=("st0100",),
            corpus_index=self.corpus_index,
            json_cache=self.json_cache,
        )

        stage_groups = reverse_indexes["stage_group_references"]["st0100"]
        self.assertIn(93, stage_groups)
        self.assertTrue(
            any(ref["flag_value"] == 2429 and ref["quest_id"] == 70003001 for ref in stage_groups[93]["gpl_refs"]),
            "Expected stage/group reverse index to retain the GPL guard for flag 2429",
        )
        lot_reference = stage_groups[93]["lot_reference"]
        self.assertIsInstance(lot_reference, dict)
        assert isinstance(lot_reference, dict)
        self.assertEqual(lot_reference["file_name"], "st0100_13m28n_p93.lot.json")
        self.assertIn("SetInfoOmWarp", lot_reference.get("type_names", []))

    def test_graph_expansion_includes_stage_owner_and_family_edges(self) -> None:
        payload = self._payload_for_quest(20090)
        graph = payload["quest_graph_expansion"]

        edge_types = {edge["edge_type"] for edge in graph["edges"]}
        derivation_classes = {edge["derivation_class"] for edge in graph["edges"]}
        self.assertIn("quest_archive_stage", edge_types)
        self.assertIn("stage_owner_index", edge_types)
        self.assertIn("promoted_dependency", edge_types)
        self.assertIn("graph_expanded", derivation_classes)
        self.assertIn("dependency_inferred", derivation_classes)

    def test_graph_expansion_accepts_direct_family_hits(self) -> None:
        payload = build_payload(
            "quest",
            5,
            [],
            [],
            hits_by_value={5: [{"flag_value": 5, "source_type": "fsm"}]},
            candidate_hits_by_value={},
            exe_results={},
            corpus_index=self.corpus_index,
            json_cache=self.json_cache,
        )

        graph = payload["quest_graph_expansion"]
        direct_family_nodes = [node for node in graph["nodes"] if node["kind"] == "direct_family"]
        self.assertTrue(any(node["metadata"].get("source_type") == "fsm" for node in direct_family_nodes))

    def test_asciidoc_report_links_json_paths_with_line_numbers(self) -> None:
        lines = build_asciidoc_lines(
            {
                "query": {"mode": "quest", "value": 40000001},
                "generated_at": "2026-04-12T00:00:00+00:00",
                "targets": [
                    {
                        "target": {
                            "flag_value": 123,
                            "quest_id": 40000001,
                            "flag_type": "quest_flag",
                            "origin": "derived",
                            "doc_comment": "",
                        },
                        "hits": [
                            {
                                "resource_family": "qst",
                                "source_type": "qst",
                                "derivation_class": "direct_deterministic",
                                "confidence": 92,
                                "file_path": "client/03040008/quest/q40000001.arc.json",
                                "json_path": "Resource[0].Path",
                                "field_name": "Path",
                                "why": "Test hit",
                            }
                        ],
                        "candidate_hits": [],
                    }
                ],
                "quest_graph_expansion": {
                    "max_depth": 1,
                    "node_count": 2,
                    "edge_count": 1,
                    "node_kind_counts": {"quest": 1, "stage": 1},
                    "derivation_counts": {"direct_deterministic": 3},
                    "nodes": [
                        {
                            "node_id": "quest:40000001",
                            "label": "Quest 40000001",
                            "kind": "quest",
                            "depth": 0,
                            "derivation_class": "direct_deterministic",
                        },
                        {
                            "node_id": "stage:st0001",
                            "label": "st0001",
                            "kind": "stage",
                            "depth": 1,
                            "derivation_class": "direct_deterministic",
                        },
                    ],
                    "edges": [
                        {
                            "from": "quest:40000001",
                            "to": "stage:st0001",
                            "edge_type": "quest_archive_stage",
                            "depth": 1,
                            "derivation_class": "direct_deterministic",
                            "why": "Test graph edge",
                        }
                    ],
                },
            }
        )

        content = "\n".join(lines)
        self.assertIn(
            "link:../../../../client/03040008/quest/q40000001.arc.json#L15[client/03040008/quest/q40000001.arc.json#L15]",
            content,
        )
        self.assertIn("[mermaid]", content)
        self.assertIn("flowchart TD", content)

    def test_q7_quest_does_not_promote_external_dependency_targets(self) -> None:
        payload = self._payload_for_quest(70032001)

        self.assertEqual(payload["quest_dependency_targets"], [])

    def test_quest_20090_dependency_targets_include_expected_q6_owner_flag(self) -> None:
        payload = self._payload_for_quest(20090)

        owner_indexes = {entry["owner_quest_id"]: entry for entry in payload["quest_owner_indexes"]}
        dependency_targets = {entry["owner_quest_id"]: entry for entry in payload["quest_dependency_targets"]}
        self.assertIn(60310000, owner_indexes)
        self.assertEqual(owner_indexes[60310000]["owner_family"], "q6")
        self.assertIn(6972, owner_indexes[60310000]["linked_flag_values"])
        self.assertIn(60310000, dependency_targets)
        self.assertEqual(dependency_targets[60310000]["owner_family"], "q6")
        self.assertIn(6972, dependency_targets[60310000]["flag_values"])

    def test_quest_5_includes_local_qst_targets(self) -> None:
        """Non-world-manage quests should seed local QST flags before fallback-only scanning."""
        targets, documented_targets = self._resolve_targets_for_quest(5)

        target_values = {target.flag_value for target in targets}
        self.assertTrue({5, 907, 911, 976, 1226}.issubset(target_values))

        local_qst_targets = [target for target in targets if target.origin == "derived_qst_local"]
        self.assertTrue(local_qst_targets, "Expected quest-local QST targets for quest 5")
        self.assertTrue(
            {907, 911, 976, 1226}.issubset({target.flag_value for target in local_qst_targets}),
            "Expected quest-local QST seeding to cover the known stage-layout values",
        )
        self.assertTrue(
            any(target.origin == "derived_special_query" and target.flag_value == 5 for target in documented_targets),
            "Quest-id association fallback should remain available alongside local QST targets",
        )

    def test_quest_70032001_matches_baseline(self) -> None:
        """The flagship manifest quest should produce identical output."""
        baseline_path = BASELINES_DIR / "quest_70032001_baseline.json"
        generated_path = GENERATED_DIR / "client_investigation_quest_70032001.json"

        self.assertTrue(baseline_path.exists(), f"Baseline not found: {baseline_path}")
        self.assertTrue(generated_path.exists(), f"Generated output not found: {generated_path}")

        baseline = _load_json(baseline_path)
        generated = _strip_volatile(_load_json(generated_path))

        # Compare structure
        self.assertEqual(baseline["format"], generated["format"])
        self.assertEqual(baseline["query"], generated["query"])
        self.assertEqual(len(baseline["targets"]), len(generated["targets"]))

        # Compare each target's hit counts and target metadata
        for i, (b_target, g_target) in enumerate(zip(baseline["targets"], generated["targets"])):
            b_meta = b_target["target"]
            g_meta = g_target["target"]
            self.assertEqual(
                b_meta, g_meta,
                f"Target {i} metadata mismatch: {b_meta} != {g_meta}",
            )
            self.assertEqual(
                len(b_target.get("hits", [])),
                len(g_target.get("hits", [])),
                f"Target {i} (flag={b_meta['flag_value']}) hit count mismatch",
            )
            self.assertEqual(
                len(b_target.get("candidate_hits", [])),
                len(g_target.get("candidate_hits", [])),
                f"Target {i} (flag={b_meta['flag_value']}) candidate count mismatch",
            )

    def test_quest_70032001_structural_integrity(self) -> None:
        """Verify structural properties of a known quest output."""
        generated_path = GENERATED_DIR / "client_investigation_quest_70032001.json"
        if not generated_path.exists():
            self.skipTest("Generated output not found")

        data = _load_json(generated_path)
        self.assertEqual(data["format"], "client_investigation.v4")
        self.assertEqual(data["query"]["mode"], "quest")
        self.assertEqual(data["query"]["value"], 70032001)
        self.assertGreater(len(data["targets"]), 0)

        # Every target should have the expected structure
        for target_report in data["targets"]:
            target = target_report["target"]
            self.assertIn("flag_value", target)
            self.assertIn("flag_type", target)
            self.assertIn("origin", target)
            self.assertIsInstance(target_report.get("hits", []), list)
            self.assertIsInstance(target_report.get("candidate_hits", []), list)

        # Total hits should be substantial for this quest
        total_hits = sum(len(t.get("hits", [])) for t in data["targets"])
        self.assertGreater(total_hits, 100, "Expected significant hit count for quest 70032001")


if __name__ == "__main__":
    unittest.main()
