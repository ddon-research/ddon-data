"""Quest-family classification helpers for client-side investigations."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class QuestFamilyInfo:
    key: str
    label: str
    description: str
    discovery_focus: str
    supported: bool = True

    def to_dict(self) -> dict[str, str | bool]:
        return asdict(self)


_UNKNOWN = QuestFamilyInfo(
    key="unknown",
    label="Unknown Quest Family",
    description="Quest family could not be inferred from the client quest id pattern.",
    discovery_focus="treat_as_generic",
    supported=False,
)


def classify_quest_family(quest_id: int) -> QuestFamilyInfo:
    text = f"{quest_id:08d}"
    if text.startswith("0000"):
        return QuestFamilyInfo(
            key="q0",
            label="Main Quest",
            description="Story progression quests and adjacent mainline quest-state flows.",
            discovery_focus="local_stage_topology_plus_external_dependencies",
        )
    if text.startswith("0001"):
        return QuestFamilyInfo(
            key="q1",
            label="Wildhunt / Subjugation",
            description="Wildhunt and subjugation-style quests with specialized progression rules.",
            discovery_focus="local_stage_topology_plus_special_hunt_dependencies",
        )
    if text.startswith("0002"):
        return QuestFamilyInfo(
            key="q2",
            label="World Quest",
            description="Regional and area quests outside the main-story progression chain.",
            discovery_focus="local_stage_topology_plus_persistent_world_state",
        )
    if text.startswith("0003"):
        return QuestFamilyInfo(
            key="q3",
            label="Light Quest",
            description="Light and board-style quests with repeatable or lightweight stage flows.",
            discovery_focus="local_stage_topology_plus_board_repeatability",
        )

    leading = text[0]
    if leading == "4":
        return QuestFamilyInfo(
            key="q4",
            label="Light / Board Quest",
            description="Light quests and board-quest style errands with lightweight or text-heavy quest packaging.",
            discovery_focus="local_stage_topology_plus_board_quest_context",
        )
    if leading == "5":
        return QuestFamilyInfo(
            key="q5",
            label="Extreme / Grand Mission",
            description="Extreme and grand mission content with sortie and cycle metadata.",
            discovery_focus="esi_csi_sortie_topology",
        )
    if leading == "6":
        return QuestFamilyInfo(
            key="q6",
            label="Tutorial / Unlock / Area Trial",
            description="Tutorial, area-trial, unlock, and occasional festival quests.",
            discovery_focus="jtq_tqg_jmc_scaffolding",
        )
    if leading == "7":
        return QuestFamilyInfo(
            key="q7",
            label="World Manage",
            description="Persistent world-manage state that can affect all other quest families.",
            discovery_focus="persistent_owner_state",
        )
    if leading == "8":
        return QuestFamilyInfo(
            key="q8",
            label="Partner Pawn Personal Quest",
            description="Partner Pawn personal quests and pawn-relationship quest flows.",
            discovery_focus="pawn_quest_talk_plus_personal_progression",
        )
    if leading == "9":
        return QuestFamilyInfo(
            key="q9",
            label="Reserved q9",
            description="Reserved or unimplemented quest-family bucket.",
            discovery_focus="unsupported_until_client_evidence",
            supported=False,
        )
    return _UNKNOWN