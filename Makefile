#COMPILER=clang -target riscv32
COMPILER=riscv64-unknown-elf-gcc

build:
	mkdir build

build/blink.o: blink.c | build
	# clang -c -target riscv32 -mabi=ilp32 -mcmodel=medlow -march=rv32imc -Os -ggdb3 -nostdlib -ffunction-sections $^ -o $@
	riscv64-unknown-elf-gcc -c -mabi=ilp32 -mcmodel=medlow -march=rv32imc -Os -ggdb3 -nostdlib -ffunction-sections $^ -o $@

# clang -target riscv32 -mabi=ilp32 -mcmodel=medlow -march=rv32imc -nostdlib -ggdb3 -Wl,-Map,$@.map -T $^ -o $@
build/blink.elf: link.ld build/blink.o | build
	riscv64-unknown-elf-gcc -mabi=ilp32 -mcmodel=medlow -march=rv32imc -nostdlib -ggdb3 -Wl,-Map,$@.map -T $^ -o $@

build/blink.ast.json: blink.c | build
	clang -Xclang -ast-dump=json -fsyntax-only -fparse-all-comments $^ > $@

build/adafruit_ulp_blink.py: gen_python.py build/blink.elf build/blink.ast.json
	python $^ > $@

clean:
	rm build/*

build/sleep_pin_wait.o: sleep_pin_wait.c | build
	$(COMPILER) -c -mabi=ilp32 -mcmodel=medlow -march=rv32imc -Os -ggdb3 -nostdlib -ffunction-sections $^ -o $@

build/sleep_pin_wait.elf: link.ld build/sleep_pin_wait.o | build
	$(COMPILER) -mabi=ilp32 -mcmodel=medlow -march=rv32imc -nostdlib -ggdb3 -Wl,-Map,$@.map -T $^ -o $@

build/sleep_pin_wait.ast.json: sleep_pin_wait.c | build
	clang -Xclang -ast-dump=json -fsyntax-only -fparse-all-comments $^ > $@

build/adafruit_ulp_sleep_pin_wait.py: gen_python.py build/sleep_pin_wait.elf build/sleep_pin_wait.ast.json
	python $^ > $@
