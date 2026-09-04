# Lab 02 — How big is a picofarad?

Writeup: [`docs/labs/lab-02-how-big-is-a-picofarad-overview.md`](../../docs/labs/lab-02-how-big-is-a-picofarad-overview.md)

Lab 01 priced a resistor. This one prices the other two passives, and the
answers get much worse.

Runs inside the workbench `hpretl/iic-osic-tools:2026.08` — ngspice **46**,
PDK **sky130A**. No environment setup: every deck names the model library by
absolute path.

```bash
cd labs/lab-02-how-big-is-a-picofarad
make            # about three and a half minutes, mostly silent
```

## Files

| File | What it is |
|---|---|
| `spice/picofarad.spice` | Five square MIM plates, one picofarad twice, and four capacitors built four different ways. |
| `spice/my_cap.spice` | **The file you edit.** Three plate sizes. |
| `spice/henry.spice` | The only three inductors in SKY130, swept from 100 MHz to 100 GHz. Runs instantly — no MOSFET models to load. |
| `spice/tank.spice` | A 2.4 GHz resonator built from `ind_03_90` and a MIM capacitor you can size by hand. |
| `src/plot_inductors.py` | Optional. Draws `results/ind_sweep.txt` as L and Q against frequency, with the self-resonances marked. Nothing to install. |
| `src/check_cap.py` | The grader. Fits the two terms of a plate capacitor, prices a picofarad four ways, and checks the inductors. |
| `solutions/` | Reference sizing and the arguments worth having. After your numbers pass. |

## How the measurement works

Every capacitance in this lab is read the same way: hang the device on a 1 V
AC source at 1 MHz and look at the current the source has to supply. For a
capacitor $I = 2\pi f C V$, so $C = |I| / (2\pi f)$. One division. There is no
fitting and no waveform to eyeball.

The inductors are read the same way in reverse: drive one terminal with a
**1 A** AC current source and ground the other, and the node voltage *is* the
impedance, because $Z = V/I = V/1$. Then $L = \operatorname{Im}(Z)/2\pi f$ and
$Q = \operatorname{Im}(Z)/\operatorname{Re}(Z)$.

## Two things in the output that are not bugs

**Three of the four runs are silent for about a minute** while ngspice reads
12 MB of SKY130 model cards. `make henry` is the exception and finishes
immediately, because the inductor models are three small files that live
outside the corner library — which is itself a hint about how much the foundry
expects you to use them.

**`W=1`, never `W=1u`.** SKY130 geometry parameters are plain micron numbers.
There is no `u` suffix anywhere in this package and there should be none in
yours.

## Reference numbers (ngspice 47, sky130A, tt corner, 27 °C)

**Golden** — AC operating points are deterministic; yours match to the digit.

```
MIM plate, square, side s :  C[fF] = 2.000000 s^2 + 0.659991 s - 0.017742
one picofarad             :  MIM 492.68 um^2   MOS 127.01 um^2   VPP 1096.96 um^2
ind_05_220                :  9.9220 nH   Q max 12.718   self-resonant 3.5236 GHz
ind_05_125                :  5.7857 nH   Q max 13.083   self-resonant 6.5212 GHz
ind_03_90                 :  1.5208 nH   Q max 21.126   self-resonant 16.5015 GHz
```
