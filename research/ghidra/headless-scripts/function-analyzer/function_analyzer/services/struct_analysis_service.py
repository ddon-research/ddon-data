# Struct Analysis Service - Unified service for struct and DWARF analysis
# Consolidates functionality from DataTypeService and DwarfFunctionAnalyzer

import logging
from typing import Dict, List, Optional, Set

from ghidra.program.model.data import DataType, Structure, Composite
from ghidra.program.model.listing import Program, Function


class StructAnalysisService:
    """Unified service for struct and DWARF analysis, eliminating redundancy"""

    def __init__(self, program: Program, logger: logging.Logger):
        self.program = program
        self.logger = logger
        self.data_type_manager = program.getDataTypeManager()
        self.symbol_table = program.getSymbolTable()

    def analyze_function_with_dwarf(self, function: Function) -> Dict:
        """Enhanced function analysis using DWARF information"""
        analysis = {
            'function_name': function.getName(),
            'signature': function.getSignature().getPrototypeString(),
            'namespace_info': self._extract_namespace_info(function),
            'parameter_types': self._analyze_parameters(function),
            'return_type_info': self._analyze_return_type(function),
            'related_structures': self.find_related_structures(function)
        }

        return analysis

    def _extract_namespace_info(self, function: Function) -> Dict[str, str]:
        """Extract comprehensive namespace information"""
        namespace_info = {
            'simple_name': function.getName(),
            'qualified_name': '',
            'parent_namespace': '',
            'calling_convention': function.getCallingConventionName()
        }

        # Use Ghidra's NamespaceUtils for proper namespace extraction
        parent_ns = function.getParentNamespace()
        if parent_ns and not parent_ns.isGlobal():
            namespace_info['parent_namespace'] = parent_ns.getName()
            namespace_info['qualified_name'] = parent_ns.getName() + "::" + function.getName()
        else:
            namespace_info['qualified_name'] = function.getName()

        return namespace_info

    def _analyze_parameters(self, function: Function) -> List[Dict]:
        """Analyze function parameters and their types"""
        parameters = []

        for param in function.getParameters():
            param_info = {
                'name': param.getName(),
                'type': param.getDataType().getName(),
                'size': param.getLength()
            }
            parameters.append(param_info)

        return parameters

    def _analyze_return_type(self, function: Function) -> Dict:
        """Analyze return type information"""
        return_type = function.getReturnType()
        return {
            'type': return_type.getName(),
            'size': return_type.getLength()
        }

    def find_related_structures(self, function: Function) -> List[DataType]:
        """Find structures related to a function's namespace"""
        namespace = self._extract_namespace_info(function)['parent_namespace']
        if not namespace:
            return []

        return self.get_related_datatypes(namespace)

    def get_struct_by_name(self, struct_name: str) -> Optional[Structure]:
        """Get Structure DataType by name, leveraging DWARF information"""
        # Search in all category paths
        for category in self.data_type_manager.getAllCategories():
            dt = self.data_type_manager.getDataType(category, struct_name)
            if dt and isinstance(dt, Structure):
                return dt
        return None

    def get_related_datatypes(self, namespace: str) -> List[DataType]:
        """Find all DataTypes related to a specific namespace/class"""
        related_types = []

        # Search through all categories for namespace matches
        for category in self.data_type_manager.getAllCategories():
            category_path = category.getCategoryPathName()
            if namespace.lower() in category_path.lower():
                for dt in self.data_type_manager.getDataTypes(category):
                    related_types.append(dt)

        return related_types

    def analyze_struct_dependencies(self, struct: Structure) -> Dict[str, Set[str]]:
        """Analyze dependencies between struct types"""
        dependencies = {
            'contains': set(),
            'contained_by': set(),
            'references': set()
        }

        # Analyze components
        for component in struct.getComponents():
            comp_dt = component.getDataType()
            if isinstance(comp_dt, Composite):
                dependencies['contains'].add(comp_dt.getName())

        # Find structs that contain this struct
        for dt in self.data_type_manager.getAllDataTypes():
            if isinstance(dt, Structure) and dt != struct:
                for comp in dt.getComponents():
                    if comp.getDataType().getName() == struct.getName():
                        dependencies['contained_by'].add(dt.getName())

        return dependencies

    def get_dwarf_type_info(self, data_type: DataType) -> Dict[str, str]:
        """Extract DWARF debugging information from DataType"""
        info = {
            'name': data_type.getName(),
            'category': str(data_type.getCategoryPath()),
            'size': str(data_type.getLength()),
            'source': 'Unknown'
        }

        # Check if this came from DWARF information
        description = data_type.getDescription()
        if description and 'DWARF' in description:
            info['source'] = 'DWARF'

        return info
