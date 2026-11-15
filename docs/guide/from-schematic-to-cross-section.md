# From schematic to cross-section

So far in AD102 you have drawn rectangles and called them components. This page shows what they
look like sliced through.

Everything up to now has been a **plan view**: you drew a shape on a mask layer and read a number
off a simulator. That is how layout is done, and it is enough to design with. But a chip is a
stack of films a few micrometres tall, and every surprise in this course came from that third
dimension:

- The resistor had **end resistance** (378.2448 Ω of it) because current has to climb *down*
  from metal into poly and back up again.
- The capacitor had **fringe** capacitance because field lines leave the *edge* of a plate.
- The wire had a parasitic to the substrate because it is a bar suspended *over* a plane.
- The inductor was impractical because its magnetic field goes *into* the silicon underneath it.

Each of those is a fact about the side view, which is what this page covers.

## The layer stack

[Ohms per square](../guide/ohms-per-square.md) started from

$$R = \rho\frac{L}{Wt} = \left(\frac{\rho}{t}\right)\frac{L}{W} = R_\square\frac{L}{W}$$

and treated the film thickness $t$ as a number the foundry fixed and you never need. It is fixed,
but it is also written down, in the technology file Magic uses to draw cross-sections, and that
file has been on your disk since IC101. Its `height` lines give, for each layer, how far the
bottom of the layer sits above the wafer surface and how thick it is, both in µm. Here are the
lines for the main layers (the file also lists fill, contact, via and MIM layers):

```
 height	dnwell 	    -0.1    0.1
 height	nwell,pwell  0.0    0.2062
 height alldiff	     0.2062 0.12
 height allpoly	     0.3262 0.18
 height allli	     0.9361 0.10
 height allm1	     1.3761 0.36
 height allm2	     2.0061 0.36
 height allm3	     2.7861 0.845
 height allm4	     4.0211 0.845
 height allm5	     5.3711 1.26
 height mrdl	     7.2611 3.0
```

That is the main stack of the chip in eleven lines. Read it as a building:

| Layer | Bottom | Thickness |
|---|---:|---:|
| deep n-well | −0.1 µm | 0.1 µm |
| n-well / p-well | 0.0 µm | 0.2062 µm |
| diffusion | 0.2062 µm | 0.12 µm |
| **poly** | **0.3262 µm** | **0.18 µm** |
| local interconnect (li) | 0.9361 µm | 0.10 µm |
| metal1 | 1.3761 µm | 0.36 µm |
| metal2 | 2.0061 µm | 0.36 µm |
| metal3 | 2.7861 µm | 0.845 µm |
| metal4 | 4.0211 µm | 0.845 µm |
| metal5 | 5.3711 µm | 1.26 µm |
| redistribution metal | 7.2611 µm | 3.0 µm |

