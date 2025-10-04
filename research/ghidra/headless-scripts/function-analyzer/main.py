# Function Decompilation Analyzer - Headless Mode Entry Point
# Streamlined headless execution wrapper for the modular function analyzer
#
# Environment Variables (set these before running):
# - FUNCTION_NAME: The function to analyze (e.g., "rLandInfo::load")
# - LOG_LEVEL: "DEBUG" or "INFO" (default: "INFO")
# - MAX_DEPTH: Maximum recursion depth 1-10 (default: 3)
#
# @author Sehkah
# @category ddon-research
# @keybinding 
# @menupath 
# @toolbar 
# @runtime PyGhidra

import os
import sys

from function_analyzer.analysis import FunctionDecompilationAnalyzer
from function_analyzer.config import AnalyzerConfig, ConfigurationException


def main_headless():
    """Main function for headless execution"""

    # Get configuration from environment variables
    function_name = os.environ.get('FUNCTION_NAME', '')
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    max_depth = int(os.environ.get('MAX_DEPTH', '3'))

    # Validate environment variables
    if not function_name:
        print("ERROR: FUNCTION_NAME environment variable must be set")
        print("Example: export FUNCTION_NAME='rLandInfo::load'")
        sys.exit(1)

    if log_level not in ['DEBUG', 'INFO']:
        print("ERROR: LOG_LEVEL must be 'DEBUG' or 'INFO'")
        sys.exit(1)

    if max_depth < 1 or max_depth > AnalyzerConfig.MAX_RECURSION_DEPTH:
        print(f"ERROR: MAX_DEPTH must be between 1 and {AnalyzerConfig.MAX_RECURSION_DEPTH}")
        sys.exit(1)

    # Available by global Ghidra script context
    try:
        program = globals().get('currentProgram', currentProgram)  # type: ignore

        if program is None:
            raise ConfigurationException("No program is currently loaded")
    except NameError:
        raise ConfigurationException("Not running in Ghidra script environment")

    # Create and run the analyzer
    analyzer = FunctionDecompilationAnalyzer(program, log_level)
    analyzer.analyze_function(function_name, max_depth)


# Execute the main function when run as a script
if __name__ == "__main__":
    main_headless()
