# From schematic to cross-section

**Question this page answers:** *I have been drawing rectangles and calling them components.
What do they actually look like, sliced through?*

Everything in AD102 so far has been a **plan view** — you drew a shape on a mask layer and read
a number off a simulator. That is how layout is done, and it is enough to design with. But a
chip is not a drawing; it is a stack of films a few micrometres tall, and every surprise in this
course came from that third dimension:

- The resistor had **end resistance** (378.2448 Ω of it) because current has to climb *down*
  from metal into poly and back up again.
- The capacitor had **fringe** capacitance because field lines leave the *edge* of a plate.
- The wire had a parasitic to the substrate because it is a bar suspended *over* a plane.
- The inductor was unbuildable because its magnetic field goes *into* the silicon underneath it.

Every one of those is a fact about the side view. This page is the side view.

## First: the thickness you were told you could not see

Go back to [Ohms per square](guide/ohms-per-square.md). It started from physics you already had:

$$R = \rho\frac{L}{Wt} = \left(\frac{\rho}{t}\right)\frac{L}{W} = R_\square\frac{L}{W}$$

and then said something slightly defeatist about $t$:

> *Its thickness $t$ was fixed by the foundry before you were born — you cannot change it, you
> cannot even see it.*

The first half is true. The second half is not. **The thickness is written down**, in the
technology file Magic uses to draw cross-sections, and you have had it on your disk since IC101.

### Try this — read the stack

```bash
sed -n '/^ height/,/^$/p' /foss/pdks/sky130A/libs.tech/magic/sky130A.tech
```

**What you should see** (the first column is how far the bottom of the layer sits above the
wafer surface, the second is how thick it is, both in µm):

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

That is the whole chip, in eleven lines. Read it as a building:

| Storey | Bottom | Thickness |
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

**The top of metal5 is 6.6311 µm above the silicon.** A whole SKY130 chip, every layer of
wiring included, is about as thick as a red blood cell is wide. Your 100 kΩ resistor was
314.046454 µm long: it is **forty-seven times longer than the chip is thick.**

## Now close the loop the course left open

You measured the sheet resistance of high-sheet poly yourself, in Lab 01: **317.2198 Ω/□**. The
tech file says that poly is **0.18 µm** thick. So:

$$\rho = R_\square \, t = 317.2198 \times 0.18\times10^{-6} = 5.7100\times10^{-5}\ \Omega\,\text{m}
= 5.7100\ \text{m}\Omega\,\text{cm}$$

That is not a layout number any more. That is a **material property** — the resistivity of the
p+ doped polysilicon SkyWater deposits — and you got it from a resistance you measured and a
number you read out of a file.

Do the same for the other one. `res_xhigh_po` measured **2118.7619 Ω/□** on the same 0.18 µm
film:

$$\rho = 3.8138\times10^{-4}\ \Omega\,\text{m} = 38.1377\ \text{m}\Omega\,\text{cm}$$

**Same layer, same thickness, 6.7× the resistivity.** Back on
[A resistor you cannot buy](guide/a-resistor-you-cannot-buy.md) the menu said `res_high_po` and
`res_xhigh_po` differ only by implant dose. Here is that dose, as a number: less dopant means
fewer carriers means more resistivity, and the factor is 6.7.

For scale, put those next to metals:

| Material | $\rho$ | vs copper |
|---|---:|---:|
| copper | 1.68×10⁻⁸ Ω m | 1× |
| SKY130 metal1 (0.125 Ω/□ × 0.36 µm) | 4.50×10⁻⁸ Ω m | **2.7×** |
| `res_high_po` | 5.71×10⁻⁵ Ω m | **3 399×** |
| `res_xhigh_po` | 3.81×10⁻⁴ Ω m | **22 701×** |

**This is why on-chip resistors are made of poly and not metal.** A resistor's whole job is to
be resistive, and the wiring metal is three and a half thousand times too good at conducting.
To get 10 kΩ out of metal1 at the same width you would need $10000/0.125 = 80\,000$ squares —
**80 millimetres** of wire, on a die three millimetres across.

