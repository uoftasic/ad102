# Lab 01 — A resistor you designed

Writeup: [`docs/labs/lab-01-a-resistor-you-designed-overview.md`](../../docs/labs/lab-01-a-resistor-you-designed-overview.md),
published at <https://uoftasic.com/ad102/#/labs/lab-01-a-resistor-you-designed-overview>. The
steps and expected output are there; this file is a quick reference.

## Run it

Inside the workbench `hpretl/iic-osic-tools:2026.08` (ngspice-47, PDK `sky130A` at
`/foss/pdks/sky130A`):

```bash
cd labs/lab-01-a-resistor-you-designed
make
```

`make` runs two ngspice decks and then the checker, and ends in `PASS` or `FAIL`. On a fresh
clone it ends in `FAIL`, because `spice/my_resistor.spice` ships with the naive sizing on
purpose. Each ngspice run is silent while it loads the SKY130 model cards (55–65 s per run
measured on the pinned image); it is not hung.

No environment setup is needed: no `.designinit`, no `PDK` variable, no `mod`. The decks name
the model library by absolute path, so a bare container works.

## Targets

| Target | What it does |
|---|---|
| `make` | `sheet`, then `mine`, then `check` |
| `make sheet` | 22 strips of poly: extract ohms per square and end resistance |
| `make mine` | simulate `spice/my_resistor.spice`, the file you edit |
| `make check` | re-run the verdict on logs already in `results/` |
| `make utrap` | the same device written `W=1 L=10` and `W=1u L=10u` (optional; not part of `make`) |
| `make clean` | delete the logs in `results/`, keep sources |

## Files

| File | What it is |
|---|---|
| `spice/sheet.spice` | 22 strips of `res_high_po` and `res_xhigh_po`, 1 µA forced through each. This is the measurement. |
| `spice/my_resistor.spice` | **The file you edit.** Two `L=` numbers, nothing else. |
| `spice/u_trap.spice` | The `u` suffix trap from Getting started: one device written two ways. |
| `src/check_res.py` | The checker. Extracts Ω/□ and end resistance from your log and prints the verdict. |
| `solutions/` | Reference sizing. Open it after your own numbers pass. |
| `results/` | Everything ngspice writes. Gitignored except `.gitkeep`. |

`W` and `L` on a SKY130 device are plain micron numbers: `W=1`, never `W=1u`. Apart from
`spice/u_trap.spice`, which exists to show the mistake, there is no `u` suffix anywhere in this
package.
