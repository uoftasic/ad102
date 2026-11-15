# Lab 03: A time constant in silicon

Writeup: [`docs/labs/lab-03-a-time-constant-in-silicon-overview.md`](../../docs/labs/lab-03-a-time-constant-in-silicon-overview.md),
published at <https://uoftasic.com/ad102/labs/lab-03-a-time-constant-in-silicon-overview.html>. The
steps and expected output are there; this file is a quick reference.

## Run it

Inside the workbench `hpretl/iic-osic-tools:2026.08` (ngspice-47, PDK `sky130A`):

```bash
cd labs/lab-03-a-time-constant-in-silicon
make
```

`make` runs two ngspice decks and then the checker, and ends in `PASS` or `FAIL`. On a fresh
clone it ends in `FAIL`, on area: `spice/my_rc.spice` ships with a 20 ns RC that costs twelve
times the area budget, so that you get to shrink it. Each ngspice run is silent for about a
minute while the SKY130 model cards load.

No environment setup is needed for the decks. `make edit` needs the noVNC desktop and
`PDK=sky130A`.

## Targets

| Target | What it does |
|---|---|
| `make` | `rc`, then `mine`, then `check` |
| `make rc` | the same RC eight ways, plus temperature, plus the parasitic of a bare poly strip |
| `make mine` | simulate `spice/my_rc.spice`, the file you edit |
| `make check` | re-run the verdict on logs already in `results/` |
| `make bode` | the same RC in the frequency domain, plotted against the ideal 10 kΩ × 1 pF from AD101 |
| `make figure` | re-render that plot into `docs/assets/img` (maintainers only) |
| `make netlist` | netlist `xschem/rc.sch`, the same circuit drawn, and print its two device lines |
| `make edit` | open `xschem/rc.sch` in XSchem (needs the noVNC desktop) |
| `make clean` | delete the logs, data and plots in `results/`, and `xschem/simulation/` |

The `make bode` banner says it takes about 2 s because it uses a pre-flattened library. That
library is not in the 2026.08 image; `spice/bode.spice` now loads the full `sky130.lib.spice`
and takes as long as the other decks.

## Files

| File | What it is |
|---|---|
| `spice/rc.spice` | The same RC eight ways: ideal, half-real, fully real, mis-sized, cold, hot, and one microsecond. Also measures the capacitance of a bare strip of poly. Section A is [ECE334](https://uoftasic.com/ece334-docs/)'s lab-1 RC deck, unchanged. |
| `spice/my_rc.spice` | **The file you edit.** One resistor length and one capacitor side. |
| `spice/bode.spice` | The same devices as section E in the frequency domain, with the ideal 10 kΩ × 1 pF alongside. |
| `src/check_rc.py` | The checker. Converts every `meas` into a time constant, after subtracting the 1.005 ns step offset, and prices your design. |
| `src/plot_bode.py` | Draws `results/ad102-rc-bode.png` from `results/bode.txt`. |
| `xschem/rc.sch` | Section E of `spice/rc.spice`, drawn. `make netlist` turns it back into device lines; `make edit` opens it. |
| `xschem/xschemrc` | XSchem settings for this folder. |
| `solutions/` | One good answer, and the discussion of it. Open it after yours passes. |
