# Lab 03 — A time constant in silicon

Writeup: [`docs/labs/lab-03-a-time-constant-in-silicon-overview.md`](../../docs/labs/lab-03-a-time-constant-in-silicon-overview.md)

Labs 01 and 02 designed a resistor and a capacitor. This one puts them in the
same circuit and asks whether $\tau = RC$ survives contact with silicon.

Runs inside the workbench `hpretl/iic-osic-tools:2026.04` — ngspice **46**,
PDK **sky130A**. No environment setup.

```bash
cd labs/lab-03-a-time-constant-in-silicon
make            # about two and a half minutes, mostly silent
make bode       # optional: the same RC in frequency, + the AD101 overlay (~2 s)
make netlist    # optional: turn xschem/rc.sch back into device lines (~1 s)
make edit       # optional: open it in XSchem  (needs the noVNC desktop)
```

On a fresh clone `make` ends in **FAIL**, on area. That is the lab — `spice/my_rc.spice`
ships with a 20 ns RC that costs twelve times the budget, so that you get to shrink it.

## Files

| File | What it is |
|---|---|
| `spice/rc.spice` | The same RC eight ways: ideal, half-real, fully real, mis-sized, cold, hot, and one microsecond. Plus what a bare strip of poly weighs. |
| `spice/my_rc.spice` | **The file you edit.** One resistor length and one capacitor side. |
| `spice/bode.spice` | The same devices as part E, asked a frequency-domain question. Simulates the ideal 10 kΩ × 1 pF alongside, so the Bode plot is the AD101 overlay. |
| `src/check_rc.py` | The grader. Converts every `meas` into a time constant and prices your design. |
| `src/plot_bode.py` | Draws `docs/assets/img/ad102-rc-bode.png` from `results/bode.txt`. |
| `xschem/rc.sch` | The same circuit as part E, **drawn**. `make netlist` turns it back into the two device lines it came from; `make edit` opens it in XSchem. This is AD102's one look at the tool AD103 is built on. |
| `solutions/` | One good answer, and the argument about it. After yours passes. |

## Part A is somebody else's deck

The first circuit in `spice/rc.spice` is
[ECE334](https://ece334.github.io/ece334-docs/)'s lab-1 RC deck, unchanged: a
1 kΩ/2 kΩ divider with 0.7 pF on the tap, driven by a 1.8 V pulse. It is here
because it is the version of this circuit a UofT student is most likely to
have already run, and because its answer is a Thevenin exercise rather than a
fabrication one:

$$R_{\text{th}} = 1\text{k} \parallel 2\text{k} = 666.67\ \Omega
\qquad \tau = 666.67 \times 0.7\,\text{pF} = 466.67\ \text{ps}$$

Everything after it is the same circuit with the ideal components taken away.

## The 5 picoseconds

Every `meas` in this lab reports a time measured from $t = 0$, and the step
happens at $t = 1$ ns, so you would expect $\tau = t_{\text{meas}} - 1$ ns.
It is not quite that. The measured ideal RC comes out at **11.0050 ns**, five
picoseconds late, and so does every other circuit in the deck — including the
ECE334 one, whose $\tau$ is twenty times smaller.

A constant error that does not scale with the thing being measured is a clue.
The pulse source has a **10 ps rise time**, and a first-order system does not
start responding at the foot of a ramp; it behaves as though the step arrived
at the ramp's midpoint. Half of 10 ps is 5 ps. `check_rc.py` subtracts
1.005 ns, and then the ideal circuit reads **10.0000 ns** and the ECE334
circuit reads **466.6700 ps** — both exact.

That is a measurement artefact, not a device effect, and telling the two apart
is most of what analog verification is.

## Reference numbers (ngspice 46, sky130A, tt corner)

**Golden** — a transient analysis of a linear circuit has no randomness in it.

```
ideal 10k x 1p                           tau = 10.0000 ns
your Lab 01 resistor + ideal 1 pF              10.0361 ns
ideal 10k + your Lab 02 capacitor              10.0000 ns
both of yours                                  10.0362 ns   (+0.36 %)
sized without Labs 01 and 02                   10.5647 ns   (+5.65 %)
the same silicon at -40 C / +125 C        9.7849 / 10.6544 ns  (8.66 % span)
real 1 Mohm x 1 pF                        1049.9550 ns   (+5.00 %)
poly to substrate                         0.1994 fF per um at W = 1 um
```
