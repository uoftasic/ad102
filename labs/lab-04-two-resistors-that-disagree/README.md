# Lab 04 — Two resistors that disagree

Writeup: [`docs/labs/lab-04-two-resistors-that-disagree-overview.md`](../../docs/labs/lab-04-two-resistors-that-disagree-overview.md),
published at <https://uoftasic.com/ad102/#/labs/lab-04-two-resistors-that-disagree-overview>.
The steps and expected output are there; this file is a quick reference.

## Run it

Inside the workbench `hpretl/iic-osic-tools:2026.08` (ngspice-47, PDK `sky130A`):

```bash
cd labs/lab-04-two-resistors-that-disagree
make
```

`make` runs two Monte Carlo decks (200 dies plus one nominal die each) and then the checker, and
ends in `PASS` or `FAIL`. On a fresh clone it ends in `FAIL`, because `spice/my_divider.spice`
ships with the divider everybody draws first. It prints nothing while it works: a full `make`
took 106 s and 128 s on the pinned image, most of it loading the SKY130 model cards.

No environment setup is needed.

## Targets

| Target | What it does |
|---|---|
| `make` | `mm`, then `mine`, then `check` |
| `make mm` | 200 dies: four resistor sizes and four dividers |
| `make mine` | 200 dies of `spice/my_divider.spice`, the file you edit |
| `make check` | re-run the verdict on logs already in `results/` |
| `make clean` | delete the logs in `results/`, keep sources |

Both runs print `operating points (200 dies + 1 nominal) : 201` first. If you see 2 instead of
201, the Monte Carlo loop stopped after one die; the writeup's "Expected warnings and delays"
section explains why.

## Files

| File | What it is |
|---|---|
| `spice/mismatch.spice` | Four resistor sizes and four dividers, 200 dies each, plus a nominal die with mismatch switched off. `setseed 1` makes it reproducible. |
| `spice/my_divider.spice` | **The file you edit.** A 0.45 V tap that has to be accurate, precise and small. |
| `src/check_mm.py` | The checker. Collects the dies, reports mean and σ, and reads your geometry back out of your deck. |
| `solutions/` | One good answer and the discussion of it. Open it after yours passes. |
