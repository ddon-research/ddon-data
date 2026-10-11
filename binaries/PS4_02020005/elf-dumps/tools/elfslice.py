# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Byte-level helpers for the PS4 02020005 ELF dump set.

Every subcommand writes its result to stdout (or to the paths it is given) and never writes next to
its input. Standard ELF64 section and program headers are parsed here; nothing SCE-specific is
decoded, that stays with orbis-bin and, later, ddon-dwarf-reconstructor-rust.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from collections import Counter
from pathlib import Path

OUT = sys.stdout.buffer


def emit(line: str) -> None:
    OUT.write(line.encode("utf-8") + b"\n")


# ---------------------------------------------------------------- ELF headers


class Elf:
    def __init__(self, path: str) -> None:
        self.path = path
        with open(path, "rb") as f:
            ident = f.read(64)
            if ident[:4] != b"\x7fELF" or ident[4] != 2 or ident[5] != 1:
                sys.exit(f"{path}: not a little-endian ELF64 file")
            (self.e_type, self.e_machine, _, self.e_entry, self.e_phoff, self.e_shoff, _, _,
             self.e_phentsize, self.e_phnum, self.e_shentsize, self.e_shnum,
             self.e_shstrndx) = struct.unpack_from("<HHIQQQIHHHHHH", ident, 16)
            f.seek(self.e_phoff)
            ph = f.read(self.e_phentsize * self.e_phnum)
            self.phdrs = [struct.unpack_from("<IIQQQQQQ", ph, i * self.e_phentsize)
                          for i in range(self.e_phnum)]
            f.seek(self.e_shoff)
            sh = f.read(self.e_shentsize * self.e_shnum)
            raw = [struct.unpack_from("<IIQQQQIIQQ", sh, i * self.e_shentsize)
                   for i in range(self.e_shnum)]
            strtab = raw[self.e_shstrndx]
            f.seek(strtab[4])
            names = f.read(strtab[5])
        self.sections = []
        for i, (name, typ, flags, addr, off, size, link, info, align, entsize) in enumerate(raw):
            end = names.index(b"\0", name)
            self.sections.append({
                "index": i, "name": names[name:end].decode("ascii"), "type": typ,
                "flags": flags, "addr": addr, "offset": off, "size": size,
            })

    def section(self, name: str) -> dict:
        for s in self.sections:
            if s["name"] == name:
                return s
        sys.exit(f"{self.path}: no section {name}")


SHT_NOBITS = 8


def copy_range(path: str, off: int, size: int, out) -> None:
    with open(path, "rb") as f:
        f.seek(off)
        left = size
        while left:
            chunk = f.read(min(left, 1 << 20))
            if not chunk:
                sys.exit(f"{path}: short read at {off + size - left:#x}")
            out.write(chunk)
            left -= len(chunk)


def sha256_range(path: str, off: int, size: int) -> str:
    h = hashlib.sha256()

    class W:
        write = h.update

    copy_range(path, off, size, W)
    return h.hexdigest()


# ---------------------------------------------------------------- subcommands


def cmd_info(a) -> None:
    """Print `offset size addr` of a section (hex, no prefix) for shell use."""
    s = Elf(a.elf).section(a.section)
    emit(f"{s['offset']:x} {s['size']:x} {s['addr']:x}")


def cmd_phdr(a) -> None:
    """Print `offset filesz vaddr` of program header N."""
    p = Elf(a.elf).phdrs[a.index]
    emit(f"{p[2]:x} {p[5]:x} {p[3]:x}")


def cmd_slice(a) -> None:
    if a.section:
        s = Elf(a.elf).section(a.section)
        off, size = s["offset"], s["size"]
    else:
        off, size = int(a.offset, 0), int(a.size, 0)
    copy_range(a.elf, off, size, OUT)


