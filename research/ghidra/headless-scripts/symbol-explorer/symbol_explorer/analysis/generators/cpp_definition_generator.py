# Main C++ Definition Generator
#
# This module provides the main facade class for C++ definition generation
# using the modular architecture with strategy patterns.


import logging
from typing import Set, Dict, List

from ghidra.program.model.data import DataType, Structure, Union, Enum, TypeDef

from .code_generators import StructureGenerator, UnionGenerator, EnumGenerator
from .dependency_collector import TypeDependencyCollector
from .template_extractor import TemplateParameterExtractor
from .type_discovery import CachedTypeDiscovery
from ...core.exceptions import CodeGenerationError
from ...output.formatters import CppTypeFormatter


class CppDefinitionGenerator:
    """Simplified facade for C++ definition generation using modular architecture"""

    def __init__(self, formatter: CppTypeFormatter, logger: logging.Logger, search_service):
        self.formatter = formatter
        self.logger = logger
        self.search_service = search_service  # Use search service directly instead of multiple strategies

        # Lazy initialization for components
        self.template_extractor = None
        self.dependency_collector = None

        # Code generators
        self.struct_generator = StructureGenerator(formatter, logger)
        self.union_generator = UnionGenerator(formatter, logger)
        self.enum_generator = EnumGenerator(formatter, logger)

        # State
        self.type_definitions: Dict[str, str] = {}

    def generate_full_cpp_definitions(self, data_type: DataType) -> str:
        """Generate complete C++ definitions using modular architecture"""
        try:
            # Initialize discovery and collection components
            self._initialize_components(data_type)

            # Collect all type dependencies
            if not self.dependency_collector:
                raise CodeGenerationError("Dependency collector not initialized")
            dependencies = self.dependency_collector.collect_dependencies(data_type)

            # Generate definitions for dependencies first
            self._generate_dependency_definitions(dependencies, data_type)

            # Generate main type definition
            main_definition = self._generate_single_definition(data_type)

            return self._format_complete_output(main_definition)

        except Exception as e:
            raise CodeGenerationError(f"Error generating C++ definitions: {e}") from e

    def _initialize_components(self, data_type: DataType):
        """Initialize discovery and collection components - simplified"""
        dtm = data_type.getDataTypeManager()
        if dtm and not hasattr(self, 'cached_discovery'):
            self.cached_discovery = CachedTypeDiscovery(dtm, self.logger)

        if self.template_extractor is None:
            # Use search service directly instead of redundant strategy pattern
            from .type_discovery import SearchServiceTypeDiscovery
            search_discovery = SearchServiceTypeDiscovery(self.search_service, self.logger)
            self.template_extractor = TemplateParameterExtractor(search_discovery)
            self.dependency_collector = TypeDependencyCollector(self.template_extractor, self.logger)

    def _generate_dependency_definitions(self, dependencies: Set[DataType], main_type: DataType):
        """Generate definitions for all dependencies"""
        # Sort dependencies topologically (base classes before derived)
        sorted_deps = self._topological_sort_dependencies(dependencies)

        for dep_type in sorted_deps:
            if dep_type != main_type and self._should_generate_definition(dep_type):
                try:
                    definition = self._generate_single_definition(dep_type)
                    type_name = self.formatter.get_qualified_struct_name(dep_type)

                    if type_name not in self.type_definitions:
                        self.type_definitions[type_name] = definition
                        self.logger.debug(f"Generated definition for dependency: {type_name}")

                except Exception as e:
                    self.logger.debug(f"Error generating definition for {dep_type.getName()}: {e}")

    def _should_generate_definition(self, data_type: DataType) -> bool:
        """Check if a type needs a C++ definition"""
        # Skip primitive types and invalid types
        if hasattr(data_type, 'isDeleted') and data_type.isDeleted():
            return False

        # Generate definitions for composites and enums
        return isinstance(data_type, (Structure, Union, Enum))

    def _generate_single_definition(self, data_type: DataType) -> str:
        """Generate definition for a single type using appropriate generator"""
        if isinstance(data_type, Structure):
            return self.struct_generator.generate_definition(data_type)
        elif isinstance(data_type, Union):
            return self.union_generator.generate_definition(data_type)
        elif isinstance(data_type, Enum):
            return self.enum_generator.generate_definition(data_type)
        else:
            # Fallback for other types
            return f"// Unsupported type: {data_type.getName()} ({type(data_type).__name__})"

    def _topological_sort_dependencies(self, dependencies: Set[DataType]) -> List[DataType]:
        """Sort dependencies topologically using Ghidra's type information"""
        # Simple dependency sorting - base classes first
        sorted_deps = []
        processed = set()

        def add_with_dependencies(data_type: DataType):
            if data_type in processed:
                return

            # Add base classes first for structures
            if isinstance(data_type, Structure):
                base_classes = self._get_base_classes(data_type)
                for base_class in base_classes:
                    if base_class in dependencies:
                        add_with_dependencies(base_class)

            sorted_deps.append(data_type)
            processed.add(data_type)

        for dep in dependencies:
            add_with_dependencies(dep)

        return sorted_deps

    def _get_base_classes(self, structure: Structure) -> List[DataType]:
        """Extract base class types from a structure"""
        base_classes = []

        try:
            if structure.getNumComponents() > 0:
                first_component = structure.getComponent(0)
                if (first_component and
                        first_component.getOffset() == 0 and
                        first_component.getFieldName() and
                        first_component.getFieldName().startswith("super_")):

                    base_type = first_component.getDataType()
                    while isinstance(base_type, TypeDef):
                        base_type = base_type.getDataType()

                    if isinstance(base_type, Structure):
                        base_classes.append(base_type)
        except Exception as e:
            self.logger.debug(f"Error extracting base classes from {structure.getName()}: {e}")

        return base_classes

    def _format_complete_output(self, main_definition: str) -> str:
        """Format the complete output with nested types"""
        lines = []

        if self.type_definitions:
            lines.append("// Nested type definitions:")
            lines.append("")

            for definition in self.type_definitions.values():
                lines.append(definition)
                lines.append("")

        lines.append("// Main type definition:")
        lines.append(main_definition)

        return "\n".join(lines)
