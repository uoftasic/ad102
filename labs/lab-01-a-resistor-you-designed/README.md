# Lab 01: A resistor you designed

Writeup: [`docs/labs/lab-01-a-resistor-you-designed-overview.md`](../../docs/labs/lab-01-a-resistor-you-designed-overview.md),
published at <https://uoftasic.com/ad102/labs/lab-01-a-resistor-you-designed-overview.html>. The
writeup has the steps and the expected output; this file is a quick reference to the package.

## Run it

Inside the workbench `hpretl/iic-osic-tools:2026.08` (ngspice-47, PDK `sky130A` at
`/foss/pdks/sky130A`):

```bash
cd labs/lab-01-a-resistor-you-designed
make
```

`make` runs two ngspice decks and then the checker, and ends in `PASS` or `FAIL`. On a fresh
clone it ends in `FAIL`, because `spice/my_resistor.spice` ships with the naive sizing on
purpose. Each ngspice run prints nothing while it loads the SKY130 model cards, which took
55–65 s per run on the pinned image, so a quiet terminal doesn't mean it has hung.

The decks name the model library by its absolute path, so the package runs in a bare container
without `.designinit`, the `PDK` variable or `mod`.

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

`W` and `L` on a SKY130 device are already in microns, so you write `W=1`, never `W=1u`. Apart
from `spice/u_trap.spice`, which exists to show the mistake, there is no `u` suffix anywhere in
this package.
