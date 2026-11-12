# Lab 04: Two resistors that disagree

You'll see the same resistor move at every process corner while a ratio of two resistors stays
fixed. Then you'll run a reproducible Monte Carlo mismatch simulation, check Pelgrom's law on
your own data and find where it fails, and separate **accuracy** (the nominal value is wrong)
from **precision** (the spread is wide). The lab ends with a divider you have to make accurate,
precise and small at the same time.

Package: [`labs/lab-04-two-resistors-that-disagree/`](https://github.com/uoftasic/ad102/tree/main/labs/lab-04-two-resistors-that-disagree)

## Before you start

- Finish [Lab 01](labs/lab-01-a-resistor-you-designed-overview.md); you'll need its 378.2448 Ω
  of end resistance. [Lab 02](labs/lab-02-how-big-is-a-picofarad-overview.md) and
  [Lab 03](labs/lab-03-a-time-constant-in-silicon-overview.md) help but are not required.
- Read [Process corners](guide/the-value-you-drew-is-not-what-you-get.md) and
  [Matching and Pelgrom's law](guide/matching-beats-accuracy.md).
- Open a terminal in the workbench and go to the lab folder:

  ```bash
  cd /foss/designs/modules/ad102/labs/lab-04-two-resistors-that-disagree
  ```

  This lab needs no environment setup.

**Time:** about 2 hours. The Monte Carlo runs are silent throughout. A full `make` takes between
about 30 seconds and two minutes, depending on your machine (the Makefile records 106 s and
128 s on the pinned image).

Labs 01–03 assumed that a device is worth what its geometry says: you sized a resistor to 2200 Ω
and the simulator returned 2200.006 Ω. That is the end of the design story, but not of the
manufacturing story. The strip you drew is 1 µm wide on the mask, and the finished silicon is
1 µm wide plus or minus whatever the lithography, etch, implant dose and anneal did that day, and
that is slightly different for every device on the die. A resistor's value is a random variable,
and so is every other device parameter on a chip. You cannot design that out; it comes from
building a million things at once. Much of analog design is arranging for the randomness not to
matter.

## Part 1: Process corners

The corners deck in `labs/passives-decks` is the one quoted on the two guide pages. It builds one
circuit three times, once per corner (`ll`, `tt`, `hh`), changing only one word on the `.lib`
line.

1. Go to the `passives-decks` package and run the three corners:

   ```bash
   cd ../passives-decks
   make corners
   ```

2. Read the three `absolute (moves)` blocks. Divide the `ll` and `hh` values of `r_a` by the
   `tt` value.

3. Read the three `RC corner frequency` lines. Before you compare them, work out what the `hh`
   corner should do to the corner frequency: $R$ goes up by 1.125 and the MIM capacitance by
   1.13207, so $f$ should scale by $1/(1.125 \times 1.13207)$.

4. Read the three `ratio and divider (do not move)` blocks.

5. Go back to the lab folder:

   ```bash
   cd ../lab-04-two-resistors-that-disagree
   ```

**You should see:** `r_a` at 3106.637, 3550.443 and 3994.248 Ω, which is 0.875000 and 1.125000 of
typical. Corner frequencies of 282.935, 215.410 and 169.052 MHz; your prediction for `hh` is
$1/1.2736 = 0.7852$, against a simulated 0.7848. And in all three corners:

```
ratio = 3.680396e+00
divider = 3.845828e-01
```

The absolute values moved by ±12.5 %, the RC corner frequency by a 1.67 : 1 range, and the ratio
and divider did not move in any printed digit.
[Matching and Pelgrom's law](guide/matching-beats-accuracy.md#why-the-ratio-holds) explains why.

## Part 2: Run the Monte Carlo

Corners shift every device together. Mismatch moves devices apart, and needs a different switch.
`spice/mismatch.spice` turns the SKY130 mismatch models on with one line:

```
.param mc_mm_switch=1
```

With it on, every device instance draws its own `AGAUSS()` sample when the netlist is evaluated.
The control block calls `mc_source`, which re-evaluates the netlist (in effect, fabricates a
different die), then runs one `op`, two hundred times. Then `alterparam mc_mm_switch=0`
followed by one more `mc_source` gives the nominal die, with no mismatch at all. `setseed 1` fixes the random sequence, so
your two hundred dies are the same two hundred dies as on this page, in the same order.

1. Run the lab:

   ```bash
   make
   ```

   It ends in `FAIL`; you fix that in Part 6. Leave the output in your terminal.

2. Before you trust any statistic, check the count at the top of the output.

**You should see:**

```
operating points (200 dies + 1 nominal) : 201
```

A Monte Carlo result you cannot reproduce is an anecdote, not a measurement. Seeding it costs one
word, and turns "about 5.6 mV" into a number you can put in a table and have someone else check.

## Part 3: Pelgrom's law

Part A of the deck puts 1 µA through four single resistors with areas of 1, 4, 16 and 64 µm².

1. Read the mismatch coefficients off the model card:

   ```bash
   grep pelgrom /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_high_po.model.spice
   ```

   ```
   + body_pelgrom = 0.03552
   + head_pelgrom = 0.0761
   + rbody_match = {body_pelgrom/sqrt(w*l*mult)*MC_MM_SWITCH*AGAUSS(0,1.0,1)}
   + rend_match = {head_pelgrom/sqrt((w+0.525)*num_con_row*mult)*MC_MM_SWITCH*AGAUSS(0,1.0,1)}
   + res_match = {(body_pelgrom/sqrt(w*l*mult))*MC_MM_SWITCH*AGAUSS(0,1.0,1)}
   ```

   The first two lines are the coefficients; the last three are the model using them. There are
   two coefficients because a resistor has two parts that mismatch independently: the body, and
   the contact head.

2. Predict all four spreads from `body_pelgrom / sqrt(W*L)`.

3. Find table A in the checker's output.

4. (Optional) The guide page's 1 × 1 µm against 10 × 10 µm comparison, with a different seed, is
   in `labs/passives-decks`. To reproduce it:

   ```bash
   cd ../passives-decks
   make mismatch
   cd ../lab-04-two-resistors-that-disagree
   ```

   It ends with `100x the area bought 8.38x better matching`.

**You should see:**

```
  A. one resistor, four sizes -- does sigma halve when area quadruples?
    geometry          area    sigma/R   0.03552/sqrt(A)   ratio to previous
    W=1  L=1            1     2.5852%           3.5520%                 --
    W=1  L=4            4     1.6046%           1.7760%              1.611
    W=2  L=8           16     0.8391%           0.8880%              1.912
    W=4  L=16          64     0.4007%           0.4440%              2.094
```

The last column tests the law, and for the three larger devices it holds: 1.912 and 2.094
against a predicted 2.000, from 200 samples that only pin σ down to ±5 % anyway.

The 1 µm² device does not follow it. It should have scattered by 3.55 % and scattered by 2.59 %,
27 % less than predicted, so it is *better* than the law allows.

To see why, go back to Lab 01, Part 6. At $W = 1$, $L = 1$ the resistor's total is 695.46 Ω,
and 299.89 Ω of that, 43 %, is contact head, not body. `body_pelgrom` describes only the body.
The head has its own coefficient (`head_pelgrom`, averaged over a different quantity), and on this
device its contribution to σ is about as large as the body's
([the worked example](guide/matching-beats-accuracy.md#worked-example-predicting-the-monte-carlo)
gets 13.067 Ω from the head and 14.051 Ω from the body).

So a mismatch coefficient describes a device *parameter*, not a whole device. When your geometry
stops looking like the geometry the coefficient was extracted on, the single-number version of
the law stops applying. This is the same trap as Lab 01's naive $R = R_\square L/W$, with the
same fix: measure the thing you are actually going to build.

## Part 4: The same divider at 48 times the area

Part B builds a 1:1 divider twice: once from two 0.84 µm² devices and once from two 40 µm² ones.
The schematic and ratio are the same; only the size changes.

1. Find the two `1:1` lines in the checker's `B and C` table.

**You should see:**

```
    1:1  two devices W=0.42 L=2    0.84 um^2 each   0.900000 V  25.0787 mV
    1:1  two devices W=2 L=20        40 um^2 each   0.900000 V   3.2321 mV
```

Both nominals are exactly 0.900000 V, so both are perfectly accurate. One is eight times less
precise than the other.

25 mV of scatter on a 900 mV node is 2.8 %, roughly five bits' worth of reference error in an
ADC, from a circuit whose schematic is correct. The fix is the least clever thing in engineering:
draw it bigger. 47.6 times the area bought 7.76 times the precision. Area alone predicts
$\sqrt{47.6} = 6.90$, so the small pair is about 12 % worse than area explains. It is 0.42 µm
wide, below the 0.69 µm point where Lab 01, Part 4 found the sheet resistance starts to change,
and it also pays head mismatch, which does not scale with $WL$ at all.

This is the main reason analog blocks look enormous next to digital ones: precision is paid for
in square micrometres.

## Part 5: One ratio drawn two ways

Part C builds a 3:1 divider from exactly 24 µm² of poly, twice:

- `tc`: one device of $L = 6$ and one of $L = 18$. This is the obvious drawing.
- `td`: four identical $L = 6$ units in series, tapped after the first.

They have the same ratio on paper, the same area and the same material.

1. Predict the nominal and the spread for each, and decide which will be better and why.

2. Find the two `3:1` lines and the summary below them.

**You should see:**

```
    3:1  one L=6 and one L=18        24 um^2 total  1.309327 V   5.6433 mV
    3:1  four identical L=6 units    24 um^2 total  1.350000 V   5.7290 mV

    the 3:1 ratio you asked for is 1.350000 V.
      two devices  : 1.309327 V  (-3.01 %)
      four units   : 1.350000 V  (+0.00 %)
    and the spread is 5.6433 mV against 5.7290 mV -- a 1.5 % difference,
    where 200 samples only pin sigma down to +/- 5.0 %. Those are the same number.
```

**The nominals differ by 3.01 %.** The two-device version is wrong, and wrong the same way on
every die. Lab 01 explains it: every resistor pays 378.2448 Ω of end resistance regardless of
length, so

$$\frac{R_6}{R_6+R_{18}} = \frac{378.24 + 6(317.22)}{8369.76} = 0.27260$$

and not 0.25. Build both branches from the *same unit* and that overhead appears equally in
both. The ratio becomes a ratio of **counts**, one unit out of four, and the overhead divides out
exactly. The measured nominal is `1.350000`.

**The spreads do not differ.** 5.6433 against 5.7290 mV is 1.5 % apart, and 200 samples cannot
resolve σ better than $1/\sqrt{2N} = 5$ %. Splitting the resistor into unit cells bought nothing
in random mismatch, and the algebra says it never will: for independent per-device errors, the σ
of a ratio depends on total area and nothing else about how you divided it up.

So "matching" usually means two different things, and you pay for them differently:

| | what fixes it | what it costs |
|---|---|---|
| **accuracy**: the nominal is wrong | identical unit devices | nothing |
| **precision**: the spread is wide | area | area, at 4× per factor of 2 |

Build every ratio you care about from identical unit cells. It costs nothing, and it removes a
whole class of error, including ones nobody has told you about yet.

> **What this simulation cannot show.** Every analog textbook says to lay matched devices out as
> interleaved unit cells in a common centroid, and you have just measured that unit cells do
> nothing for σ. Both are true. This simulation contains only random, per-device mismatch. Real
> wafers also have **gradients**: oxide thickness, implant dose and temperature vary smoothly
> across a die, so two devices ten micrometres apart are more alike than two a millimetre apart,
> and the left member of a pair sits in a systematically different environment from the right
> one. Interleaved unit cells in a common centroid cancel the linear part of that gradient. It is
> a large, real effect, and it is the main reason the technique exists.
>
> `AGAUSS` knows nothing about where your devices are, because your netlist does not say where
> they are; position enters a design at layout, and a SPICE netlist has no coordinates. If you
> build the interleaved version and run ten thousand dies, you will measure zero benefit, because
> you are measuring the model, not the silicon. Before you use a simulation to check a design
> decision, check that the simulator models the effect the decision is about.
>
> Post-layout extraction, which [AD104](https://uoftasic.com/ad104/) covers, does not fix this
> either: it adds parasitic $R$ and $C$ from your actual geometry, not process gradients.
> Gradient matching is checked with test chips and layout review, which is one of the real limits
> of simulation.

## Part 6: Design a 0.45 V divider

`spice/my_divider.spice` has to put **0.4500 V** on `tap` from a 1.8 V supply, using
`sky130_fd_pr__res_high_po`, and meet all three of these:

1. nominal within **0.2 %** of 0.4500 V,
2. σ at most **3.0 mV** over 200 dies,
3. total drawn area under **150 µm²**.

You can use as many devices as you like. Keep the node called `tap` and the supply called `vdd`;
the checker reads your geometry back out of the file.

The file ships with the divider everybody draws first: one resistor on top three times as long
as the one underneath (`L=18` and `L=6`, both `W=1`). The check in Part 2 failed two of the
three:

```
  1. nominal tap   0.490673 V    target 0.450000 V ( +9.04 %)      FAIL
  2. sigma           5.9285 mV   budget 3.0000 mV                    FAIL
  3. drawn area       24.00 um^2 budget    150 um^2                 PASS
```

1. Decide how to fix the nominal (Part 5) and how to fix σ (Parts 3 and 4).
2. Edit `spice/my_divider.spice`. Write `W` and `L` as plain microns, with no `u` suffix.
3. Re-run your divider and the checker:

   ```bash
   make mine check
   ```

**You should see:** all three checks marked `PASS`, then

```
PASS -- every number matches the reference run.
```

## Finishing

You are done when `make mine check` prints `PASS -- every number matches the reference run.`

`setseed 1` makes the Monte Carlo reproducible, so on the pinned image (ngspice-47, `sky130A`,
`tt` corner, seed 1, 200 dies) your numbers match these:

| | nominal | σ |
|---|---|---|
| 1 µm² resistor | 695.4646 Ω | 2.5852 % |
| 4 µm² resistor | 1647.124 Ω | 1.6046 % |
| 16 µm² resistor | 1468.119 Ω | 0.8391 % |
| 64 µm² resistor | 1370.854 Ω | 0.4007 % |
| 1:1 divider, 0.84 µm² devices | 0.900000 V | 25.0787 mV |
| 1:1 divider, 40 µm² devices | 0.900000 V | 3.2321 mV |
| 3:1, one L=6 + one L=18 | 1.309327 V | 5.6433 mV |
| 3:1, four identical L=6 units | 1.350000 V | 5.7290 mV |

After yours passes, read
[`solutions/README.md`](https://github.com/uoftasic/ad102/blob/main/labs/lab-04-two-resistors-that-disagree/solutions/README.md)
for one good answer and why unit devices do nothing for σ in this simulator.

Two results from this lab carry into everything after it: build every ratio you care about from
identical unit cells, and expect to pay for precision in square micrometres, at four times the
area per factor of two.

Next on the [Course path](README.md#course-path): read
[From schematic to cross-section](guide/from-schematic-to-cross-section.md), then do the
[Capstone: Defend a floor plan](labs/capstone-floor-plan-overview.md).

## Expected warnings and delays

**Silence.** Each of the two decks loads the SKY130 model cards (about 55 s on the pinned image)
and then evaluates 200 operating points (about 23 s for the bigger of the two), printing nothing
while it works. Most of the time is model loading, not Monte Carlo.

**The loop counter must exist before the first `mc_source`.** `mc_source` discards the previous
analysis's vectors, and a counter created after an analysis has run goes with them. If you get
this wrong, you see the following, buried in the usual model warnings:

```
Warning from checkvalid: vector run is not available or has zero length.
Error: RHS "run + 1" invalid
```

After that the loop stops at one die and every σ you compute is zero, silently, with exit status
0. That is why `make` prints the operating-point count first: you are looking for 201, and if you
see 2, this is the cause. The shipped decks create the counter immediately after `setseed 1`,
before anything has been simulated:

```
setseed 1
let run = 0          <- here
dowhile run < 200
  mc_source
  ...
```

**28,280 `unrecognized parameter (...) - ignored` lines**, of which 5,656 are `(sw_et)`. Lab 01
explains these: one set of model cards, written for several simulators. Two hundred
re-evaluations of the netlist repeat the whole block two hundred times, so `results/mismatch.log`
is 1.8 MB. `make` sends it to the log rather than to your terminal.
