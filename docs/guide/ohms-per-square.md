# Ohms per square

This page explains the unit "Ω/□", and why chip designers work with it instead of with
resistivity.

Start from the physics you already know. A block of material with resistivity $\rho$, length
$L$ and cross-section $A$ has a resistance of

$$R = \rho \frac{L}{A}$$

On a chip the block is a thin film, and its thickness $t$ was fixed by the foundry. You can't
change it, and it's the same for every device on the wafer, so it makes sense to write the
cross-section as width × thickness, $A = W t$:

$$R = \rho \frac{L}{W t} = \left(\frac{\rho}{t}\right)\frac{L}{W} = R_{\square}\,\frac{L}{W}$$

That gathers the two things you can't control, $\rho$ and $t$, into one number:

$$R_{\square} = \frac{\rho}{t} \qquad \text{units: } \frac{\Omega\,\text{m}}{\text{m}} = \Omega$$

$R_\square$ is called **sheet resistance** and is quoted in "ohms per square", written **Ω/□**.
Its dimensions are plain ohms. The "per square" doesn't mean you divide by anything; it's a
reminder of what the number describes, which the next section explains.

## Why it is called "per square"

If you set $L = W$ in $R = R_\square L/W$, the width cancels:

$$R = R_{\square}$$

A square of the material has the same resistance no matter how big the square is. A 1 µm × 1 µm
square of poly and a 500 µm × 500 µm square of the same poly have identical resistance. Making
the square wider adds parallel paths, making it longer in proportion adds series length, and the
two effects cancel exactly.

So $L/W$ is the **number of squares you drew end to end**. A strip 40 µm long and 2 µm wide is
twenty squares in series, and that stays true whether you fold it, bend it, or run it across the
whole die.

That's what makes the unit useful. It turns an electrical question into a counting question,
and counting squares is something you can do by looking at a drawing.

