# Lab 02: How big is a picofarad?

Writeup: [`docs/labs/lab-02-how-big-is-a-picofarad-overview.md`](../../docs/labs/lab-02-how-big-is-a-picofarad-overview.md),
published at <https://uoftasic.com/ad102/labs/lab-02-how-big-is-a-picofarad-overview.html>. The
writeup has the steps and the expected output; this file is a quick reference.

## Run it

Inside the workbench `hpretl/iic-osic-tools:2026.08` (ngspice-47, PDK `sky130A`):

```bash
cd labs/lab-02-how-big-is-a-picofarad
make
```

`make` runs four ngspice decks and then the checker, and ends in `PASS` or `FAIL`. On a fresh
clone it ends in `FAIL`, because `spice/my_cap.spice` ships with the naive sizing on purpose.
`pf`, `mine` and `tank` are each silent for about a minute while the SKY130 model cards load;
`henry` loads three small inductor files and finishes almost immediately.

You don't need any environment setup, because every deck names the model library by its absolute
path.

## Targets

| Target | What it does |
|---|---|
| `make` | `pf`, `mine`, `henry`, `tank`, then `check` |
| `make pf` | the MIM area ladder, one picofarad two ways, and the MOS and VPP capacitors |
| `make mine` | simulate `spice/my_cap.spice`, the file you edit |
| `make henry` | L, Q and self-resonance of the three SKY130 inductors |
| `make tank` | a 2.4 GHz resonator from `ind_03_90` and a MIM capacitor |
| `make check` | re-run the verdict on logs already in `results/` |
| `make clean` | delete the logs in `results/`, keep sources |

## Files

| File | What it is |
|---|---|
| `spice/picofarad.spice` | Five square MIM plates, one picofarad two ways, and four capacitors built four different ways. |
| `spice/my_cap.spice` | **The file you edit.** Three plate sizes. |
| `spice/henry.spice` | The three SKY130 inductor models, swept from 100 MHz to 100 GHz. |
| `spice/tank.spice` | A 2.4 GHz resonator built from `ind_03_90` and a MIM capacitor. |
| `src/check_cap.py` | The checker. Fits the plate capacitor's terms, prices a picofarad four ways, and checks the inductors. |
| `src/plot_inductors.py` | Optional. Draws `results/ind_sweep.txt` as L and Q against frequency, with the self-resonances marked. It needs nothing installed. |
| `solutions/` | Reference sizing and discussion. Open it after your numbers pass. |

The capacitors are measured on a 1 V AC source at 1 MHz, with $C = |I| / (2\pi f)$. The inductors
are driven with a 1 A AC current source, so the node voltage is the impedance; then
$L = \operatorname{Im}(Z)/2\pi f$ and $Q = \operatorname{Im}(Z)/\operatorname{Re}(Z)$.

`W` and `L` on a SKY130 device are plain numbers in microns, so you write `W=1`, never `W=1u`, and
you won't find a `u` suffix anywhere in this package.
