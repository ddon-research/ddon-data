# DWARF Symbol Explorer Analysis Class
#
# Core analysis class for exploring DWARF symbols in Ghidra and generating 
# C++ definitions from binary structures.
#
# This class handles the main logic for symbol exploration, type analysis,
# and C++ code generation while remaining independent of the entry point.


import logging
from typing import Optional

from ghidra.program.model.data import DataType
from ghidra.program.model.listing import Program

from shared.logging import LoggingConfig
from .generators import CppDefinitionGenerator
from .search_service import SymbolSearchService
from .visitors import TypeExplorationVisitor, TypeDispatcher
from ..core.data_types import DataTypeInfo
from ..output.formatters import CppTypeFormatter
from ..output.handlers import HeadlessOutputHandler


class DwarfSymbolExplorer:
    """
    Main analysis class for DWARF symbol exploration and C++ code generation.
    
    This class provides comprehensive functionality for exploring DWARF debug symbols
    in Ghidra binaries, analyzing type hierarchies with dependency resolution, and
    generating C++ struct definitions. Uses lazy initialization for optimal resource
    management in headless environments.
    """

    def __init__(self, program: Program, log_level: str = "INFO") -> None:
        """Initialize the DWARF symbol explorer with lazy component initialization.
        
        Args:
            program: Ghidra program instance containing DWARF debug information
            log_level: Logging verbosity level ("DEBUG" or "INFO")
        """
        self.program = program
        self.log_level = log_level
        self.logger = self._setup_logger()

        # Lazy initialization - create components only when needed
        self._output_handler = None
        self._search_service = None
        self._formatter = None
        self._definition_generator = None
        self._exploration_visitor = None
        self._type_dispatcher = None

    @property
    def output_handler(self) -> HeadlessOutputHandler:
        if self._output_handler is None:
            self._output_handler = HeadlessOutputHandler()
        return self._output_handler

    @property
    def search_service(self) -> SymbolSearchService:
        if self._search_service is None:
            self._search_service = SymbolSearchService(self.program.getDataTypeManager(), self.logger)
        return self._search_service

    @property
    def formatter(self) -> CppTypeFormatter:
        if self._formatter is None:
            self._formatter = CppTypeFormatter(self.logger)
        return self._formatter

    @property
    def definition_generator(self) -> CppDefinitionGenerator:
        if self._definition_generator is None:
            self._definition_generator = CppDefinitionGenerator(self.formatter, self.logger, self.search_service)
        return self._definition_generator

    @property
    def exploration_visitor(self) -> TypeExplorationVisitor:
        if self._exploration_visitor is None:
            self._exploration_visitor = TypeExplorationVisitor(self.logger, self.formatter)
        return self._exploration_visitor

    @property
    def type_dispatcher(self) -> TypeDispatcher:
        if self._type_dispatcher is None:
            self._type_dispatcher = TypeDispatcher(self.exploration_visitor)
        return self._type_dispatcher

    def _setup_logger(self) -> logging.Logger:
        """Setup logger using shared LoggingConfig"""
        return LoggingConfig.setup_logger("dwarf_symbol_explorer", self.log_level)

    def find_and_explore_symbol(self, symbol_name: str) -> Optional[DataType]:
        """Find a DWARF symbol by name in the program's data type manager.
        
        Args:
            symbol_name: Name of the DWARF symbol to search for
            
        Returns:
            DataType instance if found, None if symbol not found or unavailable
        """
        self.logger.debug(f"\n{'=' * 60}")
        self.logger.debug("DWARF SYMBOL EXPLORER STARTING")
        self.logger.debug(f"{'=' * 60}")

        self.logger.debug(f"Program: {self.program.getName()}")
        self.logger.debug(f"Searching for symbol: '{symbol_name}'")

        # Find the symbol using the search service
        data_type = self.search_service.find_symbol_by_name(symbol_name)

        if data_type is None:
            # Try nested symbol search as fallback
            data_type = self.search_service.find_nested_symbol(symbol_name)

        if data_type is None:
            self.logger.error(f"Symbol '{symbol_name}' not found in the data type manager")
            self.logger.error("Make sure DWARF debug symbols are properly imported.")
            return None

        return data_type

    def print_type_header(self, data_type: DataType, title: Optional[str] = None) -> None:
        """Print formatted header information for a data type.
        
        Args:
            data_type: Ghidra DataType instance to display information for
            title: Optional custom title for the header section
        """
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
        """Generate complete C++ struct definitions for a data type and its dependencies.
        
        Args:
            data_type: Ghidra DataType to generate C++ definitions for
            
        Returns:
            Complete C++ code string with struct definitions, including
            nested types and dependency resolution
        """
        return self.definition_generator.generate_full_cpp_definitions(data_type)

    def explore_type_details(self, data_type: DataType) -> None:
        """Perform detailed exploration of a data type using the visitor pattern.
        
        Provides comprehensive debug analysis of type structure, field layouts,
        inheritance hierarchies, and memory organization for diagnostic purposes.
        
        Args:
            data_type: Ghidra DataType to explore in detail
        """
        self.logger.debug("\nDetailed Debug Analysis:")
        self.logger.debug("=" * 40)
        self.type_dispatcher.dispatch(data_type)

    def analyze_symbol(self, symbol_name: str, explore_depth: int = 5) -> bool:
        """
        Analyze a DWARF symbol and generate C++ definitions.
        
        Args:
            symbol_name: The name of the symbol to analyze
            explore_depth: Maximum exploration depth (1-10)
            
        Returns:
            True if analysis was successful, False otherwise
        """
        try:
            # Store exploration depth for use by generators
            import os
            os.environ['EXPLORE_DEPTH'] = str(explore_depth)

            # Find the symbol
            data_type = self.find_and_explore_symbol(symbol_name)
            if data_type is None:
                return False

            # Print header information
            self.logger.debug(f"\n{'-' * 60}")
            self.print_type_header(data_type, "SYMBOL DEFINITION")
            self.logger.debug(f"{'-' * 60}")

            # Generate and write C++ definitions
            self.logger.debug("\nComplete C++ Definitions:")
            self.logger.debug("=" * 40)
            cpp_definitions = self.generate_cpp_definitions(data_type)

            if cpp_definitions:
                self.output_handler.write(cpp_definitions)
            else:
                self.output_handler.write("// Could not generate C++ definitions for this type")

            # Flush output
            self.output_handler.flush()

            # Perform detailed exploration if debug logging is enabled
            if self.logger.isEnabledFor(logging.DEBUG):
                self.explore_type_details(data_type)

            # Print completion summary
            self._print_completion_summary(symbol_name)

            return True

        except Exception as e:
            self.logger.error(f"Analysis failed with error: {e}")
            if self.log_level == 'DEBUG':
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def _print_completion_summary(self, symbol_name: str) -> None:
        """Print formatted completion summary for the analysis session.
        
        Args:
            symbol_name: Name of the analyzed symbol for summary output
        """
        self.logger.debug(f"\n{'=' * 60}")
        self.logger.debug("DWARF SYMBOL EXPLORATION COMPLETED")
        self.logger.debug(f"{'=' * 60}")
        self.logger.debug(f"Symbol: {symbol_name}")
        self.logger.debug(f"Output Format: cpp")
        self.logger.debug(f"Log Level: {self.log_level}")
        self.logger.debug(f"{'=' * 60}")
