"""Symbol Explorer Package

Modular DWARF symbol exploration package for Ghidra analysis.
Provides C++ definition generation from binary structures.
"""

from .analysis.generators import CppDefinitionGenerator, TemplateParameterExtractor
from .analysis.search_service import SymbolSearchService
# Analysis exports
from .analysis.visitors import TypeVisitor, TypeExplorationVisitor, TypeDispatcher
# Core functionality exports
from .core.config import ExplorerConfig
from .core.data_types import DataTypeInfo
from .core.exceptions import SymbolExplorationError, TypeProcessingError, NamespaceExtractionError, CodeGenerationError
from .core.logging import LoggingConfig
# Output exports
from .output.formatters import CppTypeFormatter
from .output.handlers import HeadlessOutputHandler
from .utils.namespace_utils import NamespaceUtils
# Utility exports
from .utils.type_utils import TypeUtils

# Note: Main explorer class is now at the root level in ../main.py

__version__ = "1.0.0"
__author__ = "Sehkah"
__category__ = "ddon-research"

__all__ = [
    # Core
    "ExplorerConfig",
    "SymbolExplorationError",
    "TypeProcessingError",
    "NamespaceExtractionError",
    "CodeGenerationError",
    "LoggingConfig",
    "DataTypeInfo",

    # Utils
    "TypeUtils",
    "NamespaceUtils",

    # Analysis
    "TypeVisitor",
    "TypeExplorationVisitor",
    "TypeDispatcher",
    "CppDefinitionGenerator",
    "TemplateParameterExtractor",
    "SymbolSearchService",

    # Output
    "CppTypeFormatter",
    "HeadlessOutputHandler"

    # Note: Entry point is main_headless() function in ../main.py
    # Main analysis class is DwarfSymbolExplorer in analysis submodule
]
