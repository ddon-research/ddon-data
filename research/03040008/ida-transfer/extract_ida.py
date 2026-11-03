"""Fact extractor for the PC 03040008 and PS4 02020005 IDA databases (spec 007 T004).

Run inside IDA (ida-mcp ``execute_python`` or headless ``idat -S``) with one call::

    exec(open(path).read(), {"OUT": "D:/.../pc.jsonl", "SIDE": "pc"})

Optional globals: ``DEPTH`` (callee depth, default 3), ``ROOTS`` (extra root VAs),
``ROOT_PATTERNS`` (PS4 root regexes over the demangled qualified name),
``PC_WRITE_ENTRY_OVERRIDE`` (the packet write entry whose callers are PC roots).
Headless batch (read-only): ``idat -A -L<log> -S"extract_ida.py <OUT> <SIDE>" <db>`` (arguments via
``idc.ARGV``); it prints ``extract_ida summary: {...}`` to the log, discards the session
(``DBFL_KILL``, the packed database is not rewritten) and exits with ``idc.qexit``.

The database is only read: no renames, types, comments, decompilation or saves.

Output: one JSONL file. Line 1 is the header (database identity, script version, parameters);
then ``table`` records (PC handler table), ``missing_root`` records (a root VA that is not a function
start: never replaced by the enclosing function), ``function`` records (one per function in scope),
and a final ``summary`` record with counts. The pure helpers below (no IDA import) are unit-tested in
``tests/test_extract_ida.py``; the IDA-facing code is the ``_ida_*`` functions and ``main``.

The handler-table reading (record layout, initializer literal-store proof) is adapted from
ddon-hook ``scripts/ida_packet_dispatch.py`` (C:/Users/morph/CLionProjects/ddon-hook, read-only).
"""

from __future__ import annotations

import json
import os
import re

SCRIPT_VERSION = "2"

# --- PC handler table (T002 audit: 74 groups, 1,041 records, 1,040 distinct callbacks) ---------
PC_GROUP_TABLE = 0x1BC0110
PC_GROUP_COUNT = 74
PC_RECORD_STRIDE = 0x18
PC_INITIALIZER_RANGE = (0x1A27560, 0x1A36540 + 1)  # 74 initializers, first and last start
PC_WRITE_ENTRY = 0x8BCBB0  # nUserSession::CPacket::WritePacket
PC_EXPECTED = {"table_records": 1041, "table_callbacks": 1040, "initializers": 74}
PC_CODE_RANGE = (0x401000, 0x1AE0000)  # callback literal must point into code (ddon-hook bound)

PS4_ROOT_PATTERNS = (
    r"^cSeed\w*Connection::OnPacket_\w+$",
    r"^cSeed\w*Connection::Send_\w+$",
    r"(?:^|::)CPacket_\w+::(?:ReadPacket|WritePacket)$",
)
DEFAULT_DEPTH = 3
MAX_CALLERS = 20
ARG_WINDOW = 32  # instructions scanned back from a call for its arguments

PS4_ARG_REGS = ("rdi", "rsi", "rdx", "rcx", "r8", "r9") + tuple(f"xmm{i}" for i in range(8))
_REG_ALIASES = {
    "rax": ("eax", "ax", "al", "ah"), "rcx": ("ecx", "cx", "cl", "ch"),
    "rdx": ("edx", "dx", "dl", "dh"), "rbx": ("ebx", "bx", "bl", "bh"),
    "rsp": ("esp", "sp", "spl"), "rbp": ("ebp", "bp", "bpl"),
    "rsi": ("esi", "si", "sil"), "rdi": ("edi", "di", "dil"),
}
_CANON = {alias: full for full, aliases in _REG_ALIASES.items() for alias in aliases}
_DEFAULT_NAME = re.compile(r"^sub_[0-9A-Fa-f]+$")


# --- pure helpers -------------------------------------------------------------------------------

def canon_reg(name: str | None) -> str | None:
    """Full 64-bit register name for any width alias (``edi``/``dil`` -> ``rdi``, ``r8d`` -> ``r8``)."""
    if not name:
        return None
    name = name.lower()
    if name in _CANON:
        return _CANON[name]
    m = re.fullmatch(r"(r(?:8|9|1[0-5]))[dwb]?", name)
    if m:
        return m.group(1)
    m = re.fullmatch(r"[xyz]mm(\d+)", name)
    if m:
        return f"xmm{m.group(1)}"
    return name


