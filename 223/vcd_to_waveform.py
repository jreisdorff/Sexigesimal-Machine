#!/usr/bin/env python3
"""Render a GHDL-exported tb_sex.vcd to a digital-style waveform PNG."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import gridspec


def fs_to_ns(t_fs: int) -> float:
    return t_fs / 1_000_000.0


def parse_vcd_defs(lines: list[str]) -> tuple[dict[str, tuple[str, int]], int]:
    """Return (id -> (hierarchical_name, width), line_index_after_enddefinitions)."""
    scopes: list[str] = []
    id_map: dict[str, tuple[str, int]] = {}
    i = 0
    var_re = re.compile(r"\$var\s+\S+\s+(\d+)\s+(\S+)\s+(.+?)\s+\$end")
    scope_re = re.compile(r"\$scope\s+module\s+(\S+)\s+\$end")
    while i < len(lines):
        raw = lines[i].strip()
        if raw.startswith("$scope"):
            m = scope_re.match(raw)
            if m:
                scopes.append(m.group(1))
            i += 1
            continue
        if raw.startswith("$upscope"):
            if scopes:
                scopes.pop()
            i += 1
            continue
        if raw.startswith("$var"):
            m = var_re.match(raw)
            if m:
                w = int(m.group(1))
                vid = m.group(2)
                leaf = m.group(3).strip()
                hier = ".".join(scopes + [leaf]) if scopes else leaf
                id_map[vid] = (hier, w)
            i += 1
            continue
        if raw.startswith("$enddefinitions"):
            return id_map, i + 1
        i += 1
    raise ValueError("no $enddefinitions in VCD")


def parse_vcd_events(lines: list[str], start: int) -> list[tuple[int, str, str]]:
    """List of (time_fs, id, value_str) in file order (value_str like '0','1' or '00001111')."""
    events: list[tuple[int, str, str]] = []
    cur_t = 0
    vec_re = re.compile(r"^b([01uUxXzZ]+)\s+(\S+)\s*$")
    i = start
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("$"):
            continue
        if line.startswith("#"):
            cur_t = int(line[1:])
            continue
        mv = vec_re.match(line)
        if mv:
            events.append((cur_t, mv.group(2), mv.group(1)))
            continue
        if line and line[0] in "01uUxXzZ":
            events.append((cur_t, line[1:], line[0]))
            continue
    return events


def vec_to_int(s: str) -> float:
    if any(c not in "01" for c in s):
        return float("nan")
    return float(int(s, 2))


def bit_val(s: str) -> float:
    if s not in "01":
        return float("nan")
    return float(s)


def build_step_xy(samples: list[tuple[int, float]], t_end_fs: int) -> tuple[list[float], list[float]]:
    """Piecewise-constant curve through (time_ns, value)."""
    if not samples:
        return [0.0, fs_to_ns(t_end_fs)], [0.0, 0.0]
    xs: list[float] = []
    ys: list[float] = []
    for j, (t_fs, v) in enumerate(samples):
        t_ns = fs_to_ns(t_fs)
        if j == 0 and t_fs > 0:
            xs.extend([0.0, t_ns])
            ys.extend([v, v])
        else:
            if not xs:
                xs.append(t_ns)
                ys.append(v)
            else:
                xs.append(t_ns)
                ys.append(ys[-1])
                xs.append(t_ns)
                ys.append(v)
    last_ns = fs_to_ns(t_end_fs)
    xs.extend([last_ns, last_ns])
    ys.extend([ys[-1], ys[-1]])
    return xs, ys


def main() -> int:
    ap = argparse.ArgumentParser(description="VCD → PNG waveform (tb_sex top-level signals).")
    ap.add_argument(
        "--vcd",
        type=Path,
        default=None,
        help="Input .vcd (default: tb_sex.vcd next to this script)",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PNG (default: tb_sex_waveform.png next to this script)",
    )
    ap.add_argument(
        "--run-ghdl",
        action="store_true",
        help="Run ghdl -r tb_sex --vcd=... before plotting (cwd = script dir)",
    )
    args = ap.parse_args()
    root = Path(__file__).resolve().parent
    vcd_path = args.vcd or (root / "tb_sex.vcd")
    out_path = args.output or (root / "tb_sex_waveform.png")

    if args.run_ghdl:
        subprocess.run(
            [
                "ghdl",
                "-r",
                "tb_sex",
                f"--vcd={vcd_path}",
                "--assert-level=none",
            ],
            cwd=root,
            check=True,
        )

    text = vcd_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    id_map, body_start = parse_vcd_defs(lines)
    events = parse_vcd_events(lines, body_start)

    # Map tb_sex.<leaf> -> id (exclude dut internals)
    tb_ids: dict[str, str] = {}
    for vid, (hier, _w) in id_map.items():
        parts = hier.split(".")
        if len(parts) == 2 and parts[0] == "tb_sex":
            tb_ids[parts[1]] = vid

    order = [
        ("clk", "clk", "bit"),
        ("rst", "rst", "bit"),
        ("clr_i", "clr_i", "bit"),
        ("run_i", "run_i", "bit"),
        ("inc_i", "inc_i", "bit"),
        ("digit_o[7:0]", "digit_o", "vec"),
        ("wrap_o", "wrap_o", "bit"),
    ]
    missing = [name for name, _, _ in order if name not in tb_ids]
    if missing:
        print("Missing tb_sex signals in VCD:", missing, file=sys.stderr)
        return 1

    # Replay events; keep a timeline when each tracked id changes value
    tracked = {tb_ids[name]: (label, kind) for name, label, kind in order}
    history: dict[str, list[tuple[int, float]]] = {vid: [] for vid in tracked}

    for t_fs, vid, val in events:
        if vid not in tracked:
            continue
        label, kind = tracked[vid]
        y = bit_val(val) if kind == "bit" else vec_to_int(val)
        hist = history[vid]
        if not hist:
            hist.append((t_fs, y))
        elif hist[-1][1] != y:
            hist.append((t_fs, y))

    last_t = max((t for t, _, _ in events), default=0)
    t_end = max(last_t + 5_000_000, 250_000_000)

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.facecolor": "#f8f8f8",
            "figure.facecolor": "white",
            "axes.grid": True,
            "grid.alpha": 0.35,
        }
    )
    fig = plt.figure(figsize=(12, 6.5), dpi=150)
    fig.suptitle("tb_sex (base-223 FSM) simulation waveforms", fontsize=12, fontweight="bold")
    gs = gridspec.GridSpec(len(order), 1, height_ratios=[1] * len(order), hspace=0.25)

    for row, (sig_name, label, kind) in enumerate(order):
        vid = tb_ids[sig_name]
        ax = fig.add_subplot(gs[row, 0])
        samples = history.get(vid, [])
        xs, ys = build_step_xy(samples, t_end)
        ax.plot(xs, ys, color="#1a5276", linewidth=1.2 if kind == "vec" else 1.6)
        ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=8)
        ax.yaxis.set_label_coords(-0.06, 0.5)
        if kind == "bit":
            ax.set_ylim(-0.15, 1.15)
            ax.set_yticks([0, 1])
        else:
            ys_finite = [y for _, y in samples if y == y]  # not NaN
            ymax = max(ys_finite) if ys_finite else 3
            ax.set_ylim(-0.5, max(ymax + 1, 3))
            hi = int(max(ymax, 3))
            ax.set_yticks(list(range(hi + 1)) if hi <= 16 else [0, hi // 2, hi])
        if row < len(order) - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("Time (ns)")

    fig.align_ylabels(fig.axes)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.93, bottom=0.08)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print("Wrote", out_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
