# Reference sizing — read this after your own numbers pass

## The three answers

```
C1  250 fF MIM      side 11.0170 um     (naive 11.1803 -> 257.36 fF, +2.94 %)
C2   20 fF MIM      side  3.0030 um     (naive  3.1623 ->  22.07 fF, +10.35 %)
C3  250 fF MOS      side  5.6333 um     -- the naive answer, and it passes
```

## Why C3 passed and the other two did not

All three sizings made exactly the same mistake: they used
`area = C / density` and threw the edge term away. The mistake cost 2.94 % on
C1, 10.35 % on C2, and 0.31 % on C3.

The edge term is a **perimeter** effect, so what matters is perimeter over
area, which for a square of side $s$ is $4/s$ — it grows as the plate shrinks.
That alone explains C1 versus C2: same recipe, plate **3.7× smaller**, error
**3.5× bigger**.

C3 is different in kind. Its dielectric is **gate oxide**, the thinnest
insulator anywhere in the process, so its area term is about four times the
MIM's while its edge term is dominated by the gate-to-source and
gate-to-drain overlaps, which are small. A capacitor whose area term is huge
has almost nothing left over for its edges to matter.

**The rule to carry away:** the fringe correction on a plate capacitor is
roughly `edge / (area × s)`. Big plates in a low-density technology are nearly
pure area; small plates in a low-density technology are not. Decide which one
you are drawing before you decide whether you can ignore the fringe.

## Why anybody uses MIM at all, given the numbers

The MOS capacitor is 3.9× denser and it is *free* — no extra mask, it is
literally a transistor. And part D of `picofarad.spice` is the reason nobody
uses it for signal work:

```
--- D. the same MOS cap with the gate at 0 V (farads) ---
c_nmos_off = 2.207181e-13
```

**220.72 fF, against 787.69 fF for the identical layout at 1.8 V.** Nothing
about the drawn shapes changed. The gate is only a capacitor when there is a
channel underneath it to be the other plate; take the bias away and the
channel goes with it, and what is left is the much smaller depletion
capacitance.

A capacitance that depends on the voltage across it is, in a signal path,
**distortion** — the circuit's behaviour changes with the size of the signal
going through it. So:

| | MIM | MOS | VPP |
|---|---|---|---|
| fF per µm² | 2.03 | 7.87 | 0.91 |
| linear? | yes | **no** | yes |
| extra mask? | yes | no | **no** |
| sits above the transistors? | yes | no | partly |

MOS capacitors are excellent for **supply decoupling**, where the voltage
never moves and nobody cares about distortion, and they are used that way by
the million on every chip you own. They are wrong for a filter.

## The dead end worth documenting

You will be tempted to shrink the resonator in `tank.spice` by picking a
smaller inductor. There are no smaller inductors. `ind_03_90` is the smallest
of the three models SkyWater ships, there is no width or turn-count parameter
on any of them, and — check for yourself — there is no drawn cell for them in
the PDK's GDS either:

```bash
klayout -b -r - <<'PY'
import pya
ly = pya.Layout()
ly.read("/foss/pdks/sky130A/libs.ref/sky130_fd_pr/gds/sky130_fd_pr.gds")
print(len([c for c in ly.each_cell() if "ind" in c.name.lower()]), "inductor cells")
PY
```

```
0 inductor cells
```

290 cells in that GDS and not one of them is an inductor. SkyWater
characterised three spirals and gave you the measurements; drawing one is
your problem. That is a fair summary of the state of on-chip inductors
generally.

## What to argue about

- The area column in `check_cap.py` counts the MIM plate only. A MIM capacitor
  sits on metal 3 and above, so the transistors underneath it are still usable
  — arguably it costs no device area at all. A MOS capacitor definitely does.
  How would you price them against each other honestly, and does your answer
  change if the block is routing-limited rather than device-limited?
- The tank's peak impedance is 250.13 Ω and the inductor's Q at 2.4 GHz is
  10.86. Work out the relationship, then decide whether a better capacitor
  could have helped.