def is_default_name(name: str) -> bool:
    return bool(_DEFAULT_NAME.match(name or ""))


def interesting_constant(value: int, bits: int, is_address: bool) -> bool:
    """An immediate worth fingerprinting: not an address and not in 0..255 (as unsigned)."""
    if is_address:
        return False
    value &= (1 << bits) - 1
    return not 0 <= value <= 255


def qualified_from_demangled(text: str | None) -> str | None:
    """``A::B::f(int, char) const`` -> ``A::B::f``; keeps template arguments and ``operator()``."""
    if not text:
        return text
    text = text.strip()
    if not text.endswith(")") and not text.endswith(" const"):
        return text
    end = text.rfind(")")
    depth = 0
    for i in range(end, -1, -1):
        c = text[i]
        if c == ")":
            depth += 1
        elif c == "(":
            depth -= 1
            if depth == 0:
                head = text[:i]
                if head.endswith("operator()"):
                    return head
                if head.endswith("operator"):  # "operator()" itself split: "operator(" ")"
                    return head + "()"
                return head
    return text


def match_roots(names: dict[int, str], patterns) -> list[int]:
    """VAs whose qualified name matches any root pattern (sorted)."""
    regs = [re.compile(p) for p in patterns]
    return sorted(va for va, n in names.items() if n and any(r.search(n) for r in regs))


def scope_closure(roots, callees_of, depth: int) -> dict[int, int]:
    """Breadth-first closure: VA -> distance from the nearest root (0 = root), up to ``depth``.

    ``callees_of(va)`` returns the direct callee function VAs of ``va``; it is called once per
    function reached at distance < depth.
    """
    dist = {va: 0 for va in roots}
    frontier = sorted(dist)
    for level in range(1, depth + 1):
        nxt = set()
        for va in frontier:
            for callee in callees_of(va):
                if callee not in dist:
                    dist[callee] = level
                    nxt.add(callee)
        frontier = sorted(nxt)
        if not frontier:
            break
    return dist


def partition_roots(reason: dict[int, str], func_start) -> tuple[list[int], list[dict]]:
    """Split roots into function starts and ``missing_root`` records.

    ``func_start(va)`` is the start of the function containing ``va`` (None outside any). A root
    that is not itself a function start is reported, never replaced by its enclosing function.
    """
    present, missing = [], []
    for va in sorted(reason):
        start = func_start(va)
        if start == va:
            present.append(va)
            continue
        missing.append({"kind": "missing_root", "va": va,
                        "missing": "no-function" if start is None else "inside-function",
                        "enclosing": start, "root": reason[va]})
    return present, missing


def plan_scope(reason: dict[int, str], func_start, callees_of, depth: int) -> tuple[dict[int, int], list[dict]]:
    """Scope closure over the roots that are function starts; missing roots are not expanded."""
    present, missing = partition_roots(reason, func_start)
    return scope_closure(present, callees_of, depth), missing


def pc_call_arguments(window: list[dict]) -> dict:
    """Bytes pushed and whether ecx is written in the instructions before a call (PC, 32-bit).

    ``window`` holds the instructions between the previous call (or block start) and the call,
    in address order; each is ``{"mnem", "ops": [{"type", "reg", "value"}...], "writes_ecx"}``.
    ``push`` counts 4 bytes, ``sub esp, imm`` its immediate. A ``pop`` or ``add esp`` resets
    nothing: the window already stops at the previous call.
    """
    pushed = 0
    pushes = 0
    ecx = False
    for ins in window:
        mnem = ins["mnem"]
        ops = ins.get("ops", [])
        if mnem == "push":
            pushed += 4
            pushes += 1
        elif mnem == "sub" and len(ops) == 2 and ops[0].get("type") == "reg" and ops[0].get("reg") == "rsp" \
                and ops[1].get("type") == "imm":
            pushed += ops[1]["value"]
        elif mnem == "add" and len(ops) == 2 and ops[0].get("type") == "reg" and ops[0].get("reg") == "rsp" \
                and ops[1].get("type") == "imm":
            pushed -= ops[1]["value"]
        if ins.get("writes_ecx"):
            ecx = True
    return {"pushed_bytes": pushed, "pushes": pushes, "ecx_loaded": ecx}


