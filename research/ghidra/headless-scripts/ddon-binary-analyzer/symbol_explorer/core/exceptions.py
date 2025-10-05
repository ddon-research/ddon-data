# Exception classes for symbol exploration
#
# This module contains all custom exception classes used throughout
# the DWARF symbol exploration package.


class SymbolExplorationError(Exception):
    """Base exception for symbol exploration operations"""
    pass


class TypeProcessingError(SymbolExplorationError):
    """Raised when type processing fails"""
    pass


class NamespaceExtractionError(SymbolExplorationError):
    """Raised when namespace extraction fails"""
    pass


class CodeGenerationError(SymbolExplorationError):
    """Raised when C++ code generation fails"""
    pass
