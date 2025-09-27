# This script creates a virtual table (vtable) structure for a given C++ class.
# It extracts the function pointers from the vtable and creates a corresponding
# data structure in Ghidra to represent it.
#
# Prerequisites:
# - The class structure must already be defined in Ghidra
# - The class structure must have '_vtable' as its first field
# - All functions referenced by the vtable must already exist and be properly defined
#
# Usage:
# 1. Define your class structure (e.g., MtDataReader) with _vtable as the first field
# 2. Ensure all functions referenced by the vtable are already defined with proper signatures
# 3. Select the range of memory containing the vtable entries (usually 8-byte pointers on 64-bit)
# 4. Ensure there's a label at the start address in one of these formats:
#    - PTR_~ClassName_address (e.g., PTR_~MtDataReader_03461470)
#    - ClassName::vtable (original format)
# 5. Run the script
#
# The script will:
# - Use existing function definitions to create function pointer types
# - Create a vtable structure with proper function pointer types
# - Update the existing class structure's _vtable field to point to the new vtable
#
#@author Sehkah
#@category ddon-research
#@keybinding SHIFT-V
#@menupath 
#@toolbar 
#@runtime PyGhidra

import logging

from ghidra.program.model.data import (
    StructureDataType,
    DataTypeConflictHandler,
    PointerDataType,
    ProgramBasedDataTypeManager
)
from ghidra.program.model.mem import Memory
from ghidra.program.model.address import Address
from ghidra.program.model.listing import Program, Function
from ghidra.program.model.symbol import SymbolTable, Symbol

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

currentProgram: Program = getCurrentProgram()
# Handle the case where getCurrentSelection might not be available in some contexts
try:
    currentSelection = currentSelection
except:
    currentSelection = None