def ps4_call_arguments(window: list[dict]) -> list[str]:
    """Argument registers written before a call (PS4, SysV x86-64), in ABI order."""
    written = set()
    for ins in window:
        for reg in ins.get("writes", ()):
            reg = canon_reg(reg)
            if reg in PS4_ARG_REGS:
                written.add(reg)
    return [r for r in PS4_ARG_REGS if r in written]


def reads_before_write(entry, succs, effects) -> bool:
    """True when some path from ``entry`` reads the register before writing it.

    ``succs(block)`` gives successor blocks; ``effects(block)`` the ordered per-instruction effects
    (``"read"``, ``"write"``, ``"readwrite"``, ``"clobber"`` or None). A write or clobber (call) ends
    the path; ``readwrite`` counts as a read.
    """
    seen = set()
    stack = [entry]
    while stack:
        block = stack.pop()
        if block in seen:
            continue
        seen.add(block)
        stopped = False
        for eff in effects(block):
            if eff in ("read", "readwrite"):
                return True
            if eff in ("write", "clobber"):
                stopped = True
                break
        if not stopped:
            stack.extend(succs(block))
    return False


def resolve_callback(window: list[dict], record_ea: int, code_range=PC_CODE_RANGE) -> dict:
    """Prove the callback stored into a handler record from its initializer window.

    The initializer writes ``mov [esp], imm`` (a literal), copies it with ``movq xmmN, [esp]`` and
    stores ``movq [record], xmmN``. ``window`` ends with that store (up to 8 instructions before
    it); operands are ``{"type": "imm"|"reg"|"mem"|"phrase"|"displ", "reg", "addr", "value"}`` with
    ``reg`` canonical (``rsp``). Returns ``{"callback", "store_ea", "proved", "literal"}``; a proved
    literal 0 is the null record (callback None).
    """
    out = {"callback": None, "store_ea": None, "proved": False, "literal": None}
    if not window:
        return out
    last = window[-1]
    lops = last.get("ops", [])
    if not (last["mnem"] == "movq" and len(lops) == 2 and lops[0]["type"] == "mem"
            and lops[0].get("addr") == record_ea and lops[1]["type"] == "reg"):
        return out
    xmm = lops[1]["reg"]

    def esp0(op):
        return op["type"] in ("phrase", "displ") and op.get("reg") == "rsp" and op.get("addr", 0) == 0

    copies = [i for i, ins in enumerate(window[:-1])
              if ins["mnem"] == "movq" and len(ins.get("ops", [])) == 2
              and ins["ops"][0]["type"] == "reg" and ins["ops"][0]["reg"] == xmm and esp0(ins["ops"][1])]
    if not copies:
        return out
    copy_i = copies[-1]
    stores = [i for i, ins in enumerate(window[:copy_i])
              if ins["mnem"] == "mov" and ins.get("ops") and esp0(ins["ops"][0])]
    if not stores:
        return out
    store = window[stores[-1]]
    if len(store["ops"]) != 2 or store["ops"][1]["type"] != "imm":
        return out
    clobbered = any(ins.get("ops") and ins["ops"][0]["type"] == "reg" and ins["ops"][0]["reg"] == xmm
                    for ins in window[copy_i + 1:-1])
    if clobbered:
        return out
    value = store["ops"][1]["value"]
    out["literal"] = value
    out["store_ea"] = store["ea"]
    if value == 0:
        out["proved"] = True
    elif code_range[0] <= value < code_range[1]:
        out["proved"] = True
        out["callback"] = value
    return out


def table_key(raw: bytes) -> tuple[int, int]:
    """(id, sub) of a 24-byte handler record: u16 id at +0x10, u8 sub at +0x12."""
    return int.from_bytes(raw[16:18], "little"), raw[18]


def write_jsonl(path: str, header: dict, records) -> int:
    """Write header + records as JSON lines atomically (temp file, then replace). Returns lines."""
    tmp = f"{path}.tmp"
    lines = 0
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for rec in [header, *records] if not hasattr(records, "__next__") else _chain(header, records):
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            fh.write("\n")
            lines += 1
    os.replace(tmp, path)
    return lines


def _chain(first, rest):
    yield first
    yield from rest


# --- IDA side -------------------------------------------------------------------------------------

