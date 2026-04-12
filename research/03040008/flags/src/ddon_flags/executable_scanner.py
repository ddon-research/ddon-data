from __future__ import annotations

import re
import subprocess
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LINE_RE = re.compile(r"^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F ]+\s+([a-z][a-z0-9]+)\s+(.*)$")


@dataclass(frozen=True)
class ImmediateHit:
    address: str
    mnemonic: str
    operands: str


def extract_immediate_value(mnemonic: str, operands: str) -> int | None:
    operands = operands.strip()
    if mnemonic == "push":
        match = re.fullmatch(r"0x([0-9a-fA-F]+)", operands)
        if match:
            return int(match.group(1), 16)
        return None
    if "," not in operands:
        return None
    last_operand = operands.rsplit(",", 1)[1].strip()
    match = re.fullmatch(r"0x([0-9a-fA-F]+)", last_operand)
    if match:
        return int(match.group(1), 16)
    return None


def collect_immediate_hits(exe_path: Path, objdump_path: Path, target_values: set[int]) -> dict[int, list[ImmediateHit]]:
    hits_by_value: dict[int, list[ImmediateHit]] = {value: [] for value in sorted(target_values)}
    process = subprocess.Popen(
        [str(objdump_path), "-d", "-Mintel", str(exe_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    for raw_line in process.stdout:
        match = LINE_RE.match(raw_line)
        if not match:
            continue
        address, mnemonic, operands = match.groups()
        value = extract_immediate_value(mnemonic, operands)
        if value not in target_values:
            continue
        hits_by_value[value].append(ImmediateHit(address=address.lower(), mnemonic=mnemonic, operands=operands.strip()))
    stderr = process.stderr.read() if process.stderr is not None else ""
    rc = process.wait()
    if rc != 0:
        raise RuntimeError(f"objdump failed with exit code {rc}: {stderr[:1000]}")
    return hits_by_value


def update_pending_contexts(pending_after: dict[str, int], contexts: dict[str, list[str]], line: str) -> None:
    for active_address in tuple(pending_after):
        contexts[active_address].append(line)
        pending_after[active_address] -= 1
        if pending_after[active_address] == 0:
            del pending_after[active_address]


def update_pending_following_calls(pending_after: dict[str, int], first_calls: dict[str, str], mnemonic: str, operands: str) -> None:
    for active_address in tuple(pending_after):
        if mnemonic == "call" and active_address not in first_calls:
            first_calls[active_address] = operands.strip()
            del pending_after[active_address]
            continue
        pending_after[active_address] -= 1
        if pending_after[active_address] == 0:
            del pending_after[active_address]


def collect_contexts_and_following_calls(exe_path: Path, objdump_path: Path, addresses: set[str], context_padding: int = 6, call_lookahead: int = 6) -> tuple[dict[str, list[str]], dict[str, str]]:
    contexts: dict[str, list[str]] = {address: [] for address in addresses}
    first_calls: dict[str, str] = {}
    previous_lines: deque[str] = deque(maxlen=context_padding)
    pending_contexts: dict[str, int] = {}
    pending_calls: dict[str, int] = {}
    process = subprocess.Popen(
        [str(objdump_path), "-d", "-Mintel", str(exe_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\n")
        match = LINE_RE.match(line)
        if not match:
            continue
        update_pending_contexts(pending_contexts, contexts, line)
        _, mnemonic, operands = match.groups()
        update_pending_following_calls(pending_calls, first_calls, mnemonic, operands)
        current_address = match.group(1).lower()
        if current_address in addresses:
            contexts[current_address] = list(previous_lines)
            contexts[current_address].append(line)
            pending_contexts[current_address] = context_padding
            if current_address not in first_calls:
                pending_calls[current_address] = call_lookahead
        previous_lines.append(line)
    stderr = process.stderr.read() if process.stderr is not None else ""
    rc = process.wait()
    if rc != 0:
        raise RuntimeError(f"objdump failed with exit code {rc}: {stderr[:1000]}")
    return contexts, first_calls


def format_following_call_clusters(hits: list[ImmediateHit], following_calls: dict[str, str]) -> str | None:
    call_counts: Counter[str] = Counter(
        following_calls[hit.address]
        for hit in hits
        if hit.address in following_calls
    )
    if not call_counts:
        return None
    parts = [f"{target} x{count}" for target, count in call_counts.most_common(3)]
    return ", ".join(parts)


def serialize_immediate_result(flag_value: int, hits: list[ImmediateHit], contexts_by_address: dict[str, list[str]], following_calls: dict[str, str], max_samples: int = 6) -> dict[str, Any]:
    references = []
    for hit in hits[:max_samples]:
        references.append(
            {
                "address": hit.address,
                "mnemonic": hit.mnemonic,
                "operands": hit.operands,
                "context": contexts_by_address.get(hit.address, []),
                "following_call": following_calls.get(hit.address, ""),
            }
        )
    call_summary = format_following_call_clusters(hits, following_calls)
    return {
        "flag_value": flag_value,
        "hit_count": len(hits),
        "score": 20 + min(len(hits), 10),
        "dominant_following_calls": call_summary or "",
        "references": references,
    }
