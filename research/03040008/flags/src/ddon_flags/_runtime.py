"""Runtime checks shared by CLI entrypoints and package imports."""

from __future__ import annotations

import platform
import sys


def ensure_supported_runtime() -> None:
    """Reject unsupported interpreters for this project.

    The flags suite is validated only on CPython 3.14 because optional mypyc
    artifacts and the documented workflow both target that runtime.
    """

    implementation = platform.python_implementation()
    version_info = sys.version_info

    if implementation != "CPython":
        raise RuntimeError(
            "The flags suite only supports CPython 3.14. "
            f"Current runtime: {implementation} "
            f"{version_info.major}.{version_info.minor}.{version_info.micro}."
        )

    if (version_info.major, version_info.minor) != (3, 14):
        raise RuntimeError(
            "The flags suite only supports CPython 3.14. "
            "Create or activate the local uv environment with Python 3.14."
        )
