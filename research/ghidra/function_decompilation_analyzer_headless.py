# Function Decompilation Analyzer - Headless Mode Wrapper
# This script wraps the main function_decompilation_analyzer.py for headless execution
#
# Environment Variables (set these before running):
# - FUNCTION_NAME: The function to analyze (e.g., "rLandInfo::load")
# - LOG_LEVEL: "DEBUG" or "INFO" (default: "INFO")
# - MAX_DEPTH: Maximum recursion depth 1-10 (default: 3)
#
# @author Sehkah
# @category ddon-research
# @keybinding 
# @menupath 
# @toolbar 
# @runtime PyGhidra

import os
import sys
import logging
import traceback
import re
from typing import Optional, Dict, List, Tuple, TypedDict
from dataclasses import dataclass

from ghidra.program.model.listing import Program, Function
from ghidra.program.model.address import Address
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.symbol import Reference, RefType


class AnalyzerConfig:
    """Configuration constants for the function decompilation analyzer"""
    
    # Decompilation settings
    DECOMPILATION_TIMEOUT = 30
    
    # Recursion settings
    DEFAULT_RECURSION_DEPTH = 3
    MAX_RECURSION_DEPTH = 10
    
    # Output formatting
    OUTPUT_WIDTH_MAJOR = 80
    OUTPUT_WIDTH_MEDIUM = 60
    OUTPUT_WIDTH_MINOR = 50
    
    # Dynamic separator padding
    SEPARATOR_PADDING_LARGE = 50
    SEPARATOR_PADDING_MEDIUM = 40
    SEPARATOR_PADDING_SMALL = 10
    
    # Logging
    DEFAULT_LOG_LEVEL = "DEBUG"
    INFO_LOG_LEVEL = "INFO"
    
    # Function matching
    NAMESPACE_SEPARATOR = "::"
    TEMPLATE_START = "<"
    TEMPLATE_END = ">"
    
    # Function scoring weights
    SCORE_NAMESPACE_BONUS = 10
    SCORE_PARAMETERS_BONUS = 5  
    SCORE_NON_THUNK_BONUS = 3


class NamespaceUtils:
    """Utilities for namespace and signature parsing"""
    
    # Compiled regex patterns for better performance
    NAMESPACE_PATTERNS = [
        # Pattern 1: "Class::method" in signature
        re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)::[a-zA-Z_][a-zA-Z0-9_]*\s*\('),
        # Pattern 2: "__thiscall Class::method"
        re.compile(r'__thiscall\s+([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)::[a-zA-Z_][a-zA-Z0-9_]*\s*\('),
        # Pattern 3: Parameter types for namespace hints
        re.compile(r'\(\s*([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)\s*\*\s*this')
    ]
    
    FUNCTION_CALL_PATTERNS = [
        re.compile(r'(\w+::\w+(?:<[^>]+>)?)\s*\('),  # Namespaced calls
        re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*::[a-zA-Z_][a-zA-Z0-9_]*(?:<[^>]*>)?)\s*\('),  # Complex namespaced
        re.compile(r'(\w+)\s*\(')  # Simple function calls
    ]
    
    @staticmethod
    def extract_namespace_from_signature(signature: str) -> Optional[str]:
        """Extract namespace from function signature using predefined patterns"""
        if not signature:
            return None
            
        for pattern in NamespaceUtils.NAMESPACE_PATTERNS:
            match = pattern.search(signature)
            if match:
                namespace_part = match.group(1)
                # Validate namespace (not just a type)
                if len(namespace_part) > 2 and not namespace_part.startswith('u') and namespace_part != 'void':
                    return namespace_part
        return None
    
    @staticmethod
    def extract_function_calls(decompiled_code: str) -> List[str]:
        """Extract function calls from decompiled code"""
        if not decompiled_code:
            return []
            
        function_calls = []
        for pattern in NamespaceUtils.FUNCTION_CALL_PATTERNS:
            matches = pattern.finditer(decompiled_code)
            for match in matches:
                call_name = match.group(1)
                if call_name not in function_calls:
                    function_calls.append(call_name)
        
        return function_calls
    
    @staticmethod
    def is_namespace_related(text: str, namespace: str) -> bool:
        """Check if text contains namespace-related patterns"""
        if not text or not namespace:
            return False
            
        return any([
            namespace in text,
            f"{namespace}::" in text,
            f"<{namespace}::" in text,
            f"<{namespace}" in text,
            f"{namespace}>" in text
        ])


