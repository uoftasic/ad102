# Lab 04 — Two resistors that disagree

Full runnable package: [`labs/lab-04-two-resistors-that-disagree/`](https://github.com/uoftasic/ad102/tree/main/labs/lab-04-two-resistors-that-disagree).

**Question this lab answers:** *I drew two resistors from the same mask, five
micrometres apart, on the same die. How alike are they?*

## Prerequisites

- [Lab 01 — A resistor you designed](labs/lab-01-a-resistor-you-designed-overview.md).
  You will need its 378.2448 Ω.
- Labs [02](labs/lab-02-how-big-is-a-picofarad-overview.md) and
  [03](labs/lab-03-a-time-constant-in-silicon-overview.md) help but are not required.
- You are in `labs/lab-04-two-resistors-that-disagree/`

## Objectives

- Run a reproducible Monte Carlo mismatch simulation and know what each run is
- Verify Pelgrom's law — $\sigma \propto 1/\sqrt{\text{area}}$ — on measured
  data, and find where it fails
- Separate **accuracy** (the nominal is wrong) from **precision** (the spread
  is wide), and know which one area can buy
- Explain why every analog block on a die is built out of identical unit
  cells, and why this simulation cannot show you the main reason

## Before you start: the belief you are about to lose

Everything in Labs 01–03 rested on an assumption so quiet you probably did not
notice making it: **that a device is worth what its geometry says.** You sized
a resistor to 2200 Ω and the simulator returned 2200.006 Ω, and that felt like
the end of the story.

It is the end of the *design* story. The manufacturing story is that the strip
you drew is 1 µm wide on the mask, and the finished silicon is 1 µm wide plus
or minus whatever the lithography, the etch, the implant dose and the anneal
felt like doing that day, and that number is slightly different for every
device on the die. A resistor's value is a random variable. So is every other
device parameter on a chip.

This is not a defect you can design out. It is the physics of building a
million things at once, and analog design is largely the craft of arranging
for the randomness not to matter.

## Theory (short)

Random variation between two nominally identical devices side by side follows
**Pelgrom's law**: the fractional mismatch falls as the square root of the
device area.

$$\frac{\sigma_R}{R} = \frac{A_R}{\sqrt{W L}}$$

The reason is averaging. Whatever is random — dopant atoms, grain boundaries,
edge roughness — a bigger device contains more of it, and more samples of a
random thing average better. Four times the area, half the spread.

SKY130 states $A_R$ for you. Read it off the model card:

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

The first two lines are the coefficients; the last three are the model using them.

Two coefficients, because a resistor has two parts that mismatch
independently — the body, and the contact heads that Lab 01 measured at
378.2448 Ω.

## Procedure

```bash
cd labs/lab-04-two-resistors-that-disagree
make
```

**About two and a half minutes, silent throughout.** Two decks, each loading the
SKY130 model cards (~55 s) and then re-evaluating the whole netlist two hundred
times, once per imaginary die (~23 s for the bigger of the two). Measured twice on
the pinned image: 106 s and 128 s. Model loading, not Monte Carlo, is most of it.

### Step 1 — what one Monte Carlo run is

`spice/mismatch.spice` turns the mismatch models on with one line:

```
.param mc_mm_switch=1
```

Every device instance then draws its own `AGAUSS()` sample when the netlist is
evaluated. The control block calls `mc_source` — re-evaluate the netlist,
which is to say *fabricate a different die* — then one `op`, two hundred
times. Afterwards it sets `mc_mm_switch=0` and does it once more to get the
nominal die, the one with no mismatch at all.

`setseed 1` fixes the sequence, so **your two hundred dies are the same two
hundred dies as the ones on this page**, in the same order.

- **Try this:** confirm the count before you trust any statistic.
- **What you should see:**

  ```
  operating points (200 dies + 1 nominal) : 201
  ```

- **Why an engineer cares:** a Monte Carlo result you cannot reproduce is not
  a measurement, it is an anecdote. Seeding it costs one word and turns "about
  5.6 mV" into a number you can put in a table and have someone else check.

### Step 2 — Pelgrom's law, and where it stops working

Part A puts 1 µA through four single resistors of areas 1, 4, 16 and 64 µm².

- **Try this:** predict all four spreads from `body_pelgrom / sqrt(W*L)`
  before you look.
- **What you should see:**

  ```
    A. one resistor, four sizes -- does sigma halve when area quadruples?
      geometry          area    sigma/R   0.03552/sqrt(A)   ratio to previous
      W=1  L=1            1     2.5852%           3.5520%                 --
      W=1  L=4            4     1.6046%           1.7760%              1.611
      W=2  L=8           16     0.8391%           0.8880%              1.912
      W=4  L=16          64     0.4007%           0.4440%              2.094
  ```

  The last column is the law, and for the three larger devices it is there:
  **1.912 and 2.094 against a predicted 2.000**, on 200 samples that only pin
  σ down to ±5 % anyway.

  The 1 µm² device is not there. It should have scattered by 3.55 % and
  scattered by 2.59 % — **27 % less than predicted**, in the direction of
  being *better* than the law allows.

- **Why an engineer cares:** work out where the extra steadiness came from.
  Lab 01 measured that resistor: at $W = 1$, $L = 1$ its total resistance is
  695.46 Ω, of which **378.24 Ω is contact head, not body** — 54 % of the
  device is not the thing `body_pelgrom` describes. The heads have their own
  coefficient (`head_pelgrom`, and a different area to average over), and on
  this device they dominate.

  So: a mismatch coefficient describes *a device parameter*, not a device. The
  moment your geometry stops looking like the geometry it was extracted on,
  the single-number version of the law stops applying. This is exactly the
  same trap as Lab 01's naive $R = R_\square L/W$, and it is exactly the same
  fix — measure the thing you are actually going to build.

### Step 3 — the same divider, forty-eight times the area

Part B builds a 1:1 divider twice: once from two 0.84 µm² devices, once from
two 40 µm² ones. Same schematic. Same ratio. Same everything except size.

- **What you should see:**

  ```
    1:1  two devices W=0.42 L=2    0.84 um^2 each   0.900000 V  25.0787 mV
    1:1  two devices W=2 L=20        40 um^2 each   0.900000 V   3.2321 mV
  ```

  Both nominals are **0.900000 V, exactly**. Both are perfectly accurate. One
  of them is eight times less precise.

- **Why an engineer cares:** 25 mV of scatter on a 900 mV node is 2.8 %, which
  is roughly five bits of an ADC's worth of reference error, on a circuit
  whose schematic is beyond reproach. And the fix is the least clever thing in
  engineering: draw it bigger. 47.6× the area bought **7.76×** the precision.
  The area law alone predicts $\sqrt{47.6} = 6.90$, so the small pair is about
  12 % worse than area explains — it is 0.42 µm wide, below the 0.69 µm knee
  Lab 01 found in part C, and it also pays head mismatch, which does not scale
  with $WL$ at all.

  This is the real reason analog blocks look enormous next to digital ones.
  Not because analog designers are wasteful — because **precision has a price
  in square micrometres and there is no discount.**

### Step 4 — the same ratio, the same area, two ways of drawing it

Part C is the heart of the lab. A 3:1 divider, built out of exactly 24 µm² of
poly, twice:

- `tc` — one device of $L = 6$ and one of $L = 18$. The obvious drawing.
- `td` — four identical $L = 6$ units in series, tapped after the first.

Same ratio on paper. Same area. Same material.

- **Try this:** predict both the nominal and the spread for each, then commit
  to which will be better and why.
- **What you should see:**

  ```
    3:1  one L=6 and one L=18        24 um^2 total  1.309327 V   5.6433 mV
    3:1  four identical L=6 units    24 um^2 total  1.350000 V   5.7290 mV

      the 3:1 ratio you asked for is 1.350000 V.
        two devices  : 1.309327 V  (-3.01 %)
        four units   : 1.350000 V  (+0.00 %)
      and the spread is 5.6433 mV against 5.7290 mV -- a 1.5 % difference,
      where 200 samples only pin sigma down to +/- 5.0 %. Those are the same number.
  ```

  Two results, and both are surprising in opposite directions.

  **The nominals differ by 3.01 %, for free.** The two-device version is
  simply wrong, and it is wrong the same way on every die forever. Lab 01
  explains it in one line: every resistor pays 378.2448 Ω of end resistance
  regardless of length, so

  $$\frac{R_6}{R_6+R_{18}} = \frac{378.24 + 6(317.22)}{8369.76} = 0.27260$$

  and not 0.25. Build both branches out of the *same unit* and that overhead
  appears identically in both, the ratio becomes a ratio of **counts** — one
  unit out of four — and it divides out exactly. Not approximately. The
  measured nominal is `1.350000`.

  **The spreads do not differ at all.** 5.6433 against 5.7290 is 1.5 % apart,
  and 200 samples cannot resolve σ better than $1/\sqrt{2N} = 5$ %. Chopping
  the resistor into unit cells bought **nothing** in random mismatch, and the
  algebra says it never will: for independent per-device errors, the σ of a
  ratio depends on total area and on nothing else about how you carved it up.

- **Why an engineer cares:** you have just separated the two things "matching"
  usually means, and they turn out to be bought in different shops.

  | | what fixes it | what it costs |
  |---|---|---|
  | **accuracy** — the nominal is wrong | identical unit devices | nothing |
  | **precision** — the spread is wide | area | area, at 4× per factor of 2 |

  The free one is free. **Build every ratio you care about out of identical
  unit cells**, always, because it costs you nothing and it removes an entire
  class of error including the ones nobody has told you about yet.

### Step 5 — the dead end, and why the textbooks disagree with your simulation

Every analog textbook tells you to lay matched devices out as interleaved unit
cells in a common centroid. You have just measured that unit cells do nothing
for σ. Both statements are true, and the gap between them is worth more than
either.

**This simulation contains only random, per-device mismatch.** Real wafers
also have **gradients** — oxide thickness, implant dose and temperature vary
smoothly across a die, so two devices ten micrometres apart are more alike
than two a millimetre apart, and the left member of a pair sits in a
systematically different environment from the right one. Unit cells
interleaved in a common centroid cancel the linear part of that gradient. It
is a large, real effect, and it is the main reason the technique exists.

`AGAUSS` knows nothing about where your devices are, because **your netlist
does not say where they are.** Position enters a design at layout, and a
SPICE netlist has no coordinates in it.

> **Do not go looking for the gradient effect in ngspice.** You can build the
> interleaved version, run ten thousand dies, and you will measure exactly
> zero benefit — not because common-centroid layout does not work, but because
> you would be measuring the model rather than the silicon. Knowing which
> effects your simulator contains is not a detail. It is the whole difference
> between verification and reassurance.

Post-layout extraction, which [AD104](https://uoftasic.com/ad104/) gets to,
does not fix this either — it adds parasitic $R$ and $C$ from your actual
geometry, not process gradients. Gradient matching is checked by test chips
and by layout review, and that is one of the honest limits of simulation.

### Step 6 — your turn

`spice/my_divider.spice` has to put **0.4500 V** on `tap` from a 1.8 V supply,
using `sky130_fd_pr__res_high_po`, and satisfy all three of:

1. nominal within **0.2 %** of 0.4500 V,
2. σ at most **3.0 mV** over 200 dies,
3. total drawn area under **150 µm²**.

Use as many devices as you like; keep the node called `tap` and the supply
called `vdd`, and the grader will read your geometry back out of the file.

It ships with the divider everybody draws first — one resistor three squares'
worth on top, one square's worth underneath — and it fails two of the three:

```
  1. nominal tap   0.490673 V    target 0.450000 V ( +9.04 %)      FAIL
  2. sigma           5.9285 mV   budget 3.0000 mV                    FAIL
  3. drawn area       24.00 um^2 budget    150 um^2                 PASS
```

Two failures, two entirely different fixes. One of them is free.

## What is not a bug

**Two to two and a half minutes of silence.** Two decks, each about 55 s of model
loading plus 200 operating points on top. If you were expecting the model cards to
be the fast part, they are not — they are the slow part.

**The loop counter must exist before the first `mc_source`.** `mc_source`
discards the previous analysis's vectors, and a counter created after an
analysis has run goes with them. Get it wrong and you see this, buried in the
usual wall of model warnings:

```
Warning from checkvalid: vector run is not available or has zero length.
Error: RHS "run + 1" invalid
```

after which the loop stops at **one** die and every σ you compute is zero —
silently, with exit status 0. That is why `make` prints the operating-point
count first: you are looking for **201**, and if you see **2** you have found
this. The shipped decks put `let run = 0` immediately after `setseed 1`, which
is before anything has been simulated.

**28,280 `unrecognized parameter (...) - ignored` lines**, of which 5,656 are
`(sw_et)`. Explained in Lab 01 — one set of model cards, several simulator
dialects. Two hundred re-evaluations of the netlist means two hundred repeats of
the whole wall, and `results/mismatch.log` is 1.8 MB as a result. `make` sends it
to the log rather than your terminal.

## Expected results

**Golden** — `setseed 1` makes Monte Carlo reproducible.

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

## Where this goes next

You have now priced all three passives, put two of them in a circuit, and
found out what stops the answer being exactly what you drew. The parts of a
chip that are *not* linear — the diode and the MOSFET, and the regions they
operate in — are [AD103](https://uoftasic.com/ad103/), which picks the story
up in XSchem. Drawing any of this as real polygons, with a DRC deck and an LVS
check telling you whether you drew what you meant, is
[AD104](https://uoftasic.com/ad104/).

Two things from this lab travel with you into both. Every ratio you ever care
about is built from identical unit cells. And precision is bought in square
micrometres, at four times the area per factor of two, in every technology
there has ever been.

## Links

- [Lab package](https://github.com/uoftasic/ad102/tree/main/labs/lab-04-two-resistors-that-disagree)
- [`solutions/README.md`](https://github.com/uoftasic/ad102/blob/main/labs/lab-04-two-resistors-that-disagree/solutions/README.md)
  — one good answer, and why unit devices do nothing for σ in this simulator
- Previous lab: [Lab 03 — A time constant in silicon](labs/lab-03-a-time-constant-in-silicon-overview.md)
