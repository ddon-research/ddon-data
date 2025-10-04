# Function Information - Data class for function metadata and properties  
# Provides structured information about functions including namespace details

from dataclasses import dataclass
from typing import Optional

from ghidra.program.model.address import Address
from ghidra.program.model.listing import Function

from ..config import AnalyzerConfig


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
