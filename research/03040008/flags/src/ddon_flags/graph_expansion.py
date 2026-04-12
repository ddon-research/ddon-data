"""Bounded quest graph expansion over deterministic quest, stage, and owner edges."""
from __future__ import annotations

from collections import Counter
from typing import Any

from .derivation import DerivationClass
from .reverse_indexes import build_reverse_indexes


def _node_id(kind: str, *parts: Any) -> str:
    return ":".join([kind, *(str(part) for part in parts if str(part))])


def _add_node(
    nodes: dict[str, dict[str, Any]],
    *,
    node_id: str,
    label: str,
    kind: str,
    depth: int,
    derivation_class: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    if node_id in nodes:
        return
    nodes[node_id] = {
        "node_id": node_id,
        "label": label,
        "kind": kind,
        "depth": depth,
        "derivation_class": derivation_class,
        "metadata": metadata or {},
    }


def _add_edge(
    edges: dict[tuple[str, str, str], dict[str, Any]],
    *,
    from_id: str,
    to_id: str,
    edge_type: str,
    depth: int,
    derivation_class: str,
    why: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    key = (from_id, to_id, edge_type)
    if key in edges:
        return
    edges[key] = {
        "from": from_id,
        "to": to_id,
        "edge_type": edge_type,
        "depth": depth,
        "derivation_class": derivation_class,
        "why": why,
        "metadata": metadata or {},
    }


def _add_stage_nodes(
    *,
    quest_node_id: str,
    archive_context: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, str]:
    stage_nodes: dict[str, str] = {}
    for stage in archive_context.get("stages", []):
        if not isinstance(stage, dict):
            continue
        stage_code = str(stage.get("stage_code") or "")
        if not stage_code:
            continue
        stage_label = stage_code
        if stage.get("stage_name"):
            stage_label += f" -- {stage['stage_name']}"
        stage_node_id = _node_id("stage", stage_code)
        stage_nodes[stage_code] = stage_node_id
        _add_node(
            nodes,
            node_id=stage_node_id,
            label=stage_label,
            kind="stage",
            depth=1,
            derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
            metadata={"stage_code": stage_code},
        )
        _add_edge(
            edges,
            from_id=quest_node_id,
            to_id=stage_node_id,
            edge_type="quest_archive_stage",
            depth=1,
            derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
            why="Quest archive topology directly links this quest to the stage code.",
        )
    return stage_nodes


def _add_direct_family_nodes(
    *,
    quest_node_id: str,
    hits_by_value: dict[int, list[dict[str, Any]]],
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str], dict[str, Any]],
) -> None:
    family_counts = Counter(
        str(hit.get("source_type") or "")
        for hits in hits_by_value.values()
        for hit in hits
        if str(hit.get("source_type") or "")
    )
    for source_type, count in sorted(family_counts.items()):
        family_node_id = _node_id("direct-family", source_type)
        _add_node(
            nodes,
            node_id=family_node_id,
            label=f"{source_type} direct hits ({count})",
            kind="direct_family",
            depth=1,
            derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
            metadata={"source_type": source_type, "hit_count": count},
        )
        _add_edge(
            edges,
            from_id=quest_node_id,
            to_id=family_node_id,
            edge_type="direct_source_family",
            depth=1,
            derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
            why="Decoded direct hits for the quest targets include this source family.",
        )


def _ensure_owner_node(
    *,
    owner: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
) -> str:
    owner_quest_id = int(owner.get("owner_quest_id") or 0)
    owner_node_id = _node_id("owner-quest", owner_quest_id)
    _add_node(
        nodes,
        node_id=owner_node_id,
        label=f"Owner quest {owner_quest_id} ({owner.get('owner_family', '')})",
        kind="owner_quest",
        depth=2,
        derivation_class=str(owner.get("derivation_class") or DerivationClass.OWNER_INDEX.value),
        metadata={
            "owner_quest_id": owner_quest_id,
            "owner_family": str(owner.get("owner_family") or ""),
            "flag_count": int(owner.get("flag_count") or 0),
        },
    )
    return owner_node_id


