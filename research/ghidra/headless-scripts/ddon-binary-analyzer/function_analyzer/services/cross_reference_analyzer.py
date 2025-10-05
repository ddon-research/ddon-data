# Cross Reference Analyzer - Analyzer for finding related functions and cross-references
# Provides analysis of function relationships and struct dependencies

import logging
from typing import Optional, Dict, List

from ghidra.program.model.listing import Program, Function

from shared.namespace_utils import NamespaceUtils


class CrossReferenceAnalyzer:
    """Analyzer for finding cross-referenced functions with struct relationships"""

    def __init__(self, program: Program, logger: logging.Logger):
        self.program = program
        self.logger = logger
        self.function_manager = program.getFunctionManager()

    def analyze_related_functions(self, target_function: Function, namespace_filter: Optional[str] = None) -> Dict[
        str, List[Function]]:
        """Analyze functions related to the target function"""
        self.logger.debug(f"Analyzing related functions for: {target_function.getName()}")

        related_functions = {
            'direct_calls': [],
            'struct_related_calls': [],
            'callers': [],
            'struct_related': [],
            'namespace_related': []
        }

        # Find direct function calls
        direct_calls = self._find_direct_calls(target_function)
        self.logger.debug(f"Found {len(direct_calls)} direct calls")

        # Separate struct-related calls from regular direct calls
        if namespace_filter:
            for func in direct_calls:
                if self._is_function_struct_related(func, namespace_filter):
                    related_functions['struct_related_calls'].append(func)
                else:
                    related_functions['direct_calls'].append(func)
        else:
            related_functions['direct_calls'] = direct_calls

        # Find callers
        related_functions['callers'] = self._find_callers(target_function)

        return related_functions

    def filter_relevant_functions(self, function_calls: List[str], namespace_filter: Optional[str] = None) -> List[str]:
        """Filter function calls to only include relevant ones"""
        if not namespace_filter:
            return function_calls

        relevant_calls = []
        for call in function_calls:
            if NamespaceUtils.is_namespace_related(call, namespace_filter):
                relevant_calls.append(call)

        return relevant_calls

    def _is_function_struct_related(self, function: Function, namespace: str) -> bool:
        """Check if a function is related to the specified struct namespace"""
        if function is None or not namespace:
            return False

        func_name = function.getName()
        signature = function.getPrototypeString(False, False)

        # Use centralized namespace checking
        if NamespaceUtils.is_namespace_related(func_name, namespace):
            return True

        if signature and NamespaceUtils.is_namespace_related(signature, namespace):
            return True

        return False

    def _find_direct_calls(self, function: Function) -> List[Function]:
        """Find functions directly called by the target function using Ghidra's built-in method.

        This method leverages Function.getCalledFunctions() which is more efficient and robust
        than manual reference iteration. It handles thunks, external calls, and edge cases
        automatically.
        """
        from ghidra.util.task import TaskMonitor

        # Use Ghidra's built-in method - handles all edge cases internally
        called_functions_set = function.getCalledFunctions(TaskMonitor.DUMMY)

        # Convert Set to List for consistency with existing code
        return list(called_functions_set) if called_functions_set else []

    def _find_callers(self, function: Function) -> List[Function]:
        """Find functions that call the target function using Ghidra's built-in method.

        This method leverages Function.getCallingFunctions() which is more efficient and robust
        than manual reference iteration. It automatically handles duplicate filtering and
        edge cases.
        """
        from ghidra.util.task import TaskMonitor

        # Use Ghidra's built-in method - handles all edge cases internally
        calling_functions_set = function.getCallingFunctions(TaskMonitor.DUMMY)

        # Convert Set to List for consistency with existing code
        return list(calling_functions_set) if calling_functions_set else []
