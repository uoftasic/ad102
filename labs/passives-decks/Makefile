# AD102 -- passives-decks
# The ngspice decks behind the AD102 guide pages. Every number printed on
# a guide page comes out of this directory.
#
# Runs inside hpretl/iic-osic-tools:2026.04 (ngspice 46, sky130A).
#
#   make          run every deck, then check the numbers
#   make check    re-render the verdict from logs already on disk
#   make figures  regenerate the three PNGs the guide pages embed
#   make clean    delete results/, keep sources
#
# TIMING: each ngspice run spends about 60 seconds reading 12 MB of SKY130
# model cards before printing anything. There are seven runs, so `make`
# takes roughly eight minutes and is silent for most of it. Not hung.

RES     := results
FIGS    := ../../docs/assets/img
CORNERS := tt ll hh

.PHONY: all resistor capacitor inductor corners mismatch check figures clean

all: resistor capacitor inductor corners mismatch check

$(RES):
	@mkdir -p $(RES)

## resistor -- where a resistance actually comes from
resistor: | $(RES)
	@echo "== 1/5  resistor: head, body, and three sized values =========="
	ngspice -b spice/r_head_and_body.spice > $(RES)/r_head_and_body.log 2>&1
	@grep -E "^---|^r_|^head|^body" $(RES)/r_head_and_body.log

## capacitor -- three constructions, and the one that moves with voltage
capacitor: | $(RES)
	@echo "== 2/5  capacitor: MIM vs VPP vs MOS, then a C-V sweep ========"
	ngspice -b spice/c_area.spice     > $(RES)/c_area.log 2>&1
	ngspice -b spice/c_moscap_cv.spice > $(RES)/c_moscap_cv.log 2>&1
	@grep -E "^---|^c_" $(RES)/c_area.log
	@grep -E "^---|^c_" $(RES)/c_moscap_cv.log

## inductor -- L and Q for the three spirals SKY130 models
inductor: | $(RES)
	@echo "== 3/5  inductor: L, Q and series R of three spirals =========="
	ngspice -b spice/l_spiral.spice > $(RES)/l_spiral.log 2>&1
	@grep -E "^---|^[lqr][0-9_]" $(RES)/l_spiral.log

## corners -- the same circuit at three process corners
corners: | $(RES)
	@echo "== 4/5  corners: what moves, and what refuses to =============="
	@for c in $(CORNERS); do \
	  sed "s/@CORNER@/$$c/g" spice/corners.spice.in > spice/corners_$$c.spice; \
	  ngspice -b spice/corners_$$c.spice > $(RES)/corners_$$c.log 2>&1; \
	  grep -E "^---|^r_[ab]|^ratio|^divider|^c_mim|^f3db" $(RES)/corners_$$c.log; \
	done

## mismatch -- 200 Monte Carlo wafers, seed pinned
mismatch: | $(RES)
	@echo "== 5/5  mismatch: 200 wafers, four resistors =================="
	ngspice -b spice/mismatch.spice > $(RES)/mismatch.log 2>&1
	@echo "   $$(grep -c '^1m/' $(RES)/mismatch.log) measurements recorded"

## check -- the verdict
check:
	@echo ""
	@python3 src/check_passives.py $(RES)

## figures -- the PNGs the guide pages embed
figures: | $(RES)
	python3 src/plot_figures.py $(RES) $(FIGS)

clean:
	rm -f $(RES)/*.log $(RES)/*.txt spice/corners_tt.spice \
	      spice/corners_ll.spice spice/corners_hh.spice
