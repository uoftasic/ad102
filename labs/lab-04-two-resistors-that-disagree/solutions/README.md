# One good answer (read this after yours passes)

```
four identical units, W = 1 um, L = 28 um, in series from vdd to ground,
tap taken between the first and the second counting up from ground.

  nominal tap   0.450000 V   exact
  sigma            2.7052 mV
  drawn area     112.00 um^2
```

## The shipped divider's two failures

Accuracy and precision are paid for differently. That is the point of the whole lab.

**The +9.04 % nominal error is systematic.** It is identical on every die, every wafer and every
lot. It comes from Lab 01's 378.2448 Ω of end resistance, which every device pays once regardless
of its length:

$$\frac{R_6}{R_6 + R_{18}} = \frac{378.24 + 6 \times 317.22}{(378.24 + 6 \times 317.22)+(378.24 + 18 \times 317.22)} = 0.27260$$

against the 0.25 you wanted. Making the devices bigger does not help; making them *the same*
does. Four identical units in series put the same overhead in every branch, so the ratio becomes a
ratio of **counts**, one unit out of four, and every per-device error, known or unknown, divides
out. The measured nominal is `0.450000 V`, exactly, and it costs nothing.

**The σ error is statistical.** It differs from die to die, averages to zero, and follows one law:

$$\frac{\sigma_R}{R} = \frac{0.03552}{\sqrt{W L}}$$

straight from the `res_high_po` model card's `body_pelgrom`. No topology trick fixes this one. You
pay for it in area, at four times the area per factor of two.

## Unit devices do not help σ

This is worth arguing about, because the folklore says otherwise.

`mismatch.spice` builds the same 3:1 divider twice from exactly 24 µm² of poly: once as one short
device and one long one, and once as four identical units. The nominal values are very
different. The spreads are not:

```
3:1  one L=6 and one L=18        24 um^2 total  1.309327 V   5.6433 mV
3:1  four identical L=6 units    24 um^2 total  1.350000 V   5.7290 mV
```

**5.6433 against 5.7290: a 1.5 % difference, where 200 samples only pin σ down to ±5 %.** Those
are the same number. Splitting a resistor into unit cells bought nothing in random mismatch, and
the algebra says it never will: for independent per-device errors, the σ of a ratio depends on
total area and on nothing else about how you divided it up.

So why does every analog textbook tell you to use unit devices in a common centroid?

Because **this simulation contains only random mismatch.** Real wafers also have *gradients*:
oxide thickness, implant dose and temperature all vary smoothly across a die, so two devices ten
micrometres apart are more alike than two a millimetre apart, and the device on the left of a
pair sits in a systematically different environment from the one on the right. Unit devices
interleaved in a common-centroid pattern cancel the linear part of that gradient. It is a real
and large effect, and it is the main reason the technique exists.

`AGAUSS` knows nothing about where your devices are, because your netlist does not say. **If you
try to prove that common-centroid layout helps by running Monte Carlo in ngspice, you will measure
zero benefit, because you will be measuring the model, not the silicon.** Knowing which effects
your simulator contains is the difference between verification and reassurance.

## Squeezing it further

112 µm² leaves margin. σ scales as $1/\sqrt{L}$, so $L = 22$ gives $3.0332$ mV, just over the
3.0 mV budget, and $L = 25$ or so is about the real edge. Whether you would ship a design 1 %
inside a σ budget depends on how much you trust the model's `body_pelgrom`, which was extracted
from a finite number of real wafers and is quoted to four figures.

Also worth trying: **width**. Every unit here is 1 µm wide. σ depends on area, so `W=2 L=14` has
the same 28 µm² and the same σ, but half the resistance, twice the current, and (Lab 01, Part 4)
a sheet resistance closer to the flat part of the curve. There is no single right answer, which is
why the checker checks area and not shape.

## Questions to argue about

- The three constraints in `check_mm.py` are 0.2 %, 3.0 mV and 150 µm². Where would those numbers
  come from in a real project, and which would you expect to be handed rather than to choose?
- σ of the tap is 2.7 mV on a 450 mV output, about 0.6 %. If this divider set the reference for
  an ADC, how many bits would that cost you, and would you rather spend the area or add a trim?
- The 1 µm² resistor in part A misses the Pelgrom prediction by 27 % and the 64 µm² one by 10 %.
  Both are the same device. What does that tell you about quoting a single mismatch coefficient
  for a device family?
