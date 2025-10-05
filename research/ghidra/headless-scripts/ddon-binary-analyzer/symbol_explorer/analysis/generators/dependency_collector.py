# Type Dependency Collection
#
# This module contains functionality for collecting and analyzing
# type dependencies using Ghidra's Composite interface efficiently.


import logging
from typing import Set, Optional

from ghidra.program.model.data import DataType, Composite, Pointer, Array

from .template_extractor import TemplateParameterExtractor


class TypeDependencyCollector:
    """Collects type dependencies using Ghidra's Composite interface efficiently"""

    def __init__(self, template_extractor: TemplateParameterExtractor, logger: logging.Logger):
        self.template_extractor = template_extractor
        self.logger = logger

    def collect_dependencies(self, root_type: DataType, max_depth: int = 10) -> Set[DataType]:
        """Collect all type dependencies up to specified depth"""
        dependencies = set()
        visited = set()

        def collect_recursive(data_type: DataType, depth: int):
            if depth >= max_depth or not data_type or data_type in visited:
                return

            visited.add(data_type)
            type_path = data_type.getPathName()

            # Skip if already processed or invalid
            if self._should_skip_type(data_type):
                return

            dependencies.add(data_type)
            self.logger.debug(f"Collecting dependencies for: {data_type.getName()} (depth: {depth})")

            # Collect from template parameters
            self._collect_template_dependencies(data_type, collect_recursive, depth)

            # Collect from composite members using Ghidra's efficient methods
            self._collect_composite_dependencies(data_type, collect_recursive, depth)

        collect_recursive(root_type, 0)
        return dependencies

    def _should_skip_type(self, data_type: DataType) -> bool:
        """Check if type should be skipped using Ghidra's validation methods"""
        if hasattr(data_type, 'isDeleted') and data_type.isDeleted():
            return True

        # Skip primitive types that don't need definitions
        type_name = data_type.getName().lower()
        primitives = ['void', 'char', 'int', 'float', 'double', 'byte', 'word', 'dword', 'qword', 'bool']
        from ghidra.program.model.data import Structure, Union, Enum
        return any(prim in type_name for prim in primitives) and not isinstance(data_type, (Structure, Union, Enum))

    def _collect_template_dependencies(self, data_type: DataType, collect_fn, depth: int):
        """Collect dependencies from template parameters"""
        template_params = self.template_extractor.resolve_template_parameters(data_type.getName(), data_type)
        for param_type in template_params:
            collect_fn(param_type, depth + 1)

    def _collect_composite_dependencies(self, data_type: DataType, collect_fn, depth: int):
        """Collect dependencies from composite type members using efficient Ghidra methods"""
        if not isinstance(data_type, Composite):
            return

        try:
            # Use getDefinedComponents() when available (more efficient)
            if hasattr(data_type, 'getDefinedComponents'):
                components = data_type.getDefinedComponents()
            else:
                # Fallback to manual iteration
                components = [data_type.getComponent(i) for i in range(data_type.getNumComponents())]

            for component in components:
                if component:
                    field_type = component.getDataType()
                    if field_type and not field_type.isDeleted():
                        collect_fn(field_type, depth + 1)

                        # Handle pointer/array element types
                        element_type = self._get_element_type(field_type)
                        if element_type and element_type != field_type:
                            collect_fn(element_type, depth + 1)

        except Exception as e:
            self.logger.debug(f"Error collecting composite dependencies for {data_type.getName()}: {e}")

    def _get_element_type(self, data_type: DataType) -> Optional[DataType]:
        """Get the element type for pointers and arrays"""
        if isinstance(data_type, (Pointer, Array)):
            return data_type.getDataType()
        return None
