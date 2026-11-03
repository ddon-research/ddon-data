"""v4 object-access dataflow (moved from ``extract_ida.py`` in v6; pure, no IDA import)."""

from __future__ import annotations

from .x86 import _ESP_OPAQUE, PS4_INT_ARG_REGS, canon_reg, is_padding_nop, signed

# Registers a call may change (MSVC x86 / SysV x86-64): everything else survives it by the ABI.
_CALL_CLOBBER = {"pc": ("rax", "rcx", "rdx"),
                 "ps4": ("rax", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11")}
_ENTRY_ARGS = {"pc": ("rcx",), "ps4": PS4_INT_ARG_REGS}


def _arg_value(side: str, reg: str):
    if side == "pc":
        return ("arg", "ecx", 0)
    return ("arg", reg, PS4_INT_ARG_REGS.index(reg))


def _meet(states: list[dict]) -> dict:
    """Registers on which every incoming state agrees; dirty stack slots are the union."""
    first, rest = states[0], states[1:]
    out = {k: v for k, v in first.items() if k != "_dirty" and all(s.get(k) == v for s in rest)}
    dirty = frozenset().union(*(s.get("_dirty", frozenset()) for s in states))
    if dirty:
        out["_dirty"] = dirty
    return out


def _slots(loc: int, size: int) -> set:
    first = (loc - 4) // 4
    last = (loc + max(size, 1) - 1 - 4) // 4
    return {k for k in range(first, last + 1) if k >= 0}


def _step(state: dict, ins: dict, side: str, ptr: int, emit) -> dict:
    """Transfer one instruction (:func:`object_accesses`); ``emit(ins, op_index, op, value)`` per access.

    v6: an MSVC padding nop (``lea r, [r+0]``, :func:`is_padding_nop`) changes nothing and is no access.
    ``esp``/``rsp`` is tracked as ``("frame", off)`` (off from the entry stack pointer) on PC always and on
    PS4 when the incoming state carries it (:func:`block_in_states` with ``frame=True``); the stack
    argument loads stay PC only.
    """
    st = dict(state)
    mnem, ops = ins["mnem"], ins.get("ops", [])
    if is_padding_nop(ins, ptr):
        return st
    frame = side == "pc"
    track = frame or "rsp" in st
    for i, op in enumerate(ops):
        if op.get("type") not in ("phrase", "displ") or mnem in ("nop",):
            continue
        val = st.get(op.get("base"))
        if val is None:
            if frame and op.get("base") in ("rsp", "rbp") and op.get("chg") and mnem != "push":
                st["_dirty"] = st.get("_dirty", frozenset()) | {"*"}
            continue
        if val[0] in ("arg", "field"):
            emit(ins, i, op, val)
        elif val[0] == "frame" and (op.get("chg") or mnem == "lea") and op.get("index") is None:
            loc = val[1] + op.get("addr", 0)
            if mnem == "lea":
                if loc >= 4:
                    st["_dirty"] = st.get("_dirty", frozenset()) | {"*"}
            else:
                hit = _slots(loc, op.get("size") or 4)
                if hit:
                    st["_dirty"] = st.get("_dirty", frozenset()) | hit
        elif val[0] == "frame" and op.get("chg"):
            st["_dirty"] = st.get("_dirty", frozenset()) | {"*"}
    # new register values
    new: dict = {}
    if mnem == "mov" and len(ops) == 2 and ops[0].get("type") == "reg" and ops[0].get("size") == ptr:
        dst, src = ops[0]["reg"], ops[1]
        if src.get("type") == "reg" and src.get("size") == ptr and src.get("reg") in st:
            new[dst] = st[src["reg"]]
        elif src.get("type") in ("phrase", "displ") and src.get("index") is None and src.get("size") == ptr:
            base = st.get(src.get("base"))
            if base is not None and base[0] == "arg":
                new[dst] = ("field", base[1], base[2], src.get("addr", 0))
            elif base is not None and base[0] == "frame" and frame:
                loc = base[1] + src.get("addr", 0)
                dirty = st.get("_dirty", frozenset())
                if loc >= 4 and (loc - 4) % 4 == 0 and (loc - 4) // 4 not in dirty and "*" not in dirty:
                    new[dst] = ("arg", "stack", (loc - 4) // 4)
    esp = st.get("rsp") if track else None
    if track:
        if mnem == "push" and esp is not None:
            new["rsp"] = ("frame", esp[1] - ptr)
        elif mnem == "pop" and esp is not None:
            new["rsp"] = ("frame", esp[1] + ptr)
        elif mnem in ("sub", "add") and len(ops) == 2 and ops[0].get("type") == "reg" \
                and ops[0].get("reg") == "rsp" and ops[1].get("type") == "imm" and esp is not None:
            d = signed(ops[1]["value"], 8 * ptr)
            new["rsp"] = ("frame", esp[1] + (d if mnem == "add" else -d))
        elif ins.get("call") and esp is not None and not frame:
            new["rsp"] = esp  # SysV: the callee's ret pops only the return address
        elif ins.get("call") and esp is not None and ins.get("pops") is not None:
            new["rsp"] = ("frame", esp[1] + ins["pops"])
    killed = {canon_reg(r) for r in ins.get("writes", ())}
    if ins.get("call"):
        killed |= set(_CALL_CLOBBER[side])
    if track and (mnem in ("push", "pop") or ins.get("call") or mnem in _ESP_OPAQUE):
        killed.add("rsp")
    for r in killed:
        st.pop(r, None)
    st.update(new)
    return st


def block_in_states(blocks: list[tuple[int, list[dict]]], preds: dict[int, list[int]], entry: int,
                    side: str, frame: bool = False) -> dict[int, dict | None]:
    """The must-analysis of :func:`object_accesses`: each block's incoming state (None = not reached).

    ``frame`` (v6) also tracks the PS4 ``rsp`` from entry (PC always tracks ``esp``).
    """
    ptr = 4 if side == "pc" else 8
    init: dict = {r: _arg_value(side, r) for r in _ENTRY_ARGS[side]}
    if side == "pc" or frame:
        init["rsp"] = ("frame", 0)
    order = [b for b, _ in blocks]
    body = dict(blocks)
    outs: dict[int, dict | None] = {b: None for b in order}

    def in_state(b):
        incoming = [outs[p] for p in preds.get(b, ()) if p in outs and outs[p] is not None]
        if b == entry:
            incoming.append(init)
        if not incoming:
            return {}
        return _meet(incoming)

    def reached(b):
        return b == entry or any(outs.get(p) is not None for p in preds.get(b, ()))

    def noemit(*_):
        return None

    changed = True
    rounds = 0
    while changed:
        changed = False
        rounds += 1
        if rounds > 4 * len(order) + 8:
            raise RuntimeError("object_accesses: no fixed point")
        for b in order:
            if b != entry and outs[b] is None and not reached(b):
                continue  # not reached yet
            st = in_state(b)
            for ins in body[b]:
                st = _step(st, ins, side, ptr, noemit)
            if st != outs[b]:
                outs[b] = st
                changed = True
    return {b: (in_state(b) if reached(b) else None) for b in order}


def object_accesses(blocks: list[tuple[int, list[dict]]], preds: dict[int, list[int]], entry: int,
                    side: str) -> list[dict]:
    """Memory accesses ``[base + disp]`` whose base provably holds a function argument (v4).

    ``blocks``: ``(start, instructions)`` in address order; ``preds``: block -> predecessor blocks.
    Each instruction is ``{"ea", "mnem", "ops", "writes", "call", "pops"}``: ``writes`` every register
    written (explicit and implicit, any width), ``call`` for call instructions, ``pops`` (PC) the stack
    bytes the callee's single ``ret N`` releases (0 for ``retn``, None when unknown). Memory operands
    carry ``base``/``index``/``scale`` (:func:`decode_mem`), ``addr`` (signed displacement), ``size``,
    ``chg``/``use`` (IDA's CF_CHGn/CF_USEn for that operand).

    Tracked values (a must-analysis over the blocks, iterated to a fixed point: a register holds a value
    in a block only if every predecessor agrees):
    - PC ``ecx`` at entry (``arg_loc "ecx"``, the thiscall ``this`` when the function is thiscall), PS4
      ``rdi``..``r9`` at entry (``arg`` = ABI index); copies by a pointer-width ``mov r, r``.
    - PC stack arguments: ``esp`` is tracked from entry (push/pop/``sub``/``add esp, imm``, calls with known
      ``pops``; ``ebp`` by copy), and ``mov r32, [esp/ebp+N]`` that reads entry ``esp+4+4k`` gives stack
      argument ``k``, unless a store, or a ``lea`` that leaks the argument area, may have changed it.
    - One dereference: ``mov r, [arg+disp]`` (pointer width, not indexed) gives a field pointer; accesses
      through it carry ``via`` = that disp (PS4 ``this->mpManager->mErrorCode[idx]``).
    A call clobbers the caller-saved registers (ABI), any write kills the register.

    Returns one record per memory operand: ``va``, ``op``, ``arg``, ``arg_loc``, ``disp``, ``width``,
    ``access`` (``load``/``store``/``lea``), ``rmw`` (store that also reads), ``value`` (store of an
    immediate, masked to the width), ``via``, ``indexed`` + ``index`` + ``scale``.
    """
    ptr = 4 if side == "pc" else 8
    ins_of = block_in_states(blocks, preds, entry, side)
    out: list[dict] = []

    def emit(ins, i, op, val):
        mnem = ins["mnem"]
        access = "lea" if mnem == "lea" else ("store" if op.get("chg") else "load")
        rec = {"va": ins["ea"], "op": i, "arg_loc": val[1], "arg": val[2], "disp": op.get("addr", 0),
               "width": None if access == "lea" else op.get("size"), "access": access}
        if access == "store" and op.get("use"):
            rec["rmw"] = True
        if access == "store" and mnem == "mov" and len(ins["ops"]) == 2 and ins["ops"][1].get("type") == "imm" \
                and op.get("size"):
            rec["value"] = ins["ops"][1]["value"] & ((1 << (8 * op["size"])) - 1)
        if val[0] == "field":
            rec["via"] = val[3]
        if op.get("index") is not None:
            rec.update({"indexed": True, "index": op["index"], "scale": op.get("scale")})
        out.append(rec)

    for b, body in blocks:
        st = ins_of[b]
        if st is None:
            continue
        for ins in body:
            st = _step(st, ins, side, ptr, emit)
    return sorted(out, key=lambda r: (r["va"], r["op"]))
