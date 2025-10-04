# Namespace Utilities - Functions for parsing namespaces and function signatures
# Provides utilities for extracting and working with C++ namespaces

import re
from typing import Optional, List


class NamespaceUtils:
    """Utilities for namespace and signature parsing"""

    # Consolidated regex patterns for better performance
    QUALIFIED_NAME_PATTERN = re.compile(
        r'(?:__thiscall\s+)?([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)::[a-zA-Z_][a-zA-Z0-9_]*\s*\(')
    FUNCTION_CALL_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*(?:<[^>]*>)?)\s*\(')

    @staticmethod
    def extract_namespace_from_signature(signature: str) -> Optional[str]:
        """Extract namespace from function signature using consolidated pattern"""
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
        """Extract function calls from decompiled code"""
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
