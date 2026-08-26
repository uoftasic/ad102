# Ohms per square

**Question this page answers:** *What kind of unit is "Ω/□", and why does everyone
who designs chips use it instead of resistivity?*

Start from the physics you already have. A block of material of resistivity $\rho$,
length $L$, cross-section $A$:

$$R = \rho \frac{L}{A}$$

On a chip the block is a thin film. Its thickness $t$ was fixed by the foundry
before you were born — you cannot change it, you cannot even see it, and it is the
same on every device on the wafer. So write the cross-section as width × thickness,
$A = W t$:

$$R = \rho \frac{L}{W t} = \left(\frac{\rho}{t}\right)\frac{L}{W} = R_{\square}\,\frac{L}{W}$$

Everything you cannot control got swept into one number:

$$R_{\square} = \frac{\rho}{t} \qquad \text{units: } \frac{\Omega\,\text{m}}{\text{m}} = \Omega$$

$R_\square$ is called **sheet resistance** and is quoted in "ohms per square",
written **Ω/□**. It has the dimensions of ohms — the "per square" is a reminder, not
a division.

## Why "square"

Look at $R = R_\square L/W$ and set $L = W$. The width cancels:

$$R = R_{\square}$$

**A square of the material has the same resistance no matter how big the square
is.** A 1 µm × 1 µm square of poly and a 500 µm × 500 µm square of the same poly
have identical resistance. Make it wider and you add parallel paths; make it longer
in proportion and you add series length; they cancel exactly.

So $L/W$ is not "a length over a length". It is **the number of squares you drew
end to end**. A strip 40 µm long and 2 µm wide is twenty squares in series, and it
does not matter whether you fold it, bend it, or run it across the whole die —
twenty squares is twenty squares.

That is the reason the unit exists. It turns an electrical question into a
*counting* question, and counting is something you can do on a drawing.

