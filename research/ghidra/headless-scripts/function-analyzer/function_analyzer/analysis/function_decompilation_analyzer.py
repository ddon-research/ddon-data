# Function Decompilation Analyzer - Main analyzer class with recursive analysis capabilities
# Provides comprehensive function analysis with struct relationship tracking


import traceback
from typing import List

from ghidra.program.model.listing import Program, Function

from .output_formatter import OutputFormatter
from ..config import AnalyzerConfig, AnalyzerException, FunctionNotFoundException
from ..services import FunctionSearchService, DecompilationService, CrossReferenceAnalyzer
from ..services.struct_analysis_service import StructAnalysisService
from ..types import FunctionInfo
from ..utils import LoggingConfig


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
        self.struct_analysis = StructAnalysisService(program, self.logger)
        self.output_formatter = OutputFormatter(self.logger)

    def analyze_function(self, function_name: str, max_depth: int = AnalyzerConfig.DEFAULT_RECURSION_DEPTH) -> None:
        """Perform complete recursive analysis of a function"""
        try:
            # Validate max_depth
            if max_depth > AnalyzerConfig.MAX_RECURSION_DEPTH:
                self.logger.warning(
                    f"Max depth {max_depth} exceeds limit, capping at {AnalyzerConfig.MAX_RECURSION_DEPTH}")
                max_depth = AnalyzerConfig.MAX_RECURSION_DEPTH

            self.logger.debug(f"Starting recursive analysis for function: {function_name} (max_depth: {max_depth})")

            # Find the function
            target_function = self.function_search.find_function_by_name(function_name)
            if target_function is None:
                raise FunctionNotFoundException(f"Function '{function_name}' not found")

            # Perform recursive analysis
            analysis_result = self._recursive_analyze_function(target_function, function_name, max_depth)

            # Format and display results based on log level
            self._output_analysis_results(analysis_result)

            # Summary - only show in DEBUG mode
            if self.log_level != AnalyzerConfig.INFO_LOG_LEVEL:
                total_functions = sum(
                    len(level.get('struct_related_decompilations', {})) for level in analysis_result['levels'])
                self.logger.debug(
                    f"Recursive analysis completed successfully. Analyzed {total_functions} struct-related functions across {len(analysis_result['levels'])} levels.")

        except AnalyzerException as e:
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
            debug_output = self.output_formatter.format_full_debug_analysis(analysis_result)
            print(debug_output)

            # Also include the decompiled code at the end
            code_output = self.output_formatter.format_decompiled_code_only(analysis_result)
            if code_output.strip():
                print("\n" + "=" * 80)
                print("DECOMPILED CODE OUTPUT")
                print("=" * 80)
                print(code_output)

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
