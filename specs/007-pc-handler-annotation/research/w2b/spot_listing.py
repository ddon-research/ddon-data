"""007 W2 T013b spot check: read-only headless listing of call sites (PC 03040008 / PS4 02020005).

    idat -A -L<log> -S"spot_listing.py <OUT.txt> <va>|<lo:hi> ..." <copy .i64>

For each call-site VA: the database identity, then the instructions of its basic block from the block start
(at most 24 before the site) up to and including the site, with the call target's name; for each lo:hi range, every item with block starts marked. Marks the session
not to be saved (DBFL_KILL) first and exits with qexit (1 after an error). No writes to the database.
"""
import sys
import traceback

import ida_auto
import ida_gdl
import ida_funcs
import ida_ida
import ida_lines
import ida_loader
import ida_nalt
import ida_name
import idc


def block_start(va):
    f = ida_funcs.get_func(va)
    if f is None:
        return None
    for b in ida_gdl.FlowChart(f, flags=ida_gdl.FC_NOEXT):
        if b.start_ea <= va < b.end_ea:
            return b.start_ea
    return None


def main(argv):
    out = argv[1]
    vas = [int(a, 16) for a in argv[2:] if ":" not in a]
    ranges = [tuple(int(x, 16) for x in a.split(":")) for a in argv[2:] if ":" in a]
    ida_auto.auto_wait()
    lines = [
        f"idb {idc.get_idb_path()}",
        f"input_sha256 {ida_nalt.retrieve_input_file_sha256().hex()}",
        f"64bit {ida_ida.inf_is_64bit()} imagebase {ida_nalt.get_imagebase():#x}",
    ]
    for va in vas:
        f = ida_funcs.get_func(va)
        lines.append("")
        lines.append(f"== site {va:#x} in {ida_funcs.get_func_name(va) if f else None} "
                     f"({f.start_ea:#x})" if f else f"== site {va:#x} (no function)")
        start = block_start(va)
        eas = []
        ea = va
        while ea != idc.BADADDR and len(eas) < 25:
            eas.append(ea)
            if start is not None and ea <= start:
                break
            ea = idc.prev_head(ea, 0)
        for ea in reversed(eas):
            text = idc.generate_disasm_line(ea, ida_lines.GENDSM_REMOVE_TAGS)
            tgt = idc.get_operand_value(ea, 0) if idc.print_insn_mnem(ea).startswith("call") else None
            note = f"    ; -> {ida_name.get_name(tgt) or hex(tgt)}" if tgt else ""
            lines.append(f"{ea:#x}  {idc.get_bytes(ea, idc.get_item_size(ea)).hex()}  {text}{note}")
    for lo, hi in ranges:
        lines.append("")
        lines.append(f"== range {lo:#x}..{hi:#x} (block starts marked *)")
        f = ida_funcs.get_func(lo)
        starts = {b.start_ea for b in ida_gdl.FlowChart(f, flags=ida_gdl.FC_NOEXT)} if f else set()
        ea = lo
        while ea != idc.BADADDR and ea <= hi:
            text = idc.generate_disasm_line(ea, ida_lines.GENDSM_REMOVE_TAGS)
            lines.append(f"{'*' if ea in starts else ' '}{ea:#x}  {idc.get_bytes(ea, idc.get_item_size(ea)).hex()}  {text}")
            ea = idc.next_head(ea, idc.BADADDR)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


code = 0
ida_loader.set_database_flag(ida_loader.DBFL_KILL)
try:
    main(idc.ARGV)
except Exception:
    traceback.print_exc()
    code = 1
print(f"spot_listing exit {code}")
idc.qexit(code)
