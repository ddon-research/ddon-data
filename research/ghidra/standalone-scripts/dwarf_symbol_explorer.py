# DWARF Symbol Explorer for Ghidra - C++ Definition Generator
#
# PROBLEM: Analyzing complex C++ binaries requires understanding struct hierarchies, inheritance
# relationships, and template parameters. DWARF symbols contain this information but Ghidra presents
# them as raw data structures without proper C++ syntax or topological ordering.
#
# SOLUTION: Automatically discovers and generates compilable C++ definitions from DWARF symbols,
# converting Ghidra's internal representation to properly formatted C++ code with inheritance syntax,
# namespace resolution, and dependency ordering.
#
# CORE FUNCTIONALITY:
# - Auto-detects symbols from GUI selection or accepts manual symbol names
# - Converts "super_ClassName" fields to proper inheritance syntax
# - Extracts namespace information from DWARF paths
# - Discovers and processes template parameters recursively
# - Topologically sorts definitions to resolve dependencies
# - Generates compilable C++ struct/class definitions
#
# INPUT: Symbol name (e.g., "rLandInfo") or GUI selection
# OUTPUT: Complete C++ definitions with proper inheritance and ordering
#
# USAGE:
# 1. Load ELF with DWARF symbols in Ghidra
# 2. Import DWARF symbols (Analysis → Auto Analyze → DWARF)
# 3. Navigate to a symbol or run script for manual entry
# 4. View generated C++ definitions with proper inheritance
#
# EXAMPLE OUTPUT:
# ```cpp
# struct MtObject {
#   _func_int** _vptr$MtObject;
# };
# 
# struct rLandInfo : public cResource {
#   MtTypedArray<rLandInfo::cLandInfo> mLandInfo;
# };
# ```
#
# @author Sehkah
# @category ddon-research
# @keybinding SHIFT-D
# @menupath 
# @toolbar 
# @runtime PyGhidra

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Set, Dict, List

from ghidra.program.model.data import (
    StructureDataType,
    UnionDataType,
    EnumDataType,
    ArrayDataType,
    PointerDataType,
    FunctionDefinitionDataType,
    DataType,
    DataTypeManager,
    TypedefDataType
)
from ghidra.program.model.listing import Program

# Get current program
currentProgram: Program = getCurrentProgram()


class ExplorerConfig:
    """Centralized configuration constants for symbol exploration and C++ generation"""
    
    # Logging settings
    DEBUG_ENABLED = True
    LOG_LEVEL = "DEBUG"
    
    # Output formatting
    OUTPUT_WIDTH = 80
    INDENT_SIZE = 4
    MAX_LINE_LENGTH = 100
    
    # Type filtering and formatting
    BUILTIN_TYPES = frozenset({
        'void', 'char', 'short', 'int', 'long', 'float', 'double',
        'signed', 'unsigned', 'bool', 'wchar_t', 'char16_t', 'char32_t',
        'int8_t', 'int16_t', 'int32_t', 'int64_t',
        'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
        'size_t', 'ptrdiff_t', 'nullptr_t'
    })
    
    MAX_INHERITANCE_DEPTH = 10
    MAX_TEMPLATE_PARAMS = 20
    
    # Search patterns
    IGNORED_NAMESPACES = frozenset({'std', '__gnu_cxx', '__cxxabiv1'})
    DEFAULT_TEMPLATE_FILTER = ".*<.*>.*"
    
    # Color codes for terminal output
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'end': '\033[0m'
    }


class SymbolExplorationError(Exception):
    """Base exception for symbol exploration operations"""
    pass


class TypeProcessingError(SymbolExplorationError):
    """Raised when type processing fails"""
    pass


class NamespaceExtractionError(SymbolExplorationError):
    """Raised when namespace extraction fails"""
    pass


class CodeGenerationError(SymbolExplorationError):
    """Raised when C++ code generation fails"""
    pass


class TypeUtils:
    """Utility functions for common type operations"""
    
    @staticmethod
    def is_composite_type(data_type: Optional[DataType]) -> bool:
        """Check if data type is a composite type (struct/union)"""
        if data_type is None:
            return False
        return hasattr(data_type, 'getNumComponents') and hasattr(data_type, 'getComponent')
    
    @staticmethod
    def is_builtin_type(type_name: str) -> bool:
        """Check if type name represents a built-in type"""
        return type_name in ExplorerConfig.BUILTIN_TYPES
    
    @staticmethod
    def get_type_path(data_type: Optional[DataType]) -> str:
        """Safely get type path name"""
        return data_type.getPathName() if data_type else "None"
    
    @staticmethod
    def get_type_name(data_type: Optional[DataType]) -> str:
        """Safely get type name"""
        return data_type.getName() if data_type else "None"
    
    @staticmethod
    def get_type_size(data_type: Optional[DataType]) -> int:
        """Safely get type size"""
        return data_type.getLength() if data_type else 0
    
    @staticmethod
    def is_template_type(type_name: str) -> bool:
        """Check if type name contains template parameters"""
        return '<' in type_name and '>' in type_name


