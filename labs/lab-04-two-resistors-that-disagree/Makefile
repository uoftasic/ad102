# AD102 Lab 04 -- Two resistors that disagree
# Runs inside hpretl/iic-osic-tools:2026.08 (ngspice 47, sky130A).
#
#   make          both decks, then the verdict
#   make mm       part 1: 200 dies, four sizes and four dividers
#   make mine     part 2: simulate spice/my_divider.spice, the file you edit
#   make check    re-run the verdict on logs you already have
#   make clean    delete results/, keep sources
#
# TIMING: each deck spends ~55 s loading the SKY130 model cards and then
# re-evaluates the whole netlist 200 times, once per imaginary die. Measured
# twice on the pinned image: 106 s and 128 s for a full `make`. Budget two and a
# half minutes. It prints nothing while it works. It is not hung.

RES   := results
CHECK := python3 src/check_mm.py

.PHONY: all mm mine check clean

all: mm mine check

## mm -- 200 dies: four resistor sizes, four dividers
mm: | $(RES)
	@echo "=============================================================="
	@echo " 1. TWO HUNDRED DIES          (~80 s, silent)"
	@echo "=============================================================="
	ngspice -b spice/mismatch.spice > $(RES)/mismatch.log 2>&1
	@printf "operating points (200 dies + 1 nominal) : "; grep -c "^v(s1)" $(RES)/mismatch.log
	@sed -n '/NOMINAL/,$$p' $(RES)/mismatch.log | grep -E "^---|^v\("

## mine -- your 0.45 V divider, 200 dies of it
mine: | $(RES)
	@echo ""
	@echo "=============================================================="
	@echo " 2. YOUR DIVIDER              (~50 s, silent)"
	@echo "=============================================================="
	ngspice -b spice/my_divider.spice > $(RES)/my_divider.log 2>&1
	@printf "operating points (200 dies + 1 nominal) : "; grep -c "^v(tap)" $(RES)/my_divider.log
	@sed -n '/NOMINAL/,$$p' $(RES)/my_divider.log | grep -E "^---|^v\("

## check -- the verdict, from logs already on disk
check:
	@echo ""
	@$(CHECK) --mm $(RES)/mismatch.log --mine $(RES)/my_divider.log; \
	  st=$$?; \
	  if [ $$st -ne 0 ] && [ -f $(RES)/my_divider.log ]; then \
	    echo "  ^ On a fresh clone this FAIL is the lab, not a broken"; \
	    echo "    package. spice/my_divider.spice ships with the divider"; \
	    echo "    everybody draws first, and it fails two of three checks."; \
	  fi; \
	  exit $$st

$(RES):
	@mkdir -p $(RES)

clean:
	rm -f $(RES)/*.log $(RES)/*.txt
