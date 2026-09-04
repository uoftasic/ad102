# AD102 — Linear Circuits & Fabrication

You already know what a resistor *does*. This course is about what one **is** when it is built
on silicon — and what it costs.

Part of the **UofT ASIC Team** education materials. Published at **https://uoftasic.com/ad102/**.
Labs run inside the shared **workspace** you set up in [IC101](https://uoftasic.com/ic101/).

## The angle, stated plainly

ECE110 gives you linear circuit analysis: node voltages, mesh currents, $V = IR$, RC time
constants, impedance. **AD102 does not re-teach any of that**, and it is not a substitute for
that course. If you have taken ECE110 you are ahead; if you have not,
[AD101](https://uoftasic.com/ad101/) already gave you everything this course actually leans on.

What ECE110 does *not* tell you is where the components come from. In a lab kit a resistor is a
part you pull out of a drawer, and its value is printed on the side. **On a chip there is no
drawer.** A resistor is a strip of doped polysilicon that you draw, and its value is a
consequence of that drawing — how long, how wide, and which layer you drew it on. Change the
shape and you change the value. There is no other knob.

That is the whole course: **a component value is a geometry, and geometry costs area.**

> **The belief you are bringing, and where it breaks.** On a breadboard, component values are
> free and independent: a 10 kΩ costs the same as a 100 Ω, and you can have as many as you
> like. On silicon, neither is true.
>
> A **1 pF capacitor** — the smallest value anyone would bother naming in a filter — is a
> 22 µm × 22 µm plate: **484 µm²** of silicon, which simulates at **982.5022 fF**. The entire
> 4-bit ripple adder the digital track builds in [DD103](https://uoftasic.com/dd103/) fits in
> **110.1056 µm²** of the same process. One capacitor, **4.4 adders' worth of chip**.
>
> Every analog habit you are about to learn — ratios instead of values, unit devices, and the
> reason nobody puts an inductor on a chip — falls out of that one comparison.

## At a glance

| | |
|---|---|
| **Track** | Analog |
| **Prerequisites** | [IC101](https://uoftasic.com/ic101/) then [AD101](https://uoftasic.com/ad101/), in that order |
| **Tools** | ngspice, XSchem, SiliWiz — all inside the workbench, plus one browser tab |
| **PDK** | SKY130 (`sky130A`), baked into the image |
| **Time** | 12–16 hours, self-paced |
| **Math** | Algebra, $V=IR$, and the $R$ / $C$ / frequency reading you did in AD101. No calculus. |

> **This course is pinned to the workbench image `hpretl/iic-osic-tools:2026.08`**, which ships
> **ngspice-47** and **XSchem V3.4.8RC**. Tutorials online describe other versions with
> different flags. When a command here disagrees with the internet, the command here is the one
> that runs on your machine.
>
> Check yours: `ngspice -v | head -2` should say `ngspice-47`.

> **All four labs run with `make` alone**, in a bare container, with no environment setup at
> all — every deck names its SKY130 model file by absolute path. If a setup command fails, try
> `make` anyway. Only the optional XSchem step at the end of Lab 03 needs the desktop.
>
> **On a fresh clone, every lab's first `make` ends in `FAIL`, and that is the lab.** Each
> package ships the design a first-year actually draws — the one sized straight off the model
> card — so that you get to read your own wrong number before you fix it. The verdict tells you
> which line to edit. A package that printed `PASS` before you had done anything would have
> taught you nothing.

## What you'll do

1. Measure the **sheet resistance** of SKY130 high-sheet poly yourself. The model card says
   **317.3885 Ω per square**. Draw exactly one square and ngspice says **695.4646 Ω** — more
   than twice as much. Find out where the extra ohms live, then size a 10 kΩ correctly on the
   first try (it is **30.3315 µm** long, and it lands at **9999.997 Ω**)
2. Find out what a **picofarad costs in square micrometres**, and why nobody puts a 10 µF on a chip
3. Build an RC filter out of the resistor and the capacitor **you designed**, measure its time
   constant, then measure its corner frequency and watch the two agree to six figures — with
   its Bode plot laid over the ideal one you drew in AD101 (**15.8580 MHz** against
   **15.9155 MHz**, 0.36 % apart). Then open the same circuit in **XSchem** and watch a picture
   turn into the netlist you had been typing by hand
4. Watch the same resistor come out **different at every process corner**, and learn the trick
   analog designers use to stop caring: build **ratios**, not values
5. Answer the charter's third question — *how do you fabricate an inductor?* — with the honest
   answer, which is mostly **"you don't, and here is what you build instead"**
6. Hit a filter spec using only devices the PDK actually ships, inside an area budget you have
   to defend

## Path

| Part | Guide | Lab |
|------|-------|-----|
| 0 | [Getting started](guide/getting-started.md) | — |
| I — A value is a shape | [A resistor you cannot buy](guide/a-resistor-you-cannot-buy.md) · [Ohms per square](guide/ohms-per-square.md) · [What a value costs in area](guide/what-a-value-costs-in-area.md) | [Lab 01 — A resistor you designed](labs/lab-01-a-resistor-you-designed-overview.md) |
| II — Two plates and a gap | [A capacitor is a sandwich](guide/a-capacitor-is-a-sandwich.md) · [What a picofarad costs](guide/what-a-picofarad-costs.md) · [The capacitor you did not draw](guide/the-capacitor-you-did-not-draw.md) | [Lab 02 — How big is a picofarad?](labs/lab-02-how-big-is-a-picofarad-overview.md) · [Lab 03 — A time constant in silicon](labs/lab-03-a-time-constant-in-silicon-overview.md) |
| III — The one you don't build | [The inductor problem](guide/the-inductor-problem.md) · [What analog builds instead](guide/what-analog-builds-instead.md) | [Lab 02](labs/lab-02-how-big-is-a-picofarad-overview.md), steps 6–7 (`make henry`, `make tank`) |
| IV — Nothing comes out the value you drew | [The value you drew is not what you get](guide/the-value-you-drew-is-not-what-you-get.md) · [Matching beats accuracy](guide/matching-beats-accuracy.md) | [Lab 04 — Two resistors that disagree](labs/lab-04-two-resistors-that-disagree-overview.md) |
| Capstone | [From schematic to cross-section](guide/from-schematic-to-cross-section.md) | — (browser exercise, no package) |

**Stuck?** Ask in the [team Discord](https://discord.gg/hrJnP5UsGz). Nobody expects you to work
this out alone at 2 a.m. — see [Getting help](guide/getting-started.md#getting-help).

Cheat sheets: [The SKY130 passive catalogue](reference/sky130-passive-catalogue.md) ·
[ngspice decks that actually run](reference/ngspice-decks-that-run.md)

## Quick start

```bash
# in the noVNC desktop, after IC101 and AD101
. /foss/designs/common/.designinit
mod add ad102          # first time only
mod ad102
ngspice -v | head -2    # expect: ** ngspice-47 : Circuit level simulation program
cd labs/lab-01-a-resistor-you-designed && make
```

## What you'll have at the end

A filter you designed that is built only from devices a real 130 nm process can make, simulated
at every corner it will be manufactured at, with an area number you can defend — plus the habit
of asking, about any analog schematic anyone shows you, *"what shape is that, and what does it
cost?"*

## Next courses

- **AD103** — Nonlinear Circuits: the diode and the MOSFET, and the regions they live in
- **AD104** — Layout: draw these devices yourself in Magic, DRC-clean and LVS-clean
