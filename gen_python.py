

from elftools.dwarf.descriptions import describe_form_class
from elftools.elf.elffile import ELFFile
import sys
import json
import pathlib

std_to_type = {
    "uint8_t": ("B", "int"),
    "int8_t":  ("b", "int"),
    "bool":    ("?", "bool"),
    "uint16_t":("H", "int"),
    "int16_t": ("h", "int"),
    "uint32_t":("I", "int"),
    "int32_t": ("i", "int")
}

elf_file = pathlib.Path(sys.argv[1])
ast_file = pathlib.Path(sys.argv[2])
ast = json.loads(ast_file.read_text())

c_globals = []
attributes = []
parameters = []
for i in ast["inner"]:
    if i["kind"] == "VarDecl":
        default_value = 0
        comment = []
        if "inner" in i:
            for j in i["inner"]:
                if j["kind"] == "ImplicitCastExpr":
                    default_value = j["inner"][0]["value"]
                elif j["kind"] == "FullComment":
                    for p in j["inner"]:
                        pieces = []
                        for text in p["inner"]:
                            pieces.append(text["text"].strip())
                        comment.append(" ".join(pieces))

                else:
                    print("   ", j)
        qualType = i["type"]["qualType"]
        c_globals.append((i["name"], qualType, default_value, comment))
        attribute = False
        if "volatile" in qualType:
            t = qualType.replace("volatile", "").strip()
            attribute = True
        else:
            t = qualType

        typecode = std_to_type.get(t, None)

        if not typecode:
            print(t)
            continue

        if attribute:
            attributes.append((i["name"], typecode, "\n\n".join(comment), default_value))
        else:
            parameters.append((i["name"], typecode, "\n".join(comment), default_value))

symbols = {}
binary = {}
with elf_file.open('rb') as f:
    elffile = ELFFile(f)

    symtab = elffile.get_section_by_name('.symtab')
    for symbol in symtab.iter_symbols():
        info = symbol["st_info"]
        if symbol.name and info["bind"] == "STB_GLOBAL" and info["type"] == "STT_OBJECT":
            symbols[symbol.name] = symbol["st_value"]

    # Find the segment where the symbol is loaded to, as the symbol table points to
    # the loaded address, not the offset in the file
    file_offset = None
    for seg in elffile.iter_segments():
        if seg.header['p_type'] != 'PT_LOAD':
            continue
        binary[seg["p_vaddr"]] = seg.data()
        # If the symbol is inside the range of a LOADed segment, calculate the file
        # offset by subtracting the virtual start address and adding the file offset
        # of the loaded section(s)
        # if sym['st_value'] >= seg['p_vaddr'] and sym['st_value'] < seg['p_vaddr'] + seg['p_filesz']:
        #     file_offset = sym['st_value'] - seg['p_vaddr'] + seg['p_offset']
        #     break

total_size = 0
for start_address in binary:
    total_size = max(total_size, start_address + len(binary))

class_name = "".join((s.capitalize() for s in elf_file.stem.split("_")))

print(
"""import struct
import memorymap
import espulp

class StructMemory:
    def __init__(self, address, typecode):
        self.address = address
        self.typecode = typecode
        self.buf = bytearray(struct.calcsize(typecode))
        self.end = address + len(self.buf)

    def __get__(
        self,
        obj,
        objtype = None,
    ):
        self.buf = obj.memory_map[self.address:self.end]
        return struct.unpack_from(self.typecode, self.buf)[0]

    def __set__(self, obj, value) -> None:
        struct.pack_into(self.typecode, self.buf, 0, value)
        obj.memory_map[self.address:self.end] = self.buf
""")
print(f"class {class_name}:")
# volatile variables are class descriptors
for name, typecode, comment, _ in attributes:
    address = symbols[name]
    print(f"    {name}: {typecode[1]} = StructMemory(0x{address:08x}, \"{typecode[0]}\")")
    print(f"    \"\"\"{comment}\"\"\"")

print("    def __init__(self,")
ps = []
for name, _, _, default_value in parameters:
    ps.append(f"{name}: {typecode[1]} = {default_value}")
print(",\n".join(ps))
print(") -> None:")
print("        self.ulp = espulp.ULP()")
print("        self.ulp.halt()")
print(f"        self.program = bytearray({total_size})")
full_binary = bytearray(total_size)
for start_address in binary:
    data = binary[start_address]
    end = start_address + len(data)
    full_binary[start_address:end] = data
    print(f"        self.program[{start_address}:{end}] = (")
    offset = 0
    while offset < len(data):
        hex_bytes = "".join((f"\\x{b:02x}" for b in data[offset:offset+16]))
        print(f"            b\"{hex_bytes}\" # {start_address + offset:08x}")
        offset += 16
    print("        )")
with open(str(elf_file) + ".bin", "wb") as f:
    f.write(full_binary)
for name, typecode, _, default_value in parameters:
    address = symbols[name]
    print(f"        struct.pack_into(\"{typecode[0]}\", self.program, 0x{address:08x}, {name})")
print("        self.memory_map = memorymap.AddressRange(start=0x50000000, length=0x2000)")
print("        self.ulp.run(self.program)")
print()