def _add_owner_index_edges(
    *,
    quest_node_id: str,
    owner_indexes: list[dict[str, Any]],
    stage_nodes: dict[str, str],
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[int, str]:
    owner_nodes: dict[int, str] = {}
    for owner in owner_indexes:
        if not isinstance(owner, dict):
            continue
        owner_quest_id = int(owner.get("owner_quest_id") or 0)
        if owner_quest_id <= 0:
            continue
        owner_node_id = _ensure_owner_node(owner=owner, nodes=nodes)
        owner_nodes[owner_quest_id] = owner_node_id
        linked_stage_codes = [str(value) for value in (owner.get("linked_stage_codes") or []) if str(value)]
        if not linked_stage_codes:
            _add_edge(
                edges,
                from_id=quest_node_id,
                to_id=owner_node_id,
                edge_type="owner_index_link",
                depth=2,
                derivation_class=DerivationClass.OWNER_INDEX.value,
                why="Stage-neighborhood cues link this quest to the reusable external owner catalog.",
                metadata={"linked_flag_values": owner.get("linked_flag_values") or []},
            )
            continue
        for stage_code in linked_stage_codes:
            stage_node_id = stage_nodes.get(stage_code)
            if stage_node_id is None:
                continue
            _add_edge(
                edges,
                from_id=stage_node_id,
                to_id=owner_node_id,
                edge_type="stage_owner_index",
                depth=2,
                derivation_class=DerivationClass.OWNER_INDEX.value,
                why="Stage-neighborhood cues on this stage link to the reusable owner catalog.",
                metadata={"linked_flag_values": owner.get("linked_flag_values") or []},
            )
    return owner_nodes


def _add_dependency_edges(
    *,
    quest_node_id: str,
    dependency_targets: list[dict[str, Any]],
    owner_nodes: dict[int, str],
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str], dict[str, Any]],
) -> None:
    for dependency in dependency_targets:
        if not isinstance(dependency, dict):
            continue
        owner_quest_id = int(dependency.get("owner_quest_id") or 0)
        if owner_quest_id <= 0:
            continue
        owner_node_id = owner_nodes.get(owner_quest_id)
        if owner_node_id is None:
            owner_node_id = _ensure_owner_node(owner=dependency, nodes=nodes)
            owner_nodes[owner_quest_id] = owner_node_id
        _add_edge(
            edges,
            from_id=quest_node_id,
            to_id=owner_node_id,
            edge_type="promoted_dependency",
            depth=2,
            derivation_class=DerivationClass.DEPENDENCY_INFERRED.value,
            why=str(dependency.get("why") or "Promoted dependency target."),
            metadata={"flag_values": dependency.get("flag_values") or []},
        )


def _add_event_and_group_edges(
    *,
    quest_id: int,
    reverse_indexes: dict[str, Any],
    stage_nodes: dict[str, str],
    owner_nodes: dict[int, str],
    owner_indexes: list[dict[str, Any]],
    dependency_targets: list[dict[str, Any]],
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str], dict[str, Any]],
) -> None:
    owner_ids = {int(owner.get("owner_quest_id") or 0) for owner in owner_indexes if isinstance(owner, dict)}
    owner_ids.update(int(dep.get("owner_quest_id") or 0) for dep in dependency_targets if isinstance(dep, dict))
    interesting_flags = {
        int(value)
        for owner in owner_indexes
        if isinstance(owner, dict)
        for value in (owner.get("linked_flag_values") or [])
        if int(value) > 0
    }
    interesting_flags.update(
        int(value)
        for dep in dependency_targets
        if isinstance(dep, dict)
        for value in (dep.get("flag_values") or [])
        if int(value) > 0
    )

    for stage_code, event_entries in (reverse_indexes.get("stage_to_event_viewers") or {}).items():
        stage_node_id = stage_nodes.get(stage_code)
        if stage_node_id is None:
            continue
        for entry in event_entries:
            event_owner = int(entry.get("quest_id") or 0)
            if event_owner not in owner_ids and event_owner != quest_id:
                continue
            event_code = str(entry.get("event_code") or "")
            event_node_id = _node_id("event-viewer", stage_code, event_code, event_owner)
            _add_node(
                nodes,
                node_id=event_node_id,
                label=f"Event {stage_code}/{event_code or 'unknown'}",
                kind="event_viewer",
                depth=2,
                derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                metadata={"stage_code": stage_code, "event_code": event_code, "quest_id": event_owner},
            )
            _add_edge(
                edges,
                from_id=stage_node_id,
                to_id=event_node_id,
                edge_type="stage_event_viewer",
                depth=2,
                derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                why="Reverse indexes expose event-viewer edges on this quest stage.",
            )
            if event_owner in owner_nodes:
                _add_edge(
                    edges,
                    from_id=event_node_id,
                    to_id=owner_nodes[event_owner],
                    edge_type="event_owner",
                    depth=3,
                    derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                    why="The event-viewer row points to an owner quest already linked in the owner/dependency layer.",
                )

    for stage_code, stage_groups in (reverse_indexes.get("stage_group_references") or {}).items():
        stage_node_id = stage_nodes.get(stage_code)
        if stage_node_id is None:
            continue
        for group_no, group_entry in stage_groups.items():
            gpl_refs = [ref for ref in (group_entry.get("gpl_refs") or []) if isinstance(ref, dict)]
            selected_refs = [
                ref
                for ref in gpl_refs
                if int(ref.get("flag_value") or 0) in interesting_flags or int(ref.get("quest_id") or 0) in owner_ids
            ]
            if not selected_refs:
                continue
            group_node_id = _node_id("stage-group", stage_code, group_no)
            _add_node(
                nodes,
                node_id=group_node_id,
                label=f"GPL group {stage_code}/{group_no}",
                kind="stage_group",
                depth=2,
                derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                metadata={"stage_code": stage_code, "group_no": group_no},
            )
            _add_edge(
                edges,
                from_id=stage_node_id,
                to_id=group_node_id,
                edge_type="stage_group_reference",
                depth=2,
                derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                why="Reverse indexes expose GPL group references for this stage.",
            )
            for ref in selected_refs:
                owner_quest_id = int(ref.get("quest_id") or 0)
                if owner_quest_id in owner_nodes:
                    _add_edge(
                        edges,
                        from_id=group_node_id,
                        to_id=owner_nodes[owner_quest_id],
                        edge_type="gpl_owner_guard",
                        depth=3,
                        derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                        why="GPL guard data on this stage group references an owner quest already linked in the owner/dependency layer.",
                        metadata={"flag_value": ref.get("flag_value")},
                    )
            lot_reference = group_entry.get("lot_reference")
            if isinstance(lot_reference, dict) and lot_reference.get("file_path"):
                lot_node_id = _node_id("lot-file", lot_reference.get("file_name") or lot_reference.get("file_path"))
                _add_node(
                    nodes,
                    node_id=lot_node_id,
                    label=str(lot_reference.get("file_name") or lot_reference.get("file_path") or "LOT"),
                    kind="lot_file",
                    depth=3,
                    derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                    metadata={"file_path": lot_reference.get("file_path"), "type_names": lot_reference.get("type_names") or []},
                )
                _add_edge(
                    edges,
                    from_id=group_node_id,
                    to_id=lot_node_id,
                    edge_type="group_lot_reference",
                    depth=3,
                    derivation_class=DerivationClass.GRAPH_EXPANDED.value,
                    why="LOT association resolves the GPL group to a concrete stage layout file.",
                )


