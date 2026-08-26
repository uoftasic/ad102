# AD102 Lab 01 -- A resistor you designed
# Runs inside hpretl/iic-osic-tools:2026.04 (ngspice 46, sky130A).
#
#   make          measure the device, then check the resistors you sized
#   make sheet    part 1: extract ohms-per-square and end resistance
#   make mine     part 2: simulate spice/my_resistor.spice, the file you edit
#   make check    re-run the verdict on logs you already have
#   make clean    delete results/, keep sources
#
# TIMING: each ngspice run spends about 60 seconds reading 12 MB of SKY130
# model cards before it prints anything at all. Two runs, so `make` takes
# roughly two and a half minutes and is silent for most of it. It is not hung.

RES   := results
CHECK := python3 src/check_res.py

.PHONY: all sheet mine check clean

all: sheet mine check

## sheet -- 22 strips of poly, one operating point, two numbers out of it
sheet: | $(RES)
	@echo "=============================================================="
	@echo " 1. MEASURING THE DEVICE"
	@echo "    22 resistors, 1 uA through each. ~60 s of silence first."
	@echo "=============================================================="
	ngspice -b spice/sheet.spice > $(RES)/sheet.log 2>&1
	@grep -E "^---|^r_" $(RES)/sheet.log

## mine -- the two resistors you sized yourself
mine: | $(RES)
	@echo ""
	@echo "=============================================================="
	@echo " 2. YOUR TWO RESISTORS  (spice/my_resistor.spice)"
	@echo "=============================================================="
	ngspice -b spice/my_resistor.spice > $(RES)/mine.log 2>&1
	@grep -E "^---|^r_" $(RES)/mine.log

## check -- the verdict, from logs already on disk
check:
	@echo ""
	@$(CHECK) --sheet $(RES)/sheet.log --mine $(RES)/mine.log; \
	  st=$$?; \
	  if [ $$st -ne 0 ]; then \
	    echo "  ^ On a fresh clone this FAIL is the lab, not a broken"; \
	    echo "    package. spice/my_resistor.spice ships with the naive"; \
	    echo "    sizing on purpose. Edit the two L= numbers and run"; \
	    echo "    \`make mine check\` again."; \
	  fi; \
	  exit $$st

$(RES):
	@mkdir -p $(RES)

clean:
	rm -f $(RES)/*.log $(RES)/*.txt
