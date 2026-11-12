# AD102 — Linear Circuits & Fabrication

You already know what a resistor does. This course is about what a resistor, a capacitor and an
inductor are when they are built on silicon, and what each one costs in chip area.

Part of the **UofT ASIC Team** education materials. Published at **https://uoftasic.com/ad102/**.
Labs run inside the **workbench**: the IIC-OSIC-TOOLS container you start from the `workspace`
repo you set up in [IC101](https://uoftasic.com/ic101/).

## Who this course is for

AD102 is the second course in the analog track, for 2nd–3rd year ECE students who have finished
IC101 and AD101.

ECE110 teaches linear circuit analysis: node voltages, mesh currents, $V = IR$, RC time
constants, impedance. AD102 does not re-teach any of that and is not a substitute for it. If you
have taken ECE110 you are ahead; if you have not, [AD101](https://uoftasic.com/ad101/) already
covered everything this course uses.

What ECE110 leaves out is where the components come from. In a lab kit, a resistor comes out of
a drawer with its value printed on the side. On a chip there is no drawer. A resistor is a strip
of doped polysilicon that you draw, and its value follows from the drawing: how long, how wide,
and which layer. Change the shape and you change the value; there is no other knob. The idea
this whole course builds on is that **a component value is a geometry, and geometry costs area.**

On a breadboard, component values are free and independent: a 10 kΩ costs the same as a 100 Ω,
and you can have as many as you like. On silicon neither is true. A 1 pF capacitor, about the
smallest value anyone names in a filter, is roughly a 22 µm × 22 µm plate: 484 µm² of silicon,
which simulates at 982.5022 fF (Lab 02 gives you the formula behind that number, and sizes the
plate exactly). The 4-bit ripple-carry adder that the digital track builds in
[DD103](https://uoftasic.com/dd103/), twelve SKY130 standard cells, fits in 110.1056 µm² of the
same process, so that one capacitor takes the area of 4.4 adders. The analog habits you'll pick
up here all follow from that comparison: ratios instead of values, unit devices, and keeping
inductors off the chip below a gigahertz.

## At a glance

| | |
|---|---|
| **Track** | Analog |
| **Prerequisites** | [IC101](https://uoftasic.com/ic101/) then [AD101](https://uoftasic.com/ad101/), in that order |
| **Tools** | ngspice and XSchem, both inside the workbench, plus SiliWiz (a browser layout tool that shows cross-sections) in a browser tab |
| **PDK** | SKY130 (`sky130A`), included in the image |
| **Time** | 12–16 hours, self-paced |
| **Math** | Algebra, $V=IR$, and the $R$, $C$ and frequency material from AD101. No calculus. |

## Course path

Work down this table in order. A **Read** row is one or more guide pages: concepts, figures and
worked examples, with nothing to run. A **Do** row is one lab, where you run every command
yourself. Each lab starts by listing the pages to read first.

| # | Type | What | Time |
|---|---|---|---|
| 1 | Read | [Getting started](guide/getting-started.md) · [Resistors on a chip](guide/a-resistor-you-cannot-buy.md) · [Ohms per square](guide/ohms-per-square.md) · [What a resistor costs in area](guide/what-a-value-costs-in-area.md) | 1.5 h |
| 2 | Do | [Lab 01 — A resistor you designed](labs/lab-01-a-resistor-you-designed-overview.md) | 2.5 h |
| 3 | Read | [Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md) · [What a picofarad costs](guide/what-a-picofarad-costs.md) · [Parasitic capacitance](guide/the-capacitor-you-did-not-draw.md) · [Inductors on a chip](guide/the-inductor-problem.md) | 1.5 h |
| 4 | Do | [Lab 02 — How big is a picofarad?](labs/lab-02-how-big-is-a-picofarad-overview.md) | 2.5 h |
| 5 | Read | [What to build instead of an inductor](guide/what-analog-builds-instead.md) | 30 min |
| 6 | Do | [Lab 03 — A time constant in silicon](labs/lab-03-a-time-constant-in-silicon-overview.md) | 2 h |
| 7 | Read | [Process corners](guide/the-value-you-drew-is-not-what-you-get.md) · [Matching and Pelgrom's law](guide/matching-beats-accuracy.md) | 1 h |
| 8 | Do | [Lab 04 — Two resistors that disagree](labs/lab-04-two-resistors-that-disagree-overview.md) | 2 h |
| 9 | Read | [From schematic to cross-section](guide/from-schematic-to-cross-section.md) | 30 min |
| 10 | Do | [Capstone — Defend a floor plan](labs/capstone-floor-plan-overview.md) | 1.5 h |

The times are estimates. Setup is the first part of Lab 01.

Keep these open while you work; they are for looking things up rather than reading through:
[The SKY130 passive catalogue](reference/sky130-passive-catalogue.md) ·
[ngspice deck recipes](reference/ngspice-decks-that-run.md)

**Stuck?** Ask in the [team Discord](https://discord.gg/hrJnP5UsGz). Nobody expects you to work
this out alone at 2 a.m. [Getting help](guide/getting-started.md#getting-help) says what to put
in your question.

## What you'll do

1. Measure the sheet resistance of SKY130 high-sheet poly yourself. The model card (the PDK's
   SPICE description of the device) says 317.3885 Ω per square, but one drawn square simulates
   at 695.4646 Ω, more than twice that.
   You'll find where the extra ohms come from, then size a 10 kΩ resistor correctly on the first
   try (30.3315 µm long, landing at 9999.997 Ω).
2. Work out what a picofarad costs in square micrometres, and why nobody puts a 10 µF capacitor
   on a chip.
3. Build an RC filter from the resistor and capacitor you designed and measure its time
   constant $\tau$. Then measure its corner frequency, check it against $1/(2\pi\tau)$ to six
   figures, and compare its Bode plot with that of the ideal 10 kΩ × 1 pF filter from AD101:
   15.8580 MHz for the filter you built against 15.9155 MHz for the ideal one, 0.36 % apart.
   Optionally, open the same circuit in XSchem and see a schematic turn into the device lines you
   typed by hand in the earlier labs.
4. See the same resistor come out different at every process corner, and learn why analog
   designers build ratios rather than values.
5. Find out how you fabricate an inductor on a chip. Mostly you don't, and you'll see what gets
   built instead.
6. Hit a filter spec using only devices the PDK actually ships, inside an area budget you have
   to defend.

## The workbench

This course is pinned to the workbench image **`hpretl/iic-osic-tools:2026.08`**, which ships
**ngspice-47** and **XSchem V3.4.8RC**. Tutorials online describe other versions with different
flags. When a command here disagrees with the internet, the command here is the one that runs on
your machine. Lab 01, Part 1 has you check your versions.

Each of Labs 01–04 has a **package**: a folder under `labs/` with its SPICE decks, a `Makefile`
and a checker script. The packages run with `make` alone, with no environment setup, because
every deck names its SKY130 model file by absolute path. You still do Lab 01, Part 1 once, to get
the course files and check your tools; if one of its PDK or version checks fails, try `make`
anyway. Apart from the optional SiliWiz parts, which run in a browser tab, every lab step runs in
a terminal, and only the optional XSchem part of Lab 03 opens a window on the desktop. A fifth
package, `passives-decks`, holds the decks whose output the guide pages quote, and some lab parts
run it too. The capstone has no package: it is one command, a browser exercise and a page of
arithmetic.

The first time you run each lab, its `make` ends in `FAIL`, on purpose. Each package ships the
design a first-year student would draw, sized straight off the model card, so that you read your
own wrong number before you fix it. The message tells you which line to edit.

## What you'll have at the end

A filter you designed from devices a real 130 nm process can make, simulated at every corner it
will be manufactured at, with an area number you can defend. You'll also be in the habit of
asking, for each part of an analog schematic, what shape it is and what it costs.

## Next courses

- **AD103** — Nonlinear Circuits: the diode and the MOSFET, and the regions they operate in
- **AD104** — Layout: draw these devices yourself in Magic, DRC-clean and LVS-clean
