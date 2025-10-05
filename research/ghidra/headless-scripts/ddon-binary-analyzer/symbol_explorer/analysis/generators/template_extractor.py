# Template Parameter Extraction
#
# This module contains functionality for extracting and resolving
# template parameters from C++ type names.


from typing import List, Optional

from ghidra.program.model.data import DataType

from .type_discovery import TypeDiscoveryStrategy


class TemplateParameterExtractor:
    """Enhanced template parameter extraction using Ghidra's type information"""

    def __init__(self, type_discovery: TypeDiscoveryStrategy):
        self.type_discovery = type_discovery

    def extract_template_parameters(self, type_name: str) -> List[str]:
        """Extract template parameters from a type name"""
        # Find template parameters between < and >
        start = type_name.find('<')
        if start == -1:
            return []

        end = type_name.rfind('>')
        if end == -1 or end <= start:
            return []

        param_string = type_name[start + 1:end].strip()
        return self._parse_parameter_list(param_string)

    def resolve_template_parameters(self, type_name: str, context: Optional[DataType] = None) -> List[DataType]:
        """Extract and resolve template parameters to actual DataType objects"""
        param_names = self.extract_template_parameters(type_name)
        resolved_params = []

        for param_name in param_names:
            param_type = self.type_discovery.find_type(param_name, context)
            if param_type:
                resolved_params.append(param_type)

        return resolved_params

    def _parse_parameter_list(self, param_string: str) -> List[str]:
        """Parse comma-separated template parameters handling nested templates"""
        params = []
        current_param = ""
        bracket_depth = 0

        for char in param_string:
            if char == '<':
                bracket_depth += 1
            elif char == '>':
                bracket_depth -= 1
            elif char == ',' and bracket_depth == 0:
                if current_param.strip():
                    params.append(current_param.strip())
                current_param = ""
                continue
            current_param += char

        if current_param.strip():
            params.append(current_param.strip())

        return params