class NamespaceUtils:
    """Utility functions for namespace operations"""
    
    @staticmethod
    def should_ignore_namespace(namespace: str) -> bool:
        """Check if namespace should be ignored"""
        return namespace in ExplorerConfig.IGNORED_NAMESPACES
    
    @staticmethod
    def extract_namespace(type_path: str) -> str:
        """Extract namespace from type path"""
        if '/' in type_path:
            return '/'.join(type_path.split('/')[:-1])
        return ""
    
    @staticmethod
    def get_simple_name(type_path: str) -> str:
        """Get simple type name without namespace"""
        if '/' in type_path:
            return type_path.split('/')[-1]
        return type_path


class LoggingConfig:
    """Centralized logging configuration"""
    
    @staticmethod
    def setup_logger(name: str = "dwarf_symbol_explorer") -> logging.Logger:
        """Setup and return configured logger"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        # Clear old handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add Ghidra console handler
        handler = GhidraConsoleHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger


class GhidraConsoleHandler(logging.Handler):
    """Custom logging handler for Ghidra console output"""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            print(msg)
        except Exception:
            self.handleError(record)


    """Centralized logging configuration"""
    
    @staticmethod
    def setup_logger(name: str = "dwarf_symbol_explorer") -> logging.Logger:
        """Setup and return configured logger"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        # Clear old handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add Ghidra console handler
        handler = GhidraConsoleHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger


@dataclass
class DataTypeInfo:
    """Value object for data type information with improved type safety"""
    
    data_type: Optional[DataType]
    name: str
    path: str
    size: int
    type_class: str
    
    @classmethod
    def from_data_type(cls, data_type: Optional[DataType]) -> 'DataTypeInfo':
        """Factory method to create DataTypeInfo from a DataType"""
        if data_type is None:
            return cls(
                data_type=None,
                name="None",
                path="None", 
                size=0,
                type_class="None"
            )
        
        return cls(
            data_type=data_type,
            name=data_type.getName(),
            path=data_type.getPathName(),
            size=data_type.getLength(),
            type_class=data_type.__class__.__name__
        )


class TypeVisitor(ABC):
    """Abstract base class for type visitors"""
    
    @abstractmethod
    def visit_structure(self, struct_type: StructureDataType) -> None:
        pass
    
    @abstractmethod
    def visit_union(self, union_type: UnionDataType) -> None:
        pass
    
    @abstractmethod
    def visit_enum(self, enum_type: EnumDataType) -> None:
        pass
    
    @abstractmethod
    def visit_array(self, array_type: ArrayDataType) -> None:
        pass
    
    @abstractmethod
    def visit_pointer(self, pointer_type: PointerDataType) -> None:
        pass
    
    @abstractmethod
    def visit_function(self, func_type: FunctionDefinitionDataType) -> None:
        pass
    
    @abstractmethod
    def visit_typedef(self, typedef_type: TypedefDataType) -> None:
        pass
    
    @abstractmethod
    def visit_primitive(self, data_type: DataType) -> None:
        pass


class SymbolSearchService:
    """Service for searching symbols in the data type manager"""
    
    def __init__(self, data_type_manager: DataTypeManager, logger: logging.Logger):
        self.data_type_manager = data_type_manager
        self.logger = logger
    
    def find_symbol_by_name(self, symbol_name: str, exact_only: bool = False) -> Optional[DataType]:
        """
        Search for a symbol by name across all data types.
        
        Args:
            symbol_name: The name of the symbol to search for
            exact_only: If True, only return exact matches (no partial matches)
        
        Returns:
            The first matching DataType found, or None if no match
        """
        search_type = "exact symbol" if exact_only else "symbol"
        self.logger.debug(f"Searching for {search_type}: '{symbol_name}'")
        
        # Get all data types from the manager
        all_data_types = self.data_type_manager.getAllDataTypes()
        
        # Track potential matches
        exact_matches = []
        partial_matches = []
        dwarf_exact_matches = []
        
        for data_type in all_data_types:
            dt_name = data_type.getName()
            dt_path = data_type.getPathName()
            
            # Check for exact name match
            if dt_name == symbol_name:
                exact_matches.append(data_type)
                # Prefer DWARF matches
                if "/DWARF/" in dt_path:
                    dwarf_exact_matches.append(data_type)
                    
            # Check for partial matches (only if not exact_only mode)
            elif not exact_only and symbol_name.lower() in dt_name.lower():
                partial_matches.append(data_type)
        
        # Log search results
        self.logger.debug(f"Search results:")
        self.logger.debug(f"  Exact matches: {len(exact_matches)}")
        self.logger.debug(f"  DWARF exact matches: {len(dwarf_exact_matches)}")
        if not exact_only:
            self.logger.debug(f"  Partial matches: {len(partial_matches)}")
        
        # Return the best match in priority order
        result = self._select_best_match(dwarf_exact_matches, exact_matches, 
                                       partial_matches if not exact_only else [])
        
        if result:
            self.logger.debug(f"Selected match: {result.getName()} at {result.getPathName()}")
        else:
            match_type = "exact matches" if exact_only else "matches"
            self.logger.debug(f"No {match_type} found for '{symbol_name}'")
        
        return result
    
    def find_nested_symbol(self, symbol_name: str) -> Optional[DataType]:
        """Find a symbol that might be nested in namespaces"""
        self.logger.debug(f"Searching for nested symbol: '{symbol_name}'")
        
        # Extract the class name (part after last ::)
        if '::' in symbol_name:
            class_name = symbol_name.split('::')[-1]
            namespace_parts = symbol_name.split('::')[:-1]
        else:
            class_name = symbol_name
            namespace_parts = []
            
        # Try direct search first
        result = self.find_symbol_by_name(class_name, exact_only=True)
        if result:
            return result
        
        # More comprehensive search logic here...
        return self._comprehensive_nested_search(symbol_name, class_name, namespace_parts)
    
    def _select_best_match(self, dwarf_matches: List[DataType], 
                         exact_matches: List[DataType], 
                         partial_matches: List[DataType]) -> Optional[DataType]:
        """Select the best match from available options"""
        if dwarf_matches:
            return dwarf_matches[0]
        elif exact_matches:
            return exact_matches[0]
        elif partial_matches:
            return partial_matches[0]
        return None
    
    def _comprehensive_nested_search(self, full_name: str, class_name: str, 
                                   namespace_parts: List[str]) -> Optional[DataType]:
        """Perform comprehensive search for nested symbols"""
        # Implementation details...
        all_data_types = self.data_type_manager.getAllDataTypes()
        matches = []
        
        for data_type in all_data_types:
            if data_type.getName() == class_name:
                dt_path = data_type.getPathName()
                if "/DWARF/" in dt_path:
                    matches.append(data_type)
        
        return matches[0] if matches else None