def cmd_hashes(a) -> None:
    elf = Elf(a.elf)
    if a.what == "sections":
        emit("index\tname\toffset\tsize\taddr\tsha256")
        for s in elf.sections:
            size = 0 if s["type"] == SHT_NOBITS else s["size"]
            digest = sha256_range(a.elf, s["offset"], size)
            emit(f"{s['index']}\t{s['name']}\t0x{s['offset']:x}\t0x{size:x}\t0x{s['addr']:x}\t{digest}")
    else:
        emit("index\ttype\toffset\tfilesz\tvaddr\tsha256")
        for i, (typ, _flags, off, vaddr, _pa, filesz, _memsz, _al) in enumerate(elf.phdrs):
            emit(f"{i}\t0x{typ:08x}\t0x{off:x}\t0x{filesz:x}\t0x{vaddr:x}\t{sha256_range(a.elf, off, filesz)}")


STMT_RE = re.compile(r"DW_AT_stmt_list\s*\((0x[0-9a-fA-F]+)\)")


def cmd_line_copy(a) -> None:
    """Copy every CU's line table into one contiguous blob; write the offset map and the gaps."""
    sec = Elf(a.elf).section(".debug_line")
    offsets = sorted({int(m.group(1), 16) for m in STMT_RE.finditer(Path(a.cu_list).read_text("utf-8"))})
    with open(a.elf, "rb") as f:
        f.seek(sec["offset"])
        data = f.read(sec["size"])
    tables = []
    for off in offsets:
        (length,) = struct.unpack_from("<I", data, off)
        if length >= 0xFFFFFFF0:
            sys.exit(f"line table at {off:#x}: DWARF64 or reserved length {length:#x}")
        tables.append((off, 4 + length))
    with open(a.out, "wb") as blob, open(a.map, "w", encoding="utf-8", newline="\n") as m, \
            open(a.gaps, "w", encoding="utf-8", newline="\n") as g:
        m.write("orig_offset\tnew_offset\tlength\n")
        g.write("gap_offset\tlength\tnonzero\tfirst_bytes\n")
        new = 0
        pos = 0
        for off, length in tables:
            if off < pos:
                sys.exit(f"line table at {off:#x} overlaps the previous one (ends {pos:#x})")
            if off > pos:
                gap = data[pos:off]
                g.write(f"0x{pos:x}\t{len(gap)}\t{int(any(gap))}\t{gap[:16].hex()}\n")
            blob.write(data[off:off + length])
            m.write(f"0x{off:x}\t0x{new:x}\t{length}\n")
            new += length
            pos = off + length
        if pos < len(data):
            gap = data[pos:]
            g.write(f"0x{pos:x}\t{len(gap)}\t{int(any(gap))}\t{gap[:16].hex()}\n")
    print(f"tables={len(tables)} bytes={new}", file=sys.stderr)


STR_RE = re.compile(rb"^\s*([0-9a-f]+) (.*)$")


def cmd_rebase_strings(a) -> None:
    base = int(a.base, 16)
    OUT.write(b"vaddr\tstring\n")
    for raw in sys.stdin.buffer:
        m = STR_RE.match(raw.rstrip(b"\n"))
        if not m:
            sys.exit(f"unexpected strings line: {raw[:80]!r}")
        OUT.write(b"0x%x\t%s\n" % (base + int(m.group(1), 16), m.group(2).replace(b"\t", b"\\t")))


def parse_relocs(path: str):
    """Yield dicts from `orbis-bin -r` output (entries of Offset/Addend/Type and Sym Index|Name)."""
    cur: dict = {}
    section = ""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("Relocation section:"):
                section = line.split(":", 1)[1].strip()
            elif line.startswith("Entry"):
                if cur:
                    yield cur
                cur = {"table": section, "entry": line.split()[1].rstrip(":")}
            elif line.startswith("  ") and ":" in line:
                k, v = line.strip().split(":", 1)
                cur[k.strip()] = v.strip()
    if cur:
        yield cur


def cmd_string_refs(a) -> None:
    strings: dict[int, bytes] = {}
    with open(a.strings, "rb") as f:
        next(f)
        for raw in f:
            vaddr, _, s = raw.rstrip(b"\n").partition(b"\t")
            strings[int(vaddr, 16)] = s
    OUT.write(b"# INFERRED: R_X86_64_RELATIVE slots whose addend equals the start of a .rodata string\n")
    OUT.write(b"slot\ttarget\tstring\n")
    n = 0
    for r in parse_relocs(a.relocs):
        if r.get("Type") != "R_X86_64_RELATIVE":
            continue
        target = int(r["Addend"], 16)
        s = strings.get(target)
        if s is not None:
            OUT.write(b"0x%x\t0x%x\t%s\n" % (int(r["Offset"], 16), target, s))
            n += 1
    print(f"string_refs={n}", file=sys.stderr)


