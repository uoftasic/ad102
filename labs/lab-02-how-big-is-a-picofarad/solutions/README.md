# Reference sizing (read this after your own numbers pass)

## The three answers

```
C1  250 fF MIM      side 11.0170 um     (naive 11.1803 -> 257.36 fF, +2.94 %)
C2   20 fF MIM      side  3.0030 um     (naive  3.1623 ->  22.07 fF, +10.35 %)
C3  250 fF MOS      side  5.6333 um     -- the naive answer, and it passes
```

## Why C3 passed and the other two did not

All three naive sizings made the same mistake: they used `area = C / density` and dropped the
edge term. That cost 2.94 % on C1, 10.35 % on C2, and 0.31 % on C3.

The edge term is a **perimeter** effect, so what matters is perimeter over area, which for a
square of side $s$ is $4/s$ and grows as the plate shrinks. That explains C1 against C2: same
type, a plate 3.7 times smaller, and an error 3.5 times bigger.

C3 is a different kind of device. Its dielectric is **gate oxide**, the thinnest insulator in the
process, so its area term is about four times the MIM's, while its edge term comes mostly from the
gate-to-source and gate-to-drain overlaps, which are small. When the area term is that large, the
edges have little left to contribute.

**The rule:** the fringe correction on a plate capacitor is roughly `edge / (area × s)`. Big
plates in a low-density technology are nearly pure area; small plates in a low-density technology
are not. Decide which one you are drawing before you decide whether you can ignore the fringe.

## Why anyone uses MIM, given these numbers

The MOS capacitor is 3.9 times denser and needs no extra mask, since it is a transistor. Part D of
`picofarad.spice` shows why nobody uses it for signal work:

```
--- D. the same MOS cap with the gate at 0 V (farads) ---
c_nmos_off = 2.207181e-13
```

That is 220.72 fF, against 787.69 fF for the identical layout at 1.8 V. None of the drawn shapes
changed. The gate is only a capacitor when there is a channel underneath it to be the other plate;
take the bias away and the channel goes with it, leaving the much smaller depletion capacitance.

In a signal path, a capacitance that depends on the voltage across it is **distortion**: the
circuit's behaviour changes with the size of the signal going through it. So:

| | MIM | MOS | VPP |
|---|---|---|---|
| fF per µm² | 2.03 | 7.87 | 0.91 |
| linear? | yes | **no** | yes |
| extra mask? | yes | no | **no** |
| sits above the transistors? | yes | no | partly |

MOS capacitors are excellent for **supply decoupling**, where the voltage never moves and
distortion doesn't matter, and every chip you own uses them that way by the million. They are the
wrong choice for a filter.

## Smaller inductors

You may be tempted to shrink the resonator in `tank.spice` by picking a smaller inductor. There
isn't one. `ind_03_90` is the smallest of the three models SkyWater ships, none of them has a
width or turn-count parameter, and no drawn cell in the PDK's GDS carries their names. You can
check the GDS yourself:

```bash
cat > /tmp/cells.py <<'PY'
import pya
ly = pya.Layout()
ly.read("/foss/pdks/sky130A/libs.ref/sky130_fd_pr/gds/sky130_fd_pr.gds")
names = [c.name for c in ly.each_cell()]
print(len(names), "cells")
print(len([n for n in names if "ind" in n.lower()]), "with 'ind' in the name")
print([n for n in names if "coil" in n.lower()])
PY
klayout -b -r /tmp/cells.py
```

```
290 cells
0 with 'ind' in the name
['sky130_fd_pr__rf_test_coil1', 'sky130_fd_pr__rf_test_coil2', 'sky130_fd_pr__rf_test_coil3']
```

None of the 290 cells is one of the three modelled inductors. The GDS does contain three drawn
spirals, the `rf_test_coil` cells, but they are separate test structures with their own names and
characterisation, and the smallest is 150.020 × 145.040 µm
([Inductors on a chip](../../../docs/guide/the-inductor-problem.md) has all three). SkyWater
characterised three spirals and gave you the measurements; drawing one that matches a model is
your problem. That is a fair summary of on-chip inductors in general.

## Questions to argue about

- The area column in `check_cap.py` counts the MIM plate only. A MIM capacitor sits on metal 3 and
  above, so the transistors underneath it are still usable, and you could argue it costs no device
  area at all. A MOS capacitor definitely does. How would you price them against each other
  fairly, and does your answer change if the block is limited by routing rather than by devices?
- The tank's peak impedance is 250.13 Ω and the inductor's Q at 2.4 GHz is 10.86. Work out the
  relationship, then decide whether a better capacitor could have helped.
