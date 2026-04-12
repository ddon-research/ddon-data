"""Shared derivation classes for evidence and inference outputs."""
from __future__ import annotations

from enum import Enum


class DerivationClass(str, Enum):
    DIRECT_DETERMINISTIC = "direct_deterministic"
    OWNER_INDEX = "owner_index"
    DEPENDENCY_INFERRED = "dependency_inferred"
    GRAPH_EXPANDED = "graph_expanded"
    LOWER_CONFIDENCE = "lower_confidence"
    BINARY_AUXILIARY = "binary_auxiliary"


DERIVATION_LABELS: dict[str, str] = {
    DerivationClass.DIRECT_DETERMINISTIC.value: "Direct",
    DerivationClass.OWNER_INDEX.value: "Owner Index",
    DerivationClass.DEPENDENCY_INFERRED.value: "Dependency",
    DerivationClass.GRAPH_EXPANDED.value: "Graph",
    DerivationClass.LOWER_CONFIDENCE.value: "Lower Confidence",
    DerivationClass.BINARY_AUXILIARY.value: "Binary",
}


def derivation_label(value: str) -> str:
    return DERIVATION_LABELS.get(value, value)


# Compatibility aliases for older imports and generated payload readers.
ProvenanceClass = DerivationClass
PROVENANCE_LABELS = DERIVATION_LABELS


def provenance_label(value: str) -> str:
    return derivation_label(value)