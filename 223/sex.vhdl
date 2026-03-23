library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
-- Control FSM + one digit in base 223 (0 .. 222).
-- inc_i must be high for exactly one clk_i cycle (single-cycle pulse).
entity base223_fsm is
  port (
    clk_i   : in  std_logic;
    rst_i   : in  std_logic;
    clr_i   : in  std_logic;              -- synchronous clear -> digit 0, state CLEAR
    run_i   : in  std_logic;              -- 0 = paused, 1 = may count
    inc_i   : in  std_logic;              -- pulse: +1 mod 223
    digit_o : out unsigned(7 downto 0);  -- current value 0 .. 222
    wrap_o  : out std_logic               -- 1 for one cycle when 222 -> 0
  );
end entity base223_fsm;
architecture rtl of base223_fsm is
  type state_t is (ST_CLEAR, ST_RUN, ST_PAUSE);
  signal state_r, state_x : state_t;
  signal digit_r, digit_x : unsigned(7 downto 0);
  signal wrap_x, wrap_r   : std_logic;
begin
  comb : process (all) is
  begin
    state_x <= state_r;
    digit_x <= digit_r;
    wrap_x  <= '0';
    case state_r is
      when ST_CLEAR =>
        digit_x <= (others => '0');
        if run_i = '1' then
          state_x <= ST_RUN;
        else
          state_x <= ST_PAUSE;
        end if;
      when ST_PAUSE =>
        if clr_i = '1' then
          state_x <= ST_CLEAR;
        elsif run_i = '1' then
          state_x <= ST_RUN;
        end if;
      when ST_RUN =>
        if clr_i = '1' then
          state_x <= ST_CLEAR;
        elsif run_i = '0' then
          state_x <= ST_PAUSE;
        elsif inc_i = '1' then
          if digit_r = to_unsigned(222, digit_r'length) then
            digit_x <= (others => '0');
            wrap_x  <= '1';
          else
            digit_x <= digit_r + 1;
          end if;
        end if;
    end case;
  end process comb;
  seq : process (clk_i) is
  begin
    if rising_edge(clk_i) then
      if rst_i = '1' then
        state_r <= ST_CLEAR;
        digit_r <= (others => '0');
        wrap_r  <= '0';
      else
        state_r <= state_x;
        digit_r <= digit_x;
        wrap_r  <= wrap_x;
      end if;
    end if;
  end process seq;
  digit_o <= digit_r;
  wrap_o  <= wrap_r;
end architecture rtl;
