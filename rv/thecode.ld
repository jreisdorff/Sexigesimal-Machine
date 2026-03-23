/* qemu-system-riscv64 -machine virt -bios none -kernel loads into DRAM at 0x8000_0000.
 * Do not set .text at 0x4000_0000 — QEMU will not run it there on `virt`.
 * ctrl_port is a RAM alias for the SoC MMIO at 0x4000_0000 (see thecode.S). */
ENTRY(_start)
SECTIONS
{
  . = 0x40000000;
  .text : { *(.text) }
  . = ALIGN(8);
  ctrl_port = .;
  . += 8;
}
