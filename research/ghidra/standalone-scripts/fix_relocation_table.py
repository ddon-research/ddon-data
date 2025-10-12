#@author Sehkah
#@category ddon-research
#@keybinding SHIFT-R
#@menupath 
#@toolbar 
#@runtime PyGhidra

# DRY_RUN: True = report only. False = create pointers and log them.
# UNDO: True = read log and undefine each logged address (cleanup).
from ghidra.program.model.data import PointerDataType, Undefined
from ghidra.util import Msg
import os

DRY_RUN = False      # set False to apply changes
UNDO = False        # set True to revert based on log
LOG_FILE = os.path.expanduser("~/ghidra_defined_ptrs.txt")

program = currentProgram
mem = program.getMemory()
ptr_size = program.getDefaultPointerSize()
reloc_table = program.getRelocationTable()
refmgr = program.getReferenceManager()
monitor.setMessage("Relro pointer define script")

def write_log_line(path, line):
    with open(path, "a") as f:
        f.write(line + "\n")

def read_log(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [l.strip() for l in f if l.strip()]

if UNDO:
    lines = read_log(LOG_FILE)
    if not lines:
        print("No log found at %s" % LOG_FILE)
    else:
        undone = 0
        for ln in lines:
            try:
                addr = toAddr(int(ln, 16))
                if monitor.isCancelled(): break
                clearListing(addr)
                createData(addr, Undefined.getUndefinedDataType(ptr_size))
                undone += 1
            except Exception as e:
                print("Failed undo for %s: %s" % (ln, e))
        print("UNDO done. reverted=%d" % undone)
    raise SystemExit()

# locate rel.ro block
relro_block = None
for b in mem.getBlocks():
    nm = b.getName()
    if nm and ("rel.ro" in nm or ".data.rel.ro" in nm):
        relro_block = b
        break

if relro_block is None:
    Msg.error(None, "No .data.rel.ro block found. Aborting.")
    print("No .data.rel.ro block found.")
    raise SystemExit()

start = relro_block.getStart()
end = relro_block.getEnd()
print("Relro:", start, "->", end, "ptr_size:", ptr_size, "DRY_RUN=", DRY_RUN, "LOG=", LOG_FILE)

# collect relocations in range
relocs = []
try:
    relocs = list(reloc_table.getRelocations(start, end))
except Exception:
    addr = start
    while addr.compareTo(end) <= 0:
        if monitor.isCancelled(): break
        try:
            if reloc_table.hasRelocation(addr):
                for r in list(reloc_table.getRelocations(addr)):
                    relocs.append(r)
        except Exception:
            pass
        addr = addr.add(ptr_size)

# dedupe by relocation address
seen = set()
relocs_unique = []
for r in relocs:
    a = r.getAddress()
    key = a.getOffset()
    if key not in seen:
        seen.add(key)
        relocs_unique.append(r)

processed = candidates = created = already = skipped = errors = 0

for reloc in relocs_unique:
    if monitor.isCancelled(): break
    processed += 1
    try:
        loc = reloc.getAddress()
    except Exception:
        errors += 1
        continue
    try:
        if ptr_size == 8:
            raw = mem.getLong(loc)
            val = raw & 0xFFFFFFFFFFFFFFFF
        elif ptr_size == 4:
            raw = mem.getInt(loc)
            val = raw & 0xFFFFFFFF
        else:
            buf = bytearray(ptr_size)
            mem.getBytes(loc, buf)
            val = 0
            for i, b in enumerate(buf):
                val |= (b & 0xff) << (8 * i)
    except Exception:
        errors += 1
        continue

    if val == 0:
        skipped += 1
        continue

    try:
        tgt = toAddr(val)
    except Exception:
        skipped += 1
        continue

    if not mem.contains(tgt):
        skipped += 1
        continue

    func = getFunctionContaining(tgt)
    if func is None:
        skipped += 1
        continue

    candidates += 1

    data = getDataAt(loc)
    is_pointer_dtype = False
    if data is not None:
        try:
            dn = data.getDataType().getName().lower()
            if "pointer" in dn or dn.startswith("ptr") or "addr" in dn:
                is_pointer_dtype = True
        except Exception:
            pass

    has_ref = False
    try:
        for r in list(refmgr.getReferencesFrom(loc)):
            try:
                if r.getToAddress().equals(tgt):
                    has_ref = True
                    break
            except Exception:
                try:
                    if r.getToAddress() == tgt:
                        has_ref = True
                        break
                except Exception:
                    pass
    except Exception:
        try:
            for r in getReferencesFrom(loc):
                if r.getToAddress().equals(tgt):
                    has_ref = True
                    break
        except Exception:
            pass

    if is_pointer_dtype or has_ref:
        already += 1
        print("EXISTING: %s -> %s (func: %s)" % (loc, tgt, func.getName()))
        continue

    print("CANDIDATE: %s -> %s (func: %s)" % (loc, tgt, func.getName()))

    if not DRY_RUN:
        try:
            clearListing(loc)
            createData(loc, PointerDataType())
            created += 1
            write_log_line(LOG_FILE, format(loc.getOffset(), 'x'))
            print("  Defined:", loc)
        except Exception as e:
            errors += 1
            print("  Failed define %s : %s" % (loc, e))

print("Done. processed=%d candidates=%d created=%d already=%d skipped=%d errors=%d" %
      (processed, candidates, created, already, skipped, errors))
