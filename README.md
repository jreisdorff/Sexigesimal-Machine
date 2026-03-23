# SexCPU

VHDL simulation of a **base-60 (sexagesimal) counter FSM** plus tooling to drive it from either a procedural testbench, a VCD-style glyph script, or to inspect wave dumps.

## In plain English

Imagine a **single digit on a digital clock** that only goes from **0 up to 59**, then rolls back to 0 (like seconds or minutes). This project builds that behavior as a **simulated chip** on your computer: it does not ship a physical circuit; **GHDL** runs a virtual copy so you can see the numbers change without soldering anything.

You control that digit with simple ideas anyone would recognize:

- **Run / pause:** counting only happens while it is “running.”
- **Tick:** each tick adds one (when it is running).
- **Clear:** snap the digit back to zero.
- **Reset:** power-on style restart of the whole block.

When the digit goes from **59 to 0**, the design can raise a short **“I just wrapped”** flag for one instant—useful if you later chain digits (tens of seconds, etc.).

The **testbenches** are automated scripts that press those abstract buttons in a fixed order and print what the digit read at each step. One testbench pretends a **tiny program wrote bytes to a special memory address** (how a real CPU might turn a peripheral on or off). Another path uses a **shorthand script** (`glyph_script.txt`) that gets turned into VHDL by a small Python program. A third helper **reads a waveform log** (`.vcd`) and writes it out as plain text so you can scroll the timeline without a scope UI.

## Hardware core (`sex.vhdl`)

The file `sex.vhdl` implements the entity **`base60_fsm`**:

- **Inputs:** clock, reset, synchronous clear (`clr_i`), run/pause (`run_i`), and a single-cycle increment pulse (`inc_i`).
- **Outputs:** `digit_o` in `0 .. 59` and `wrap_o` asserted for one cycle when the digit wraps `59 → 0`.
- **Behavior:** FSM states CLEAR / RUN / PAUSE; counting only advances when `run_i = '1'` and `inc_i` pulses high for exactly one clock cycle.

## Testbench: MMIO-style stimulus (`tb_sex.vhdl`)

`tb_sex` instantiates `base60_fsm` and drives it in a way that mirrors **byte stores to a control port at `0x4000_0000`**, as sketched in `thecode` (RISC-V-style `sb` sequences):

- Byte **1:** run (`run_i = '1'`, clear deasserted).
- Byte **2:** pause (`run_i = '0'`).
- Byte **4:** one-cycle clear pulse on `clr_i`.

The bench also emits three single-cycle `inc_i` pulses, then pause and clear, and prints **simulation notes** with `digit_o` and `wrap_o` at each checkpoint.

### Run with GHDL

```bash
ghdl -a --std=08 sex.vhdl
ghdl -a --std=08 tb_sex.vhdl
ghdl -e --std=08 tb_sex
ghdl -r --std=08 tb_sex
```

Optional Value Change Dump:

```bash
ghdl -r --std=08 tb_sex --vcd=tb_sex.vcd
```

## Glyph script → second testbench (`glyph_script.txt`, `glyph_to_tb.py`, `tb_sex_glyph.vhdl`)

`glyph_script.txt` is a **compact, VCD-inspired notation**: each line starting with `!` is one clock step; characters map to `rst`, `clr_i`, `run_i`, and `inc_i` (see the generator for full rules).

`glyph_to_tb.py` reads `glyph_script.txt` and:

1. Writes **`tb_sex_glyph.vhdl`** — a self-contained testbench (marked auto-generated) that replays those steps against `base60_fsm`.
2. Writes **`glyphs.txt`** — a human-readable legend and per-step expansion.

Regenerate and simulate:

```bash
python3 glyph_to_tb.py
ghdl -a --std=08 sex.vhdl
ghdl -a --std=08 tb_sex_glyph.vhdl
ghdl -e --std=08 tb_sex_glyph
ghdl -r --std=08 tb_sex_glyph
```

## VCD inspection (`vcd_dump.py`)

`vcd_dump.py` prints a **literal, ordered transcript** of a `.vcd` file: timescale, identifier map, and each timestamp block with value updates in file order (no resampling). If you pass no argument, it defaults to `tb_sex.vcd` next to the script.

```bash
python3 vcd_dump.py tb_sex.vcd
# or redirect:
python3 vcd_dump.py tb_sex.vcd > tb_sex_vcd_dump.txt
```

## Other files (reference / artifacts)

| Item | Role |
|------|------|
| `thecode` | Short assembly-style comment block tying MMIO bytes to `tb_sex` behavior. |
| `tb_sex.vcd`, `tb_sex_vcd_dump.txt` | Example waveform dump and text expansion from `vcd_dump.py`. |
| `tb_sex_waveform.png` | Exported waveform image (if present in your tree). |
| `work-obj08.cf`, `*.o`, `tb_sex`, `tb_sex_glyph` | GHDL library / elaboration outputs (rebuilt by the commands above). |

## Requirements

- **GHDL** with VHDL-2008 (`--std=08`).
- **Python 3** for `glyph_to_tb.py` and `vcd_dump.py` (stdlib only).