REG_RE = re.compile(r"\bDW_OP_b?reg(?:x)?\d*\s+([A-Z][A-Z0-9]+)\b")


def cmd_register_usage(a) -> None:
    counts: Counter[tuple[str, str]] = Counter()
    op_re = re.compile(r"\b(DW_OP_b?regx?\d*)\s+([A-Z][A-Z0-9]+)\b")
    with open(a.debug_loc, encoding="utf-8", errors="replace") as f:
        for line in f:
            for op, reg in op_re.findall(line):
                counts[("breg" if op.startswith("DW_OP_breg") else "reg", reg)] += 1
    emit("kind\tregister\tcount")
    for (kind, reg), c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        emit(f"{kind}\t{reg}\t{c}")


# ---------------------------------------------------------------- oracles


def oracle_dynamic(path: str) -> None:
    emit("index\ttag\tdata\tinterpretation")
    with open(path, encoding="utf-8") as f:
        next(f)
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            tag, data, interp = line[:26].strip(), line[26:46].strip(), line[46:].strip()
            emit(f"{i}\t{tag}\t{data}\t{interp}")


PH_HEAD = re.compile(r"^0x([0-9A-F]+) - (.+)$")
PH_FIELD = re.compile(r"([A-Za-z ]+?):\s+(0x[0-9A-F]+|[A-Za-z, ]+?)(?:\s*\||$)")


def oracle_phdrs(path: str) -> None:
    emit("index\ttype\tflags\toffset\tvaddr\tfilesz\tmemsz\talign")
    cur = None
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = PH_HEAD.match(line)
            if m:
                cur = {"index": int(m.group(1), 16), "type": m.group(2)}
                rows.append(cur)
            elif cur is not None and line.startswith("  "):
                for k, v in PH_FIELD.findall(line):
                    cur[k.strip()] = v.strip()
    for r in rows:
        emit("\t".join(str(r.get(k, "")) for k in
                       ("index", "type", "Flags", "Offset", "Virtual Addr", "File Size", "Image Size", "Align")))


DYN_HEAD = re.compile(r"^0x([0-9A-Fa-f]+) - (.*?):\s*$")


def oracle_dynsym(path: str) -> None:
    emit("index\tnid_or_name\tresolved\tlibrary\tmodule\tbinding\ttype")
    cur = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = DYN_HEAD.match(line)
            if m:
                name = m.group(2)
                nid, resolved, lib, mod = name, "", "", ""
                mm = re.match(r"^(\S+) \((.*)\)$", name)
                if mm:
                    nid = mm.group(1)
                    parts = mm.group(2).split("#")
                    resolved = parts[0]
                    lib = parts[1] if len(parts) > 1 else ""
                    mod = parts[2] if len(parts) > 2 else ""
                cur = [str(int(m.group(1), 16)), nid, resolved, lib, mod, "", ""]
            elif cur is not None and "Binding:" in line:
                fields = dict(p.strip().split(": ", 1) for p in line.split("|"))
                cur[5], cur[6] = fields.get("Binding", ""), fields.get("Type", "")
                emit("\t".join(cur))
                cur = None


def oracle_relocs(path: str) -> None:
    emit("table\tentry\toffset\ttype\taddend\tsymbol")
    n_rel = 0
    for r in parse_relocs(path):
        t = r.get("Type", "")
        if t == "R_X86_64_RELATIVE":
            n_rel += 1
            if n_rel % 500 != 1:
                continue
        emit("\t".join([r["table"], r["entry"], r.get("Offset", ""), t, r.get("Addend", ""),
                        r.get("Sym Name", r.get("Sym Index", ""))]))


def oracle_stack(path: str) -> None:
    emit("rank\tsize\tfunction")
    with open(path, encoding="utf-8") as f:
        rows = [l.rstrip("\n") for l in f if re.match(r"^\d+\s", l) or l.startswith("??")]
    for i, row in enumerate(rows):
        if i < 50 or i % 250 == 0:
            size, _, fn = row.partition(" ")
            emit(f"{i}\t{size}\t{fn.strip()}")


