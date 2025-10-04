# DWARF Symbol Explorer - Headless Mode Entry Point
# Streamlined headless execution wrapper for the modular DWARF symbol explorer
#
# Environment Variables (set these before running):
# - SYMBOL_NAME: The DWARF symbol to analyze (e.g., "rLandInfo")
# - LOG_LEVEL: "DEBUG" or "INFO" (default: "INFO")
# - EXPLORE_DEPTH: Maximum exploration depth 1-10 (default: 5)
#
# @author Sehkah
# @category ddon-research
# @keybinding 
# @menupath 
# @toolbar 
# @runtime PyGhidra

import os
import sys

from symbol_explorer.analysis import DwarfSymbolExplorer


def main_headless():
    """Main function for headless execution"""

    # Get configuration from environment variables (direct access - no wrapper needed)
    symbol_name = os.environ.get('SYMBOL_NAME', '').strip()
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()

    try:
        explore_depth = max(1, min(10, int(os.environ.get('EXPLORE_DEPTH', '5'))))
    except (ValueError, TypeError):
        explore_depth = 5

    # Validate environment variables
    if not symbol_name:
        print("ERROR: SYMBOL_NAME environment variable must be set")
        print("Example: export SYMBOL_NAME='rLandInfo'")
        sys.exit(1)

    if log_level not in ['DEBUG', 'INFO']:
        print("ERROR: LOG_LEVEL must be 'DEBUG' or 'INFO'")
        sys.exit(1)

    # Available by global Ghidra script context
    try:
        program = globals().get('currentProgram', currentProgram)  # type: ignore

        if program is None:
            print("ERROR: No program is currently loaded")
            sys.exit(1)
    except NameError:
        print("ERROR: Not running in Ghidra script environment")
        sys.exit(1)

    # Create and run the analyzer
    explorer = DwarfSymbolExplorer(program, log_level)
    success = explorer.analyze_symbol(symbol_name, explore_depth)

    if not success:
        print(f"ERROR: Failed to analyze symbol '{symbol_name}'")
        sys.exit(1)


# Execute the main function
if __name__ == "__main__":
    main_headless()
