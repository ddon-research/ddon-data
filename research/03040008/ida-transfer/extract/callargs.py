"""v6: the value each argument slot provably holds at a call site (T013a; T012 § 2 items 1-4).

Pure (no IDA import). Input: the blocks of :func:`extract.dataflow.object_accesses` (instruction dicts with
``ea``, ``mnem``, ``ops`` (memory operands with ``base``/``index``/``scale``/``addr``), ``writes``,
``call``, ``pops``; call operands ``{"type": "near", "addr": target}``).

Values that cross blocks come from the must-analysis of :func:`extract.dataflow.block_in_states`: the
function arguments (PC ``ecx`` and stack arguments, PS4 ``rdi``..``r9``) and their copies, the stack
pointer as a frame offset. Everything derived from them is proved **within the block** only (the brief's
rule): ``lea r, [base+X]``, ``mov r, base`` + ``add``/``sub r, imm``, constants, the pushes of the call's
window, the return value of an allocator call. MSVC padding nops (``lea r, [r+0]``) are skipped.

Kinds (one record per argument slot with a provable value; anything else records nothing):

- ``const``: ``{"value"}`` (``mov r, imm``, ``xor r, r``, ``push imm``);
- ``obj``: ``{"arg", "arg_loc", "disp", "def"}`` = function argument ``arg`` (``arg_loc`` ``ecx``,
  ``stack`` or the PS4 register) plus ``disp``; ``def`` the ``lea``/``add``/``sub`` that formed it (None
  for the argument itself or a plain copy);
- ``stack``: ``{"frame", "def"}`` = the address of a stack slot, ``frame`` relative to the stack pointer at
  function entry (the return address is at ``frame`` 0; PC stack argument k at ``4 + 4k``);
- ``element``: ``{"from", ..., "disp", "def"}`` = an array element plus ``disp``. ``from: "result"``: the
  return of a call to an allocator (``site``, ``callee``; ``getter`` when the call is an indirect call on
  the result of an allocator getter); ``from: "index"``: ``lea r, [data + i*scale]`` / ``add data, i``
  where ``data`` = ``[arg+via]`` (``arg``, ``arg_loc``, ``via``, ``index``, ``scale``).

Slots: PC ``"ecx"`` and the stack slots ``0 .. arg_bytes/4 - 1`` (the pushes and ``mov [esp+N]`` since the
previous call in the block; :func:`extract_ida.call_arg_bytes`, None = no stack slot); PS4 the integer
argument registers.
"""

from __future__ import annotations

from .dataflow import _step, block_in_states
from .x86 import _ESP_OPAQUE, PS4_INT_ARG_REGS, canon_reg, is_padding_nop, signed

_BASE_KINDS = ("arg", "frame", "addr", "saddr", "elem")


def _noemit(*_):
    return None


def _reg_op(op: dict, ptr: int) -> str | None:
    if op.get("type") == "reg" and op.get("size") == ptr:
        return op.get("reg")
    return None


def _offset(value, disp: int, ea: int):
    """``value`` + ``disp`` for a base kind, or None."""
    kind = value[0]
    if kind == "arg":
        return ("addr", value, disp, ea)
    if kind == "frame":
        return ("saddr", value[1] + disp, ea)
    if kind == "addr":
        return ("addr", value[1], value[2] + disp, ea)
    if kind == "saddr":
        return ("saddr", value[1] + disp, ea)
    if kind == "elem":
        return ("addr", value, disp, ea)
    return None


