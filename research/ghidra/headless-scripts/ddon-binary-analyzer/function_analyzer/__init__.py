"""DDON Function Analyzer - Modular function decompilation and analysis system.

A comprehensive system for analyzing C++ functions extracted from Dragon's Dogma Online
binary files using Ghidra. Provides recursive decompilation, namespace analysis, 
cross-reference tracking, and struct relationship mapping.

Architecture:
- config: Configuration and exception handling
- types: Type definitions and data structures
- utils: Utilities and helper functions  
- services: Core business logic services
- analysis: High-level analysis components

Usage:
    from function_analyzer import FunctionDecompilationAnalyzer
    
    analyzer = FunctionDecompilationAnalyzer(program, "INFO")
    analyzer.analyze_function("rLandInfo::load", max_depth=3)
"""

# Main exports
from .analysis import FunctionDecompilationAnalyzer, OutputFormatter
from .config import (
    AnalyzerConfig,
    AnalyzerException,
    FunctionNotFoundException,
    DecompilationException,
    ConfigurationException
)
from .services.cross_reference_analyzer import CrossReferenceAnalyzer
from .services.decompilation_service import DecompilationService
from .services.function_search_service import FunctionSearchService
from .services.struct_analysis_service import StructAnalysisService
from .types import AnalysisTypes, FunctionInfo
from .utils import NamespaceUtils, LoggingConfig, GhidraConsoleHandler

__version__ = "2.0.0"
__author__ = "Sehkah"
__category__ = "ddon-research"

__all__ = [
    # Main analyzer
    'FunctionDecompilationAnalyzer',

    # Services
    'FunctionSearchService',
    'DecompilationService',
    'CrossReferenceAnalyzer',
    'StructAnalysisService',
    'OutputFormatter',

    # Types
    'AnalysisTypes',
    'FunctionInfo',

    # Utils
    'NamespaceUtils',
    'LoggingConfig',
    'GhidraConsoleHandler',

    # Config
    'AnalyzerConfig',
    'AnalyzerException',
    'FunctionNotFoundException',
    'DecompilationException',
    'ConfigurationException'
]