**The reflex check:** any time a table gives you Ω/□, you are one multiplication away from a
material property, and material properties are how you tell whether a number is plausible.
5.7 mΩ·cm is a normal doped-semiconductor resistivity. If your arithmetic had produced
5.7 Ω·cm or 5.7 µΩ·cm, something was wrong.

## Try this — draw the side view yourself

Reading heights out of a file is not the same as seeing it. **SiliWiz** puts a live
cross-section under your drawing:

**<https://app.siliwiz.com/?preset=blank>**

### 1. The resistor you designed

1. Draw a **poly** rectangle, long and thin — 20 grid units by 2, roughly the aspect ratio of
   your Lab 01 resistor.
2. Put a **contact** at each end and a **metal1** pad over each contact.
3. Label the two pads `a` and `b`.
4. Look at the **cross-section** pane. Follow the current path with your finger: down the
   metal1 pad, through the contact, along the poly strip, up the far contact, out the far pad.

**What you should see:** the current does not travel in a straight line through one material.
It makes two right-angle turns through a via that is much smaller than the strip. **That
detour is the 378.2448 Ω** you spent all of Lab 01 accounting for — the "end resistance" is not
a fudge factor, it is a shape you can point at.

- **Try this:** drag the strip longer. Watch the resistance climb linearly while the two ends
  stay exactly as they were.
- **Why an engineer cares:** it is now obvious why $R = R_\square L/W$ has a constant added to
  it, and why the constant does not scale. You are looking at the constant.

### 2. The capacitor you designed

1. New drawing. Put a **metal1** rectangle down, and a **metal2** rectangle directly over it,
   same size.
2. Label them and tick **Show SPICE**.
3. Find the capacitance between them, then drag the top plate to overhang the bottom one.

**What you should see:** the capacitance is *not* proportional to overlap area alone. Push the
plates out of alignment and it falls more slowly than the overlap does, because the field is
still bending around the edges. That is the perimeter term —
$C = 2.000000\,s^2 + 0.659991\,s - 0.017742$ fF from
[What a picofarad costs](guide/what-a-picofarad-costs.md) — with the middle coefficient made
visible.

### 3. The parasitic you did not draw

1. Draw a single **metal1** wire and nothing else. Label it.
2. Read the SPICE output.

There is a capacitor in it, to the substrate, from a circuit you did not draw. That is
[The capacitor you did not draw](guide/the-capacitor-you-did-not-draw.md), and the reason is
now visible: the wire is a bar, the substrate is a plane, and there is nowhere for the field to
go except down.

