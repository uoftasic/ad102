# Ohms per square

This page explains the unit "Ω/□", and why chip designers use it instead of resistivity.

Start from the physics you already have. A block of material with resistivity $\rho$, length
$L$ and cross-section $A$ has

$$R = \rho \frac{L}{A}$$

On a chip the block is a thin film. Its thickness $t$ was fixed by the foundry; you cannot
change it, and it is the same on every device on the wafer. So write the cross-section as width
× thickness, $A = W t$:

$$R = \rho \frac{L}{W t} = \left(\frac{\rho}{t}\right)\frac{L}{W} = R_{\square}\,\frac{L}{W}$$

The two things you cannot control, $\rho$ and $t$, combine into one number:

$$R_{\square} = \frac{\rho}{t} \qquad \text{units: } \frac{\Omega\,\text{m}}{\text{m}} = \Omega$$

$R_\square$ is called **sheet resistance** and is quoted in "ohms per square", written **Ω/□**.
Its dimensions are ohms; the "per square" is a reminder, not a division.

## Why it is called "per square"

Set $L = W$ in $R = R_\square L/W$ and the width cancels:

$$R = R_{\square}$$

A square of the material has the same resistance no matter how big the square is. A 1 µm × 1 µm
square of poly and a 500 µm × 500 µm square of the same poly have identical resistance. Making
it wider adds parallel paths; making it longer in proportion adds series length; the two cancel
exactly.

So $L/W$ is the **number of squares you drew end to end**. A strip 40 µm long and 2 µm wide is
twenty squares in series, and that stays true whether you fold it, bend it, or run it across the
whole die.

This is why the unit exists: it turns an electrical question into a counting question, and you
can count squares on a drawing.

The animation on [Resistors on a chip](guide/a-resistor-you-cannot-buy.md#animation-resistor-geometry)
shows this. It draws the squares onto a strip and numbers them, then stretches the strip and
widens it while the count and the resistance move together. Then it grows length and width at
the same time, so the count stays at one square and 317 Ω (the sheet resistance; the contacts
add to that, as the head-and-body section below shows) while the shape grows ten-fold. If
counting squares still seems odd, watch that part.

## Sheet resistance of the SKY130 layers

These numbers ship with the PDK. They come from
`/foss/pdks/sky130A/libs.tech/magic/sky130A.tech`, the technology file for Magic (the layout tool
you'll use in AD104), which starts the block with the comment
*"# Resistances are in milliohms per square"*. Abridged:

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

Divided by 1000 and sorted:

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

That is nearly six orders of magnitude on one chip, from 4400 Ω/□ down to 0.005. Met5 at
0.029 Ω/□ and n-well at 950 Ω/□ differ by a factor of 32 759.

> **Two files, two sets of numbers.** The ngspice models at
> `/foss/pdks/sky130A/libs.tech/ngspice/r+c/res_typical__cap_typical.spice` carry their own
> copies. `rdn=120`,
> `rdp=197`, `rp1=48.2` and `rm1=0.125` agree exactly; `rl1=12.2` (not 12.8), `rm5=0.0285`
> (not 0.029) and `rnw=1700` (not 950) do not. Magic's table is what the *extractor* uses when
> it reads your layout; the ngspice file is what the *simulator* uses. When they disagree, your
> simulation results came from the ngspice number. Finding disagreements like this is a normal
> part of reading a PDK, not a sign that something is broken.

## Contact resistance

Current has to get into the strip, and it does that through a **contact cut**: a small hole in
the insulator, filled with metal. The same file lists resistance per cut:

| contact | Ω each |
|---|---:|
| `ndc`, metal to n+ diffusion | 185 |
| `pdc`, metal to p+ diffusion | 585 |
| `pc`, metal to poly | 152 |
| `mcon`, li to met1 | 9.3 |
| `via`, met1 to met2 | 4.5 |
| `via2`, `via3` | 3.41 |
| `via4`, met4 to met5 | 0.38 |

One contact to p+ diffusion costs 585 Ω, nearly two squares of `res_high_po` material. That is
why a real resistor device has a wide **head** at each end, holding a row of contacts in
parallel.

## Head and body of one resistor

`sky130_fd_pr__res_high_po` is a `.subckt`, and inside it a node called `rb` sits between the
contact head and the resistive body. Probing that node splits one measured resistance into its
two parts.

A first guess: the sheet resistance is 319.8 Ω/□ (Magic) or 317.3885 Ω/□ (the `rsheet`
parameter on the ngspice model card). A strip drawn W = 1 µm, L = 1 µm is one square, so it
should be about 318 Ω, and the L = 10 µm strip should be ten times that, about 3180 Ω.

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

Both guesses are wrong, and these six lines say why. One square of `res_high_po` measures 695.4646 Ω, more than twice the sheet resistance, because
299.8915 Ω of it is the head, not the body. (The one-square body itself is 395.5731 Ω rather
than 317, because the model makes the body slightly longer than drawn; the next section has
the numbers.)

The head at L = 10 µm is also `2.998915e+02`, the same to seven digits. Making the strip longer
did not change the contacts, so the head is a fixed cost you pay once per resistor.

The bodies are the part that scales with length:

$$\frac{3250.551 - 395.5731}{10 - 1} = \frac{2854.978}{9} = \boxed{317.2198\ \Omega/\square}$$

That is the sheet resistance, measured, and it is within 0.06 % of the `rsheet = 317.3885` on
the model card. You'll run this deck in
[Lab 01, Part 6](labs/lab-01-a-resistor-you-designed-overview.md#part-6-split-a-resistor-into-head-and-body).

## The design equation

Rearranged into the form you will use, for W = 1 µm:

$$R(L) = 378.2448 + 317.2198\,L \qquad (L \text{ in µm})$$

The 378.2448 Ω intercept is the head plus a small fixed body extension the model adds
(`leff = l + 0.247` on the card: the strip is electrically 0.247 µm longer than you drew it).
[Lab 01](labs/lab-01-a-resistor-you-designed-overview.md) extracts both constants from a deck of
22 strips of different lengths and widths, and gets `317.2198 ohm/square  378.2448 ohm of ends`,
the same two numbers from a different deck. Lab 01, Part 4 also does the fit at other widths,
where the per-micron slope and the end resistance both change.

Checked against the simulator:

| L (µm) | $378.2448 + 317.2198L$ | ngspice |
|---:|---:|---:|
| 1 | 695.4646 | 695.4646 |
| 10 | 3550.443 | 3550.443 |
| 50 | 16 239.23 | 16 239.23 |

The habit to take away: before you trust any on-chip resistor value, ask what the ends cost. At
L = 1 µm the ends are 54 % of the device; at L = 100 µm they are 1.2 %. If your resistor is
short, you are mostly paying for contacts.

## Using sheet resistance

Sheet resistance is why a layout engineer can look at a drawing and say "that's about 3 kΩ"
without a simulator: count the squares and multiply by the number from the table. It is also why
a wire has a resistance you must respect. 1000 µm of minimum-width met1 is
1000 / 0.14 = 7143 squares × 0.125 Ω/□ = **893 Ω**, a real resistor in your signal path whether
you drew it or not.

Next: [What a resistor costs in area](guide/what-a-value-costs-in-area.md), where you find out
how much silicon a 100 kΩ resistor occupies.
