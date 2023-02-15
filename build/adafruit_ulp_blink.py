import struct
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

class Blink:
    delay: int = StructMemory(0x0000010c, "I")
    """The delay between toggles in milliseconds"""
    def __init__(self,
led_pin: microcontroller.Pin,
sx_version: int = 3,
delay: int = 500
) -> None:
        self.ulp = espulp.ULP()
        self.ulp.halt()
        self.pins = []
        self.program = bytearray(262)
        self.program[0:260] = (
            b"\x6f\x00\xe0\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" # 00000000
            b"\x82\x80\x21\x65\x83\x25\x45\x10\x37\x06\xc0\xfd\x7d\x16\xf1\x8d" # 00000010
            b"\x23\x22\xb5\x10\x82\x80\x21\x65\xb7\xc5\x0f\x00\x23\x22\xb5\x10" # 00000020
            b"\x83\x25\x45\x10\x37\x06\x00\x02\xd1\x8d\x23\x22\xb5\x10\x83\x25" # 00000030
            b"\x45\x10\x37\x06\x40\x00\xd1\x8d\x23\x22\xb5\x10\x82\x80\x37\x21" # 00000040
            b"\x00\x00\x97\x00\x00\x00\xe7\x80\x00\xfc\x97\x00\x00\x00\xe7\x80" # 00000050
            b"\x00\x01\x97\x00\x00\x00\xe7\x80\x40\xfc\x37\x05\x00\x00\x03\x25" # 00000060
            b"\x85\x10\x89\x45\x63\x0e\xb5\x00\x8d\x45\x63\x1f\xb5\x00\x35\x65" # 00000070
            b"\xb7\x05\x00\x80\x23\x22\xb5\x90\x11\x65\x13\x05\xc5\x45\x31\xa0" # 00000080
            b"\x09\x65\x13\x05\x45\x13\x11\xa0\x01\x45\xb7\x08\x00\x00\x83\xa5" # 00000090
            b"\x48\x10\x8a\x05\x29\x68\x13\x06\x48\x48\xb2\x95\x37\x06\x08\x00" # 000000a0
            b"\x90\xc1\x83\xa5\x48\x10\xa9\x05\x85\x42\xb3\x95\xb2\x00\x23\x28" # 000000b0
            b"\xb8\x40\x37\x07\x00\x00\x93\x07\x88\x40\x05\x46\x83\xa5\x48\x10" # 000000c0
            b"\xa9\x05\x93\x76\x16\x00\xb3\x95\xb2\x00\x81\xc6\x23\x22\xb8\x40" # 000000d0
            b"\x11\xa0\x8c\xc3\xf3\x26\x00\xc0\x83\x25\xc7\x10\xb3\x85\xa5\x02" # 000000e0
            b"\xb6\x95\x63\xf6\xb6\x00\xf3\x26\x00\xc0\xe3\xee\xb6\xfe\x13\x46" # 000000f0
            b"\x16\x00\xe9\xb7" # 00000100
        )
        self.program[260:272] = (
            b"\x0f\x00\x00\x00\x03\x00\x00\x00\xf4\x01\x00\x00" # 00000104
        )
        self.pins.append(led_pin)
        struct.pack_into("I", self.program, 0x00000104, espulp.get_rtc_gpio_number(led_pin))
        struct.pack_into("I", self.program, 0x00000108, sx_version)
        struct.pack_into("I", self.program, 0x0000010c, delay)
        self.memory_map = memorymap.AddressRange(start=0x50000000, length=0x2000)
        self.ulp.run(self.program, pins=self.pins)

