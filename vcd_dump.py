#!/usr/bin/env python3
"""
1:1 dump of a Value Change Dump: every timestamp block and each variable
update exactly as encoded in the file (no resampling, no guessing).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("tb_sex.vcd")
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    timescale_line = "1 fs"
    scope: list[str] = []
    # id -> (hierarchical_name, width); width 1 = scalar
    vars_: dict[str, tuple[str, int]] = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if line.startswith("$timescale"):
            i += 1
            parts: list[str] = []
            while i < len(lines) and lines[i].strip() != "$end":
                parts.append(lines[i].strip())
                i += 1
            if parts:
                timescale_line = parts[0]
            i += 1
            continue
        if line.startswith("$scope"):
            m = re.match(r"\$scope\s+module\s+(\S+)\s+\$end", line)
            if m:
                scope.append(m.group(1))
            i += 1
            continue
        if line.startswith("$upscope"):
            if scope:
                scope.pop()
            i += 1
            continue
        if line.startswith("$var"):
            m = re.match(
                r"\$var\s+\S+\s+(\d+)\s+(\S+)\s+(.+?)\s+\$end", line
            )
            if m:
                width = int(m.group(1))
                vid = m.group(2)
                leaf = m.group(3).strip()
                hier = ".".join(scope + [leaf]) if scope else leaf
                vars_[vid] = (hier, width)
            i += 1
            continue
        if line.startswith("$enddefinitions"):
            i += 1
            break
        i += 1

    # Parse body: #time then one or more value lines until next # or EOF
    events: list[tuple[int, list[tuple[str, str]]]] = []
    current_t: int | None = None
    current_block: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal current_t, current_block
        if current_t is not None:
            events.append((current_t, list(current_block)))
        current_block = []

    re_time = re.compile(r"^#(\d+)$")
    # binary vector: b<bits><space><id>
    re_vec = re.compile(r"^b([01xXzZuU]+)\s+(\S+)\s*$")
    # scalar: one char value + id (id is rest of line after first char)
    re_sca = re.compile(r"^([01xXzZuU])(\S+)\s*$")

    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("$"):
            continue
        mt = re_time.match(line)
        if mt:
            flush()
            current_t = int(mt.group(1))
            continue
        if current_t is None:
            continue
        mv = re_vec.match(line)
        if mv:
            bits, vid = mv.group(1), mv.group(2)
            current_block.append((vid, f"b{bits}"))
            continue
        ms = re_sca.match(line)
        if ms:
            val, vid = ms.group(1), ms.group(2)
            current_block.append((vid, val))
            continue
        # ignore unknown token lines

    # Emit final timestamp even when it has no value lines (matches EOF in file)
    flush()

    out_lines: list[str] = []
    out_lines.append(f"file: {path.resolve()}")
    out_lines.append(f"timescale: {timescale_line}")
    out_lines.append("id map (as in $var):")
    for vid in sorted(vars_.keys(), key=lambda x: (len(x), x)):
        name, w = vars_[vid]
        out_lines.append(f"  {vid!r} -> {name}  width={w}")
    out_lines.append("")
    out_lines.append("events (time in dump units, then each change in file order):")

    for t, changes in events:
        out_lines.append(f"#{t}")
        if not changes:
            out_lines.append("  (no value lines in VCD before next # or EOF)")
        else:
            for vid, val in changes:
                name_w = vars_.get(vid)
                if name_w:
                    name, _w = name_w
                    out_lines.append(f"  {vid!r} {name} = {val}")
                else:
                    out_lines.append(f"  {vid!r} <unknown id> = {val}")

    print("\n".join(out_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
