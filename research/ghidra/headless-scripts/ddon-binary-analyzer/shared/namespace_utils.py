# Shared Namespace Utilities
# Common functions for parsing namespaces, function signatures, and type paths
# Used by both function analyzer and symbol explorer
#
# @author Sehkah
# @category ddon-research

import re
from typing import Optional, List

from ghidra.program.model.data import CategoryPath, DataTypePath, DataType


class NamespaceUtils:
    """Utilities for namespace and signature parsing across both analyzers.
    
    Provides centralized functions for parsing C++ namespaces, function signatures,
    type paths, and extracting function calls from decompiled code. Used by both
    the function analyzer and symbol explorer components.
    """

    # Regex patterns for function signature parsing
    QUALIFIED_NAME_PATTERN = re.compile(
        r'(?:__thiscall\s+)?([a-zA-Z_]\w*(?:::[a-zA-Z_]\w*)*)::[a-zA-Z_]\w*\s*\(')
    FUNCTION_CALL_PATTERN = re.compile(r'([a-zA-Z_]\w*(?:::[a-zA-Z_]\w*)*(?:<[^>]*>)?)\s*\(')

    # ========== Function Signature Parsing (used by function_analyzer) ==========

    @staticmethod
    def extract_namespace_from_signature(signature: str) -> Optional[str]:
        """Extract namespace from C++ function signature string.
        
        Parses function signatures to extract the namespace portion,
        filtering out type names and invalid namespace patterns.

        Args:
            signature: C++ function signature string to parse

        Returns:
            Namespace string if found and valid, None otherwise
        """
        if not signature:
            return None

        match = NamespaceUtils.QUALIFIED_NAME_PATTERN.search(signature)
        if match:
            namespace_part = match.group(1)
            # Validate namespace (not just a type)
            if len(namespace_part) > 2 and not namespace_part.startswith('u') and namespace_part != 'void':
                return namespace_part
        return None

    @staticmethod
    def extract_function_calls(decompiled_code: str) -> List[str]:
        """Extract function call identifiers from decompiled C/C++ code.
        
        Parses decompiled code to identify function calls, including
        namespaced functions and template instantiations.

        Args:
            decompiled_code: Decompiled C/C++ code string to analyze

        Returns:
            List of unique function call names
        """
        if not decompiled_code:
            return []

        function_calls = []
        matches = NamespaceUtils.FUNCTION_CALL_PATTERN.finditer(decompiled_code)
        for match in matches:
            call_name = match.group(1)
            if call_name not in function_calls:
                function_calls.append(call_name)

        return function_calls

    @staticmethod
    def is_namespace_related(text: str, namespace: str) -> bool:
        """Check if text contains namespace-related patterns

        Args:
            text: Text to search in
            namespace: Namespace to look for

        Returns:
            True if namespace-related content found
        """
        if not text or not namespace:
            return False

        return any([
            namespace in text,
            f"{namespace}::" in text,
            f"<{namespace}::" in text,
            f"<{namespace}" in text,
            f"{namespace}>" in text
        ])

    # ========== Ghidra DataType Path Parsing (used by symbol_explorer) ==========

    @staticmethod
    def get_category_path(data_type: DataType) -> Optional[CategoryPath]:
        """Get CategoryPath from DataType using Ghidra's built-in functionality

        Args:
            data_type: Ghidra DataType instance

        Returns:
            CategoryPath or None
        """
        if data_type is None:
            return None
        return data_type.getCategoryPath()

    @staticmethod
    def get_data_type_path(data_type: DataType) -> Optional[DataTypePath]:
        """Get DataTypePath using Ghidra's built-in functionality

        Args:
            data_type: Ghidra DataType instance

        Returns:
            DataTypePath or None
        """
        if data_type is None:
            return None
        return data_type.getDataTypePath()

    @staticmethod
    def is_dwarf_type(data_type: DataType) -> bool:
        """Check if type is from DWARF using CategoryPath

        Args:
            data_type: Ghidra DataType instance

        Returns:
            True if type is from DWARF debug info
        """
        if data_type is None:
            return False
        cat_path = data_type.getCategoryPath()
        if cat_path is None:
            return False
        path_str = cat_path.getPath()
        return "/DWARF/" in path_str or path_str.startswith("/DWARF")

    @staticmethod
    def extract_namespace_from_path(type_path: str) -> str:
        """Extract namespace from DWARF type path

        Args:
            type_path: DWARF type path string

        Returns:
            Namespace string (C++ style with ::)
        """
        if "/DWARF/" in type_path:
            # Handle DWARF paths like "/DWARF/rLandInfo.h/rLandInfo/cLandInfo"
            parts = type_path.split('/')
            dwarf_index = -1
            for i, part in enumerate(parts):
                if part == "DWARF":
                    dwarf_index = i
                    break

            if dwarf_index >= 0 and len(parts) > dwarf_index + 2:
                # Skip DWARF and .h file, collect namespace parts
                namespace_parts = []
                for i in range(dwarf_index + 2, len(parts) - 1):  # Exclude last part (type name)
                    if parts[i]:  # Skip empty parts
                        namespace_parts.append(parts[i])
                return "::".join(namespace_parts)

        # Fallback to generic path parsing
        if '/' in type_path:
            return '/'.join(type_path.split('/')[:-1])
        return ""

    @staticmethod
    def get_simple_name_from_path(type_path: str) -> str:
        """Get simple type name without namespace

        Args:
            type_path: Type path string

        Returns:
            Simple type name
        """
        if '/' in type_path:
            return type_path.split('/')[-1]
        return type_path

    @staticmethod
    def create_qualified_name(data_type: DataType) -> str:
        """Create C++ qualified name from DWARF path

        Args:
            data_type: Ghidra DataType instance

        Returns:
            Fully qualified C++ type name
        """
        if data_type is None:
            return "void"

        type_name = data_type.getName()
        namespace = NamespaceUtils.extract_namespace_from_path(data_type.getPathName())

        if namespace:
            return f"{namespace}::{type_name}"
        return type_name

    # ========== Namespace Path Utilities (Ghidra API) ==========

    @staticmethod
    def get_namespace_path_list(namespace) -> List[str]:
        """Get namespace path as list of components using Ghidra's built-in method.

        This uses Namespace.getPathList() which is more reliable than manual string parsing.

        Args:
            namespace: Ghidra Namespace instance

        Returns:
            List of namespace components (e.g., ['rLandInfo', 'cLandInfo'] for rLandInfo::cLandInfo)
        """
        if namespace is None:
            return []

        try:
            # Use Ghidra's built-in method - omits library names by default
            path_list = namespace.getPathList(False)  # False = omit library
            return list(path_list) if path_list else []
        except Exception:
            # Fallback to empty list
            return []

    @staticmethod
    def get_namespace_qualified_path(namespace, delimiter: str = "::") -> str:
        """Get fully qualified namespace path using Ghidra's built-in method.

        Args:
            namespace: Ghidra Namespace instance
            delimiter: Delimiter to use (default "::" for C++)

        Returns:
            Qualified namespace path string
        """
        if namespace is None:
            return ""

        path_components = NamespaceUtils.get_namespace_path_list(namespace)
        return delimiter.join(path_components) if path_components else ""

    @staticmethod
    def is_global_namespace(namespace) -> bool:
        """Check if namespace is the global namespace.

        Args:
            namespace: Ghidra Namespace instance

        Returns:
            True if global namespace
        """
        if namespace is None:
            return True

        try:
            return namespace.isGlobal()
        except Exception:
            return False
