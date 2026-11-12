# Lab 02 — How big is a picofarad?

You'll measure capacitance from an AC current, separate a plate capacitor's area term from its
edge term, and price one picofarad in each of the capacitor types SKY130 offers. Then you'll
measure the inductance, Q and self-resonance of the PDK's on-chip spirals, and build a 2.4 GHz
resonator from one.

Package: [`labs/lab-02-how-big-is-a-picofarad/`](https://github.com/uoftasic/ad102/tree/main/labs/lab-02-how-big-is-a-picofarad)

## Before you start

- Finish [Lab 01](labs/lab-01-a-resistor-you-designed-overview.md): `make mine check` in
  `labs/lab-01-a-resistor-you-designed` prints `PASS`.
- Read [Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md),
  [What a picofarad costs](guide/what-a-picofarad-costs.md),
  [Parasitic capacitance](guide/the-capacitor-you-did-not-draw.md) and
  [Inductors on a chip](guide/the-inductor-problem.md).
- Open a terminal in the workbench and go to the lab folder:

  ```bash
  cd /foss/designs/modules/ad102/labs/lab-02-how-big-is-a-picofarad
  ```

  This lab needs no environment setup; every deck names its model files by absolute path.

**Time:** about 2.5 hours. A full `make` runs four ngspice decks (`pf`, `mine`, `henry` and
`tank`) and then a checker script, `src/check_cap.py`, which fits and prints the results. Three
of the decks are silent while the SKY130 model cards load, anywhere from about 10 seconds to a
minute each depending on your machine. `henry` loads three small inductor files instead and
finishes almost immediately.

The only theory you need beyond the guide pages: two plates of area $A$ separated by a dielectric
of thickness $t$ give $C = \varepsilon A / t$. On a chip $\varepsilon$ and $t$ are both fixed, so
capacitor design comes down to one constant, farads per square micrometre, and one decision, how
much area to spend. Real plates also have edges, where the field bulges out and adds capacitance
that scales with perimeter. For a square plate of side $s$:

$$C = \alpha s^2 + \beta s$$

The edge term matters less the bigger the plate. That is the same pattern as Lab 01's end
resistance: a fixed overhead that matters less as the device grows.

Every capacitance in this lab is read the same way: the deck hangs the device on a 1 V AC source
at 1 MHz and reads the current the source supplies. For a capacitor $I = 2\pi f C V$, so
$C = |I| / (2\pi f)$, one division with no fitting.

## Part 1: The area ladder

`spice/picofarad.spice` builds five square MIM capacitors with sides from 1 µm to 20 µm.

1. Read the density off the MIM model's parameter file:

   ```bash
   grep -hE "^\+ c[ap]mimc" /foss/pdks/sky130A/libs.tech/ngspice/r+c/res_typical__cap_typical__lin.spice
   ```

   ```
   + camimc=  2.00e-15  ; Units: farad/micrometer^2
   + cpmimc = 0.19e-15 ; Units: farad/micrometer
   ```

2. On paper, predict all five capacitances using only the first number, `camimc`.

3. Run the lab:

   ```bash
   make
   ```

   It ends in `FAIL`; you fix that in Part 6. Leave the output in your terminal, because the
   other parts read from it.

4. Find block A and compare it with your predictions.

**You should see:**

```
--- A. MIM area ladder, square plates (farads) ---
c_s1 = 2.642250e-15
c_s2 = 9.302250e-15
c_s5 = 5.328225e-14
c_s10 = 2.065822e-13
c_s20 = 8.131822e-13
```

The 20 µm plate: predicted 800.0 fF, measured 813.18 fF, 1.6 % high. The 1 µm plate: predicted
2.00 fF, measured 2.64 fF, 32 % high. Both are high, but the relative error on the small plate is
twenty times larger.

This matters because the two capacitors an analog designer most wants to match are usually a big
one and a small one, such as a sampling capacitor and a reference, or the two arms of a divider.
If you size both from the area term alone, the small one comes out proportionally bigger, the
ratio you built is not the ratio you designed, and no measurement of either capacitor on its own
will show it.

## Part 2: Fit the area and edge terms

$C = \alpha s^2 + \beta s$ has two unknowns, and you have five measurements.

1. Take the two extremes, $s = 1$ and $s = 20$, in femtofarads, and solve for $\alpha$ and
   $\beta$.

2. Compare with what the checker printed:

   ```
     two plates, two terms:  C[fF] = area*s^2 + edge*s
       area term   2.000887 fF per um^2       reference 2.000887
       edge term   0.641363 fF per um of side  reference 0.641363

       against the three plates it was not fitted to
         side   2.0 um   fit     9.2863 fF   measured     9.3022 fF   (-0.1717 %)
         side   5.0 um   fit    53.2290 fF   measured    53.2822 fF   (-0.0999 %)
         side  10.0 um   fit   206.5024 fF   measured   206.5822 fF   (-0.0386 %)
   ```

3. Look at the signs of those three residuals and decide what they tell you before you go on.

   (All three are negative, and they shrink as the plate grows. A fit that was only noisy would
   miss in both directions. A systematic miss that fades with size means something small and
   constant is missing: a term that does not scale with the plate at all.)

4. Find the checker's three-term fit:

   ```
     three plates, three terms:  C[fF] = area*s^2 + edge*s + const
       area    2.000000    edge   0.659991    const  -0.017742
       against all five plates
         side   1.0 um   fit     2.6422 fF   measured     2.6422 fF   (+0.0000 %)
         side   2.0 um   fit     9.3022 fF   measured     9.3022 fF   (-0.0001 %)
         side   5.0 um   fit    53.2822 fF   measured    53.2822 fF   (-0.0001 %)
         side  10.0 um   fit   206.5822 fF   measured   206.5822 fF   (+0.0000 %)
         side  20.0 um   fit   813.1822 fF   measured   813.1822 fF   (+0.0000 %)
   ```

**You should see:** three coefficients from three plates reproduce all five to one part in a
million, and the area term comes out as 2.000000, the model card's `camimc = 2.00e-15` to seven
figures.

You now have a model of the device that is better than the headline number, that you built
yourself, and that you can invert to answer "what side length gives me 250 fF?", which is the
question you will actually ask it.

> **Where the edge term comes from.** The card says the perimeter term is `cpmimc = 0.19e-15`
> farads per micrometre of edge, and a square of side $s$ has $4s$ of edge, so you would expect
> $\beta = 0.76$. You measured 0.659991. The difference is that the plate is not the size you
> drew: the model computes with `wc = w + m3_dw`, where `m3_dw` is the **metal-3 width bias**,
> how much narrower the etched metal comes out than the mask. Substituting $s \to s - d$ into
> $2s^2 + 0.76s$ gives $2s^2 + (0.76 - 4d)s + (2d^2 - 0.76d)$. Setting $0.76 - 4d = 0.659991$
> gives $d = 0.025002$ µm, and that same $d$ predicts the constant term as −0.017751 fF, against
> the −0.017742 you measured. The checker prints both:
>
> ```
>     the edge term implies a metal etch bias of 25.00 nm per side,
>     which predicts a constant term of -0.017751 fF against the -0.017742 you measured.
> ```
>
> You measured a 25 nm etch bias with a capacitance measurement, from five numbers, without
> being told it existed. It is the same story as `weff`, the effective width, in Lab 01, Part 4:
> the mask is not the silicon, and the model knows the difference even when the datasheet
> headline doesn't mention it.

## Part 3: Size one picofarad

1. Work out the naive size: $A = 1000\,\text{fF} / 2.00 = 500\ \mu\mathrm{m}^2$, a square of side
   $\sqrt{500} = 22.3607$ µm. The deck contains it as `c_naive`.

2. Solve $2.000000\,s^2 + 0.659991\,s - 0.017742 = 1000$ for the corrected side. The deck contains
   it as `c_fixed`.

3. Find block B.

**You should see:**

```
--- B. one picofarad, naive vs fixed (farads) ---
c_naive = 1.014742e-12
c_fixed = 1.000001e-12
```

The naive plate gives 1.0147 pF, 1.47 % high. The corrected side, $s = 22.1965$ µm, measures
1.000001 pF, one part in a million.

1.47 % on a single capacitor is usually survivable. 1.47 % on the *ratio* of two capacitors is a
switched-capacitor filter with the wrong corner frequency, or an ADC that is a quarter of a bit
non-linear. Capacitor ratios are the most precise thing available on a chip (better than 0.1 %
is routine), and ignoring the fringe term throws that precision away.

## Part 4: Three ways to build a capacitor

Block C measures the other two kinds of capacitor from
[Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md): MOS (an nFET gate and a pFET gate,
biased at 1.8 V) and VPP (interleaved metal fingers). Block D takes the bias away from one of
the MOS capacitors.

1. Before reading the output, guess which construction is densest.

2. Find block C:

   ```
   --- C. three technologies (farads) ---
   c_nmos10 = 7.876883e-13
   c_nmos11 = 9.999739e-13
   c_pmos10 = 8.429616e-13
   c_vpp = 1.164030e-13
   ```

   `c_nmos10` is a 10 µm × 10 µm nFET gate, and `c_nmos11` is the 11.2699 µm square that makes
   one picofarad.

3. Find the checker's price list, which turns each density into the area one picofarad needs:

   ```
     what one picofarad costs
       recipe                               fF/um^2   um^2 for 1 pF   adders
       MIM  cap_mim_m3_1                     2.0297          492.68     4.47
       MOS  nfet_01v8 gate at 1.8 V          7.8732          127.01     1.15
       MOS  pfet_01v8 gate at 1.8 V          8.4296          118.63     1.08
       VPP  m1-m4 wafflecap                  0.9116         1096.96     9.96
   ```

   The last column is the area divided by 110.11 µm², the area a 4-bit ripple-carry adder
   synthesises to in [DD103](https://uoftasic.com/dd103/) (twelve SKY130 standard cells that add
   two nibbles and produce a carry).

4. Find block D, the 10 µm × 10 µm nFET capacitor with the gate at 0 V instead of 1.8 V.

**You should see:** one picofarad of MIM, drawn the way you would actually draw it, costs about
four and a half ripple-carry adders. And block D:

```
--- D. the same MOS cap with the gate at 0 V (farads) ---
c_nmos_off = 2.207181e-13
```

220.72 fF instead of the 787.69 fF of `c_nmos10`, with no change to a single shape in the
layout.

The densest capacitor uses the gate oxide, because it is the thinnest insulator in the process.
But it is a transistor, so it is only a capacitor while there is a channel under the gate to act
as the other plate. Remove the bias and 72 % of the capacitance goes with it. A capacitance that
depends on the voltage across it causes distortion, so MOS capacitors go on the supply rails by
the million, where the voltage never moves, and stay out of signal paths. Density, linearity and
mask cost (MIM needs extra masks; see the table on
[Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md#choosing-between-them)) are separate
properties, and no device wins on all three.

## Part 5: The MOS capacitor's C–V curve

The guide pages quote a second set of decks in `labs/passives-decks`. `spice/c_area.spice`
measures one MIM, VPP and MOS capacitor each at 1 kHz, and `spice/c_moscap_cv.spice` sweeps one
MOS capacitor's gate from 0 V to 1.8 V in 100 mV steps.

1. Go to the `passives-decks` package and run both:

   ```bash
   cd ../passives-decks
   make capacitor
   ```

2. Divide each MIM capacitance in the first block by its drawn area (1, 100 and 900 µm²).

3. Read `c_000mv` through `c_180mv` in the second block. Find the voltage range where the
   capacitance climbs fastest.

4. Go back to the lab folder:

   ```bash
   cd ../lab-02-how-big-is-a-picofarad
   ```

**You should see:** MIM densities of 2.64, 2.07 and 2.02 fF/µm², falling as the plate grows. In
the sweep, 220.7182 fF at 0 V (`c_000mv = 2.207182e-13`), a steep climb between 0.3 V and
0.7 V, and a flattening toward 787.6883 fF at 1.8 V (`c_180mv = 7.876883e-13`). That is the
curve plotted on [Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md#mos-capacitance-and-gate-voltage):
the steep part is the transistor's threshold.

## Part 6: Size your own capacitors

`spice/my_cap.spice` has three plates to size:

| | device | target |
|---|---|---|
| C1 | `cap_mim_m3_1`, square | **250 fF** |
| C2 | `cap_mim_m3_1`, square | **20 fF** |
| C3 | `nfet_01v8` gate at 1.8 V, square | **250 fF** |

The file ships with all three sized from the area term alone, so the check in Part 1 failed on
two of them:

```
  C1  cap_mim_m3_1, square
    target    250.00 fF
    got       257.36 fF   (+2.94 %)   FAIL
  C2  cap_mim_m3_1, square
    target     20.00 fF
    got        22.07 fF   (+10.35 %)   FAIL
  C3  nfet_01v8 gate at 1.8 V, square
    target    250.00 fF
    got       250.79 fF   (+0.31 %)   PASS
```

1. Before you change anything, work out why C3 passed with the naive sizing and the other two
   did not. That is the point of the third row.
2. Solve for the side lengths of C1 and C2 using your three-term fit from Part 2. Leave C3 as
   it is.
3. Edit the sizes in `spice/my_cap.spice`. Write them as plain microns, with no `u` suffix.
4. Re-run your file and the checker:

   ```bash
   make mine check
   ```

**You should see:** all three capacitors marked `PASS`, then

```
PASS -- every number matches the reference run.
```

## Part 7: The three inductors

`make` already ran `make henry`, which sweeps the three SKY130 inductor models from 100 MHz to
100 GHz. It is the fast run, because the inductor models live in three small files outside the
corner library.

1. Find out how many inductors SKY130 offers:

   ```bash
   ls /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/ | grep "__ind_"
   ```

   ```
   sky130_fd_pr__ind_03_90.model.spice
   sky130_fd_pr__ind_05_125.model.spice
   sky130_fd_pr__ind_05_220.model.spice
   ```

   There are three fixed devices, with no width or turn-count parameters and nothing to size.
   With the resistor, every value you wanted was a number you typed.

2. Find the inductor table in the checker's output:

   ```
       inductor        L @100 MHz    Q max   at GHz   self-res GHz  inner um^2
       ind_05_220        9.9220 nH   12.718   1.3717         3.5236       48400
       ind_05_125        5.7857 nH   13.083   2.2539         6.5212       15625
       ind_03_90         1.5208 nH   21.126   6.3668        16.5015        8100
   ```

3. The last column comes from the PDK's own LVS deck, which describes these devices in a
   comment. Check it:

   ```bash
   grep "# # RF Inductor" /foss/pdks/sky130A/libs.tech/klayout/lvs/sky130.lvs
   ```

   ```
   # # RF Inductor with 3 turns and internal diameter of 90um
   # # RF Inductor with 5 turns and internal diameter of 125um
   # # RF Inductor with 5 turns and internal diameter of 220um
   ```

   220 µm across the hole in the middle is 48,400 µm², and the five turns of metal go outside
   that. So 48,400 µm² is a lower bound on the footprint, not the footprint.

4. (Optional) `make henry` also leaves `results/ind_sweep.txt`, the whole 100 MHz to 100 GHz
   sweep. To see it as a plot (nothing to install):

   ```bash
   python3 src/plot_inductors.py      # -> results/inductors.svg
   ```

   It marks each self-resonance, where the apparent inductance crosses zero. Above that line the
   device behaves as a capacitor, even though it is still called an inductor.

5. Now look at the low-frequency end, which the guide page quotes. Run the `passives-decks`
   inductor deck:

   ```bash
   cd ../passives-decks
   make inductor
   cd ../lab-02-how-big-is-a-picofarad
   ```

**You should see:** in the `make inductor` output, `q_1khz = 1.50516e-05` for `ind_05_220`: at
1 kHz the largest inductor is almost entirely resistance, as
[Inductors on a chip](guide/the-inductor-problem.md) explains. The best Q for `ind_03_90` is
about 21.1, near 6.4 GHz, matching the `henry` table.

Put the three passives side by side, all from your own runs in the same process:

| you drew | area | in ripple adders |
|---|---|---|
| 1 kΩ resistor (Lab 01, strip only) | 1.96 µm² | 0.018 |
| 1 pF MIM capacitor | 492.68 µm² | 4.5 |
| 9.92 nH inductor | ≥ 48,400 µm² | **≥ 440** |

On a schematic the three symbols are the same size. In silicon they span a factor of
twenty-five thousand.

And 9.92 nH is not a useful inductance for anything but radio. A switching regulator wants
microhenries. Even if inductance scaled linearly with area (it doesn't; a spiral does
considerably worse), 10 µH would need 4.9 × 10⁷ µm², which is 49 mm², larger than most entire
chips. That is why every switching regulator you have seen has an inductor soldered next to the
chip rather than inside it. It also answers one of the three questions this course set out to
answer, how you fabricate an inductor at the micro scale: mostly, you don't.

## Part 8: A 2.4 GHz resonator

`spice/tank.spice` puts `ind_03_90` in parallel with a MIM capacitor and looks for the impedance
peak. The sizing uses numbers you already have:

$$L(2.4\,\text{GHz}) = 1.554019\;\text{nH} \;\Rightarrow\;
C = \frac{1}{(2\pi f)^2 L} = 2829.85\;\text{fF} \;\Rightarrow\;
s = 37.4508\;\mu\mathrm{m}$$

using the three-term fit from Part 2.

1. Do that arithmetic yourself. Note that 1.554019 nH is not the 1.5208 nH the inductor shows at
   100 MHz: at 2.4 GHz you are at a seventh of its self-resonant frequency, and its apparent
   inductance has already risen 2.2 %.

2. Find the tank result in the output from Part 1:

   ```
   fpeak               =  2.40000e+09 with=  2.50130e+02
   ```

**You should see:** resonance at 2.4000 GHz, exactly where you aimed, with a peak impedance of
250.13 Ω.

Two things check out at once. The resonance landing on the digit says your capacitor model, your
inductor reading and your arithmetic all agree. And
$250.13 / (2\pi \times 2.4\text{GHz} \times 1.554\text{nH}) = 10.7$, close to the inductor's own
Q at 2.4 GHz, 10.86 (`q_090_2g4` in the `henry` output). So the capacitor contributed almost no
loss, and the resonator's quality is nearly all the inductor's. That is the usual case on silicon, and it is why people quote on-chip Q for inductors
and never for capacitors.

The whole resonator is 8,100 µm² of inductor (a lower bound) plus 1,403 µm² of capacitor: 86
ripple adders for one tuned circuit.

## Part 9 (optional): Parasitic capacitance in SiliWiz

[Parasitic capacitance](guide/the-capacitor-you-did-not-draw.md) is easier to believe once you
see that a wire is a bar hanging over a plane. SiliWiz draws the cross-section live.

1. Open **<https://app.siliwiz.com/?preset=blank>**.
2. Draw a **metal2** rectangle. Draw a second one beside it, not touching.
3. Label one `in` and the other `out` (click, then **Set Label** or press `S`).
4. Tick **Show SPICE** at the bottom and find the line starting `C0 out in`. That is the coupling
   between two wires you never meant to connect.
5. Drag the rectangles closer together and watch the number.
6. Now put one on **metal1** and the other on **metal2**, overlapping.

**You should see:** the `C0 out in` value climbs as the two metal2 wires get closer. With one wire
on metal1 and the other on metal2, overlapping, the capacitance is lower than for the two metal2
wires at their closest, because the vertical gap between metal layers is bigger than the
horizontal gap you can draw between two wires on the same layer.

There is a guided walkthrough at <https://tinytapeout.com/siliwiz/parasitics/>, and the capacitor
tutorial at <https://tinytapeout.com/siliwiz/capacitors/> builds the same three kinds of
capacitor as [Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md).

> **Warning:** SiliWiz is not SKY130. Its layer stack, permittivities and numbers are simplified
> for teaching. Use it for the shape of the answer (closer means more, a thicker gap means less,
> edges matter) and use the PDK's `parameters/typical.spice` (see
> [Parasitic capacitance](guide/the-capacitor-you-did-not-draw.md)) for the value.

## Finishing

You are done when `make mine check` prints `PASS -- every number matches the reference run.`

AC operating points have no randomness in them, so on the pinned image (ngspice-47, `sky130A`,
`tt` corner, 27 °C) your numbers match these:

```
MIM square plate, side s :  C[fF] = 2.000000 s^2 + 0.659991 s - 0.017742
                            (etch bias d = 25.00 nm per side falls out of it)
1 pF                     :  MIM 22.1965 um square = 492.68 um^2
                            MOS 11.2699 um square = 127.01 um^2
                            VPP                     1096.96 um^2
MOS cap, gate at 0 V     :  220.72 fF vs 787.69 fF biased -- x3.57
ind_03_90 at 2.4 GHz     :  L = 1.554019 nH   Q = 10.864   Rs = 2.157 ohm
2.4 GHz tank             :  peak |Z| = 250.13 ohm at 2.4000 GHz
```

After yours pass, read
[`solutions/README.md`](https://github.com/uoftasic/ad102/blob/main/labs/lab-02-how-big-is-a-picofarad/solutions/README.md)
for the reference sizes, why C3 passed, and a check of what inductor geometry the PDK's GDS
actually contains.

Next on the [Course path](README.md#course-path): read
[What to build instead of an inductor](guide/what-analog-builds-instead.md), then do
[Lab 03 — A time constant in silicon](labs/lab-03-a-time-constant-in-silicon-overview.md), which
puts your resistor and capacitor into the same circuit.

## Expected warnings and delays

**Silence.** `pf`, `mine` and `tank` each load SKY130's model cards before printing anything.
`henry` does not. It is not hung.

**`W=1`, never `W=1u`.** SKY130 geometry parameters are plain micron numbers. There is no `u`
suffix anywhere in this package, and there should be none in yours.