def _add_family_context_edges(
    *,
    quest_node_id: str,
    family_relationships: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str], dict[str, Any]],
) -> None:
    relationship_specs = {
        "quest_sequence": "Quest Sequence",
        "repeatable_sortie": "Repeatable Sortie",
        "tutorial_scaffolding": "Tutorial Scaffolding",
        "evidence_chain": "Evidence Chain",
        "blocked_spots": "Blocked Spots",
    }
    for key, label in relationship_specs.items():
        value = family_relationships.get(key)
        if not isinstance(value, dict):
            continue
        context_node_id = _node_id("family-context", key)
        _add_node(
            nodes,
            node_id=context_node_id,
            label=label,
            kind="family_context",
            depth=1,
            derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
            metadata={"context_key": key},
        )
        _add_edge(
            edges,
            from_id=quest_node_id,
            to_id=context_node_id,
            edge_type=f"family_context:{key}",
            depth=1,
            derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
            why="Family-specific decoded tables provide deterministic context for this quest.",
        )

        if key == "quest_sequence":
            for direction in ("previous", "next"):
                entry = value.get(direction)
                if not isinstance(entry, dict):
                    continue
                linked_quest_id = int(entry.get("quest_id") or 0)
                if linked_quest_id <= 0:
                    continue
                linked_node_id = _node_id("sequence-quest", linked_quest_id)
                _add_node(
                    nodes,
                    node_id=linked_node_id,
                    label=f"Quest {linked_quest_id}",
                    kind="sequence_quest",
                    depth=2,
                    derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
                    metadata={"quest_id": linked_quest_id, "direction": direction},
                )
                _add_edge(
                    edges,
                    from_id=context_node_id,
                    to_id=linked_node_id,
                    edge_type=f"sequence_{direction}",
                    depth=2,
                    derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
                    why="QuestSequence links this quest to its neighboring sequence quest.",
                )
        elif key == "repeatable_sortie":
            for cycle_sub_no in (value.get("cycle_sub_nos") or [])[:8]:
                sub_node_id = _node_id("cycle-sub-no", cycle_sub_no)
                _add_node(
                    nodes,
                    node_id=sub_node_id,
                    label=f"CycleSubNo {cycle_sub_no}",
                    kind="cycle_sub_no",
                    depth=2,
                    derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
                    metadata={"cycle_sub_no": cycle_sub_no},
                )
                _add_edge(
                    edges,
                    from_id=context_node_id,
                    to_id=sub_node_id,
                    edge_type="repeatable_cycle",
                    depth=2,
                    derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
                    why="Repeatable sortie tables link this quest to a cycle sub number.",
                )
        elif key == "tutorial_scaffolding":
            for group_id in (value.get("group_ids") or [])[:8]:
                group_node_id = _node_id("tutorial-group", group_id)
                _add_node(
                    nodes,
                    node_id=group_node_id,
                    label=f"Tutorial Group {group_id}",
                    kind="tutorial_group",
                    depth=2,
                    derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
                    metadata={"group_id": group_id},
                )
                _add_edge(
                    edges,
                    from_id=context_node_id,
                    to_id=group_node_id,
                    edge_type="tutorial_group",
                    depth=2,
                    derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
                    why="Tutorial quest tables group this quest into an authored tutorial scaffold.",
                )


