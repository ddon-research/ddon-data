# Decompilation Service - Service for extracting and processing decompiled code
# Provides decompilation capabilities with error handling and output management

import logging
from typing import Optional, List, Dict

from ghidra.app.decompiler import DecompInterface, DecompileResults
from ghidra.program.model.listing import Program, Function
from ghidra.util.task import ConsoleTaskMonitor

from ..config import AnalyzerConfig, DecompilationException
from ..utils import NamespaceUtils


class DecompilationService:
    """Service for extracting and processing decompiled code"""

    def __init__(self, program: Program, logger: logging.Logger):
        self.program = program
        self.logger = logger
        self.decompiler = None
        self._initialize_decompiler()

    def _initialize_decompiler(self):
        """Initialize the decompiler interface"""
        try:
            self.decompiler = DecompInterface()

            # Use simple initialization that was working
            # The default options should enable both C code and syntax tree
            success = self.decompiler.openProgram(self.program)
            if not success:
                raise DecompilationException("Failed to open program in decompiler")

            self.logger.debug("Decompiler initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize decompiler: {e}")
            self.decompiler = None

    def get_decompiled_function(self, function: Function) -> Optional[str]:
        """Get decompiled code for a function using enhanced DecompInterface API"""
        if self.decompiler is None:
            self.logger.error("Decompiler not available")
            return None

        try:
            self.logger.debug(f"Decompiling function: {function.getName()}")

            # Set up task monitor
            task_monitor = ConsoleTaskMonitor()

            # Perform decompilation with configured timeout
            decompile_results = self.decompiler.decompileFunction(
                function,
                AnalyzerConfig.DECOMPILATION_TIMEOUT,
                task_monitor
            )

            return self._process_decompile_results(decompile_results, function)

        except Exception as e:
            self.logger.error(f"Error decompiling function {function.getName()}: {e}")
            return None

    def _process_decompile_results(self, decompile_results: DecompileResults, function: Function) -> Optional[str]:
        """Process decompilation results with comprehensive error checking"""
        if decompile_results is None:
            self.logger.error(f"Decompilation returned null for {function.getName()}")
            return None

        # Add diagnostic information
        self.logger.debug(f"Decompile completed: {decompile_results.decompileCompleted()} for {function.getName()}")

        # Check for various failure modes
        if decompile_results.isCancelled():
            self.logger.warning(f"Decompilation was cancelled for {function.getName()}")
            return None

        if decompile_results.isTimedOut():
            self.logger.warning(f"Decompilation timed out for {function.getName()}")
            return None

        if decompile_results.failedToStart():
            self.logger.error(f"Decompiler failed to start for {function.getName()}")
            return None

        if not decompile_results.decompileCompleted():
            error_msg = decompile_results.getErrorMessage() or "Unknown decompilation error"
            self.logger.error(f"Decompilation failed for {function.getName()}: {error_msg}")
            return None

        # Add more diagnostics
        has_high_func = decompile_results.getHighFunction() is not None
        has_markup = decompile_results.getCCodeMarkup() is not None
        has_decomp_func = decompile_results.getDecompiledFunction() is not None
        self.logger.debug(
            f"Results for {function.getName()}: HighFunc={has_high_func}, Markup={has_markup}, DecompFunc={has_decomp_func}")

        # Use the original working approach first
        high_function = decompile_results.getHighFunction()
        if high_function is None:
            self.logger.error(f"No high function available for {function.getName()}")
            return None

        # Get C code using the method that was working
        decompiled_func = decompile_results.getDecompiledFunction()
        if decompiled_func is None:
            self.logger.error(f"No decompiled function available for {function.getName()}")
            return None

        decompiled_code = decompiled_func.getC()
        if decompiled_code is None or decompiled_code.strip() == "":
            self.logger.warning(f"Empty decompiled code for {function.getName()}")
            return None

        self.logger.debug(f"Successfully decompiled {function.getName()}")
        return decompiled_code

    def get_function_calls_from_decompiled_code(self, decompiled_code: str) -> List[str]:
        """Extract function calls from decompiled code using centralized utilities"""
        function_calls = NamespaceUtils.extract_function_calls(decompiled_code)
        self.logger.debug(f"Found {len(function_calls)} function calls in decompiled code")
        return function_calls

    def get_decompiled_functions(self, functions: List[Function]) -> Dict[str, Optional[str]]:
        """Get decompiled code for multiple functions"""
        decompiled_functions = {}
        processed_signatures = set()  # Track processed function signatures to avoid duplicates

        for func in functions:
            func_name = func.getName()
            func_signature = func.getPrototypeString(False, False)

            # Skip if we've already processed this exact function signature
            if func_signature in processed_signatures:
                self.logger.debug(f"Skipping duplicate function signature: {func_name}")
                continue

            processed_signatures.add(func_signature)
            self.logger.debug(f"Decompiling struct-related function: {func_name}")
            decompiled_code = self.get_decompiled_function(func)
            decompiled_functions[func_name] = decompiled_code

        return decompiled_functions

    def cleanup(self):
        """Cleanup decompiler resources properly"""
        if self.decompiler:
            try:
                # Proper shutdown sequence
                self.decompiler.flushCache()  # Clear any cached data
                self.decompiler.closeProgram()  # Close the program
                self.decompiler.dispose()  # Dispose of resources
                self.logger.debug("Decompiler resources cleaned up successfully")
            except Exception as e:
                self.logger.debug(f"Error cleaning up decompiler: {e}")
            finally:
                self.decompiler = None
