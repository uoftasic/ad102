# Reference sizing (read this after your own numbers pass)

`my_resistor.spice` in this folder is one correct answer. The notes below are the more useful
part.

## Why the model has one head resistor

`sky130_fd_pr__res_high_po` is a subcircuit with exactly two resistors in it: a `rhead` and a
`rbody`. There is only one head, even though a real drawn resistor has a contact at each end.

Look at how `rhead` is declared:

```
rhead r0 rb rhead_model w = {weff+0.1558} l = 1.0
```

`l = 1.0` looks like a length, but nothing in your layout is 1 µm long unless you drew it that
way; it's a fitting constant. Whatever both contacts contribute was measured on real silicon and
folded into the single number `rsh = 345.8312`, with `l` pinned at 1 so that width is the only
thing left to vary. A compact model is a curve fit that reproduces measured silicon rather than a
picture of it, so you can't read the layout out of a `.model` line, and if you try, you'll invent
a device that doesn't exist.

## Why the lab fixes W at 1 µm

Without that, the honest answer to "design a 2.2 kΩ resistor" is "at what width?", and the lab
would have no single right answer. Width is a real degree of freedom, and the table below shows
what it buys and what it costs. Every number in it was measured by the deck you already ran:

| W (µm) | Ω per µm of length | end Ω | µm² of body per kΩ | Ω per **square** |
|---|---|---|---|---|
| 0.35 | 971.641 | 958.562 | 0.3602 | 340.074 |
| 0.69 | 459.946 | 523.544 | 1.5002 | 317.362 |
| 1 | 317.220 | 378.245 | 3.1524 | 317.220 |
| 2 | 158.530 | 199.875 | 12.6159 | 317.061 |
| 5 | 63.393 | 82.841 | 78.8728 | 316.966 |

Each row is a straight line through the two points your `make sheet` printed under
`--- C. width ladder, L = 10 um (ohms) ---` and `--- C2. the same four widths at L = 5 um (ohms) ---`.
Fit it yourself; it takes two subtractions.

Three things follow from that table.

**Ω per square is the same for every width down to 0.69 µm, but not below it.** The values
317.362, 317.220, 317.061 and 316.966 agree to a tenth of a percent, while at W = 0.35 µm it is
340.074, seven percent high. The model applies `weff = w − 0.001 − 0.0672 × (0.69 − w)` below 0.69 µm, so a
strip drawn 0.35 µm wide conducts as if it were 0.326 µm wide. Lithography and etch do not
deliver the width you drew, and the model card accounts for it. "Sheet resistance is a constant"
is true in the middle of the range and false at the edge.

**Density is set by width alone.** 0.36 µm² per kΩ at 0.35 µm, against 78.87 µm² per kΩ at
5 µm: a factor of 219 for the same material. Halving the width quarters the area for a given
resistance, because you win once on width and again on the length you no longer need.

**The end resistance does not scale away.** It falls with width, but only about as 1/W, so as a
fraction of a fixed-value resistor it stays roughly constant. You can't get rid of it by choosing
a different width, only by drawing more squares.

A real design fixes width from the matching and current-density requirements first, and then
solves for length. Lab 04 is where the matching requirement comes from.

## Why not use `res_xhigh_po` for everything

It's 6.7 times denser, but it's also the device with `vc1_body = -1.00e-3` in its model card.
That term is a **voltage coefficient**: the resistance depends on the voltage across it, by about
0.1 % per volt. `res_high_po` has no such term.

A bias string that never moves, or a gate pull-up, is fine in `xhigh`. A resistor inside a signal
path is a different matter, because there the voltage across it is the signal, and a resistance
that varies with the signal distorts it. Cheap and linear are separate properties, and the PDK
gives you one device for each.

## Questions to argue about

- Should `check_res.py` accept 1 % on a resistor? Real precision resistors on a chip are trimmed
  or ratioed, never absolute. What tolerance would you defend to a colleague, and would you
  defend the same number for a bias string and for a gain-setting element?
- The lab measured at 27 °C. `res_high_po` has `tc1 = 0.514e-3`, and a part qualified to 125 °C
  is not unusual. Work out what your 2.2 kΩ becomes at 125 °C before you get to Lab 03, which
  measures it.
