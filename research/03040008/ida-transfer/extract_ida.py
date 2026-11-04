"""Fact extractor for the PC 03040008 and PS4 02020005 IDA databases (spec 007 T004).

Run inside IDA (ida-mcp ``execute_python`` or headless ``idat -S``) with one call::

    exec(open(path).read(), {"OUT": "D:/.../pc.jsonl", "SIDE": "pc"})

Optional globals: ``DEPTH`` (callee depth, default 3), ``CODEC_DEPTH`` (codec path depth, default 8),
``ROOTS`` (extra root VAs),
``ROOT_PATTERNS`` (PS4 root regexes over the demangled qualified name),
``PC_WRITE_ENTRY_OVERRIDE`` (the packet write entry whose callers are PC roots).
Headless batch (read-only): ``idat -A -L<log> -S"extract_ida.py <OUT> <SIDE>" <db>`` (arguments via
``idc.ARGV``); it prints ``extract_ida summary: {...}`` to the log, discards the session
(``DBFL_KILL``, the packed database is not rewritten) and exits with ``idc.qexit``.

The database is only read: no renames, types, comments, decompilation or saves.

Output: one JSONL file. Line 1 is the header (database identity, script version, parameters);
then ``table`` records (PC handler table), ``missing_root`` records (a root VA that is not a function
start: never replaced by the enclosing function), ``function`` records (one per function in scope),
``extern`` records (v3: one per call target the dump does not describe, :func:`extern_reason`) and a
final ``summary`` record with counts. v3 adds per call site ``arg_bytes``, ``const_stack``
``[[slot, value]]`` and ``const_ecx`` (PC, :func:`pc_const_args`) or ``const_regs`` (PS4,
:func:`ps4_const_args`), and per function ``codec`` (:func:`classify_codec`). v4 adds per function
``object_accesses`` (:func:`object_accesses`), ``codec_distance`` (:func:`codec_distance`) and, for
functions added only to complete reader paths, ``scope: "codec_path"`` (:func:`codec_scope`, depth
``CODEC_DEPTH``); the callers of ``reserveNetworkErrorDialog`` are roots (``root: "requester"``, a
call site outside any function is a ``requester_site`` record). v6 adds per call site ``args``
(:func:`extract.callargs.call_argument_values`: the provable value of each argument slot) and skips MSVC
padding nops; the pure helpers live in the package ``extract/`` (``docs/reference/ida-transfer-tools.md``).
The pure helpers below (no IDA import) are unit-tested in ``tests/test_extract_ida.py`` and
``tests/test_extract_ida_v3.py`` / ``tests/test_extract_ida_v4.py``; the IDA-facing code is the
``_ida_*`` functions and ``main``.

The handler-table reading (record layout, initializer literal-store proof) is adapted from
ddon-hook ``scripts/ida_packet_dispatch.py`` (C:/Users/morph/CLionProjects/ddon-hook, read-only).
"""

from __future__ import annotations

import json
import os
import re
import sys

# v6: the pure helpers live in the sibling package ``extract/``. IDA runs this file with ``__file__`` set
# (``idat -S``); the ``exec`` route passes ``SCRIPT_DIR`` (the folder of this file) when cwd is elsewhere.
_HERE = os.path.dirname(os.path.abspath(globals().get("__file__") or os.path.join(
    globals().get("SCRIPT_DIR") or os.getcwd(), "extract_ida.py")))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from extract.callargs import call_argument_values, describe  # noqa: E402,F401
from extract.dataflow import (  # noqa: E402,F401  (re-exported for the tests and older callers)
    _CALL_CLOBBER,
    _ENTRY_ARGS,
    _arg_value,
    _meet,
    _slots,
    _step,
    block_in_states,
    object_accesses,
)
from extract.x86 import (  # noqa: E402,F401
    _CANON,
    _ESP_OPAQUE,
    _REG_ALIASES,
    PS4_INT_ARG_REGS,
    canon_reg,
    is_padding_nop,
    signed,
)

SCRIPT_VERSION = "6"

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
_DEFAULT_NAME = re.compile(r"^sub_[0-9A-Fa-f]+$")


# --- pure helpers -------------------------------------------------------------------------------

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


# --- v3: constant call arguments, codec shapes, extern call targets (T005c) -----------------------

_STRING_OPS = {"movs": ("rsi", "rdi"), "stos": ("rdi",), "lods": ("rsi", "rax"), "scas": ("rdi",),
               "cmps": ("rsi", "rdi"), "ins": ("rdi",), "outs": ("rsi",)}
_IMPLICIT = {
    "loop": ("rcx",), "loope": ("rcx",), "loopne": ("rcx",), "loopw": ("rcx",),
    "mul": ("rax", "rdx"), "div": ("rax", "rdx"), "idiv": ("rax", "rdx"),
    "cdq": ("rdx",), "cqo": ("rdx",), "cwd": ("rdx",), "cwde": ("rax",), "cdqe": ("rax",), "cbw": ("rax",),
    "cpuid": ("rax", "rbx", "rcx", "rdx"), "rdtsc": ("rax", "rdx"), "rdtscp": ("rax", "rcx", "rdx"),
    "syscall": ("rcx", "r11"), "cmpxchg": ("rax",), "lahf": ("rax",), "xlat": ("rax",),
    "enter": ("rsp", "rbp"), "leave": ("rsp", "rbp"),
}
_NON_WRITING = {"cmp", "test", "push", "bt"}