def _derive(st: dict, ins: dict, ptr: int):
    """``(register, value)`` an instruction defines from the pre-state, or None."""
    mnem, ops = ins["mnem"], ins.get("ops", [])
    if len(ops) != 2:
        return None
    dst = _reg_op(ops[0], ptr)
    src = ops[1]
    if mnem in ("mov", "xor") and ops[0].get("type") == "reg" and ops[0].get("size") in (4, ptr) \
            and ops[0].get("reg") != "rsp":
        reg, size = ops[0]["reg"], ops[0]["size"]
        if mnem == "mov" and src.get("type") == "imm":
            return reg, ("const", src["value"] & ((1 << (8 * size)) - 1))  # a 32-bit write zero-extends
        if mnem == "xor" and src.get("type") == "reg" and src.get("reg") == reg:
            return reg, ("const", 0)
        return None
    if dst is None or dst == "rsp":
        return None
    if mnem == "lea" and src.get("type") in ("phrase", "displ"):
        base = st.get(src.get("base"))
        if base is None:
            return None
        disp = src.get("addr", 0) or 0
        if src.get("index") is None:
            return dst, _offset(base, disp, ins["ea"])
        if base[0] == "field" and src.get("index") != src.get("base"):
            elem = ("elem", ("index", base[1], base[2], base[3], src["index"], src.get("scale") or 1, ins["ea"]))
            return dst, (elem if disp == 0 else _offset(elem, disp, ins["ea"]))
        return None
    if mnem in ("add", "sub") and src.get("type") == "imm":
        cur = st.get(dst)
        if cur is None:
            return None
        d = signed(src["value"], 8 * ptr)
        return dst, _offset(cur, d if mnem == "add" else -d, ins["ea"])
    if mnem == "add" and src.get("type") == "reg" and src.get("size") == ptr and src.get("reg") not in (dst, "rsp"):
        cur = st.get(dst)
        if cur is not None and cur[0] == "field":
            return dst, ("elem", ("index", cur[1], cur[2], cur[3], src["reg"], 1, ins["ea"]))
    return None


def describe(value) -> dict | None:
    """The output record of a tracked value (module docstring), or None when it is no argument kind."""
    if value is None:
        return None
    kind = value[0]
    if kind == "const":
        return {"kind": "const", "value": value[1]}
    if kind == "arg":
        return {"kind": "obj", "arg": value[2], "arg_loc": value[1], "disp": 0, "def": None}
    if kind == "frame":
        return {"kind": "stack", "frame": value[1], "def": None}
    if kind == "saddr":
        return {"kind": "stack", "frame": value[1], "def": value[2]}
    if kind == "elem":
        return dict(_elem(value[1]), disp=0, def_=None)
    if kind == "addr":
        base, disp, ea = value[1], value[2], value[3]
        if base[0] == "arg":
            return {"kind": "obj", "arg": base[2], "arg_loc": base[1], "disp": disp, "def": ea}
        if base[0] == "elem":
            return dict(_elem(base[1]), disp=disp, def_=ea)
    return None


def _elem(info) -> dict:
    if info[0] == "result":
        out = {"kind": "element", "from": "result", "site": info[1], "callee": info[2]}
        if info[3] is not None:
            out["getter"] = info[3]
        return out
    return {"kind": "element", "from": "index", "arg": info[2], "arg_loc": info[1], "via": info[3],
            "index": info[4], "scale": info[5], "index_def": info[6]}


def _record(slot, value) -> dict | None:
    rec = describe(value)
    if rec is None:
        return None
    if "def_" in rec:
        rec["def"] = rec.pop("def_")
    return {"slot": slot, **rec}