class AnalyzerExceptions:
    """Custom exceptions for the analyzer"""
    
    class AnalyzerException(Exception):
        """Base exception for analyzer errors"""
        pass
    
    class FunctionNotFoundError(AnalyzerException):
        """Function could not be found"""
        pass
    
    class DecompilationError(AnalyzerException):
        """Decompilation failed"""
        pass
    
    class ConfigurationError(AnalyzerException):
        """Configuration or setup error"""
        pass


# Type definitions for better type safety
class LevelResult(TypedDict):
    depth: int
    function_analyses: List[Dict]
    struct_related_decompilations: Dict[str, Optional[str]]

class AnalysisResult(TypedDict):
    main_function: Function
    main_function_name: str
    levels: List[LevelResult]

class LoggingConfig:
    """Centralized logging configuration for function analyzer"""
    
    @staticmethod
    def setup_logger(name: str = "function_decompilation_analyzer", level: str = "DEBUG") -> logging.Logger:
        """Setup and return configured logger
        
        Args:
            name: Logger name
            level: Logging level ("DEBUG" or "INFO")
        """
        logger = logging.getLogger(name)
        
        # Set logging level based on parameter
        if level.upper() == "INFO":
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
            
        logger.propagate = False
        
        # Clear old handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add Ghidra console handler
        handler = GhidraConsoleHandler()
        if level.upper() == "INFO":
            formatter = logging.Formatter("%(message)s")  # No prefixes for INFO level
        else:
            formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    @staticmethod
    def setup_info_logger(name: str = "function_decompilation_analyzer") -> logging.Logger:
        """Setup logger for INFO level output (minimal information)"""
        return LoggingConfig.setup_logger(name, "INFO")


class GhidraConsoleHandler(logging.Handler):
    """Custom logging handler for Ghidra console output"""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            print(msg)
        except Exception:
            self.handleError(record)


@dataclass
class FunctionInfo:
    """Value object for function information"""
    
    function: Optional[Function]
    name: str
    signature: str
    address: Optional[Address]
    qualified_name: str
    namespace: Optional[str] = None
    class_name: Optional[str] = None
    
    def __post_init__(self):
        """Initialize computed fields after dataclass creation"""
        if self.function:
            self.name = self.function.getName()
            self.signature = self.function.getPrototypeString(False, False)
            self.address = self.function.getEntryPoint()
        else:
            self.name = "None"
            self.signature = "None"
            self.address = None
            
        # Extract namespace information
        self.namespace = self._extract_namespace()
        self.class_name = self._extract_class_name()
    
    @classmethod
    def from_function(cls, function: Function, qualified_name: Optional[str] = None):
        """Create FunctionInfo from a Function object"""
        return cls(
            function=function,
            name="",  # Will be set in __post_init__
            signature="",  # Will be set in __post_init__
            address=None,  # Will be set in __post_init__
            qualified_name=qualified_name or (function.getName() if function else "None")
        )
    
    def _extract_namespace(self) -> Optional[str]:
        """Extract namespace from qualified function name"""
        if AnalyzerConfig.NAMESPACE_SEPARATOR in self.qualified_name:
            parts = self.qualified_name.split(AnalyzerConfig.NAMESPACE_SEPARATOR)
            if len(parts) > 1:
                return AnalyzerConfig.NAMESPACE_SEPARATOR.join(parts[:-1])
        return None
    
    def _extract_class_name(self) -> Optional[str]:
        """Extract class name from qualified function name"""
        if AnalyzerConfig.NAMESPACE_SEPARATOR in self.qualified_name:
            parts = self.qualified_name.split(AnalyzerConfig.NAMESPACE_SEPARATOR)
            if len(parts) > 1:
                return parts[-2]  # Get the class name before method
        return None