def build_structure(class_name, startAddress, count):
    """
    Build a vtable structure by examining function pointers at consecutive addresses.
    
    Args:
        class_name: Name of the C++ class (extracted from vtable label)
        startAddress: Starting address of the vtable
        count: Number of function pointers in the vtable
    
    Returns:
        StructureDataType representing the vtable
    """
    path = "{}_vtable_t".format(class_name)
    logger.info("=== Building vtable structure ===")
    logger.info("Class name: {}".format(class_name))
    logger.info("Structure name: {}".format(path))
    logger.info("Start address: {}".format(startAddress))
    logger.info("Entry count: {}".format(count))
    logger.info("Address range: {} to {}".format(startAddress, startAddress.add((count-1) * 8)))
    structure = StructureDataType(path, 0)

    for index in range(count):
        logger.info("\n--- Processing vtable entry {} of {} ---".format(index + 1, count))
        address = startAddress.add(index * 8)  # 8 bytes per entry
        logger.info("Entry address: {}".format(address))
        
        # Read the function address directly from memory (8 bytes as long)
        try:
            memory: Memory = currentProgram.getMemory()
            logger.debug("Attempting to read 8 bytes from address {}".format(address))
            
            # Use Ghidra's built-in getLong method to read 8 bytes directly
            long_value = memory.getLong(address)
            addr_func = toAddr(long_value)
            
            # Log the value for debugging
            logger.info("Memory read successful:")
            logger.info("  Raw long value: 0x{:016x} ({})".format(long_value, long_value))
            logger.info("  Target function address: {}".format(addr_func))
            
        except Exception as e:
            logger.error("Memory read failed at address {}: {}".format(address, e))
            raise ValueError("Could not read function address at {}: {}".format(address, e))
        
        if addr_func is None:
            raise ValueError("Could not determine function address at vtable entry {}".format(address))
            
        # Get the symbol table to find symbol information (for logging)
        try:
            symtab: SymbolTable = currentProgram.getSymbolTable()
            symbol_at_addr = symtab.getPrimarySymbol(address)
            if symbol_at_addr is not None:
                logger.info("Symbol at vtable entry:")
                logger.info("  Symbol name: '{}'".format(symbol_at_addr.getName()))
                logger.info("  Symbol type: {}".format(symbol_at_addr.getSymbolType()))
                logger.info("  Symbol namespace: {}".format(symbol_at_addr.getParentNamespace().getName()))
            else:
                logger.debug("No symbol found at vtable entry address {}".format(address))
        except Exception as e:
            logger.warning("Could not access symbol table: {}".format(e))
            
        # Now get the function at the target address
        logger.debug("Looking for function at address {}".format(addr_func))
        function: Function = getFunctionAt(addr_func)
        
        if function is None:
            logger.error("Function lookup failed:")
            logger.error("  Target address: {}".format(addr_func))
            logger.error("  No function definition found at this address")
            logger.error("  Ensure all vtable functions are properly defined before running this script")
            raise ValueError("No function found at address {}. All functions must already exist before running this script.".format(addr_func))

        function_name = function.getName()
        logger.info("Function found successfully:")
        logger.info("  Function name: '{}'".format(function_name))
        logger.info("  Function address: {}".format(addr_func))
        logger.info("  Function namespace: {}".format(function.getParentNamespace().getName()))
        logger.info("  Calling convention: {}".format(function.getCallingConventionName()))
        logger.info("  Return type: {}".format(function.getReturnType().getName()))
        logger.info("  Parameter count: {}".format(function.getParameterCount()))

        # Update calling convention to __thiscall if it's not already set correctly
        current_convention = function.getCallingConventionName()
        if current_convention != "__thiscall":
            logger.info("Updating calling convention from '{}' to '__thiscall'".format(current_convention))
            try:
                function.setCallingConvention("__thiscall")
                logger.info("Successfully updated calling convention")
            except Exception as e:
                logger.warning("Could not update calling convention: {}".format(e))
        else:
            logger.debug("Calling convention already set to __thiscall")

        # This retrieves the actual data type from the Data Type Manager, preserving its
        # original category path from the DWARF import and preventing duplicates.
        logger.info("Directly retrieving existing function definition from function signature")
        funcDefinition = function.getSignature(True)

        logger.info("Function signature retrieved:")
        logger.info("  Signature: {}".format(funcDefinition))
        logger.info("  Definition name: {}".format(funcDefinition.getName()))
        logger.info("  Definition path: {}".format(funcDefinition.getPathName()))

        # Create an 8-byte pointer to the function definition
        ptr_func_definition_data_type = PointerDataType(funcDefinition, 8)  # Explicitly 8 bytes
        logger.debug("Created 8-byte pointer type: {}".format(ptr_func_definition_data_type))
        logger.debug("Pointer size: {} bytes".format(ptr_func_definition_data_type.getLength()))

        # Resolve the pointer type to ensure it's properly managed and avoid duplicates.
        # This is still good practice as the pointer type itself might not exist yet.
        data_type_manager: ProgramBasedDataTypeManager = currentProgram.getDataTypeManager()
        resolved_pointer = data_type_manager.resolve(ptr_func_definition_data_type, DataTypeConflictHandler.REPLACE_HANDLER)
        logger.debug("Resolved pointer type: {}".format(resolved_pointer.getPathName()))
        
        # Use the resolved pointer type
        ptr_func_definition_data_type = resolved_pointer

        logger.debug("Data types resolved successfully:")
        logger.debug("  Function definition: {} at {}".format(funcDefinition.getName(), funcDefinition.getPathName()))
        logger.debug("  Pointer type: {} at {}".format(ptr_func_definition_data_type.getName(), ptr_func_definition_data_type.getPathName()))

        logger.debug("Adding entry to vtable structure:")
        logger.debug("  Offset: {}".format(index * 8))
        logger.debug("  Field name: {}".format(function_name))
        
        structure.insertAtOffset(
            index * 8,  # 8 bytes per entry
            ptr_func_definition_data_type,
            8,  # 8 bytes size
            function_name,
            "",
        )
        logger.info("Entry {} added to structure successfully".format(index + 1))

    logger.info("\n=== Vtable structure build complete ===")
    logger.info("Structure name: {}".format(structure.getName()))
    logger.info("Total entries: {}".format(count))
    logger.info("Structure size: {} bytes".format(structure.getLength()))
    return structure


def set_vtable_datatype(class_name, structure):
    """
    Updates an existing class structure's _vtable field to point to the new vtable structure.
    Expects the class structure to already exist with _vtable as the first field.
    """
    data_type_manager = currentProgram.getDataTypeManager()
    
    # Get the program name to build dynamic DWARF paths
    program_name: str = currentProgram.getName()
    
    # Debug: Try to find the class structure
    logger.info("Searching for class structure '{}'".format(class_name))
    logger.info("Program name: '{}'".format(program_name))
    
    # Try different possible paths dynamically
    possible_paths = [
        "/{}/DWARF/{}.h/{}".format(program_name, class_name, class_name),  # Program/DWARF/Header.h/Class
        "/DWARF/{}.h/{}".format(class_name, class_name),                    # DWARF/Header.h/Class
        "/DWARF/{}".format(class_name),                                     # DWARF/Class
        "/{}".format(class_name),                                           # /Class
        class_name,                                                         # Class
        "/{}".format(class_name.lower()),                                   # /class (lowercase)
        class_name.lower()                                                  # class (lowercase)
    ]
    
    class_type = None
    found_path = None
    
    for path in possible_paths:
        logger.debug("Trying path: '{}'".format(path))
        class_type = data_type_manager.getDataType(path)
        if class_type is not None:
            found_path = path
            logger.info("Found class structure at path: '{}'".format(path))
            break
    
    # If still not found, search through all data types
    if class_type is None:
        logger.info("Direct path lookup failed, searching all data types...")
        all_data_types = data_type_manager.getAllDataTypes()
        matching_types = []
        
        for dt in all_data_types:
            dt_name = dt.getName()
            if class_name.lower() in dt_name.lower():
                matching_types.append("{}::{}".format(dt.getCategoryPath(), dt_name))
                if dt_name == class_name:
                    class_type = dt
                    found_path = dt.getPathName()
                    logger.info("Found exact match: {}".format(found_path))
                    break
        
        if len(matching_types) > 0:
            logger.info("Found {} potential matches:".format(len(matching_types)))
            for match in matching_types[:10]:  # Limit to first 10
                logger.info("  - {}".format(match))
    
    if class_type is None or class_type.isZeroLength():
        logger.error("Class structure '{}' not found in data type manager".format(class_name))
        logger.error("Searched paths: {}".format(possible_paths))
        raise ValueError("Class structure '{}' must be defined before running this script. Please create the class structure first.".format(class_name))

    # Check if the class has any fields
    if class_type.getNumComponents() == 0:
        raise ValueError("Class '{}' has no fields. Expected _vtable as the first field.".format(class_name))
        
    field = class_type.getComponent(0)
    field_name = field.getFieldName()

    if field_name != "_vtable":
        raise ValueError("Expected first field of class '{}' to be named '_vtable', found '{}'. Please ensure _vtable is the first field.".format(class_name, field_name))

    logger.info("Updating _vtable field in class '{}' to point to {}".format(class_name, structure.getName()))

    vtable_ptr = data_type_manager.resolve(PointerDataType(structure), DataTypeConflictHandler.REPLACE_HANDLER)
    field.setDataType(vtable_ptr)
    return True


