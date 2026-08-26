# What a picofarad costs

**Question this page answers:** *Why does every chip schematic have capacitors in
femtofarads, when the ones in my parts drawer are microfarads?*

Because on a chip you buy capacitance by the square micrometre, and the exchange
rate is bad.

From [the previous page](guide/a-capacitor-is-a-sandwich.md), measured, not quoted:
a MIM capacitor is **about 2 fF per µm²**. Turn that into floor plan.

## The exchange rate

| you want | MIM plate area | plate is about | in `sky130_fd_sc_hd__inv_1` (3.7536 µm²) |
|---:|---:|---|---:|
| 100 fF | 49 µm² | 7 × 7 µm | 13 |
| 1 pF | 494 µm² | 22 × 22 µm | 132 |
| 10 pF | 4 940 µm² | 70 × 70 µm | 1 316 |
| 100 pF | 49 400 µm² | 222 × 222 µm | 13 160 |
| 1 nF | 494 000 µm² | 703 × 703 µm | 131 600 |
| 1 µF | 494.6 mm² | *a plate 2.2 cm on a side* | 132 million |

Those numbers come straight from the measured 30 × 30 device: 1819.782 fF over
900 µm² is 2.0220 fF/µm², so 1 pF needs $1000/2.0220 = 494.6$ µm².

Read the last row and then look at the 100 nF ceramic chip you would casually
solder next to a microcontroller. A typical small SKY130 die is about 3 mm × 3 mm,
which is **9 mm²**. The 1 µF wants 494.6 mm² — **fifty-five entire chips**, for one
component. It is not that on-chip capacitors are small because designers are timid.
It is that a 1 µF capacitor is physically impossible on a die, and no cleverness
closes that gap.

Even the densest option does not rescue you. A MOS capacitor at 7.88 fF/µm² gets
1 µF down to 126.9 mm² — still fourteen whole dies, and now with a value that
changes by 3.57× depending on the voltage across it.

## So what does fit?

| capacitance | what it is used for |
|---:|---|
| 1–50 fF | sampling caps in an ADC, compensation on an amplifier, charge redistribution |
| 50–500 fF | filter capacitors, matched arrays, bandgap compensation |
| 1–20 pF | serious on-die decoupling, a big integrator, an off-chip driver's load |
| > 50 pF | you are budgeting a substantial fraction of the die for one component |

This is the entire reason analog IC design *looks* the way it does. A discrete
designer builds a 1 kHz low-pass from 16 kΩ and 10 nF. That capacitor is
**4.94 mm²** on-die — bigger than most whole chips. So the on-chip designer does not
build that filter. They build a switched-capacitor filter, or they use a very large
resistance made from a starved transistor, or they push the corner frequency up by
three decades and filter the rest off-chip. See
[What analog builds instead](guide/what-analog-builds-instead.md).

## Try this: watch the density change with size

```bash
cd labs/passives-decks
make capacitor
```

**What you should see** (already familiar from the previous page):

```
c_mim_1x1 = 2.642250e-15
c_mim_10x10 = 2.065822e-13
c_mim_30x30 = 1.819782e-12
```

- **Try this:** divide each by its drawn area — 1, 100 and 900 µm².
- **What you should see:** 2.64, 2.07, 2.02 fF/µm². The density *falls* as the
  capacitor gets bigger.
- **Why an engineer cares:** the extra in the small one is edge field —
  `cpmimc = 0.19e-15` farads per micron of perimeter. Perimeter grows as the side
  length; area grows as its square. So the edge bonus is a 24 % windfall at 1 µm and
  a 1 % rounding error at 30 µm. **Never estimate a small capacitor by area alone.**

## Predict, then be wrong

Here is a question worth getting wrong before reading on.

*You need 1 pF. You have room for a single 23 × 23 µm MIM. Alternatively you could
place one hundred 2.3 × 2.3 µm MIMs in parallel, which occupies the same 529 µm² of
plate. Which gives more capacitance?*

Most people say "the same". They are not the same, and the perimeter term says why.
One big plate: $2.00 \times 22.975^2 + 0.19 \times 2 \times (22.975+22.975) = 1055.65 + 17.46 = 1073.1$ fF.
One hundred small plates: each is $2.00 \times 2.275^2 + 0.19 \times 2 \times (2.275+2.275) = 10.35 + 1.729 = 12.08$ fF,
times 100 = **1208 fF**. The chopped-up version is **12.6 % bigger** for the same
plate area, purely because you created a lot more edge.

That is a real technique — it is exactly why VPP capacitors exist, and why
`sky130_fd_pr__cap_vpp_*` structures are drawn as interleaved fingers rather than
slabs. (In practice the hundred small plates also need a hundred sets of
connections and a lot of spacing between them, which is why nobody takes it to that
extreme. But the direction is right, and the foundry took it as far as it goes when
they drew the VPP cells.)

## What a capacitor costs besides area

Three bills that do not appear in the farad number:

**Bottom-plate parasitic.** A MIM plate is a big sheet of metal sitting over the
substrate. It has its *own* capacitance to ground, whether you asked for it or not
— the `.subckt` has a third terminal for exactly this. In a switched-capacitor
circuit this parasitic is the dominant error source, and the entire art is arranging
for it to be driven by something that does not care.

**Series resistance.** Look at the MIM `.subckt` and you find two resistors in
series with the capacitance:

```
rs1 a  b1 'r1' tc1 = {tc1rm3} tc2 = {tc2rm3}
rs2 b1 c1 'r2' tc1 = {tc1rvia3} tc2 = {tc2rvia3}
```

`r1` is the met3 plate's own sheet resistance; `r2` is the via array. Your capacitor
is a capacitor *and* a small resistor, and at high frequency the resistor wins.

**Corner spread.** The MIM's area capacitance is `2.00e-15` F/µm² typical, but
`1.778e-15` at the low corner and `2.231e-15` at the high one — about **±11 %**.
[Movement IV](guide/the-value-you-drew-is-not-what-you-get.md) is about what to do
with that.

## Why an engineer cares

When you read an analog paper and see "C₁ = 240 fF", that is not an arbitrary
number — it is 119 µm² of somebody's floor plan, argued over in a design review.
Area is the currency of this whole field, and capacitors are the most expensive
thing you can buy with it.

[Lab 02 — How big is a picofarad?](labs/lab-02-how-big-is-a-picofarad-overview.md)
makes you separate the area term from the edge term yourself, and then size a
capacitor to a target.

Next: [The capacitor you did not draw](guide/the-capacitor-you-did-not-draw.md) —
because the capacitors that cost you the most are the ones nowhere in your
schematic.