def _ida():
    import ida_bytes
    import ida_funcs
    import ida_gdl
    import ida_ida
    import ida_idp
    import ida_kernwin
    import ida_nalt
    import ida_name
    import ida_segment
    import ida_ua
    import idautils
    import idc

    return {
        "ida_bytes": ida_bytes, "ida_funcs": ida_funcs, "ida_gdl": ida_gdl, "ida_ida": ida_ida,
        "ida_idp": ida_idp, "ida_kernwin": ida_kernwin, "ida_nalt": ida_nalt, "ida_name": ida_name,
        "ida_segment": ida_segment, "ida_ua": ida_ua, "idautils": idautils, "idc": idc,
    }


class _Db:
    """Thin read-only view over the IDA modules, with per-run caches."""

    def __init__(self, side: str):
        self.m = _ida()
        self.side = side
        self.bits = 64 if self.m["ida_ida"].inf_is_64bit() else 32
        self.ptr = self.bits // 8
        ua = self.m["ida_ua"]
        self.optype = {ua.o_reg: "reg", ua.o_mem: "mem", ua.o_phrase: "phrase", ua.o_displ: "displ",
                       ua.o_imm: "imm", ua.o_near: "near", ua.o_far: "far"}
        self._strings: dict[int, str | None] = {}

    # identity
    def header(self, params: dict) -> dict:
        m = self.m
        sha = m["ida_nalt"].retrieve_input_file_sha256()
        return {
            "kind": "header", "script": "extract_ida", "script_version": SCRIPT_VERSION,
            "side": self.side, "database_path": m["idc"].get_idb_path(),
            "idb_path": m["idc"].get_idb_path(),
            "input_path": m["ida_nalt"].get_input_file_path(),
            "input_sha256": sha.hex() if sha else None,
            "bitness": self.bits, "image_base": m["ida_nalt"].get_imagebase(),
            "ida_version": m["ida_kernwin"].get_kernel_version(), "params": params,
        }

    # instructions
    def insn(self, ea):
        ins = self.m["ida_ua"].insn_t()
        if self.m["ida_ua"].decode_insn(ins, ea) <= 0:
            return None
        return ins

    def reg_name(self, reg: int, dtype) -> str | None:
        size = self.m["ida_ua"].get_dtype_size(dtype)
        return canon_reg(self.m["ida_idp"].get_reg_name(reg, size if size in (1, 2, 4, 8, 16) else self.ptr))

    def ops(self, ins) -> list[dict]:
        out = []
        for op in ins.ops:
            if op.type == self.m["ida_ua"].o_void:
                break
            kind = self.optype.get(op.type, f"t{op.type}")
            d = {"type": kind}
            if kind == "reg":
                d["reg"] = self.reg_name(op.reg, op.dtype)
            elif kind in ("phrase", "displ"):
                ua = self.m["ida_ua"]
                d["reg"] = self.reg_name(op.phrase, ua.dt_qword if self.bits == 64 else ua.dt_dword)
                d["addr"] = op.addr
            elif kind == "imm":
                d["value"] = op.value
            elif kind in ("mem", "near", "far"):
                d["addr"] = op.addr
            out.append(d)
        return out

    def mnem(self, ins) -> str:
        return (ins.get_canon_mnem() or "").lower()

    def writes(self, ins, ops) -> list[str]:
        """Registers an instruction writes (explicit operand 0/1 with CF_CHG), plus pop/xor idioms."""
        idp = self.m["ida_idp"]
        feat = ins.get_canon_feature()
        chg = (idp.CF_CHG1, idp.CF_CHG2)
        regs = []
        for i, op in enumerate(ops[:2]):
            if op["type"] == "reg" and feat & chg[i]:
                regs.append(op["reg"])
        return regs

    def reads_reg(self, ins, ops, reg: str) -> bool:
        idp = self.m["ida_idp"]
        feat = ins.get_canon_feature()
        use = (idp.CF_USE1, idp.CF_USE2, idp.CF_USE3)
        mnem = self.mnem(ins)
        for i, op in enumerate(ops[:3]):
            if op["type"] == "reg" and op["reg"] == reg and feat & use[i]:
                if i == 1 and mnem in ("xor", "sub") and ops[0].get("reg") == reg:
                    return False  # zeroing idiom
                if i == 0 and mnem in ("xor", "sub") and len(ops) > 1 and ops[1].get("reg") == reg:
                    return False
                return True
            if op["type"] in ("phrase", "displ") and reg in self._mem_regs(ins.ea, i):
                return True
        if mnem.startswith("rep") or mnem in ("loop", "loope", "loopne", "jecxz", "jrcxz"):
            return reg == "rcx"
        if reg == "rcx" and mnem in ("movs", "stos", "cmps", "scas", "lods", "ins", "outs") \
                and "rep" in (self.m["idc"].GetDisasm(ins.ea) or "").lower():
            return True  # rep/repne prefix reads the count
        return False

    def _mem_regs(self, ea, n) -> set[str]:
        text = (self.m["idc"].print_operand(ea, n) or "").lower()
        return {canon_reg(t) for t in re.findall(r"[a-z][a-z0-9]+", text)}

    # strings and data
    def string_at(self, ea) -> str | None:
        if ea in self._strings:
            return self._strings[ea]
        b = self.m["ida_bytes"]
        text = None
        if b.is_strlit(b.get_flags(ea)):
            raw = b.get_strlit_contents(ea, -1, self.m["ida_nalt"].get_str_type(ea))
            if raw is not None:
                text = raw.decode("utf-8", "replace")
        self._strings[ea] = text
        return text

    def is_address(self, value: int) -> bool:
        return self.m["ida_segment"].getseg(value) is not None

    def func(self, ea):
        return self.m["ida_funcs"].get_func(ea)

    def func_start(self, ea):
        f = self.func(ea)
        return None if f is None else f.start_ea

    def name(self, ea) -> str:
        return self.m["ida_name"].get_name(ea) or ""

    def demangled(self, ea) -> str | None:
        nm = self.name(ea)
        dem = self.m["ida_name"].demangle_name(nm, 0) if nm else None
        return qualified_from_demangled(dem) if dem else nm

    def items(self, f):
        return list(self.m["idautils"].FuncItems(f.start_ea))

    def block_starts(self, f) -> set[int]:
        return {b.start_ea for b in self.m["ida_gdl"].FlowChart(f)}