def main():
    logger.info("\n" + "="*60)
    logger.info("GHIDRA VTABLE CREATION SCRIPT STARTING")
    logger.info("="*60)

    selection = currentSelection
    if selection is None or selection.isEmpty():
        raise ValueError("No memory selection found. Please select the vtable memory range first.")
    
    startAddress: Address = selection.getFirstRange().getMinAddress()
    length: int = selection.getFirstRange().getLength()
    count: int = length // 8  # Use 8 bytes per pointer entry (64-bit)

    logger.info("Selection information:")
    logger.info("  Start address: {}".format(startAddress))
    logger.info("  Selection length: {} bytes".format(length))
    logger.info("  Calculated entry count: {} (8 bytes per pointer)".format(count))
    logger.info("  End address: {}".format(startAddress.add(length - 1)))

    sym: Symbol = getSymbolAt(startAddress)

    if sym is None:
        logger.error("No symbol found at the selected address {}".format(startAddress))
        raise ValueError("No symbol found at the selected address")
    
    symbol_name = sym.getName()
    logger.info("\nSymbol analysis:")
    logger.info("  Symbol name: '{}'".format(symbol_name))
    logger.info("  Symbol type: {}".format(sym.getSymbolType()))
    logger.info("  Is global: {}".format(sym.isGlobal()))
    logger.info("  Namespace: {}".format(sym.getParentNamespace().getName()))
    
    class_name = None
    
    # Handle different vtable label formats
    if symbol_name.startswith("PTR_~"):
        # Format: PTR_~ClassName_address
        # Extract class name by removing PTR_~ prefix and _address suffix
        temp_name = symbol_name[5:]  # Remove "PTR_~"
        underscore_pos = temp_name.rfind("_")  # Find last underscore
        if underscore_pos > 0:
            class_name = temp_name[:underscore_pos]
        else:
            class_name = temp_name
    elif symbol_name == "vtable" and not sym.isGlobal():
        # Original format: ClassName::vtable
        class_name = sym.getParentNamespace().getName()
        if "::" in class_name:
            raise ValueError("Probably you want to handle manually this one: namespace '{}'".format(class_name))
    else:
        raise ValueError(
            "Expected a vtable label (either 'PTR_~ClassName_address' or 'ClassName::vtable'), got: '{}'".format(symbol_name))
    
    if class_name is None:
        raise ValueError("Could not extract class name from symbol: '{}'".format(symbol_name))

    structure = build_structure(class_name, startAddress, count)

    data_type_manager: ProgramBasedDataTypeManager = currentProgram.getDataTypeManager()

    logger.info("Adding/updating vtable structure in data type manager...")
    data_type_manager.addDataType(structure, DataTypeConflictHandler.REPLACE_HANDLER)

    # Update the existing class structure's _vtable field
    logger.info("\nUpdating class structure...")
    set_vtable_datatype(class_name, structure)
    
    logger.info("\n" + "="*60)
    logger.info("VTABLE CREATION COMPLETED SUCCESSFULLY")
    logger.info("="*60)
    logger.info("Class: {}".format(class_name))
    logger.info("Vtable structure: {}".format(structure.getName()))
    logger.info("Entries processed: {}".format(count))
    logger.info("Class _vtable field updated successfully")
    logger.info("="*60)

# Execute the main function
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Script failed with an error: {}".format(e))