# Resistors on a chip

In ECE110 you were handed a resistor. It came out of a drawer with four coloured bands, and
someone in a factory had already decided it was 10 kΩ. Your job was to put it in a mesh and write
KCL. Every equation you learned there still holds on a chip.

What changes is where the 10 kΩ comes from. On a chip there is no drawer. A chip is one crystal
of silicon with patterns printed on it, and the only thing you can decide is what shape to
print. So "how do I get 10 kΩ?" becomes a question about geometry, and geometry costs area, and
area costs money. That is the subject of AD102; the rest is arithmetic.

## Animation: resistor geometry

This clip is **192 seconds**, silent, with captions; the captions are the narration. It covers
this page and the next two (the symbol, the strip, ohms per square, and what 100 kΩ costs in
silicon), so come back to it after you have read those as well.

<!-- The Manim animation of this movement's central idea. Renders to
     dist/ResistorGeometry.web.mp4 from tooling/manim/scenes/ad102_resistor_geometry.py;
     deploy copies it here alongside its poster frame. -->
<video controls loop muted playsinline preload="none"
       poster="../assets/img/ad102-resistor-geometry.poster.png"
       style="width:100%;max-width:820px;border-radius:8px">
  <source src="../assets/img/ad102-resistor-geometry.web.mp4" type="video/mp4">
  Your browser will not play embedded video —
  <a href="../assets/img/ad102-resistor-geometry.web.mp4">download the clip</a>.
</video>

*Source: [`tooling/manim/scenes/ad102_resistor_geometry.py`](https://github.com/uoftasic/ad102)
— `ResistorGeometry`. Every figure in it is one of this course's own measured numbers, and the
two footprints in the closing comparison are drawn to the same scale.*

Before you press play, answer this. A strip of poly 40 µm long and 2 µm wide has some
resistance. You redraw it 40 µm long and 4 µm wide. Does the resistance go up, go down, or stay
the same, and by how much? Write the number down; the animation counts it out on screen.

## What the resistor is made of

Take away the packaging and a resistor is a piece of material with current squeezing through
it. Long and thin gives high resistance; short and wide gives low resistance. The through-hole
resistor you soldered works the same way: inside is a spiral of resistive carbon film cut into a
ceramic rod, cut longer for more ohms.

On a chip, the resistive material is a **strip of doped silicon or polysilicon**, drawn as a
rectangle on one mask layer. Current goes in one end and out the other. Three things set the
value:

1. What the strip is made of, meaning how heavily it was doped. The foundry's recipe fixes this,
   not you.
2. How long you draw it.
3. How wide you draw it.

You control the length and width. For the material, you choose from a menu.

## The SKY130 resistor menu

Here is the list from the header comment of the Magic technology file,
`/foss/pdks/sky130A/libs.tech/magic/sky130A.tech`:

```
# sky130_fd_pr__res_generic_nd   rdn      n+ diff resistor
# sky130_fd_pr__res_generic_pd   rdp      p+ diff resistor
# sky130_fd_pr__res_generic_l1   rli      local interconnect resistor
# sky130_fd_pr__res_generic_po   npres    n+ poly resistor
# sky130_fd_pr__res_high_po_*    ppres    p+ poly resistor (300 Ohms/sq)
# sky130_fd_pr__res_xhigh_po_*   xres     p+ poly resistor (2k Ohms/sq)
# sky130_fd_pr__res_iso_pw       rpw      pwell resistor (in deep nwell)
```

That is seven entries: not seven values, but seven materials. The last two are on the same layer
(`p+ poly`) with the same drawing rules, and differ by a factor of about six because they get a
different implant dose. That factor of six is the only value knob the foundry hands you;
everything else you get by drawing.

`res_high_po` and `res_xhigh_po` are the **precision** resistors, the ones SkyWater
characterised carefully because analog designers build references out of them. They are the two
this course uses.

## The same strip in four materials

Draw one strip, 314.046454 µm long and 1 µm wide, and change only which resistor model it is.
Section C of
[`spice/r_head_and_body.spice`](https://github.com/uoftasic/ad102/blob/main/labs/passives-decks/spice/r_head_and_body.spice)
does exactly that:

```
--- C. one 314 um x 1 um strip, four implants (ohms) ---
r_high = 1.000000e+05
r_xhigh = 6.653872e+05
r_pdiff = 6.138915e+04
r_ndiff = 3.689775e+04
```

| model | value of that one strip |
|---|---|
| `sky130_fd_pr__res_high_po` | **100.0000 kΩ** |
| `sky130_fd_pr__res_xhigh_po` | 665.3872 kΩ |
| `sky130_fd_pr__res_generic_pd` (p+ diffusion) | 61.38915 kΩ |
| `sky130_fd_pr__res_generic_nd` (n+ diffusion) | 36.89775 kΩ |

Same drawing, same silicon area, an 18:1 spread in value. Choosing the material is the first
design decision, and it is the only one that does not cost area. You'll run this deck yourself
in [Lab 01, Part 6](../labs/lab-01-a-resistor-you-designed-overview.md#part-6-split-a-resistor-into-head-and-body).

When you do, the run prints a block of model warnings first (see
[Getting started](../guide/getting-started.md#expected-warnings)). The `rbody_model` warning shows
`rsh` as `3.173885e+02`. That number is the sheet resistance of `res_high_po` in ohms per
square: the most important parameter of the device, sitting in a warning you would normally
scroll past.

## Writing W and L

On a SKY130 device, `W` and `L` are plain micron numbers with no unit suffix:

```
Xa a 0 0 sky130_fd_pr__res_high_po W=1 L=10       <- one micron by ten microns
Xa a 0 0 sky130_fd_pr__res_high_po W=1u L=10u     <- a millionth of that, in both
```

Every deck in this course uses the first form. The second multiplies both numbers by 10⁻⁶ and
puts the device outside every bin its model was fitted over. On a MOSFET that stops the run with
`could not find a valid modelname`. On a resistor the run does not stop: the strip that reads
3550.443 Ω written `W=1 L=10` reads 3193.812 Ω written `W=1u L=10u`, an ordinary-looking
resistance 10 % off, and ngspice still exits with status 0.
[Getting started](../guide/getting-started.md#the-u-suffix-trap) goes through it in detail. Apart
from Lab 01's `u_trap.spice`, which exists to show the mistake, there is no `u` in any deck in
this course, and there should be none in yours.

Next: [Ohms per square](../guide/ohms-per-square.md), the unit that turns a rectangle into ohms.
