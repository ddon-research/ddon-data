# C++ type formatter 
#
# This module provides formatting capabilities for converting Ghidra
# data types to C++ type definitions.


import logging
from typing import Optional

from ghidra.program.model.data import (
    DataType,
    PointerDataType,
    ArrayDataType,
    TypedefDataType,
    FunctionDefinitionDataType,
    BitFieldDataType
)


class CppTypeFormatter:
    """Formatter for generating C++ type definitions with C++ standards compliance
    
    This formatter converts Ghidra data types to proper C++ type definitions with
    special attention to:
    - C++ standard integral types (uint32_t, int32_t, etc.)
    - Proper bitfield syntax (type name : size) 
    - Bitfield validation (integral types only, reasonable sizes)
    - Ghidra BitFieldDataType handling for accurate analysis
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger
        self.type_mapping = {
            'bool': 'bool',
            'char': 'char',
            'uchar': 'unsigned char',
            'short': 'short',
            'ushort': 'unsigned short',
            'int': 'int',
            'uint': 'unsigned int',
            'long': 'long',
            'ulong': 'unsigned long',
            'longlong': 'long long',
            'ulonglong': 'unsigned long long',
            'float': 'float',
            'double': 'double',
            'void': 'void',
            # Ghidra non-standard types to C++ standard types
            'u8': 'uint8_t',
            'u16': 'uint16_t',
            'u32': 'uint32_t',
            'u64': 'uint64_t',
            's8': 'int8_t',
            's16': 'int16_t',
            's32': 'int32_t',
            's64': 'int64_t'
        }

    def get_cpp_type_name(self, data_type: DataType) -> str:
        """Convert Ghidra data type to C++ type name"""
        if data_type is None:
            return "void"

        type_name = data_type.getName()
        class_name = data_type.__class__.__name__

        # Handle BitFieldDataType instances (Ghidra's native bitfield type)
        if isinstance(data_type, BitFieldDataType):
            base_data_type = data_type.getBaseDataType()
            base_type_name = self.get_cpp_type_name(base_data_type)
            return base_type_name

        # Handle pointers using Ghidra's type hierarchy (more reliable than string checking)
        if isinstance(data_type, PointerDataType):
            referenced_type = data_type.getDataType()
            if referenced_type is not None:
                base_type = self.get_cpp_type_name(referenced_type)
                return f"{base_type}*"
            return "void*"

        # Handle bitfield types from string parsing (fallback for older representations)
        # Note: This returns just the base type, bitfield syntax is handled at field level
        # Only consider it a bitfield if it matches the pattern: primitive_type:digits
        if self._is_likely_bitfield(type_name):
            base_type, bit_size = type_name.split(':', 1)
            mapped_base = self.type_mapping.get(base_type, base_type)
            # Validate that the base type is integral (required for C++ bitfields)
            if mapped_base and self._is_integral_type(mapped_base):
                return mapped_base
            else:
                # Non-integral types cannot be bitfields in C++
                if self.logger:
                    self.logger.warning(f"Non-integral type {mapped_base} used in bitfield, this is not valid C++")
                return mapped_base or "int"

        # Handle arrays - return just the element type, array syntax handled at field level
        if "Array" in class_name or isinstance(data_type, ArrayDataType):
            if hasattr(data_type, 'getDataType') and hasattr(data_type, 'getNumElements'):
                element_type = self.get_cpp_type_name(data_type.getDataType())
                return element_type
            return type_name

        # Handle typedefs
        if "TypedefDB" in class_name or isinstance(data_type, TypedefDataType):
            if hasattr(data_type, 'getDataType'):
                base_type = data_type.getDataType()
                # Check if this is a Ghidra non-standard type that should be mapped
                mapped_type = self.type_mapping.get(type_name)
                if mapped_type is not None:
                    return mapped_type
                # For other typedefs, try to get the base type
                return self.get_cpp_type_name(base_type)

        # Handle function pointers
        if isinstance(data_type, FunctionDefinitionDataType):
            return_type = self.get_cpp_type_name(data_type.getReturnType())
            params = data_type.getArguments()
            param_types = [self.get_cpp_type_name(param.getDataType()) for param in params]
            return f"{return_type}(*)({', '.join(param_types)})"

        # Handle basic types
        mapped_type = self.type_mapping.get(type_name)
        return mapped_type if mapped_type is not None else type_name

    def _is_likely_bitfield(self, type_name: str) -> bool:
        """Check if a type name represents a bitfield (primitive:digits pattern)
        
        Avoids false positives with template types like MtTypedArray<Type::Nested>
        """
        import re
        # Match pattern: primitive_type:positive_integer
        # Primitive types are typically short (u8, u16, u32, u64, s8, s16, s32, s64, int, char, etc.)
        bitfield_pattern = r'^[a-zA-Z_]\w{0,15}:\d+$'
        return bool(re.match(bitfield_pattern, type_name))

    def _is_integral_type(self, cpp_type: str) -> bool:
        """Check if a C++ type is integral (valid for bitfields)"""
        integral_types = {
            'bool', 'char', 'signed char', 'unsigned char',
            'short', 'unsigned short', 'int', 'unsigned int',
            'long', 'unsigned long', 'long long', 'unsigned long long',
            'int8_t', 'uint8_t', 'int16_t', 'uint16_t',
            'int32_t', 'uint32_t', 'int64_t', 'uint64_t'
        }
        return cpp_type in integral_types

    def get_array_info(self, data_type: DataType) -> tuple:
        """Extract array information from Ghidra data type
        
        Returns:
            tuple: (element_type, array_size) if array, (type_name, None) otherwise
        """
        if data_type is None:
            return ("void", None)

        class_name = data_type.__class__.__name__

        # Handle arrays
        if "Array" in class_name or isinstance(data_type, ArrayDataType):
            if hasattr(data_type, 'getDataType') and hasattr(data_type, 'getNumElements'):
                element_type = self.get_cpp_type_name(data_type.getDataType())
                array_size = data_type.getNumElements()
                return (element_type, array_size)

        # Not an array
        return (self.get_cpp_type_name(data_type), None)

    def get_bitfield_info(self, data_type: DataType) -> tuple:
        """Extract bitfield information from Ghidra data type
        
        Returns:
            tuple: (base_type, bit_size) if bitfield, (type_name, None) otherwise
        """
        if data_type is None:
            return ("void", None)

        # Handle Ghidra's native BitFieldDataType
        if isinstance(data_type, BitFieldDataType):
            base_data_type = data_type.getBaseDataType()
            base_type_name = self.get_cpp_type_name(base_data_type)

            # Use effective bit size (may be truncated based on base type)
            bit_size = data_type.getBitSize()
            declared_bit_size = data_type.getDeclaredBitSize()

            # Log if declared size was truncated
            if declared_bit_size != bit_size and self.logger:
                self.logger.debug(
                    f"Bitfield declared size {declared_bit_size} truncated to {bit_size} based on base type {base_type_name}")

            # Validate integral type for C++ compliance (should always pass for valid Ghidra bitfields)
            if not self._is_integral_type(base_type_name):
                if self.logger:
                    self.logger.warning(
                        f"Non-integral type {base_type_name} used in bitfield (should not happen with valid Ghidra BitFieldDataType)")
                return (base_type_name, None)

            # Validate bit size (should always be > 0 for valid Ghidra bitfields)
            if bit_size <= 0:
                if self.logger:
                    self.logger.warning(f"Invalid bitfield size {bit_size}, must be > 0")
                return (base_type_name, None)

            return (base_type_name, bit_size)

        type_name = data_type.getName()

        # Handle bitfield types from string parsing (fallback for older representations)
        if self._is_likely_bitfield(type_name):
            base_type, bit_size = type_name.split(':', 1)
            try:
                bit_size_int = int(bit_size)
                # Validate bit size is reasonable
                if bit_size_int < 0:
                    if self.logger:
                        self.logger.warning(f"Invalid bitfield size {bit_size_int}, must be >= 0")
                    return (self.get_cpp_type_name(data_type), None)
                elif bit_size_int > 64:  # Reasonable upper limit
                    if self.logger:
                        self.logger.warning(f"Bitfield size {bit_size_int} is unusually large")

                mapped_base = self.type_mapping.get(base_type, base_type)

                # Validate integral type
                if mapped_base and not self._is_integral_type(mapped_base):
                    if self.logger:
                        self.logger.warning(f"Non-integral type {mapped_base} used in bitfield")
                    return (mapped_base, None)

                return (mapped_base or "int", bit_size_int)
            except ValueError:
                if self.logger:
                    self.logger.warning(f"Invalid bitfield size '{bit_size}', not a valid integer")
                return (self.get_cpp_type_name(data_type), None)

        # Not a bitfield
        return (self.get_cpp_type_name(data_type), None)

    def get_qualified_struct_name(self, data_type: DataType) -> str:
        """Get qualified struct name with namespace from DWARF path"""
        if data_type is None:
            return "void"

        type_name = data_type.getName()
        type_path = data_type.getPathName()

        # For DWARF types, try to extract namespace information from the path
        if "/DWARF/" in type_path:
            # Extract namespace from path like "/DWARF/rLandInfo.h/rLandInfo/cLandInfo"
            path_parts = type_path.split('/')

            # Find the parts after the header file
            dwarf_index = -1
            for i, part in enumerate(path_parts):
                if part == "DWARF":
                    dwarf_index = i
                    break

            if dwarf_index >= 0 and len(path_parts) > dwarf_index + 2:
                # Skip DWARF and the .h file, collect namespace parts
                namespace_parts = []
                for i in range(dwarf_index + 2, len(path_parts)):
                    part = path_parts[i]
                    # Skip empty parts
                    if part:
                        namespace_parts.append(part)

                if len(namespace_parts) > 1:
                    # The last part should be the same as type_name, but the preceding parts are namespace
                    # Join with :: to create qualified name like "rLandInfo::cLandInfo"
                    qualified_name = "::".join(namespace_parts)
                    if self.logger:
                        self.logger.debug(f"Qualified name for {type_name}: {qualified_name} (from path: {type_path})")
                    return qualified_name
                elif len(namespace_parts) == 1:
                    # Single part, might be at root level
                    if namespace_parts[0] == type_name:
                        # It's a root level type
                        if self.logger:
                            self.logger.debug(f"Root level type: {type_name}")
                        return type_name
                    else:
                        # Unexpected structure
                        if self.logger:
                            self.logger.debug(f"Unexpected single namespace part for {type_name}: {namespace_parts[0]}")
                        return type_name

        # Fallback to simple name if no namespace found
        if self.logger:
            self.logger.debug(f"Using simple name for {type_name} (no namespace found from path: {type_path})")
        return type_name
