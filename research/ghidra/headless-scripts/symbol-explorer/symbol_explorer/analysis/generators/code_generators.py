# C++ Code Generation Strategies
#
# This module contains abstract base class and concrete implementations
# for generating C++ code from Ghidra DataType objects.


import logging
from abc import ABC, abstractmethod
from typing import Dict, List

from ghidra.program.model.data import (
    DataType, Structure, Union, Enum, DataTypeComponent, TypeDef
)

from ...output.formatters import CppTypeFormatter


class CppCodeGenerator(ABC):
    """Abstract base for C++ code generation strategies"""

    @abstractmethod
    def generate_definition(self, data_type: DataType) -> str:
        """Generate C++ definition for a DataType"""
        pass


class StructureGenerator(CppCodeGenerator):
    """Generates C++ struct definitions using Ghidra's Structure interface"""

    def __init__(self, formatter: CppTypeFormatter, logger: logging.Logger):
        self.formatter = formatter
        self.logger = logger

    def generate_definition(self, data_type: DataType) -> str:
        """Generate struct definition leveraging Ghidra's Structure methods"""
        if not isinstance(data_type, Structure):
            raise ValueError(f"Expected Structure, got {type(data_type)}")

        qualified_name = self.formatter.get_qualified_struct_name(data_type)

        # Use Ghidra's packing information if available
        packing_info = self._get_packing_info(data_type)

        # Extract inheritance and fields using efficient Ghidra methods
        base_classes, fields = self._analyze_structure_layout(data_type)

        return self._format_struct_definition(qualified_name, base_classes, fields, data_type, packing_info)

    def _get_packing_info(self, structure: Structure) -> Dict:
        """Extract packing information using Ghidra's interface"""
        info = {}
        try:
            if hasattr(structure, 'isPackingEnabled'):
                info['packing_enabled'] = structure.isPackingEnabled()
            if hasattr(structure, 'getExplicitPackingValue'):
                info['pack_value'] = structure.getExplicitPackingValue()
            if hasattr(structure, 'getExplicitMinimumAlignment'):
                info['min_alignment'] = structure.getExplicitMinimumAlignment()
        except Exception as e:
            self.logger.debug(f"Could not get packing info for {structure.getName()}: {e}")

        return info

    def _analyze_structure_layout(self, structure: Structure) -> tuple:
        """Analyze structure layout using Ghidra's component interface"""
        base_classes = []
        fields = []

        try:
            # Use getDefinedComponents() for better performance
            if hasattr(structure, 'getDefinedComponents'):
                components = structure.getDefinedComponents()
            else:
                components = [structure.getComponent(i) for i in range(structure.getNumComponents())]

            for component in components:
                if not component or component.getDataType().isDeleted():
                    continue

                field_info = self._extract_component_info(component)

                if self._is_base_class_component(component):
                    base_class = self._extract_base_class_info(component)
                    base_classes.append(base_class)
                else:
                    fields.append(field_info)

        except Exception as e:
            self.logger.warning(f"Error analyzing structure layout for {structure.getName()}: {e}")

        return base_classes, fields

    def _extract_component_info(self, component: DataTypeComponent) -> Dict:
        """Extract comprehensive component information using Ghidra's interface"""
        field_type = component.getDataType()

        info = {
            'name': component.getFieldName() or f"field_{component.getOrdinal()}",
            'type': self.formatter.get_cpp_type_name(field_type),
            'offset': component.getOffset(),
            'size': component.getLength(),
            'ordinal': component.getOrdinal() if hasattr(component, 'getOrdinal') else 0
        }

        # Extract bitfield information using formatter
        base_type, bit_size = self.formatter.get_bitfield_info(field_type)
        if bit_size is not None:
            info['type'] = base_type
            info['bit_size'] = bit_size

        # Extract array information
        array_element_type, array_size = self.formatter.get_array_info(field_type)
        if array_size is not None:
            info['type'] = array_element_type
            info['array_size'] = array_size

        # Add comment if available
        if hasattr(component, 'getComment'):
            comment = component.getComment()
            if comment:
                info['comment'] = comment

        return info

    def _is_base_class_component(self, component: DataTypeComponent) -> bool:
        """Detect base class components (super_ prefix at offset 0)"""
        field_name = component.getFieldName()
        return (bool(field_name) and field_name.startswith("super_") and
                component.getOffset() == 0)

    def _extract_base_class_info(self, component: DataTypeComponent) -> str:
        """Extract base class type name"""
        field_type = component.getDataType()

        # Unwrap typedefs
        while isinstance(field_type, TypeDef):
            field_type = field_type.getDataType()

        if isinstance(field_type, (Structure, Union)):
            return self.formatter.get_qualified_struct_name(field_type)

        return self.formatter.get_cpp_type_name(field_type)

    def _format_struct_definition(self, name: str, base_classes: List[str],
                                  fields: List[Dict], structure: Structure,
                                  packing_info: Dict) -> str:
        """Format the complete struct definition"""
        lines = []

        # Struct declaration with inheritance
        if base_classes:
            inheritance = ", ".join(f"public {base}" for base in base_classes)
            lines.append(f"struct {name} : {inheritance} {{")
        else:
            lines.append(f"struct {name} {{")

        # Add packing comment if relevant
        if packing_info.get('packing_enabled'):
            pack_val = packing_info.get('pack_value', 'default')
            lines.append(f"  // Packed structure (pack value: {pack_val})")

        # Add fields
        for field in fields:
            field_line = self._format_field_line(field)
            lines.append(f"  {field_line}")

        # Close struct with size comment
        lines.append(f"}};  // Total size: {structure.getLength()} bytes")

        return "\n".join(lines)

    def _format_field_line(self, field: Dict) -> str:
        """Format a single field line with all attributes"""
        name = field['name']
        cpp_type = field['type']

        # Handle bitfields
        if 'bit_size' in field:
            field_decl = f"{cpp_type} {name} : {field['bit_size']}"
        # Handle arrays  
        elif 'array_size' in field:
            field_decl = f"{cpp_type} {name}[{field['array_size']}]"
        # Regular fields
        else:
            field_decl = f"{cpp_type} {name}"

        # Add offset and size comment
        comment_parts = [f"offset: {field['offset']}", f"size: {field['size']}"]

        # Add user comment if present
        if 'comment' in field:
            comment_parts.append(field['comment'])

        comment = ", ".join(comment_parts)
        return f"{field_decl};  // {comment}"