class CppTypeFormatter:
    """Formatter for generating C++ type definitions"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger
        self.type_mapping = {
            'bool': 'bool',
            'char': 'char',
            'uchar': 'unsigned char',
            'short': 'short',
            'ushort': 'unsigned short', 
            'int': 'int',
            'uint': 'unsigned int',
            'long': 'long',
            'ulong': 'unsigned long',
            'longlong': 'long long',
            'ulonglong': 'unsigned long long',
            'float': 'float',
            'double': 'double',
            'void': 'void'
        }
    
    def get_cpp_type_name(self, data_type: DataType) -> str:
        """Convert Ghidra data type to C++ type name"""
        if data_type is None:
            return "void"
            
        type_name = data_type.getName()
        class_name = data_type.__class__.__name__
        
        # Handle pointers
        if "PointerDB" in class_name or isinstance(data_type, PointerDataType):
            if hasattr(data_type, 'getDataType'):
                referenced_type = data_type.getDataType()
                if referenced_type is not None:
                    base_type = self.get_cpp_type_name(referenced_type)
                    return f"{base_type}*"
            return "void*"
            
        # Handle arrays
        if "Array" in class_name or isinstance(data_type, ArrayDataType):
            if hasattr(data_type, 'getDataType') and hasattr(data_type, 'getNumElements'):
                element_type = self.get_cpp_type_name(data_type.getDataType())
                return f"{element_type}[{data_type.getNumElements()}]"
            return type_name
            
        # Handle typedefs
        if "TypedefDB" in class_name or isinstance(data_type, TypedefDataType):
            if hasattr(data_type, 'getDataType'):
                base_type = data_type.getDataType()
                # For common typedefs, use the typedef name
                if type_name in ['u8', 'u16', 'u32', 'u64', 's8', 's16', 's32', 's64']:
                    return type_name
                # For others, try to get the base type
                return self.get_cpp_type_name(base_type)
                
        # Handle function pointers
        if isinstance(data_type, FunctionDefinitionDataType):
            return_type = self.get_cpp_type_name(data_type.getReturnType())
            params = data_type.getArguments()
            param_types = [self.get_cpp_type_name(param.getDataType()) for param in params]
            return f"{return_type}(*)({', '.join(param_types)})"
            
        # Handle basic types
        return self.type_mapping.get(type_name, type_name)
    
    def get_qualified_struct_name(self, data_type: DataType) -> str:
        """Get qualified struct name with namespace from DWARF path"""
        if data_type is None:
            return "void"
            
        type_name = data_type.getName()
        type_path = data_type.getPathName()
        
        # For DWARF types, try to extract namespace information from the path
        if "/DWARF/" in type_path:
            # Extract namespace from path like "/DWARF/rLandInfo.h/rLandInfo/cLandInfo"
            path_parts = type_path.split('/')
            
            # Find the parts after the header file
            dwarf_index = -1
            for i, part in enumerate(path_parts):
                if part == "DWARF":
                    dwarf_index = i
                    break
            
            if dwarf_index >= 0 and len(path_parts) > dwarf_index + 2:
                # Skip DWARF and the .h file, collect namespace parts
                namespace_parts = []
                for i in range(dwarf_index + 2, len(path_parts)):
                    part = path_parts[i]
                    # Skip empty parts
                    if part:
                        namespace_parts.append(part)
                
                if len(namespace_parts) > 1:
                    # The last part should be the same as type_name, but the preceding parts are namespace
                    # Join with :: to create qualified name like "rLandInfo::cLandInfo"
                    qualified_name = "::".join(namespace_parts)
                    if self.logger:
                        self.logger.debug(f"Qualified name for {type_name}: {qualified_name} (from path: {type_path})")
                    return qualified_name
                elif len(namespace_parts) == 1:
                    # Single part, might be at root level
                    if namespace_parts[0] == type_name:
                        # It's a root level type
                        if self.logger:
                            self.logger.debug(f"Root level type: {type_name}")
                        return type_name
                    else:
                        # Unexpected structure
                        if self.logger:
                            self.logger.debug(f"Unexpected single namespace part for {type_name}: {namespace_parts[0]}")
                        return type_name
        
        # Fallback to simple name if no namespace found
        if self.logger:
            self.logger.debug(f"Using simple name for {type_name} (no namespace found from path: {type_path})")
        return type_name


class CppDefinitionGenerator:
    """Generator for complete C++ definitions"""
    
    def __init__(self, formatter: CppTypeFormatter, logger: logging.Logger, search_service: 'SymbolSearchService'):
        self.formatter = formatter
        self.logger = logger
        self.search_service = search_service
        self.processed_types: Set[str] = set()
        self.type_definitions: Dict[str, str] = {}
        self.template_extractor = TemplateParameterExtractor()
    
    def generate_full_cpp_definitions(self, data_type: DataType) -> str:
        """Generate complete C++ definitions for a type and all its nested types"""
        self.processed_types.clear()
        self.type_definitions.clear()
        
        try:
            nested_types = self._collect_nested_types(data_type)
            self._generate_nested_definitions(nested_types, data_type)
            main_definition = self._generate_single_definition(data_type)
            
            return self._format_complete_output(main_definition)
            
        except Exception as e:
            raise CodeGenerationError(f"Error generating C++ definitions: {e}") from e
    
    def _collect_nested_types(self, data_type: DataType) -> Set[str]:
        """Recursively collect all nested types"""
        nested_types = set()
        visited_paths = set()
        
        def collect_recursive(dt):
            if dt is None or TypeUtils.get_type_path(dt) in visited_paths:
                return
            
            visited_paths.add(TypeUtils.get_type_path(dt))
            self.logger.debug(f"Collecting nested types from: {TypeUtils.get_type_name(dt)} at {TypeUtils.get_type_path(dt)}")
            
            self._collect_template_parameter_types(dt, collect_recursive, visited_paths)
            self._collect_composite_member_types(dt, collect_recursive, nested_types)
        
        collect_recursive(data_type)
        return nested_types
    
    def _collect_template_parameter_types(self, data_type: DataType, collect_fn, visited_paths: Set[str]):
        """Collect types from template parameters"""
        template_params = self.template_extractor.extract_template_parameters(data_type.getName())
        self.logger.debug(f"Extracted template parameters: {template_params}")
        
        for param in template_params:
            self.logger.debug(f"Processing template parameter: '{param}'")
            param_type = self._find_template_parameter_type(param)
            
            if param_type and param_type.getPathName() not in visited_paths:
                self.logger.debug(f"Found template parameter type: {param_type.getName()} at {param_type.getPathName()}")
                collect_fn(param_type)
            else:
                self._log_template_parameter_status(param, param_type)
    
    def _collect_composite_member_types(self, data_type: DataType, collect_fn, nested_types: Set[str]):
        """Collect types from composite type members"""
        if not TypeUtils.is_composite_type(data_type):
            return
            
        try:
            num_components = data_type.getNumComponents()
            if num_components > 0:
                nested_types.add(data_type.getPathName())
                
                for i in range(num_components):
                    component = data_type.getComponent(i)
                    field_type = component.getDataType()
                    collect_fn(field_type)
                    
                    # Handle pointer/array element types
                    if hasattr(field_type, 'getDataType'):
                        collect_fn(field_type.getDataType())
                        
        except Exception as e:
            self.logger.debug(f"Error processing composite type {data_type.getName()}: {e}")
    
    def _log_template_parameter_status(self, param: str, param_type: Optional[DataType]):
        """Log the status of template parameter resolution"""
        if param_type is None:
            self.logger.debug(f"Could not find template parameter type: '{param}'")
        else:
            self.logger.debug(f"Template parameter type already visited: {param_type.getPathName()}")
    
    def _find_template_parameter_type(self, param_name: str) -> Optional[DataType]:
        """Find a template parameter type, handling namespace variations"""
        self.logger.debug(f"Searching for template parameter: '{param_name}'")
        
        # Use the search service to find nested symbols
        return self.search_service.find_nested_symbol(param_name)
    
    def _generate_nested_definitions(self, nested_types: Set[str], main_type: DataType):
        """Generate definitions for all nested types"""
        # Find the actual data type objects for all nested type paths
        all_data_types = {}
        dtm = main_type.getDataTypeManager() if main_type else None
        if dtm:
            for dt in dtm.getAllDataTypes():
                all_data_types[dt.getPathName()] = dt
        
        # Generate definitions for all nested types first (dependencies)
        for type_path in nested_types:
            nested_type = all_data_types.get(type_path)
            if nested_type and nested_type.getPathName() != main_type.getPathName():
                try:
                    definition = self._generate_single_definition(nested_type)
                    # Use qualified name as key for consistency
                    type_name = self.formatter.get_qualified_struct_name(nested_type)
                    if type_name not in self.type_definitions:  # Avoid duplicates by name
                        self.type_definitions[type_name] = definition
                        self.logger.debug(f"Generated definition for nested type: {type_name}")
                except Exception as e:
                    self.logger.debug(f"Error generating definition for {nested_type.getName()}: {e}")
    
    def _generate_single_definition(self, data_type: DataType) -> str:
        """Generate C++ definition for a single type"""
        if data_type is None:
            return "void"
            
        if TypeUtils.is_composite_type(data_type):
            return self._generate_composite_definition(data_type)
        else:
            return self.formatter.get_cpp_type_name(data_type)
    
    def _generate_composite_definition(self, data_type: DataType) -> str:
        """Generate definition for composite types (struct/union)"""
        num_components = data_type.getNumComponents()
        qualified_name = self.formatter.get_qualified_struct_name(data_type)
        
        # Parse inheritance and regular fields
        base_classes, regular_fields = self._parse_composite_members(data_type, num_components)
        
        # Generate definition based on type
        if 'Union' in data_type.__class__.__name__:
            return self._generate_union_definition(qualified_name, data_type, num_components)
        else:
            return self._generate_struct_definition(qualified_name, base_classes, regular_fields, data_type)
    
    def _parse_composite_members(self, data_type: DataType, num_components: int) -> tuple:
        """Parse composite type members into base classes and regular fields"""
        base_classes = []
        regular_fields = []
        
        if num_components > 0:
            for i in range(num_components):
                component = data_type.getComponent(i)
                field_name = component.getFieldName() or f"field_{i}"
                field_type = component.getDataType()
                cpp_type = self.formatter.get_cpp_type_name(field_type)
                
                if self._is_base_class_field(field_name, component.getOffset()):
                    base_class_type = self._extract_base_class_type(field_name, field_type, cpp_type)
                    base_classes.append(base_class_type)
                    self.logger.debug(f"Detected base class: {base_class_type} from field {field_name}")
                else:
                    regular_fields.append({
                        'name': field_name,
                        'type': cpp_type,
                        'offset': component.getOffset(),
                        'size': component.getLength()
                    })
        
        return base_classes, regular_fields
    
    def _is_base_class_field(self, field_name: str, offset: int) -> bool:
        """Check if field represents a base class (super_ prefix and at offset 0)"""
        return field_name.startswith("super_") and offset == 0
    
    def _extract_base_class_type(self, field_name: str, field_type: DataType, cpp_type: str) -> str:
        """Extract base class type name from field information"""
        # Use the actual field type name instead of the field name for consistency
        if hasattr(field_type, 'getNumComponents'):
            return self.formatter.get_qualified_struct_name(field_type)
        return cpp_type
    
    def _generate_union_definition(self, qualified_name: str, data_type: DataType, num_components: int) -> str:
        """Generate union definition (unions don't support inheritance)"""
        definition = f"union {qualified_name} {{\n"
        
        if num_components > 0:
            for i in range(num_components):
                component = data_type.getComponent(i)
                field_name = component.getFieldName() or f"field_{i}"
                field_type = component.getDataType()
                cpp_type = self.formatter.get_cpp_type_name(field_type)
                definition += f"  {cpp_type} {field_name};  // offset: {component.getOffset()}, size: {component.getLength()}\n"
        
        definition += f"}};  // Total size: {data_type.getLength()} bytes"
        return definition
    
    def _generate_struct_definition(self, qualified_name: str, base_classes: List[str], regular_fields: List[dict], data_type: DataType) -> str:
        """Generate struct definition with inheritance support"""
        if base_classes:
            inheritance_list = ", ".join(f"public {base_class}" for base_class in base_classes)
            definition = f"struct {qualified_name} : {inheritance_list} {{\n"
        else:
            definition = f"struct {qualified_name} {{\n"
        
        # Add regular fields
        if regular_fields:
            for field in regular_fields:
                definition += f"  {field['type']} {field['name']};  // offset: {field['offset']}, size: {field['size']}\n"
        elif not base_classes:
            definition += "  // Empty structure\n"
        
        definition += f"}};  // Total size: {data_type.getLength()} bytes"
        return definition
    
    def _format_complete_output(self, main_definition: str) -> str:
        """Format the complete output with nested types"""
        definitions = []
        
        if self.type_definitions:
            definitions.append("// Nested type definitions:")
            # Sort types topologically to ensure base classes come before derived classes
            sorted_types = self._topological_sort_types(self.type_definitions)
            for type_name in sorted_types:
                definitions.append("")
                definitions.append(self.type_definitions[type_name])
            definitions.append("")
        
        definitions.append("// Main type definition:")
        definitions.append(main_definition)
        
        return "\n".join(definitions)
    
    def _topological_sort_types(self, type_definitions: Dict[str, str]) -> List[str]:
        """Sort types topologically so base classes come before derived classes"""
        dependencies = self._build_type_dependency_graph(type_definitions)
        return self._kahn_topological_sort(dependencies, set(type_definitions.keys()))
    
    def _build_type_dependency_graph(self, type_definitions: Dict[str, str]) -> Dict[str, List[str]]:
        """Build dependency graph from type definitions"""
        dependencies = {}
        all_types = set(type_definitions.keys())
        
        for type_name, definition in type_definitions.items():
            dependencies[type_name] = self._extract_base_class_dependencies(definition, all_types)
            
        return dependencies
    
    def _extract_base_class_dependencies(self, definition: str, all_types: Set[str]) -> List[str]:
        """Extract base class dependencies from a type definition"""
        base_classes = []
        
        if ": public " in definition:
            inheritance_part = definition.split(": public ", 1)[1]
            inheritance_part = inheritance_part.split(" {", 1)[0]
            
            # Handle multiple inheritance (comma-separated)
            raw_base_classes = [base.strip() for base in inheritance_part.split(",")]
            
            for base_class in raw_base_classes:
                # Clean up the base class name (remove "public " prefix if any)
                base_class = base_class.replace("public ", "").strip()
                if base_class in all_types:
                    base_classes.append(base_class)
                    self.logger.debug(f"Dependency: extracted base class {base_class}")
        
        return base_classes
    
    def _kahn_topological_sort(self, dependencies: Dict[str, List[str]], all_types: Set[str]) -> List[str]:
        """Perform topological sort using Kahn's algorithm"""
        # Count incoming edges (dependencies)
        in_degree = {type_name: 0 for type_name in all_types}
        for type_name in dependencies:
            for base_class in dependencies[type_name]:
                in_degree[type_name] += 1
        
        # Start with nodes that have no dependencies
        queue = [type_name for type_name in all_types if in_degree[type_name] == 0]
        sorted_types = []
        
        while queue:
            queue.sort()  # Ensure consistent ordering for types at same level
            current = queue.pop(0)
            sorted_types.append(current)
            
            # Remove this node's effect on other nodes
            self._update_dependencies_after_node_removal(current, dependencies, in_degree, queue)
        
        # Handle circular dependencies
        return self._handle_circular_dependencies(sorted_types, all_types)
    
    def _update_dependencies_after_node_removal(self, current: str, dependencies: Dict[str, List[str]], 
                                               in_degree: Dict[str, int], queue: List[str]):
        """Update in-degree counts after removing a node from the graph"""
        for type_name in dependencies:
            if current in dependencies[type_name]:
                in_degree[type_name] -= 1
                if in_degree[type_name] == 0:
                    queue.append(type_name)
    
    def _handle_circular_dependencies(self, sorted_types: List[str], all_types: Set[str]) -> List[str]:
        """Handle circular dependencies by adding remaining types in alphabetical order"""
        if len(sorted_types) != len(all_types):
            remaining_types = all_types - set(sorted_types)
            self.logger.warning(f"Circular dependencies detected among: {remaining_types}")
            sorted_types.extend(sorted(remaining_types))
        
        self.logger.debug(f"Topological sort result: {sorted_types}")
        return sorted_types


class TemplateParameterExtractor:
    """Utility class for extracting template parameters from type names"""
    
    def extract_template_parameters(self, type_name: str) -> List[str]:
        """Extract template parameters from a type name like MtTypedArray<rLandInfo::cLanddebug>"""
        template_params = []
        
        # Find template parameters between < and >
        start = type_name.find('<')
        if start == -1:
            return template_params
            
        end = type_name.rfind('>')
        if end == -1 or end <= start:
            return template_params
            
        # Extract the parameter string
        param_string = type_name[start + 1:end].strip()
        
        # Split by comma, handling nested templates
        params = []
        current_param = ""
        bracket_depth = 0
        
        for char in param_string:
            if char == '<':
                bracket_depth += 1
            elif char == '>':
                bracket_depth -= 1
            elif char == ',' and bracket_depth == 0:
                params.append(current_param.strip())
                current_param = ""
                continue
            current_param += char
            
        if current_param.strip():
            params.append(current_param.strip())
            
        return params


class TypeExplorationVisitor(TypeVisitor):
    """Concrete visitor for exploring and logging type details"""
    
    def __init__(self, logger: logging.Logger, formatter: CppTypeFormatter):
        self.logger = logger
        self.formatter = formatter
        self.indent_level = 0
        self.visited_types: Set[str] = set()
    
    def visit_structure(self, struct_type: StructureDataType) -> None:
        self._visit_composite("Structure", struct_type)
    
    def visit_union(self, union_type: UnionDataType) -> None:
        self._visit_composite("Union", union_type)
    
    def visit_enum(self, enum_type: EnumDataType) -> None:
        self.logger.debug(f"Enum: {enum_type.getName()}")
        self._explore_enum_details(enum_type)
    
    def visit_array(self, array_type: ArrayDataType) -> None:
        self.logger.debug(f"Array: {array_type.getName()}")
        self._explore_array_details(array_type)
    
    def visit_pointer(self, pointer_type: PointerDataType) -> None:
        self.logger.debug(f"Pointer: {pointer_type.getName()}")
        self._explore_pointer_details(pointer_type)
    
    def visit_function(self, func_type: FunctionDefinitionDataType) -> None:
        self.logger.debug(f"Function: {func_type.getName()}")
        self._explore_function_details(func_type)
    
    def visit_typedef(self, typedef_type: TypedefDataType) -> None:
        self.logger.debug(f"Typedef: {typedef_type.getName()}")
        self._explore_typedef_details(typedef_type)
    
    def visit_primitive(self, data_type: DataType) -> None:
        self.logger.debug(f"Primitive type: {data_type.getName()} (size: {data_type.getLength()} bytes)")
    
    def _visit_composite(self, type_name: str, composite_type) -> None:
        """Common logic for visiting composite types"""
        type_key = composite_type.getPathName()
        if type_key in self.visited_types:
            self.logger.debug(f"(Already visited: {composite_type.getName()})")
            return
            
        self.visited_types.add(type_key)
        
        num_components = composite_type.getNumComponents()
        self.logger.debug(f"{type_name}: {composite_type.getName()}")
        self.logger.debug(f"Components: {num_components}")
        
        if num_components == 0:
            self.logger.debug("(Empty structure)")
            return
        
        self.indent_level += 1
        
        for i in range(num_components):
            component = composite_type.getComponent(i)
            self._explore_component(component, i)
            
        self.indent_level -= 1
    
    def _explore_component(self, component, index: int) -> None:
        """Explore a single component of a composite type"""
        field_name = component.getFieldName() or "(unnamed)"
        data_type = component.getDataType()
        offset = component.getOffset()
        length = component.getLength()
        
        indent = "  " * self.indent_level
        self.logger.debug(f"{indent}Field {index}: {field_name}")
        self.logger.debug(f"{indent}  Offset: {offset} bytes")
        self.logger.debug(f"{indent}  Size: {length} bytes")
        self.logger.debug(f"{indent}  Type: {data_type.getName()} ({data_type.__class__.__name__})")
        
        # Recursively explore the field's type using the visitor pattern
        type_dispatcher = TypeDispatcher(self)
        type_dispatcher.dispatch(data_type)
    
    def _explore_enum_details(self, enum_type: EnumDataType) -> None:
        """Explore enumeration details"""
        values = enum_type.getValues()
        names = enum_type.getNames()
        
        self.logger.debug(f"Enumeration values: ({len(values)} total)")
        
        self.indent_level += 1
        for i, (name, value) in enumerate(zip(names, values)):
            indent = "  " * self.indent_level
            self.logger.debug(f"{indent}{name} = {value} (0x{value & 0xFFFFFFFF:x})")
            if i >= 20:  # Limit output for very large enums
                remaining = len(values) - i - 1
                if remaining > 0:
                    self.logger.debug(f"{indent}... and {remaining} more values")
                break
        self.indent_level -= 1
    
    def _explore_array_details(self, array_type: ArrayDataType) -> None:
        """Explore array type details"""
        element_type = array_type.getDataType()
        element_count = array_type.getNumElements()
        element_size = element_type.getLength()
        
        self.logger.debug("Array details:")
        self.logger.debug(f"  Element count: {element_count}")
        self.logger.debug(f"  Element size: {element_size} bytes")
        self.logger.debug(f"  Element type: {element_type.getName()}")
        
        # Explore the element type if it's complex
        if isinstance(element_type, (StructureDataType, UnionDataType, EnumDataType)):
            self.logger.debug("Element type details:")
            self.indent_level += 1
            type_dispatcher = TypeDispatcher(self)
            type_dispatcher.dispatch(element_type)
            self.indent_level -= 1
    
    def _explore_pointer_details(self, pointer_type: PointerDataType) -> None:
        """Explore pointer type details"""
        referenced_type = pointer_type.getDataType()
        if referenced_type is not None:
            self.logger.debug(f"Points to: {referenced_type.getName()} ({referenced_type.__class__.__name__})")
            
            # Explore referenced type if it's complex
            if isinstance(referenced_type, (StructureDataType, UnionDataType, EnumDataType)):
                self.logger.debug("Referenced type details:")
                self.indent_level += 1
                type_dispatcher = TypeDispatcher(self)
                type_dispatcher.dispatch(referenced_type)
                self.indent_level -= 1
        else:
            self.logger.debug("Points to: (unknown/void)")
    
    def _explore_function_details(self, func_type: FunctionDefinitionDataType) -> None:
        """Explore function type details"""
        return_type = func_type.getReturnType()
        params = func_type.getArguments()
        
        self.logger.debug("Function signature:")
        self.logger.debug(f"  Return type: {return_type.getName()}")
        self.logger.debug(f"  Parameters: {len(params)}")
        
        if len(params) > 0:
            self.indent_level += 1
            for i, param in enumerate(params):
                param_type = param.getDataType()
                param_name = param.getName() if param.getName() else "(unnamed)"
                indent = "  " * self.indent_level
                self.logger.debug(f"{indent}Param {i}: {param_type.getName()} {param_name}")
            self.indent_level -= 1
    
    def _explore_typedef_details(self, typedef_type: TypedefDataType) -> None:
        """Explore typedef details"""
        base_type = typedef_type.getDataType()
        self.logger.debug(f"Typedef of: {base_type.getName()} ({base_type.__class__.__name__})")
        
        # Explore the underlying type
        self.indent_level += 1
        type_dispatcher = TypeDispatcher(self)
        type_dispatcher.dispatch(base_type)
        self.indent_level -= 1


class TypeDispatcher:
    """Dispatcher for routing data types to appropriate visitor methods"""
    
    def __init__(self, visitor: TypeVisitor):
        self.visitor = visitor
    
    def dispatch(self, data_type: DataType) -> None:
        """Dispatch data type to appropriate visitor method"""
        if data_type is None:
            return
        
        # Check for composite types first (both Structure and Union)
        if TypeUtils.is_composite_type(data_type):
            if 'Union' in data_type.__class__.__name__:
                self.visitor.visit_union(data_type)
            else:
                self.visitor.visit_structure(data_type)
        elif isinstance(data_type, EnumDataType):
            self.visitor.visit_enum(data_type)
        elif isinstance(data_type, ArrayDataType):
            self.visitor.visit_array(data_type)
        elif isinstance(data_type, PointerDataType):
            self.visitor.visit_pointer(data_type)
        elif isinstance(data_type, FunctionDefinitionDataType):
            self.visitor.visit_function(data_type)
        elif isinstance(data_type, TypedefDataType):
            self.visitor.visit_typedef(data_type)
        else:
            self.visitor.visit_primitive(data_type)


class DwarfSymbolExplorer:
    """
    Main facade class for exploring DWARF debug symbols.
    
    This class coordinates between all the service classes to provide
    comprehensive DWARF symbol exploration functionality.
    """
    
    def __init__(self, program: Program):
        """Initialize the explorer with a Ghidra program"""
        self.program = program
        self.logger = LoggingConfig.setup_logger()
        self.search_service = SymbolSearchService(program.getDataTypeManager(), self.logger)
        self.formatter = CppTypeFormatter(self.logger)
        self.definition_generator = CppDefinitionGenerator(self.formatter, self.logger, self.search_service)
        self.exploration_visitor = TypeExplorationVisitor(self.logger, self.formatter)
        self.type_dispatcher = TypeDispatcher(self.exploration_visitor)
    
    def find_and_explore_symbol(self, symbol_name: str) -> Optional[DataType]:
        """Find a symbol and return it for further operations"""
        self.logger.debug(f"\n{'='*60}")
        self.logger.debug("DWARF SYMBOL EXPLORER STARTING")
        self.logger.debug(f"{'='*60}")
        
        self.logger.debug(f"Program: {self.program.getName()}")
        self.logger.debug(f"Searching for symbol: '{symbol_name}'")
        
        # Find the symbol using the search service
        data_type = self.search_service.find_symbol_by_name(symbol_name)
        
        if data_type is None:
            # Try nested symbol search as fallback
            data_type = self.search_service.find_nested_symbol(symbol_name)
        
        if data_type is None:
            self.logger.error(f"Symbol '{symbol_name}' not found in the data type manager")
            self.logger.debug("Make sure DWARF debug symbols are properly imported.")
            return None
        
        return data_type
    
    def print_type_header(self, data_type: DataType, title: Optional[str] = None) -> None:
        """Print header information for a data type"""
        if title:
            self.logger.debug(f"=== {title} ===")
        
        if data_type is None:
            self.logger.debug("Data type is None")
            return
            
        info = DataTypeInfo.from_data_type(data_type)
        self.logger.debug(f"Name: {info.name}")
        self.logger.debug(f"Path: {info.path}")
        self.logger.debug(f"Size: {info.size} bytes")
        self.logger.debug(f"Type: {info.type_class}")
    
    def generate_cpp_definitions(self, data_type: DataType) -> str:
        """Generate complete C++ definitions for a data type"""
        return self.definition_generator.generate_full_cpp_definitions(data_type)
    
    def explore_type_details(self, data_type: DataType) -> None:
        """Perform detailed exploration of a data type using the visitor pattern"""
        self.logger.debug("\nDetailed Debug Analysis:")
        self.logger.debug("="*40)
        self.type_dispatcher.dispatch(data_type)
    
    def run_complete_analysis(self, symbol_name: str) -> None:
        """Run complete analysis of a symbol"""
        try:
            # Find the symbol
            data_type = self.find_and_explore_symbol(symbol_name)
            if data_type is None:
                return
            
            # Print header information
            self.logger.debug(f"\n{'-'*60}")
            self.print_type_header(data_type, "SYMBOL DEFINITION")
            self.logger.debug(f"{'-'*60}")
            
            # Generate and print C++ definitions
            self.logger.debug("\nComplete C++ Definitions:")
            self.logger.debug("="*40)
            cpp_definitions = self.generate_cpp_definitions(data_type)
            
            # Print the definitions line by line for better formatting
            if cpp_definitions:
                for line in cpp_definitions.split('\n'):
                    print(line)  # Use print instead of logger to avoid prefixes
            else:
                print("// Could not generate C++ definitions for this type")
            
            # Perform detailed exploration if debug logging is enabled
            if self.logger.isEnabledFor(logging.DEBUG):
                self.explore_type_details(data_type)
            
            # Print completion summary
            self._print_completion_summary(symbol_name, cpp_definitions)
            
        except Exception as e:
            self.logger.error(f"Script failed with error: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _print_completion_summary(self, symbol_name: str, cpp_definitions: str) -> None:
        """Print completion summary"""
        self.logger.debug(f"\n{'='*60}")
        self.logger.debug("DWARF SYMBOL EXPLORATION COMPLETED")
        self.logger.debug(f"{'='*60}")
        self.logger.debug(f"Symbol: {symbol_name}")
        struct_count = cpp_definitions.count('struct ') + cpp_definitions.count('union ')
        self.logger.debug(f"Nested types found: {struct_count}")
        self.logger.debug(f"{'='*60}")

def main():
    """Main function to run the DWARF symbol explorer"""
    if currentProgram is None:
        print("ERROR: No program is currently loaded")
        return
    symbol_name = askString("DWARF Symbol Explorer", "Enter the symbol name to explore:")

    if not symbol_name:
        print("No symbol name provided, exiting.")
        return
    
    # Create and run the explorer
    explorer = DwarfSymbolExplorer(currentProgram)
    explorer.run_complete_analysis(symbol_name)


# Execute the main function
if __name__ == "__main__":
    main()