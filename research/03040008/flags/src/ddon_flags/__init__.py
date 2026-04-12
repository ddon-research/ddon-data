"""DDON client flag investigation package."""

from ._runtime import ensure_supported_runtime

ensure_supported_runtime()

__all__ = ["ensure_supported_runtime"]