def oracle_head(path: str, n: int) -> None:
    with open(path, "rb") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            OUT.write(line)


def cmd_oracle(a) -> None:
    match a.kind:
        case "dynamic":
            oracle_dynamic(a.input)
        case "phdrs":
            oracle_phdrs(a.input)
        case "dynsym":
            oracle_dynsym(a.input)
        case "relocations":
            oracle_relocs(a.input)
        case "stack":
            oracle_stack(a.input)
        case "head":
            oracle_head(a.input, a.lines)


# ---------------------------------------------------------------- stand-ins for local dumps

FUNC_RE = re.compile(rb"^([0-9a-f]{8,16}) <(.*)>:\s*$")
INSN_RE = re.compile(rb"^\s+[0-9a-f]+:\s")
DE_HEAD_RE = re.compile(rb"^(\S.*?):\s*$")


def cmd_standin(a) -> None:
    """Summaries of a local-only dump read from stdin."""
    src = sys.stdin.buffer
    if a.kind == "disassembly":
        emit("address\tinstructions\tfunction")
        addr, name, n, total = None, b"", 0, 0
        for line in src:
            m = FUNC_RE.match(line)
            if m:
                if addr is not None:
                    OUT.write(b"0x%s\t%d\t%s\n" % (addr.lstrip(b"0") or b"0", n, name))
                addr, name, n = m.group(1), m.group(2), 0
            elif INSN_RE.match(line):
                n += 1
                total += 1
        if addr is not None:
            OUT.write(b"0x%s\t%d\t%s\n" % (addr.lstrip(b"0") or b"0", n, name))
        print(f"instructions={total}", file=sys.stderr)
    else:  # everything: line count per top-level heading
        emit("line\tlines_until_next\theading")
        last, last_line, i = None, 0, 0
        for i, line in enumerate(src, 1):
            if line[:1] not in b" \t\r\n" and DE_HEAD_RE.match(line) and len(line) < 120:
                if last is not None:
                    OUT.write(b"%d\t%d\t%s\n" % (last_line, i - last_line, last))
                last, last_line = line.rstrip(), i
        if last is not None:
            OUT.write(b"%d\t%d\t%s\n" % (last_line, i - last_line + 1, last))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(required=True)

    s = sub.add_parser("info"); s.add_argument("elf"); s.add_argument("section"); s.set_defaults(fn=cmd_info)
    s = sub.add_parser("phdr"); s.add_argument("elf"); s.add_argument("index", type=int); s.set_defaults(fn=cmd_phdr)
    s = sub.add_parser("slice"); s.add_argument("elf"); s.add_argument("--section")
    s.add_argument("--offset"); s.add_argument("--size"); s.set_defaults(fn=cmd_slice)
    s = sub.add_parser("hashes"); s.add_argument("elf"); s.add_argument("what", choices=["sections", "segments"])
    s.set_defaults(fn=cmd_hashes)
    s = sub.add_parser("line-copy")
    for n in ("elf", "cu_list", "out", "map", "gaps"):
        s.add_argument(n)
    s.set_defaults(fn=cmd_line_copy)
    s = sub.add_parser("rebase-strings"); s.add_argument("base"); s.set_defaults(fn=cmd_rebase_strings)
    s = sub.add_parser("string-refs"); s.add_argument("relocs"); s.add_argument("strings")
    s.set_defaults(fn=cmd_string_refs)
    s = sub.add_parser("register-usage"); s.add_argument("debug_loc"); s.set_defaults(fn=cmd_register_usage)
    s = sub.add_parser("oracle"); s.add_argument("kind", choices=["dynamic", "phdrs", "dynsym", "relocations", "stack", "head"])
    s.add_argument("input"); s.add_argument("--lines", type=int, default=1000); s.set_defaults(fn=cmd_oracle)
    s = sub.add_parser("standin"); s.add_argument("kind", choices=["disassembly", "everything"])
    s.set_defaults(fn=cmd_standin)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
