# Function Search Service - Service for finding and discovering functions in Ghidra
# Provides comprehensive function search capabilities with namespace support

import logging
import re
from typing import Optional, List

from ghidra.app.util import NamespaceUtils as GhidraNamespaceUtils
from ghidra.program.model.address import Address
from ghidra.program.model.listing import Program, Function
from ghidra.program.model.symbol import SymbolType

from ..config import AnalyzerConfig


class FunctionSearchService:
    """Service for searching and discovering functions"""

    def __init__(self, program: Program, logger: logging.Logger):
        self.program = program
        self.logger = logger
        self.function_manager = program.getFunctionManager()
        self.symbol_table = program.getSymbolTable()

    def find_function_by_name(self, function_name: str) -> Optional[Function]:
        """
        Find function by name, supporting namespace syntax
        
        Args:
            function_name: Function name like "rLandInfo::load" or "load"
            
        Returns:
            Function object if found, None otherwise
        """
        self.logger.debug(f"Searching for function: '{function_name}'")

        # Try symbol table search first (more efficient for DWARF symbols)
        symbol_matches = self.find_functions_by_symbol_table(function_name)
        if symbol_matches:
            self.logger.debug(f"Found {len(symbol_matches)} symbol table matches")
            return self._select_best_function_match(symbol_matches)

        # Try exact match
        exact_matches = self._find_exact_matches(function_name)
        if exact_matches:
            self.logger.debug(f"Found {len(exact_matches)} exact matches")
            return self._select_best_function_match(exact_matches)

        # Try partial matches if no exact match
        partial_matches = self._find_partial_matches(function_name)
        if partial_matches:
            self.logger.debug(f"Found {len(partial_matches)} partial matches")
            return self._select_best_function_match(partial_matches)

        self.logger.debug(f"No matches found for '{function_name}'")
        return None

    def get_function_at_address(self, address: Address) -> Optional[Function]:
        """Get function at specific address"""
        return self.function_manager.getFunctionAt(address)

    def get_function_containing_address(self, address: Address) -> Optional[Function]:
        """Get function containing the given address"""
        return self.function_manager.getFunctionContaining(address)

    def get_qualified_function_name(self, function: Function) -> str:
        """Get fully qualified function name from signature or symbols"""
        if function is None:
            return "None"

        # Get function signature which often contains namespace information
        signature = function.getPrototypeString(False, False)
        self.logger.debug(f"Function signature: {signature}")

        # Extract namespace from signature patterns
        namespace_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)::[a-zA-Z_][a-zA-Z0-9_]*\s*\('
        match = re.search(namespace_pattern, signature)
        if match:
            namespace_part = match.group(1)
            simple_name = function.getName()
            qualified_name = f"{namespace_part}::{simple_name}"
            self.logger.debug(f"Extracted qualified name: {qualified_name}")
            return qualified_name

        # Pattern 2: Look for calling convention patterns like "__thiscall Class::method"
        thiscall_pattern = r'__thiscall\s+([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)::[a-zA-Z_][a-zA-Z0-9_]*\s*\('
        match = re.search(thiscall_pattern, signature)
        if match:
            namespace_part = match.group(1)
            simple_name = function.getName()
            qualified_name = f"{namespace_part}::{simple_name}"
            self.logger.debug(f"Extracted qualified name from thiscall: {qualified_name}")
            return qualified_name

        # Pattern 3: Look at parameter types for namespace hints
        param_pattern = r'\(\s*([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)[\s\*]*\s*this'
        match = re.search(param_pattern, signature)
        if match:
            namespace_part = match.group(1)
            simple_name = function.getName()
            # Only use if it looks like a reasonable namespace
            if len(namespace_part) > 2 and not namespace_part.startswith('u') and namespace_part != 'void':
                qualified_name = f"{namespace_part}::{simple_name}"
                self.logger.debug(f"Extracted qualified name from parameter: {qualified_name}")
                return qualified_name

        # Fallback: check if any symbols at this address have namespace information
        address = function.getEntryPoint()
        if address:
            symbols = self.symbol_table.getSymbols(address)
            for symbol in symbols:
                symbol_name = symbol.getName()
                if "::" in symbol_name and symbol_name.endswith(function.getName()):
                    self.logger.debug(f"Found qualified symbol name: {symbol_name}")
                    return symbol_name

        # Return simple name if no namespace found
        simple_name = function.getName()
        self.logger.debug(f"Using simple name: {simple_name}")
        return simple_name

    def find_functions_by_symbol_table(self, function_name: str) -> List[Function]:
        """Search for functions using symbol table - more efficient for DWARF symbols"""
        matches = []

        # Search symbols directly - this is more efficient than iterating all functions
        symbol_iterator = self.symbol_table.getSymbolIterator(function_name, True)

        for symbol in symbol_iterator:
            if symbol.getSymbolType() == SymbolType.FUNCTION:
                func = self.function_manager.getFunction(symbol.getID())
                if func:
                    matches.append(func)

        # Also search for qualified names
        if "::" in function_name:
            # Try searching for just the function part
            simple_name = function_name.split("::")[-1]
            simple_iterator = self.symbol_table.getSymbolIterator(simple_name, True)

            for symbol in simple_iterator:
                if symbol.getSymbolType() == SymbolType.FUNCTION:
                    func = self.function_manager.getFunction(symbol.getID())
                    if func and self._function_matches_qualified_name(func, function_name):
                        if func not in matches:
                            matches.append(func)

        return matches

    def _function_matches_qualified_name(self, function: Function, qualified_name: str) -> bool:
        """Check if function matches the qualified name pattern"""
        func_qualified = GhidraNamespaceUtils.getNamespaceQualifiedName(function, "::", False)
        return func_qualified == qualified_name or func_qualified.endswith(qualified_name)

    def _find_exact_matches(self, function_name: str) -> List[Function]:
        """Find functions with exact name match"""
        matches = []

        # Search through all functions
        all_functions = self.function_manager.getFunctions(True)  # Forward direction
        for function in all_functions:
            if function.getName() == function_name:
                matches.append(function)

            # Also check for namespace variations
            if "::" in function_name:
                # Try without namespace
                simple_name = function_name.split("::")[-1]
                if function.getName() == simple_name:
                    # Check if this function is in the right namespace
                    if self._is_function_in_namespace(function, function_name):
                        matches.append(function)

        return matches

    def _find_partial_matches(self, function_name: str) -> List[Function]:
        """Find functions with partial name match"""
        matches = []
        search_terms = function_name.lower().replace("::", "_").split("_")

        all_functions = self.function_manager.getFunctions(True)
        for function in all_functions:
            func_name_lower = function.getName().lower()

            # Check if all search terms are in the function name
            if all(term in func_name_lower for term in search_terms):
                matches.append(function)

        return matches

    def _is_function_in_namespace(self, function: Function, full_name: str) -> bool:
        """Check if function belongs to the specified namespace"""
        # This is a simplified check - could be enhanced with more sophisticated namespace analysis
        namespace_part = "::".join(full_name.split("::")[:-1])

        # Check function signature or symbol information for namespace indicators
        signature = function.getPrototypeString(False, False)
        return namespace_part in signature

    def _select_best_function_match(self, matches: List[Function]) -> Function:
        """Select the best function match from multiple candidates"""
        if len(matches) == 1:
            return matches[0]

        # Prefer functions with DWARF information or more complete signatures
        scored_matches = []
        for func in matches:
            score = 0
            signature = func.getPrototypeString(False, False)

            # Prefer functions with namespace information
            if "::" in signature:
                score += AnalyzerConfig.SCORE_NAMESPACE_BONUS

            # Prefer functions with parameter information
            if "(" in signature and signature.count(",") > 0:
                score += 5  # Parameters bonus

            # Prefer non-thunk functions
            if not func.isThunk():
                score += 3  # Non-thunk bonus

            scored_matches.append((score, func))

        # Sort by score and return the best match
        scored_matches.sort(key=lambda x: x[0], reverse=True)
        return scored_matches[0][1]
