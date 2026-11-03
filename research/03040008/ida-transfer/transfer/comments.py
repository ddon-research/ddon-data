"""Rule 4: one function comment per written function; an existing comment is kept and ours appended below a
separator line (idempotent: nothing when the existing comment already holds our text)."""

from __future__ import annotations

from dataclasses import dataclass

SEPARATOR = "----"


@dataclass(frozen=True)
class CommentRow:
    pc_va: int
    action: str  # set | append | equal
    comment: str
    existing: str


def text(pc_string_ea: int | None, ps4: tuple[str, str, str] | None, flags: str) -> str:
    """``ps4`` = (qualified name, mangled symbol, rule)."""
    parts = []
    if pc_string_ea is not None:
        parts.append(f"PC name from string at {pc_string_ea:#x}.")
    if ps4 is not None:
        q, sym, rule = ps4
        parts.append(f"PS4 02020005: {q}" + (f" ({sym})" if sym and sym != q else "") + f"; paired by {rule}.")
    if flags and flags != "-":
        parts.append(f"Season 3: {flags}.")
    return " ".join(parts)


def comment_row(pc_va: int, ours: str, existing: str | None) -> CommentRow:
    ex = existing or ""
    if not ex.strip():
        return CommentRow(pc_va, "set", ours, ex)
    if ours in ex:
        return CommentRow(pc_va, "equal", ex, ex)
    return CommentRow(pc_va, "append", f"{ex}\n{SEPARATOR}\n{ours}", ex)
