"""008 T003: read-only headless dump of handlers, senders and their callers (PC 03040008).

Run: idat -A -L<log> -S"read_funcs.py <OUT.txt>" <private copy .i64>
Writes, per function: name, decompiled pseudocode (if Hex-Rays succeeds) and disassembly.
Never modifies the database: sets DBFL_KILL before qexit.
"""
import sys
import traceback

import ida_auto
import ida_funcs
import ida_ida
import ida_lines
import ida_loader
import ida_nalt
import idautils
import idc

FUNCS = []  # T003: always pass VAs or names on the command line
EXTRA = []  # second pass: callees named on the command line


def dump(out, ea):
    f = ida_funcs.get_func(ea)
    out.write("=" * 78 + "\n")
    if f is None:
        out.write("0x%X: no function\n" % ea)
        return
    out.write("0x%X %s (start 0x%X end 0x%X)\n" % (ea, idc.get_func_name(f.start_ea), f.start_ea, f.end_ea))
    try:
        import ida_hexrays
        cf = ida_hexrays.decompile(f.start_ea)
        out.write("--- pseudocode\n")
        for sl in cf.get_pseudocode():
            out.write(ida_lines.tag_remove(sl.line) + "\n")
    except Exception as e:  # coverage gap, not evidence
        out.write("--- pseudocode failed: %r\n" % (e,))
    out.write("--- callers\n")
    for x in idautils.XrefsTo(f.start_ea):
        cf_ = ida_funcs.get_func(x.frm)
        out.write("  0x%X in %s\n" % (x.frm, idc.get_func_name(cf_.start_ea) if cf_ else "-"))
    out.write("--- disasm\n")
    for h in idautils.FuncItems(f.start_ea):
        out.write("%08X  %s\n" % (h, idc.generate_disasm_line(h, 0)))


def resolve(a):
    """A hex VA, or a function name (``::`` or ``__`` form)."""
    try:
        return int(a, 16)
    except ValueError:
        for n in (a, a.replace("__", "::")):
            ea = idc.get_name_ea_simple(n)
            if ea != idc.BADADDR:
                return ea
        for ea in idautils.Functions():
            if idc.get_func_name(ea) in (a, a.replace("__", "::")):
                return ea
        raise


def main(path, extra):
    ida_auto.auto_wait()
    with open(path, "w", encoding="utf-8") as out:
        out.write("idb %s\n" % idc.get_idb_path())
        out.write("input %s sha256 %s\n" % (ida_nalt.get_input_file_path(),
                                            ida_nalt.retrieve_input_file_sha256().hex()))
        out.write("64bit %s imagebase 0x%X\n" % (ida_ida.inf_is_64bit(), ida_nalt.get_imagebase()))
        for ea in (extra or FUNCS):
            dump(out, ea)


code = 1
try:
    args = list(idc.ARGV)[1:]
    main(args[0], [resolve(a) for a in args[1:]])
    print("read_funcs: ok")
    code = 0
except BaseException:
    traceback.print_exc()
    print("read_funcs: error")
ida_loader.set_database_flag(ida_loader.DBFL_KILL)
idc.qexit(code)
