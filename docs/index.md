# AD102 — Linear Circuits & Fabrication

In this course you find out how resistors, capacitors and inductors are built on a SKY130 chip,
measure them in ngspice, and size your own resistors and capacitors to hit target values inside
an area budget.

A resistor on a chip is a strip of doped polysilicon, and its value depends on the strip's
length, its width and the layer it's on. A capacitor plate 22 µm on a side covers 484 µm² and
simulates at 982.5022 fF, a little short of 1 pF. In Lab 02 you fit the formula behind that
number and size a 1 pF plate exactly. The 4-bit ripple-carry adder that the digital track builds
in [DD103](https://uoftasic.com/dd103/) is made of twelve SKY130 standard cells and fits in
110.1056 µm², so that one plate takes the area of 4.4 adders.

The course is part of the **UofT ASIC Team** education materials, and it's published at
**https://uoftasic.com/ad102/**. The labs run inside the **workbench**, which is the
IIC-OSIC-TOOLS container that you start from the `workspace` repo you set up in
[IC101](https://uoftasic.com/ic101/).

## Who this course is for

AD102 is the second course in the analog track, for 2nd–3rd year ECE students who have finished
IC101 and AD101.

ECE110 teaches linear circuit analysis: node voltages, mesh currents, $V = IR$, RC time
constants, impedance. AD102 doesn't teach that again. Having taken ECE110 helps but isn't
required. You should know $V = IR$ and series and parallel resistors, and you'll use the RC
corner frequency from [AD101](https://uoftasic.com/ad101/).

## At a glance

| | |
|---|---|
| **Track** | Analog |
| **Prerequisites** | [IC101](https://uoftasic.com/ic101/) then [AD101](https://uoftasic.com/ad101/), in that order |
| **Tools** | ngspice in the workbench, and SiliWiz (a layout tool that runs in a browser tab and shows cross-sections). XSchem comes up only in an optional part of Lab 03. |
| **PDK** | SKY130 (`sky130A`), included in the image |
| **Time** | About 15.5 hours, self-paced |
| **Math** | Algebra, $V=IR$, and the $R$, $C$ and frequency material from AD101. No calculus. |

## Course path

Work down this table in order. A Read row is one or more guide pages: concepts, figures and
worked examples, with nothing to run. A Do row is one lab, where you run every command
yourself. Each lab starts by listing the pages to read first.

| # | | What | Time |
|---|---|---|---|
| 1 | Read | [Getting started](guide/getting-started.md) · [Resistors on a chip](guide/a-resistor-you-cannot-buy.md) · [Ohms per square](guide/ohms-per-square.md) · [What a resistor costs in area](guide/what-a-value-costs-in-area.md) | 1.5 h |
| 2 | Do | [Lab 01: A resistor you designed](labs/lab-01-a-resistor-you-designed-overview.md). Load the course, measure the sheet and end resistance of SKY130 poly, and size two resistors to within 1 % of their targets. | 2.5 h |
| 3 | Read | [Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md) · [What a picofarad costs](guide/what-a-picofarad-costs.md) · [Parasitic capacitance](guide/the-capacitor-you-did-not-draw.md) · [Inductors on a chip](guide/the-inductor-problem.md) | 1.5 h |
| 4 | Do | [Lab 02: How big is a picofarad?](labs/lab-02-how-big-is-a-picofarad-overview.md). Fit a MIM capacitor's area and edge terms, size two capacitors, and measure the three inductors SKY130 ships. | 2.5 h |
| 5 | Read | [What to build instead of an inductor](guide/what-analog-builds-instead.md) | 30 min |
| 6 | Do | [Lab 03: A time constant in silicon](labs/lab-03-a-time-constant-in-silicon-overview.md). Measure the time constant of your own resistor and capacitor in one circuit, then build a 20 ns RC in under 400 µm². | 2 h |
| 7 | Read | [Process corners](guide/the-value-you-drew-is-not-what-you-get.md) · [Matching and Pelgrom's law](guide/matching-beats-accuracy.md) | 1 h |
| 8 | Do | [Lab 04: Two resistors that disagree](labs/lab-04-two-resistors-that-disagree-overview.md). Run three process corners and a seeded Monte Carlo, then design a 0.45 V divider that is accurate, precise and under 150 µm². | 2 h |
| 9 | Read | [From schematic to cross-section](guide/from-schematic-to-cross-section.md) | 30 min |
| 10 | Do | [Capstone: Defend a floor plan](labs/capstone-floor-plan-overview.md). Read the layer stack, look at cross-sections in SiliWiz, and size a 1 MHz low-pass filter whose area you can defend. | 1.5 h |

The times are estimates, and they add up to the 15.5 hours above. There's no separate setup row,
because setting up is the first part of Lab 01.

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
   try (30.3315 µm long, landing at 9999.997 Ω), and two more of your own.
2. Work out what a picofarad costs in square micrometres, and why nobody puts a 1 µF capacitor
   on a chip.
3. Build an RC filter from the resistor and capacitor you designed and measure its time
   constant $\tau$. Then measure its corner frequency, check it against $1/(2\pi\tau)$ to five
   figures, and compare its Bode plot with that of the same filter built from an ideal 10 kΩ and
   an ideal 1 pF: 15.8580 MHz for the filter you built against 15.9155 MHz for the ideal one,
   0.36 % apart.
   Optionally, open the same circuit in XSchem and see a schematic turn into the device lines you
   have been editing by hand.
4. See the same resistor come out different at every process corner, and learn why analog
   designers build ratios rather than values.
5. Find out how you fabricate an inductor on a chip. Mostly you don't, so you'll also see what
   gets built instead.
6. Hit a filter spec using only devices the PDK actually ships, inside an area budget you have
   to defend.

## The workbench

This course is pinned to the workbench image **`hpretl/iic-osic-tools:2026.08`**, which ships
**ngspice-47** and **XSchem V3.4.8RC**. Tutorials online describe other versions, which have
different flags, so when a command here disagrees with one you find online, use the one here:
it's the one that runs on your machine. You'll check your versions in Lab 01, Part 1.

Each of Labs 01–04 has a **package**: a folder under `labs/` with its SPICE decks, a `Makefile`
and a checker script. The packages run with `make` alone, with no environment setup, because
every deck names its SKY130 model file by absolute path. You still do Lab 01, Part 1 once, to get
the course files and check your tools. Apart from the SiliWiz parts, which run in a browser tab,
every lab step runs in a terminal, and only the optional XSchem part of Lab 03 opens a window on
the desktop. A fifth package, `passives-decks`, holds the decks whose output the guide pages
quote, and some lab parts run it too. The capstone has no package, because all it needs is one
command, a browser exercise and a page of arithmetic.

The first time you run each lab, its `make` ends in `FAIL`, and that's on purpose. Each package
ships the design a first-year student would draw, usually sized straight off the model card, so
that you read your own wrong number before you fix it. The message tells you which file to edit.

## What you'll have at the end

You'll have a filter you designed from devices a real 130 nm process can make, simulated at every
corner it will be manufactured at, with an area number you can defend. You'll also be in the habit of
asking, for each part of an analog schematic, what shape it is and what it costs.

## Next courses

- **AD103** — Nonlinear Circuits: the diode and the MOSFET, and the regions they operate in
- **AD104** — Layout: draw these devices yourself in Magic, DRC-clean and LVS-clean
