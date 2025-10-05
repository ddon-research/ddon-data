"""Function Information Data Class

Provides a structured representation of Ghidra function metadata including
namespace information, signatures, and addresses. This module wraps Ghidra's
Function objects to provide a consistent interface for function analysis.
"""

from dataclasses import dataclass, field
from typing import Optional

from ghidra.program.model.address import Address
from ghidra.program.model.listing import Function

from ..config import AnalyzerConfig


@dataclass
class FunctionInfo:
    """Immutable value object representing function metadata.

    This class wraps a Ghidra Function object and provides convenient access
    to function properties including namespace-aware names and signatures.

    Attributes:
        function: Underlying Ghidra Function object (may be None for invalid functions)
        name: Simple function name without namespace qualification
        signature: Function signature string without parameter names
        address: Entry point address of the function
        qualified_name: Fully qualified C++ name (e.g., "rLandInfo::load")
        namespace: Namespace portion of qualified name (e.g., "rLandInfo")
        class_name: Class name for member functions (e.g., "rLandInfo" for "rLandInfo::load")

    Example:
        >>> func_info = FunctionInfo.from_function(ghidra_function, "rLandInfo::load")
        >>> print(func_info.name)  # "load"
        >>> print(func_info.namespace)  # "rLandInfo"
        >>> print(func_info.class_name)  # "rLandInfo"
    """

    function: Optional[Function]
    qualified_name: str
    name: str = field(init=False)
    signature: str = field(init=False)
    address: Optional[Address] = field(init=False)
    namespace: Optional[str] = field(init=False)
    class_name: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        """Initialize computed fields from Ghidra Function object.

        Extracts function properties from the Ghidra Function API and computes
        derived fields like namespace and class name.
        """
        # Extract basic properties from Ghidra Function
        if self.function:
            self.name = self.function.getName()
            self.signature = self.function.getPrototypeString(False, False)
            self.address = self.function.getEntryPoint()
        else:
            # Handle None/invalid function case
            self.name = "<invalid>"
            self.signature = "<no signature>"
            self.address = None

        # Compute namespace-related fields
        self.namespace = self._extract_namespace()
        self.class_name = self._extract_class_name()

    @classmethod
    def from_function(
            cls,
            function: Optional[Function],
            qualified_name: Optional[str] = None
    ) -> 'FunctionInfo':
        """Factory method to create FunctionInfo from Ghidra Function.

        Args:
            function: Ghidra Function object to wrap
            qualified_name: Optional fully qualified name (e.g., "rLandInfo::load").
                          If None, uses function.getName()

        Returns:
            New FunctionInfo instance with computed properties

        Example:
            >>> info = FunctionInfo.from_function(func, "rLandInfo::load")
            >>> info = FunctionInfo.from_function(func)  # Uses func.getName()
        """
        if qualified_name is None and function is not None:
            qualified_name = function.getName()
        elif qualified_name is None:
            qualified_name = "<invalid>"

        return cls(
            function=function,
            qualified_name=qualified_name
        )

    def _extract_namespace(self) -> Optional[str]:
        """Extract namespace from qualified function name.

        Parses the qualified name to extract everything before the final
        component (the function name itself).

        Returns:
            Namespace string (e.g., "rLandInfo" from "rLandInfo::load"),
            or None if no namespace present

        Example:
            "rLandInfo::load" -> "rLandInfo"
            "rLandInfo::cLandInfo::getData" -> "rLandInfo::cLandInfo"
            "standalone_function" -> None
        """
        if AnalyzerConfig.NAMESPACE_SEPARATOR not in self.qualified_name:
            return None

        parts = self.qualified_name.split(AnalyzerConfig.NAMESPACE_SEPARATOR)
        if len(parts) <= 1:
            return None

        # Join all parts except the last (which is the function name)
        return AnalyzerConfig.NAMESPACE_SEPARATOR.join(parts[:-1])

    def _extract_class_name(self) -> Optional[str]:
        """Extract class name from qualified function name.

        For member functions, extracts the immediate containing class name
        (the second-to-last component).

        Returns:
            Class name string (e.g., "rLandInfo" from "rLandInfo::load"),
            or None if not a member function

        Example:
            "rLandInfo::load" -> "rLandInfo"
            "rLandInfo::cLandInfo::getData" -> "cLandInfo"
            "standalone_function" -> None
        """
        if AnalyzerConfig.NAMESPACE_SEPARATOR not in self.qualified_name:
            return None

        parts = self.qualified_name.split(AnalyzerConfig.NAMESPACE_SEPARATOR)
        if len(parts) <= 1:
            return None

        # Return the second-to-last part (immediate parent class)
        return parts[-2]

    def is_member_function(self) -> bool:
        """Check if this is a C++ member function.

        Returns:
            True if function has a namespace (is a member function),
            False for free functions
        """
        return self.namespace is not None

    def is_valid(self) -> bool:
        """Check if this FunctionInfo represents a valid function.

        Returns:
            True if underlying Ghidra Function exists, False otherwise
        """
        return self.function is not None

    def __str__(self) -> str:
        """String representation showing qualified name and address."""
        if self.address:
            return f"{self.qualified_name} @ {self.address}"
        return self.qualified_name

    def __repr__(self) -> str:
        """Developer representation with all fields."""
        return (
            f"FunctionInfo("
            f"qualified_name='{self.qualified_name}', "
            f"address={self.address}, "
            f"namespace='{self.namespace}', "
            f"valid={self.is_valid()})"
        )
