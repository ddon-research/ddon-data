"""Compatibility wrapper for the migrated ddon_flags validation CLI."""

from __future__ import annotations

import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parent / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ddon_flags.validate_targets import main


if __name__ == "__main__":
    main()
