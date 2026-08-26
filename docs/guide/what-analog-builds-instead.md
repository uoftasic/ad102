# What analog builds instead

**Question this page answers:** *If I cannot have an inductor, how does anyone build
a filter, an oscillator, or a supply on a chip?*

By noticing what the inductor was *for* and finding another way to get it. There are
four standard answers, and the first three are used constantly.

## 1. Just use R and C, and move the frequency

Most of what an inductor does in a discrete design — set a corner frequency, shape a
response — an RC network does too, with one fewer pole per stage. The catch is that
an RC corner is only as good as R × C, and you already know what those cost:

$$f_{-3\text{dB}} = \frac{1}{2\pi R C}$$

A 1 kHz corner needs $RC = 159$ µs. Pair the 100 kΩ you sized in
[Movement I](guide/what-a-value-costs-in-area.md) — 314 µm² of poly — with the
1.6 nF that requires, and the capacitor alone is **791 300 µm²**: 0.79 mm²,
about **9 % of a 3 mm × 3 mm die**, or 210 800 inverters, for one pole. Not
happening.

So the on-chip designer does the only thing left: **put the corner somewhere else**.
The corners deck builds an RC low-pass out of one 3550 Ω resistor and one 206.5822 fF
MIM:

```
--- tt : RC corner frequency, Hz ---
f3db                =  2.15410e+08
```

**215.410 MHz.** ([Lab 03 — A time constant in
silicon](labs/lab-03-a-time-constant-in-silicon-overview.md) builds the same RC and
measures its τ in the time domain.) That is what "a resistor and a capacitor you can
afford" buys you:
a corner five orders of magnitude above the one you wanted. Anything slower than a
few megahertz gets filtered off-chip, or by one of the next two techniques.

## 2. Switched capacitors — a resistor made of a clock

This is the single most important trick in analog IC design, and it exists because
of the two facts you have just learned.

Take a capacitor $C$ and a two-phase clock at frequency $f_{clk}$. Alternately
connect $C$ to node A and to node B. Each cycle it carries $Q = C\,\Delta V$ from one
to the other, so the average current is $I = f_{clk}\,C\,\Delta V$ — which is Ohm's
law with

$$R_{\text{eq}} = \frac{1}{f_{clk}\,C}$$

**A capacitor plus a switch is a resistor**, and its value is set by a *clock
frequency* rather than by a length of poly.

Put numbers on it. Take a 100 fF capacitor — about 49 µm², thirteen inverters — and
clock it at 1 MHz:

$$R_{\text{eq}} = \frac{1}{10^{6} \times 100\times10^{-15}} = 10\ \text{M}\Omega$$

**10 MΩ in 49 µm².** The same 10 MΩ built as `res_xhigh_po` at 1 µm wide would be
$(10^7 - 34.2111)/2118.7619 = 4719.7$ µm long — **4.72 millimetres**, wider than
most dies, and 4720 µm² of poly at a 1 µm width. The switched capacitor wins by a
factor of about ninety-six in area, and it wins by infinity in "is this a thing I
can actually place".

Two further gifts:

- **The value is tunable.** Change the clock, change the resistance. No mask spin.
- **The time constant becomes a capacitor ratio.** An RC made from a switched
  capacitor $C_1$ and an integrating capacitor $C_2$ has
  $\tau = R_{eq}C_2 = C_2/(f_{clk} C_1)$ — a *ratio of capacitors* times a clock
  period. And a ratio of capacitors, as [the next
  movement](guide/matching-beats-accuracy.md) demonstrates to seven digits, is the
  most accurate thing on a chip. This is why almost every ADC you will ever meet is
  built out of switched capacitors.

The cost is that the circuit is now sampled: it only makes sense below
$f_{clk}/2$, and it folds noise. AD202 is where that gets treated properly.

## 3. Gyrators — make a capacitor look inductive

An inductor's defining relation is $V = L\,dI/dt$; a capacitor's is
$I = C\,dV/dt$. They are the same equation with current and voltage swapped. So a
circuit that swaps current and voltage — a **gyrator**, built from two
transconductors — turns a capacitor at one port into an inductance at the other:

$$L_{\text{eq}} = \frac{C}{g_{m1} g_{m2}}$$

With $g_m = 100$ µS and $C = 1$ pF you get $L_{eq} = 100$ µH — ten thousand times
the biggest spiral in the PDK, in about 500 µm² of MIM plus two small amplifiers.

The catch is that it is *active*: it needs supply current, it adds noise, it has a
limited signal swing, and it stops working above the transconductors' bandwidth. It
is not an inductor; it is a circuit that behaves like one over a range. That is
usually enough, and "active inductor" or "simulated inductor" filters are standard
practice at audio and low RF.

## 4. Put the inductor somewhere that is not the die

If you genuinely need a real inductor — a switching regulator, an RF matching
network, a high-current supply — you buy one and put it on the board. Two on-die
pads and a package pin cost a few thousand µm² and get you a component with a Q of
40 and a value in microhenries.

Even the package itself is used deliberately: a bond wire is roughly **1 nH per
millimetre**, and RF designers absolutely do design that inductance into the
matching network rather than fighting it.

## Where the spiral does earn its keep

None of the above means the three SKY130 spirals are useless. Above about a
gigahertz, where Q climbs past 10, an on-die inductor is the right and often the
only answer:

- the **LC tank** of a voltage-controlled oscillator, where Q sets phase noise;
- **inductive peaking** on a wideband amplifier, where a couple of nanohenries
  extends bandwidth by tens of percent;
- **impedance matching** to a 50 Ω antenna.

That is what those cells exist for. It is a narrow, real, well-paid niche, and it is
not where AD102 or AD103 live.

## The pattern worth taking away

Every one of these four answers has the same shape:

> **On a chip, absolute values are expensive and ratios are cheap. So build the
> thing you want out of ratios, and get the absolute scale from something that is
> not silicon — a clock, a bias current, a component on the board.**

A switched-capacitor filter's corner is a capacitor ratio times a clock. A gyrator's
inductance is a capacitance over two transconductances that are themselves set by a
bias current. A bandgap reference's output is a resistor *ratio* times a physical
constant.

That principle is not a stylistic preference. It falls directly out of the
measurement in the next movement, which is that on-chip absolute values are poor and
on-chip ratios are essentially exact.

Next: [The value you drew is not what you get](guide/the-value-you-drew-is-not-what-you-get.md).
