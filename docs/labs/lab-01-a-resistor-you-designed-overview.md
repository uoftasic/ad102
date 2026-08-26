# Lab 01 — A resistor you designed

Full runnable package: [`labs/lab-01-a-resistor-you-designed/`](https://github.com/uoftasic/ad102/tree/main/labs/lab-01-a-resistor-you-designed).

**Question this lab answers:** *I have written `R = 10k` on a schematic a
hundred times. On a chip, ten kilohms of what?*

## Prerequisites

- [IC101](https://uoftasic.com/ic101/) complete — you can start the workbench
  container and get a shell in it
- ECE110-level circuit analysis: Ohm's law and a voltage divider. Nothing else.
- This repo cloned; you are in `labs/lab-01-a-resistor-you-designed/`

## Objectives

- Explain a resistor's value as a **count of squares**, not a length
- Extract sheet resistance and end resistance from a simulation you ran
- Size a resistor to a target value and hit it inside 1 %
- Say what a given resistance costs in square micrometres, and compare that
  cost to a piece of digital logic

## The one-paragraph version

Nobody puts a component in a chip. There is nothing to put. A resistor on a
chip is a **strip of doped silicon or poly-silicon** with a wire touching each
end, and the only thing the designer controls is its shape. The material
decides how many ohms you get per unit of shape; you decide how much shape to
buy. That is the whole of on-chip passive design, and it is why an analog
designer's first instinct on seeing `R = 10k` is to ask *how much floor
space?*

## Theory (short)

Current runs down the strip's length $L$ and spreads across its width $W$.
Double the length and you double the resistance; double the width and you
halve it. So resistance depends on $L$ and $W$ only through their **ratio**:

$$R = R_\square \, \frac{L}{W}$$

$R_\square$ is the **sheet resistance**, in ohms per square. Its unit is
strange until you notice that $L/W$ is dimensionless: it counts how many
squares of material you laid end to end. A strip 1 µm × 1 µm and a strip
50 µm × 50 µm have the *same* resistance. One square is one square.

That formula is where everyone starts, and this lab is about the two places it
is not enough.

## Procedure

```bash
cd labs/lab-01-a-resistor-you-designed
make
```

Two ngspice runs, about **two and a half minutes**, most of it silent —
see [What is not a bug](#what-is-not-a-bug) below before you reach for Ctrl-C.

### Step 1 — measure the material

`spice/sheet.spice` builds twenty-two strips of `sky130_fd_pr__res_high_po`,
forces exactly 1 µA through each, and prints the voltage that appears across
it. Dividing by 1 µA gives the resistance. There is no instrument and no
curve fitting here — it is one application of Ohm's law per device.

The first block is a **length ladder**: $W$ pinned at 1 µm, $L$ walking from
1 µm to 100 µm.

- **Try this:** before running anything, open the model card and read the one
  number the foundry advertises.

  ```bash
  grep rsheet /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_high_po.model.spice
  ```

  ```
  + rsheet = 317.3885
  ```

  Now predict, on paper, what the seven strips will measure. At $W = 1$ µm the
  ratio $L/W$ is just $L$, so you are predicting
  $317.3885 \times 1$, $\times 2$, $\times 5$, and so on.

- **What you should see:**

  ```
  --- A. length ladder, W = 1 um (ohms) ---
  r_l1 = 6.954646e+02
  r_l2 = 1.012684e+03
  r_l5 = 1.964344e+03
  r_l10 = 3.550443e+03
  r_l20 = 6.722641e+03
  r_l50 = 1.623923e+04
  r_l100 = 3.210022e+04
  ```

  Your prediction for the last one was 31,739 Ω and it measured 32,100 Ω —
  1 % high, fine. Your prediction for the *first* one was 317 Ω and it
  measured **695**. You are out by a factor of 2.2 on the small resistor and
  by 1 % on the big one, from the same formula. Something is being added that
  does not care how long you drew the strip.

- **Why an engineer cares:** a model that is right at one end of your design
  range and wrong at the other is worse than one that is uniformly wrong,
  because it will pass every check you run on the big case.

### Step 2 — two numbers, not one

Plot those seven points, or just look at them: the differences between
consecutive lengths are steady. $R$ is a straight line in $L$, but the line
does not go through the origin. So write down the honest form:

$$R = R_{\text{end}} + R_\square \, \frac{L}{W}$$

Two unknowns, and you have seven measurements. Take the two extremes:

$$
R_\square = \frac{32100.22 - 695.4646}{100 - 1} = 317.2198 \;\Omega/\square
\qquad
R_{\text{end}} = 695.4646 - 317.2198 = 378.2448 \;\Omega
$$

- **Try this:** put those two numbers back into the five measurements you did
  *not* use.
- **What you should see:** at $L = 10$, $378.2448 + 3172.198 = 3550.4424$
  against a measured **3550.443**. At $L = 20$, $6722.640$ against
  **6722.641**. The line is exact across a hundred-to-one range in length.
  `make` prints the same extraction for you:

  ```
    the two numbers that define the device
      device          ohm/square    end ohms                 reference
      high_po           317.2198    378.2448      317.2198 / 378.2448
      xhigh_po         2118.7619     34.2111      2118.7619 / 34.2111
  ```

- **Why an engineer cares:** 378 Ω is a **fixed overhead per resistor**. It is
  the price of the two contact heads where metal meets poly, plus a little
  length the strip has that you did not draw. On a 100 kΩ resistor it is
  0.4 % and you may ignore it. On a 500 Ω resistor it is most of the device.

> **Where the 378 Ω comes from, if you want it.** Open the model card. The
> body is declared `l = {leff}` with `leff = {l + 0.247}` — the strip is
> electrically 0.247 µm longer than you drew it, worth
> $317.2198 \times 0.247 = 78.35\ \Omega$. The head is a second resistor,
> `rsh = 345.8312` over a width of `weff + 0.1558 = 1.1548`, giving
> $345.8312 / 1.1548 = 299.47\ \Omega$; its temperature coefficients
> (`tc1 = -4.3e-4`, `tc2 = 12e-6`, `tnom = 30`) scale that by
> $1 + (-4.3{\times}10^{-4})(-3) + (12{\times}10^{-6})(9) = 1.001398$ at the
> 27 °C ngspice simulated at, giving 299.89 Ω. And
> $299.89 + 78.35 = 378.24$. The number you measured is
> **378.2448**. The arithmetic closes to five figures using nothing but
> constants printed in a text file you can `cat`.

### Step 3 — the design, done wrong on purpose

Now use it. Design a 10 kΩ resistor at $W = 1$ µm.

- **Try this:** the naive answer first. $L = 10000 / 317.3885 = 31.5074$ µm.
  The deck already contains it.
- **What you should see:**

  ```
  --- B. the 10 kohm design, naive vs fixed (ohms) ---
  r_naive = 1.037302e+04
  r_fixed = 9.999997e+03
  ```

  **10,373 Ω.** You asked for 10 kΩ and drew something 3.7 % too big. Now
  redo it with the number you extracted:

  $$L = \frac{10000 - 378.2448}{317.2198} = 30.3315 \;\mu\mathrm{m}$$

  which is `r_fixed` — **9999.997 Ω**, three parts in ten million.

- **Why an engineer cares:** 3.7 % does not sound like much until you remember
  what resistors are usually *for*. A resistor that sets a bias current sets it
  3.7 % wrong. A pair of them setting a gain of 10 sets it wrong twice. And
  the error is systematic — every chip on every wafer gets the same 3.7 %,
  so no amount of averaging finds it. This is the difference between a
  tolerance and a **mistake**.

### Step 4 — width is a separate decision

The length ladder was all at $W = 1$ µm. Parts C and C2 sweep width at two
lengths, so you can fit a slope for each width the same way you did in Step 2.

- **Try this:** do the fit for all four widths. Two subtractions each.
- **What you should see:**

  | W (µm) | Ω per µm of length | end Ω | Ω per **square** | µm² of body per kΩ |
  |---|---|---|---|---|
  | 0.35 | 971.641 | 958.562 | **340.074** | **0.3602** |
  | 0.69 | 459.946 | 523.544 | 317.362 | 1.5002 |
  | 1 | 317.220 | 378.245 | 317.220 | 3.1524 |
  | 2 | 158.530 | 199.875 | 317.061 | 12.6159 |
  | 5 | 63.393 | 82.841 | 316.966 | 78.8728 |

  Read the fourth column downward: 317.362, 317.220, 317.061, 316.966. Sheet
  resistance really is a property of the material, constant to a tenth of a
  percent — right up until 0.35 µm, where it jumps 7 % to **340.074**. Below
  0.69 µm the model applies
  `weff = w - 0.001 - 0.0672 * (0.69 - w)`, so a strip drawn 0.35 µm wide
  conducts as though it were 0.326 µm wide. Lithography and etch do not hand
  you the width you drew.

  Now read the fifth column: **0.36 µm² per kΩ at the narrowest width against
  78.9 at the widest.** Same material, same sheet resistance, a factor of 219
  in area.

- **Why an engineer cares:** you win twice by going narrow — directly on
  width, and again on the length you no longer need — so area per ohm goes as
  $W^2$. That makes "just draw it narrow" look free, and it is not: Lab 04
  measures what narrow costs you in **matching**, which is the currency analog
  design actually runs on.

### Step 5 — the other recipe

Part D repeats the length ladder on `sky130_fd_pr__res_xhigh_po`. Same layer,
same drawing rules, different implant dose.

- **Try this:** extract $R_\square$ and $R_{\text{end}}$ for it, then compare
  what the model card advertises.

  ```bash
  grep rsheet /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_xhigh_po__base.model.spice
  ```

- **What you should see:** the card says `rsheet = 2000.0`. Your extraction
  says **2118.7619 Ω/□** — 5.9 % higher — with only **34.21 Ω** of ends. Both
  differences matter, and they point opposite ways: 6.7× the ohms per square,
  and a tenth of the fixed overhead.

- **Why an engineer cares:** two things. First, the headline number on a model
  card is a *nominal*, and the thing that will actually be fabricated is what
  the model computes. Design against the simulation. Second, this is the only
  knob in the whole lab that is not geometry — the foundry gives you a small
  menu of doses, and choosing from it is the one place you can change ohms per
  square rather than buying more area.

### Step 6 — your turn

`spice/my_resistor.spice` contains two devices and two `L=` numbers. Size them:

| | device | W | target |
|---|---|---|---|
| R1 | `sky130_fd_pr__res_high_po` | 1 µm | **2.2 kΩ** |
| R2 | `sky130_fd_pr__res_xhigh_po` | 1 µm | **50 kΩ** |

The file ships with the naive lengths, so **your first `make` fails on
purpose.** It prints this, and it is not a broken package:

```
  R1  sky130_fd_pr__res_high_po  W=1
    target     2200.0 ohm
    got        2577.1 ohm   (+17.14 %)   FAIL
```

+17.14 %. On a 2.2 kΩ resistor the 378 Ω of ends is no longer a rounding
error, it is a sixth of the device. Fix both lengths and run `make mine check`
again until you see:

```
PASS -- every number matches the reference run.
```

## What is not a bug

**Roughly a minute of silence per ngspice run.** `.lib sky130.lib.spice tt`
pulls in 12 MB of model cards covering every device in SKY130 — mostly
MOSFETs you are not using. Measured on the pinned image: **61 s** before the
first line of output. `make` runs the simulator twice.

**170 `unrecognized parameter` lines, in 34 blocks.** `grep -c` them in
`results/sheet.log` and you get exactly those two numbers.

```
Warning: Model issue on line 4842 :
  .model xl1:rhead_model r sw_et=0 isnoisy=0 rsh=    3.458312000000000e+02 ...
unrecognized parameter (sw_et) - ignored
unrecognized parameter (isnoisy) - ignored
unrecognized parameter (p2) - ignored
unrecognized parameter (q2) - ignored
```

SkyWater writes one set of cards for several simulators. `sw_et`, `isnoisy`
and `p2`/`q2`/`p3`/`q3` describe self-heating, noise and voltage coefficients
in a dialect ngspice does not speak. It says so and carries on with the
parameters it does understand, which are the ones this lab measures. Thirty-four
blocks for twenty-two resistors, because most of these devices expand into
more than one `.model` card.

A line that begins with **`Error`** is a different animal. That one stops the
run and your log will contain no `r_` lines at all — which is exactly what
`check_res.py` tells you to look for.

**`W=1`, never `W=1u`.** On a SKY130 device the geometry parameters are plain
micron numbers. Writing `W=1u` means one **metre**, which is outside every bin
the model was fitted over. On a MOSFET that stops the run with
`could not find a valid modelname`; on a resistor it quietly returns a number
that is wrong by a factor of a million. There is no `u` suffix anywhere in
this package.

## Expected results

**Golden** — a DC operating point contains no randomness, so on the pinned
image these match to every digit shown.

| | `res_high_po` | `res_xhigh_po` |
|---|---|---|
| Ω per square | 317.2198 | 2118.7619 |
| end resistance | 378.2448 Ω | 34.2111 Ω |
| card advertises | 317.3885 | 2000.0 |
| L for 10 kΩ at W = 1 µm | 30.3315 µm | 4.7036 µm |
| L for 100 kΩ at W = 1 µm | 314.0465 µm | 47.1812 µm |

## What it costs

Line up the last row against a number from the digital track. In
[DD103](https://uoftasic.com/dd103/) a 4-bit ripple-carry adder — twelve
SKY130 standard cells, the thing that adds two nibbles — synthesises to
**110.11 µm²**.

| you drew | area | in adders |
|---|---|---|
| 1 kΩ, `res_high_po`, W = 1 µm | 1.96 µm² | 0.018 |
| 10 kΩ, `res_high_po`, W = 1 µm | 30.33 µm² | 0.28 |
| 100 kΩ, `res_high_po`, W = 1 µm | 314.05 µm² | **2.85** |
| 100 kΩ, `res_xhigh_po`, W = 1 µm | 47.18 µm² | 0.43 |

Those areas are the strip only. A drawn resistor also needs its two contact
heads, the spacing to whatever is beside it, and usually a guard ring — call
it half again — so treat them as a floor, not a quote.

One resistor, one of the cheapest things in the analog toolbox, and at
100 kΩ it outweighs a working arithmetic unit. That ratio is the reason
analog blocks look enormous next to digital ones in a die photograph, and it
is the reason a chip designer's answer to "just add a resistor" is never
immediate.

## Links

- [Lab package](https://github.com/uoftasic/ad102/tree/main/labs/lab-01-a-resistor-you-designed)
- Reference sizing and the arguments worth having:
  [`solutions/README.md`](https://github.com/uoftasic/ad102/blob/main/labs/lab-01-a-resistor-you-designed/solutions/README.md)
  — after your own numbers pass, not before
- Next lab: [Lab 02 — How big is a picofarad?](labs/lab-02-how-big-is-a-picofarad-overview.md),
  which asks the same question about the other two passives and gets a much
  worse answer
