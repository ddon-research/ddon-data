"""Shared models and relationship constants for the flags tooling."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final


OPTIONAL_INT_FIELDS: Final[tuple[str, ...]] = (
    "quest_id",
    "stage_no",
    "group_serial",
    "msg_serial",
    "npc_id",
)
OPTIONAL_STR_FIELDS: Final[tuple[str, ...]] = (
    "flag_kind",
    "relationship",
    "quest_name",
    "quest_name_jp",
    "stage_name",
    "stage_name_jp",
    "area_name",
    "area_name_jp",
    "stage_code",
    "event_code",
    "comment",
    "context",
    "npc_name",
    "npc_name_jp",
    "function_name",
    "function_name_jp",
)


@dataclass(frozen=True)
class FlagHit:
    """A single reference to a target value found in decoded client data."""

    source_type: str
    file_path: str
    json_path: str
    field_name: str
    flag_value: int
    flag_kind: str = ""
    relationship: str = ""
    quest_id: int = 0
    quest_name: str = ""
    quest_name_jp: str = ""
    stage_no: int = 0
    stage_name: str = ""
    stage_name_jp: str = ""
    area_name: str = ""
    area_name_jp: str = ""
    stage_code: str = ""
    event_code: str = ""
    comment: str = ""
    context: str = ""
    group_serial: int = 0
    msg_serial: int = 0
    npc_id: int = 0
    npc_name: str = ""
    npc_name_jp: str = ""
    function_name: str = ""
    function_name_jp: str = ""

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "source_type": self.source_type,
            "file_path": self.file_path,
            "json_path": self.json_path,
            "field_name": self.field_name,
            "flag_value": self.flag_value,
        }
        for field_name in OPTIONAL_STR_FIELDS:
            value = getattr(self, field_name)
            if value:
                data[field_name] = value
        for field_name in OPTIONAL_INT_FIELDS:
            value = getattr(self, field_name)
            if value:
                data[field_name] = value
        return data


REL_LAYOUT_GUARD = "layout_guard"
REL_DOOR_GATE = "door_gate"
REL_WARP_GATE = "warp_gate"
REL_QUEST_CONDITION = "quest_condition"
REL_QUEST_ERASE = "quest_erase"
REL_EVENT_STATE = "event_state"
REL_FSM_CHECK = "fsm_check"
REL_FSM_SET = "fsm_set"
REL_FSM_FREE_FLAG = "fsm_free_flag"
REL_NPC_STATE = "npc_state"
REL_NPC_CHATTER = "npc_chatter"
REL_NPC_FUNCTION = "npc_function"
REL_MARKER_GATE = "marker_gate"
REL_BLOCK_QUEST = "block_quest"
REL_QUEST_OM = "quest_om"
REL_TEXT_QUEST = "text_quest"
REL_FIELD_ADJOIN = "field_adjoin"
REL_EVENT_PARAM = "event_param"
REL_EVIDENCE_FLAG = "evidence_flag"
REL_REPEATABLE_SORTIE = "repeatable_sortie"
REL_TUTORIAL_QUEST = "tutorial_quest"
REL_TUTORIAL_GROUP = "tutorial_group"
REL_JOB_MASTER = "job_master"
REL_SPOT_BLOCK = "spot_block"