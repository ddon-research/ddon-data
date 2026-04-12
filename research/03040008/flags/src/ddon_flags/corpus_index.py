"""Single-pass file index for the decoded client corpus.

Walks the client root once and classifies every JSON file by scanner
suffix.  This eliminates repeated ``rglob`` traversals that dominate
the runtime of batch investigations.

Usage::

    index = build_corpus_index(ddon_data_root)
    for path in index.scanner_paths(".lot.json"):
        ...
    for path in index.mss_paths():
        ...
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .client_scanner import SCANNER_MAP
from .scan_utils import STAGE_CODE_PATTERN, parse_code


# Suffixes handled by the structured scanners (order doesn't matter).
_SCANNER_SUFFIXES: tuple[str, ...] = tuple(SCANNER_MAP.keys())

# MSS files are used only for enrichment, not scanning.
_MSS_SUFFIX = ".mss.json"


class CorpusIndex:
    """Pre-built index of JSON files in the decoded client corpus."""

    def __init__(
        self,
        by_suffix: dict[str, list[Path]],
        by_stage_code: dict[str, list[tuple[str, Path]]],
        mss: list[Path],
        other: list[Path],
        total: int,
    ) -> None:
        self._by_suffix = by_suffix
        self._by_stage_code = by_stage_code
        self._mss = mss
        self._other = other
        self._total = total

    # -- Accessors -----------------------------------------------------------

    @property
    def total_files(self) -> int:
        return self._total

    @property
    def scanner_file_count(self) -> int:
        return sum(len(paths) for paths in self._by_suffix.values())

    def scanner_paths(self, suffix: str) -> list[Path]:
        """Return all paths for a given scanner suffix (e.g. ".qst.json")."""
        return self._by_suffix.get(suffix, [])

    def all_scanner_paths(self) -> Iterator[tuple[str, Path]]:
        """Yield ``(suffix, path)`` for every scanner-relevant file."""
        for suffix, paths in self._by_suffix.items():
            for path in paths:
                yield suffix, path

    def stage_scanner_paths(self, stage_code: str) -> list[tuple[str, Path]]:
        """Return scanner-relevant files indexed under a stage code."""
        return self._by_stage_code.get(stage_code, [])

    def mss_paths(self) -> list[Path]:
        """Return all MSS message-set file paths."""
        return self._mss

    def other_paths(self) -> list[Path]:
        """Return all JSON paths not handled by scanners or MSS."""
        return self._other

    def all_json_paths(self) -> Iterator[Path]:
        """Yield every JSON path in the corpus (scanner + MSS + other)."""
        for paths in self._by_suffix.values():
            yield from paths
        yield from self._mss
        yield from self._other


def _classify_suffix(filename: str) -> str | None:
    """Return the matching scanner suffix, or None."""
    for suffix in _SCANNER_SUFFIXES:
        if filename.endswith(suffix):
            return suffix
    return None


def build_corpus_index(ddon_data_root: Path) -> CorpusIndex:
    """Walk the client corpus once and build a classified file index."""
    client_root = ddon_data_root / "client" / "03040008"

    by_suffix: dict[str, list[Path]] = {suffix: [] for suffix in _SCANNER_SUFFIXES}
    by_stage_code: dict[str, list[tuple[str, Path]]] = {}
    mss: list[Path] = []
    other: list[Path] = []
    total = 0

    if not client_root.exists():
        return CorpusIndex(by_suffix, by_stage_code, mss, other, total)

    for json_path in client_root.rglob("*.json"):
        total += 1
        name = json_path.name

        suffix = _classify_suffix(name)
        if suffix is not None:
            by_suffix[suffix].append(json_path)
            stage_code = parse_code(STAGE_CODE_PATTERN, json_path.as_posix())
            if stage_code:
                by_stage_code.setdefault(stage_code, []).append((suffix, json_path))
            continue

        if name.endswith(_MSS_SUFFIX):
            mss.append(json_path)
            continue

        other.append(json_path)

    return CorpusIndex(by_suffix, by_stage_code, mss, other, total)
