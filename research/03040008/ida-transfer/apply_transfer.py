"""Write the T006 transfer rows to the PC 03040008 work copy and check them back (spec 007 T007).

Headless batch only, on the work copy ``ddon-data-007work`` (README "Read path and write path")::

    idat -A -L<log> -S"apply_transfer.py <manifest/transfer dir> <OUT jsonl> [--apply]" <work copy .i64>
    idat -A -L<log> -S"apply_transfer.py <dir> <OUT jsonl> --verify --apply-log <apply jsonl>" <work copy .i64>
    idat -A -L<log> -S"apply_transfer.py <dir> <OUT jsonl> --undo <apply jsonl>" <work copy .i64>

Modes:

- dry run (default): computes every action and its before-state, writes nothing to the database and
  exits with ``DBFL_KILL`` (the copy is not re-saved);
- ``--apply``: writes, then ``idc.qexit(0)`` saves and packs the database;
- ``--verify`` (read-only, ``DBFL_KILL``): every row against the database, the counts of non-default
  names, typed functions and local types against the apply log's header plus the applied rows, and a
  decompilation of every function with a transferred prototype;
- ``--undo <apply jsonl>``: restores the before-state of every ``undo`` record of an apply log, in
  reverse order (the recovery path; saves).

Precheck (every mode): the database input sha256 is the PC exe's (:data:`PC_SHA256`), the idb path is
under ``ddon-data-007work``, and every manifest file names the same PC dump source. The manifest
files' sha256 go into the header.

Apply order: types (``types.h``; through the ``ida_typeinf`` tinfo/udt API, so template names such as
``MtTypedArray<CDataX>`` stay verbatim), ``remove-label`` rows, names (``set``/``correct``),
prototypes (``set``/``replace``; ``apply_tinfo`` with ``TINFO_DEFINITE``; compared as ``tinfo_t``,
:func:`same_prototype`),
function comments (``set``/``append``; appended below a ``----`` line, never replaced). ``correct`` names and
``replace`` prototypes (T009b: settled conflicts) overwrite a user value only when the database's current value
equals the row's ``current`` (else ``refused current-changed``). ``conflict`` rows
of ``skipped.tsv`` are reported, never written. Every write: the ``undo`` record (before-state) is
written and flushed first, then the write, then a read-back compared with the row (mismatch: ``failed``
with both values, no retry). A second ``--apply`` finds every row ``already``.

The decisions are pure functions over an adapter (:class:`_Ida` in IDA, fakes in
``tests/test_apply_transfer.py``).
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from dataclasses import dataclass, field

SCRIPT_VERSION = "2"
PC_SHA256 = "f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20"
WORK_COPY_MARK = "ddon-data-007work"
# T013c: the smoke test's scratch copy of the work copy (``cp``, deleted afterwards)
WORK_COPY_MARKS = (WORK_COPY_MARK, "ddon-data-007smoke")
SUMMARY_PREFIX = "apply_transfer summary: "
SEPARATOR = "\n----\n"
MANIFEST_FILES = ("names.tsv", "prototypes.tsv", "comments.tsv", "types.tsv", "skipped.tsv", "types.h")
# wave 2 (T013c, ``transfer.py --wave2``): partial types and locals only
MANIFEST_FILES_W2 = ("types.tsv", "locals.tsv", "types.h")
STEPS = ("types", "remove-label", "names", "prototypes", "comments", "locals")
WRITTEN = {"set", "declared", "defined", "replaced", "removed", "restored"}


# --- manifest -------------------------------------------------------------------------------------

def _unescape(cell: str) -> str:
    """Inverse of transfer/run.py ``_cell`` (``\\\\``, ``\\t``, ``\\n``)."""
    return re.sub(r"\\(\\|t|n)", lambda m: {"\\": "\\", "t": "\t", "n": "\n"}[m.group(1)], cell)


def read_tsv(path: str) -> tuple[str, list[dict]]:
    """A T006 TSV: one ``#`` header comment line, the column line, the rows."""
    with open(path, encoding="utf-8", newline="") as fh:
        head = fh.readline().rstrip("\n")
        if not head.startswith("#"):
            raise ValueError(f"{path}: no header comment")
        rd = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
        cols = next(rd)
        rows = []
        for n, r in enumerate(rd, start=3):
            if len(r) != len(cols):
                raise ValueError(f"{path}:{n}: {len(r)} cells, {len(cols)} columns")
            rows.append({c: _unescape(v) for c, v in zip(cols, r, strict=True)})
    return head, rows


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _our_comment(r: dict) -> dict:
    """An ``append`` row carries ``existing + SEPARATOR + ours``; T007 appends ``ours`` to whatever the database
    holds (never replaces), so the row keeps only ``ours``. A row not of that shape fails closed."""
    if r["action"] == "set":
        return r
    prefix = r["existing"] + SEPARATOR
    if not r["existing"] or not r["comment"].startswith(prefix) or len(r["comment"]) == len(prefix):
        raise ValueError(f"comments.tsv {r['pc_va']}: append row is not existing + separator + ours")
    return {**r, "comment": r["comment"][len(prefix):]}


def load_manifest(directory: str) -> dict:
    """The T006 rows T007 writes, the conflicts it reports, ``types.h`` and the files' sha256. A wave-2 directory
    (``locals.tsv`` present, T013c) has types and locals only."""
    wave2 = os.path.exists(os.path.join(directory, "locals.tsv"))
    files = MANIFEST_FILES_W2 if wave2 else MANIFEST_FILES
    sha = {f: _sha256(os.path.join(directory, f)) for f in files}
    heads = {}
    tables = {}
    for f in files[:-1]:
        heads[f], tables[f] = read_tsv(os.path.join(directory, f))
    with open(os.path.join(directory, "types.h"), encoding="utf-8") as fh:
        header_text = fh.read()
    heads["types.h"] = header_text.split("\n", 1)[0]
    pc_source = f"pc-ida.jsonl source {PC_SHA256}"
    for f, h in heads.items():
        if pc_source not in h:
            raise ValueError(f"{f}: header does not name {pc_source!r}")
    if len(set(h.lstrip("#/ ") for h in heads.values())) != 1:
        raise ValueError("manifest files come from different T006 runs")
    if wave2:
        bad = [r for r in tables["locals.tsv"] if r["status"] not in ("accepted", "refused", "duplicate")]
        if bad:
            raise ValueError("locals.tsv rows with a status this script does not know")
        return {"sha256": sha, "head": heads["types.tsv"], "names": [], "labels": [], "prototypes": [],
                "comments": [], "types": {r["type"]: r for r in tables["types.tsv"]}, "types_h": header_text,
                "conflicts": [], "locals": [r for r in tables["locals.tsv"] if r["status"] == "accepted"],
                "wave": 2}
    names = [r for r in tables["names.tsv"] if r["action"] in ("set", "correct")]
    labels = [r for r in tables["names.tsv"] if r["action"] == "remove-label"]
    other = [r for r in tables["names.tsv"] if r["action"] not in ("set", "correct", "remove-label")]
    protos = [r for r in tables["prototypes.tsv"] if r["action"] in ("set", "replace")]
    comments = [_our_comment(r) for r in tables["comments.tsv"] if r["action"] in ("set", "append")]
    if other or len(protos) != len(tables["prototypes.tsv"]) or len(comments) != len(tables["comments.tsv"]):
        raise ValueError("manifest rows with an action this script does not know")
    conflicts = [r for r in tables["skipped.tsv"] if r["action"] == "conflict"]
    return {"sha256": sha, "head": heads["names.tsv"], "names": names, "labels": labels, "prototypes": protos,
            "comments": comments, "types": {r["type"]: r for r in tables["types.tsv"]},
            "types_h": header_text, "conflicts": conflicts, "locals": [], "wave": 1}


