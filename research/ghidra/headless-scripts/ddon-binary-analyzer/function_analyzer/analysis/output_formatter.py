# Output Formatter - Formatter for generating readable analysis output
# Provides clean, structured output formatting for analysis results

import logging


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

    def format_full_debug_analysis(self, analysis_result: dict) -> str:
        """Format comprehensive debug analysis with detailed information"""
        output_lines = []

        # Header with analysis overview
        main_func_name = analysis_result['main_function_name']
        total_levels = len(analysis_result['levels'])

        output_lines.append("=" * 80)
        output_lines.append(f"COMPREHENSIVE FUNCTION ANALYSIS: {main_func_name}")
        output_lines.append("=" * 80)
        output_lines.append(f"Analysis completed with {total_levels} recursion levels")
        output_lines.append("")

        # Process each recursion level
        for level_idx, level_result in enumerate(analysis_result['levels']):
            depth = level_result['depth']
            function_count = len(level_result['function_analyses'])
            struct_count = len(level_result['struct_related_decompilations'])

            output_lines.append(f"-" * 60)
            output_lines.append(f"RECURSION LEVEL {depth} (Level {level_idx + 1}/{total_levels})")
            output_lines.append(f"Functions analyzed: {function_count}, Struct-related: {struct_count}")
            output_lines.append(f"-" * 60)
            output_lines.append("")

            # Detail each function analysis
            for func_idx, func_analysis in enumerate(level_result['function_analyses']):
                func_info = func_analysis['function_info']
                output_lines.append(f"[{level_idx + 1}.{func_idx + 1}] Function Analysis: {func_info.name}")
                output_lines.append(f"  Qualified Name: {func_info.qualified_name}")
                output_lines.append(f"  Namespace: {func_info.namespace or 'Global'}")
                output_lines.append(f"  Class: {func_info.class_name or 'None'}")
                output_lines.append(f"  Address: {func_info.address}")

                # Cross-reference information
                related_funcs = func_analysis['related_functions']
                output_lines.append(f"  Direct calls: {len(related_funcs.get('direct_calls', []))}")
                output_lines.append(f"  Struct-related calls: {len(related_funcs.get('struct_related_calls', []))}")
                output_lines.append(f"  Callers: {len(related_funcs.get('callers', []))}")

                # Function calls from decompiled code
                relevant_calls = func_analysis.get('relevant_calls', [])
                if relevant_calls:
                    output_lines.append(f"  Relevant calls found: {len(relevant_calls)}")
                    for call in relevant_calls[:5]:  # Show first 5
                        output_lines.append(f"    - {call}")
                    if len(relevant_calls) > 5:
                        output_lines.append(f"    ... and {len(relevant_calls) - 5} more")

                output_lines.append("")

            # Show struct-related decompilations for this level
            if level_result['struct_related_decompilations']:
                output_lines.append(f"Struct-related functions at level {depth}:")
                for func_name in sorted(level_result['struct_related_decompilations'].keys()):
                    output_lines.append(f"  - {func_name}")
                output_lines.append("")

        # Summary section
        output_lines.append("=" * 60)
        output_lines.append("ANALYSIS SUMMARY")
        output_lines.append("=" * 60)

        # Count unique functions across all levels
        all_functions = set()
        for level_result in analysis_result['levels']:
            for func_analysis in level_result['function_analyses']:
                all_functions.add(func_analysis['function_info'].name)
            for func_name in level_result['struct_related_decompilations'].keys():
                all_functions.add(func_name)

        output_lines.append(f"Total unique functions analyzed: {len(all_functions)}")
        output_lines.append(
            f"Maximum recursion depth reached: {max(level['depth'] for level in analysis_result['levels']) if analysis_result['levels'] else 0}")
        output_lines.append(f"Recursion levels processed: {len(analysis_result['levels'])}")
        output_lines.append("")

        # List all unique functions
        output_lines.append("Complete function list:")
        for func_name in sorted(all_functions):
            output_lines.append(f"  - {func_name}")

        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("END DEBUG ANALYSIS")
        output_lines.append("=" * 80)

        return "\n".join(output_lines)