def implicit_writes(mnem: str, n_ops: int = 0, rep: bool = False) -> tuple[str, ...]:
    """Registers an x86 instruction writes without naming them as operands (canonical names).

    IDA's ``CF_CHG`` features cover explicit operands only; string instructions, ``loop``, one-operand
    ``mul``/``imul``/``div``, sign extensions and ``cpuid`` change registers implicitly. ``rep`` adds
    ``rcx`` (the count) to a string instruction.
    """
    mnem = mnem.lower()
    if mnem in _STRING_OPS:
        return _STRING_OPS[mnem] + (("rcx",) if rep else ())
    if mnem == "imul":
        return ("rax", "rdx") if n_ops == 1 else ()
    return _IMPLICIT.get(mnem, ())


def call_arg_bytes(callee_rets, after: dict | None) -> int | None:
    """Stack argument bytes of a PC call, or None when not provable.

    ``callee_rets``: the immediates of the callee's ``ret`` instructions (a plain ``retn`` counts 0),
    or None when the callee is unknown (indirect, not a function). ``after``: the instruction after
    the call. A callee that pops its arguments (``ret N``, one N) gives N; otherwise an ``add esp, N``
    right after the call (caller cleanup) gives N; a known callee with plain ``retn`` and no cleanup
    gives 0. Mixed ``ret`` immediates prove nothing.
    """
    rets = None if callee_rets is None else set(callee_rets)
    if rets is not None and len(rets) > 1:
        return None
    if rets and next(iter(rets)) > 0:
        return next(iter(rets))
    if after is not None and after.get("mnem") == "add":
        ops = after.get("ops", [])
        if len(ops) == 2 and ops[0].get("type") == "reg" and ops[0].get("reg") == "rsp" \
                and ops[1].get("type") == "imm":
            return ops[1]["value"] & 0xFFFFFFFF
    if rets is not None:
        return 0
    return None


def _esp_mem(op: dict) -> bool:
    return op.get("type") in ("phrase", "displ") and op.get("reg") == "rsp"