class _Cells:
    """The PC outgoing argument area of one call window (as :func:`extract_ida.pc_const_args`)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.cells: dict[int, object] = {}
        self.depth = 0
        self.opaque = False

    def step(self, st: dict, ins: dict, side: str) -> None:
        if side != "pc" or self.opaque:
            return
        mnem, ops = ins["mnem"], ins.get("ops", [])
        if mnem in _ESP_OPAQUE:
            self.opaque = True
            return
        if mnem == "push":
            self.depth += 4
            op = ops[0] if ops else {}
            if op.get("type") == "imm":
                self.cells[self.depth] = ("const", op["value"] & 0xFFFFFFFF)
            elif op.get("type") == "reg" and op.get("size") == 4:
                self.cells[self.depth] = st.get(op.get("reg"))
            else:
                self.cells[self.depth] = None
            return
        if mnem == "pop":
            self.depth -= 4
            self.cells = {k: v for k, v in self.cells.items() if k <= self.depth}
            return
        if len(ops) == 2 and ops[0].get("type") == "reg" and ops[0].get("reg") == "rsp":
            if mnem in ("sub", "add") and ops[1].get("type") == "imm":
                d = signed(ops[1]["value"], 32)
                self.depth += d if mnem == "sub" else -d
                self.cells = {k: v for k, v in self.cells.items() if k <= self.depth}
                return
            if mnem not in ("cmp", "test"):
                self.opaque = True
                return
        if "rsp" in {canon_reg(r) for r in ins.get("writes", ())}:
            self.opaque = True
            return
        for i, op in enumerate(ops):
            if op.get("type") not in ("phrase", "displ") or not op.get("chg"):
                continue
            if op.get("base") == "rsp" and op.get("index") is None:
                key = self.depth - (op.get("addr", 0) or 0)
                size = op.get("size") or 4
                for k in range(key - size + 4, key + 1, 4) if size >= 4 else [key]:
                    self.cells[k] = None
                if i == 0 and mnem == "mov" and size == 4 and key % 4 == 0 and len(ops) == 2:
                    src = ops[1]
                    if src.get("type") == "imm":
                        self.cells[key] = ("const", src["value"] & 0xFFFFFFFF)
                    elif src.get("type") == "reg" and src.get("size") == 4:
                        self.cells[key] = st.get(src.get("reg"))
            else:
                base = st.get(op.get("base"))
                if base is not None and base[0] in ("frame", "saddr"):
                    self.opaque = True  # a store through another stack pointer may alias the area

    def slots(self, arg_bytes: int | None) -> list[tuple[int, object]]:
        if self.opaque or not arg_bytes:
            return []
        out = []
        for key, value in self.cells.items():
            off = self.depth - key
            if value is not None and 0 <= off < arg_bytes and off % 4 == 0:
                out.append((off // 4, value))
        return sorted(out, key=lambda kv: kv[0])


def call_argument_values(blocks: list[tuple[int, list[dict]]], preds: dict[int, list[int]], entry: int,
                         side: str, arg_bytes: dict[int, int | None] | None = None, allocators=(),
                         allocator_getters=()) -> dict[int, list[dict]]:
    """Call site ea -> argument value records (module docstring), for the sites with at least one.

    ``arg_bytes``: PC call site -> stack argument bytes (missing = None). ``allocators``: call targets whose
    return value is a new array element; ``allocator_getters``: targets returning an allocator, whose
    indirect method call (``this`` = PC ``ecx`` / PS4 ``rdi`` holding that return) returns a new element.
    """
    ptr = 4 if side == "pc" else 8
    this_reg = "rcx" if side == "pc" else "rdi"
    allocators, allocator_getters = set(allocators), set(allocator_getters)
    arg_bytes = arg_bytes or {}
    starts = block_in_states(blocks, preds, entry, side, frame=True)
    out: dict[int, list[dict]] = {}
    for b, body in blocks:
        st = starts.get(b)
        if st is None:
            continue
        cells = _Cells()
        for ins in body:
            if is_padding_nop(ins, ptr):
                continue
            if ins.get("call"):
                recs = []
                if side == "pc":
                    recs.append(_record("ecx", st.get("rcx")))
                    recs += [_record(k, v) for k, v in cells.slots(arg_bytes.get(ins["ea"]))]
                else:
                    recs += [_record(r, st.get(r)) for r in PS4_INT_ARG_REGS]
                recs = [r for r in recs if r is not None]
                if recs:
                    out[ins["ea"]] = recs
                ops = ins.get("ops", [])
                target = ops[0].get("addr") if ops and ops[0].get("type") in ("near", "far") else None
                this = st.get(this_reg)
                st = _step(st, ins, side, ptr, _noemit)
                if target is not None and target in allocators:
                    st["rax"] = ("elem", ("result", ins["ea"], target, None))
                elif target is None and this is not None and this[0] == "ret" and this[2] in allocator_getters:
                    st["rax"] = ("elem", ("result", ins["ea"], "indirect", this[2]))
                elif target is not None:
                    st["rax"] = ("ret", ins["ea"], target)
                cells.reset()
                continue
            cells.step(st, ins, side)
            derived = _derive(st, ins, ptr)
            st = _step(st, ins, side, ptr, _noemit)
            if derived is not None and derived[1] is not None:
                st[derived[0]] = derived[1]
        # values derived in this block are not carried to the next (the in-states have none)
    return out
