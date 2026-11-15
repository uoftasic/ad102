# Parasitic capacitance

If a capacitor is just two conductors near each other, then every wire on a chip is a capacitor.
It has capacitance to the substrate, to the wires above and below it, and to the wires running
alongside. You did not draw any of these and you cannot delete them. They are called
**parasitics**, and on a modern chip they are usually the largest capacitance in the design.

Parasitics are why digital chips have a maximum clock rate, why a layout that passes DRC can
still be slow, and why AD104 exists.

## Parasitic capacitance in the PDK

The numbers are in `/foss/pdks/sky130A/libs.tech/ngspice/parameters/typical.spice`, lines
2876–2902. Area terms are in F/m², sidewall terms in F/m:

```
+ cp1f = 1.06e-04  cp1fsw = 8.64e-11
+ cl1f = 3.69e-05  cl1fsw = 8.30e-11
+ cm1f = 2.58e-05  cm1fsw = 1.07e-10
+ cm2f = 1.75e-05  cm2fsw = 1.08e-10
+ cm5f = 6.48e-06  cm5fsw = 7.85e-11
+ cm2m1 = 1.28e-04 cm2m1sw = 1.03e-10
```

Converted to the units a layout engineer uses (1 F/m² = 1e-12 F/µm², 1 F/m = 1e-6 F/µm):

| coupling | area | fringe, per edge |
|---|---:|---:|
| poly → substrate (`cp1f`) | 0.106 fF/µm² | 0.0864 fF/µm |
| li → substrate (`cl1f`) | 0.0369 fF/µm² | 0.0830 fF/µm |
| met1 → substrate (`cm1f`) | 0.0258 fF/µm² | 0.107 fF/µm |
| met2 → substrate (`cm2f`) | 0.0175 fF/µm² | 0.108 fF/µm |
| met5 → substrate (`cm5f`) | 0.00648 fF/µm² | 0.0785 fF/µm |
| met2 → met1 (`cm2m1`) | 0.128 fF/µm² | 0.103 fF/µm |

A MIM capacitor is 2.00 fF/µm². Met1 to substrate is 0.0258 fF/µm², 78 times less dense. That
is what you want: the purpose-built capacitor should beat the accidental one. But 78 times less
dense is not zero, and a chip has an enormous amount of wire.

## Fringe capacitance of a thin wire

Take a met1 wire at minimum width. The PDK gives that width one directory up, in
`libs.tech/ngspice/sky130_fd_pr__model__r+c.model.spice`, as `wminm1= 0.14u`. Run it 1000 µm
across the chip.

- **Plate area:** $1000 \times 0.14 = 140$ µm², times 0.0258 fF/µm² = 3.61 fF
- **Fringe:** two edges, 1000 µm each, times 0.107 fF/µm = 214.0 fF

The total is about 217.6 fF, and the parallel-plate part you would have calculated from
$\varepsilon A/d$ is 1.7 % of it.

Almost everyone first estimates a wire's capacitance from its area, because that is the formula
from the previous page. For a minimum-width wire that estimate is off by a factor of sixty. The
reason is geometric: the wire is 0.14 µm wide and sits on the order of a micron above the
substrate. It is more like a string than a plate, and most of its field leaves through the
sides. `cm1fsw` is that field, measured and tabulated by SkyWater, and it is why extraction tools
exist.

The rule: for anything narrower than it is tall, sidewall capacitance dominates. Use the `*sw`
term, not the area term.

## What a long wire costs

Put that wire on the output of the smallest inverter, `sky130_fd_sc_hd__inv_1`, which drives a
few femtofarads of gate load comfortably. Hang 217.6 fF on it, roughly fifty times its normal
load, and the rise time goes up by roughly the same factor. That is the mechanism behind "long
wires are slow", and it is why place-and-route tools spend most of their effort on wire length
rather than gate count.

The same wire is a resistance problem too. 1000 µm of minimum-width met1 is $1000/0.14 = 7143$
squares at 0.125 Ω/□ = 893 Ω (see [Ohms per square](../guide/ohms-per-square.md)). A wire is a
distributed RC line, not a single node, and the delay through it grows as the square of its
length.

You can draw two wires in SiliWiz and watch their coupling capacitance change as you move them in
[Lab 02, Part 9](../labs/lab-02-how-big-is-a-picofarad-overview.md#part-9-optional-parasitic-capacitance-in-siliwiz).

## VPP capacitors and parasitic extraction

First, parasitic capacitance is why a VPP capacitor works. If ordinary metal wires couple to
their neighbours at about 0.1 fF per micron of edge whether you like it or not, you can use that
on purpose: interleave enough fingers and the accident becomes the component.
`sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5` measured 147.3400 fF on
[Capacitors on a chip](../guide/a-capacitor-is-a-sandwich.md), built entirely out of wire.

Second, every number on this page came from a pre-characterised table, because the real value
depends on what happens to be nearby. A **parasitic extraction** (PEX) run reads your finished
layout, works out these couplings for the shapes you actually drew, and hands back a netlist
with hundreds of capacitors your schematic never had. AD104 runs one and compares the before and
after.

Every chip designer at some point sees a circuit that simulated perfectly come back from
extraction 40 % slower, with nothing in the schematic changed. This page is meant to prepare you
for that.

Next: [Inductors on a chip](../guide/the-inductor-problem.md).
