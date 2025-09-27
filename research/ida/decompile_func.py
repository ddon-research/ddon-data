import ida_idaapi
import ida_pro
import ida_lines
import ida_name
import ida_funcs
import ida_hexrays
import ida_typeinf
import idaapi
import idc
import os
import sys
import traceback

til: ida_typeinf.til_t = ida_typeinf.get_idati()

class str_sink(idaapi.text_sink_t):
    def __init__(self):
        idaapi.text_sink_t.__init__(self)
        self.text = ""

    def _print(self, defstr):
        self.text += defstr
        return 0

    def res(self):
        return self.text
    
def get_type_structure_by_id(typeId: str) -> ida_typeinf.udt_type_data_t:
    if typeId is None:
        print("No structure ID provided")
        return None

    try:
        ordinal = int(typeId)
    except ValueError:
        print(f"Invalid ordinal value: '{typeId}'")
        return None

    tif = ida_typeinf.tinfo_t()
    if not tif.get_numbered_type(til, ordinal):
        print(f"Cannot get numbered type for ordinal '{ordinal}'")
        return None

    if not tif.is_struct():
        return None  # Not a struct/union, return None silently

    udt = ida_typeinf.udt_type_data_t()
    if not tif.get_udt_details(udt):
        print(f"Unable to get udt details for ordinal '{ordinal}'")
        return None

    return udt

def get_type_structure_by_name(name: str) -> ida_typeinf.udt_type_data_t:
    if name is None:
        print("No structure name provided")
        return None

    tif = ida_typeinf.tinfo_t()
    if not tif.get_named_type(til, name, ida_typeinf.BTF_STRUCT, True, False):
        print(f"'{name}' is not a structure")
        return None

    if tif.is_typedef():
        print(f"'{name}' is not a (non typedefed) structure.")
        return None

    udt = ida_typeinf.udt_type_data_t()
    if not tif.get_udt_details(udt):
        print(f"Unable to get udt details for structure '{name}'")
        return None

    return udt

def get_udm_ordinal(udm: ida_typeinf.udm_t) -> int:
    """Extract ordinal from UDM type, handling template types like MtTypedArray<Type>"""
    type_str: str = str(udm.type)
    
    if '<' in type_str and '>' in type_str:
        # Extract the nested type from within angle brackets
        start = type_str.find('<')
        end = type_str.rfind('>')
        if start != -1 and end != -1 and end > start:
            nested_type = type_str[start + 1:end].strip()
            print(f"  Detected template type, extracting nested type: '{nested_type}'")
            udm_tid = ida_typeinf.get_named_type_tid(nested_type)
        else:
            udm_tid = ida_typeinf.get_named_type_tid(type_str)
    else:
        udm_tid = ida_typeinf.get_named_type_tid(type_str)
    
    # Check for BADADDR (invalid TID)
    if udm_tid == idaapi.BADADDR:
        return 0
    
    return ida_typeinf.get_tid_ordinal(udm_tid)

def collect_all_ordinals(base_ordinal: int, collected: set[int] = None) -> list[int]:
    """Recursively collect all ordinals from a type structure and its dependencies"""
    if collected is None:
        collected = set()
    
    # Avoid infinite recursion by checking if we've already processed this ordinal
    # Also check for invalid ordinal (0 means no ordinal or error)
    if base_ordinal in collected or base_ordinal == 0:
        return []
    
    collected.add(base_ordinal)
    all_ordinals = [base_ordinal]
    
    # Get the type structure for this ordinal
    udt = get_type_structure_by_id(str(base_ordinal))
    if udt is None:
        return all_ordinals
    
    print(f"  Recursively processing ordinal {base_ordinal} with {udt.size()} fields")
    
    # Process each field in the structure
    for udm in udt:
        udm_ordinal = get_udm_ordinal(udm)
        if udm_ordinal != 0 and udm_ordinal not in collected:
            # Recursively collect ordinals from this field's type
            nested_ordinals = collect_all_ordinals(udm_ordinal, collected)
            all_ordinals.extend(nested_ordinals)
    
    return all_ordinals

