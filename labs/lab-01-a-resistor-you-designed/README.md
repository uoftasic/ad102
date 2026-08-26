# Lab 01 — A resistor you designed

Writeup: [`docs/labs/lab-01-a-resistor-you-designed-overview.md`](../../docs/labs/lab-01-a-resistor-you-designed-overview.md)

You have written `R = 10k` on a schematic many times. This lab asks the next
question: **10 kΩ of what, shaped how, and how much silicon does it cost?**

Runs inside the workbench `hpretl/iic-osic-tools:2026.04` — ngspice **46**,
PDK **sky130A** at `/foss/pdks/sky130A`. Check yours with `ngspice -v`.

```bash
cd labs/lab-01-a-resistor-you-designed
make            # measure the device, then check the two resistors you sized
```

No environment setup. No `.designinit`, no `PDK` variable, no `mod`. The two
decks name the model library by absolute path, so a bare container works.

## Files

| File | What it is |
|---|---|
| `spice/sheet.spice` | 22 strips of poly-silicon, 1 µA forced through each. This is the measurement. |
| `spice/my_resistor.spice` | **The file you edit.** Two `L=` numbers, nothing else. |
| `src/check_res.py` | The grader. Extracts Ω/□ and end resistance from your log and renders a verdict. |
| `solutions/` | Reference sizing. Open it *after* your own numbers pass, not before. |
| `results/` | Everything ngspice writes. Gitignored except `.gitkeep`. |

## Two things in the output that are not bugs

**ngspice prints nothing for about a minute.** Each run reads
`sky130.lib.spice`, which pulls in 12 MB of model cards for every device in
SKY130 — most of them MOSFETs you are not using. Measured on the pinned
image: **61 s** before the first line appears. It is not hung. `make` runs the
simulator twice, so budget about two and a half minutes.

**A wall of `unrecognized parameter` warnings.** Exactly **170** of them in
`results/sheet.log`, across **34** blocks that look like this:

```
Warning: Model issue on line 4842 :
  .model xl1:rhead_model r sw_et=0 isnoisy=0 rsh=    3.458312000000000e+02 ...
unrecognized parameter (sw_et) - ignored
unrecognized parameter (isnoisy) - ignored
unrecognized parameter (p2) - ignored
unrecognized parameter (q2) - ignored
```

Harmless, and worth knowing why. SkyWater writes one set of model cards for
several simulators. `sw_et`, `isnoisy`, `p2`, `q2`, `p3` and `q3` are
Spectre-flavoured keywords describing self-heating, noise and the resistor's
voltage coefficients. ngspice does not implement them, says so, and uses the
parameters it does understand. The resistance you measure is the sheet
resistance, the geometry and the temperature coefficients — which is all this
lab is about.

An **`Error`** at the start of a line is a different matter. That one is real.

## The trap that catches everyone once

`W` and `L` on a SKY130 device are **plain micron numbers with no unit
suffix**:

```
Xr1 a 0 0 sky130_fd_pr__res_high_po W=1 L=10       <- one micron by ten microns
Xr1 a 0 0 sky130_fd_pr__res_high_po W=1u L=10u     <- one METRE by ten metres
```

The second one is outside every bin the model was fitted over. On a MOSFET
it stops the simulation with `could not find a valid modelname`; on a resistor
it silently gives you an answer that is wrong by a factor of a million. There
is no `u` anywhere in either deck in this package, and there should be none in
yours.

## Reference numbers (ngspice 46, sky130A, tt corner, 27 °C)

These are **golden** — a DC operating point has no randomness in it, so your
run matches to every digit printed.

```
sky130_fd_pr__res_high_po      317.2198 ohm/square    378.2448 ohm of ends
sky130_fd_pr__res_xhigh_po    2118.7619 ohm/square     34.2111 ohm of ends
```

If those two lines come out of your own `make sheet`, everything else in the
lab is arithmetic you can do on paper.
