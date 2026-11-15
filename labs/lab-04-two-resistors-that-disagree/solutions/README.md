# One good answer (read this after yours passes)

```
four identical units, W = 1 um, L = 28 um, in series from vdd to ground,
tap taken between the first and the second counting up from ground.

  nominal tap   0.450000 V   exact
  sigma            2.7052 mV
  drawn area     112.00 um^2
```

## The shipped divider's two failures

The shipped divider fails on accuracy and on precision, and the whole lab turns on the fact that
you pay for those two in different ways.

**The +9.04 % nominal error is systematic.** It is the same on every die, every wafer and every
lot, because it comes from Lab 01's 378.2448 Ω of end resistance, which every device pays once
whatever its length:

$$\frac{R_6}{R_6 + R_{18}} = \frac{378.24 + 6 \times 317.22}{(378.24 + 6 \times 317.22)+(378.24 + 18 \times 317.22)} = 0.27260$$

against the 0.25 you wanted. Making the devices bigger won't fix this, but making them *the
same* will. Four identical units in series put the same overhead in every branch, which
turns the ratio into a ratio of counts (one unit out of four), and every per-device error, known
or unknown, divides out. The measured nominal is `0.450000 V` exactly, and it costs nothing.

**The σ error is statistical.** It differs from die to die and averages to zero, and its size
follows one law:

$$\frac{\sigma_R}{R} = \frac{0.03552}{\sqrt{W L}}$$

which comes straight from the `res_high_po` model card's `body_pelgrom`. No choice of topology
changes it, so you pay for precision in area: halving σ takes four times the area.

## Unit devices and σ

This section is worth arguing about, because the folklore says unit devices reduce σ.

`mismatch.spice` builds the same 3:1 divider twice from exactly 24 µm² of poly: once as one short
device and one long one, and once as four identical units. The nominal values are very
different, but the spreads are almost the same:

```
3:1  one L=6 and one L=18        24 um^2 total  1.309327 V   5.6433 mV
3:1  four identical L=6 units    24 um^2 total  1.350000 V   5.7290 mV
```

5.6433 mV against 5.7290 mV is a 1.5 % difference, and 200 samples only pin σ down to ±5 %, so
within this run the two are the same number. Splitting a resistor into unit cells bought nothing
in random mismatch, and the algebra says it never will: for independent per-device errors, the σ
of a ratio depends on the total area and not on how you divided that area up.

Every analog textbook still tells you to use unit devices in a common centroid. The textbooks and
this run disagree because this simulation contains only random mismatch. Real wafers also have *gradients*: oxide
thickness, implant dose and temperature all vary smoothly across a die, so two devices ten
micrometres apart are more alike than two a millimetre apart, and the device on the left of a
pair sits in a systematically different environment from the one on the right. Unit devices
interleaved in a common-centroid pattern cancel the linear part of that gradient. The effect is
real and large, and it is the main reason the technique exists.

`AGAUSS` knows nothing about where your devices are, because your netlist doesn't say. **If you
try to prove that common-centroid layout helps by running Monte Carlo in ngspice, you will measure
zero benefit, because you will be measuring the model rather than the silicon.** Before you trust
a simulation to verify a design, check that the simulator contains the effects you're relying on;
otherwise the run only reassures you.

## Squeezing it further

112 µm² leaves some margin under the 150 µm² limit. σ scales as $1/\sqrt{L}$, so $L = 22$ gives
$3.0332$ mV, just over the 3.0 mV budget, and the real edge is somewhere around $L = 25$. Whether
you would ship a design 1 % inside a σ budget depends on how much you trust the model's
`body_pelgrom`, which was extracted from a finite number of real wafers and is quoted to four
figures.

Width is also worth trying. Every unit here is 1 µm wide, and since σ depends on area, `W=2 L=14`
has the same 28 µm² and the same σ, but half the resistance, twice the current, and
(Lab 01, Part 4) a sheet resistance closer to the flat part of the curve. There is no single
right answer, which is why the checker checks area and not shape.

## Questions to argue about

- The three constraints in `check_mm.py` are 0.2 %, 3.0 mV and 150 µm². Where would those numbers
  come from in a real project, and which would you expect to be handed rather than to choose?
- σ of the tap is 2.7 mV on a 450 mV output, about 0.6 %. If this divider set the reference for
  an ADC, how many bits would that cost you, and would you rather spend the area or add a trim?
- The 1 µm² resistor in part A misses the Pelgrom prediction by 27 % and the 64 µm² one by 10 %.
  Both are the same device. What does that tell you about quoting a single mismatch coefficient
  for a device family?