def _ida_function(db: _Db, va: int, depth: int, roots_reason: dict) -> dict | None:
    m = db.m
    f = db.func(va)
    if f is None or f.start_ea != va:
        return None
    idc = m["idc"]
    flags_has_user = m["ida_bytes"].has_user_name(m["ida_bytes"].get_flags(va))
    name = db.name(va)
    items = db.items(f)
    starts = db.block_starts(f)
    rec = {
        "kind": "function", "va": va, "name": name,
        "default_name": is_default_name(name) and not flags_has_user,
        "demangled": db.demangled(va) if db.side == "ps4" else None,
        "size": sum(c[1] - c[0] for c in m["idautils"].Chunks(va)),
        "chunks": len(list(m["idautils"].Chunks(va))),
        "instructions": len(items), "depth": depth, "root": roots_reason.get(va),
        "prototype": idc.get_type(va), "prototype_user": bool(m["ida_nalt"].is_userti(va)),
    }
    calls, strings, data, consts, rets = [], [], [], [], []
    window: list[dict] = []
    seen_data = set()
    for ea in items:
        ins = db.insn(ea)
        if ins is None:
            continue
        if ea in starts:
            window = []
        mnem = db.mnem(ins)
        ops = db.ops(ins)
        is_call = m["ida_idp"].is_call_insn(ins)
        is_jmp = mnem == "jmp"
        if is_call or (is_jmp and ops and ops[0]["type"] == "near"):
            target = ops[0].get("addr") if ops and ops[0]["type"] in ("near", "far") else None
            if is_jmp and (target is None or db.func_start(target) == va or db.func_start(target) != target):
                target = None  # an intra-function jump, not a tail call
                is_tail = False
            else:
                is_tail = is_jmp
            if is_call or is_tail:
                site = {"site": ea, "target": target if target is not None else "indirect"}
                if is_tail:
                    site["tail"] = True
                if target is None and ops and ops[0]["type"] == "mem":
                    site["via_mem"] = ops[0]["addr"]
                if db.side == "pc":
                    site.update(pc_call_arguments(window[-ARG_WINDOW:]))
                else:
                    site["arg_regs"] = ps4_call_arguments(window[-ARG_WINDOW:])
                calls.append(site)
                window = []
                continue
        if mnem in ("retn", "ret") and ops and ops[0]["type"] == "imm":
            rets.append(ops[0]["value"])
        for i, op in enumerate(ops):
            if op["type"] == "imm":
                addr = db.is_address(op["value"])
                if not addr and not (i == 1 and ops[0].get("type") == "reg" and ops[0].get("reg") == "rsp") \
                        and interesting_constant(op["value"], db.bits, False):
                    consts.append(op["value"] & ((1 << db.bits) - 1))
        for t in m["idautils"].DataRefsFrom(ea):
            if t in seen_data:
                continue
            seen_data.add(t)
            s = db.string_at(t)
            if s is not None:
                strings.append({"ea": t, "text": s})
            elif db.func_start(t) is None:
                data.append(t)
        entry = {"mnem": mnem, "ops": ops}
        if db.side == "pc":
            entry["writes_ecx"] = "rcx" in db.writes(ins, ops)
        else:
            entry["writes"] = db.writes(ins, ops)
        window.append(entry)
    rec.update({"calls": calls, "strings": strings, "data_refs": sorted(data),
                "constants": sorted(set(consts)), "ret_imm": sorted(set(rets))})
    callers = sorted({x.frm for x in m["idautils"].XrefsTo(va) if x.iscode})
    caller_funcs = sorted({s for s in (db.func_start(c) for c in callers) if s is not None})
    rec["caller_sites"] = len(callers)
    rec["callers_count"] = len(caller_funcs)
    rec["callers"] = caller_funcs[:MAX_CALLERS]
    if db.side == "pc":
        rec["ecx_read_before_write"] = _ida_ecx_rbw(db, f)
        rec["annotations"] = _ida_annotations(db, f, items)
    return rec


