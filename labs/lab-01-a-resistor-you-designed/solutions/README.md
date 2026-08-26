# Reference sizing — read this after your own numbers pass

`my_resistor.spice` in this folder is one correct answer. It is not the
interesting part. These are.

## Why the end resistance is one number and not two

`sky130_fd_pr__res_high_po` is a subcircuit with exactly two resistors in it:
a `rhead` and a `rbody`. Not two heads — **one**. A real drawn resistor
obviously has a contact at each end, so where did the other one go?

Nowhere, and that is the point. Look at how `rhead` is declared:

```
rhead r0 rb rhead_model w = {weff+0.1558} l = 1.0
```

`l = 1.0` is not a length in your layout — nothing in your layout is 1 µm long
unless you drew it that way. It is a fitting constant. Whatever both contacts
actually contribute was measured on real silicon and squeezed into the single
number `rsh = 345.8312`, with `l` pinned at 1 so that the width is the only
thing left to vary. **A compact model is a curve fit that reproduces measured
silicon, not a picture of it.** You cannot read layout out of a `.model` line,
and every time you try you will invent a device that does not exist.

## Why we told you to fix `W` at 1 µm

Because otherwise the honest answer to "design a 2.2 kΩ resistor" is *"at what
width?"*, and the lab would have no single right answer. Width is a real
degree of freedom, and here is what it buys and costs — every number measured
by the deck you already ran:

| W (µm) | Ω per µm of length | end Ω | µm² of body per kΩ | Ω per **square** |
|---|---|---|---|---|
| 0.35 | 971.641 | 958.562 | 0.3602 | 340.074 |
| 0.69 | 459.946 | 523.544 | 1.5002 | 317.362 |
| 1 | 317.220 | 378.245 | 3.1524 | 317.220 |
| 2 | 158.530 | 199.875 | 12.6159 | 317.061 |
| 5 | 63.393 | 82.841 | 78.8728 | 316.966 |

Every one of those is a straight line through the two points your own
`make sheet` printed under `--- C. width ladder ---` and
`--- C2. the same four widths at L = 5 um ---`. Fit it yourself; it takes two
subtractions.

Three things fall out of that table.

**Ω per square is the same for every width down to 0.69 µm — and then it is
not.** 317.362, 317.220, 317.061, 316.966: flat to a tenth of a percent. At
W = 0.35 µm it is **340.074**, seven percent high. The model applies
`weff = w − 0.001 − 0.0672 × (0.69 − w)` below 0.69 µm, so a strip drawn
0.35 µm wide conducts as if it were 0.326 µm wide. Lithography and etch do not
deliver the width you drew, and the model card knows it. "Sheet resistance is
a constant" is true in the middle of the range and false at the edge of it.

**Density is set by width and nothing else.** 0.36 µm² per kΩ at 0.35 µm
against 78.87 µm² per kΩ at 5 µm — a factor of **219** for the same material.
Halving the width quarters the area for a given resistance, because you win
once on width and once again on the length you no longer need.

**The end resistance does not scale away.** It falls with width, but only
about as 1/W, so as a *fraction* of a fixed-value resistor it is roughly
constant. You never outrun it by choosing a different width; you outrun it by
drawing more squares.

A real design fixes width from the matching and current-density requirements
first, and *then* solves for length. Lab 04 is where that requirement comes
from.

## Why not just use `res_xhigh_po` for everything

It is 6.7× denser. It is also the device with `vc1_body = -1.00e-3` in its
model card — a **voltage coefficient**. Its resistance depends on the voltage
across it, by about 0.1 % per volt. `res_high_po` has no such term.

So: a bias string that never moves, or a gate pull-up, is happy in `xhigh`. A
resistor inside a signal path, where the voltage across it *is* the signal, is
not — a resistance that varies with signal is distortion. Cheap and linear are
different axes, and the PDK gives you one device on each.

## What to argue about

- Should `check_res.py` accept 1 % on a resistor? Real precision resistors on
  a chip are trimmed or ratioed, never absolute. What tolerance would you
  defend to a colleague, and would you defend the same number for a bias
  string and for a gain-setting element?
- The lab measured at 27 °C. `res_high_po` has `tc1 = 0.514e-3` and a part
  qualified to 125 °C is not unusual. Work out what your 2.2 kΩ becomes at
  125 °C before you look at Lab 03, which measures it.
