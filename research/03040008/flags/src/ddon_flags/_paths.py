"""Shared filesystem locations and external tool defaults for the flags suite."""

from __future__ import annotations

from pathlib import Path


FLAGS_PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = FLAGS_PROJECT_ROOT / "src"
DDON_DATA_ROOT = FLAGS_PROJECT_ROOT.parents[2]
CLIENT_ROOT = DDON_DATA_ROOT / "client" / "03040008"
GENERATED_DIR = FLAGS_PROJECT_ROOT / "generated"
TEST_BASELINES_DIR = FLAGS_PROJECT_ROOT / "test_baselines"

DEFAULT_UPSTREAM_ROOT = Path(
    r"C:\Users\morph\Documents\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream"
)
DEFAULT_DDO_EXE_PATH = Path(r"D:\DDON_03040008\DDO.exe")
DEFAULT_OBJDUMP_PATH = Path(r"C:\msys64\usr\bin\objdump.exe")