def _ida_ecx_rbw(db: _Db, f) -> bool:
    fc = db.m["ida_gdl"].FlowChart(f)
    blocks = {b.start_ea: b for b in fc}

    def succs(start):
        return [s.start_ea for s in blocks[start].succs()]

    def effects(start):
        b = blocks[start]
        ea = b.start_ea
        out = []
        while ea < b.end_ea:
            ins = db.insn(ea)
            if ins is None:
                break
            ops = db.ops(ins)
            if db.m["ida_idp"].is_call_insn(ins):
                out.append("clobber")
            elif db.reads_reg(ins, ops, "rcx"):
                out.append("readwrite" if "rcx" in db.writes(ins, ops) else "read")
            elif "rcx" in db.writes(ins, ops):
                out.append("write")
            else:
                out.append(None)
            ea += ins.size
        return out

    return reads_before_write(f.start_ea, succs, effects)


def _ida_annotations(db: _Db, f, items) -> dict:
    """Non-default local names/types and comments of a PC function, for apply to preserve."""
    idc = db.m["idc"]
    out = {"function_comment": idc.get_func_cmt(f.start_ea, 0) or None,
           "function_comment_repeatable": idc.get_func_cmt(f.start_ea, 1) or None,
           "insn_comments": [], "lvars": None, "hexrays_comments": None}
    for ea in items:
        for rpt in (0, 1):
            c = idc.get_cmt(ea, rpt)
            if c:
                out["insn_comments"].append({"ea": ea, "repeatable": bool(rpt), "text": c})
    try:
        import ida_hexrays
    except ImportError:
        return out
    try:
        if not ida_hexrays.init_hexrays_plugin():
            return out
        lv = ida_hexrays.lvar_uservec_t()
        if ida_hexrays.restore_user_lvar_settings(lv, f.start_ea):
            lvars = []
            for s in lv.lvvec:
                ll = s.ll
                loc = None
                if ll.is_stk_var():
                    loc = {"stkoff": ll.get_stkoff()}
                elif ll.is_reg1():
                    loc = {"reg": ll.get_reg1()}
                lvars.append({"name": s.name or None, "type": str(s.type) if s.type and not s.type.empty() else None,
                              "comment": s.cmt or None, "defea": ll.defea, "location": loc})
            out["lvars"] = lvars
        cm = ida_hexrays.restore_user_cmts(f.start_ea)
        if cm is not None:
            rows = []
            it = ida_hexrays.user_cmts_begin(cm)
            while it != ida_hexrays.user_cmts_end(cm):
                loc = ida_hexrays.user_cmts_first(it)
                rows.append({"ea": loc.ea, "itp": loc.itp, "text": str(ida_hexrays.user_cmts_second(it))})
                it = ida_hexrays.user_cmts_next(it)
            ida_hexrays.user_cmts_free(cm)
            out["hexrays_comments"] = rows
    except Exception as exc:  # report, never guess
        out["hexrays_error"] = repr(exc)
    return out


