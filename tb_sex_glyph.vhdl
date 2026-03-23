-- Auto-generated from glyph_script.txt by glyph_to_tb.py — do not hand-edit stim.
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
    -- from glyph_script.txt (VCD-ish replay)
    rst   <= '1';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    wait for clk_period * 2;
    rst <= '0';
    wait for clk_period * 2;
    snapshot("glyph: after reset preamble");
    wait until rising_edge(clk); -- glyph step 1
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 1");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 2
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 2");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 3
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 3");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 4
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 4");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 5
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 5");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 6
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 6");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 7
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '1';
    snapshot("glyph step 7");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 8
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 8");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 9
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 9");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 10
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '1';
    snapshot("glyph step 10");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 11
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 11");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 12
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 12");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 13
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '1';
    snapshot("glyph step 13");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 14
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 14");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 15
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 15");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 16
    rst   <= '0';
    clr_i <= '0';
    run_i <= '1';
    inc_i <= '0';
    snapshot("glyph step 16");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 17
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 17");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 18
    rst   <= '0';
    clr_i <= '1';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 18");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 19
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 19");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 20
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 20");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 21
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 21");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 22
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 22");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 23
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 23");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 24
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 24");
    wait until rising_edge(clk);
    wait until rising_edge(clk); -- glyph step 25
    rst   <= '0';
    clr_i <= '0';
    run_i <= '0';
    inc_i <= '0';
    snapshot("glyph step 25");
    wait until rising_edge(clk);
    wait for clk_period * 2;
    snapshot("glyph: before finish");
    std.env.finish;
  end process stim;

end architecture sim;
