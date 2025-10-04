# Type visitor classes and visitor pattern implementation
#
# This module contains abstract visitor interfaces and concrete implementations
# for processing different types of data structures in DWARF symbols.


import logging
from abc import ABC, abstractmethod
from typing import Set

from ghidra.program.model.data import (
    StructureDataType,
    UnionDataType,
    EnumDataType,
    ArrayDataType,
    PointerDataType,
    FunctionDefinitionDataType,
    DataType,
    TypedefDataType
)

from ..output.formatters import CppTypeFormatter
from ..utils.type_utils import TypeUtils


class TypeVisitor(ABC):
    """Abstract base class for type visitors"""

    @abstractmethod
    def visit_structure(self, struct_type: StructureDataType) -> None:
        pass

    @abstractmethod
    def visit_union(self, union_type: UnionDataType) -> None:
        pass

    @abstractmethod
    def visit_enum(self, enum_type: EnumDataType) -> None:
        pass

    @abstractmethod
    def visit_array(self, array_type: ArrayDataType) -> None:
        pass

    @abstractmethod
    def visit_pointer(self, pointer_type: PointerDataType) -> None:
        pass

    @abstractmethod
    def visit_function(self, func_type: FunctionDefinitionDataType) -> None:
        pass

    @abstractmethod
    def visit_typedef(self, typedef_type: TypedefDataType) -> None:
        pass

    @abstractmethod
    def visit_primitive(self, data_type: DataType) -> None:
        pass


