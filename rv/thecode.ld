/* qemu-system-riscv64 -machine virt -bios none -kernel loads into DRAM at 0x8000_0000.
 * A small scratch word after .text stands in for the SoC MMIO at 0x4000_0000 (see thecode.S). */
ENTRY(_start)
SECTIONS
{
  . = 0x40000000;
  .text : { *(.text) }
}
