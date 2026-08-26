# AD102 Lab 03 -- A time constant in silicon
# Runs inside hpretl/iic-osic-tools:2026.04 (ngspice 46, sky130A).
#
#   make          both decks, then the verdict
#   make rc       part 1: the same RC eight ways, plus temperature
#   make mine     part 2: simulate spice/my_rc.spice, the file you edit
#   make check    re-run the verdict on logs you already have
#   make bode     the same RC in the frequency domain, and the AD101 overlay
#   make figure   re-render that plot into docs/assets/img (maintainers only)
#   make netlist  netlist xschem/rc.sch -- the same circuit, drawn
#   make edit     open xschem/rc.sch in XSchem   (needs the noVNC desktop)
#   make clean    delete results/, keep sources
#
# TIMING: two ngspice runs, each about 60 seconds of silence while the SKY130
# model cards load, then a few seconds of actual simulation. Budget two and a
# half minutes for a full `make`.

RES   := results
CHECK := python3 src/check_rc.py

.PHONY: all rc mine check bode figure netlist edit clean

all: rc mine check

## rc -- ideal, real, mis-sized, cold, hot, and one microsecond
rc: | $(RES)
	@echo "=============================================================="
	@echo " 1. THE SAME RC, EIGHT WAYS   (~60 s of silence first)"
	@echo "=============================================================="
	ngspice -b spice/rc.spice > $(RES)/rc.log 2>&1
	@grep -E "^t_|^v_|^cpar|^---" $(RES)/rc.log

## mine -- 20 ns, as cheaply as you can manage
mine: | $(RES)
	@echo ""
	@echo "=============================================================="
	@echo " 2. YOUR 20 ns TIME CONSTANT  (spice/my_rc.spice)"
	@echo "=============================================================="
	ngspice -b spice/my_rc.spice > $(RES)/my_rc.log 2>&1
	@grep -E "^t_" $(RES)/my_rc.log

## check -- the verdict, from logs already on disk
check:
	@echo ""
	@$(CHECK) --rc $(RES)/rc.log --mine $(RES)/my_rc.log; \
	  st=$$?; \
	  if [ $$st -ne 0 ] && [ -f $(RES)/my_rc.log ]; then \
	    echo "  ^ On a fresh clone this FAIL is the lab, not a broken"; \
	    echo "    package. spice/my_rc.spice ships with a 20 ns RC that"; \
	    echo "    costs twelve times the area budget. Make it smaller."; \
	  fi; \
	  exit $$st

## bode -- the same RC asked a frequency-domain question (about 2 s: fast lib)
bode: | $(RES)
	@echo "=============================================================="
	@echo " THE SAME RC, IN FREQUENCY   (~2 s -- this deck uses the fast"
	@echo " pre-flattened tt library, because it needs no other corner)"
	@echo "=============================================================="
	ngspice -b spice/bode.spice > $(RES)/bode.log 2>&1
	@grep -E "^f3db|^ph_real|^g_10x|^---" $(RES)/bode.log
	@python3 src/plot_bode.py $(RES)/bode.txt $(RES)

## figure -- the same plot, written where the guide page embeds it (maintainers)
figure: | $(RES)
	@python3 src/plot_bode.py $(RES)/bode.txt ../../docs/assets/img

## netlist -- prove the drawn version is the same circuit as spice/rc.spice part E
netlist:
	@echo "== netlisting xschem/rc.sch"
	@cd xschem && PDK=sky130A PDK_ROOT=$${PDK_ROOT:-/foss/pdks} xschem -n -q -x rc.sch >/dev/null 2>&1
	@test -f xschem/simulation/rc.spice || { \
	  echo "   XSchem wrote no netlist. If you are in a bare container with no"; \
	  echo "   desktop, that is expected -- this target needs the workbench."; exit 1; }
	@echo "   wrote xschem/simulation/rc.spice"
	@grep -E "^x(r1|c1) |^X(R1|C1) " xschem/simulation/rc.spice || true

## edit -- open the drawn version (needs the noVNC desktop and $PDK=sky130A)
edit:
	@cd xschem && xschem rc.sch &

$(RES):
	@mkdir -p $(RES)

clean:
	rm -f $(RES)/*.log $(RES)/*.txt $(RES)/*.png
	rm -rf xschem/simulation
