/* Same sequence as repo `thecode` (pause byte 2, clear byte 4), but the port address:
 * on silicon: li + 0x4000_0000; here: la ctrl_port (RAM alias) so QEMU virt does not trap. */
.section .text
.global _start
_start:
        li      a0, 0x40000000
        li      a1, 2
        sb      a1, 0(a0)
        li      a1, 4
        sb      a1, 0(a0)

        li      a0, 0x100000
        li      a1, 0x5555
        sw      a1, 0(a0)

1:      j       1b
