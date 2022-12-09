ENTRY(reset)

MEMORY
{
    ram(RW) : ORIGIN = 0, LENGTH = 0x2000
}

SECTIONS
{
    . = ORIGIN(ram);
    .text :
    {
        *(.text.reset) /* Default reset vector must link to offset 0x0 */
        . = 0x0010;
        *(.text.interrupt) /* Interrupt vector must link to offset 0x10 */
        *(.text.*)
    } > ram

    .rodata ALIGN(4):
    {
        *(.rodata)
        *(.rodata*)
    } > ram

    .data ALIGN(4):
    {
        *(.data)
        *(.data*)
        *(.sdata)
        *(.sdata*)
    } > ram

    .bss ALIGN(4) :
    {
        *(.bss)
        *(.bss*)
        *(.sbss)
        *(.sbss*)
    } > ram

    __stack_top = ORIGIN(ram) + LENGTH(ram);
}