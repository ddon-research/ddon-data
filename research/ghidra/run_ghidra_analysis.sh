#!/bin/bash

# Unified Ghidra Analysis Runner
# This script runs either DWARF symbol exploration or function decompilation analysis
# in Ghidra headless mode based on the specified mode.
#
# Usage: ./run_ghidra_analysis.sh MODE [OPTIONS...]
#
# Modes:
#   dwarf     - DWARF Symbol Explorer mode
#   function  - Function Decompilation Analyzer mode
#
# DWARF Mode Usage:
#   ./run_ghidra_analysis.sh dwarf SYMBOL_NAME PROGRAM_NAME [LOG_LEVEL] [EXPLORE_DEPTH]
#   
#   Parameters:
#     SYMBOL_NAME: Symbol to explore (e.g., "rLandInfo")
#     PROGRAM_NAME: Program to analyze (e.g., "DDOORBIS.elf" or "*" for all programs)
#     LOG_LEVEL: "DEBUG" or "INFO" (default from .env)
#     EXPLORE_DEPTH: Maximum exploration depth 1-10 (default from .env)
#
# Function Mode Usage:
#   ./run_ghidra_analysis.sh function FUNCTION_NAME PROGRAM_NAME [LOG_LEVEL] [MAX_DEPTH]
#   
#   Parameters:
#     FUNCTION_NAME: Function to analyze (e.g., "rLandInfo::load")
#     PROGRAM_NAME: Program to analyze (e.g., "DDOORBIS.elf" or "*" for all programs)
#     LOG_LEVEL: "DEBUG" or "INFO" (default from .env)
#     MAX_DEPTH: Maximum recursion depth 1-10 (default from .env)
#
# Examples:
#   ./run_ghidra_analysis.sh dwarf "rLandInfo" "DDOORBIS.elf" "INFO" 5
#   ./run_ghidra_analysis.sh function "rLandInfo::load" "DDOORBIS.elf" "DEBUG" 3
# Quiet mode (suppress Ghidra system output, logs saved to logs/):
#   ./run_ghidra_analysis.sh dwarf "rLandInfo" "DDOORBIS.elf" --quiet
#   ./run_ghidra_analysis.sh function "rLandInfo::load" "DDOORBIS.elf" --quiet

# Script directory (for finding .env file)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Load configuration from .env file
ENV_FILE="$SCRIPT_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: Configuration file not found at: $ENV_FILE"
    echo "Please create a .env file with the required configuration variables."
    exit 1
fi

# Source the .env file
# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

# Output control configuration
QUIET_MODE=false
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Function to display usage information
show_usage() {
    echo "Usage: $0 MODE [OPTIONS...] [--quiet]"
    echo ""
    echo "Modes:"
    echo "  dwarf     - DWARF Symbol Explorer mode"
    echo "  function  - Function Decompilation Analyzer mode"
    echo ""
    echo "Options:"
    echo "  --quiet   - Suppress Ghidra system output (logs saved to $LOG_DIR)"
    echo ""
    echo "DWARF Mode:"
    echo "  $0 dwarf SYMBOL_NAME PROGRAM_NAME [LOG_LEVEL] [EXPLORE_DEPTH] [--quiet]"
    echo ""
    echo "  Parameters:"
    echo "    SYMBOL_NAME    Symbol to explore (e.g., 'rLandInfo')"
    echo "    PROGRAM_NAME   Program to analyze (e.g., 'DDOORBIS.elf' or '*' for all)"
    echo "    LOG_LEVEL      'DEBUG' or 'INFO' (default: $DEFAULT_LOG_LEVEL)"
    echo "    EXPLORE_DEPTH  Maximum exploration depth 1-10 (default: $DEFAULT_EXPLORE_DEPTH)"
    echo ""
    echo "Function Mode:"
    echo "  $0 function FUNCTION_NAME PROGRAM_NAME [LOG_LEVEL] [MAX_DEPTH] [--quiet]"
    echo ""
    echo "  Parameters:"
    echo "    FUNCTION_NAME  Function to analyze (e.g., 'rLandInfo::load')"
    echo "    PROGRAM_NAME   Program to analyze (e.g., 'DDOORBIS.elf' or '*' for all)"
    echo "    LOG_LEVEL      'DEBUG' or 'INFO' (default: $DEFAULT_LOG_LEVEL)"
    echo "    MAX_DEPTH      Maximum recursion depth 1-10 (default: $DEFAULT_MAX_DEPTH)"
    echo ""
    echo "Examples:"
    echo "  $0 dwarf 'rLandInfo' 'DDOORBIS.elf'"
    echo "  $0 dwarf 'MtObject' 'DDOORBIS.elf' 'DEBUG' 3 --quiet"
    echo "  $0 function 'rLandInfo::load' 'DDOORBIS.elf'"
    echo "  $0 function 'rLandInfo::load' '*' 'DEBUG' 5 --quiet"
}

