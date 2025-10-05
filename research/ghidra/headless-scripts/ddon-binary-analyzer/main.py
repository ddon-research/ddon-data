# @author Sehkah
# @category ddon-research
# @keybinding
# @menupath
# @toolbar
# @runtime PyGhidra

"""DDON Binary Analyzer - Unified Entry Point

PyGhidra headless script that combines Function Analyzer and Symbol Explorer
for automated analysis of Dragon's Dogma Online PS4 binaries.

Environment Variables:
    ANALYZER_MODE (required): Analysis mode - "function" or "dwarf"
    LOG_LEVEL (optional): Logging verbosity - "DEBUG" or "INFO" (default: "INFO")

Function Mode Variables:
    FUNCTION_NAME (required): Qualified function name (e.g., "rLandInfo::load")
    MAX_DEPTH (optional): Call graph recursion depth 1-10 (default: 3)

DWARF Mode Variables:
    SYMBOL_NAME (required): DWARF symbol name (e.g., "rLandInfo")
    EXPLORE_DEPTH (optional): Type dependency depth 1-10 (default: 5)

Usage:
    export ANALYZER_MODE=function
    export FUNCTION_NAME="rLandInfo::load"
    export MAX_DEPTH=3
    pyghidra main.py
"""

import os
import sys
from typing import NoReturn

from ghidra.program.model.listing import Program

from function_analyzer.analysis import FunctionDecompilationAnalyzer
from function_analyzer.config import AnalyzerConfig, ConfigurationException
from symbol_explorer.analysis import DwarfSymbolExplorer

# Module-level constants
DEFAULT_FUNCTION_DEPTH = 3
DEFAULT_DWARF_DEPTH = 5
MIN_DEPTH = 1


def _exit_with_error(message: str, example: str = "") -> NoReturn:
    """Exit program with formatted error message.

    Args:
        message: Primary error message
        example: Optional example command to display

    Raises:
        SystemExit: Always exits with code 1
    """
    print(f"ERROR: {message}", file=sys.stderr)
    if example:
        print(f"Example: {example}", file=sys.stderr)
    sys.exit(1)


def _validate_depth(depth_str: str, max_depth: int, param_name: str) -> int:
    """Validate and normalize depth parameter.

    Args:
        depth_str: Depth value as string from environment
        max_depth: Maximum allowed depth
        param_name: Parameter name for error messages

    Returns:
        Validated depth value

    Raises:
        SystemExit: If validation fails
    """
    try:
        depth = int(depth_str)
    except (ValueError, TypeError) as e:
        _exit_with_error(
            f"Invalid {param_name}: must be an integer",
            f"export {param_name}=3"
        )

    if not (MIN_DEPTH <= depth <= max_depth):
        _exit_with_error(
            f"{param_name} must be between {MIN_DEPTH} and {max_depth}",
            f"export {param_name}=3"
        )

    return depth


def run_function_analyzer(program: Program, log_level: str) -> None:
    """Execute function decompilation analysis.

    Analyzes a function and its call graph up to specified depth, extracting
    decompiled C code and struct-related dependencies.

    Args:
        program: Ghidra program instance containing the function
        log_level: Logging level ("DEBUG" or "INFO")

    Raises:
        SystemExit: If required environment variables are missing or invalid
    """
    function_name = os.environ.get('FUNCTION_NAME', '').strip()
    if not function_name:
        _exit_with_error(
            "FUNCTION_NAME environment variable must be set for function mode",
            "export FUNCTION_NAME='rLandInfo::load'"
        )

    max_depth_str = os.environ.get('MAX_DEPTH', str(DEFAULT_FUNCTION_DEPTH))
    max_depth = _validate_depth(
        max_depth_str,
        AnalyzerConfig.MAX_RECURSION_DEPTH,
        'MAX_DEPTH'
    )

    analyzer = FunctionDecompilationAnalyzer(program, log_level)
    analyzer.analyze_function(function_name, max_depth)


def run_dwarf_explorer(program: Program, log_level: str) -> None:
    """Execute DWARF symbol extraction and C++ code generation.

    Parses DWARF debug symbols to extract struct definitions with dependency
    resolution and generates C++ header-style output.

    Args:
        program: Ghidra program instance containing DWARF debug info
        log_level: Logging level ("DEBUG" or "INFO")

    Raises:
        SystemExit: If required environment variables are missing, invalid,
                   or symbol analysis fails
    """
    symbol_name = os.environ.get('SYMBOL_NAME', '').strip()
    if not symbol_name:
        _exit_with_error(
            "SYMBOL_NAME environment variable must be set for dwarf mode",
            "export SYMBOL_NAME='rLandInfo'"
        )

    explore_depth_str = os.environ.get('EXPLORE_DEPTH', str(DEFAULT_DWARF_DEPTH))
    explore_depth = _validate_depth(
        explore_depth_str,
        10,  # Maximum depth for DWARF exploration
        'EXPLORE_DEPTH'
    )

    explorer = DwarfSymbolExplorer(program, log_level)
    success = explorer.analyze_symbol(symbol_name, explore_depth)

    if not success:
        _exit_with_error(f"Failed to analyze symbol '{symbol_name}'")


def _get_ghidra_program() -> Program:
    """Retrieve current Ghidra program from execution context.

    Returns:
        Ghidra Program instance

    Raises:
        ConfigurationException: If no program loaded or not in Ghidra environment
    """
    try:
        # Access Ghidra's global currentProgram variable
        program = globals().get('currentProgram', currentProgram)  # type: ignore

        if program is None:
            raise ConfigurationException("No program is currently loaded in Ghidra")

        return program

    except NameError as e:
        raise ConfigurationException(
            "Not running in Ghidra script environment. "
            "This script must be executed via PyGhidra or Ghidra's script manager."
        ) from e


def main_headless() -> None:
    """Main entry point for PyGhidra headless execution.

    Parses environment variables, validates configuration, and dispatches
    to the appropriate analyzer based on ANALYZER_MODE.

    Environment Variables:
        ANALYZER_MODE: "function" or "dwarf" (required)
        LOG_LEVEL: "DEBUG" or "INFO" (optional, default: "INFO")
        Additional mode-specific variables (see module docstring)

    Raises:
        SystemExit: If configuration is invalid or analysis fails
        ConfigurationException: If Ghidra environment is unavailable
    """
    # Parse and validate environment configuration
    mode = os.environ.get('ANALYZER_MODE', '').lower().strip()
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper().strip()

    # Validate analyzer mode
    VALID_MODES = {'function', 'dwarf'}
    if mode not in VALID_MODES:
        _exit_with_error(
            "ANALYZER_MODE must be set to 'function' or 'dwarf'",
            "export ANALYZER_MODE='function'"
        )

    # Validate log level
    VALID_LOG_LEVELS = {'DEBUG', 'INFO'}
    if log_level not in VALID_LOG_LEVELS:
        _exit_with_error(
            "LOG_LEVEL must be 'DEBUG' or 'INFO'",
            "export LOG_LEVEL='INFO'"
        )

    # Retrieve Ghidra program instance
    try:
        program = _get_ghidra_program()
    except ConfigurationException as e:
        _exit_with_error(str(e))

    # Dispatch to appropriate analyzer
    if mode == 'function':
        run_function_analyzer(program, log_level)
    elif mode == 'dwarf':
        run_dwarf_explorer(program, log_level)
    else:
        # Should never reach here due to validation above
        _exit_with_error(f"Unknown analyzer mode: {mode}")


# Script entry point
if __name__ == "__main__":
    main_headless()