def select(manifest: dict, decls: list[TypeDecl], limit_types: int | None, limit_locals: int | None
           ) -> tuple[list[TypeDecl], list[dict]]:
    """The smoke-test filter (T013c): the first ``limit_types`` partial types (those a local is retyped to
    first, then in ``types.h`` order) with every declaration they embed, and the first ``limit_locals`` locals
    whose retype is none or a selected type. Without limits: everything."""
    rows = manifest["locals"]
    if limit_types is None and limit_locals is None:
        return decls, rows
    partial = [d.name for d in decls if d.kind == "struct" and manifest["types"].get(d.name, {}).get("status")
               == "partial"]
    first = [r["retype"] for r in rows if r["retype"] in partial]
    order = list(dict.fromkeys(first + partial))
    chosen = set(order[:limit_types] if limit_types is not None else order)
    by_name = {d.name: d for d in decls if d.kind == "struct"}
    keep = set(chosen)
    todo = list(chosen)
    while todo:
        for ref in by_name[todo.pop()].refs():
            if ref in by_name and ref not in keep:
                keep.add(ref)
                todo.append(ref)
    out = [d for d in decls if d.name in keep and (d.kind == "struct" or d.name not in by_name)]
    loc = [r for r in rows if r["retype"] == "-" or r["retype"] in chosen]
    return out, loc[:limit_locals] if limit_locals is not None else loc


# --- types.h --------------------------------------------------------------------------------------

@dataclass
class Member:
    name: str
    type: str  # base type text, without pointer stars
    ptr: int  # pointer depth
    count: int | None  # array element count
    offset: int
    size: int
    base: bool = False
    vptr: bool = False
    base_of: str | None = None  # class of an untransferred base rendered as bytes (``base X (not transferred)``)


@dataclass
class TypeDecl:
    name: str
    kind: str  # "opaque" or "struct"
    size: int | None = None
    members: list[Member] = field(default_factory=list)
    comment: str | None = None  # T013c: ``// <name>: Partial: ...`` line before the struct (the type comment)

    def refs(self) -> set[str]:
        """Types this struct embeds by value (they must be defined first)."""
        return {m.type for m in self.members if m.ptr == 0}

    def row_members(self) -> list[tuple]:
        """The members in the adapter's form ``(name, offset, size, kind, type)``; a plain member's type with its
        pointer depth and array count (:func:`row_type`), as the adapter prints an unnamed type."""
        return [(m.name, m.offset, m.size, "vptr" if m.vptr else "base" if m.base else "",
                 m.type if m.vptr or m.base else row_type(m))
                for m in self.members]


def layout_key(size, members) -> tuple:
    """Size and the non-gap members as given (exact; used for before/after states of one database)."""
    return size, tuple(tuple(m) for m in members if not re.fullmatch(r"gap[0-9A-Fa-f]+", m[0]))


_VPTR_NAME = re.compile(r"__vftable|_vptr\$.*|vfptr")
_BASE_NAME = re.compile(r"baseclass_[0-9A-Fa-f]+")


def existing_member(m) -> dict:
    """A local-type member as the IDA adapter reads it: ``(name, offset, size[, kind, type])``.

    ``kind`` is ``"vptr"`` (udm vftable flag), ``"base"`` (udm base-class flag) or ``""``; ``type`` the
    member's type name, or its printed type when it has no name (``MtObject **``, ``unsigned int[4]``).
    Old three-field records read as kind ``""``, type unknown (``None``).
    """
    name, off, size = m[0], m[1], m[2]
    return {"name": name, "offset": off, "size": size, "kind": m[3] if len(m) > 3 else "",
            "type": m[4] if len(m) > 4 else None}


def member_equal(ex: dict, row: Member) -> bool:
    """One existing member against one ``types.h`` member at the same position.

    Offsets and sizes must match. A row vptr equals an existing vptr at 0 (vftable flag, ``__vftable``,
    ``_vptr$*`` or ``vfptr``); a row base equals an existing base (base-class flag, ``baseclass_*``, unnamed,
    or named after its class) whose type name is the row's base class. A row base rendered as bytes because
    its class is not transferred (``base X (not transferred)``, :attr:`Member.base_of`) compares by that class
    ``X``, not by ``unsigned __int8``. Otherwise names must be equal, neither side may be a vptr or a base,
    and a known existing type must equal the row's type with its pointer depth and array count
    (:func:`norm_type`; T008 F2: offset, size and name alone let ``MtObject *`` pass for ``MtObject **``).
    """
    if (ex["offset"], ex["size"]) != (row.offset, row.size):
        return False
    if row.vptr:
        return row.offset == 0 and ex["kind"] != "base" and (ex["kind"] == "vptr" or bool(
            _VPTR_NAME.fullmatch(ex["name"])))
    if row.base:
        cls = row.base_of or row.type
        if ex["kind"] == "vptr" or ex["type"] != cls:
            return False
        return ex["kind"] == "base" or ex["name"] in ("", cls) or bool(_BASE_NAME.fullmatch(ex["name"]))
    if ex["kind"] != "" or ex["name"] != row.name:
        return False
    return ex["type"] is None or norm_type(ex["type"]) == norm_type(row_type(row))


_TYPE_NOISE = re.compile(r"\b(?:struct|const)\b|\s+")


# one spelling per scalar: the database's typedefs (T007e: ``uint32_t mLength``) and IDA's sized names
_SCALAR_ALIAS = {
    alias: canon
    for canon, aliases in {
        "unsigned __int8": ("uint8_t", "_BYTE", "unsigned char", "unsigned __int8"),
        "__int8": ("int8_t", "signed char", "signed __int8", "__int8"),
        "unsigned __int16": ("uint16_t", "_WORD", "unsigned short", "unsigned __int16"),
        "__int16": ("int16_t", "short", "signed __int16", "__int16"),
        "unsigned int": ("uint32_t", "_DWORD", "unsigned int", "unsigned __int32"),
        "int": ("int32_t", "int", "signed int", "__int32", "signed __int32"),
        "unsigned __int64": ("uint64_t", "_QWORD", "unsigned __int64", "unsigned long long"),
        "__int64": ("int64_t", "__int64", "signed __int64", "long long"),
    }.items()
    for alias in aliases
}
_SCALAR_KEY = {_TYPE_NOISE.sub("", a): _TYPE_NOISE.sub("", c) for a, c in _SCALAR_ALIAS.items()}
_TYPE_SUFFIX = re.compile(r"[*&]*(?:\[\d+\])*$")


def norm_type(t: str) -> str:
    """A type text without spaces, ``struct`` (IDA's print prefix, T007d) and ``const``; a scalar base type in
    one spelling (``uint32_t`` = ``unsigned int``), pointer stars and array counts kept."""
    s = _TYPE_NOISE.sub("", t)
    suffix = _TYPE_SUFFIX.search(s)
    assert suffix is not None
    base = s[:suffix.start()]
    return _SCALAR_KEY.get(base, base) + suffix.group(0)


def row_type(m: Member) -> str:
    """A ``types.h`` member's full type: base type, pointer stars, array count (``MtObject **``)."""
    return m.type + (" " + "*" * m.ptr if m.ptr else "") + (f"[{m.count}]" if m.count is not None else "")


def same_layout(size, members, d: TypeDecl) -> bool:
    """Whether an existing local type (``size``, adapter ``members``) is the ``types.h`` struct ``d``."""
    if size != d.size:
        return False
    ex = [existing_member(m) for m in members if not _GAP.fullmatch(m[0])]
    rw = [m for m in d.members if not _GAP.fullmatch(m.name)]
    return len(ex) == len(rw) and all(member_equal(e, r) for e, r in zip(ex, rw, strict=True))


_MEMBER = re.compile(r"(?P<type>[^*;]+?)\s*(?P<stars>\*+)?\s*(?P<name>[A-Za-z_]\w*)(?:\[(?P<n>\d+)\])?;"
                     r"(?:\s*//\s*\+0x(?P<off>[0-9a-fA-F]+)\s+(?P<size>\d+)(?P<rest>.*))?")
_GAP = re.compile(r"gap([0-9A-Fa-f]+)")
_OPAQUE_BASE = re.compile(r"base (?P<cls>.+) \(not transferred\)")
_PARTIAL_NOTE = re.compile(r"//\s*(?P<name>[^;{}]+?): (?P<cmt>Partial: .+)")


