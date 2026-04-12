"""Compatibility shim for legacy provenance imports."""
from __future__ import annotations

from .derivation import DERIVATION_LABELS, DerivationClass, derivation_label


ProvenanceClass = DerivationClass
PROVENANCE_LABELS = DERIVATION_LABELS


def provenance_label(value: str) -> str:
    return derivation_label(value)