# Validation functions
validate_log_level() {
    if [[ ! "$1" =~ ^(DEBUG|INFO)$ ]]; then
        echo "Error: LOG_LEVEL must be 'DEBUG' or 'INFO'"
        return 1
    fi
}

validate_depth() {
    local depth="$1"
    local param_name="$2"
    if [[ ! "$depth" =~ ^[1-9]|10$ ]]; then
        echo "Error: $param_name must be between 1 and 10"
        return 1
    fi
}

validate_required_files() {
    if [[ ! -f "$PYGHIDRA_RUN" ]]; then
        echo "Error: PyGhidra script not found at: $PYGHIDRA_RUN"
        echo "Please update PYGHIDRA_RUN in $ENV_FILE"
        return 1
    fi

    if [[ ! -d "$PROJECT_DIR" ]]; then
        echo "Error: Project directory not found at: $PROJECT_DIR"
        echo "Please update PROJECT_DIR in $ENV_FILE"
        return 1
    fi

    return 0
}

# Check for help flag or no arguments
if [[ $# -eq 0 || "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# Check for quiet mode flag in any position
for arg in "$@"; do
    if [[ "$arg" == "--quiet" ]]; then
        QUIET_MODE=true
        # Remove --quiet from arguments array
        set -- "${@/--quiet/}"
        break
    fi
done

# Get mode
MODE="$1"
shift

# Validate mode
if [[ "$MODE" != "dwarf" && "$MODE" != "function" ]]; then
    echo "Error: Invalid mode '$MODE'. Must be 'dwarf' or 'function'."
    echo ""
    show_usage
    exit 1
fi

# Validate required files
validate_required_files || exit 1

# Function to execute PyGhidra with output control
execute_pyghidra() {
    local cmd=("$@")
    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    local ghidra_log="$LOG_DIR/ghidra_${timestamp}.log"
    local script_log="$LOG_DIR/script_${timestamp}.log"
    local system_log="$LOG_DIR/system_${timestamp}.log"
    
    if [[ "$QUIET_MODE" == "true" ]]; then
        # In quiet mode, filter out system noise and only show script output
        "${cmd[@]}" -log "$ghidra_log" -scriptlog "$script_log" 2>&1 | \
        tee "$system_log" | \
        awk '
        BEGIN { in_script_paths = 0 }
        /HEADLESS Script Paths:/ { in_script_paths = 1; next }
        in_script_paths && /^[[:space:]]*[A-Za-z]:[\\]/ { next }
        in_script_paths && /^[[:space:]]*\/.*ghidra/ { next } 
        in_script_paths && /^[[:space:]]*[A-Za-z].*ghidra_scripts/ { next }
        /^INFO.*HEADLESS: execution starts/ { in_script_paths = 0; next }
        /Last used Python|Using Python command|Switching to Ghidra/ { next }
        /Name:|Version:|Summary:|Home-page:|Author|License:|Location:|Requires:|Required-by:/ { next }
        /INFO.*(Using log|Loading|Searching|Class search|Initializing|Random Number|Trust manager|Headless startup|Class searcher|Opening|Processing)/ { next }
        /^INFO.*SCRIPT:/ { next }
        { print }
        '
    else
        # Run normally but still log to files for debugging
        "${cmd[@]}" -log "$ghidra_log" -scriptlog "$script_log"
    fi
}

# Mode-specific parameter handling
if [[ "$MODE" == "dwarf" ]]; then
    # DWARF Symbol Explorer mode
    SYMBOL_NAME="${1:-}"
    PROGRAM_NAME="${2:-}"
    LOG_LEVEL="${3:-$DEFAULT_LOG_LEVEL}"
    EXPLORE_DEPTH="${4:-$DEFAULT_EXPLORE_DEPTH}"
    
    # Validation
    if [[ -z "$SYMBOL_NAME" ]]; then
        echo "Error: Symbol name is required for dwarf mode!"
        echo ""
        show_usage
        exit 1
    fi
    
    if [[ -z "$PROGRAM_NAME" ]]; then
        echo "Error: Program name is required for dwarf mode!"
        echo ""
        show_usage
        exit 1
    fi
    
    validate_log_level "$LOG_LEVEL" || exit 1
    validate_depth "$EXPLORE_DEPTH" "EXPLORE_DEPTH" || exit 1
    
    # Check script file
    SCRIPT_PATH="$SCRIPTS_BASE_DIR/$DWARF_EXPLORER_SCRIPT"
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        echo "Error: DWARF explorer script not found at: $SCRIPT_PATH"
        echo "Please update DWARF_EXPLORER_SCRIPT in $ENV_FILE"
        exit 1
    fi
    
    # Set environment variables for the script
    export SYMBOL_NAME="$SYMBOL_NAME"
    export LOG_LEVEL="$LOG_LEVEL"
    export EXPLORE_DEPTH="$EXPLORE_DEPTH"
    
    if [[ "$QUIET_MODE" != "true" ]]; then
        echo "=== DWARF Symbol Explorer - Headless Mode ==="
        echo "Symbol to explore: $SYMBOL_NAME"
        echo "Program to analyze: $PROGRAM_NAME"
        echo "Log level: $LOG_LEVEL"
        echo "Exploration depth: $EXPLORE_DEPTH"
        echo "Project: $PROJECT_DIR/$PROJECT_NAME"
        echo "Script: $SCRIPT_PATH"
        [[ "$QUIET_MODE" == "true" ]] && echo "Quiet mode: enabled"
        echo "=============================================="
        echo ""
    fi
    
    # Run PyGhidra for DWARF exploration
    execute_pyghidra "$PYGHIDRA_RUN" --headless "$PROJECT_DIR" "$PROJECT_NAME" \
        -scriptPath "$SCRIPTS_BASE_DIR" \
        -postScript "$DWARF_EXPLORER_SCRIPT" \
        -process "$PROGRAM_NAME" \
        -noanalysis

elif [[ "$MODE" == "function" ]]; then
    # Function Decompilation Analyzer mode
    FUNCTION_NAME="${1:-}"
    PROGRAM_NAME="${2:-}"
    LOG_LEVEL="${3:-$DEFAULT_LOG_LEVEL}"
    MAX_DEPTH="${4:-$DEFAULT_MAX_DEPTH}"
    
    # Validation
    if [[ -z "$FUNCTION_NAME" ]]; then
        echo "Error: Function name is required for function mode!"
        echo ""
        show_usage
        exit 1
    fi
    
    if [[ -z "$PROGRAM_NAME" ]]; then
        echo "Error: Program name is required for function mode!"
        echo ""
        show_usage
        exit 1
    fi
    
    validate_log_level "$LOG_LEVEL" || exit 1
    validate_depth "$MAX_DEPTH" "MAX_DEPTH" || exit 1
    
    # Check script file
    SCRIPT_PATH="$SCRIPTS_BASE_DIR/$FUNCTION_ANALYZER_SCRIPT"
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        echo "Error: Function analyzer script not found at: $SCRIPT_PATH"
        echo "Please update FUNCTION_ANALYZER_SCRIPT in $ENV_FILE"
        exit 1
    fi
    
    # Set environment variables for the script
    export FUNCTION_NAME="$FUNCTION_NAME"
    export LOG_LEVEL="$LOG_LEVEL"
    export MAX_DEPTH="$MAX_DEPTH"
    
    if [[ "$QUIET_MODE" != "true" ]]; then
        echo "=== Ghidra Function Decompilation Analyzer - Headless Mode ==="
        echo "Function to analyze: $FUNCTION_NAME"
        echo "Program to analyze: $PROGRAM_NAME"
        echo "Log level: $LOG_LEVEL"
        echo "Max recursion depth: $MAX_DEPTH"
        echo "Project: $PROJECT_DIR/$PROJECT_NAME"
        echo "Script: $SCRIPT_PATH"
        [[ "$QUIET_MODE" == "true" ]] && echo "Quiet mode: enabled"
        echo "=============================================================="
        echo ""
    fi
    
    # Run PyGhidra for function analysis
    execute_pyghidra "$PYGHIDRA_RUN" --headless "$PROJECT_DIR" "$PROJECT_NAME" \
        -scriptPath "$SCRIPTS_BASE_DIR" \
        -postScript "$FUNCTION_ANALYZER_SCRIPT" \
        -process "$PROGRAM_NAME" \
        -noanalysis
fi

GHIDRA_EXIT_CODE=$?

# Check exit status
if [[ $GHIDRA_EXIT_CODE -eq 0 ]]; then
    echo ""
    if [[ "$MODE" == "dwarf" ]]; then
        echo "DWARF symbol exploration completed successfully!"
    else
        echo "Function analysis completed successfully!"
    fi
else
    echo ""
    if [[ "$MODE" == "dwarf" ]]; then
        echo "DWARF symbol exploration failed with exit code $GHIDRA_EXIT_CODE"
    else
        echo "Function analysis failed with exit code $GHIDRA_EXIT_CODE"
    fi
    exit 1
fi