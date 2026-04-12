"""Run the primary flag investigation entrypoint as a module."""

from __future__ import annotations

from importlib import import_module


def main() -> None:
    """Load the primary CLI lazily during the migration to src layout."""

    module = import_module("ddon_flags.investigate_flags")
    module.main()


if __name__ == "__main__":
    main()