class FunctionSearchService:
    """Service for searching and discovering functions"""
    
    def __init__(self, program: Program, logger: logging.Logger):
        self.program = program
        self.logger = logger
        self.function_manager = program.getFunctionManager()
        self.symbol_table = program.getSymbolTable()
    
    def find_function_by_name(self, function_name: str) -> Optional[Function]:
        """
        Find function by name, supporting namespace syntax
        
        Args:
            function_name: Function name like "rLandInfo::load" or "load"
            
        Returns:
            Function object if found, None otherwise
        """
        self.logger.debug(f"Searching for function: '{function_name}'")
        
        # Try exact match first
        exact_matches = self._find_exact_matches(function_name)
        if exact_matches:
            self.logger.debug(f"Found {len(exact_matches)} exact matches")
            return self._select_best_function_match(exact_matches)
        
        # Try partial matches if no exact match
        partial_matches = self._find_partial_matches(function_name)
        if partial_matches:
            self.logger.debug(f"Found {len(partial_matches)} partial matches")
            return self._select_best_function_match(partial_matches)
        
        self.logger.debug(f"No matches found for '{function_name}'")
        return None
    
    def get_function_at_address(self, address: Address) -> Optional[Function]:
        """Get function at specific address"""
        return self.function_manager.getFunctionAt(address)
    
    def get_function_containing_address(self, address: Address) -> Optional[Function]:
        """Get function containing the given address"""
        return self.function_manager.getFunctionContaining(address)
    
    def get_qualified_function_name(self, function: Function) -> str:
        """Get fully qualified function name from signature or symbols"""
        if function is None:
            return "None"
            
        # Get function signature which often contains namespace information
        signature = function.getPrototypeString(False, False)
        self.logger.debug(f"Function signature: {signature}")
        
        # Extract namespace from signature patterns
        namespace_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)::[a-zA-Z_][a-zA-Z0-9_]*\s*\('
        match = re.search(namespace_pattern, signature)
        if match:
            namespace_part = match.group(1)
            simple_name = function.getName()
            qualified_name = f"{namespace_part}::{simple_name}"
            self.logger.debug(f"Extracted qualified name: {qualified_name}")
            return qualified_name
        
        # Pattern 2: Look for calling convention patterns like "__thiscall Class::method"
        thiscall_pattern = r'__thiscall\s+([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)::[a-zA-Z_][a-zA-Z0-9_]*\s*\('
        match = re.search(thiscall_pattern, signature)
        if match:
            namespace_part = match.group(1)
            simple_name = function.getName()
            qualified_name = f"{namespace_part}::{simple_name}"
            self.logger.debug(f"Extracted qualified name from thiscall: {qualified_name}")
            return qualified_name
            
        # Pattern 3: Look at parameter types for namespace hints
        param_pattern = r'\(\s*([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)[\s\*]*\s*this'
        match = re.search(param_pattern, signature)
        if match:
            namespace_part = match.group(1)
            simple_name = function.getName()
            # Only use if it looks like a reasonable namespace
            if len(namespace_part) > 2 and not namespace_part.startswith('u') and namespace_part != 'void':
                qualified_name = f"{namespace_part}::{simple_name}"
                self.logger.debug(f"Extracted qualified name from parameter: {qualified_name}")
                return qualified_name
        
        # Fallback: check if any symbols at this address have namespace information
        address = function.getEntryPoint()
        if address:
            symbols = self.symbol_table.getSymbols(address)
            for symbol in symbols:
                symbol_name = symbol.getName()
                if "::" in symbol_name and symbol_name.endswith(function.getName()):
                    self.logger.debug(f"Found qualified symbol name: {symbol_name}")
                    return symbol_name
        
        # Return simple name if no namespace found
        simple_name = function.getName()
        self.logger.debug(f"Using simple name: {simple_name}")
        return simple_name
    
    def _find_exact_matches(self, function_name: str) -> List[Function]:
        """Find functions with exact name match"""
        matches = []
        
        # Search through all functions
        all_functions = self.function_manager.getFunctions(True)  # Forward direction
        for function in all_functions:
            if function.getName() == function_name:
                matches.append(function)
            
            # Also check for namespace variations
            if "::" in function_name:
                # Try without namespace
                simple_name = function_name.split("::")[-1]
                if function.getName() == simple_name:
                    # Check if this function is in the right namespace
                    if self._is_function_in_namespace(function, function_name):
                        matches.append(function)
        
        return matches
    
    def _find_partial_matches(self, function_name: str) -> List[Function]:
        """Find functions with partial name match"""
        matches = []
        search_terms = function_name.lower().replace("::", "_").split("_")
        
        all_functions = self.function_manager.getFunctions(True)
        for function in all_functions:
            func_name_lower = function.getName().lower()
            
            # Check if all search terms are in the function name
            if all(term in func_name_lower for term in search_terms):
                matches.append(function)
        
        return matches
    
    def _is_function_in_namespace(self, function: Function, full_name: str) -> bool:
        """Check if function belongs to the specified namespace"""
        # This is a simplified check - could be enhanced with more sophisticated namespace analysis
        namespace_part = "::".join(full_name.split("::")[:-1])
        
        # Check function signature or symbol information for namespace indicators
        signature = function.getPrototypeString(False, False)
        return namespace_part in signature
    
    def _select_best_function_match(self, matches: List[Function]) -> Function:
        """Select the best function match from multiple candidates"""
        if len(matches) == 1:
            return matches[0]
        
        # Prefer functions with DWARF information or more complete signatures
        scored_matches = []
        for func in matches:
            score = 0
            signature = func.getPrototypeString(False, False)
            
            # Prefer functions with namespace information
            if "::" in signature:
                score += AnalyzerConfig.SCORE_NAMESPACE_BONUS
            
            # Prefer functions with parameter information
            if "(" in signature and signature.count(",") > 0:
                score += AnalyzerConfig.SCORE_PARAMETERS_BONUS
            
            # Prefer non-thunk functions
            if not func.isThunk():
                score += AnalyzerConfig.SCORE_NON_THUNK_BONUS
            
            scored_matches.append((score, func))
        
        # Sort by score and return the best match
        scored_matches.sort(key=lambda x: x[0], reverse=True)
        return scored_matches[0][1]


class DecompilationService:
    """Service for extracting and processing decompiled code"""
    
    def __init__(self, program: Program, logger: logging.Logger):
        self.program = program
        self.logger = logger
        self.decompiler = None
        self._initialize_decompiler()
    
    def _initialize_decompiler(self):
        """Initialize the decompiler interface"""
        try:
            self.decompiler = DecompInterface()
            self.decompiler.openProgram(self.program)
            self.logger.debug("Decompiler initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize decompiler: {e}")
            self.decompiler = None
    
    def get_decompiled_function(self, function: Function) -> Optional[str]:
        """Get decompiled code for a function"""
        if self.decompiler is None:
            self.logger.error("Decompiler not available")
            return None
        
        try:
            self.logger.debug(f"Decompiling function: {function.getName()}")
            
            # Set up task monitor
            task_monitor = ConsoleTaskMonitor()
            
            # Perform decompilation with configured timeout
            decompile_results = self.decompiler.decompileFunction(
                function, 
                AnalyzerConfig.DECOMPILATION_TIMEOUT, 
                task_monitor
            )
            
            if decompile_results is None:
                self.logger.error(f"Decompilation returned null for {function.getName()}")
                return None
            
            if not decompile_results.decompileCompleted():
                error_msg = decompile_results.getErrorMessage()
                self.logger.error(f"Decompilation failed for {function.getName()}: {error_msg}")
                return None
            
            # Get the decompiled code
            high_function = decompile_results.getHighFunction()
            if high_function is None:
                self.logger.error(f"No high function available for {function.getName()}")
                return None
            
            # Get C code
            decompiled_code = decompile_results.getDecompiledFunction().getC()
            
            self.logger.debug(f"Successfully decompiled {function.getName()}")
            return decompiled_code
            
        except Exception as e:
            self.logger.error(f"Error decompiling function {function.getName()}: {e}")
            return None
    
    def get_function_calls_from_decompiled_code(self, decompiled_code: str) -> List[str]:
        """Extract function calls from decompiled code using centralized utilities"""
        function_calls = NamespaceUtils.extract_function_calls(decompiled_code)
        self.logger.debug(f"Found {len(function_calls)} function calls in decompiled code")
        return function_calls
    
    def get_decompiled_functions(self, functions: List[Function]) -> Dict[str, Optional[str]]:
        """Get decompiled code for multiple functions"""
        decompiled_functions = {}
        processed_signatures = set()  # Track processed function signatures to avoid duplicates
        
        for func in functions:
            func_name = func.getName()
            func_signature = func.getPrototypeString(False, False)
            
            # Skip if we've already processed this exact function signature
            if func_signature in processed_signatures:
                self.logger.debug(f"Skipping duplicate function signature: {func_name}")
                continue
                
            processed_signatures.add(func_signature)
            self.logger.debug(f"Decompiling struct-related function: {func_name}")
            decompiled_code = self.get_decompiled_function(func)
            decompiled_functions[func_name] = decompiled_code
            
        return decompiled_functions
    
    def cleanup(self):
        """Cleanup decompiler resources"""
        if self.decompiler:
            try:
                self.decompiler.closeProgram()
                self.decompiler.dispose()
            except Exception as e:
                self.logger.debug(f"Error cleaning up decompiler: {e}")


class CrossReferenceAnalyzer:
    """Analyzer for finding cross-referenced functions with struct relationships"""
    
    def __init__(self, program: Program, logger: logging.Logger):
        self.program = program
        self.logger = logger
        self.function_manager = program.getFunctionManager()
    
    def analyze_related_functions(self, target_function: Function, namespace_filter: Optional[str] = None) -> Dict[str, List[Function]]:
        """Analyze functions related to the target function"""
        self.logger.debug(f"Analyzing related functions for: {target_function.getName()}")
        
        related_functions = {
            'direct_calls': [],
            'struct_related_calls': [],
            'callers': [],
            'struct_related': [],
            'namespace_related': []
        }
        
        # Find direct function calls
        direct_calls = self._find_direct_calls(target_function)
        self.logger.debug(f"Found {len(direct_calls)} direct calls")
        
        # Separate struct-related calls from regular direct calls
        if namespace_filter:
            for func in direct_calls:
                if self._is_function_struct_related(func, namespace_filter):
                    related_functions['struct_related_calls'].append(func)
                else:
                    related_functions['direct_calls'].append(func)
        else:
            related_functions['direct_calls'] = direct_calls
        
        # Find callers
        related_functions['callers'] = self._find_callers(target_function)
        
        return related_functions
    
    def filter_relevant_functions(self, function_calls: List[str], namespace_filter: Optional[str] = None) -> List[str]:
        """Filter function calls to only include relevant ones"""
        if not namespace_filter:
            return function_calls
        
        relevant_calls = []
        for call in function_calls:
            if NamespaceUtils.is_namespace_related(call, namespace_filter):
                relevant_calls.append(call)
        
        return relevant_calls
    
    def _is_function_struct_related(self, function: Function, namespace: str) -> bool:
        """Check if a function is related to the specified struct namespace"""
        if function is None or not namespace:
            return False
            
        func_name = function.getName()
        signature = function.getPrototypeString(False, False)
        
        # Use centralized namespace checking
        if NamespaceUtils.is_namespace_related(func_name, namespace):
            return True
            
        if signature and NamespaceUtils.is_namespace_related(signature, namespace):
            return True
                
        return False
    
    def _find_direct_calls(self, function: Function) -> List[Function]:
        """Find functions directly called by the target function"""
        called_functions = []
        
        # Get all references from this function
        references = function.getBody().getAddresses(True)
        for address in references:
            refs: List[Reference] = self.program.getReferenceManager().getReferencesFrom(address)
            for ref in refs:
                if ref.getReferenceType() == RefType.UNCONDITIONAL_CALL or ref.getReferenceType() == RefType.CONDITIONAL_CALL:
                    called_func = self.function_manager.getFunctionAt(ref.getToAddress())
                    if called_func and called_func not in called_functions:
                        called_functions.append(called_func)
        
        return called_functions
    
    def _find_callers(self, function: Function) -> List[Function]:
        """Find functions that call the target function"""
        callers = []
        
        # Get references to this function
        references = self.program.getReferenceManager().getReferencesTo(function.getEntryPoint())
        for ref in references:
            caller_func = self.function_manager.getFunctionContaining(ref.getFromAddress())
            if caller_func and caller_func not in callers:
                callers.append(caller_func)
        
        return callers


class OutputFormatter:
    """Formatter for generating readable output"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def format_decompiled_code_only(self, analysis_result: dict) -> str:
        """Format only decompiled code for INFO level output, avoiding duplicates"""
        output_lines = []
        
        # Collect all unique functions with their decompiled code
        unique_functions = {}
        
        # Process each level and collect unique decompiled code
        for level_result in analysis_result['levels']:
            # Main function decompilations
            for func_analysis in level_result['function_analyses']:
                decompiled_code = func_analysis['decompiled_code']
                function_name = func_analysis['function_info'].name
                if decompiled_code and function_name not in unique_functions:
                    unique_functions[function_name] = decompiled_code.strip()
            
            # Struct-related decompilations
            for func_name, decompiled_code in level_result['struct_related_decompilations'].items():
                if decompiled_code and func_name not in unique_functions:
                    unique_functions[func_name] = decompiled_code.strip()
        
        # Output all unique functions in a consistent order
        for function_name in sorted(unique_functions.keys()):
            decompiled_code = unique_functions[function_name]
            output_lines.append(f"// Function: {function_name}")
            output_lines.append(decompiled_code)
            output_lines.append("")  # Empty line separator
        
        return "\n".join(output_lines)


class FunctionDecompilationAnalyzer:
    """Main facade class for analyzing function decompilation and cross-references."""
    
    def __init__(self, program: Program, log_level: str = AnalyzerConfig.DEFAULT_LOG_LEVEL):
        """Initialize the analyzer with a Ghidra program"""
        self.program = program
        self.log_level = log_level.upper()
        self.logger = LoggingConfig.setup_logger(level=log_level)
        self.function_search = FunctionSearchService(program, self.logger)
        self.decompilation_service = DecompilationService(program, self.logger)
        self.cross_ref_analyzer = CrossReferenceAnalyzer(program, self.logger)
        self.output_formatter = OutputFormatter(self.logger)
    
    def analyze_function(self, function_name: str, max_depth: int = AnalyzerConfig.DEFAULT_RECURSION_DEPTH) -> None:
        """Perform complete recursive analysis of a function"""
        try:
            # Validate max_depth
            if max_depth > AnalyzerConfig.MAX_RECURSION_DEPTH:
                self.logger.warning(f"Max depth {max_depth} exceeds limit, capping at {AnalyzerConfig.MAX_RECURSION_DEPTH}")
                max_depth = AnalyzerConfig.MAX_RECURSION_DEPTH
                
            self.logger.debug(f"Starting recursive analysis for function: {function_name} (max_depth: {max_depth})")
            
            # Find the function
            target_function = self.function_search.find_function_by_name(function_name)
            if target_function is None:
                raise AnalyzerExceptions.FunctionNotFoundError(f"Function '{function_name}' not found")
            
            # Perform recursive analysis
            analysis_result = self._recursive_analyze_function(target_function, function_name, max_depth)
            
            # Format and display results based on log level
            self._output_analysis_results(analysis_result)
            
            # Summary - only show in DEBUG mode
            if self.log_level != AnalyzerConfig.INFO_LOG_LEVEL:
                total_functions = sum(len(level.get('struct_related_decompilations', {})) for level in analysis_result['levels'])
                self.logger.debug(f"Recursive analysis completed successfully. Analyzed {total_functions} struct-related functions across {len(analysis_result['levels'])} levels.")
            
        except AnalyzerExceptions.AnalyzerException as e:
            if self.log_level == AnalyzerConfig.INFO_LOG_LEVEL:
                print(f"ERROR: {e}")
            else:
                self.logger.error(f"Analysis failed: {e}")
        except Exception as e:
            if self.log_level == AnalyzerConfig.INFO_LOG_LEVEL:
                print(f"ERROR: Analysis failed with unexpected error: {e}")
            else:
                self.logger.error(f"Analysis failed with unexpected error: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
        finally:
            # Cleanup
            self.decompilation_service.cleanup()
    
    def _output_analysis_results(self, analysis_result: dict) -> None:
        """Output analysis results based on log level"""
        if self.log_level == AnalyzerConfig.INFO_LOG_LEVEL:
            # INFO level: Only show decompiled code without any metadata
            output = self.output_formatter.format_decompiled_code_only(analysis_result)
            if output.strip():  # Only print if there's actual content
                self.logger.info(output)
        else:
            # DEBUG level: Show full analysis with debug information
            print("Full debug analysis not implemented in headless wrapper - use INFO mode")
    
    def _recursive_analyze_function(self, target_function: Function, function_name: str, max_depth: int) -> dict:
        """Recursively analyze function and its struct-related dependencies"""
        analyzed_functions = set()  # Track already analyzed functions to avoid duplicates
        analysis_result = {
            'main_function': target_function,
            'main_function_name': function_name,
            'levels': []
        }
        
        # Start with the main function at depth 0
        current_depth_functions = [(target_function, function_name)]
        
        for depth in range(max_depth + 1):
            if not current_depth_functions:
                break
                
            self.logger.debug(f"Processing depth level {depth} with {len(current_depth_functions)} functions")
            
            # Filter out already analyzed functions
            functions_to_analyze = []
            for func, qual_name in current_depth_functions:
                func_signature = func.getPrototypeString(False, False) if func else "unknown"
                func_address = str(func.getEntryPoint()) if func and func.getEntryPoint() else "unknown"
                func_id = f"{func_address}:{func_signature}"
                
                if func_id not in analyzed_functions:
                    functions_to_analyze.append((func, qual_name, depth))
                    analyzed_functions.add(func_id)
                    
            if not functions_to_analyze:
                self.logger.debug(f"No new functions to analyze at depth {depth}")
                break
            
            # Analyze all functions at this depth level
            level_result = self._analyze_function_level(functions_to_analyze)
            if level_result['function_analyses']:  # Only add level if it has analyses
                analysis_result['levels'].append(level_result)
            
            # Collect functions for next depth level
            next_depth_functions = []
            if depth < max_depth:  # Only continue if we haven't reached max depth
                for func_analysis in level_result['function_analyses']:
                    struct_related_calls = func_analysis['related_functions'].get('struct_related_calls', [])
                    for related_func in struct_related_calls:
                        qualified_name = self.function_search.get_qualified_function_name(related_func)
                        next_depth_functions.append((related_func, qualified_name))
            
            current_depth_functions = next_depth_functions
            
            if depth < max_depth:
                self.logger.debug(f"Found {len(next_depth_functions)} functions for next depth level {depth + 1}")
        
        self.logger.debug(f"Recursive analysis completed with {len(analysis_result['levels'])} levels")
        return analysis_result
    
    def _analyze_function_level(self, functions_at_level: List[tuple]) -> dict:
        """Analyze all functions at a specific recursion level"""
        if not functions_at_level:
            return {'depth': 0, 'function_analyses': [], 'struct_related_decompilations': {}}
            
        level_result = {
            'depth': functions_at_level[0][2] if len(functions_at_level[0]) > 2 else 0,
            'function_analyses': [],
            'struct_related_decompilations': {}
        }
        
        for func_data in functions_at_level:
            if len(func_data) == 3:
                func, qual_name, depth = func_data
            else:
                func, qual_name = func_data
                depth = 0
                
            self.logger.debug(f"Analyzing function at depth {depth}: {qual_name}")
            
            # Create function info object
            function_info = FunctionInfo.from_function(func, qual_name)
            
            # Get decompiled code
            decompiled_code = self.decompilation_service.get_decompiled_function(func)
            
            # Extract function calls from decompiled code
            function_calls = []
            if decompiled_code:
                function_calls = self.decompilation_service.get_function_calls_from_decompiled_code(decompiled_code)
            
            # Determine namespace filter from function name
            namespace_filter = function_info.class_name or function_info.namespace
            
            # Filter relevant function calls
            relevant_calls = self.cross_ref_analyzer.filter_relevant_functions(function_calls, namespace_filter)
            
            # Analyze cross-references
            related_functions = self.cross_ref_analyzer.analyze_related_functions(func, namespace_filter)
            
            # Store function analysis
            func_analysis = {
                'function_info': function_info,
                'decompiled_code': decompiled_code,
                'relevant_calls': relevant_calls,
                'related_functions': related_functions
            }
            level_result['function_analyses'].append(func_analysis)
            
            # Decompile struct-related functions for this specific function
            if related_functions.get('struct_related_calls'):
                struct_decompilations = self.decompilation_service.get_decompiled_functions(
                    related_functions['struct_related_calls']
                )
                # Only add new decompilations that aren't already present
                for func_name, decompiled_code in struct_decompilations.items():
                    if func_name not in level_result['struct_related_decompilations']:
                        level_result['struct_related_decompilations'][func_name] = decompiled_code
        
        return level_result


def main_headless():
    """Main function for headless execution"""
    
    # Get configuration from environment variables
    function_name = os.environ.get('FUNCTION_NAME', '')
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    max_depth = int(os.environ.get('MAX_DEPTH', '3'))
    
    # Validate environment variables
    if not function_name:
        print("ERROR: FUNCTION_NAME environment variable must be set")
        print("Example: export FUNCTION_NAME='rLandInfo::load'")
        sys.exit(1)
    
    if log_level not in ['DEBUG', 'INFO']:
        print("ERROR: LOG_LEVEL must be 'DEBUG' or 'INFO'")
        sys.exit(1)
    
    if max_depth < 1 or max_depth > AnalyzerConfig.MAX_RECURSION_DEPTH:
        print(f"ERROR: MAX_DEPTH must be between 1 and {AnalyzerConfig.MAX_RECURSION_DEPTH}")
        sys.exit(1)
    
    # Available by global Ghidra script context
    try:
        program = globals().get('currentProgram', currentProgram)  # type: ignore
        
        if program is None:
            raise AnalyzerExceptions.ConfigurationError("No program is currently loaded")
    except NameError:
        raise AnalyzerExceptions.ConfigurationError("Not running in Ghidra script environment")
    
    # Create and run the analyzer
    analyzer = FunctionDecompilationAnalyzer(program, log_level)
    analyzer.analyze_function(function_name, max_depth)


# Execute the main function when run as a script
if __name__ == "__main__":
    main_headless()