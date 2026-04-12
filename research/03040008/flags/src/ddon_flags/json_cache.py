"""In-memory JSON payload cache for decoded client resources.

On a research workstation the entire scanner-relevant corpus (~40 K files)
fits comfortably in memory.  Caching parsed payloads means the first quest
scan loads everything from disk, and all subsequent quests operate purely
from RAM.

Usage::

    cache = JsonCache()
    payload = cache.load(path)          # parsed dict / list, or None
    cache.preload(corpus_index, verbose=True)
"""
from __future__ import annotations

import orjson
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .corpus_index import CorpusIndex


class JsonCache:
    """Thread-unsafe JSON payload cache keyed by absolute ``Path``."""

    def __init__(self) -> None:
        self._store: dict[Path, Any] = {}
        self._misses: int = 0
        self._hits: int = 0

    # -- Core API ------------------------------------------------------------

    def load(self, path: Path) -> Any | None:
        """Return the cached payload, or parse from disk and cache it."""
        cached = self._store.get(path)
        if cached is not None:
            self._hits += 1
            return cached
        # Sentinel for previously-failed loads.
        if path in self._store:
            self._misses += 1
            return None
        payload = self._parse(path)
        self._store[path] = payload
        return payload

    def preload(self, index: "CorpusIndex", *, verbose: bool = False) -> None:
        """Bulk-load all scanner-relevant and MSS files into cache."""
        loaded = 0
        failed = 0
        for _suffix, path in index.all_scanner_paths():
            payload = self._parse(path)
            self._store[path] = payload
            if payload is not None:
                loaded += 1
            else:
                failed += 1
        for path in index.mss_paths():
            payload = self._parse(path)
            self._store[path] = payload
            if payload is not None:
                loaded += 1
            else:
                failed += 1
        if verbose:
            print(f"  JSON cache: {loaded} loaded, {failed} failed, {loaded + failed} total")

    # -- Diagnostics ---------------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._store)

    @property
    def stats(self) -> dict[str, int]:
        return {"cached": len(self._store), "hits": self._hits, "misses": self._misses}

    def clear(self) -> None:
        self._store.clear()
        self._hits = 0
        self._misses = 0

    # -- Internal ------------------------------------------------------------

    @staticmethod
    def _parse(path: Path) -> Any | None:
        try:
            return orjson.loads(path.read_bytes())
        except (OSError, UnicodeDecodeError, orjson.JSONDecodeError):
            return None
