"""Authoritative target manifest for the current Season 3 quest/flag investigation.

This module captures the exact user-supplied quest IDs, quest flags, and layout
flags that the current validation and batch workflows must use. It exists to
prevent drift between the investigation CLI, one-off validation scripts, and
archive summaries.

These values define WHAT to investigate. They are not evidence sources.
"""
from __future__ import annotations

from typing import Final


AUTHORITATIVE_WORLD_MANAGE_TARGETS: Final[dict[int, dict[str, tuple[int, ...]]]] = {
    70000001: {
        "quest_flags": (
            364, 551, 569, 570, 591, 616, 657, 659, 660, 661, 662, 663,
            703, 704, 707, 764, 765, 766, 768, 771, 772, 784, 786, 787,
            830, 831, 843, 846, 847, 848, 849, 850, 851, 891, 927, 932,
        ),
        "layout_flags": (
            1109, 1111, 1150, 1201, 1215, 1216, 1217, 1218, 1219, 1220,
            1221, 1222, 1223, 1224, 1250, 1262, 1293, 1297, 1310, 1317,
            1658, 1671, 2208, 2212, 2380,
        ),
    },
    70001001: {
        "quest_flags": (),
        "layout_flags": (1851, 1954),
    },
    70003001: {
        "quest_flags": (),
        "layout_flags": (1098, 1104, 1106, 1119, 1121, 1123, 1202, 2429, 2431, 2458),
    },
    70002001: {
        "quest_flags": (),
        "layout_flags": (1113, 1115, 1117, 3859),
    },
    70004001: {
        "quest_flags": (),
        "layout_flags": (761,),
    },
    70020001: {
        "quest_flags": (1400, 1409, 1490, 1491, 1524, 1627),
        "layout_flags": (3002, 3805),
    },
    70021001: {
        "quest_flags": (),
        "layout_flags": (3650,),
    },
    70022001: {
        "quest_flags": (2424, 2425, 2428),
        "layout_flags": (3950, 4043, 4470, 4555, 4557, 4806),
    },
    70023001: {
        "quest_flags": (),
        "layout_flags": (4372, 4507, 4511, 4516),
    },
    70030001: {
        "quest_flags": (),
        "layout_flags": (
            5552, 5557, 5584, 5587, 5589, 5614, 5632, 5634, 5636, 5669,
            5705, 6151, 6322, 6469, 6470, 6471, 6472, 6473, 6474, 6539,
            6561, 6750, 6968, 6969, 7206,
        ),
    },
    70030002: {
        "quest_flags": (2952,),
        "layout_flags": (6194, 7316),
    },
    70032001: {
        "quest_flags": (),
        "layout_flags": (7240, 7341, 7386, 7496, 7512, 7544, 7549, 7551, 7553, 7555, 7557, 7927, 7929),
    },
    70033001: {
        "quest_flags": (),
        "layout_flags": (7888, 7889, 7965, 7967, 7973, 8043, 8044, 8045, 8046, 8047, 8066, 8133, 8201, 8202),
    },
    70034001: {
        "quest_flags": (5184, 5185, 5186, 5187, 5379),
        "layout_flags": (),
    },
}

AUTHORITATIVE_WORLD_MANAGE_QUEST_IDS: Final[tuple[int, ...]] = tuple(AUTHORITATIVE_WORLD_MANAGE_TARGETS.keys())


def get_authoritative_targets_for_quest(quest_id: int) -> dict[str, tuple[int, ...]] | None:
    return AUTHORITATIVE_WORLD_MANAGE_TARGETS.get(quest_id)
