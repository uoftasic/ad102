# One good answer — read this after yours passes

```
four identical units, W = 1 um, L = 28 um, in series from vdd to ground,
tap taken between the first and the second counting up from ground.

  nominal tap   0.450000 V   exact
  sigma            2.7052 mV
  drawn area     112.00 um^2
```

## The two failures the shipped divider has are not the same kind of failure

Accuracy and precision are different currencies and they are bought in
different shops. That is the whole lab.

**The +9.04 % nominal error is systematic.** It is identical on every die,
every wafer and every lot. It comes from Lab 01's 378.2448 Ω of end
resistance, which every device pays once regardless of how long it is drawn:

$$\frac{R_6}{R_6 + R_{18}} = \frac{378.24 + 6 \times 317.22}{(378.24 + 6 \times 317.22)+(378.24 + 18 \times 317.22)} = 0.27260$$

against the 0.25 you wanted. Making the devices bigger does not help; making
them *the same* does. Four identical units in series put the same overhead in
every branch, so the ratio becomes a ratio of **counts** — one unit out of
four — and every per-device error, known or unknown, divides out. The
measured nominal is `0.450000 V`, exactly, and it costs nothing.

**The σ error is statistical.** It differs from die to die, it averages to
zero, and it obeys one law:

$$\frac{\sigma_R}{R} = \frac{0.03552}{\sqrt{W L}}$$

— straight off the `res_high_po` model card as `body_pelgrom`. There is no
clever topology for this one. You buy it with area, at four times the area per
factor of two, forever.

## The dead end: unit devices do not help σ

This is the part worth arguing about, because the folklore says otherwise.

`mismatch.spice` builds the same 3:1 divider twice out of exactly 24 µm² of
poly — once as one short device and one long one, once as four identical
units. The nominal values are wildly different. The spreads are not:

```
3:1  one L=6 and one L=18        24 um^2 total  1.309327 V   5.6433 mV
3:1  four identical L=6 units    24 um^2 total  1.350000 V   5.7290 mV
```

**5.6433 against 5.7290 — a 1.5 % difference, where 200 samples only pin σ
down to ±5 %.** Those are the same number. Segmenting a resistor into unit
cells bought exactly nothing in random mismatch, and the algebra says it never
will: for independent per-device errors, σ of a ratio depends on total area
and on nothing else about how you carved it up.

So why does every analog textbook tell you to use unit devices in a common
centroid?

Because **this simulation contains only random mismatch.** Real wafers also
have *gradients* — oxide thickness, implant dose and temperature all vary
smoothly across a die, so two devices ten micrometres apart are more alike
than two devices a millimetre apart, and a device on the left of a pair sits
in a systematically different environment from the one on the right. Unit
devices interleaved in a common-centroid pattern cancel the linear part of
that gradient. It is a real and large effect and it is the main reason the
technique exists.

`AGAUSS` knows nothing about where your devices are, because your netlist does
not say. **If you set out to prove common-centroid layout helps by running
Monte Carlo in ngspice, you will measure exactly zero benefit, and you will be
measuring the model, not the silicon.** Knowing which effects your simulator
contains is not a detail; it is the difference between verification and
reassurance.

## Squeezing it further

112 µm² has margin. σ scales as $1/\sqrt{L}$, so $L = 22$ gives
$3.0332$ mV — just over the 3.0 mV budget — and $L = 25$ or so is about the
real edge. Whether you would ship a design sitting 1 % inside a σ budget is a
question about how much you trust the model's `body_pelgrom`, which was
extracted from a finite number of real wafers and quoted to four figures.

Also worth trying: **width**. Every unit here is 1 µm wide. Area is what σ
cares about, so `W=2 L=14` has the same 28 µm² and the same σ — but half the
resistance, twice the current, and (Lab 01, part C) a sheet resistance closer
to the flat part of the curve. There is no single right answer, which is why
the grader checks area and not shape.

## What to argue about

- The three constraints in `check_mm.py` are 0.2 %, 3.0 mV and 150 µm². Where
  would those numbers come from in a real project, and which one would you
  expect to be handed to you rather than chosen?
- σ of the tap is 2.7 mV on a 450 mV output — about 0.6 %. If this divider set
  the reference for an ADC, how many bits would that cost you, and would you
  rather spend the area or add a trim?
- The 1 µm² resistor in part A misses the Pelgrom prediction by 27 % and the
  64 µm² one by 10 %. Both are the same device. What does that tell you about
  quoting a single mismatch coefficient for a device family?
