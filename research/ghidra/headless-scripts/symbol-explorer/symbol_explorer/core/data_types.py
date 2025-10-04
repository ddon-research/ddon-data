# Data type information classes
#
# This module contains data classes and value objects for representing
# Ghidra data type information in a structured way.


from dataclasses import dataclass
from typing import Optional

from ghidra.program.model.data import DataType

from ..utils.type_utils import TypeUtils


@dataclass
class DataTypeInfo:
    """Simplified data type information - use utility functions instead of duplicating Ghidra data"""

    data_type: Optional[DataType]

    @classmethod
    def from_data_type(cls, data_type: Optional[DataType]) -> 'DataTypeInfo':
        """Simplified factory - just wrap the DataType, access properties directly when needed"""
        return cls(data_type=data_type)

    @property
    def name(self) -> str:
        return self.data_type.getName() if self.data_type else "None"

    @property
    def path(self) -> str:
        return self.data_type.getPathName() if self.data_type else "None"

    @property
    def size(self) -> int:
        return self.data_type.getLength() if self.data_type else 0

    @property
    def type_class(self) -> str:
        return self.data_type.__class__.__name__ if self.data_type else "None"

    @property
    def is_composite(self) -> bool:
        return TypeUtils.is_composite_type(self.data_type) if self.data_type else False

    @property
    def is_dwarf(self) -> bool:
        if not self.data_type:
            return False
        category_path = self.data_type.getCategoryPath()
        if category_path:
            path_str = category_path.getPath()
            return "/DWARF/" in path_str or path_str.startswith("/DWARF")
        return False

    @property
    def qualified_name(self) -> str:
        """Get qualified C++ name using CategoryPath information"""
        if not self.data_type or not self.is_dwarf:
            return self.name

        category_path = self.data_type.getCategoryPath()
        if not category_path:
            return self.name

        path_str = category_path.getPath()
        if "/DWARF/" in path_str:
            # Extract namespace from DWARF path
            parts = path_str.split('/')
            namespace_parts = []

            # Find DWARF index and collect meaningful parts
            dwarf_found = False
            for part in parts:
                if part == "DWARF":
                    dwarf_found = True
                    continue
                if dwarf_found and part and not part.endswith('.h'):
                    namespace_parts.append(part)

            if len(namespace_parts) > 1:
                # Remove the last part if it matches the type name (avoid duplication)
                if namespace_parts[-1] == self.name:
                    namespace_parts = namespace_parts[:-1]

                if namespace_parts:
                    return f"{'::'.join(namespace_parts)}::{self.name}"

        return self.name