def _ida_pc_table(db: _Db) -> tuple[list[dict], set[int]]:
    m = db.m
    b = m["ida_bytes"]
    records, inits = [], set()
    for group in range(PC_GROUP_COUNT):
        ea = PC_GROUP_TABLE + group * 8
        ptr, count = b.get_dword(ea), b.get_dword(ea + 4)
        if count > 1000 or (count and not ptr):
            raise ValueError(f"handler group {group} at {ea:#x}: implausible {{ptr={ptr:#x}, count={count}}}")
        for i in range(count):
            at = ptr + i * PC_RECORD_STRIDE
            raw = b.get_bytes(at, PC_RECORD_STRIDE)
            if raw is None or len(raw) != PC_RECORD_STRIDE:
                raise ValueError(f"handler record {at:#x} not loaded")
            cid, sub = table_key(raw)
            row = {"kind": "table", "group": group, "id": cid, "sub": sub, "record_va": at,
                   "key": (sub << 16) | cid, "bytes": raw.hex(), "callback": None,
                   "initializer": None, "assignment_va": None, "proved": False}
            for x in m["idautils"].XrefsTo(at):
                owner = db.func_start(x.frm)
                if owner is None or not (PC_INITIALIZER_RANGE[0] <= owner < PC_INITIALIZER_RANGE[1]):
                    continue
                inits.add(owner)
                win = _ida_window_before(db, x.frm, 8)
                res = resolve_callback(win, at)
                if res["proved"]:
                    if row["proved"] and row["callback"] != res["callback"]:
                        row["conflict"] = True
                    row.update({"callback": res["callback"], "initializer": owner,
                                "assignment_va": x.frm, "proved": True, "literal": res["literal"]})
            records.append(row)
    return records, inits


def _ida_window_before(db: _Db, ea: int, n: int) -> list[dict]:
    out = []
    cur = ea
    for _ in range(n + 1):
        ins = db.insn(cur)
        if ins is None:
            break
        out.append({"ea": cur, "mnem": db.mnem(ins), "ops": db.ops(ins)})
        prev = db.m["idc"].prev_head(cur, 0)
        if prev == db.m["idc"].BADADDR or db.func_start(prev) != db.func_start(ea):
            break
        cur = prev
    return list(reversed(out))


def _ida_onpacket_functions(db: _Db) -> tuple[set[int], list[dict]]:
    funcs, orphans = set(), []
    for s in db.m["idautils"].Strings():
        text = str(s)
        if "OnPacket_" not in text:
            continue
        for x in db.m["idautils"].XrefsTo(s.ea):
            fs = db.func_start(x.frm)
            if fs is None:
                orphans.append({"string_ea": s.ea, "text": text, "from": x.frm})
            else:
                funcs.add(fs)
    return funcs, orphans


def _ida_callees(db: _Db, va: int) -> list[int]:
    f = db.func(va)
    if f is None or f.start_ea != va:
        return []  # never the enclosing function's callees
    out = set()
    for ea in db.items(f):
        ins = db.insn(ea)
        if ins is None:
            continue
        is_call = db.m["ida_idp"].is_call_insn(ins)
        if not is_call and db.mnem(ins) != "jmp":
            continue
        op = ins.ops[0]
        if op.type not in (db.m["ida_ua"].o_near, db.m["ida_ua"].o_far):
            continue
        t = db.func_start(op.addr)
        if t == op.addr and t != va:
            out.add(t)
    return sorted(out)


