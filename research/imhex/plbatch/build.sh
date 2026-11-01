#!/usr/bin/env bash
# Build plbatch against PatternLanguage at the commit ImHex 1.38.1 pins, with MSYS2 mingw64.
#
# Usage: research/imhex/plbatch/build.sh
# Output: research/imhex/plbatch/build/bin/plbatch.exe (the build/ folder is gitignored).
#
# Environment overrides:
#   MINGW_BIN  MSYS2 mingw64 bin dir (default /c/msys64/mingw64/bin). Never Strawberry's g++/cmake.
#   PL_URL     PatternLanguage remote (default https://github.com/WerWolv/PatternLanguage)
set -o errexit -o nounset -o pipefail

PL_COMMIT=fb6ea061f7c8b66ed94b44ff1d3a10ee63a82612   # tag ImHex-v1.38.1
PL_URL=${PL_URL:-https://github.com/WerWolv/PatternLanguage}
MINGW_BIN=${MINGW_BIN:-/c/msys64/mingw64/bin}

die() { echo "ERROR: $*" >&2; exit 2; }

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
build=$here/build
src=$build/pl-src
obj=$build/obj

command -v git >/dev/null 2>&1 || die "git not found"
for tool in gcc g++ cmake ninja ld.lld; do
  command -v "$MINGW_BIN/$tool" >/dev/null 2>&1 \
    || die "$MINGW_BIN/$tool not found (pacman -S mingw-w64-x86_64-{gcc,cmake,ninja,lld})"
done

# Fetch the pinned source once; never build inside the reference clone D:/GitHub/WerWolv/PatternLanguage.
if [[ ! -d $src/.git ]]; then
  mkdir -p "$build"
  git init -q "$src"
  git -C "$src" remote add origin "$PL_URL"
fi
if [[ $(git -C "$src" rev-parse -q --verify HEAD 2>/dev/null || true) != "$PL_COMMIT" ]]; then
  git -C "$src" fetch -q --depth 1 origin "$PL_COMMIT"
  git -C "$src" -c advice.detachedHead=false checkout -q "$PL_COMMIT"
fi
git -C "$src" submodule update -q --init --recursive --depth 1
[[ $(git -C "$src" rev-parse HEAD) == "$PL_COMMIT" ]] || die "PatternLanguage checkout is not at $PL_COMMIT"

# The mingw64 tools must find their own DLLs first, not Strawberry's.
export PATH="$MINGW_BIN:$PATH"
"$MINGW_BIN/cmake" -S "$here" -B "$obj" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="$MINGW_BIN/gcc.exe" \
  -DCMAKE_CXX_COMPILER="$MINGW_BIN/g++.exe" \
  -DCMAKE_MAKE_PROGRAM="$MINGW_BIN/ninja.exe" \
  -DCMAKE_CXX_FLAGS="-fuse-ld=lld" \
  -DCMAKE_EXE_LINKER_FLAGS="-fuse-ld=lld" \
  -DCMAKE_RUNTIME_OUTPUT_DIRECTORY="$build/bin" \
  -DPL_SOURCE_DIR="$src"
"$MINGW_BIN/cmake" --build "$obj" --target plbatch
echo "built $build/bin/plbatch.exe"