class TypeExplorationVisitor(TypeVisitor):
    """Concrete visitor for exploring and logging type details"""

    def __init__(self, logger: logging.Logger, formatter: CppTypeFormatter):
        self.logger = logger
        self.formatter = formatter
        self.indent_level = 0
        self.visited_types: Set[str] = set()

    def visit_structure(self, struct_type: StructureDataType) -> None:
        self._visit_composite("Structure", struct_type)

    def visit_union(self, union_type: UnionDataType) -> None:
        self._visit_composite("Union", union_type)

    def visit_enum(self, enum_type: EnumDataType) -> None:
        self.logger.debug(f"Enum: {enum_type.getName()}")
        self._explore_enum_details(enum_type)

    def visit_array(self, array_type: ArrayDataType) -> None:
        self.logger.debug(f"Array: {array_type.getName()}")
        self._explore_array_details(array_type)

    def visit_pointer(self, pointer_type: PointerDataType) -> None:
        self.logger.debug(f"Pointer: {pointer_type.getName()}")
        self._explore_pointer_details(pointer_type)

    def visit_function(self, func_type: FunctionDefinitionDataType) -> None:
        self.logger.debug(f"Function: {func_type.getName()}")
        self._explore_function_details(func_type)

    def visit_typedef(self, typedef_type: TypedefDataType) -> None:
        self.logger.debug(f"Typedef: {typedef_type.getName()}")
        self._explore_typedef_details(typedef_type)

    def visit_primitive(self, data_type: DataType) -> None:
        self.logger.debug(f"Primitive type: {data_type.getName()} (size: {data_type.getLength()} bytes)")

    def _visit_composite(self, type_name: str, composite_type) -> None:
        """Common logic for visiting composite types"""
        type_key = composite_type.getPathName()
        if type_key in self.visited_types:
            self.logger.debug(f"(Already visited: {composite_type.getName()})")
            return

        self.visited_types.add(type_key)

        num_components = composite_type.getNumComponents()
        self.logger.debug(f"{type_name}: {composite_type.getName()}")
        self.logger.debug(f"Components: {num_components}")

        if num_components == 0:
            self.logger.debug("(Empty structure)")
            return

        self.indent_level += 1

        for i in range(num_components):
            component = composite_type.getComponent(i)
            self._explore_component(component, i)

        self.indent_level -= 1

    def _explore_component(self, component, index: int) -> None:
        """Explore a single component of a composite type"""
        field_name = component.getFieldName() or "(unnamed)"
        data_type = component.getDataType()
        offset = component.getOffset()
        length = component.getLength()

        indent = "  " * self.indent_level
        self.logger.debug(f"{indent}Field {index}: {field_name}")
        self.logger.debug(f"{indent}  Offset: {offset} bytes")
        self.logger.debug(f"{indent}  Size: {length} bytes")
        self.logger.debug(f"{indent}  Type: {data_type.getName()} ({data_type.__class__.__name__})")

        # Recursively explore the field's type using the visitor pattern
        type_dispatcher = TypeDispatcher(self)
        type_dispatcher.dispatch(data_type)

    def _explore_enum_details(self, enum_type: EnumDataType) -> None:
        """Explore enumeration details"""
        values = enum_type.getValues()
        names = enum_type.getNames()

        self.logger.debug(f"Enumeration values: ({len(values)} total)")

        self.indent_level += 1
        for i, (name, value) in enumerate(zip(names, values)):
            indent = "  " * self.indent_level
            self.logger.debug(f"{indent}{name} = {value} (0x{value & 0xFFFFFFFF:x})")
            if i >= 20:  # Limit output for very large enums
                remaining = len(values) - i - 1
                if remaining > 0:
                    self.logger.debug(f"{indent}... and {remaining} more values")
                break
        self.indent_level -= 1

    def _explore_array_details(self, array_type: ArrayDataType) -> None:
        """Explore array type details"""
        element_type = array_type.getDataType()
        element_count = array_type.getNumElements()
        element_size = element_type.getLength()

        self.logger.debug("Array details:")
        self.logger.debug(f"  Element count: {element_count}")
        self.logger.debug(f"  Element size: {element_size} bytes")
        self.logger.debug(f"  Element type: {element_type.getName()}")

        # Explore the element type if it's complex
        if isinstance(element_type, (StructureDataType, UnionDataType, EnumDataType)):
            self.logger.debug("Element type details:")
            self.indent_level += 1
            type_dispatcher = TypeDispatcher(self)
            type_dispatcher.dispatch(element_type)
            self.indent_level -= 1

    def _explore_pointer_details(self, pointer_type: PointerDataType) -> None:
        """Explore pointer type details"""
        referenced_type = pointer_type.getDataType()
        if referenced_type is not None:
            self.logger.debug(f"Points to: {referenced_type.getName()} ({referenced_type.__class__.__name__})")

            # Explore referenced type if it's complex
            if isinstance(referenced_type, (StructureDataType, UnionDataType, EnumDataType)):
                self.logger.debug("Referenced type details:")
                self.indent_level += 1
                type_dispatcher = TypeDispatcher(self)
                type_dispatcher.dispatch(referenced_type)
                self.indent_level -= 1
        else:
            self.logger.debug("Points to: (unknown/void)")

    def _explore_function_details(self, func_type: FunctionDefinitionDataType) -> None:
        """Explore function type details"""
        return_type = func_type.getReturnType()
        params = func_type.getArguments()

        self.logger.debug("Function signature:")
        self.logger.debug(f"  Return type: {return_type.getName()}")
        self.logger.debug(f"  Parameters: {len(params)}")

        if len(params) > 0:
            self.indent_level += 1
            for i, param in enumerate(params):
                param_type = param.getDataType()
                param_name = param.getName() if param.getName() else "(unnamed)"
                indent = "  " * self.indent_level
                self.logger.debug(f"{indent}Param {i}: {param_type.getName()} {param_name}")
            self.indent_level -= 1

    def _explore_typedef_details(self, typedef_type: TypedefDataType) -> None:
        """Explore typedef details"""
        base_type = typedef_type.getDataType()
        self.logger.debug(f"Typedef of: {base_type.getName()} ({base_type.__class__.__name__})")

        # Explore the underlying type
        self.indent_level += 1
        type_dispatcher = TypeDispatcher(self)
        type_dispatcher.dispatch(base_type)
        self.indent_level -= 1


class TypeDispatcher:
    """Dispatcher for routing data types to appropriate visitor methods"""

    def __init__(self, visitor: TypeVisitor):
        self.visitor = visitor

    def dispatch(self, data_type: DataType) -> None:
        """Dispatch data type to appropriate visitor method"""
        if data_type is None:
            return

        # Check for composite types first (both Structure and Union)
        if TypeUtils.is_composite_type(data_type):
            if 'Union' in data_type.__class__.__name__:
                self.visitor.visit_union(data_type)
            else:
                self.visitor.visit_structure(data_type)
        elif isinstance(data_type, EnumDataType):
            self.visitor.visit_enum(data_type)
        elif isinstance(data_type, ArrayDataType):
            self.visitor.visit_array(data_type)
        elif isinstance(data_type, PointerDataType):
            self.visitor.visit_pointer(data_type)
        elif isinstance(data_type, FunctionDefinitionDataType):
            self.visitor.visit_function(data_type)
        elif isinstance(data_type, TypedefDataType):
            self.visitor.visit_typedef(data_type)
        else:
            self.visitor.visit_primitive(data_type)
