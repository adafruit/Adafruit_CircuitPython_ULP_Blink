build:
	mkdir build

build/blink.o: blink.c | build
	clang -c -target riscv32 -mabi=ilp32 -mcmodel=medlow -march=rv32imc -ggdb3 -nostdlib -ffunction-sections $^ -o $@

build/blink.elf: link.ld build/blink.o | build
	clang -target riscv32 -mabi=ilp32 -mcmodel=medlow -march=rv32imc -nostdlib -ggdb3 -Wl,-Map,$@.map -T $^ -o $@

build/blink.ast.json: blink.c | build
	clang -Xclang -ast-dump=json -fsyntax-only -fparse-all-comments $^ > $@

build/adafruit_ulp_blink.py: gen_python.py build/blink.elf build/blink.ast.json
	python $^ > $@

clean:
	rm build/*
