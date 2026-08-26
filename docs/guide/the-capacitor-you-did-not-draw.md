# The capacitor you did not draw

**Question this page answers:** *If a capacitor is just two conductors near each
other, then isn't every wire on my chip a capacitor?*

Yes. All of them. To the substrate, to the wires above, to the wires below, and to
the wires running alongside. You did not draw any of them and you cannot delete
them. They are called **parasitics**, and on a modern chip they are usually the
dominant capacitance in the design.

This is not a footnote. It is the reason digital chips have a clock ceiling, the
reason a layout that passes DRC can still be slow, and the reason AD104 exists.

## The numbers are in the PDK, unhidden

`/foss/pdks/sky130A/libs.tech/ngspice/parameters/typical.spice`, lines 2876–2902.
Area terms are in F/m², sidewall terms in F/m:

```
+ cp1f = 1.06e-04  cp1fsw = 8.64e-11
+ cl1f = 3.69e-05  cl1fsw = 8.30e-11
+ cm1f = 2.58e-05  cm1fsw = 1.07e-10
+ cm2f = 1.75e-05  cm2fsw = 1.08e-10
+ cm5f = 6.48e-06  cm5fsw = 7.85e-11
+ cm2m1 = 1.28e-04 cm2m1sw = 1.03e-10
```

Converted to the units a layout engineer thinks in (1 F/m² = 1e-12 F/µm²,
1 F/m = 1e-6 F/µm):

| coupling | area | fringe, per edge |
|---|---:|---:|
| poly → substrate (`cp1f`) | 0.106 fF/µm² | 0.0864 fF/µm |
| li → substrate (`cl1f`) | 0.0369 fF/µm² | 0.0830 fF/µm |
| met1 → substrate (`cm1f`) | 0.0258 fF/µm² | 0.107 fF/µm |
| met2 → substrate (`cm2f`) | 0.0175 fF/µm² | 0.108 fF/µm |
| met5 → substrate (`cm5f`) | 0.00648 fF/µm² | 0.0785 fF/µm |
| met2 → met1 (`cm2m1`) | 0.128 fF/µm² | 0.103 fF/µm |

Compare the top of that table to a MIM capacitor at **2.00 fF/µm²**. Met1 to
substrate is 0.0258 — **78 times less dense**. Which is exactly what you want: the
purpose-built capacitor should beat the accident. But "78 times less dense" is not
"zero", and you have an enormous amount of wire.

## The fringe wins, and that surprises everyone

Take a met1 wire at minimum width. The PDK states it one directory up, in
`libs.tech/ngspice/sky130_fd_pr__model__r+c.model.spice`, as `wminm1= 0.14u`. Run it
1000 µm across the chip.

- **Plate area:** $1000 \times 0.14 = 140$ µm², times 0.0258 fF/µm² = **3.61 fF**
- **Fringe:** two edges, 1000 µm each, times 0.107 fF/µm = **214.0 fF**

Total ≈ **217.6 fF**, of which the parallel-plate part you would have calculated
from $\varepsilon A/d$ is **1.7 %**.

**Predict → be wrong.** Almost everyone sizes a wire's capacitance from its area,
because that is the formula on the previous page. For a minimum-width wire it is off
by a factor of sixty. The reason is geometric: the wire is 0.14 µm wide and it sits
on the order of a micron above the substrate. It is not a *plate*; it is a *string*,
and most of its field leaves through the sides. `cm1fsw` is that field, measured and
tabulated by SkyWater, and it is why extraction tools exist.

**The reflex:** *for anything narrower than it is tall, sidewall capacitance
dominates. Use the `*sw` term, not the area term.*

## What it costs you

Put that wire on the output of the smallest inverter. `sky130_fd_sc_hd__inv_1`
drives roughly a few femtofarads of gate load comfortably. Now hang 217.6 fF on it —
call it fifty times its natural load — and the rise time goes up by roughly the same
factor. That is the entire mechanism behind "long wires are slow", and it is why
place-and-route tools spend most of their effort on wire length rather than gate
count.

It is also a resistance problem at the same time. That same 1000 µm of minimum-width
met1 is $1000/0.14 = 7143$ squares at 0.125 Ω/□ = **893 Ω** (see
[Ohms per square](guide/ohms-per-square.md)). A wire is a distributed RC line, not a
node, and the delay through it grows as the *square* of its length.

## Try this: see the layers

The parasitic story is a picture problem, not an equation problem — you have to see
that a wire is a bar hanging over a plane. **SiliWiz** draws the cross-section live:

**<https://app.siliwiz.com/?preset=blank>**

1. Draw a **metal2** rectangle. Draw a second one beside it, not touching.
2. Label one **in** and the other **out** (click, then **Set Label** or press `S`).
3. Tick **Show SPICE** at the bottom and look for a line starting `C0 out in`. That
   is the coupling between two wires you never intended to connect.
4. Drag them closer together and watch the number climb.
5. Now put one on **metal1** and the other on **metal2**, overlapping. The
   capacitance *falls* — the vertical gap between metal layers is bigger than the
   horizontal gap you can draw between two wires on the same layer.

There is a guided walkthrough at <https://tinytapeout.com/siliwiz/parasitics/>, and
the capacitor construction tutorial at
<https://tinytapeout.com/siliwiz/capacitors/> builds the same three sandwiches this
movement described.

> **Same warning as before: SiliWiz is not SKY130.** Its layer stack, its
> permittivities and its numbers are simplified for teaching. Read it for the
> *shape* of the answer — "closer is more, thicker gap is less, edges matter" — and
> read `typical.spice` for the value.

## The two useful consequences

**One.** Parasitic capacitance is the *reason* a VPP capacitor works. If ordinary
metal wires unavoidably couple to their neighbours at 0.1 fF per micron of edge,
then you can stop fighting it and start using it: interleave enough fingers and the
accident becomes the component. `sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5`
measured **147.3400 fF** in [the previous
page's run](guide/a-capacitor-is-a-sandwich.md), built entirely out of wire.

**Two.** Every number on this page came from a *pre-characterised table*, because
the real value depends on what happens to be nearby. That is what a **parasitic
extraction** (PEX) run does: read your finished layout, work out every one of these
couplings for the actual shapes you drew, and hand back a netlist with hundreds of
capacitors your schematic never had. AD104 runs one and compares the before and
after.

## Why an engineer cares

There is a moment in every chip designer's education where a circuit that simulated
perfectly comes back from extraction 40 % slower, and nothing in the schematic
changed. This page is that moment, arriving early and on purpose.

Next: [The inductor problem](guide/the-inductor-problem.md) — the component whose
parasitics are so bad that the usual advice is *don't*.
