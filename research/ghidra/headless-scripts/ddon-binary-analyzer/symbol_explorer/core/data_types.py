"""Data Type Information Classes

Provides structured wrappers around Ghidra DataType objects for DWARF symbol
analysis. These classes extract and cache commonly-needed properties to provide
a consistent interface across the symbol explorer.
"""

from dataclasses import dataclass
from typing import Optional

from ghidra.program.model.data import DataType

from ..utils.type_utils import TypeUtils


@dataclass
class DataTypeInfo:
    """Lightweight wrapper for Ghidra DataType objects.

    This class provides property-based access to DataType attributes,
    computing values on-demand rather than caching. This approach minimizes
    memory overhead while maintaining a clean API.

    The class specifically handles DWARF debug symbol types and provides
    helpers for extracting qualified C++ names from DWARF category paths.

    Attributes:
        data_type: Underlying Ghidra DataType object (may be None)

    Example:
        >>> dt_info = DataTypeInfo.from_data_type(ghidra_datatype)
        >>> print(dt_info.name)  # "rLandInfo"
        >>> print(dt_info.qualified_name)  # "rLandInfo::cLandInfo"
        >>> print(dt_info.is_dwarf)  # True
    """

    data_type: Optional[DataType]

    @classmethod
    def from_data_type(cls, data_type: Optional[DataType]) -> 'DataTypeInfo':
        """Factory method to create DataTypeInfo from Ghidra DataType.

        Args:
            data_type: Ghidra DataType object to wrap (may be None)

        Returns:
            New DataTypeInfo instance

        Example:
            >>> info = DataTypeInfo.from_data_type(datatype)
        """
        return cls(data_type=data_type)

    @property
    def name(self) -> str:
        """Get simple type name without namespace qualification.

        Returns:
            Type name string, or "<invalid>" if data_type is None

        Example:
            >>> info.name  # "rLandInfo"
        """
        return self.data_type.getName() if self.data_type else "<invalid>"

    @property
    def path(self) -> str:
        """Get full Ghidra path name including category.

        Returns:
            Full path string (e.g., "/DWARF/rLandInfo.h/rLandInfo"),
            or "<invalid>" if data_type is None

        Example:
            >>> info.path  # "/DWARF/rLandInfo.h/rLandInfo"
        """
        return self.data_type.getPathName() if self.data_type else "<invalid>"

    @property
    def size(self) -> int:
        """Get type size in bytes.

        Returns:
            Size in bytes, or 0 if data_type is None or size undefined

        Example:
            >>> info.size  # 144 (bytes)
        """
        return self.data_type.getLength() if self.data_type else 0

    @property
    def type_class(self) -> str:
        """Get Python class name of underlying Ghidra type.

        Useful for determining the concrete type (StructureDataType,
        UnionDataType, TypedefDataType, etc.) at runtime.

        Returns:
            Class name string (e.g., "StructureDataType"),
            or "<invalid>" if data_type is None

        Example:
            >>> info.type_class  # "StructureDataType"
        """
        return self.data_type.__class__.__name__ if self.data_type else "<invalid>"

    @property
    def is_composite(self) -> bool:
        """Check if type is a composite (struct, union, class).

        Returns:
            True for Structure/Union types, False otherwise

        Example:
            >>> info.is_composite  # True for structures
        """
        return (
            TypeUtils.is_composite_type(self.data_type)
            if self.data_type else False
        )

    @property
    def is_dwarf(self) -> bool:
        """Check if type originates from DWARF debug information.

        Examines the category path to determine if this type was imported
        from DWARF debug symbols (resides in /DWARF/ category).

        Returns:
            True if type is from DWARF debug info, False otherwise

        Example:
            >>> info.is_dwarf  # True for types in /DWARF/ category
        """
        if not self.data_type:
            return False

        category_path = self.data_type.getCategoryPath()
        if not category_path:
            return False

        path_str = category_path.getPath()
        return "/DWARF/" in path_str or path_str.startswith("/DWARF")

    @property
    def qualified_name(self) -> str:
        """Get C++-style qualified name extracted from DWARF category path.

        For DWARF types, constructs a qualified name by parsing the category
        path structure. For example:
        - Category: /DWARF/rLandInfo.h/rLandInfo/cLandInfo
        - Result: rLandInfo::cLandInfo

        For non-DWARF types, returns the simple name.

        Returns:
            Qualified name string with :: separators

        Example:
            >>> info.qualified_name  # "rLandInfo::cLandInfo"
        """
        if not self.data_type or not self.is_dwarf:
            return self.name

        category_path = self.data_type.getCategoryPath()
        if not category_path:
            return self.name

        path_str = category_path.getPath()
        if "/DWARF/" not in path_str:
            return self.name

        # Parse DWARF category path to extract namespace components
        parts = path_str.split('/')
        namespace_parts = []

        # Find DWARF category and collect meaningful namespace components
        dwarf_found = False
        for part in parts:
            if part == "DWARF":
                dwarf_found = True
                continue

            # Skip empty parts and header file names
            if dwarf_found and part and not part.endswith('.h'):
                namespace_parts.append(part)

        # Handle case where last component is the type name
        if len(namespace_parts) > 1:
            # Avoid duplicating type name in qualified name
            if namespace_parts[-1] == self.name:
                namespace_parts = namespace_parts[:-1]

            if namespace_parts:
                return f"{'::'.join(namespace_parts)}::{self.name}"

        return self.name

    def is_valid(self) -> bool:
        """Check if this DataTypeInfo wraps a valid DataType.

        Returns:
            True if data_type is not None, False otherwise
        """
        return self.data_type is not None

    def __str__(self) -> str:
        """String representation showing qualified name and size."""
        if self.is_valid():
            return f"{self.qualified_name} ({self.size} bytes)"
        return "<invalid>"

    def __repr__(self) -> str:
        """Developer representation with key fields."""
        return (
            f"DataTypeInfo("
            f"name='{self.name}', "
            f"size={self.size}, "
            f"is_dwarf={self.is_dwarf}, "
            f"type_class='{self.type_class}', "
            f"valid={self.is_valid()})"
        )
