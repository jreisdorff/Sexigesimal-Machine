#!/bin/sh
set -e
cd "$(dirname "$0")"
PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
command -v riscv64-elf-gcc >/dev/null 2>&1 || {
  echo "Install: brew install riscv64-elf-gcc" >&2
  exit 1
}
command -v qemu-system-riscv64 >/dev/null 2>&1 || {
  echo "Install: brew install qemu" >&2
  exit 1
}
riscv64-elf-gcc -march=rv64i -mabi=lp64 -mcmodel=medany \
  -nostdlib -nostartfiles -Wl,--no-relax -Tthecode.ld \
  -o thecode.elf thecode.S
exec qemu-system-riscv64 -machine virt -nographic -bios none -kernel thecode.elf
