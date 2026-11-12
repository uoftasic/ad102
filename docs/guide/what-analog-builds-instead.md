# What to build instead of an inductor

If you cannot have an inductor, how does anyone build a filter, an oscillator or a power supply
on a chip? By working out what the inductor was for and getting that another way. There are four
standard answers, and the first three are used all the time.

## 1. Use R and C, at a different frequency

Most of what an inductor does in a discrete design, such as setting a corner frequency or shaping
a response, an RC network can also do, with one fewer pole per stage. The catch is that an RC
corner depends on R × C, and you already know what those cost:

$$f_{-3\text{dB}} = \frac{1}{2\pi R C}$$

A 1 kHz corner needs $RC = 159$ µs. Pair the 100 kΩ from
[What a resistor costs in area](guide/what-a-value-costs-in-area.md) (314 µm² of poly) with the
1.6 nF that requires, and the capacitor alone is 791 300 µm²: 0.79 mm², about 9 % of a
3 mm × 3 mm die, or 210 800 inverters, for one pole. Nobody builds that.

So the on-chip designer moves the corner. The corners deck in `labs/passives-decks` builds an RC
low-pass from one 3550 Ω resistor and one 206.5822 fF MIM capacitor:

```
--- tt : RC corner frequency, Hz ---
f3db                =  2.15410e+08
```

That is 215.410 MHz: a resistor and a capacitor you can afford give you a corner five orders of
magnitude above the 1 kHz you wanted. Anything slower than a few megahertz gets filtered
off-chip, or by one of the next two techniques.
[Lab 03](labs/lab-03-a-time-constant-in-silicon-overview.md) builds an RC from the resistor and
capacitor you designed and measures its time constant in the time domain.

## 2. Switched capacitors

This is the most important trick in analog IC design, and it exists because of the two facts you
have just learned.

Take a capacitor $C$ and a two-phase clock at frequency $f_{clk}$. Connect $C$ alternately to
node A and to node B. Each cycle it carries a charge $Q = C\,\Delta V$ from one node to the
other, so the average current is $I = f_{clk}\,C\,\Delta V$. That is Ohm's law with

$$R_{\text{eq}} = \frac{1}{f_{clk}\,C}$$

So a capacitor plus a switch acts as a resistor, and its value is set by a clock frequency rather
than by a length of poly.

With numbers: take a 100 fF capacitor (about 49 µm², thirteen inverters) and clock it at 1 MHz:

$$R_{\text{eq}} = \frac{1}{10^{6} \times 100\times10^{-15}} = 10\ \text{M}\Omega$$

That is 10 MΩ in 49 µm². The same 10 MΩ built as `res_xhigh_po` at 1 µm wide would be
$(10^7 - 34.2111)/2118.7619 = 4719.7$ µm long: 4.72 millimetres, wider than most dies, and
4720 µm² of poly. The switched capacitor uses about ninety-six times less area, and unlike the
4.72 mm strip, it is something you can actually place.

It has two more advantages:

- **The value is tunable.** Change the clock and you change the resistance, with no new masks.
- **The time constant becomes a capacitor ratio.** An RC made from a switched capacitor $C_1$ and
  an integrating capacitor $C_2$ has $\tau = R_{eq}C_2 = C_2/(f_{clk} C_1)$: a ratio of
  capacitors times a clock period. A ratio of matched devices is the most accurate thing on a
  chip (see [Matching and Pelgrom's law](guide/matching-beats-accuracy.md)). This is why almost
  every ADC you will meet is built from switched capacitors.

The cost is that the circuit is now sampled: it only works below $f_{clk}/2$, and it folds noise.
AD202 covers that properly.

## 3. Gyrators

An inductor obeys $V = L\,dI/dt$ and a capacitor obeys $I = C\,dV/dt$: the same equation with
current and voltage swapped. A circuit that swaps current and voltage, called a **gyrator** and
built from two transconductors, turns a capacitor at one port into an inductance at the other:

$$L_{\text{eq}} = \frac{C}{g_{m1} g_{m2}}$$

With $g_m = 100$ µS and $C = 1$ pF you get $L_{eq} = 100$ µH, ten thousand times the biggest
spiral in the PDK, in about 500 µm² of MIM plus two small amplifiers.

The catch is that it is *active*: it needs supply current, adds noise, has a limited signal
swing, and stops working above the transconductors' bandwidth. It is a circuit that behaves like
an inductor over a range, which is usually enough. "Active inductor" or "simulated inductor"
filters are standard practice at audio and low RF.

## 4. Put the inductor off the die

If you really need an inductor (a switching regulator, an RF matching network, a high-current
supply), you buy one and put it on the board. Two on-die pads and a package pin cost a few
thousand µm² and get you a component with a Q of 40 and a value in microhenries.

The package itself gets used too. A bond wire is roughly 1 nH per millimetre, and RF designers do
design that inductance into the matching network rather than fighting it.

## When to use an on-chip spiral

None of this makes the three SKY130 spirals useless. Above about a gigahertz, where Q climbs past
10, an on-die inductor is the right answer and often the only one:

- the **LC tank** of a voltage-controlled oscillator, where Q sets the phase noise;
- **inductive peaking** on a wideband amplifier, where a couple of nanohenries extends the
  bandwidth by tens of percent;
- **impedance matching** to a 50 Ω antenna.

That is what those cells are for. It is a narrow, real and well-paid niche, and it is not where
AD102 or AD103 work.

## What the four answers have in common

All four answers have the same shape:

> **On a chip, absolute values are expensive and ratios are cheap. So build what you need out of
> ratios, and get the absolute scale from something that is not silicon: a clock, a bias current,
> or a component on the board.**

A switched-capacitor filter's corner is a capacitor ratio times a clock. A gyrator's inductance
is a capacitance over two transconductances, which are themselves set by a bias current. A
bandgap reference's output is a resistor ratio times a physical constant.

This principle follows directly from a measurement you'll see on the next two pages: on-chip
absolute values are poor, and on-chip ratios are essentially exact.

Next on the [Course path](README.md#course-path):
[Lab 03 — A time constant in silicon](labs/lab-03-a-time-constant-in-silicon-overview.md).
After that, read [Process corners](guide/the-value-you-drew-is-not-what-you-get.md).
