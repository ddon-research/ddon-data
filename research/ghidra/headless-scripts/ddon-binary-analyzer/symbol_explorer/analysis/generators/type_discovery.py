# Type Discovery Strategies
#
# This module contains abstract base class and concrete implementations
# for type discovery strategies used in C++ definition generation.


import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, List

from ghidra.program.model.data import DataType, DataTypeManager


class TypeDiscoveryStrategy(ABC):
    """Abstract strategy for discovering and resolving DataType objects"""

    @abstractmethod
    def find_type(self, identifier: str, context: Optional[DataType] = None) -> Optional[DataType]:
        """Find a DataType by identifier with optional context"""
        pass


class CachedTypeDiscovery(TypeDiscoveryStrategy):
    """Cached type discovery using DataTypeManager's efficient iterators"""

    def __init__(self, dtm: DataTypeManager, logger: logging.Logger):
        self.dtm = dtm
        self.logger = logger
        self._type_cache: Dict[str, DataType] = {}
        self._initialized = False

    def find_type(self, identifier: str, context: Optional[DataType] = None) -> Optional[DataType]:
        """Find type with caching optimization"""
        if not self._initialized:
            self._populate_cache()

        # Direct cache lookup
        if identifier in self._type_cache:
            return self._type_cache[identifier]

        # Try path variations
        variations = self._generate_path_variations(identifier)
        for variation in variations:
            if variation in self._type_cache:
                # Cache the original identifier for future lookups
                self._type_cache[identifier] = self._type_cache[variation]
                return self._type_cache[variation]

        return None

    def _populate_cache(self):
        """Efficiently populate cache using DataTypeManager iterators"""
        try:
            # Use Ghidra's efficient getAllDataTypes() with proper iteration
            data_types = self.dtm.getAllDataTypes()
            while data_types.hasNext():
                dt = data_types.next()
                if dt and not dt.isDeleted():
                    path = dt.getPathName()
                    self._type_cache[path] = dt
                    # Also cache by simple name for quick lookup
                    self._type_cache[dt.getName()] = dt

            self._initialized = True
            self.logger.debug(f"Cached {len(self._type_cache)} types from DataTypeManager")

        except Exception as e:
            self.logger.warning(f"Error populating type cache: {e}")

    def _generate_path_variations(self, identifier: str) -> List[str]:
        """Generate common path variations for an identifier"""
        return [
            identifier,
            f"/{identifier}",
            f"::/{identifier}",
            identifier.replace("::", "/"),
            identifier.split("::")[-1] if "::" in identifier else identifier
        ]


class SearchServiceTypeDiscovery(TypeDiscoveryStrategy):
    """Fallback type discovery using search service"""

    def __init__(self, search_service, logger: logging.Logger):
        self.search_service = search_service
        self.logger = logger

    def find_type(self, identifier: str, context: Optional[DataType] = None) -> Optional[DataType]:
        """Find type using search service"""
        try:
            return self.search_service.find_nested_symbol(identifier)
        except Exception as e:
            self.logger.debug(f"Search service lookup failed for '{identifier}': {e}")
            return None
