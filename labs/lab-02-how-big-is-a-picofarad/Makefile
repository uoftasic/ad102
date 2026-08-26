# AD102 Lab 02 -- How big is a picofarad?
# Runs inside hpretl/iic-osic-tools:2026.04 (ngspice 46, sky130A).
#
#   make          everything, then the verdict
#   make pf       part 1: what a farad costs, in three technologies
#   make mine     part 2: simulate spice/my_cap.spice, the file you edit
#   make henry    part 3: the only three inductors in the PDK
#   make tank     part 4: a 2.4 GHz resonator out of two real devices
#   make check    re-run the verdict on logs you already have
#   make clean    delete results/, keep sources
#
# TIMING: pf, mine and tank each spend about 60 seconds reading SKY130's
# model cards before printing anything. henry does not -- it loads three small
# files and finishes instantly. Budget about three and a half minutes for a
# full `make`, most of it silent. It is not hung.

RES   := results
CHECK := python3 src/check_cap.py

.PHONY: all pf mine henry tank check clean

all: pf mine henry tank check

## pf -- the area ladder, one picofarad twice, and three technologies
pf: | $(RES)
	@echo "=============================================================="
	@echo " 1. WHAT A FARAD COSTS      (~60 s of silence first)"
	@echo "=============================================================="
	ngspice -b spice/picofarad.spice > $(RES)/picofarad.log 2>&1
	@grep -E "^---|^c_" $(RES)/picofarad.log

## mine -- the three capacitors you sized yourself
mine: | $(RES)
	@echo ""
	@echo "=============================================================="
	@echo " 2. YOUR THREE CAPACITORS   (spice/my_cap.spice)"
	@echo "=============================================================="
	ngspice -b spice/my_cap.spice > $(RES)/my_cap.log 2>&1
	@grep -E "^---|^c_" $(RES)/my_cap.log

## henry -- L, Q and self-resonance of every inductor SKY130 ships
henry: | $(RES)
	@echo ""
	@echo "=============================================================="
	@echo " 3. AND THE INDUCTOR?       (this one is fast)"
	@echo "=============================================================="
	ngspice -b spice/henry.spice > $(RES)/henry.log 2>&1
	@grep -E "^---|^l_|^q_|^r_" $(RES)/henry.log

## tank -- put the inductor and a capacitor you sized into one resonator
tank: | $(RES)
	@echo ""
	@echo "=============================================================="
	@echo " 4. ONE RESONATOR AT 2.4 GHz  (~60 s of silence first)"
	@echo "=============================================================="
	ngspice -b spice/tank.spice > $(RES)/tank.log 2>&1
	@grep -E "^fpeak|^zpeak" $(RES)/tank.log

## check -- the verdict, from logs already on disk
check:
	@echo ""
	@$(CHECK) --pf $(RES)/picofarad.log --mine $(RES)/my_cap.log \
	          --henry $(RES)/henry.log --sweep $(RES)/ind_sweep.txt \
	          --tank $(RES)/tank.log; \
	  st=$$?; \
	  if [ $$st -ne 0 ] && [ -f $(RES)/my_cap.log ]; then \
	    echo "  ^ On a fresh clone this FAIL is the lab, not a broken"; \
	    echo "    package. spice/my_cap.spice ships with the naive sizing"; \
	    echo "    on purpose. Fix it and run \`make mine check\` again."; \
	  fi; \
	  exit $$st

$(RES):
	@mkdir -p $(RES)

clean:
	rm -f $(RES)/*.log $(RES)/*.txt
