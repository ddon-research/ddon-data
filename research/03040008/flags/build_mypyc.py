"""Build the optional mypyc-accelerated hot-path modules in-place."""

from __future__ import annotations

from setuptools import setup
from mypyc.build import mypycify


MODULES = [
    "src/ddon_flags/scan_utils.py",
    "src/ddon_flags/scan_models.py",
    "src/ddon_flags/client_scanner.py",
    "src/ddon_flags/corpus_index.py",
    "src/ddon_flags/json_cache.py",
    "src/ddon_flags/candidate_finder.py",
    "src/ddon_flags/handlers/_helpers.py",
    "src/ddon_flags/handlers/quest_handlers.py",
    "src/ddon_flags/handlers/layout_handlers.py",
    "src/ddon_flags/handlers/fsm_handlers.py",
    "src/ddon_flags/handlers/marker_handlers.py",
    "src/ddon_flags/handlers/npc_handlers.py",
    "src/ddon_flags/handlers/special_handlers.py",
]


def main() -> None:
    """Compile the documented hot-path module set with mypyc."""

    setup(
        name="ddon-flags-mypyc",
        package_dir={"": "src"},
        packages=["ddon_flags", "ddon_flags.handlers"],
        ext_modules=mypycify(
            MODULES,
            opt_level="3",
            debug_level="1",
            strict_dunder_typing=False,
            log_trace=False,
        ),
        script_args=["build_ext", "--inplace"],
    )


if __name__ == "__main__":
    main()