> **SiliWiz is not SKY130.** Its layer stack, its permittivities and its numbers are simplified
> for teaching, and its cross-section is a cartoon of the table above rather than a rendering of
> it. Read it for the **shape** of the answer — "the current turns two corners", "the field
> bends around the edge", "there is a plate under everything" — and read the tech file and your
> own ngspice runs for the values. Guided walkthroughs, if you want them:
> [resistors](https://tinytapeout.com/siliwiz/resistors/) ·
> [capacitors](https://tinytapeout.com/siliwiz/capacitors/) ·
> [parasitics](https://tinytapeout.com/siliwiz/parasitics/).

## The capstone exercise: defend a floor plan

No package for this one. It is a page of arithmetic, and every number you need is one you
already measured.

**The brief.** Build a first-order low-pass with a corner at **1 MHz**, on-die, in SKY130. You
may use `res_high_po`, `res_xhigh_po`, and `cap_mim_m3_1`. You must state the drawn area, and
you must defend it.

Work it in this order:

1. **$RC = 1/(2\pi f_c) = 159.15$ ns.** That is your only hard constraint, and it fixes only
   the *product*. Every split of it is legal.
2. **Price both halves.** From Lab 01, `res_high_po` at $W = 1$ µm costs $L = (R -
   378.2448)/317.2198$ µm of area per ohm. From Lab 02, a MIM plate of side $s$ holds
   $2.000000\,s^2 + 0.659991\,s - 0.017742$ fF and costs $s^2$ µm². Tabulate total area for
   $R$ = 10 kΩ, 100 kΩ, 1 MΩ and 10 MΩ.
3. **Find the minimum, then find the wall.** The area curve has a bottom; you found the same
   shape in [Lab 03](labs/lab-03-a-time-constant-in-silicon-overview.md) step 6. Then check the
   answer against [What a value costs in area](guide/what-a-value-costs-in-area.md): a 1 MΩ of
   `res_high_po` is **3.15 mm** of poly. Which of your rows are actually buildable on a 3 mm
   die?
4. **Check the resistor against itself.** Lab 03 measured a bare 471.98 µm strip of 1 µm poly
   carrying **95.278 fF** to the substrate, of which half adds to the time constant. At what
   resistor length does that parasitic become a visible fraction of the capacitor you were
   planning? That is the wall, and it is the reason the answer is not "just use an enormous
   resistor".
5. **Now price it in adders.** Convert your winning area into DD103 ripple-carry adders at
   **110.1056 µm²** each. Write the sentence out loud: *"my one filter pole costs N adders."*
6. **Then answer the real question.** Would you build it? Or would you do what
   [What analog builds instead](guide/what-analog-builds-instead.md) describes, and move the
   pole off-chip or into the digital domain?

There is no marking scheme. The deliverable is the sentence in step 5 and a defensible answer to
step 6, and if you can produce both you have the habit this course exists to install.

## What AD102 was actually about

Three questions from the charter, answered:

- **How do you fabricate a resistor at the micro scale?** A strip of doped poly, 0.18 µm thick,
  $\rho = 5.71$ mΩ·cm. Its value is $R_\square L/W$ plus a fixed end resistance you cannot
  avoid, and you buy ohms with length.
- **A capacitor?** Two plates and a gap: metal3 and a thin dielectric above it for a MIM, a gate
  oxide for a MOS cap, or interleaved wire fingers for a VPP. About **2 fF per µm²** at best, so
  a picofarad is a plate 22 µm on a side.
- **An inductor?** Mostly, you don't. A spiral of top metal gets you a couple of nanohenries at
  a $Q$ in the teens and costs tens of thousands of square micrometres, and everything below
  ~1 GHz is better served by
  [what analog builds instead](guide/what-analog-builds-instead.md).

And one habit underneath all three: **a component value is a geometry, and geometry costs
area.** Ask of any analog schematic anyone ever shows you — *what shape is that, and what does
it cost?*

## Where you go next

**[AD103 — Nonlinear Circuits](https://uoftasic.com/ad103/)** is the next course, and it takes
the same question — *what is this component, physically?* — to devices where the answer stops
being linear. The MOS capacitor whose value moved by 3.57× with voltage on
[A capacitor is a sandwich](guide/a-capacitor-is-a-sandwich.md) was a transistor turning on, and
AD103 opens by explaining what you were actually looking at. It is also where **XSchem** stops
being a one-step cameo — [Lab 03's step 7](labs/lab-03-a-time-constant-in-silicon-overview.md)
was your introduction to it on purpose.

**[AD104 — Layout](https://uoftasic.com/ad104/)** is where the cross-section stops being a
browser toy. You draw these devices as real geometry in Magic, on the real stack in the table
above, and prove with DRC that a fab could make them and with LVS that what you drew is the
circuit you meant. Two things from this course are waiting for you there: the **unit-device**
and **common-centroid** rules from
[Matching beats accuracy](guide/matching-beats-accuracy.md), which stop being advice and become
rectangles; and **parasitic extraction**, which reads your finished layout and hands you back
the netlist including every capacitor on
[The capacitor you did not draw](guide/the-capacitor-you-did-not-draw.md).

**Stuck, or want to argue about a floor plan?** The team Discord is at
<https://discord.gg/hrJnP5UsGz>. Bring your area table.
