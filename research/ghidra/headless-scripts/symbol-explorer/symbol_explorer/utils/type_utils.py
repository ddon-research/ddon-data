# Type utility functions
#
# This module contains utility functions for common type operations
# and checks in DWARF symbol exploration.


from typing import Optional

from ghidra.program.model.data import (
    DataType,
    Composite,
    Structure,
    Union,
    Enum,
    AbstractIntegerDataType,
    AbstractFloatDataType,
    PointerDataType,
    ArrayDataType,
    VoidDataType
)


class TypeUtils:
    """Utility functions leveraging Ghidra's built-in type system"""

    @staticmethod
    def is_composite_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is a composite type using Ghidra's type hierarchy"""
        if data_type is None:
            return False
        # Use Ghidra's built-in type hierarchy instead of duck typing
        return isinstance(data_type, Composite)

    @staticmethod
    def is_structure_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is specifically a Structure"""
        return isinstance(data_type, Structure) if data_type else False

    @staticmethod
    def is_union_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is specifically a Union"""
        return isinstance(data_type, Union) if data_type else False

    @staticmethod
    def is_enum_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is an Enum"""
        return isinstance(data_type, Enum) if data_type else False

    @staticmethod
    def is_primitive_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is a primitive type using Ghidra hierarchy"""
        if data_type is None:
            return False
        return (isinstance(data_type, (AbstractIntegerDataType, AbstractFloatDataType)) or
                isinstance(data_type, VoidDataType))

    @staticmethod
    def is_pointer_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is a pointer using Ghidra's type system"""
        return isinstance(data_type, PointerDataType) if data_type else False

    @staticmethod
    def is_array_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is an array using Ghidra's type system"""
        return isinstance(data_type, ArrayDataType) if data_type else False

    @staticmethod
    def get_type_path(data_type: Optional[DataType]) -> str:
        """Safely get type path name"""
        return data_type.getPathName() if data_type else "None"

    @staticmethod
    def get_type_name(data_type: Optional[DataType]) -> str:
        """Safely get type name"""
        return data_type.getName() if data_type else "None"

    @staticmethod
    def get_type_size(data_type: Optional[DataType]) -> int:
        """Safely get type size"""
        return data_type.getLength() if data_type else 0

    @staticmethod
    def is_template_type(type_name: str) -> bool:
        """Check if type name contains template parameters"""
        return '<' in type_name and '>' in type_name