def build_quest_graph_expansion(
    quest_id: int,
    *,
    targets: list[Any],
    hits_by_value: dict[int, list[dict[str, Any]]],
    family_relationships: dict[str, Any] | None,
    archive_context: dict[str, Any] | None,
    owner_indexes: list[dict[str, Any]] | None,
    dependency_targets: list[dict[str, Any]] | None,
    corpus_index: Any | None = None,
    json_cache: Any | None = None,
    max_depth: int = 3,
) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str], dict[str, Any]] = {}
    quest_node_id = _node_id("quest", quest_id)
    _add_node(
        nodes,
        node_id=quest_node_id,
        label=f"Quest {quest_id}",
        kind="quest",
        depth=0,
        derivation_class=DerivationClass.DIRECT_DETERMINISTIC.value,
        metadata={"quest_id": quest_id, "target_count": len(targets)},
    )

    archive_context = archive_context if isinstance(archive_context, dict) else {}
    family_relationships = family_relationships if isinstance(family_relationships, dict) else {}
    owner_indexes = [entry for entry in (owner_indexes or []) if isinstance(entry, dict)]
    dependency_targets = [entry for entry in (dependency_targets or []) if isinstance(entry, dict)]

    stage_nodes = _add_stage_nodes(quest_node_id=quest_node_id, archive_context=archive_context, nodes=nodes, edges=edges)
    _add_direct_family_nodes(quest_node_id=quest_node_id, hits_by_value=hits_by_value, nodes=nodes, edges=edges)
    _add_family_context_edges(quest_node_id=quest_node_id, family_relationships=family_relationships, nodes=nodes, edges=edges)

    reverse_indexes = build_reverse_indexes(
        quest_ids=(quest_id,),
        stage_codes=archive_context.get("stage_codes") or [],
        corpus_index=corpus_index,
        json_cache=json_cache,
    )
    owner_nodes = _add_owner_index_edges(
        quest_node_id=quest_node_id,
        owner_indexes=owner_indexes,
        stage_nodes=stage_nodes,
        nodes=nodes,
        edges=edges,
    )
    _add_dependency_edges(
        quest_node_id=quest_node_id,
        dependency_targets=dependency_targets,
        owner_nodes=owner_nodes,
        nodes=nodes,
        edges=edges,
    )
    _add_event_and_group_edges(
        quest_id=quest_id,
        reverse_indexes=reverse_indexes,
        stage_nodes=stage_nodes,
        owner_nodes=owner_nodes,
        owner_indexes=owner_indexes,
        dependency_targets=dependency_targets,
        nodes=nodes,
        edges=edges,
    )

    node_kind_counts = Counter(node["kind"] for node in nodes.values())
    edge_type_counts = Counter(edge["edge_type"] for edge in edges.values())
    derivation_counts = Counter(
        [node["derivation_class"] for node in nodes.values()] + [edge["derivation_class"] for edge in edges.values()]
    )
    return {
        "max_depth": max_depth,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_kind_counts": dict(sorted(node_kind_counts.items())),
        "edge_type_counts": dict(sorted(edge_type_counts.items())),
        "derivation_counts": dict(sorted(derivation_counts.items())),
        "nodes": sorted(nodes.values(), key=lambda item: (int(item.get("depth") or 0), str(item.get("kind") or ""), str(item.get("label") or ""))),
        "edges": sorted(edges.values(), key=lambda item: (int(item.get("depth") or 0), str(item.get("edge_type") or ""), str(item.get("from") or ""), str(item.get("to") or ""))),
    }
