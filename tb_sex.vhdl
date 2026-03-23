-- Testbench: replay MMIO writes from `thecode` (RISC-V sb to 0x4000_0000)
-- Byte 2 -> pause (run_i = '0'); byte 4 -> clear (clr_i pulse for one cycle).
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity tb_sex is
end entity tb_sex;

architecture sim of tb_sex is
  constant ctrl_base : natural := 16#4000_0000#;

  signal clk     : std_logic := '0';
  signal rst     : std_logic := '1';
  signal clr_i   : std_logic := '0';
  signal run_i   : std_logic := '0';
  signal inc_i   : std_logic := '0';
  signal digit_o : unsigned(5 downto 0);
  signal wrap_o  : std_logic;

  constant clk_period : time := 10 ns;

  procedure mmio_sb (
    signal clock : in std_logic;
    signal run_s : out std_logic;
    signal clr_s : out std_logic;
    addr         : natural;
    byte         : natural) is
  begin
    wait until rising_edge(clock);
    case byte is
      when 1 =>
        run_s <= '1';
        clr_s <= '0';
      when 2 =>
        run_s <= '0';
        clr_s <= '0';
      when 4 =>
        clr_s <= '1';
    end case;
    wait until rising_edge(clock);
    clr_s <= '0';
  end procedure;

  -- Single-cycle inc_i pulse: high is sampled on one rising_edge(clk).
  procedure pulse_inc (signal clock : in std_logic; signal inc_s : out std_logic) is
  begin
    wait until rising_edge(clock);
    inc_s <= '1';
    wait until rising_edge(clock);
    inc_s <= '0';
    wait until rising_edge(clock);
  end procedure;

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
    inc_i <= '0';
    clr_i <= '0';
    run_i <= '0';
    rst   <= '1';
    wait for clk_period * 2;
    rst <= '0';
    wait for clk_period * 2;
    snapshot("after reset deassert");

    report "MMIO sb @0x40000000 byte 1 (run)" severity note;
    mmio_sb(clk, run_i, clr_i, ctrl_base, 1);
    snapshot("after run (sb 1)");

    for k in 1 to 3 loop
      report "inc_i pulse #" & integer'image(k) severity note;
      pulse_inc(clk, inc_i);
      snapshot("after inc pulse #" & integer'image(k));
    end loop;

    -- Mirrors thecode (thecode skips run + inc; stores only 2 then 4)
    -- li x10, 0x40000000  — implicit in mmio_sb addr
    report "MMIO sb @0x40000000 byte 2 (pause)" severity note;
    mmio_sb(clk, run_i, clr_i, ctrl_base, 2);
    snapshot("after pause (sb 2)");

    report "MMIO sb @0x40000000 byte 4 (clear pulse)" severity note;
    mmio_sb(clk, run_i, clr_i, ctrl_base, 4);
    -- Sample after DUT seq runs (avoid reading digit_o in same delta as clk edge)
    wait until rising_edge(clk);
    wait until falling_edge(clk);
    snapshot("after clear (sb 4)");

    wait for clk_period * 5;
    snapshot("before finish");
    std.env.finish;
  end process stim;

end architecture sim;
