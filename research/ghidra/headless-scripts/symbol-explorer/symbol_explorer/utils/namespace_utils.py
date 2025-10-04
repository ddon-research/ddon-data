# Namespace utility functions
#
# This module contains u                return \"::\".join(namespace_parts)ility functions for namespace operations
# and path manipulations in DWARF symbol exploration.


from typing import Optional

from ghidra.program.model.data import CategoryPath, DataTypePath, DataType


class NamespaceUtils:
    """Utility functions for namespace operations using Ghidra's CategoryPath API"""

    @staticmethod
    def get_category_path(data_type: Optional[DataType]) -> Optional[CategoryPath]:
        """Get CategoryPath from DataType using Ghidra's built-in functionality"""
        if data_type is None:
            return None
        return data_type.getCategoryPath()

    @staticmethod
    def get_data_type_path(data_type: Optional[DataType]) -> Optional[DataTypePath]:
        """Get DataTypePath using Ghidra's built-in functionality"""
        if data_type is None:
            return None
        return data_type.getDataTypePath()

    @staticmethod
    def is_dwarf_type(data_type: Optional[DataType]) -> bool:
        """Check if type is from DWARF using CategoryPath"""
        if data_type is None:
            return False
        cat_path = data_type.getCategoryPath()
        if cat_path is None:
            return False
        path_str = cat_path.getPath()
        return "/DWARF/" in path_str or path_str.startswith("/DWARF")

    @staticmethod
    def extract_namespace_from_path(type_path: str) -> str:
        """Extract namespace from DWARF type path"""
        if "/DWARF/" in type_path:
            # Handle DWARF paths like "/DWARF/rLandInfo.h/rLandInfo/cLandInfo"
            parts = type_path.split('/')
            dwarf_index = -1
            for i, part in enumerate(parts):
                if part == "DWARF":
                    dwarf_index = i
                    break

            if dwarf_index >= 0 and len(parts) > dwarf_index + 2:
                # Skip DWARF and .h file, collect namespace parts
                namespace_parts = []
                for i in range(dwarf_index + 2, len(parts) - 1):  # Exclude last part (type name)
                    if parts[i]:  # Skip empty parts
                        namespace_parts.append(parts[i])
                return ":::".join(namespace_parts)

        # Fallback to generic path parsing
        if '/' in type_path:
            return '/'.join(type_path.split('/')[:-1])
        return ""

    @staticmethod
    def get_simple_name_from_path(type_path: str) -> str:
        """Get simple type name without namespace using CategoryPath logic"""
        if '/' in type_path:
            return type_path.split('/')[-1]
        return type_path

    @staticmethod
    def create_qualified_name(data_type: Optional[DataType]) -> str:
        """Create C++ qualified name from DWARF path"""
        if data_type is None:
            return "void"

        type_name = data_type.getName()
        namespace = NamespaceUtils.extract_namespace_from_path(data_type.getPathName())

        if namespace:
            return f"{namespace}::{type_name}"
        return type_name
