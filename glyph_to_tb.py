#!/usr/bin/env python3
"""Expand glyph_script.txt (VCD-style shorthand) into tb_sex_glyph.vhdl stim."""
from __future__ import annotations

from pathlib import Path

STIM = {'"': "rst", "#": "clr_i", "$": "run_i", "%": "inc_i"}
def parse_line(tail: str) -> list[tuple[str, str]]:
    """Return list of (vhdl_signal, '0'|'1') from tail after '!'."""
    out: list[tuple[str, str]] = []
    i = 0
    n = len(tail)
    while i < n:
        c = tail[i]
        if c.isspace():
            i += 1
            continue
        if c == "b":
            j = i + 1
            while j < n and tail[j] in "01":
                j += 1
            while j < n and tail[j].isspace():
                j += 1
            if j < n:
                j += 1  # skip VCD id (vector — not tb stim)
            i = j
            continue
        if c in "01" and i + 1 < n:
            vid = tail[i + 1]
            if vid in STIM:
                out.append((STIM[vid], c))
            i += 2
            continue
        if c in STIM:
            out.append((STIM[c], "1"))
            i += 1
            continue
        if c == "C":
            i += 1
            continue
        i += 1
    return out


def write_glyphs_reference(
    root: Path,
    source_lines: list[str],
    steps: list[list[tuple[str, str]]],
) -> None:
    """Write human-readable glyph legend + per-step expansion."""
    inv = {v: k for k, v in STIM.items()}
    lines_out: list[str] = []
    lines_out.append("# SexCPU VCD glyphs (GHDL tb_sex dump codes)")
    lines_out.append("# Timescale in VCD: 1 fs; each script line starting with '!' = one rising_edge(clk).")
    lines_out.append("")
    lines_out.append("## Identifier map (from $var in tb_sex.vcd)")
    lines_out.append("id  hierarchical signal              tb drives?")
    lines_out.append("!   tb_sex.clk                        no — clock is concurrent; '!' marks a cycle step")
    lines_out.append('"   tb_sex.rst                         yes')
    lines_out.append("#   tb_sex.clr_i                       yes")
    lines_out.append("$   tb_sex.run_i                       yes")
    lines_out.append("%   tb_sex.inc_i                       yes")
    lines_out.append("&   tb_sex.digit_o[5:0]               no (DUT out)")
    lines_out.append("'   tb_sex.wrap_o                      no (DUT out)")
    lines_out.append("(   tb_sex.dut.clk_i                  no (alias of clk)")
    lines_out.append(")   tb_sex.dut.rst_i                  no")
    lines_out.append("*   tb_sex.dut.clr_i                  no")
    lines_out.append("+   tb_sex.dut.run_i                  no")
    lines_out.append(",   tb_sex.dut.inc_i                  no")
    lines_out.append("-   tb_sex.dut.digit_o[5:0]           no")
    lines_out.append(".   tb_sex.dut.wrap_o                 no")
    lines_out.append("/   tb_sex.dut.digit_r[5:0]           no")
    lines_out.append("0   tb_sex.dut.digit_x[5:0]           no (id is digit zero)")
    lines_out.append("1   tb_sex.dut.wrap_x                 no")
    lines_out.append("2   tb_sex.dut.wrap_r                 no")
    lines_out.append("")
    lines_out.append("## Shorthand rules (glyph_script.txt)")
    lines_out.append("- Lines starting with '\"' are header / initial dump — skipped by the generator.")
    lines_out.append("- '!' starts a cycle: apply tail tokens, then wait until rising_edge(clk).")
    lines_out.append("- 'C' in tail: no stim change this cycle (clock-only beat).")
    lines_out.append("- Bare # $ % \" : force that stim to '1'.")
    lines_out.append("- Pair 0x or 1x with x in {#,$,%,\"}: set that stim to 0 or 1.")
    lines_out.append("- 'b01010<id>' vector tokens are ignored for driving (DUT internal / bus dump).")
    lines_out.append("")
    lines_out.append("## glyph_script.txt → parsed deltas (before each clock edge)")
    si = 0
    for raw in source_lines:
        line = raw.strip()
        if not line or line.startswith('"') or not line.startswith("!"):
            continue
        if si >= len(steps):
            break
        d = steps[si]
        si += 1
        parts = [f"{s}<={v}" for s, v in d] if d else ["(hold)"]
        lines_out.append(f"step {si:2d}  {line!s}")
        lines_out.append(f"         → {', '.join(parts)}")
    lines_out.append("")
    (root / "glyphs.txt").write_text("\n".join(lines_out), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parent
    raw_lines = (root / "glyph_script.txt").read_text(encoding="utf-8").splitlines()
    steps: list[list[tuple[str, str]]] = []
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith('"'):
            continue
        if not line.startswith("!"):
            continue
        tail = line[1:].strip()
        steps.append(parse_line(tail))

    state = {"rst": "1", "clr_i": "0", "run_i": "0", "inc_i": "0"}
    vhdl_lines: list[str] = []
    vhdl_lines.append("    -- from glyph_script.txt (VCD-ish replay)")
    vhdl_lines.append("    rst   <= '1';")
    vhdl_lines.append("    clr_i <= '0';")
    vhdl_lines.append("    run_i <= '0';")
    vhdl_lines.append("    inc_i <= '0';")
    vhdl_lines.append("    wait for clk_period * 2;")
    vhdl_lines.append("    rst <= '0';")
    vhdl_lines.append("    wait for clk_period * 2;")
    vhdl_lines.append('    snapshot("glyph: after reset preamble");')
    state["rst"] = "0"  # match preamble; glyph tails never touch "

    for idx, deltas in enumerate(steps):
        vhdl_lines.append(f"    wait until rising_edge(clk); -- glyph step {idx + 1}")
        for sig, val in deltas:
            state[sig] = val
        vhdl_lines.append(f"    rst   <= '{state['rst']}';")
        vhdl_lines.append(f"    clr_i <= '{state['clr_i']}';")
        vhdl_lines.append(f"    run_i <= '{state['run_i']}';")
        vhdl_lines.append(f"    inc_i <= '{state['inc_i']}';")
        vhdl_lines.append(f'    snapshot("glyph step {idx + 1}");')
        vhdl_lines.append("    wait until rising_edge(clk);")

    vhdl_lines.append("    wait for clk_period * 2;")
    vhdl_lines.append('    snapshot("glyph: before finish");')
    vhdl_lines.append("    std.env.finish;")

    stim_body = "\n".join(vhdl_lines)

    tb = f'''-- Auto-generated from glyph_script.txt by glyph_to_tb.py — do not hand-edit stim.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity tb_sex_glyph is
end entity tb_sex_glyph;

architecture sim of tb_sex_glyph is
  signal clk     : std_logic := '0';
  signal rst     : std_logic := '1';
  signal clr_i   : std_logic := '0';
  signal run_i   : std_logic := '0';
  signal inc_i   : std_logic := '0';
  signal digit_o : unsigned(5 downto 0);
  signal wrap_o  : std_logic;

  constant clk_period : time := 10 ns;

  procedure snapshot (constant msg : in string) is
  begin
    report msg & " | digit_o=" & integer'image(to_integer(digit_o))
      & " wrap_o=" & std_logic'image(wrap_o)
      severity note;
  end procedure;

begin

  clk <= not clk after clk_period / 2;

  dut : entity work.base60_fsm
    port map (
      clk_i   => clk,
      rst_i   => rst,
      clr_i   => clr_i,
      run_i   => run_i,
      inc_i   => inc_i,
      digit_o => digit_o,
      wrap_o  => wrap_o);

  stim : process is
  begin
{stim_body}
  end process stim;

end architecture sim;
'''
    (root / "tb_sex_glyph.vhdl").write_text(tb, encoding="utf-8")
    write_glyphs_reference(root, raw_lines, steps)
    print("Wrote", root / "tb_sex_glyph.vhdl", f"({len(steps)} glyph steps)")
    print("Wrote", root / "glyphs.txt")


if __name__ == "__main__":
    main()