> **See it counted.** The animation on
> [A resistor you cannot buy](guide/a-resistor-you-cannot-buy.md#watch-this-first) draws the
> squares onto a strip and numbers them, then stretches the strip and widens it while the
> count and the resistance move together — and then grows length and width *at the same
> time*, so the count sticks at one square and 317 Ω while the shape balloons ten-fold. If
> the paragraph above did not land, that beat is where it does.

## The SKY130 numbers

These are shipped, not estimated. From
`/foss/pdks/sky130A/libs.tech/magic/sky130A.tech`, which prefaces the block with
*"# Resistances are in milliohms per square"*:

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

Divide by 1000 and sort:

| layer | $R_\square$ (Ω/□) | ratio to met1 |
|---|---:|---:|
| p-well | 4400 | 35 200 |
| `uhrpoly` — the `res_xhigh_po` implant | 2000 | 16 000 |
| n-well | 950 | 7 600 |
| `xhrpoly` — the `res_high_po` implant | 319.8 | 2 558 |
| p+ diffusion | 197 | 1 576 |
| n+ diffusion | 120 | 960 |
| poly (ordinary, silicided) | 48.2 | 386 |
| local interconnect (`li`) | 12.8 | 102 |
| met1, met2 | 0.125 | 1 |
| met3, met4 | 0.047 | 0.38 |
| met5 | 0.029 | 0.23 |
| redistribution layer | 0.005 | 0.04 |

Nearly six orders of magnitude on one chip — 4400 Ω/□ down to 0.005. Read the table
twice: the same word "wire" covers met5 at 0.029 Ω/□ and n-well at 950 Ω/□, a factor
of **32 759**.

> **Two files, two slightly different numbers.** The ngspice models at
> `libs.tech/ngspice/r+c/res_typical__cap_typical.spice` carry their own copies:
> `rdn=120`, `rdp=197`, `rp1=48.2`, `rm1=0.125` agree exactly; `rl1=12.2` (not
> 12.8), `rm5=0.0285` (not 0.029) and `rnw=1700` (not 950) do not. Magic's table is
> what the *extractor* uses when it reads your layout; the ngspice file is what the
> *simulator* uses. When they disagree, the simulator's number is the one your
> results came from. Noticing this is a normal part of reading a PDK, not a sign
> that something is broken.

## Contacts are not free

You have to get current *into* the strip, and that happens through a contact cut —
a tiny hole in the insulator, filled with metal. Same file, `Ω` per cut this time:

| contact | Ω each |
|---|---:|
| `ndc` — metal to n+ diffusion | 185 |
| `pdc` — metal to p+ diffusion | 585 |
| `pc` — metal to poly | 152 |
| `mcon` — li to met1 | 9.3 |
| `via` — met1 to met2 | 4.5 |
| `via2`, `via3` | 3.41 |
| `via4` — met4 to met5 | 0.38 |

**One contact to p+ diffusion costs 585 Ω.** That is nearly two squares of the
`res_high_po` material. This is not a rounding error; it is the reason a real
resistor device has a *fat head* at each end holding a row of contacts in parallel.

## Demonstrate it: split one resistor into head and body

`sky130_fd_pr__res_high_po` is a `.subckt`, and inside it there is a node called
`rb` sitting exactly between the contact head and the resistive body. Probe it, and
one measured resistance splits into its two halves.

```bash
cd labs/passives-decks
make resistor
```

**Predict first.** Sheet resistance is 319.8 Ω/□ (Magic) or 317.3885 Ω/□ (the
`rsheet` parameter on the ngspice model card). A strip drawn W = 1 µm, L = 1 µm is
one square. So it should be about 318 Ω, and the L = 10 µm strip should be ten
times that, about 3180 Ω.

**What you should see:**

```
--- A. one strip, split into head and body (ohms) ---
r_l1 = 6.954646e+02
head_l1 = 2.998915e+02
body_l1 = 3.955731e+02
r_l10 = 3.550443e+03
head_l10 = 2.998915e+02
body_l10 = 3.250551e+03
```

Both predictions are wrong, and the reason is in the same six lines.

**695.4646 Ω, not 318.** One square of `res_high_po` is more than twice the sheet
resistance, because **299.8915 Ω of it is not body at all.** It is the head.

**And look at the head at L = 10 µm.** `2.998915e+02`. The same number, to seven
digits. Of course it is — you did not change the contacts, you only made the strip
longer. The head is a fixed toll you pay once, regardless.

Now take the bodies, which are the part that scales:

$$\frac{3250.551 - 395.5731}{10 - 1} = \frac{2854.978}{9} = \boxed{317.2198\ \Omega/\square}$$

That is the sheet resistance, measured, from your own run — and it lands within
**0.06 %** of the `rsheet = 317.3885` printed in the model card. The arithmetic
closes.

## The design equation

Rearranged into the form you will actually use, for W = 1 µm:

$$R(L) = 378.2448 + 317.2198\,L \qquad (L \text{ in µm})$$

The 378.2448 Ω intercept is the head *plus* a small fixed body extension the model
adds (`leff = l + 0.247` on the card — the strip is electrically 0.247 squares
longer than you drew it). [Lab 01](labs/lab-01-a-resistor-you-designed-overview.md)
extracts both constants from a 22-strip ladder and gets
`317.2198 ohm/square  378.2448 ohm of ends` — the same two numbers, from a
different deck.

Check it against the run above:

| L (µm) | $378.2448 + 317.2198L$ | ngspice |
|---:|---:|---:|
| 1 | 695.4646 | 695.4646 |
| 10 | 3550.443 | 3550.443 |
| 50 | 16 239.23 | 16 239.23 |

**The reflex to keep:** *before you trust any on-chip resistor value, ask what the
ends cost.* At L = 1 µm the ends are 54 % of the device. At L = 100 µm they are
1.2 %. If your resistor is short, you are mostly buying contacts.

## Why an engineer cares

Sheet resistance is why a layout engineer can look at a drawing and say "that's
about 3 kΩ" without a simulator. Count the squares, multiply by the number from the
table. It is also why a *wire* has a resistance you must respect: 1000 µm of
minimum-width met1 is 1000 / 0.14 = 7143 squares × 0.125 Ω/□ = **893 Ω**, which is
a real resistor sitting in your signal path whether you drew it or not.

Next: [What a value costs in area](guide/what-a-value-costs-in-area.md), where you
find out how much silicon that 100 kΩ actually occupies.