def get_type_definition(name: str) -> str:
    if name is None:
        print("No structure name provided")
        return

    udt: ida_typeinf.udt_type_data_t = get_type_structure_by_name(name)
    if udt is None:
        print("Failed to retrieve structure details")
        return

    sink: str_sink = str_sink()
    
    base_tid = ida_typeinf.get_named_type_tid(name)
    base_ordinal: int = ida_typeinf.get_tid_ordinal(base_tid)
    
    print(f"Starting recursive collection from base ordinal: {base_ordinal}")
    type_ordinals: list[int] = collect_all_ordinals(base_ordinal)
    
    print(f"Collected {len(type_ordinals)} total ordinals: {type_ordinals}")
    
    ida_typeinf.print_decls(sink, til, type_ordinals, ida_typeinf.PDF_INCL_DEPS | ida_typeinf.PDF_DEF_FWD | ida_typeinf.PDF_DEF_BASE)
    res = sink.res()
    return res


def debug(msg):
    sys.stdout.write(f"[DEBUG] {msg}\n")
    sys.stdout.flush()

def dump_env():
    debug("Environment dump:")
    for k in sorted(os.environ.keys()):
        debug(f"  {k} = {os.environ[k]}")

def dump_sysinfo():
    debug(f"sys.version = {sys.version}")
    try:
        import struct
        debug(f"Python build bitness: {struct.calcsize('P')*8}-bit")
    except Exception as e:
        debug(f"Could not get bitness: {e}")
    debug(f"sys.path = {sys.path}")
    debug(f"sys.argv = {sys.argv}")
    debug(f"idc.argv = {idc.ARGV}")

def decompile_function(func_name, out_fd):
    #debug(f"Looking up function name: {func_name!r}")
    ea:  ida_idaapi.ea_t = ida_name.get_name_ea(0, func_name)
    if ea == idaapi.BADADDR:
        debug(f"get_name_ea returned BADADDR")
        print(f"[!] function name '{func_name}' not found", file=out_fd)
        return False
    #debug(f"Found EA = {hex(ea)}")
    func: ida_funcs.func_t = ida_funcs.get_func(ea)
    if not func:
        debug("ida_funcs.get_func returned None")
        print(f"[!] no function at {hex(ea)}", file=out_fd)
        return False
    try:
        debug("Calling ida_hexrays.decompile_func(...)")
        cfunc: ida_hexrays.cfuncptr_t = ida_hexrays.decompile_func(func)
    except Exception as e:
        debug(f"Exception during decompile: {e}")
        traceback.print_exc(file=out_fd)
        return False
    pc: ida_pro.strvec_t = cfunc.get_pseudocode()
    lines = [ida_lines.tag_remove(sl.line) for sl in pc]
    #debug(f"Number of pseudocode lines: {len(lines)}")
    for line in lines:
        print(str(line), file=out_fd)
    return True

def main():
    dump_sysinfo()
    
    if len(idc.ARGV) < 2:
        debug("No function name passed as argument")
        func_name = os.environ.get("IDA_FUNC_NAME")
        if not func_name:
            debug("No env var IDA_FUNC_NAME either")
            print("Usage: idat -A -Sdecompile_func.py:funcname[:outfile]", file=sys.stderr)
            ida_pro.qexit(1)
    else:
        func_name = idc.ARGV[1]

    out_fd = sys.stdout
    if len(idc.ARGV) >= 3:
        outname = idc.ARGV[2]
        try:
            out_fd = open(outname, "w")
            debug(f"Opened output file {outname}")
        except Exception as e:
            debug(f"Failed to open output file {outname}: {e}")
            print(f"[!] cannot open output file {outname}: {e}", file=sys.stderr)
            ida_pro.qexit(1)

    success = decompile_function(func_name, out_fd)
    print(get_type_definition("rLandInfo"))

    if out_fd is not sys.stdout:
        out_fd.close()
        debug("Closed output file")

    #debug(f"Exiting with status {0 if success else 1}")
    ida_pro.qexit(0 if success else 1)

if __name__ == "__main__":
    main()