def pc_const_args(window: list[dict], arg_bytes: int | None) -> dict:
    """Constant arguments of a PC (32-bit) call from the instructions before it.

    ``window``: the instructions after the previous call (or the block start) up to the call, as in
    :func:`pc_call_arguments`, with ``writes_ecx`` covering implicit writes and operand ``size``.
    Stack cells are tracked relative to the window start: ``push`` and ``sub esp`` move the depth,
    ``pop`` and ``add esp`` move it back and drop popped cells, ``mov [esp+N], imm`` sets a cell, any
    other write to an ``[esp+N]`` operand makes it unknown, and an unmodelled ``esp`` change drops the
    whole picture. A cell is an argument only when it lies in the call's first ``arg_bytes`` bytes
    (:func:`call_arg_bytes`); ``arg_bytes`` None records no stack argument.

    ``ecx``: the last write to ecx in the window when it is ``mov ecx, imm`` / ``xor ecx, ecx``
    (``imm``), ``lea ecx, [abs]`` (``addr``) or ``mov ecx, [abs]`` (``load``); any later write to ecx,
    implicit ones included, leaves nothing. Returns ``{"stack": [[slot, value], ...], "ecx": dict|None}``.
    """
    cells: dict[int, int | None] = {}
    depth = 0
    opaque = False
    for ins in window:
        mnem, ops = ins["mnem"], ins.get("ops", [])
        if mnem in _ESP_OPAQUE:
            opaque = True
            break
        if mnem == "push":
            depth += 4
            op = ops[0] if ops else {}
            cells[depth] = op["value"] & 0xFFFFFFFF if op.get("type") == "imm" else None
            continue
        if mnem == "pop":
            depth -= 4
            cells = {k: v for k, v in cells.items() if k <= depth}
            continue
        if len(ops) == 2 and ops[0].get("type") == "reg" and ops[0].get("reg") == "rsp":
            if mnem in ("sub", "add") and ops[1].get("type") == "imm":
                depth += ops[1]["value"] if mnem == "sub" else -ops[1]["value"]
                cells = {k: v for k, v in cells.items() if k <= depth}
                continue
            if mnem not in _NON_WRITING:
                opaque = True
                break
        if ops and _esp_mem(ops[0]) and mnem not in _NON_WRITING:
            key = depth - ops[0].get("addr", 0)
            size = ops[0].get("size") or 4
            const = mnem == "mov" and len(ops) == 2 and ops[1].get("type") == "imm" and size == 4
            for k in range(key - size + 4, key + 1, 4) if size >= 4 else [key]:
                cells[k] = None
            if const and key % 4 == 0:
                cells[key] = ops[1]["value"] & 0xFFFFFFFF
    stack = []
    if not opaque and arg_bytes:
        for key, value in cells.items():
            off = depth - key
            if value is not None and 0 <= off < arg_bytes and off % 4 == 0:
                stack.append([off // 4, value])
    return {"stack": sorted(stack), "ecx": _ecx_const(window)}


def _ecx_const(window: list[dict]) -> dict | None:
    last = None
    for ins in window:
        if ins.get("writes_ecx"):
            last = ins
    if last is None:
        return None
    mnem, ops = last["mnem"], last.get("ops", [])
    if len(ops) != 2 or ops[0].get("type") != "reg" or ops[0].get("reg") != "rcx" or ops[0].get("size", 4) != 4:
        return None
    src = ops[1]
    if mnem == "mov" and src.get("type") == "imm":
        return {"kind": "imm", "value": src["value"] & 0xFFFFFFFF}
    if mnem in ("xor", "sub") and src.get("type") == "reg" and src.get("reg") == "rcx":
        return {"kind": "imm", "value": 0}
    if mnem == "lea" and src.get("type") == "mem":
        return {"kind": "addr", "value": src["addr"]}
    if mnem == "mov" and src.get("type") == "mem":
        return {"kind": "load", "addr": src["addr"]}
    return None




def ps4_const_args(window: list[dict]) -> dict[str, int]:
    """Immediates in the SysV integer argument registers at a PS4 call.

    ``window``: the same-block instructions since the previous call, each with ``writes`` (explicit
    and implicit, any width) and ``ops`` with ``size``. A register counts only when its last write is
    ``mov r32/r64, imm`` (a 32-bit write zero-extends) or ``xor r32/r64, same`` (0); a later write of
    any width, or an 8/16-bit write, leaves nothing.
    """
    last: dict[str, dict] = {}
    for ins in window:
        for reg in ins.get("writes", ()):
            reg = canon_reg(reg)
            if reg in PS4_INT_ARG_REGS:
                last[reg] = ins
    out = {}
    for reg, ins in last.items():
        ops = ins.get("ops", [])
        if len(ops) != 2 or ops[0].get("type") != "reg" or ops[0].get("reg") != reg:
            continue
        size = ops[0].get("size")
        if size not in (4, 8):
            continue
        mask = (1 << (8 * size)) - 1
        if ins["mnem"] == "mov" and ops[1].get("type") == "imm":
            out[reg] = ops[1]["value"] & mask
        elif ins["mnem"] == "xor" and ops[1].get("type") == "reg" and ops[1].get("reg") == reg:
            out[reg] = 0
    return {r: out[r] for r in PS4_INT_ARG_REGS if r in out}


CODEC_WIDTHS = (1, 2, 4, 8)
CODEC_MAX_INSNS = 64
PC_CURSOR_DISP = {"read": 0x0C, "write": 0x10}  # CPacket m_pReader / m_pWriter (T005b § 2.1)
_STACK_REGS = ("rsp", "rbp")


def _mem_nonstack(op: dict) -> bool:
    return op.get("type") in ("phrase", "displ") and op.get("reg") not in _STACK_REGS


def classify_codec(insns: list[dict], cursor_disp: dict | None = None, ret_width: bool = False) -> dict | None:
    """The fixed-width packet codec shape of a function body (T005b § 2.1/2.2), or None.

    ``insns``: the body in address order, ``{"mnem", "ops": [{"type", "reg", "addr", "value", "size"}]}``.
    Width comes from the instructions only: exactly one cursor advance (``add [base+d], N`` or
    ``inc [base+d]`` = 1, N in 1/2/4/8, base not esp/ebp), and a bounds check with the same N, which
    also gives the direction: ``lea r, [x+N]`` (read: cursor + N against the limit) or ``cmp r, N``
    (write: room left against N), never both. ``cursor_disp`` (PC: :data:`PC_CURSOR_DISP`) requires
    the advanced field to be the direction's cursor. With ``ret_width`` (PC) every ``mov eax, imm`` of
    a codec width must equal N. The load width and the byte swap are recorded as evidence.
    """
    if not insns or len(insns) > CODEC_MAX_INSNS:
        return None
    advances, lea_n, cmp_n, rets, loads = [], set(), set(), set(), set()
    swap = None
    calls = 0
    for ins in insns:
        mnem, ops = ins["mnem"], ins.get("ops", [])
        if mnem == "call":
            calls += 1
        if mnem == "add" and len(ops) == 2 and _mem_nonstack(ops[0]) and ops[1].get("type") == "imm":
            advances.append((ops[0].get("addr", 0), ops[1]["value"]))
        elif mnem == "inc" and len(ops) == 1 and _mem_nonstack(ops[0]):
            advances.append((ops[0].get("addr", 0), 1))
        elif mnem == "lea" and len(ops) == 2 and ops[1].get("type") == "displ" \
                and ops[1].get("reg") not in _STACK_REGS and ops[1].get("addr") in CODEC_WIDTHS:
            lea_n.add(ops[1]["addr"])
        elif mnem == "cmp" and len(ops) == 2 and ops[0].get("type") == "reg" and ops[1].get("type") == "imm" \
                and ops[1]["value"] in CODEC_WIDTHS:
            cmp_n.add(ops[1]["value"])
        elif mnem == "mov" and len(ops) == 2 and ops[0].get("type") == "reg" and ops[0].get("reg") == "rax" \
                and ops[1].get("type") == "imm":
            rets.add(ops[1]["value"])
        if mnem in ("movzx", "movsx", "movbe") and len(ops) == 2 and _mem_nonstack(ops[1]):
            loads.add(ops[1].get("size"))
        if mnem == "bswap":
            swap = "bswap"
        elif mnem == "movbe":
            swap = swap or "movbe"
        elif mnem in ("rol", "ror") and len(ops) == 2 and ops[1].get("value") == 8:
            swap = swap or "rotate"
        elif mnem in ("shl", "shr") and len(ops) == 2 and ops[1].get("value") in (8, 0x18):
            swap = swap or "shift"
    if len(advances) != 1:
        return None
    disp, n = advances[0]
    if n not in CODEC_WIDTHS:
        return None
    if n in lea_n and n in cmp_n:
        return None
    if n in lea_n:
        direction = "read"
    elif n in cmp_n:
        direction = "write"
    else:
        return None
    if cursor_disp is not None and cursor_disp.get(direction) != disp:
        return None
    width_rets = rets & set(CODEC_WIDTHS)
    if ret_width and (not width_rets or width_rets != {n}):
        return None
    evidence = {"advance": n, "bounds": n, "cursor_disp": disp, "ret": n if n in rets else None,
                "load": max((s for s in loads if s), default=None), "swap": swap or ("call" if calls else None)}
    return {"dir": direction, "width": n, "evidence": evidence}


def extern_reason(target: int, func_start, dumped, import_name, segment_class: str | None) -> str | None:
    """Why a call target needs an ``extern`` record, or None when the dump already describes it.

    ``func_start``: start of the function containing ``target`` (None outside any); ``dumped``: VAs
    with a function record; ``import_name``: the import/PLT name or None; ``segment_class``: IDA's
    segment class (``XTRN`` for the extern segment).
    """
    if import_name is not None:
        return "import"
    if segment_class == "XTRN":
        return "extern_segment"
    if target in dumped:
        return None
    if func_start is None:
        return "not_function"
    if func_start != target:
        return "inside_function"
    return "out_of_scope"


# --- v4: object-relative accesses, requester roots, codec-path depth (T005f) ----------------------

# sNetworkExt::reserveNetworkErrorDialog (PC 03040008): the function the slot requesters call with the
# slot (T005b § 1.3, § 5). Named so in the work copy; the v3 dump has it at this VA with 581 caller sites
# (the T005b § 5 count) and `ret 4` (thiscall, one stack argument: the slot).
# v6 array elements (T012 § 1.4, inferred from the listing): PC sub_8BC2E0(size, align) allocates through
# the global allocator and returns the element; PS4 calls the allocator object's method on the result of
# MtMemoryAllocator::getAllocator (out of line), or operator new.
PC_ELEMENT_ALLOCATORS = (0x8BC2E0,)
PS4_ALLOCATOR_NAME = re.compile(r"^operator new(?:\[\])?$")
PS4_ALLOCATOR_GETTER_NAME = re.compile(r"^MtMemoryAllocator::getAllocator$")

PC_RESERVE_DIALOG = 0xBB39D0
RESERVE_DIALOG_NAME = "sNetworkExt::reserveNetworkErrorDialog"
PC_CALL_ON_PACKET = 0x878860  # cSeedGameSvConnection::callOnPacketFunc (slot = const_stack slot 0)
# Variable-length PC codecs the v3 shape classifier does not know (T005b § 2.1).
PC_VARIABLE_CODECS = (0x8BC5B0, 0x8BC710, 0x8BC790, 0x8BCA30)
PS4_CODEC_NAME = re.compile(r"^nPacket::(?:Read|Write)_\w+$")
CODEC_DEPTH = 8



# x86 operand encoding (IDA SDK ``intel.hpp``: ``hasSIB`` = ``op_t.specflag1``, ``sib`` = ``specflag2``,
# ``rex`` = ``insn_t.insnpref``; ``auxpref`` bits ``aux_use32`` 0x8, ``aux_use64`` 0x10, ``aux_natad`` 0x1000).
_AUX_USE32, _AUX_USE64, _AUX_NATAD = 0x8, 0x10, 0x1000
_REX_X, _REX_B = 2, 1
_INDEX_NONE = 4  # SIB index field 100b: no index register
_VSIB = re.compile(r"^v?p?(?:gather|scatter)")  # VSIB: the SIB index is a vector register


def decode_mem(optype: str, phrase: int, has_sib: int, sib: int, rex: int, auxpref: int,
               mnem: str = "") -> dict:
    """Base, index and scale register numbers of a memory operand from the decoded ``op_t`` (v5).

    Mirrors ``x86_base_reg`` / ``x86_index_reg`` / ``x86_scale`` of the IDA SDK ``intel.hpp`` (inline C++
    helpers that IDAPython does not export): with a SIB byte the base is ``sib & 7`` (+8 with REX.B in
    64-bit mode; none for ``o_mem``), the index ``(sib >> 3) & 7`` (+8 with REX.X; ``100b`` without REX.X =
    no index), the scale ``1 << (sib >> 6)``; without SIB the base is ``op_t.phrase`` and there is no index.
    Register names (and so IDA's register-variable renames) play no part. 16-bit addressing and VSIB
    (gather/scatter) give no registers (fail closed). Numbers are IDA's x86 register numbers (0 = rax ..
    15 = r15).
    """
    out = {"base": None, "index": None, "scale": None}
    mode = auxpref & (_AUX_USE32 | _AUX_USE64 | _AUX_NATAD)
    if mode in (_AUX_NATAD, _AUX_USE32) or _VSIB.match(mnem or ""):
        return out
    m64 = bool(auxpref & _AUX_USE64)
    if has_sib:
        sib &= 0xFF
        if optype != "mem":
            out["base"] = (sib & 7) | (8 if m64 and rex & _REX_B else 0)
        idx = ((sib >> 3) & 7) | (8 if m64 and rex & _REX_X else 0)
        if idx != _INDEX_NONE:
            out["index"], out["scale"] = idx, 1 << ((sib >> 6) & 3)
    elif optype != "mem":
        out["base"] = phrase
    return out


def requester_roots(sites, func_start, target: int) -> tuple[dict[int, str], list[dict]]:
    """Roots for the callers of ``reserveNetworkErrorDialog``: each call site's function (``requester``);
    a site outside any function gives a ``requester_site`` record (never its neighbour function)."""
    roots: dict[int, str] = {}
    orphans: list[dict] = []
    for s in sorted(set(sites)):
        fs = func_start(s)
        if fs is None:
            orphans.append({"kind": "requester_site", "va": s, "target": target, "missing": "no-function"})
        elif fs != target:
            roots.setdefault(fs, "requester")
    return roots, orphans


def codec_distance(callees_of, is_codec, max_depth: int = CODEC_DEPTH):
    """``dist(va, budget)``: least call distance from ``va`` to a codec (0 = ``va`` is one), or None
    when none lies within ``budget`` levels. Memoised; cycles end at the budget."""
    memo: dict[tuple[int, int], int | None] = {}

    def dist(va: int, budget: int) -> int | None:
        key = (va, budget)
        if key in memo:
            return memo[key]
        if is_codec(va):
            memo[key] = 0
            return 0
        best = None
        if budget > 0:
            for c in callees_of(va):
                d = dist(c, budget - 1)
                if d is not None and (best is None or d + 1 < best):
                    best = d + 1
        memo[key] = best
        return best

    return dist


def check_reserve(side: str, va: int | None, start: int | None, name: str) -> None:
    """Fail closed unless ``va`` is the start of the reserveNetworkErrorDialog function: PC by its VA
    (named so, or still default-named), PS4 by its one symbol."""
    if va is None:
        raise ValueError(f"{side}: no unique {RESERVE_DIALOG_NAME} function")
    if start != va:
        raise ValueError(f"{side}: {RESERVE_DIALOG_NAME} {va:#x} is not a function start ({start})")
    if name != RESERVE_DIALOG_NAME and not (side == "pc" and is_default_name(name)):
        raise ValueError(f"{side}: {va:#x} is named {name!r}, not {RESERVE_DIALOG_NAME}")


def codec_scope(scope: dict[int, int], callees_of, is_codec, max_depth: int = CODEC_DEPTH,
                dist=None) -> dict[int, int]:
    """Functions to add beyond ``scope`` (VA -> distance from a root) so that every call path of at most
    ``max_depth`` levels from a scope function to a codec is in the dump, plus the direct callees of each
    function on such a path (so a reader's non-codec callees are described, not gaps). Expansion stops
    where no codec is reachable within the remaining depth. ``dist``: a shared :func:`codec_distance`."""
    dist = dist or codec_distance(callees_of, is_codec, max_depth)
    added: dict[int, int] = {}
    frontier = sorted((va for va, d in scope.items() if d < max_depth and dist(va, max_depth - d) not in (None, 0)),
                      key=lambda va: (scope[va], va))
    level_of = dict(scope)
    while frontier:
        nxt = []
        for va in frontier:
            d = level_of[va]
            for c in callees_of(va):
                if c in level_of:
                    continue
                level_of[c] = added[c] = d + 1
                left = max_depth - d - 1
                if left > 0 and dist(c, left) not in (None, 0):
                    nxt.append(c)
        frontier = sorted(set(nxt), key=lambda va: (level_of[va], va))
    return added


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
        self._rets: dict[int, list[int] | None] = {}
        self._imports: dict[int, dict] | None = None

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
            d = {"type": kind, "size": self.m["ida_ua"].get_dtype_size(op.dtype)}
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

    def all_writes(self, ins, ops) -> list[str]:
        """:meth:`writes` plus the implicit writes of :func:`implicit_writes` (canonical names)."""
        mnem = self.mnem(ins)
        rep = mnem in _STRING_OPS and "rep" in (self.m["idc"].GetDisasm(ins.ea) or "").lower()
        return self.writes(ins, ops) + list(implicit_writes(mnem, len(ops), rep))

    def ret_values(self, va) -> list[int] | None:
        """Immediates of the ``ret`` instructions of the function starting at ``va`` (plain = 0)."""
        if va in self._rets:
            return self._rets[va]
        f = self.func(va)
        out = None
        if f is not None and f.start_ea == va:
            out = []
            for ea in self.items(f):
                ins = self.insn(ea)
                if ins is not None and self.mnem(ins) in ("retn", "ret"):
                    ops = self.ops(ins)
                    out.append(ops[0]["value"] if ops and ops[0]["type"] == "imm" else 0)
        self._rets[va] = out
        return out

    def imports(self) -> dict[int, dict]:
        """Import address (IAT slot / extern entry) -> ``{"module", "name"}`` (``ida_nalt``)."""
        if self._imports is None:
            nalt = self.m["ida_nalt"]
            out: dict[int, dict] = {}
            for i in range(nalt.get_import_module_qty()):
                module = nalt.get_import_module_name(i)

                def cb(ea, name, ordinal, module=module):
                    out[ea] = {"module": module, "name": name or (f"#{ordinal}" if ordinal else None)}
                    return True

                nalt.enum_import_names(i, cb)
            self._imports = out
        return self._imports

    def import_of(self, ea) -> dict | None:
        """The import a call target resolves to: the address itself, or a PLT stub ``jmp [slot]``."""
        imp = self.imports()
        if ea in imp:
            return imp[ea]
        ins = self.insn(ea)
        if ins is not None and self.mnem(ins) == "jmp":
            ops = self.ops(ins)
            if ops and ops[0]["type"] == "mem" and ops[0]["addr"] in imp:
                return imp[ops[0]["addr"]]
        return None

    def segment(self, ea) -> tuple[str | None, str | None]:
        seg = self.m["ida_segment"].getseg(ea)
        if seg is None:
            return None, None
        return self.m["ida_segment"].get_segm_name(seg), self.m["ida_segment"].get_segm_class(seg)

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
            if op["type"] in ("phrase", "displ") and reg in self._mem_regs(ins, i):
                return True
        if mnem.startswith("rep") or mnem in ("loop", "loope", "loopne", "jecxz", "jrcxz"):
            return reg == "rcx"
        if reg == "rcx" and mnem in ("movs", "stos", "cmps", "scas", "lods", "ins", "outs") \
                and "rep" in (self.m["idc"].GetDisasm(ins.ea) or "").lower():
            return True  # rep/repne prefix reads the count
        return False

    def mem_regs(self, ins, n: int, optype: str) -> dict:
        """Canonical base/index register names and the scale of memory operand ``n`` (:func:`decode_mem`)."""
        op = ins.ops[n]
        d = decode_mem(optype, op.phrase, op.specflag1, op.specflag2, ins.insnpref, ins.auxpref, self.mnem(ins))
        dt = self.m["ida_ua"].dt_qword if self.bits == 64 else self.m["ida_ua"].dt_dword
        return {"base": None if d["base"] is None else self.reg_name(d["base"], dt),
                "index": None if d["index"] is None else self.reg_name(d["index"], dt), "scale": d["scale"]}

    def _mem_regs(self, ins, n) -> set[str]:
        d = self.mem_regs(ins, n, self.optype.get(ins.ops[n].type, ""))
        return {r for r in (d["base"], d["index"]) if r is not None}

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

    # v4
    def v4_insn(self, ins) -> dict:
        """Instruction dict for :func:`object_accesses` (memory operands with base/index/scale, signed
        displacement and CF_CHGn/CF_USEn; ``pops`` for PC calls)."""
        idp = self.m["ida_idp"]
        feat = ins.get_canon_feature()
        chg = [getattr(idp, f"CF_CHG{i}", 0) for i in range(1, 7)]
        use = [getattr(idp, f"CF_USE{i}", 0) for i in range(1, 7)]
        ops = []
        for i, op in enumerate(self.ops(ins)):
            op = dict(op)
            if op["type"] in ("phrase", "displ", "mem"):
                op.update(self.mem_regs(ins, i, op["type"]))
                op["addr"] = signed(op.get("addr", 0), self.bits) if op["type"] == "displ" else \
                    (0 if op["type"] == "phrase" else op.get("addr"))
                op["chg"] = bool(i < 6 and feat & chg[i])
                op["use"] = bool(i < 6 and feat & use[i])
            ops.append(op)
        is_call = bool(idp.is_call_insn(ins))
        out = {"ea": ins.ea, "mnem": self.mnem(ins), "ops": ops, "writes": self.all_writes(ins, ops),
               "call": is_call, "pops": None}
        if is_call and self.side == "pc" and ops and ops[0]["type"] in ("near", "far"):
            rets = self.ret_values(ops[0]["addr"])
            if rets is not None and len(set(rets)) <= 1:
                out["pops"] = rets[0] if rets else None
        return out

    def callees(self, va: int) -> list[int]:
        if not hasattr(self, "_callees"):
            self._callees: dict[int, list[int]] = {}
        if va not in self._callees:
            self._callees[va] = _ida_callees(self, va)
        return self._callees[va]

    def is_codec(self, va: int) -> bool:
        """A packet codec: the v3 shape classifier, the PC variable-length codecs, PS4 ``nPacket::Read_*``
        / ``Write_*`` by symbol."""
        if not hasattr(self, "_codec"):
            self._codec: dict[int, bool] = {}
        if va in self._codec:
            return self._codec[va]
        res = False
        if self.side == "pc" and va in PC_VARIABLE_CODECS:
            res = True
        elif self.side == "ps4" and PS4_CODEC_NAME.match(self.demangled(va) or ""):
            res = True
        else:
            f = self.func(va)
            if f is not None and f.start_ea == va:
                items = self.items(f)
                if len(items) <= CODEC_MAX_INSNS:
                    body = []
                    for ea in items:
                        ins = self.insn(ea)
                        if ins is not None:
                            body.append({"mnem": "call" if self.m["ida_idp"].is_call_insn(ins) else self.mnem(ins),
                                         "ops": self.ops(ins)})
                    res = classify_codec(body, PC_CURSOR_DISP if self.side == "pc" else None,
                                         self.side == "pc") is not None
        self._codec[va] = res
        return res


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
    body: list[dict] = []
    seen_data = set()
    for ea in items:
        ins = db.insn(ea)
        if ins is None:
            continue
        if ea in starts:
            window = []
        mnem = db.mnem(ins)
        ops = db.ops(ins)
        body.append({"mnem": "call" if db.m["ida_idp"].is_call_insn(ins) else mnem, "ops": ops})
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
                win = window[-ARG_WINDOW:]
                if db.side == "pc":
                    site.update(pc_call_arguments(win))
                    if not is_tail:
                        _pc_site_constants(db, site, win, ea + ins.size, target)
                else:
                    site["arg_regs"] = ps4_call_arguments(win)
                    if not is_tail:
                        consts_regs = ps4_const_args(win)
                        if consts_regs:
                            site["const_regs"] = consts_regs
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
            entry["writes_ecx"] = "rcx" in db.all_writes(ins, ops)
        else:
            entry["writes"] = db.all_writes(ins, ops)
        window.append(entry)
    rec.update({"calls": calls, "strings": strings, "data_refs": sorted(data),
                "constants": sorted(set(consts)), "ret_imm": sorted(set(rets))})
    rec["codec"] = classify_codec(body, PC_CURSOR_DISP if db.side == "pc" else None, db.side == "pc")
    callers = sorted({x.frm for x in m["idautils"].XrefsTo(va) if x.iscode})
    caller_funcs = sorted({s for s in (db.func_start(c) for c in callers) if s is not None})
    rec["caller_sites"] = len(callers)
    rec["callers_count"] = len(caller_funcs)
    rec["callers"] = caller_funcs[:MAX_CALLERS]
    blocks, preds = _ida_blocks(db, f)
    rec["object_accesses"] = object_accesses(blocks, preds, f.start_ea, db.side)
    _ida_call_args(db, f, blocks, preds, calls)
    if db.side == "pc":
        rec["ecx_read_before_write"] = _ida_ecx_rbw(db, f)
        rec["annotations"] = _ida_annotations(db, f, items)
    return rec


def _pc_site_constants(db: _Db, site: dict, window: list[dict], after_ea: int, target) -> None:
    """``arg_bytes``, ``const_stack`` and ``const_ecx`` of one PC call site (:func:`pc_const_args`)."""
    after = None
    nxt = db.insn(after_ea) if db.func_start(after_ea) == db.func_start(site["site"]) else None
    if nxt is not None:
        after = {"mnem": db.mnem(nxt), "ops": db.ops(nxt)}
    rets = db.ret_values(target) if target is not None else None
    arg_bytes = call_arg_bytes(rets, after)
    site["arg_bytes"] = arg_bytes
    consts = pc_const_args(window, arg_bytes)
    if consts["stack"]:
        site["const_stack"] = consts["stack"]
    if consts["ecx"] is not None:
        site["const_ecx"] = consts["ecx"]


def _ida_externs(db: _Db, targets: dict[int, int], via_mem: dict[int, int], dumped: set[int]) -> list[dict]:
    """One ``extern`` record per call target the dump does not describe (:func:`extern_reason`).

    ``targets``: direct call target -> call sites; ``via_mem``: ``call [slot]`` slot -> call sites
    (only import slots are recorded).
    """
    out = []
    for va in sorted(targets):
        imp = db.import_of(va)
        seg, cls = db.segment(va)
        reason = extern_reason(va, db.func_start(va), dumped, imp, cls)
        if reason is None:
            continue
        out.append({"kind": "extern", "va": va, "via": "call", "reason": reason, "name": db.name(va) or None,
                    "import": imp, "segment": seg, "segment_class": cls, "function_start": db.func_start(va),
                    "sites": targets[va]})
    for va in sorted(via_mem):
        imp = db.imports().get(va)
        if imp is None:
            continue
        seg, cls = db.segment(va)
        out.append({"kind": "extern", "va": va, "via": "mem", "reason": "import", "name": db.name(va) or None,
                    "import": imp, "segment": seg, "segment_class": cls, "function_start": None,
                    "sites": via_mem[va]})
    return out


def _ida_blocks(db: _Db, f) -> tuple[list[tuple[int, list[dict]]], dict[int, list[int]]]:
    """The function's blocks as :meth:`_Db.v4_insn` dicts and their predecessors (no external blocks)."""
    gdl = db.m["ida_gdl"]
    fc = gdl.FlowChart(f, flags=getattr(gdl, "FC_NOEXT", 0) | getattr(gdl, "FC_PREDS", 0))
    blocks, preds = [], {}
    for b in sorted(fc, key=lambda b: b.start_ea):
        insns = []
        ea = b.start_ea
        while ea < b.end_ea:
            ins = db.insn(ea)
            if ins is None:
                break
            insns.append(db.v4_insn(ins))
            ea += ins.size
        blocks.append((b.start_ea, insns))
        preds[b.start_ea] = [p.start_ea for p in b.preds()]
    return blocks, preds


def _ida_object_accesses(db: _Db, f) -> list[dict]:
    blocks, preds = _ida_blocks(db, f)
    return object_accesses(blocks, preds, f.start_ea, db.side)


def _ida_call_args(db: _Db, f, blocks, preds, calls: list[dict]) -> None:
    """v6: ``args`` per call site (:func:`extract.callargs.call_argument_values`)."""
    targets = {c["target"] for c in calls if isinstance(c["target"], int)}
    if db.side == "pc":
        allocators, getters = set(PC_ELEMENT_ALLOCATORS), set()
    else:
        names = {t: db.demangled(t) or "" for t in targets}
        allocators = {t for t, n in names.items() if PS4_ALLOCATOR_NAME.match(n)}
        getters = {t for t, n in names.items() if PS4_ALLOCATOR_GETTER_NAME.match(n)}
    arg_bytes = {c["site"]: c.get("arg_bytes") for c in calls}
    values = call_argument_values(blocks, preds, f.start_ea, db.side, arg_bytes, allocators, getters)
    for c in calls:
        if c["site"] in values:
            c["args"] = values[c["site"]]


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


def pc_roots(db: _Db, write_entry: int = PC_WRITE_ENTRY):
    """PC roots: table callbacks, ``OnPacket_`` string users, callers of the packet write entry.

    Returns ``(table, initializers, reason, onpacket_functions, orphan_refs, senders)``; ``reason``
    maps each root VA to the first reason found. ``repair_functions.py`` uses the same roots.
    """
    reason: dict[int, str] = {}
    table, inits = _ida_pc_table(db)
    for va in sorted({r["callback"] for r in table if r["callback"]}):
        reason.setdefault(va, "table")
    onp, orphans = _ida_onpacket_functions(db)
    for va in sorted(onp):
        reason.setdefault(va, "onpacket_string")
    senders = {db.func_start(x.frm) for x in db.m["idautils"].XrefsTo(write_entry) if x.iscode}
    senders.discard(None)
    for va in sorted(senders):
        reason.setdefault(va, "write_entry_caller")
    return table, inits, reason, onp, orphans, senders


def main(out_path: str, side: str, depth: int = DEFAULT_DEPTH, extra_roots=(), patterns=None,
         write_entry: int = PC_WRITE_ENTRY, codec_depth: int = CODEC_DEPTH) -> dict:
    if side not in ("pc", "ps4"):
        raise ValueError(f"SIDE must be 'pc' or 'ps4', not {side!r}")
    db = _Db(side)
    params = {"depth": depth, "extra_roots": sorted(extra_roots)}
    table: list[dict] = []
    reason: dict[int, str] = {}
    summary = {"kind": "summary"}
    if side == "pc":
        table, inits, reason, onp, orphans, senders = pc_roots(db, write_entry)
        cbs = {r["callback"] for r in table if r["callback"]}
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
    # v4: requester roots (callers of reserveNetworkErrorDialog)
    if side == "pc":
        reserve = PC_RESERVE_DIALOG
        reserve_name = db.name(reserve)
    else:
        found = [va for va, n in names.items() if n == RESERVE_DIALOG_NAME]
        reserve = found[0] if len(found) == 1 else None
        reserve_name = RESERVE_DIALOG_NAME
    check_reserve(side, reserve, db.func_start(reserve) if reserve is not None else None, reserve_name)
    sites = [x.frm for x in db.m["idautils"].XrefsTo(reserve) if x.iscode]
    req_roots, req_orphans = requester_roots(sites, db.func_start, reserve)
    for va, why in req_roots.items():
        reason.setdefault(va, why)
    params.update({"reserve_dialog": reserve, "codec_depth": codec_depth})
    summary.update({"reserve_dialog": reserve, "reserve_dialog_name": reserve_name,
                    "requester_sites": len(sites), "requesters": len(req_roots),
                    "requester_sites_outside_functions": len(req_orphans)})
    for va in extra_roots:
        reason.setdefault(va, "extra")
    dist, missing = plan_scope(reason, db.func_start, db.callees, depth)
    cdist = codec_distance(db.callees, db.is_codec, codec_depth)
    added = codec_scope(dist, db.callees, db.is_codec, codec_depth, cdist) if codec_depth > depth else {}
    dist.update(added)
    summary["codec_path_functions"] = len(added)
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
        yield from req_orphans
        n = n0 = ncodec = nacc = 0
        nargs: dict[str, int] = {}
        targets: dict[int, int] = {}
        via_mem: dict[int, int] = {}
        dumped: set[int] = set()
        for va in sorted(dist):
            rec = _ida_function(db, va, dist[va], reason)
            if rec is not None:
                n += 1
                n0 += dist[va] == 0
                dumped.add(va)
                ncodec += rec["codec"] is not None
                nacc += len(rec["object_accesses"])
                rec["codec_distance"] = cdist(va, codec_depth)
                if va in added:
                    rec["scope"] = "codec_path"
                for c in rec["calls"]:
                    for a in c.get("args", ()):
                        nargs[a["kind"]] = nargs.get(a["kind"], 0) + 1
                    if isinstance(c["target"], int):
                        targets[c["target"]] = targets.get(c["target"], 0) + 1
                    elif "via_mem" in c:
                        via_mem[c["via_mem"]] = via_mem.get(c["via_mem"], 0) + 1
                yield rec
        externs = _ida_externs(db, targets, via_mem, dumped)
        yield from externs
        summary["functions"] = n
        summary["depth0_functions"] = n0
        summary["externs"] = len(externs)
        summary["externs_by_reason"] = {r: sum(1 for e in externs if e["reason"] == r)
                                        for r in sorted({e["reason"] for e in externs})}
        summary["codec_functions"] = ncodec
        summary["object_accesses"] = nacc
        summary["call_args_by_kind"] = dict(sorted(nargs.items()))
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
                    globals().get("PC_WRITE_ENTRY_OVERRIDE", PC_WRITE_ENTRY),
                    globals().get("CODEC_DEPTH", CODEC_DEPTH))
    print(SUMMARY_PREFIX + json.dumps(_short(_SUMMARY), sort_keys=True))
elif __name__ == "__main__":
    try:
        import idc as _idc
    except ImportError:
        _idc = None
    if _idc is not None and len(_idc.ARGV) >= 3:
        batch(list(_idc.ARGV), **_ida_batch_hooks())
