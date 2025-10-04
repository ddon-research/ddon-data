# Cross Reference Analyzer - Analyzer for finding related functions and cross-references
# Provides analysis of function relationships and struct dependencies

import logging
from typing import Optional, Dict, List

from ghidra.program.model.listing import Program, Function

from ..utils import NamespaceUtils


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
        """Find functions directly called by the target function using optimized ReferenceManager API"""
        called_functions = []
        seen_functions = set()  # Use set for O(1) lookup

        ref_manager = self.program.getReferenceManager()
        function_body = function.getBody()

        # Use ReferenceIterator for more efficient traversal
        # Get references starting from function entry point
        ref_iterator = ref_manager.getReferenceIterator(function.getEntryPoint())

        while ref_iterator.hasNext():
            ref = ref_iterator.next()
            from_addr = ref.getFromAddress()

            # Only process references from within this function's body
            if not function_body.contains(from_addr):
                # If we've moved past this function's address range, break
                if from_addr.compareTo(function_body.getMaxAddress()) > 0:
                    break
                continue

            ref_type = ref.getReferenceType()
            if ref_type.isCall():  # More general than checking specific call types
                called_func = self.function_manager.getFunctionAt(ref.getToAddress())
                if called_func and called_func.getEntryPoint() not in seen_functions:
                    called_functions.append(called_func)
                    seen_functions.add(called_func.getEntryPoint())

        return called_functions

    def _find_callers(self, function: Function) -> List[Function]:
        """Find functions that call the target function using optimized ReferenceManager API"""
        callers = []
        seen_callers = set()  # Use set for O(1) duplicate detection

        ref_manager = self.program.getReferenceManager()

        # Use ReferenceIterator for more efficient traversal
        ref_iterator = ref_manager.getReferencesTo(function.getEntryPoint())

        while ref_iterator.hasNext():
            ref = ref_iterator.next()
            caller_func = self.function_manager.getFunctionContaining(ref.getFromAddress())
            if caller_func and caller_func.getEntryPoint() not in seen_callers:
                callers.append(caller_func)
                seen_callers.add(caller_func.getEntryPoint())

        return callers
