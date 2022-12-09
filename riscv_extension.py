# Annotate a RISC-V disassembly with the extension for each instruction

import sys

EXTENSION_MAPPING = {
    "j": "I",
    "c.ret": "C",
    "c.addi": "C",
    "c.sw":   "C",
    "c.lui":  "C",
    "lw":     "I",
    "lui":    "I",
    "c.and":  "C",
    "sw":     "I",
    "c.lw":   "C",
    "c.or":   "C",
    "auipc":  "I",
    "jalr":   "I",
    "c.li":   "C",
    "addi":   "I",
    "sb":     "I",
    "slli":   "I",
    "c.add":  "C",
    "sll":    "I",
    "lbu":    "I",
    "c.andi": "C",
    "beq":    "I",
    "rdcycle": "I",
    "sub":    "I",
    "bltu":   "I",
    "lb":     "I",
    "not":    "I"
}

disassembly_started = False
for line in sys.stdin:
    if disassembly_started and line.startswith(" "):
        pieces = line.strip().split("\t")
        length = len(pieces[0].split()) - 1
        if length == 2:
            pieces[1] = "c." + pieces[1]
        pieces.insert(1, EXTENSION_MAPPING[pieces[1]])
        print("\t".join(pieces))

    else:
        disassembly_started = disassembly_started or line.startswith("Disassembly")
        print(line)
