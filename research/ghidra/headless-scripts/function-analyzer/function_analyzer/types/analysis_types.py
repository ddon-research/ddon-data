# Analysis Types - TypedDict definitions for structured data
# Provides type definitions for analysis results and data structures

from typing import Dict, List, Optional, TypedDict


class AnalysisTypes:
    """Type definitions for analysis results and data structures"""

    class LevelResult(TypedDict):
        depth: int
        function_analyses: List[Dict]
        struct_related_decompilations: Dict[str, Optional[str]]

    class AnalysisResult(TypedDict):
        main_function: object  # Function type from Ghidra
        main_function_name: str
        levels: List['AnalysisTypes.LevelResult']
