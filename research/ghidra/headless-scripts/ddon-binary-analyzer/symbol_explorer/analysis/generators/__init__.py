# Generators Package - Java-style Modular Architecture
#
# This package provides a modular architecture for C++ definition generation
# from Ghidra DataType objects, organized with individual files for each class.


from .code_generators import CppCodeGenerator, StructureGenerator, UnionGenerator, EnumGenerator
from .cpp_definition_generator import CppDefinitionGenerator
from .dependency_collector import TypeDependencyCollector
from .template_extractor import TemplateParameterExtractor
# Import all the main classes for easy access
from .type_discovery import TypeDiscoveryStrategy, CachedTypeDiscovery, SearchServiceTypeDiscovery

# Export the main classes
__all__ = [
    # Abstract interfaces
    "TypeDiscoveryStrategy",
    "CppCodeGenerator",

    # Concrete implementations
    "CachedTypeDiscovery",
    "SearchServiceTypeDiscovery",
    "TemplateParameterExtractor",
    "TypeDependencyCollector",
    "StructureGenerator",
    "UnionGenerator",
    "EnumGenerator",

    # Main facade
    "CppDefinitionGenerator"
]