The top of metal5 is 6.6311 µm above the silicon. A whole SKY130 chip, every layer of wiring
included, is about as thick as a red blood cell is wide. Your 100 kΩ resistor was 314.046454 µm
long, forty-seven times longer than the chip is thick. You'll print this stack yourself in
[the capstone, Part 1](../labs/capstone-floor-plan-overview.md#part-1-read-the-layer-stack).

## From sheet resistance to resistivity

You measured the sheet resistance of high-sheet poly yourself in Lab 01: 317.2198 Ω/□. The tech
file says that poly is 0.18 µm thick. So

$$\rho = R_\square \, t = 317.2198 \times 0.18\times10^{-6} = 5.7100\times10^{-5}\ \Omega\,\text{m}
= 5.7100\ \text{m}\Omega\,\text{cm}$$

That is no longer a layout number. It is a **material property**, the resistivity of the p+ doped
polysilicon SkyWater deposits, and you got it from a resistance you measured and a number you
read out of a file.

Do the same for `res_xhigh_po`, which measured 2118.7619 Ω/□ on the same 0.18 µm film:

$$\rho = 3.8138\times10^{-4}\ \Omega\,\text{m} = 38.1377\ \text{m}\Omega\,\text{cm}$$

Same layer, same thickness, 6.7 times the resistivity.
[Resistors on a chip](../guide/a-resistor-you-cannot-buy.md) said `res_high_po` and `res_xhigh_po`
differ only in implant dose. This is that dose, as a number: less dopant means fewer carriers,
which means higher resistivity, by a factor of 6.7.

For scale, here they are next to metals:

| Material | $\rho$ | vs copper |
|---|---:|---:|
| copper | 1.68×10⁻⁸ Ω m | 1× |
| SKY130 metal1 (0.125 Ω/□ × 0.36 µm) | 4.50×10⁻⁸ Ω m | **2.7×** |
| `res_high_po` | 5.71×10⁻⁵ Ω m | **3 399×** |
| `res_xhigh_po` | 3.81×10⁻⁴ Ω m | **22 701×** |

This is why on-chip resistors are made of poly and not metal. A resistor's job is to resist, and
the wiring metal conducts three and a half thousand times too well. To get 10 kΩ from metal1 at
the same width you would need $10000/0.125 = 80\,000$ squares: 80 millimetres of wire, on a die
three millimetres across.

A habit worth keeping: whenever a table gives you Ω/□, you are one multiplication away from a
material property, and material properties tell you whether a number is plausible.
5.7 mΩ·cm is a normal resistivity for a doped semiconductor. If your arithmetic had produced
5.7 Ω·cm or 5.7 µΩ·cm, something would be wrong.

In [the capstone, Part 2](../labs/capstone-floor-plan-overview.md#part-2-look-at-cross-sections-in-siliwiz)
you draw a resistor, a capacitor and a wire in SiliWiz and look at each one's cross-section. Then
Part 3 has you size a filter and defend its area.

## The three questions AD102 answers

AD102 set out to answer three questions:

- **How do you fabricate a resistor at the micro scale?** As a strip of doped poly, 0.18 µm
  thick, with $\rho = 5.71$ mΩ·cm. Its value is $R_\square L/W$ plus a fixed end resistance you
  cannot avoid, and you buy ohms with length.
- **A capacitor?** As two plates and a gap: metal3 and a thin dielectric above it for a MIM, a
  gate oxide for a MOS capacitor, or interleaved wire fingers for a VPP. At best about 2 fF per
  µm² for a linear capacitor, so a picofarad is a plate 22 µm on a side.
- **An inductor?** Mostly, you don't. A spiral of top metal gets you a couple of nanohenries at
  a $Q$ in the teens and costs tens of thousands of square micrometres, and below about 1 GHz
  [the alternatives](../guide/what-analog-builds-instead.md) do the job better.

Underneath all three is one habit: **a component value is a geometry, and geometry costs area.**
Of any analog schematic anyone shows you, ask what shape each part is, and what it costs.

## Where you go next

**[AD103 — Nonlinear Circuits](https://uoftasic.com/ad103/)** is the next course. It asks the
same question, what is this component physically, about devices whose behaviour is no longer
linear. The MOS capacitor whose value moved by 3.57× with voltage on
[Capacitors on a chip](../guide/a-capacitor-is-a-sandwich.md) was a transistor turning on, and AD103
opens by explaining what you were looking at. It is also where XSchem becomes the main tool;
[Lab 03, Part 8](../labs/lab-03-a-time-constant-in-silicon-overview.md#part-8-optional-the-same-circuit-in-xschem)
was your introduction to it.

**[AD104 — Layout](https://uoftasic.com/ad104/)** is where the cross-section becomes real
geometry. You draw these devices in Magic, on the real stack in the table above, and prove with
DRC that a fab could make them and with LVS that what you drew is the circuit you meant. Two
things from this course come back there: the **unit-device** and **common-centroid** rules from
[Matching and Pelgrom's law](../guide/matching-beats-accuracy.md), which become rectangles you draw;
and **parasitic extraction**, which reads your finished layout and hands back a netlist including
every capacitor from [Parasitic capacitance](../guide/the-capacitor-you-did-not-draw.md).

Next on the [Course path](../index.md#course-path):
[Capstone: Defend a floor plan](../labs/capstone-floor-plan-overview.md).
