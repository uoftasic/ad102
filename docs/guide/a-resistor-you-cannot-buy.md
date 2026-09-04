# A resistor you cannot buy

**Question this page answers:** *I have written `R1 = 10k` a hundred times. What is
that, physically, on a chip?*

In ECE110 you were handed a resistor. It came out of a drawer, it had four coloured
bands, and someone in a factory had already decided it was 10 kΩ. Your job was to
put it in a mesh and write KCL. That skill is not going anywhere — every equation
you learned still holds, unchanged, on a chip.

What changes is where the 10 kΩ comes from. **There is no drawer.** A chip is one
crystal of silicon with patterns printed on it, and the only thing you can do is
decide what shape to print. So the question "how do I get 10 kΩ" turns into a
question about *geometry* — and geometry costs area, and area costs money.

That is the whole of AD102 in one sentence. Everything else is arithmetic.

## Watch this first

**192 seconds**, silent, captioned. The captions are the narration, so read rather than
listen. It covers this whole movement — the symbol, the strip, ohms per square, and what
100 kΩ costs in silicon — so come back to it after the next two pages as well.

<!-- The Manim animation of this movement's central idea. Renders to
     dist/ResistorGeometry.web.mp4 from tooling/manim/scenes/ad102_resistor_geometry.py;
     deploy copies it here alongside its poster frame. -->
<video controls loop muted playsinline preload="none"
       poster="assets/img/ad102-resistor-geometry.poster.png"
       style="width:100%;max-width:820px;border-radius:8px">
  <source src="assets/img/ad102-resistor-geometry.web.mp4" type="video/mp4">
  Your browser will not play embedded video —
  <a href="assets/img/ad102-resistor-geometry.web.mp4">download the clip</a>.
</video>

*Source: [`tooling/manim/scenes/ad102_resistor_geometry.py`](https://github.com/uoftasic/ad102)
— `ResistorGeometry`. Every figure in it is one of this course's own measured numbers, and
the two footprints in the closing comparison are drawn to the same scale.*

**Before you press play, answer this.** A strip of poly 40 µm long and 2 µm wide has some
resistance. You redraw it 40 µm long and 4 µm wide. Does the resistance go up, down, or stay
the same — and by how much? Write the number down. The animation counts it out on screen.

## What is actually down there

Strip away the packaging and a resistor is a piece of material with current
squeezing through it. Long and thin: hard, high resistance. Short and fat: easy,
low resistance. The carbon film inside the through-hole part you soldered is
exactly this — a spiral of resistive film cut into a ceramic rod, cut longer for
more ohms.

On a chip, the resistive material is a **strip of doped silicon or poly-silicon**,
drawn as a rectangle on one mask layer. Current goes in one end, out the other. The
value is set by three things:

1. **What the strip is made of** — how heavily it was doped, which is fixed by the
   foundry recipe, not by you.
2. **How long you draw it.**
3. **How wide you draw it.**

You control (2) and (3). You choose from a menu for (1).

## The menu SKY130 actually offers

Here is the list, taken from the header comment of the Magic technology file at
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

Seven entries. Not seven thousand values — **seven materials**. Look at the last
two: same layer (`p+ poly`), same drawing rules, and a factor of about six between
them, because they get a different implant dose. That factor of six is the only
value knob a foundry hands you. Everything else you get by drawing.

Two of those names, `res_high_po` and `res_xhigh_po`, are the *precision* resistors
— the ones SkyWater characterised carefully because analog designers were going to
build references out of them. They are the two this course uses.

## The same rectangle, four recipes

Draw one strip: **314.046454 µm long, 1 µm wide**. Do not change a single
coordinate. Just change which resistor model the strip is. From
[`spice/r_head_and_body.spice`](https://github.com/uoftasic/ad102/blob/main/labs/passives-decks/spice/r_head_and_body.spice):

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

Same drawing. Same silicon area. An 18:1 spread in value. Choosing the recipe is
the first design decision, and it is the only one that does not cost area.

## Try this

You need the workbench — `hpretl/iic-osic-tools:2026.08` — and nothing else.

```bash
cd labs/passives-decks
make resistor
```

**What you should see:** about a minute of complete silence, then the block above.

Two things in that silence that are **not** bugs, and are worth expecting:

- **ngspice prints nothing for roughly 60 seconds.** `.lib sky130.lib.spice tt`
  pulls in about 12 MB of model cards for every device SKY130 has, nearly all of
  them MOSFETs you are not using. It is loading, not hung.
- **A wall of `unrecognized parameter` warnings.** Exactly **100** of them for this
  deck, in blocks like

  ```
  Warning: Model issue on line 4841 :
    .model xa:rbody_model r sw_et=0 isnoisy=0 rsh=    3.173885000000000e+02  ...
  unrecognized parameter (sw_et) - ignored
  unrecognized parameter (isnoisy) - ignored
  unrecognized parameter (p2) - ignored
  ```

  Count them yourself:

  ```bash
  grep -c 'unrecognized parameter' results/r_head_and_body.log
  ```

  SkyWater writes one model card for several simulators. `sw_et`, `isnoisy`, `p2`,
  `q2`, `p3` and `q3` describe self-heating, noise and the voltage coefficients in
  a Spectre dialect ngspice does not implement. It says so, ignores them, and uses
  the rest. **An `Error` at the start of a line is a different matter — that one is
  real.**

**Why an engineer cares:** the number in that warning, `3.173885e+02`, is the sheet
resistance of `res_high_po` in ohms per square. The simulator just told you the
single most important parameter of the device, in the middle of a warning you were
about to scroll past.

## The trap, before you hit it

On a SKY130 device, `W` and `L` are **plain micron numbers with no unit suffix**:

```
Xa a 0 0 sky130_fd_pr__res_high_po W=1 L=10       <- one micron by ten microns
Xa a 0 0 sky130_fd_pr__res_high_po W=1u L=10u     <- a millionth of that, in both
```

Every deck in this course is written the first way. The second way multiplies both
numbers by 10⁻⁶ and puts the device outside every bin its model was fitted over. On
a MOSFET that stops the run with

```
could not find a valid modelname
    Simulation interrupted due to error!
```

On a resistor it does something worse: it does not stop. The same strip that reads
**3550.443 Ω** written `W=1 L=10` reads **3193.812 Ω** written `W=1u L=10u` — an
entirely ordinary-looking resistance **10 % off**, with ngspice still exiting `0`.
The full autopsy is in
[Getting started, step 5](guide/getting-started.md#5-the-trap-that-will-cost-you-an-afternoon-u).
There is no `u` anywhere in any deck in this course, and there should be none in
yours.

## Where this is going

You now know a resistor is a rectangle of a chosen material. The next page gives
you the unit that turns a rectangle into ohms — **ohms per square**, which is not a
typo and not a unit of area.

Next: [Ohms per square](guide/ohms-per-square.md).
