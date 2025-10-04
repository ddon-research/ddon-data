# Symbol search service for DWARF exploration
#
# This module provides symbol search capabilities for finding and resolving
# DWARF symbols in Ghidra data type managers.


import logging
from typing import Optional, List

from ghidra.program.model.data import DataType, DataTypeManager, CategoryPath


class SymbolSearchService:
    """Service for searching symbols in the data type manager using efficient Ghidra API patterns"""

    def __init__(self, data_type_manager: DataTypeManager, logger: logging.Logger):
        self.dtm = data_type_manager
        self.logger = logger
        self._type_cache = {}
        self._cache_initialized = False

    def find_symbol_by_name(self, symbol_name: str, exact_only: bool = False) -> Optional[DataType]:
        """
        Search for a symbol by name using DWARF-aware DataTypeManager operations.
        
        Args:
            symbol_name: The name of the symbol to search for
            exact_only: If True, only return exact matches (no partial matches)
        
        Returns:
            The first matching DataType found, or None if no match
        """
        search_type = "exact symbol" if exact_only else "symbol"
        self.logger.debug(f"Searching for {search_type}: '{symbol_name}'")

        # Step 1: Try direct category path lookup (most efficient for DWARF types)
        result = self.find_by_category_path(symbol_name)
        if result:
            self._log_search_result(result, symbol_name, exact_only)
            return result

        # Step 2: Initialize cache if needed and try cache lookup
        if not self._cache_initialized:
            self._populate_type_cache()

        result = self._find_in_cache(symbol_name, exact_only)
        if result:
            self._log_search_result(result, symbol_name, exact_only)
            return result

        # Step 3: Check for conflict types (based on DWARF test patterns)
        conflict_types = self.find_conflicted_types(symbol_name)
        if conflict_types:
            result = conflict_types[0]  # Return first conflict type
            self.logger.debug(f"Found conflict type for '{symbol_name}': {result.getName()}")
            self._log_search_result(result, symbol_name, exact_only)
            return result

        self._log_search_result(None, symbol_name, exact_only)
        return None

    def find_nested_symbol(self, symbol_name: str) -> Optional[DataType]:
        """Find a symbol that might be nested in namespaces using path variations"""
        self.logger.debug(f"Searching for nested symbol: '{symbol_name}'")

        if not self._cache_initialized:
            self._populate_type_cache()

        # Generate path variations and try each one
        variations = self._generate_symbol_variations(symbol_name)

        for variation in variations:
            if variation in self._type_cache:
                result = self._type_cache[variation]
                if result and not result.isDeleted():
                    self.logger.debug(f"Found nested symbol '{symbol_name}' as '{variation}'")
                    return result

        self.logger.debug(f"No nested symbol found for '{symbol_name}'")
        return None

    def _populate_type_cache(self):
        """Efficiently populate cache using DataTypeManager iterator"""
        try:
            data_types = self.dtm.getAllDataTypes()
            cache_size = 0

            while data_types.hasNext():
                dt = data_types.next()
                if dt and not dt.isDeleted():
                    # Cache by full path
                    path = dt.getPathName()
                    self._type_cache[path] = dt
                    # Cache by simple name
                    self._type_cache[dt.getName()] = dt
                    cache_size += 1

            self._cache_initialized = True
            self.logger.debug(f"Cached {cache_size} types from DataTypeManager")

        except Exception as e:
            self.logger.warning(f"Error populating type cache: {e}")

    def _find_in_cache(self, symbol_name: str, exact_only: bool) -> Optional[DataType]:
        """Find symbol in cache with DWARF-aware match prioritization"""
        # Collect all exact matches first, then prioritize by type and location
        exact_matches = []
        partial_matches = []

        symbol_lower = symbol_name.lower()
        for cached_name, dt in self._type_cache.items():
            if dt and not dt.isDeleted():
                if cached_name == symbol_name:
                    exact_matches.append(dt)
                elif not exact_only and symbol_lower in cached_name.lower():
                    partial_matches.append(dt)

        # Prioritize matches: Structure/Union in DWARF > Other types in DWARF > Structure/Union elsewhere > Others
        def get_priority(dt):
            class_name = dt.__class__.__name__
            path_name = dt.getPathName()
            is_dwarf = "/DWARF/" in path_name
            is_composite = 'Structure' in class_name or 'Union' in class_name or 'Enum' in class_name
            is_function = 'FunctionDefinition' in class_name

            if is_composite and is_dwarf:
                return 1  # Highest priority
            elif is_composite:
                return 2  # Second priority
            elif is_dwarf and not is_function:
                return 3  # Third priority
            elif is_function:
                return 5  # Lowest priority
            else:
                return 4  # Fourth priority

        # Sort and return best match
        all_matches = exact_matches + (partial_matches if not exact_only else [])
        if all_matches:
            best_match = min(all_matches, key=get_priority)
            return best_match

        return None

    def _generate_symbol_variations(self, symbol_name: str) -> List[str]:
        """Generate DWARF-aware symbol name and path variations using official Ghidra patterns"""
        variations = [symbol_name]

        # Handle C++ namespace syntax (following DWARFNameInfoTest patterns)
        if '::' in symbol_name:
            class_name = symbol_name.split('::')[-1]
            namespace_path = symbol_name.replace('::', '/')

            variations.extend([
                class_name,
                namespace_path,
                f"/{namespace_path}",
                f"/DWARF/{namespace_path}",
                f"/DWARF/_UNCATEGORIZED_/{class_name}",
                f"/DWARF/_UNCATEGORIZED_/{namespace_path}"
            ])
        else:
            # Standard DWARF paths from test patterns
            variations.extend([
                f"/{symbol_name}",
                f"/DWARF/{symbol_name}",
                f"/DWARF/_UNCATEGORIZED_/{symbol_name}",
                # Handle anon struct patterns from tests
                f"/DWARF/{symbol_name}.h/{symbol_name}"
            ])

        return variations

    def find_by_category_path(self, symbol_name: str) -> Optional[DataType]:
        """Find DataType using DWARF category path patterns from official Ghidra tests"""
        # Try DWARF-specific category paths based on DWARFDataTypeImporterTest
        dwarf_paths = [
            CategoryPath("/DWARF/_UNCATEGORIZED_"),
            CategoryPath("/DWARF"),
            CategoryPath.ROOT
        ]

        # Prioritize composite types (Structure, Union) over function definitions
        best_match = None
        function_match = None

        for cat_path in dwarf_paths:
            try:
                dt = self.dtm.getDataType(cat_path, symbol_name)
                if dt and not dt.isDeleted():
                    self.logger.debug(f"Found '{symbol_name}' in category: {cat_path}")

                    # Prioritize Structure/Union types over function definitions
                    class_name = dt.__class__.__name__
                    if 'Structure' in class_name or 'Union' in class_name or 'Enum' in class_name:
                        return dt  # Return immediately for composite types
                    elif 'FunctionDefinition' in class_name:
                        if function_match is None:
                            function_match = dt
                    else:
                        if best_match is None:
                            best_match = dt
            except Exception as e:
                self.logger.debug(f"Category search failed for {cat_path}/{symbol_name}: {e}")

        # Return best available match (composite > other > function)
        return best_match or function_match

    def find_conflicted_types(self, symbol_name: str) -> List[DataType]:
        """Find types with conflict suffix using official Ghidra patterns"""
        conflict_variations = [
            f"{symbol_name}.conflict",
            f"{symbol_name}.conflict1",
            f"{symbol_name}.conflict2"
        ]

        results = []
        for variation in conflict_variations:
            if variation in self._type_cache:
                dt = self._type_cache[variation]
                if dt and not dt.isDeleted():
                    results.append(dt)

        return results

    def _log_search_result(self, result: Optional[DataType], symbol_name: str, exact_only: bool):
        """Log search results consistently with DWARF context"""
        if result:
            path = result.getPathName()
            is_dwarf = "/DWARF/" in path
            dwarf_marker = " [DWARF]" if is_dwarf else ""
            self.logger.debug(f"Found symbol '{symbol_name}': {result.getName()} at {path}{dwarf_marker}")
        else:
            match_type = "exact matches" if exact_only else "matches"
            self.logger.debug(f"No {match_type} found for '{symbol_name}'")