The animation on [Resistors on a chip](../guide/a-resistor-you-cannot-buy.md#animation-resistor-geometry)
shows this happening. It draws the squares onto a strip and numbers them, then stretches the
strip and widens it, and you can watch the count and the resistance move together. Then it grows
the length and width at the same time, so the count stays at one square and the resistance stays
at 317 Ω while the shape grows ten-fold. (That 317 Ω is the sheet resistance alone; the contacts
add to it, as the head-and-body section below shows.) If counting squares still seems odd,
watch that part of the animation.

## Sheet resistance of the SKY130 layers

The sheet resistance of every layer ships with the PDK. These numbers come from
`/foss/pdks/sky130A/libs.tech/magic/sky130A.tech`, the technology file for Magic (the layout tool
you'll use in AD104). The block that lists them starts with the comment
*"# Resistances are in milliohms per square"*, and here it is, abridged:

```
 resist (pwell,isosub)/well     4400000
 resist (nwell)/well             950000
 resist (*ndiff,nsd)/active      120000
 resist (*pdiff,*psd)/active     197000
 resist mrp1/active               48200
 resist xhrpoly/active           319800
 resist uhrpoly/active          2000000
 resist (allli)/locali            12800
 resist (allm1)/metal1              125
 resist (allm3)/metal3               47
 resist (allm5)/metal5               29
 resist mrdl/metali                   5
```

Divided by 1000 to give ohms per square, and sorted from highest to lowest:

| layer | $R_\square$ (Ω/□) | ratio to met1 |
|---|---:|---:|
| p-well | 4400 | 35 200 |
| `uhrpoly`, the `res_xhigh_po` implant | 2000 | 16 000 |
| n-well | 950 | 7 600 |
| `xhrpoly`, the `res_high_po` implant | 319.8 | 2 558 |
| p+ diffusion | 197 | 1 576 |
| n+ diffusion | 120 | 960 |
| poly (ordinary, silicided) | 48.2 | 386 |
| local interconnect (`li`) | 12.8 | 102 |
| met1, met2 | 0.125 | 1 |
| met3, met4 | 0.047 | 0.38 |
| met5 | 0.029 | 0.23 |
| redistribution layer | 0.005 | 0.04 |

That's a range of nearly six orders of magnitude on one chip, from 4400 Ω/□ down to 0.005 Ω/□.
Met5 at 0.029 Ω/□ and n-well at 950 Ω/□ differ by a factor of 32 759.

> **The ngspice models have their own numbers.** The model files at
> `/foss/pdks/sky130A/libs.tech/ngspice/r+c/res_typical__cap_typical.spice` carry their own
> copies of these values. `rdn=120`, `rdp=197`, `rp1=48.2` and `rm1=0.125` agree exactly with
> Magic's table, but `rl1=12.2` (not 12.8), `rm5=0.0285` (not 0.029) and `rnw=1700` (not 950)
> don't. Magic's table is what the *extractor* uses when it reads your layout, and the ngspice
> file is what the *simulator* uses, so when the two disagree, your simulation results came from
> the ngspice number. Disagreements like this are a normal part of reading a PDK, and they don't
> mean that something is broken.

## Contact resistance

Current has to get into the strip, and it does that through a **contact cut**: a small hole in
the insulator, filled with metal. The same Magic file lists the resistance of each cut:

| contact | Ω each |
|---|---:|
| `ndc`, metal to n+ diffusion | 185 |
| `pdc`, metal to p+ diffusion | 585 |
| `pc`, metal to poly | 152 |
| `mcon`, li to met1 | 9.3 |
| `via`, met1 to met2 | 4.5 |
| `via2`, `via3` | 3.41 |
| `via4`, met4 to met5 | 0.38 |

A single contact to p+ diffusion costs 585 Ω, which is nearly two squares of `res_high_po`
material. That's why a real resistor device has a wide **head** at each end, with room for a row
of contacts in parallel.

## Head and body of one resistor

`sky130_fd_pr__res_high_po` is a `.subckt`, and inside it a node called `rb` sits between the
contact head and the resistive body. If you probe that node, you can split one measured
resistance into its two parts.

Start with a first guess. The sheet resistance is 319.8 Ω/□ (from Magic) or 317.3885 Ω/□ (the
`rsheet` parameter on the ngspice model card). A strip drawn W = 1 µm, L = 1 µm is one square,
so it should measure about 318 Ω, and the L = 10 µm strip should be ten times that, about
3180 Ω.

Here is what `labs/passives-decks/spice/r_head_and_body.spice` prints:

```
--- A. one strip, split into head and body (ohms) ---
r_l1 = 6.954646e+02
head_l1 = 2.998915e+02
body_l1 = 3.955731e+02
r_l10 = 3.550443e+03
head_l10 = 2.998915e+02
body_l10 = 3.250551e+03
```

Both guesses are wrong, and the six lines show why. One square of `res_high_po` measures
695.4646 Ω, more than twice the sheet resistance, because 299.8915 Ω of that is in the head
rather than the body. (The one-square body itself is 395.5731 Ω rather than 317 Ω, because the
model makes the body slightly longer than you drew it; the next section has the numbers.)

The head at L = 10 µm is also `2.998915e+02`, the same to seven digits, because making the strip
longer didn't change the contacts. The head is a fixed cost that you pay once per resistor.

The body is the part that scales with length, so the difference between the two bodies, divided
by the difference in length, gives the resistance of each extra square:

$$\frac{3250.551 - 395.5731}{10 - 1} = \frac{2854.978}{9} = \boxed{317.2198\ \Omega/\square}$$

That's the sheet resistance as the simulator measures it, and it's within 0.06 % of the
`rsheet = 317.3885` on the model card. You'll run this deck yourself in
[Lab 01, Part 6](../labs/lab-01-a-resistor-you-designed-overview.md#part-6-split-a-resistor-into-head-and-body).

## The design equation

Rearranged into the form you'll design with, the resistance of a strip with W = 1 µm is

$$R(L) = 378.2448 + 317.2198\,L \qquad (L \text{ in µm})$$

The 378.2448 Ω intercept is the head plus a small, fixed extension of the body that the model
adds. The card says `leff = l + 0.247`, which means the strip is electrically 0.247 µm longer
than you drew it. [Lab 01](../labs/lab-01-a-resistor-you-designed-overview.md) extracts both
constants from a different deck, one with 22 strips of different lengths and widths, and gets
`317.2198 ohm/square  378.2448 ohm of ends`, the same two numbers. Lab 01, Part 4 also does the
fit at other widths, where the per-micron slope and the end resistance both change.

Here is the equation checked against the simulator:

| L (µm) | $378.2448 + 317.2198L$ | ngspice |
|---:|---:|---:|
| 1 | 695.4646 | 695.4646 |
| 10 | 3550.443 | 3550.443 |
| 50 | 16 239.23 | 16 239.23 |

Before you trust any on-chip resistor value, ask what the ends cost, and make a habit of it. At
L = 1 µm the ends are 54 % of the device, and at L = 100 µm they are 1.2 %, so if your resistor
is short, you're mostly paying for contacts.

## Using sheet resistance

Sheet resistance is what lets a layout engineer look at a drawing and say "that's about 3 kΩ"
without a simulator: they count the squares and multiply by the number from the table. It's also
the reason a wire has a resistance you have to take into account. A 1000 µm run of
minimum-width met1 is 1000 / 0.14 = 7143 squares, and 7143 squares × 0.125 Ω/□ = **893 Ω**,
which is a real resistor in your signal path whether you drew one there or not.

Next: [What a resistor costs in area](../guide/what-a-value-costs-in-area.md), where you find out
how much silicon a 100 kΩ resistor occupies.