class UnionGenerator(CppCodeGenerator):
    """Generates C++ union definitions"""

    def __init__(self, formatter: CppTypeFormatter, logger: logging.Logger):
        self.formatter = formatter
        self.logger = logger

    def generate_definition(self, data_type: DataType) -> str:
        """Generate union definition (unions don't support inheritance)"""
        if not isinstance(data_type, Union):
            raise ValueError(f"Expected Union, got {type(data_type)}")

        qualified_name = self.formatter.get_qualified_struct_name(data_type)
        lines = [f"union {qualified_name} {{"]

        try:
            for i in range(data_type.getNumComponents()):
                component = data_type.getComponent(i)
                if component and not component.getDataType().isDeleted():
                    field_name = component.getFieldName() or f"field_{i}"
                    field_type = self.formatter.get_cpp_type_name(component.getDataType())

                    # Handle bitfields and arrays
                    base_type, bit_size = self.formatter.get_bitfield_info(component.getDataType())
                    array_element_type, array_size = self.formatter.get_array_info(component.getDataType())

                    if bit_size is not None:
                        field_decl = f"{base_type} {field_name} : {bit_size}"
                    elif array_size is not None:
                        field_decl = f"{array_element_type} {field_name}[{array_size}]"
                    else:
                        field_decl = f"{field_type} {field_name}"

                    lines.append(f"  {field_decl};  // offset: {component.getOffset()}, size: {component.getLength()}")

        except Exception as e:
            self.logger.warning(f"Error generating union definition for {data_type.getName()}: {e}")
            lines.append("  // Error processing union members")

        lines.append(f"}};  // Total size: {data_type.getLength()} bytes")
        return "\n".join(lines)


class EnumGenerator(CppCodeGenerator):
    """Generates C++ enum definitions using Ghidra's Enum interface"""

    def __init__(self, formatter: CppTypeFormatter, logger: logging.Logger):
        self.formatter = formatter
        self.logger = logger

    def generate_definition(self, data_type: DataType) -> str:
        """Generate enum definition leveraging Ghidra's Enum methods"""
        if not isinstance(data_type, Enum):
            raise ValueError(f"Expected Enum, got {type(data_type)}")

        qualified_name = self.formatter.get_qualified_struct_name(data_type)
        lines = [f"enum {qualified_name} {{"]

        try:
            names = data_type.getNames()
            for i, name in enumerate(names):
                value = self._extract_enum_value(data_type, name, i)
                lines.append(f"  {name} = {value},")
        except Exception as e:
            self.logger.debug(f"Could not extract enum values for {qualified_name}: {e}")
            lines.append("  // Enum values not available")

        lines.append(f"}};  // Size: {data_type.getLength()} bytes")
        return "\n".join(lines)

    def _extract_enum_value(self, data_type: Enum, name: str, index: int):
        """Extract enum value with multiple fallback strategies"""
        try:
            # Try different Ghidra enum value extraction methods
            if hasattr(data_type, 'getIntValueForName'):
                return data_type.getIntValueForName(name)
            elif hasattr(data_type, 'getValues'):
                values = data_type.getValues()
                if values and index < len(values):
                    return values[index]

            # Fallback to index
            return index

        except Exception:
            return index
