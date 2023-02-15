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

class SleepPinWait:
    def __init__(self,
button_pin: microcontroller.Pin,
led_pin: microcontroller.Pin,
sx_version: int = 3
) -> None:
        self.ulp = espulp.ULP()
        self.ulp.halt()
        self.pins = []
        self.program = bytearray(278)
        self.program[0:276] = (
            b"\x6f\x00\xe0\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" # 00000000
            b"\x82\x80\x21\x65\x83\x25\x45\x10\x37\x06\xc0\xfd\x7d\x16\xf1\x8d" # 00000010
            b"\x23\x22\xb5\x10\x82\x80\x21\x65\xb7\xc5\x0f\x00\x23\x22\xb5\x10" # 00000020
            b"\x83\x25\x45\x10\x37\x06\x00\x02\xd1\x8d\x23\x22\xb5\x10\x83\x25" # 00000030
            b"\x45\x10\x37\x06\x40\x00\xd1\x8d\x23\x22\xb5\x10\x82\x80\x37\x21" # 00000040
            b"\x00\x00\x97\x00\x00\x00\xe7\x80\x00\xfc\x97\x00\x00\x00\xe7\x80" # 00000050
            b"\x00\x01\x97\x00\x00\x00\xe7\x80\x40\xfc\x37\x05\x00\x00\x03\x25" # 00000060
            b"\xc5\x11\x8d\x45\x63\x18\xb5\x00\x35\x65\x13\x05\x45\x90\xb7\x05" # 00000070
            b"\x00\x80\x0c\xc1\x37\x08\x00\x00\x03\x25\x48\x11\x0a\x05\xa9\x65" # 00000080
            b"\x13\x86\x45\x48\x32\x95\x14\x41\x37\x07\x08\x00\xd9\x8e\x14\xc1" # 00000090
            b"\x03\x25\x48\x11\x0a\x05\x32\x95\x14\x41\x37\x07\xfa\xff\x7d\x17" # 000000a0
            b"\xf9\x8e\x14\xc1\x03\x25\x48\x11\x0a\x05\x32\x95\x10\x41\xb7\x26" # 000000b0
            b"\x00\x08\x55\x8e\x10\xc1\x03\x25\x48\x11\x29\x05\x85\x48\x33\x95" # 000000c0
            b"\xa8\x00\x23\xaa\xa5\x40\x03\x25\x48\x11\x01\x47\xb3\x97\xa8\x00" # 000000d0
            b"\x21\x65\x93\x06\x85\x0d\x61\x05\x90\x42\x5d\x8e\x90\xc2\x03\x26" # 000000e0
            b"\x48\x11\xb3\x97\xc8\x00\x03\xa6\x45\x42\x29\x82\x7d\x8e\xb3\x36" # 000000f0
            b"\xc0\x00\xd9\x8e\x85\x8a\x13\x37\x16\x00\xf5\xf6\x85\x47\xaa\x86" # 00000100
            b"\xe1\xbf\x00\x00" # 00000110
        )
        self.program[276:288] = (
            b"\x0e\x00\x00\x00\x10\x00\x00\x00\x03\x00\x00\x00" # 00000114
        )
        self.pins.append(button_pin)
        struct.pack_into("I", self.program, 0x00000114, espulp.get_rtc_gpio_number(button_pin))
        self.pins.append(led_pin)
        struct.pack_into("I", self.program, 0x00000118, espulp.get_rtc_gpio_number(led_pin))
        struct.pack_into("I", self.program, 0x0000011c, sx_version)
        self.memory_map = memorymap.AddressRange(start=0x50000000, length=0x2000)
        self.ulp.run(self.program, pins=self.pins)

