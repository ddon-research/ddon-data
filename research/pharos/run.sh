#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)

# Utility functions
require_cmd() {
  local cmd=$1
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: Required command '$cmd' not found in PATH" >&2
    exit 1
  fi
}

abs_path() {
  local path=$1
  if [[ "$path" =~ ^(/|[A-Za-z]:) ]]; then
    echo "$path"
    return
  fi
  echo "$(cd "$(dirname "$path")" && pwd -P)/$(basename "$path")"
}

host_to_docker_path() {
  local path=$1
  if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "$path" | sed -e 's|\\|/|g' -e 's|^\([A-Za-z]\):|/\L\1|'
  else
    echo "$path"
  fi
}

usage() {
  cat <<'USAGE'
Usage: run.sh <path-to-binary> [output-directory]

Analyze a 32-bit Windows executable with Pharos OOAnalyzer inside the
official Docker image. The script follows the recommended multi-step
workflow for large binaries (partition, fact extraction, Prolog, JSON).

Environment variables:
  PHAROS_IMAGE        Override the Docker image (default: ghcr.io/cmu-sei/pharos:master)
  PHAROS_MAX_MEMORY   Maximum memory in MB for partition/analysis (default: 50000)
  PHAROS_TIMEOUT      Per-function timeout in seconds (default: 60)
  PHAROS_THREADS      Override thread count for ooanalyzer (default: container nproc)

Examples:
  # Basic usage - output goes to <binary-dir>/pharos-<basename>
  ./run.sh /path/to/binary.exe

  # Specify custom output directory
  ./run.sh /path/to/binary.exe /path/to/output

  # Override memory limit (for large binaries on systems with lots of RAM)
  PHAROS_MAX_MEMORY=55000 ./run.sh /path/to/binary.exe

  # Override thread count
  PHAROS_THREADS=16 ./run.sh /path/to/binary.exe
USAGE
}

parse_args() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    usage
    exit 0
  fi

  BIN_PATH=$1
  
  if [[ ! -f "$BIN_PATH" ]]; then
    echo "Error: Binary file not found: $BIN_PATH" >&2
    exit 1
  fi

  BIN_PATH=$(abs_path "$BIN_PATH")
  BIN_DIR=$(dirname "$BIN_PATH")
  BIN_NAME=$(basename "$BIN_PATH")
  BASE_NAME=${BIN_NAME%.*}

  OUTPUT_DIR=${2:-"$BIN_DIR/pharos-${BASE_NAME}"}
  OUTPUT_DIR=$(abs_path "$OUTPUT_DIR")
}

prepare_environment() {
  require_cmd docker
  mkdir -p "$OUTPUT_DIR"

  IMAGE=${PHAROS_IMAGE:-ghcr.io/cmu-sei/pharos:master}
  MAX_MEMORY=${PHAROS_MAX_MEMORY:-50000}
  TIMEOUT=${PHAROS_TIMEOUT:-60}
  THREADS=${PHAROS_THREADS:-}

  if [[ -z $THREADS ]]; then
    THREAD_MSG="PHAROS_THREADS not set; container will auto-detect cores."
  else
    THREAD_MSG="Using PHAROS_THREADS=$THREADS"
  fi

  INPUT_DIR=$(host_to_docker_path "$BIN_DIR")
  OUTPUT_DIR_DOCKER=$(host_to_docker_path "$OUTPUT_DIR")

  export PHAROS_IMAGE="$IMAGE"
  export INPUT_DIR
  export OUTPUT_DIR="$OUTPUT_DIR_DOCKER"
  export BINARY_NAME="$BIN_NAME"
  export BASE_NAME
  export MAX_MEMORY
  export TIMEOUT
  export THREADS
}

print_plan() {
  cat <<INFO
=============================================================================
Running Pharos OOAnalyzer workflow with Docker Compose
=============================================================================
  Image:        ${PHAROS_IMAGE:-ghcr.io/cmu-sei/pharos:master}
  Binary:       $BIN_PATH ($BIN_NAME)
  Output dir:   $OUTPUT_DIR
  Max memory:   ${MAX_MEMORY} MB
  Timeout:      ${TIMEOUT} seconds per function
$THREAD_MSG
=============================================================================

INFO
}

run_analysis() {
  echo "Starting analysis with Docker Compose..."
  echo
  
  docker-compose -f "$SCRIPT_DIR/docker-compose.yml" run --rm ooanalyzer
  
  local exit_code=$?
  
  if [[ $exit_code -eq 0 ]]; then
    echo
    echo "==================================================================="
    echo "Analysis complete! Outputs written to:"
    echo "  $OUTPUT_DIR"
    echo "==================================================================="
  else
    echo
    echo "==================================================================="
    echo "Analysis failed with exit code: $exit_code"
    echo "Check logs in: $OUTPUT_DIR"
    echo "==================================================================="
    exit $exit_code
  fi
}

main() {
  parse_args "$@"
  prepare_environment
  print_plan
  run_analysis
}

main "$@"
