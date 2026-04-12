"""Remove build products and caches for the flags project."""

from __future__ import annotations

import shutil
from pathlib import Path

from ._paths import FLAGS_PROJECT_ROOT


DIRECTORIES_TO_REMOVE = (
    FLAGS_PROJECT_ROOT / "build",
    FLAGS_PROJECT_ROOT / "handlers",
    FLAGS_PROJECT_ROOT / ".mypy_cache",
    FLAGS_PROJECT_ROOT / "__pycache__",
)


def _is_virtual_environment_path(path: Path) -> bool:
    return any(part.startswith(".venv") for part in path.parts)


def _remove_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
        print(f"Removed directory: {path}")


def _remove_matching_files(pattern: str) -> None:
    for path in FLAGS_PROJECT_ROOT.rglob(pattern):
        if _is_virtual_environment_path(path):
            continue
        if not path.is_file():
            continue
        path.unlink()
        print(f"Removed file: {path}")


def main() -> None:
    """Remove stale mypyc outputs, caches, and temporary build directories."""

    for path in DIRECTORIES_TO_REMOVE:
        _remove_directory(path)

    _remove_matching_files("*.pyd")
    _remove_matching_files("*.so")

    for path in FLAGS_PROJECT_ROOT.rglob("__pycache__"):
        if _is_virtual_environment_path(path):
            continue
        if path.is_dir():
            shutil.rmtree(path)
            print(f"Removed directory: {path}")


if __name__ == "__main__":
    main()