def parse_types_h(text: str) -> list[TypeDecl]:
    """The declarations of T006's generated header, in order (dependencies first).

    The header's own grammar only (transfer/render.py): ``struct X;``, ``struct X // PC size 0x..``
    + ``{`` + one member per line with ``// +0x<off> <size>`` (gaps: ``unsigned __int8 gapN[k];``)
    + ``};``. Anything else fails closed, as does a layout that is not contiguous.
    """
    decls: list[TypeDecl] = []
    cur: TypeDecl | None = None
    opened = False
    notes: dict[str, str] = {}
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        c = _PARTIAL_NOTE.fullmatch(line)
        if c and cur is None:
            notes[c["name"]] = c["cmt"]
            continue
        if not line or line.startswith("//") or line.startswith("#pragma"):
            continue
        if cur is None:
            m = re.fullmatch(r"struct (?P<name>[^;{}/]+?);", line)
            if m:
                decls.append(TypeDecl(m["name"], "opaque"))
                continue
            m = re.fullmatch(r"struct (?P<name>[^;{}/]+?)\s*//\s*PC size 0x(?P<size>[0-9a-fA-F]+)", line)
            if not m:
                raise ValueError(f"types.h:{n}: unexpected {line!r}")
            cur = TypeDecl(m["name"], "struct", int(m["size"], 16), comment=notes.pop(m["name"], None))
            opened = False
            continue
        if not opened:
            if line != "{":
                raise ValueError(f"types.h:{n}: expected '{{'")
            opened = True
            continue
        if line == "};":
            _check_layout(cur, n)
            decls.append(cur)
            cur = None
            continue
        m = _MEMBER.fullmatch(line)
        if not m:
            raise ValueError(f"types.h:{n}: unexpected member {line!r}")
        count = int(m["n"]) if m["n"] else None
        g = _GAP.fullmatch(m["name"])
        if m["off"] is not None:
            off, size, rest = int(m["off"], 16), int(m["size"]), m["rest"] or ""
        elif g and m["type"] == "unsigned __int8" and count and not m["stars"]:
            off, size, rest = int(g[1], 16), count, ""
        else:
            raise ValueError(f"types.h:{n}: member without offset {line!r}")
        member = Member(m["name"], m["type"].strip(), len(m["stars"] or ""), count, off, size,
                        base=rest.strip().startswith("base "), vptr=rest.strip() == "vptr")
        ob = _OPAQUE_BASE.fullmatch(rest.strip())
        if ob:  # render.py: ``unsigned __int8 baseclass_<off>[<size>]; // ... base X (not transferred)``
            if (member.type, member.ptr, member.count, member.name) != ("unsigned __int8", 0, size,
                                                                        f"baseclass_{off:X}"):
                raise ValueError(f"types.h:{n}: untransferred base not rendered as bytes {line!r}")
            member.base_of = ob["cls"]
        cur.members.append(member)
    if cur is not None:
        raise ValueError("types.h: unterminated struct")
    seen: set[str] = set()
    for d in decls:
        if d.kind == "struct" and d.name in seen and any(x.name == d.name and x.kind == "struct" for x in decls
                                                         if x is not d):
            raise ValueError(f"types.h: {d.name} defined twice")
        seen.add(d.name)
    return decls


def render_decls(decls: list[TypeDecl]) -> str:
    """``types.h`` text of parsed declarations (the filter's subset; :func:`parse_types_h` reads it back)."""
    out = []
    for d in decls:
        if d.kind == "opaque":
            out.append(f"struct {d.name};")
            continue
        if d.comment:
            out.append(f"// {d.name}: {d.comment}")
        out += [f"struct {d.name} // PC size {d.size:#x}", "{"]
        for m in d.members:
            stars = " " + "*" * m.ptr if m.ptr else ""
            cnt = f"[{m.count}]" if m.count is not None else ""
            if m.vptr:
                rest = " vptr"
            elif m.base_of:
                rest = f" base {m.base_of} (not transferred)"
            elif m.base:
                rest = f" base {m.type}"
            else:
                rest = ""
            out.append(f"  {m.type}{stars} {m.name}{cnt}; // +{m.offset:#x} {m.size}{rest}")
        out.append("};")
    return "\n".join(out) + "\n"


def _check_layout(d: TypeDecl, n: int) -> None:
    at = 0
    for m in d.members:
        if m.offset != at:
            raise ValueError(f"types.h:{n}: {d.name}.{m.name} at {m.offset:#x}, expected {at:#x}")
        at += m.size
    if at != d.size:
        raise ValueError(f"types.h:{n}: {d.name} members end at {at:#x}, size {d.size:#x}")


# --- prototypes -----------------------------------------------------------------------------------

def norm(s: str | None) -> str:
    return " ".join((s or "").split())


_CC = re.compile(r"\b(__thiscall|__stdcall|__cdecl|__fastcall)\s*\(")


