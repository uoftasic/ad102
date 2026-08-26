# Lab 04 — Two resistors that disagree

Writeup: [`docs/labs/lab-04-two-resistors-that-disagree-overview.md`](../../docs/labs/lab-04-two-resistors-that-disagree-overview.md)

Labs 01–03 assumed a resistor is worth what the geometry says. Two resistors
drawn from the same mask, side by side on the same die, are not.

Runs inside the workbench `hpretl/iic-osic-tools:2026.04` — ngspice **46**,
PDK **sky130A**. No environment setup.

```bash
cd labs/lab-04-two-resistors-that-disagree
make            # about five and a half minutes, silent throughout
```

**This is the slow lab.** Each deck loads 12 MB of SKY130 model cards (~60 s)
and then re-evaluates the entire netlist two hundred times, once per imaginary
die (~100 s). Two decks. It prints nothing while it works.

## Files

| File | What it is |
|---|---|
| `spice/mismatch.spice` | Four resistor sizes and four dividers, 200 dies each, plus a nominal die with mismatch switched off. |
| `spice/my_divider.spice` | **The file you edit.** A 0.45 V tap that has to be accurate, precise *and* small. |
| `src/check_mm.py` | The grader. Collects the dies, reports mean and σ, and reads your geometry back out of your deck. |
| `solutions/` | One good answer and the argument about it. After yours passes. |

## How Monte Carlo works here

SKY130's device models carry a mismatch term gated by one parameter:

```
.param mc_mm_switch=1
```

With it on, every device instance draws its own `AGAUSS()` sample when the
netlist is evaluated. `mc_source` re-evaluates the netlist — a fresh imaginary
die off the same imaginary wafer — and `alterparam mc_mm_switch=0` followed by
`mc_source` gives you the nominal die with no mismatch at all.

`setseed 1` makes the whole sequence reproducible. **Your two hundred dies are
the same two hundred dies, in the same order, as the ones in the writeup**, so
every number below matches to the digit. Statistics you cannot reproduce are
not evidence.

## The trap in the loop

The Monte Carlo loop counter has to be created **before** the first
`mc_source`:

```
setseed 1
let run = 0          <- here
dowhile run < 200
  mc_source
  ...
```

`mc_source` discards the vectors belonging to the previous analysis, and a
counter created after one has run goes with them. The symptom is this, buried
in a wall of model warnings:

```
Warning from checkvalid: vector run is not available or has zero length.
Error: RHS "run + 1" invalid
```

after which the loop quietly stops at **one** die and every standard deviation
you compute is zero. `make` prints the operating-point count so you can see at
a glance whether you got 201 or 2.

## Reference numbers (ngspice 46, sky130A, tt corner, seed 1, 200 dies)

**Golden**, because of `setseed`.

```
one resistor        1 um^2  sigma/R 2.5852 %      4 um^2  1.6046 %
                   16 um^2          0.8391 %     64 um^2  0.4007 %
1:1 divider   0.84 um^2 devices  nominal 0.900000 V  sigma 25.0787 mV
1:1 divider     40 um^2 devices  nominal 0.900000 V  sigma  3.2321 mV
3:1  one L=6 + one L=18          nominal 1.309327 V  sigma  5.6433 mV
3:1  four identical L=6 units    nominal 1.350000 V  sigma  5.7290 mV
```