def main(out_path: str, side: str, depth: int = DEFAULT_DEPTH, extra_roots=(), patterns=None,
         write_entry: int = PC_WRITE_ENTRY) -> dict:
    if side not in ("pc", "ps4"):
        raise ValueError(f"SIDE must be 'pc' or 'ps4', not {side!r}")
    db = _Db(side)
    params = {"depth": depth, "extra_roots": sorted(extra_roots)}
    table: list[dict] = []
    reason: dict[int, str] = {}
    summary = {"kind": "summary"}
    if side == "pc":
        table, inits = _ida_pc_table(db)
        cbs = {r["callback"] for r in table if r["callback"]}
        for va in cbs:
            reason.setdefault(va, "table")
        onp, orphans = _ida_onpacket_functions(db)
        for va in onp:
            reason.setdefault(va, "onpacket_string")
        senders = {db.func_start(x.frm) for x in db.m["idautils"].XrefsTo(write_entry) if x.iscode}
        senders.discard(None)
        for va in senders:
            reason.setdefault(va, "write_entry_caller")
        params.update({"group_table": PC_GROUP_TABLE, "groups": PC_GROUP_COUNT,
                       "write_entry": write_entry, "initializer_range": list(PC_INITIALIZER_RANGE)})
        counts = {"table_records": len(table), "table_callbacks": len(cbs), "initializers": len(inits)}
        summary.update(counts)
        summary["expected"] = PC_EXPECTED
        summary["table_ok"] = counts == PC_EXPECTED
        summary["unproved_records"] = [r["record_va"] for r in table if not r["proved"]]
        summary["onpacket_functions"] = len(onp)
        summary["onpacket_orphan_refs"] = orphans
        summary["senders"] = len(senders)
    else:
        pats = tuple(patterns or PS4_ROOT_PATTERNS)
        params["root_patterns"] = list(pats)
        names = {va: db.demangled(va) for va in db.m["idautils"].Functions()}
        for va in match_roots(names, pats):
            reason.setdefault(va, "symbol")
    for va in extra_roots:
        reason.setdefault(va, "extra")
    dist, missing = plan_scope(reason, db.func_start, lambda va: _ida_callees(db, va), depth)
    summary["roots"] = len(reason)
    summary["missing_roots"] = len(missing)
    summary["missing_roots_by_kind"] = {k: sum(1 for r in missing if r["missing"] == k)
                                        for k in ("no-function", "inside-function")}
    summary["depth0_expected"] = len(reason) - len(missing)
    if side == "pc":
        summary["onpacket_orphan_ref_count"] = len(summary["onpacket_orphan_refs"])

    def records():
        yield from table
        yield from missing
        n = n0 = 0
        for va in sorted(dist):
            rec = _ida_function(db, va, dist[va], reason)
            if rec is not None:
                n += 1
                n0 += dist[va] == 0
                yield rec
        summary["functions"] = n
        summary["depth0_functions"] = n0
        yield summary

    write_jsonl(out_path, db.header(params), records())
    return summary


SUMMARY_PREFIX = "extract_ida summary: "


def _short(summary: dict) -> dict:
    return {k: v for k, v in summary.items() if k != "onpacket_orphan_refs"}


def batch(argv, run=None, kill=None, qexit=None, wait=None) -> int:
    """Headless read-only entry: ``argv`` = ``[script, OUT, SIDE, ...]`` (a trailing ``--exit`` is
    accepted and ignored: the batch always exits). Waits for auto-analysis, runs :func:`main`, prints
    the summary line to the log, marks the database not to be saved (``DBFL_KILL``: the packed
    ``.i64`` stays as it was) and calls ``qexit`` (0, or 1 after an exception). The hooks default to
    IDA; tests pass fakes. Returns the exit code.
    """
    import traceback

    code = 1
    try:
        args = [a for a in argv[1:] if a != "--exit"]
        if len(args) != 2:
            raise ValueError(f"usage: extract_ida.py <OUT> <pc|ps4>, got {args!r}")
        if wait is not None:
            wait()
        summary = (run or main)(args[0], args[1])
        print(SUMMARY_PREFIX + json.dumps(_short(summary), sort_keys=True), flush=True)
        code = 0
    except BaseException:  # any failure must still end the batch process
        traceback.print_exc()
        print(SUMMARY_PREFIX + json.dumps({"error": True}), flush=True)
    if kill is not None:
        kill()
    if qexit is not None:
        qexit(code)
    return code


def _ida_batch_hooks():
    import ida_auto
    import ida_loader
    import idc

    return {"wait": ida_auto.auto_wait, "qexit": idc.qexit,
            "kill": lambda: ida_loader.set_database_flag(ida_loader.DBFL_KILL)}


if "OUT" in globals() and "SIDE" in globals():
    _SUMMARY = main(OUT, SIDE, globals().get("DEPTH", DEFAULT_DEPTH),  # noqa: F821
                    globals().get("ROOTS", ()), globals().get("ROOT_PATTERNS"),
                    globals().get("PC_WRITE_ENTRY_OVERRIDE", PC_WRITE_ENTRY))
    print(SUMMARY_PREFIX + json.dumps(_short(_SUMMARY), sort_keys=True))
elif __name__ == "__main__":
    try:
        import idc as _idc
    except ImportError:
        _idc = None
    if _idc is not None and len(_idc.ARGV) >= 3:
        batch(list(_idc.ARGV), **_ida_batch_hooks())