def split_args(text: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch in "<(":
            depth += 1
        elif ch in ">)":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def prototype_plan(decl: str, special: list[str]) -> dict:
    """A parseable declaration for ``decl`` plus the arguments to patch through the tinfo API.

    ``special`` are type names the C parser may refuse (templates, ``::``). Each argument (or the return
    type) that names one is parsed as ``void`` with the same pointer depth and patched afterwards to a
    pointer to the named local type: ``patch`` = [(index or -1 for the return, name, depth)].
    """
    m = _CC.search(decl)
    if not m or not decl.rstrip().endswith(")"):
        raise ValueError(f"not a function type: {decl!r}")
    ret = decl[:m.start()].strip()
    args = split_args(decl[m.end():decl.rstrip().rfind(")")])
    names = sorted(special, key=len, reverse=True)
    patch = []

    def fix(text: str, idx: int) -> str:
        for name in names:
            mm = re.fullmatch(rf"(?:struct\s+)?{re.escape(name)}\s*(?P<stars>\**)\s*(?P<var>[A-Za-z_]\w*)?", text)
            if mm:
                if not mm["stars"]:
                    raise ValueError(f"{name} by value in {decl!r}")
                patch.append((idx, name, len(mm["stars"])))
                return f"void {mm['stars']}{mm['var'] or ''}".rstrip()
            if re.search(rf"(?<![\w:<]){re.escape(name)}(?![\w>])", text):
                raise ValueError(f"{name} in an unsupported position in {decl!r}")
        return text

    ret2 = fix(ret, -1)
    args2 = [fix(a, i) for i, a in enumerate(args)]
    parse = f"{ret2} {m.group(1)} __t007_f({', '.join(args2)});"
    return {"parse": parse, "patch": patch}


def same_prototype(ida, a, b) -> bool:
    """Whether two function ``tinfo_t`` are the same prototype, compared as types, not printed text.

    Calling convention, return type, argument count, and each argument's type (``ida.type_equal``:
    ``tinfo_t.compare_with(.., TCMP_EQUAL)``) and name. The function's own name is not part of its type.
    IDA prints a ``::`` or template type as ``struct X``; the row text has no ``struct `` (T007b rerun).
    """
    pa, pb = ida.func_parts(a), ida.func_parts(b)
    if pa is None or pb is None or pa["cc"] != pb["cc"] or len(pa["args"]) != len(pb["args"]):
        return False
    if not ida.type_equal(pa["ret"], pb["ret"]):
        return False
    return all(na == nb and ida.type_equal(ta, tb)
               for (ta, na), (tb, nb) in zip(pa["args"], pb["args"], strict=True))


def row_prototype(ida, decl: str, special: list[str]):
    """The row's declaration as a ``tinfo_t`` (the parse used for writing), or None when it does not parse."""
    try:
        plan = prototype_plan(decl, special)
    except ValueError:
        return None
    tif, err = ida.parse_prototype(plan)
    return None if err else tif


def has_prototype(ida, ea: int, decl: str, special: list[str]) -> bool:
    """Whether the function at ``ea`` has the row's prototype (types compared, see :func:`same_prototype`)."""
    row = row_prototype(ida, decl, special)
    cur = ida.func_tinfo(ea)
    return row is not None and cur is not None and same_prototype(ida, cur, row)


def unique_decls(decls: list[TypeDecl]) -> list[TypeDecl]:
    """One declaration per name, the struct body where a name is also declared opaque."""
    best: dict[str, TypeDecl] = {}
    for d in decls:
        if d.name not in best or d.kind == "struct":
            best[d.name] = d
    return list(best.values())


# --- planning and writing -------------------------------------------------------------------------

class Log:
    """The OUT jsonl: one record per line, flushed after each (undo records precede their writes)."""

    def __init__(self, fh):
        self.fh = fh
        self.results: list[dict] = []

    def write(self, rec: dict) -> None:
        self.fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        self.fh.flush()
        if rec.get("kind") == "result":
            self.results.append(rec)


def _result(log: Log, step: str, key, status: str, **kw) -> dict:
    rec = {"kind": "result", "step": step, "key": key, "status": status, **kw}
    log.write(rec)
    return rec


def precheck(ida) -> dict:
    sha = ida.input_sha256()
    path = ida.idb_path() or ""
    if sha != PC_SHA256:
        raise ValueError(f"input sha256 {sha} is not the PC 03040008 exe {PC_SHA256}")
    if not any(m.lower() in path.replace("\\", "/").lower() for m in WORK_COPY_MARKS):
        raise ValueError(f"database {path!r} is not under {' or '.join(WORK_COPY_MARKS)}")
    return {"input_sha256": sha, "idb_path": path}


def special_names(decls: list[TypeDecl], manifest: dict) -> list[str]:
    names = {d.name for d in decls}
    for r in manifest["prototypes"]:
        names.update(t for t in r.get("types", "").split() if t != "-")
    return sorted(n for n in names if re.search(r"[^A-Za-z0-9_]", n))


def do_types(ida, decls: list[TypeDecl], rows: dict, apply: bool, log: Log) -> set[str]:
    """Plan and (with ``apply``) write the local types. Returns the refused type names."""
    plan: dict[str, tuple[str, dict]] = {}
    before: dict[str, dict | None] = {}
    for d in decls:
        if d.name in plan and d.kind == "opaque":
            continue
        ex = ida.local_type(d.name)
        before[d.name] = ex
        row = rows.get(d.name, {})
        if d.kind == "opaque":
            plan[d.name] = ("already", {}) if ex is not None else ("declare", {})
        elif ex is None or ex.get("forward"):
            plan[d.name] = ("define", {})
        elif same_layout(ex["size"], ex["members"], d):
            plan[d.name] = ("already", {})
        elif row.get("status") == "replace":
            plan[d.name] = ("replace", {"reason": row.get("basis", "")})
        else:
            plan[d.name] = ("refused", {"check": "different-local-type",
                                        "existing": _layout_json(ex["size"], ex["members"]),
                                        "row": _layout_json(d.size, d.row_members())})
    structs = {d.name: d for d in decls if d.kind == "struct"}
    changed = True
    while changed:  # a struct embedding a refused struct is refused
        changed = False
        for name, d in structs.items():
            if plan[name][0] in ("refused",):
                continue
            bad = sorted(r for r in d.refs() if r in plan and plan[r][0] == "refused")
            if bad:
                plan[name] = ("refused", {"check": "embeds-refused-type", "types": bad})
                changed = True
    refused = {n for n, (a, _) in plan.items() if a == "refused"}
    order = list(dict.fromkeys(d.name for d in decls))
    # forward declarations first, so every reference by name resolves
    for name in order:
        action, info = plan[name]
        if action in ("already", "refused"):
            _result(log, "types", name, action, **info)
            continue
        if not apply:
            _result(log, "types", name, f"would-{action}", **info)
            continue
        if before[name] is None:
            log.write({"kind": "undo", "step": "types", "key": name, "before": None})
            err = ida.declare_forward(name)
            if err:
                plan[name] = ("failed", {"check": "declare", "error": err})
    for name in order:
        action, info = plan[name]
        if not apply or action in ("already", "refused"):
            continue
        if action == "failed":
            _result(log, "types", name, "failed", **info)
            continue
        if action == "declare":
            got = ida.local_type(name)
            _result(log, "types", name, "declared" if got is not None else "failed",
                    **({} if got is not None else {"check": "read-back", "got": None}))
            continue
        d = structs[name]
        if before[name] is not None:
            log.write({"kind": "undo", "step": "types", "key": name, "before": before[name]})
        err = ida.define_struct(d)
        got = ida.local_type(name)
        if err:
            _result(log, "types", name, "failed", check="define", error=err)
        elif got is None or got.get("forward") or not same_layout(got["size"], got["members"], d):
            _result(log, "types", name, "failed", check="read-back",
                    got=None if got is None or got.get("forward") else _layout_json(got["size"], got["members"]),
                    row=_layout_json(d.size, d.row_members()))
        else:
            if d.comment:
                info = {**info, "comment": d.comment, "comment_error": ida.set_type_comment(name, d.comment)}
            _result(log, "types", name, "defined" if action == "define" else "replaced", **info)
    return refused


def _layout_json(size, members) -> dict:
    return {"size": size, "members": [list(m) for m in members]}


def do_labels(ida, rows: list[dict], apply: bool, log: Log) -> set[int]:
    """``remove-label`` rows. Returns the addresses whose label is (or would be) gone."""
    gone = set()
    for r in rows:
        ea = int(r["pc_va"], 16)
        name, user = ida.get_name(ea), ida.has_user_name(ea)
        if not user:
            gone.add(ea)
            _result(log, "remove-label", r["pc_va"], "already")
            continue
        if name != r["current"]:
            _result(log, "remove-label", r["pc_va"], "refused", check="current-changed", db=name, row=r["current"])
            continue
        if not apply:
            gone.add(ea)
            _result(log, "remove-label", r["pc_va"], "would-remove", db=name)
            continue
        log.write({"kind": "undo", "step": "remove-label", "key": r["pc_va"], "before": {"name": name, "user": True}})
        ok = ida.set_name(ea, "")
        if ok and not ida.has_user_name(ea):
            gone.add(ea)
            _result(log, "remove-label", r["pc_va"], "removed", before=name)
        else:
            _result(log, "remove-label", r["pc_va"], "failed", check="read-back", db=ida.get_name(ea), row="")
    return gone


def do_names(ida, rows: list[dict], gone: set[int], apply: bool, log: Log) -> None:
    for r in rows:
        ea, key = int(r["pc_va"], 16), r["pc_va"]
        name, user = ida.get_name(ea), ida.has_user_name(ea)
        if name == r["name"] and user:
            _result(log, "names", key, "already")
            continue
        if ida.func_start(ea) != ea:
            _result(log, "names", key, "refused", check="not-function-start")
            continue
        if name != r["current"]:
            _result(log, "names", key, "refused", check="current-changed", db=name, row=r["current"])
            continue
        other = ida.name_ea(r["name"])
        if other is not None and other != ea and other not in gone:
            _result(log, "names", key, "refused", check="name-used-elsewhere", at=f"{other:#x}", name=r["name"])
            continue
        if not apply:
            _result(log, "names", key, "would-set", action=r["action"], db=name)
            continue
        log.write({"kind": "undo", "step": "names", "key": key, "before": {"name": name, "user": user}})
        ok = ida.set_name(ea, r["name"])
        got = ida.get_name(ea)
        if ok and got == r["name"]:
            _result(log, "names", key, "set", action=r["action"], before=name, before_user=user)
        else:
            _result(log, "names", key, "failed", check="read-back", db=got, row=r["name"])


def do_prototypes(ida, rows: list[dict], special: list[str], refused_types: set[str], apply: bool,
                  log: Log) -> None:
    for r in rows:
        ea, key = int(r["pc_va"], 16), r["pc_va"]
        cur, user = ida.get_type(ea), ida.is_userti(ea)
        if user and has_prototype(ida, ea, r["decl"], special):
            _result(log, "prototypes", key, "already")
            continue
        if ida.func_start(ea) != ea:
            _result(log, "prototypes", key, "refused", check="not-function-start")
            continue
        bad = sorted(t for t in r.get("types", "").split() if t in refused_types)
        if bad:
            _result(log, "prototypes", key, "refused", check="uses-refused-type", types=bad)
            continue
        if user and r["action"] != "replace":  # replace: a settled conflict, guarded by the current check
            _result(log, "prototypes", key, "refused", check="user-prototype", db=cur, row=r["decl"])
            continue
        if norm(cur) != norm(r["current"]):
            _result(log, "prototypes", key, "refused", check="current-changed", db=cur, row=r["current"])
            continue
        try:
            plan = prototype_plan(r["decl"], special)
        except ValueError as e:
            _result(log, "prototypes", key, "refused", check="parse", error=str(e))
            continue
        if not apply:
            _result(log, "prototypes", key, "would-set", action=r["action"], db=cur)
            continue
        tif, err = ida.parse_prototype(plan)
        if err:
            _result(log, "prototypes", key, "refused", check="parse", error=err)
            continue
        log.write({"kind": "undo", "step": "prototypes", "key": key,
                   "before": {"type": cur, "user": user, "blob": ida.type_blob(ea)}})
        ok = ida.apply_prototype(ea, tif)
        got = ida.get_type(ea)
        cur_tif = ida.func_tinfo(ea)
        if ok and cur_tif is not None and same_prototype(ida, cur_tif, tif):
            _result(log, "prototypes", key, "set", action=r["action"], before=cur, before_user=user)
        else:
            _result(log, "prototypes", key, "failed", check="read-back", db=got, row=r["decl"], applied=bool(ok))


def merged_comment(existing: str, ours: str) -> str | None:
    """The comment to write, or None when ours is already there."""
    existing = existing or ""
    if ours in existing.split(SEPARATOR):
        return None
    return ours if not existing else existing + SEPARATOR + ours


def do_comments(ida, rows: list[dict], apply: bool, log: Log) -> None:
    for r in rows:
        ea, key = int(r["pc_va"], 16), r["pc_va"]
        if ida.func_start(ea) != ea:
            _result(log, "comments", key, "refused", check="not-function-start")
            continue
        cur = ida.get_func_cmt(ea) or ""
        new = merged_comment(cur, r["comment"])
        if new is None:
            _result(log, "comments", key, "already")
            continue
        if not apply:
            _result(log, "comments", key, "would-set", appended=bool(cur))
            continue
        log.write({"kind": "undo", "step": "comments", "key": key, "before": {"comment": cur}})
        ok = ida.set_func_cmt(ea, new)
        got = ida.get_func_cmt(ea) or ""
        if ok and got == new:
            _result(log, "comments", key, "set", appended=bool(cur))
        else:
            _result(log, "comments", key, "failed", check="read-back", db=got, row=new)


# --- locals (T013c) -------------------------------------------------------------------------------

def local_key(r: dict) -> str:
    return f"{r['pc_va']}@{r['pc_frame']}"


def plan_local(r: dict, found: dict, type_size) -> tuple[str, dict]:
    """(status, details) for one ``locals.tsv`` row against the adapter's :meth:`_Ida.find_lvar` result.

    ``found``: ``{"error"}`` or ``{"ida_off", "lea_off", "matches": [lvar dicts]}``; ``type_size``: the defined
    local type's size of the row's retype (None: absent or a forward declaration).
    The PC lvar is the one stack lvar whose IDA frame offset is the row's entry-relative frame plus the return
    address offset; the defining ``lea`` must address the same offset. Refused: no unique lvar, an argument, a
    user name (or a user type when retyping), a width other than the row's size (R1/R2), a retype whose local
    type is missing or of another size."""
    if found.get("error"):
        return "refused", {"check": "decompile", "error": found["error"]}
    if found.get("lea_off") is not None and found["lea_off"] != found["ida_off"]:
        return "refused", {"check": "frame-mismatch", "ida_off": found["ida_off"], "lea_off": found["lea_off"]}
    ms = found["matches"]
    if len(ms) != 1:
        return "refused", {"check": "lvar-not-unique", "matches": len(ms)}
    m = ms[0]
    retype = r["retype"] if r["retype"] != "-" else None
    size = int(r["size"]) if r["size"] not in ("", "-") else None
    if m["is_arg"]:
        return "refused", {"check": "argument", "lvar": m}
    if m["name"] == r["name"] and (retype is None or norm_type(m["type"] or "") == norm_type(retype)):
        return "already", {"lvar": m}
    if m["user_name"]:
        return "refused", {"check": "user-name", "lvar": m}
    if retype is not None:
        if m["user_type"]:
            return "refused", {"check": "user-type", "lvar": m}
        if type_size is None:
            return "refused", {"check": "type-missing", "type": retype}
        if type_size != size:
            return "refused", {"check": "type-size", "type": retype, "type_size": type_size, "row": size}
    elif m["width"] != size:
        return "refused", {"check": "width", "lvar": m, "row": size}
    return "set", {"lvar": m}


def _type_size(ida, name: str):
    got = ida.local_type(name)
    return None if got is None or got.get("forward") else got["size"]


def _pc_def(r: dict):
    return int(r["pc_def"], 16) if r["pc_def"] not in ("", "-") else None


def do_locals(ida, rows: list[dict], refused_types: set[str], apply: bool, log: Log) -> None:
    for r in rows:
        ea, key = int(r["pc_va"], 16), local_key(r)
        retype = r["retype"] if r["retype"] != "-" else None
        if retype in refused_types:
            _result(log, "locals", key, "refused", check="uses-refused-type", type=retype)
            continue
        found = ida.find_lvar(ea, int(r["pc_frame"]), _pc_def(r))
        status, info = plan_local(r, found, _type_size(ida, retype) if retype else None)
        if status != "set":
            _result(log, "locals", key, status, name=r["name"], rule=r["rule"], **info)
            continue
        m = info["lvar"]
        if not apply:
            _result(log, "locals", key, "would-set", name=r["name"], rule=r["rule"], retype=retype, lvar=m)
            continue
        log.write({"kind": "undo", "step": "locals", "key": key, "before": m})
        err = ida.set_lvar(ea, m, r["name"], retype)
        g = ida.find_lvar(ea, int(r["pc_frame"]), _pc_def(r)).get("matches") or []
        ok = (err is None and len(g) == 1 and g[0]["name"] == r["name"]
              and (retype is None or norm_type(g[0]["type"] or "") == norm_type(retype)))
        if ok:
            _result(log, "locals", key, "set", name=r["name"], rule=r["rule"], retype=retype, before=m, after=g[0])
        else:
            _result(log, "locals", key, "failed", check="read-back", error=err, got=g, name=r["name"],
                    retype=retype)


def report_conflicts(rows: list[dict], log: Log) -> None:
    for r in rows:
        _result(log, f"conflict-{r['rule']}", r["item"], "conflict", candidate=r["candidate"], reason=r["reason"])


def summarize(results: list[dict]) -> dict:
    out: dict[str, dict[str, int]] = {}
    for r in results:
        step = out.setdefault(r["step"], {})
        step[r["status"]] = step.get(r["status"], 0) + 1
    return out


def header(ida, manifest: dict, mode: str, extra=None) -> dict:
    return {"kind": "header", "script": "apply_transfer", "script_version": SCRIPT_VERSION, "mode": mode,
            "build": "PC 03040008", "manifest_sha256": manifest["sha256"], "manifest_head": manifest["head"],
            **precheck(ida), "counts_before": ida.counts(), **(extra or {})}


def run_apply(ida, manifest: dict, apply: bool, log: Log) -> dict:
    log.write(header(ida, manifest, "apply" if apply else "dry-run", {"filter": manifest.get("filter")}))
    decls = parse_types_h(manifest["types_h"])
    special = special_names(decls, manifest)
    refused = do_types(ida, decls, manifest["types"], apply, log)
    gone = do_labels(ida, manifest["labels"], apply, log)
    do_names(ida, manifest["names"], gone, apply, log)
    do_prototypes(ida, manifest["prototypes"], special, refused, apply, log)
    do_comments(ida, manifest["comments"], apply, log)
    do_locals(ida, manifest["locals"], refused, apply, log)
    report_conflicts(manifest["conflicts"], log)
    summary = {"kind": "summary", "mode": "apply" if apply else "dry-run", "steps": summarize(log.results),
               "counts_after": ida.counts()}
    log.write(summary)
    return summary


# --- verify ---------------------------------------------------------------------------------------

def read_log(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def expected_deltas(records: list[dict]) -> dict:
    """Count changes the applied rows of an apply log account for."""
    d = {"names": 0, "typed_functions": 0, "local_types": 0}
    undo_types = {r["key"]: r["before"] for r in records if r.get("kind") == "undo" and r["step"] == "types"}
    for r in records:
        if r.get("kind") != "result":
            continue
        if r["step"] == "names" and r["status"] == "set" and not r.get("before_user"):
            d["names"] += 1
        elif r["step"] == "remove-label" and r["status"] == "removed":
            d["names"] -= 1
        elif r["step"] == "prototypes" and r["status"] == "set" and not r.get("before_user"):
            d["typed_functions"] += 1
        elif r["step"] == "types" and r["status"] in ("declared", "defined") and r["key"] in undo_types \
                and undo_types[r["key"]] is None:
            d["local_types"] += 1
    return d


def run_verify(ida, manifest: dict, apply_records: list[dict], log: Log) -> dict:
    head = next((r for r in apply_records if r.get("kind") == "header"), None)
    if head is None or head.get("mode") != "apply":
        raise ValueError("--apply-log is not an apply log")
    pre = precheck(ida)
    if head["input_sha256"] != pre["input_sha256"]:
        raise ValueError("apply log is for another database")
    if head["manifest_sha256"] != manifest["sha256"]:
        raise ValueError("apply log was written from other manifest files")
    log.write(header(ida, manifest, "verify", {"apply_log_counts_before": head["counts_before"]}))
    if head.get("filter") != manifest.get("filter"):
        raise ValueError("apply log was written with another --limit filter")
    decls = parse_types_h(manifest["types_h"])
    for d in unique_decls(decls):
        got = ida.local_type(d.name)
        if d.kind == "opaque":
            ok = got is not None
        else:
            ok = got is not None and not got.get("forward") and same_layout(got["size"], got["members"], d)
        _result(log, "types", d.name, "ok" if ok else "mismatch")
    for r in manifest["labels"]:
        ok = not ida.has_user_name(int(r["pc_va"], 16))
        _result(log, "remove-label", r["pc_va"], "ok" if ok else "mismatch", db=None if ok else ida.get_name(
            int(r["pc_va"], 16)))
    for r in manifest["names"]:
        got = ida.get_name(int(r["pc_va"], 16))
        _result(log, "names", r["pc_va"], "ok" if got == r["name"] else "mismatch",
                **({} if got == r["name"] else {"db": got, "row": r["name"]}))
    typed = []
    special = special_names(decls, manifest)
    for r in manifest["prototypes"]:
        ea = int(r["pc_va"], 16)
        got = ida.get_type(ea)
        ok = ida.is_userti(ea) and has_prototype(ida, ea, r["decl"], special)
        if ok:
            typed.append(r["pc_va"])
        _result(log, "prototypes", r["pc_va"], "ok" if ok else "mismatch", **({} if ok else {"db": got,
                                                                                          "row": r["decl"]}))
    for r in manifest["comments"]:
        got = ida.get_func_cmt(int(r["pc_va"], 16)) or ""
        ok = merged_comment(got, r["comment"]) is None
        _result(log, "comments", r["pc_va"], "ok" if ok else "mismatch", **({} if ok else {"db": got}))
    applied_locals = {r["key"] for r in apply_records if r.get("kind") == "result" and r["step"] == "locals"
                      and r["status"] in ("set", "already")}
    for r in manifest["locals"]:
        if local_key(r) not in applied_locals:
            continue
        g = ida.find_lvar(int(r["pc_va"], 16), int(r["pc_frame"]), _pc_def(r)).get("matches") or []
        ok = len(g) == 1 and g[0]["name"] == r["name"] and (
            r["retype"] == "-" or norm_type(g[0]["type"] or "") == norm_type(r["retype"]))
        _result(log, "locals", local_key(r), "ok" if ok else "mismatch", **({} if ok else {"db": g}))
    after = ida.counts()
    delta = expected_deltas(apply_records)
    before = head["counts_before"]
    expected = {k: before[k] + delta[k] for k in delta}
    counts = {"before": before, "applied_delta": delta, "expected": expected, "after": after,
              "ok": all(after[k] == expected[k] for k in expected)}
    log.write({"kind": "counts", **counts})
    for key in typed:
        err = ida.decompile(int(key, 16))
        _result(log, "decompile", key, "ok" if err is None else "failed", **({} if err is None else {"error": err}))
    summary = {"kind": "summary", "mode": "verify", "steps": summarize(log.results), "counts_ok": counts["ok"]}
    log.write(summary)
    return summary


# --- undo -----------------------------------------------------------------------------------------

def run_undo(ida, manifest: dict, apply_records: list[dict], log: Log) -> dict:
    head = next((r for r in apply_records if r.get("kind") == "header"), None)
    if head is None or head.get("mode") != "apply":
        raise ValueError("--undo needs an apply log")
    pre = precheck(ida)
    if head["input_sha256"] != pre["input_sha256"]:
        raise ValueError("apply log is for another database")
    log.write(header(ida, manifest, "undo"))
    for u in reversed([r for r in apply_records if r.get("kind") == "undo"]):
        step, key, before = u["step"], u["key"], u["before"]
        if step == "types":
            if before is None:
                ok = ida.delete_local_type(key)
                ok = ok and ida.local_type(key) is None
            else:
                ok = ida.restore_local_type(key, before)
                got = ida.local_type(key)
                ok = ok and got is not None and _same_type_state(got, before)
        elif step in ("names", "remove-label"):
            ea = int(key, 16)
            ok = ida.set_name(ea, before["name"] if before["user"] else "")
            ok = ok and (ida.get_name(ea) == before["name"] if before["user"] else not ida.has_user_name(ea))
        elif step == "prototypes":
            ea = int(key, 16)
            ok = ida.restore_type(ea, before["blob"] if before["user"] else None)
            ok = ok and norm(ida.get_type(ea)) == norm(before["type"]) and ida.is_userti(ea) == before["user"]
        elif step == "comments":
            ea = int(key, 16)
            ok = ida.set_func_cmt(ea, before["comment"]) and (ida.get_func_cmt(ea) or "") == before["comment"]
        elif step == "locals":
            ok = ida.unset_lvar(int(key.split("@")[0], 16), before)
        else:
            raise ValueError(f"unknown undo step {step!r}")
        _result(log, step, key, "restored" if ok else "failed")
    summary = {"kind": "summary", "mode": "undo", "steps": summarize(log.results), "counts_after": ida.counts()}
    log.write(summary)
    return summary


def _same_type_state(got: dict, before: dict) -> bool:
    if before.get("forward") or got.get("forward"):
        return bool(before.get("forward")) == bool(got.get("forward"))
    return layout_key(got["size"], got["members"]) == layout_key(before["size"], before["members"])


# --- entry ----------------------------------------------------------------------------------------

def parse_batch_args(argv) -> dict:
    """``idc.ARGV`` (``argv[0]`` is the script) to :func:`main` keyword arguments."""
    import argparse

    ap = argparse.ArgumentParser(prog="apply_transfer.py", exit_on_error=False)
    ap.add_argument("manifest_dir")
    ap.add_argument("out")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true")
    g.add_argument("--verify", action="store_true")
    g.add_argument("--undo", metavar="APPLY_LOG")
    ap.add_argument("--apply-log")
    ap.add_argument("--limit-types", type=int, help="wave 2 smoke test: the first N partial types")
    ap.add_argument("--limit-locals", type=int, help="wave 2 smoke test: the first N locals")
    ns = ap.parse_args(list(argv[1:]))
    if ns.verify and not ns.apply_log:
        raise ValueError("--verify needs --apply-log <apply jsonl>")
    if ns.apply_log and not ns.verify:
        raise ValueError("--apply-log goes with --verify")
    mode = "apply" if ns.apply else "verify" if ns.verify else "undo" if ns.undo else "dry-run"
    return {"manifest_dir": ns.manifest_dir, "out_path": ns.out, "mode": mode,
            "apply_log": ns.apply_log or ns.undo, "limit_types": ns.limit_types, "limit_locals": ns.limit_locals}


def main(manifest_dir: str, out_path: str, mode: str = "dry-run", apply_log: str | None = None, ida=None,
         limit_types: int | None = None, limit_locals: int | None = None) -> dict:
    manifest = load_manifest(manifest_dir)
    if limit_types is not None or limit_locals is not None:
        decls, loc = select(manifest, parse_types_h(manifest["types_h"]), limit_types, limit_locals)
        manifest = {**manifest, "types_h": render_decls(decls), "locals": loc,
                    "filter": {"types": limit_types, "locals": limit_locals}}
    ida = ida if ida is not None else _Ida()
    precheck(ida)
    records = read_log(apply_log) if apply_log else None
    tmp = f"{out_path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        log = Log(fh)
        if mode in ("dry-run", "apply"):
            summary = run_apply(ida, manifest, mode == "apply", log)
        elif mode == "verify":
            summary = run_verify(ida, manifest, records, log)
        elif mode == "undo":
            summary = run_undo(ida, manifest, records, log)
        else:
            raise ValueError(f"unknown mode {mode!r}")
    os.replace(tmp, out_path)
    return summary


def saves(mode: str) -> bool:
    """Only ``--apply`` and ``--undo`` keep their changes; dry run and verify discard the session."""
    return mode in ("apply", "undo")


def batch(argv, run=None, kill=None, qexit=None, wait=None) -> int:
    """Headless entry: parse ``argv``, run, print the summary line, exit IDA with the right save state.

    The hooks default to IDA (``ida_auto.auto_wait``, ``DBFL_KILL``, ``idc.qexit``); tests pass fakes.
    """
    import traceback

    code = 1
    mode = None
    try:
        kw = parse_batch_args(argv)
        mode = kw["mode"]
        if wait is not None:
            wait()
        summary = (run or main)(**kw)
        print(SUMMARY_PREFIX + json.dumps({k: v for k, v in summary.items() if k != "kind"}, sort_keys=True),
              flush=True)
        code = 0
    except BaseException:  # noqa: BLE001 - any failure must still end the batch process
        traceback.print_exc()
        print(SUMMARY_PREFIX + json.dumps({"error": True, "saved": False}), flush=True)
    if (code != 0 or not saves(mode)) and kill is not None:
        kill()
    if qexit is not None:
        qexit(code)
    return code


# --- IDA side (not unit-tested: needs IDA; T007b runs it) ------------------------------------------

class _Ida:
    def __init__(self):
        import importlib

        import ida_idaapi
        import ida_typeinf

        self.m = {n: importlib.import_module(n) for n in (
            "ida_bytes", "ida_funcs", "ida_hexrays", "ida_loader", "ida_nalt", "ida_name", "idautils", "idc")}
        self.ti = ida_typeinf
        self.til = ida_typeinf.get_idati()
        self.BADADDR = ida_idaapi.BADADDR

    # database identity
    def input_sha256(self):
        sha = self.m["ida_nalt"].retrieve_input_file_sha256()
        return sha.hex() if sha else None

    def idb_path(self):
        ld = self.m["ida_loader"]
        return ld.get_path(ld.PATH_TYPE_IDB)

    def counts(self) -> dict:
        idautils, nalt = self.m["idautils"], self.m["ida_nalt"]
        return {"names": sum(1 for _ in idautils.Names()),
                "typed_functions": sum(1 for f in idautils.Functions() if nalt.is_userti(f)),
                "local_types": self.ti.get_ordinal_count(self.til)}

    # names
    def get_name(self, ea):
        return self.m["ida_name"].get_name(ea)

    def has_user_name(self, ea):
        b = self.m["ida_bytes"]
        return bool(b.has_user_name(b.get_flags(ea)))

    def name_ea(self, name):
        ea = self.m["ida_name"].get_name_ea(self.BADADDR, name)
        return None if ea == self.BADADDR else ea

    def set_name(self, ea, name):
        n = self.m["ida_name"]
        return bool(n.set_name(ea, name, n.SN_NOWARN | n.SN_NOCHECK))

    def func_start(self, ea):
        f = self.m["ida_funcs"].get_func(ea)
        return None if f is None else f.start_ea

    # prototypes
    def get_type(self, ea):
        return self.m["idc"].get_type(ea)

    def is_userti(self, ea):
        return bool(self.m["ida_nalt"].is_userti(ea))

    def func_tinfo(self, ea):
        tif = self.ti.tinfo_t()
        return tif if self.m["ida_nalt"].get_tinfo(tif, ea) and tif.is_func() else None

    def func_parts(self, tif):
        """Calling convention, return type and ``(type, name)`` per argument of a function ``tinfo_t``."""
        ftd = self.ti.func_type_data_t()
        if tif is None or not tif.is_func() or not tif.get_func_details(ftd):
            return None
        return {"cc": ftd.get_cc(), "ret": ftd.rettype, "args": [(a.type, a.name) for a in ftd]}

    def type_equal(self, a, b):
        # tinfo_t.compare_with(r, tcflags) and TCMP_EQUAL "are types equal?" (IDA 9.5 python/ida_typeinf.py)
        return bool(a.compare_with(b, self.ti.TCMP_EQUAL))

    def type_blob(self, ea):
        tif = self.ti.tinfo_t()
        if not self.m["ida_nalt"].get_tinfo(tif, ea):
            return None
        t, f, c = tif.serialize()
        return [(x or b"").hex() for x in (t, f, c)]

    def _ref(self, name, depth):
        t = self.ti.tinfo_t()
        t.create_typedef(self.til, name, self.ti.BTF_STRUCT, True)
        for _ in range(depth):
            p = self.ti.tinfo_t()
            p.create_ptr(t)
            t = p
        return t

    def parse_prototype(self, plan):
        tif = self.ti.tinfo_t()
        if self.ti.parse_decl(tif, self.til, plan["parse"], self.ti.PT_SIL) is None or not tif.is_func():
            return None, f"parse_decl refused {plan['parse']!r}"
        if not plan["patch"]:
            return tif, None
        for _idx, name, _d in plan["patch"]:
            if self.ti.get_named_type(self.til, name, self.ti.NTF_TYPE) is None:
                return None, f"no local type {name!r}"
        ftd = self.ti.func_type_data_t()
        if not tif.get_func_details(ftd):
            return None, "get_func_details failed"
        for idx, name, depth in plan["patch"]:
            if idx == -1:
                ftd.rettype = self._ref(name, depth)
            else:
                ftd[idx].type = self._ref(name, depth)
        out = self.ti.tinfo_t()
        if not out.create_func(ftd):
            return None, "create_func failed"
        return out, None

    def apply_prototype(self, ea, tif):
        return bool(self.ti.apply_tinfo(ea, tif, self.ti.TINFO_DEFINITE))

    def restore_type(self, ea, blob):
        if blob is None:
            self.m["ida_nalt"].del_tinfo(ea)
            return True
        tif = self.ti.tinfo_t()
        if not tif.deserialize(self.til, *(bytes.fromhex(x) for x in blob)):
            return False
        return bool(self.ti.apply_tinfo(ea, tif, self.ti.TINFO_DEFINITE))

    # comments
    def get_func_cmt(self, ea):
        return self.m["idc"].get_func_cmt(ea, 0)

    def set_func_cmt(self, ea, text):
        return bool(self.m["idc"].set_func_cmt(ea, text, 0))

    # local types
    def local_type(self, name):
        tif = self.ti.tinfo_t()
        if not tif.get_named_type(self.til, name, self.ti.BTF_STRUCT, True, False):
            return None
        t, f, c = tif.serialize()
        blob = [(x or b"").hex() for x in (t, f, c)]
        if tif.is_forward_decl() or not tif.is_udt():
            return {"forward": True, "blob": blob}
        udt = self.ti.udt_type_data_t()
        tif.get_udt_details(udt)
        # type: the name of a named type (bases compare by it), else the printed type (pointers, arrays: T008 F2)
        members = [(u.name, u.offset // 8, u.size // 8,
                    "vptr" if u.is_vftable() else "base" if u.is_baseclass() else "",
                    u.type.get_type_name() or u.type.dstr())
                   for u in udt]
        return {"forward": False, "size": tif.get_size(), "members": members, "blob": blob}

    def declare_forward(self, name):
        tif = self.ti.tinfo_t()
        code = tif.create_forward_decl(self.til, self.ti.BTF_STRUCT, name)
        return None if code == self.ti.TERR_OK else f"create_forward_decl: {self.ti.tinfo_errstr(code)}"

    def _member_type(self, m: Member):
        if self.ti.get_named_type(self.til, m.type, self.ti.NTF_TYPE) is not None:
            t = self._ref(m.type, m.ptr)
        else:
            t = self.ti.tinfo_t()
            decl = f"{m.type} {'*' * m.ptr}__t007_m;"
            if self.ti.parse_decl(t, self.til, decl, self.ti.PT_SIL) is None:
                raise ValueError(f"member type {decl!r} not parsed")
        if m.count is not None:
            a = self.ti.tinfo_t()
            a.create_array(t, m.count)
            t = a
        return t

    def define_struct(self, d: TypeDecl):
        try:
            udt = self.ti.udt_type_data_t()
            for m in d.members:
                u = self.ti.udm_t()
                u.name = m.name
                u.type = self._member_type(m)
                u.offset = m.offset * 8
                u.size = m.size * 8
                if m.base:
                    u.set_baseclass(True)
                if m.vptr:
                    u.set_vftable(True)
                udt.push_back(u)
            udt.total_size = d.size
            udt.pack = 1
            udt.set_fixed(True)
            tif = self.ti.tinfo_t()
            if not tif.create_udt(udt, self.ti.BTF_STRUCT):
                return "create_udt failed"
            code = tif.set_named_type(self.til, d.name, self.ti.NTF_REPLACE)
            return None if code == self.ti.TERR_OK else f"set_named_type: {self.ti.tinfo_errstr(code)}"
        except Exception as e:  # noqa: BLE001 - reported as the row's failure, the run goes on
            return f"{type(e).__name__}: {e}"

    def delete_local_type(self, name):
        return bool(self.ti.del_named_type(self.til, name, self.ti.NTF_TYPE))

    def restore_local_type(self, name, before):
        tif = self.ti.tinfo_t()
        if not tif.deserialize(self.til, *(bytes.fromhex(x) for x in before["blob"])):
            return False
        return tif.set_named_type(self.til, name, self.ti.NTF_REPLACE) == self.ti.TERR_OK

    def set_type_comment(self, name, cmt):
        """The type comment of a local type (T013c partial types); an error text or None."""
        try:
            tif = self.ti.tinfo_t()
            if not tif.get_named_type(self.til, name, self.ti.BTF_STRUCT, True, False):
                return "type not found"
            code = tif.set_type_cmt(cmt)
            return None if code in (None, True, self.ti.TERR_OK) else f"set_type_cmt: {code}"
        except Exception as e:  # noqa: BLE001 - reported, the type itself is defined
            return f"{type(e).__name__}: {e}"

    # locals (T013c)
    def _cfunc(self, ea, fresh=False):
        hr = self.m["ida_hexrays"]
        if not hr.init_hexrays_plugin():
            raise RuntimeError("hexrays not available")
        if fresh:
            hr.mark_cfunc_dirty(ea, False)
        return hr.decompile(ea)

    def _lea_off(self, ea, pfn):
        """IDA frame offset addressed by the stack operand of the instruction at ``ea`` (the defining lea)."""
        import ida_frame
        import ida_ua

        insn = ida_ua.insn_t()
        if not ida_ua.decode_insn(insn, ea):
            return None
        for n in range(len(insn.ops)):
            op = insn.ops[n]
            if op.type == ida_ua.o_void:
                break
            if op.type in (ida_ua.o_displ, ida_ua.o_phrase):
                off = ida_frame.calc_stkvar_struc_offset(pfn, insn, n)
                if off != self.BADADDR:
                    return off
        return None

    def find_lvar(self, ea, frame, def_ea):
        """Stack lvars of ``ea``'s decompilation at the entry-relative ``frame`` (return address at 0), as
        dicts; ``ida_off`` the IDA frame offset (``frame_off_retaddr + frame``), ``lea_off`` the defining lea's."""
        import ida_frame

        try:
            pfn = self.m["ida_funcs"].get_func(ea)
            if pfn is None or pfn.start_ea != ea:
                return {"error": "not a function start"}
            cf = self._cfunc(ea, fresh=True)
            if cf is None:
                return {"error": "decompile returned None"}
            ida_off = ida_frame.frame_off_retaddr(pfn) + frame
            lea_off = self._lea_off(def_ea, pfn) if def_ea is not None else None
            mba = cf.mba
            out = []
            for lv in cf.get_lvars():
                if not lv.is_stk_var():
                    continue
                off = mba.stkoff_vd2ida(lv.location.stkoff())
                if off != ida_off:
                    continue
                out.append({"name": lv.name, "type": str(lv.type()), "width": lv.width, "is_arg": bool(lv.is_arg_var),
                            "user_name": bool(lv.has_user_name), "user_type": bool(lv.has_user_type),
                            "stkoff": lv.location.stkoff(), "defea": lv.defea, "ida_off": off})
            return {"ida_off": ida_off, "lea_off": lea_off, "matches": out}
        except Exception as e:  # noqa: BLE001 - a decompilation failure refuses the row
            return {"error": f"{type(e).__name__}: {e}"}

    def _locator(self, m):
        hr = self.m["ida_hexrays"]
        loc = hr.vdloc_t()
        loc.set_stkoff(m["stkoff"])
        return hr.lvar_locator_t(loc, m["defea"])

    def set_lvar(self, ea, m, name, type_name):
        """``modify_user_lvar_info`` by locator (stack offset + defea): MLI_NAME, plus MLI_TYPE for a retype."""
        hr = self.m["ida_hexrays"]
        try:
            info = hr.lvar_saved_info_t()
            info.ll = self._locator(m)
            info.name = name
            flags = hr.MLI_NAME
            if type_name is not None:
                tif = self.ti.tinfo_t()
                if not tif.get_named_type(self.til, type_name, self.ti.BTF_STRUCT, True, False):
                    return f"no local type {type_name!r}"
                info.type = tif
                flags |= hr.MLI_TYPE
            if not hr.modify_user_lvar_info(ea, flags, info):
                return "modify_user_lvar_info failed"
            return None
        except Exception as e:  # noqa: BLE001 - reported as the row's failure
            return f"{type(e).__name__}: {e}"

    def unset_lvar(self, ea, before):
        """Undo: drop the saved user settings of the lvar at ``before``'s locator (the gate allowed no user name
        before), then check it is back to its old name."""
        hr = self.m["ida_hexrays"]
        lvs = hr.lvar_uservec_t()
        if not hr.restore_user_lvar_settings(lvs, ea):
            return False
        keep = hr.lvar_uservec_t()
        hit = False
        for x in lvs.lvvec:
            if x.ll.location.is_stkoff() and x.ll.location.stkoff() == before["stkoff"] \
                    and x.ll.defea == before["defea"]:
                hit = True
                continue
            keep.lvvec.push_back(x)
        if not hit:
            return False
        keep.lmaps = lvs.lmaps
        keep.stkoff_delta = lvs.stkoff_delta
        keep.ulv_flags = lvs.ulv_flags
        hr.save_user_lvar_settings(ea, keep)
        cf = self._cfunc(ea, fresh=True)
        return cf is not None and any(lv.is_stk_var() and lv.location.stkoff() == before["stkoff"]
                                      and lv.name == before["name"] for lv in cf.get_lvars())

    # verify
    def decompile(self, ea):
        hr = self.m["ida_hexrays"]
        if not hr.init_hexrays_plugin():
            return "hexrays not available"
        try:
            cf = hr.decompile(ea)
        except hr.DecompilationFailure as e:
            return str(e)
        return None if cf is not None else "decompile returned None"


def _ida_batch_hooks():
    import ida_auto
    import ida_loader
    import idc

    return {"wait": ida_auto.auto_wait, "qexit": idc.qexit,
            "kill": lambda: ida_loader.set_database_flag(ida_loader.DBFL_KILL)}


if __name__ == "__main__":
    try:
        import idc as _idc
    except ImportError:
        _idc = None
    if _idc is not None and len(_idc.ARGV) >= 2:
        batch(list(_idc.ARGV), **_ida_batch_hooks())
