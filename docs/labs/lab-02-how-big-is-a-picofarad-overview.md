# Lab 02 — How big is a picofarad?

Full runnable package: [`labs/lab-02-how-big-is-a-picofarad/`](https://github.com/uoftasic/ad102/tree/main/labs/lab-02-how-big-is-a-picofarad).

**Question this lab answers:** *A picofarad is the smallest capacitance anyone
bothers to write down. How much silicon is it?*

## Prerequisites

- [Lab 01 — A resistor you designed](labs/lab-01-a-resistor-you-designed-overview.md),
  finished, with your own `PASS`
- You are in `labs/lab-02-how-big-is-a-picofarad/`

## Objectives

- Measure capacitance from an AC current, in one division
- Separate a plate capacitor's **area** term from its **edge** term, and say
  when each matters
- Price one picofarad in the three technologies SKY130 offers, and compare
  those prices to a piece of digital logic
- Measure inductance, quality factor and self-resonance of a real on-chip
  spiral, and explain why nobody builds one if they can avoid it

## The one-paragraph version

Lab 01's resistor was expensive because you buy ohms by the square. A
capacitor is worse, because the thing you buy is **area outright** and the
exchange rate was fixed by the process engineers when they chose how thick to
make an oxide layer. You cannot make the oxide thinner; you can only make the
plate bigger. And the inductor is worse again — bad enough that the honest
engineering answer is usually *don't*.

## Theory (short)

Two plates of area $A$ separated by a dielectric of thickness $t$:

$$C = \frac{\varepsilon A}{t}$$

On a chip $\varepsilon$ and $t$ are both fixed, so the whole of capacitor
design collapses to a single constant — **farads per square micrometre** — and
one decision, how much area to spend. That constant is the only lever a
process has, and making it bigger means making $t$ smaller, which means lower
breakdown voltage and more leakage. Density is not free.

Real plates also have edges, where field lines bulge out and add capacitance
that scales with **perimeter** rather than area. For a square plate of side
$s$:

$$C = \alpha s^2 + \beta s$$

The second term is a smaller fraction of the total the bigger you draw the
plate — which is the exact mirror image of Lab 01, where the fixed 378 Ω of
end resistance mattered less the *longer* you drew the strip.

## Procedure

```bash
cd labs/lab-02-how-big-is-a-picofarad
make
```

Four ngspice runs, about **three and a half minutes**, three of them silent
for a minute first.

### Step 1 — the area ladder

`spice/picofarad.spice` hangs five square MIM capacitors, sides 1 µm to 20 µm,
on 1 V AC sources at 1 MHz and reads the current each one draws. $C = |I| /
2\pi f$.

- **Try this:** read the density off the model card before you run anything.

  ```bash
  grep -hE "^\+ c[ap]mimc" /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice | head -2
  ```

  ```
  + camimc=  2.00e-15  ; Units: farad/micrometer^2
  + cpmimc = 0.19e-15 ; Units: farad/micrometer
  ```

  Predict all five, on paper, using **only** the first of those.

- **What you should see:**

  ```
  --- A. MIM area ladder, square plates (farads) ---
  c_s1 = 2.642250e-15
  c_s2 = 9.302250e-15
  c_s5 = 5.328225e-14
  c_s10 = 2.065822e-13
  c_s20 = 8.131822e-13
  ```

  The 20 µm plate: predicted 800.0 fF, measured **813.18** — 1.6 % high. The
  1 µm plate: predicted 2.00 fF, measured **2.64** — **32 % high**. Same
  error, same sign, wildly different size, exactly like Lab 01 in reverse.

- **Why an engineer cares:** the two capacitors an analog designer most cares
  about matching are usually a big one and a small one — the sampling
  capacitor and the reference, the two arms of a divider. If you size them
  both from the area term alone, the small one comes out proportionally
  bigger, the ratio you actually built is not the ratio you designed, and no
  measurement of either capacitor on its own will show you that.

### Step 2 — two terms, from two plates

$C = \alpha s^2 + \beta s$, two unknowns, five measurements. Take the two
extremes ($s = 1$ and $s = 20$, in femtofarads) and solve. `make` does it and
prints it:

```
  two plates, two terms:  C[fF] = area*s^2 + edge*s
    area term   2.000887 fF per um^2       reference 2.000887
    edge term   0.641363 fF per um of side  reference 0.641363

    against the three plates it was not fitted to
      side   2.0 um   fit     9.2863 fF   measured     9.3022 fF   (-0.1717 %)
      side   5.0 um   fit    53.2290 fF   measured    53.2822 fF   (-0.0999 %)
      side  10.0 um   fit   206.5024 fF   measured   206.5822 fF   (-0.0386 %)
```

- **Try this:** look at the sign of those three residuals before reading on.
- **What you should see:** all three are **negative**, and they shrink as the
  plate grows. A fit that were merely noisy would scatter either way. A
  systematic miss that fades with size means something small and *constant* is
  missing — a term that does not scale with the plate at all. Add one:

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

  Three coefficients from three plates, and it reproduces all five to one part
  in a million. And the area term came out as **2.000000** — the model card's
  `camimc = 2.00e-15` to seven figures.

- **Why an engineer cares:** you now have a model of the device that is better
  than the headline number, that you built yourself, and that you can invert
  to answer "what side length gives me 250 fF?" — which is the only question
  you will ever actually ask it.

> **Where the edge term comes from, and a free measurement of the etch.** The
> card says the perimeter term is `cpmimc = 0.19e-15` farads per micrometre of
> edge, and a square of side $s$ has $4s$ of edge, so you would expect
> $\beta = 0.76$. You measured **0.659991**. The gap is that the plate is not
> the size you drew it: the model computes with `wc = w + m3_dw`, where
> `m3_dw` is the **metal-3 width bias** — how much narrower the etched metal
> comes out than the drawn mask. Substituting $s \to s - d$ into
> $2s^2 + 0.76s$ gives
> $2s^2 + (0.76 - 4d)s + (2d^2 - 0.76d)$.
> Setting $0.76 - 4d = 0.659991$ gives $d = 0.025002$ µm, and that same $d$
> predicts the constant term as **−0.017751** fF against the **−0.017742** you
> measured. `make` prints both:
>
> ```
>     the edge term implies a metal etch bias of 25.00 nm per side,
>     which predicts a constant term of -0.017751 fF against the -0.017742 you measured.
> ```
>
> **You just measured a 25 nm etch bias with a capacitance meter**, from five
> numbers, without being told it existed. This is the same story as `weff` in
> Lab 01: the mask is not the silicon, and the model knows the difference even
> when the datasheet headline does not mention it.

### Step 3 — one picofarad, done wrong on purpose

- **Try this:** naive first. $A = 1000\,\text{fF} / 2.00 = 500\ \mu\mathrm{m}^2$,
  so a square of side $\sqrt{500} = 22.3607$ µm. The deck contains it, and the
  corrected side beside it.
- **What you should see:**

  ```
  --- B. one picofarad, naive vs fixed (farads) ---
  c_naive = 1.014742e-12
  c_fixed = 1.000001e-12
  ```

  **1.0147 pF**, 1.47 % high. Solving $2.000000\,s^2 + 0.659991\,s - 0.017742
  = 1000$ gives $s = 22.1965$ µm, which measures **1.000001 pF** — one part in a
  million.

- **Why an engineer cares:** 1.47 % on a single capacitor is usually
  survivable. 1.47 % on the *ratio* of two capacitors is a switched-capacitor
  filter with the wrong corner frequency, or an ADC that is a quarter of a bit
  non-linear. Capacitor ratios are the most precise thing available on a chip
  — better than 0.1 % is routine — and that precision is exactly what the
  fringe term destroys if you ignore it.

### Step 4 — three ways to make a capacitor

Part C builds the same job four different ways, and part D removes the bias
from one of them.

- **Try this:** before reading the output, guess which is densest.
- **What you should see:** `make` prints the table:

  ```
    what one picofarad costs
      recipe                               fF/um^2   um^2 for 1 pF   adders
      MIM  cap_mim_m3_1                     2.0297          492.68     4.47
      MOS  nfet_01v8 gate at 1.8 V          7.8732          127.01     1.15
      MOS  pfet_01v8 gate at 1.8 V          8.4296          118.63     1.08
      VPP  m1-m4 wafflecap                  0.9116         1096.96     9.96
  ```

  The last column is that area divided by **110.11 µm²**, the area a 4-bit
  ripple-carry adder synthesises to in
  [DD103](https://uoftasic.com/dd103/) — twelve SKY130 standard cells that add
  two nibbles and produce a carry.

  **One picofarad, drawn the way you would actually draw it, costs four and a
  half ripple-carry adders.**

  Then part D, the same MOS capacitor with the gate at 0 V instead of 1.8 V:

  ```
  --- D. the same MOS cap with the gate at 0 V (farads) ---
  c_nmos_off = 2.207181e-13
  ```

  **220.72 fF instead of 787.69 fF.** Not one shape in the layout changed.

- **Why an engineer cares:** the densest capacitor is the gate oxide, because
  it is the thinnest insulator in the process — and it is a transistor, so it
  is only a capacitor while there is a channel under the gate to be the other
  plate. Take the bias away and 72 % of your capacitance leaves with it. A
  capacitance that depends on the voltage across it is distortion. MOS
  capacitors go on the supply rails by the million, where the voltage never
  moves; they do not go in signal paths. **Density, linearity and mask cost
  are three different axes and no device wins all three.**

### Step 5 — your turn

`spice/my_cap.spice` has three plates to size:

| | device | target |
|---|---|---|
| C1 | `cap_mim_m3_1`, square | **250 fF** |
| C2 | `cap_mim_m3_1`, square | **20 fF** |
| C3 | `nfet_01v8` gate at 1.8 V, square | **250 fF** |

It ships with all three sized from the area term alone, so **your first `make`
fails** — on two of the three. Work out which one passes and why before you
fix anything; that is the whole point of the third row.

### Step 6 — and the inductor?

`make henry` is the fast one: the inductor models live in three small files
outside the corner library, so ngspice starts immediately. That fact is worth
a moment on its own.

- **Try this:** find out how many inductors SKY130 offers.

  ```bash
  ls /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/ | grep "__ind_"
  ```

  ```
  sky130_fd_pr__ind_03_90.model.spice
  sky130_fd_pr__ind_05_125.model.spice
  sky130_fd_pr__ind_05_220.model.spice
  ```

  Three. Not three families with width and turn-count parameters — three
  fixed devices, with nothing to size. Compare that to the resistor, where
  every value you wanted was a number you typed.

- **What you should see:**

  ```
      inductor        L @100 MHz    Q max   at GHz   self-res GHz  inner um^2
      ind_05_220        9.9220 nH   12.718   1.3717         3.5236       48400
      ind_05_125        5.7857 nH   13.083   2.2539         6.5212       15625
      ind_03_90         1.5208 nH   21.126   6.3668        16.5015        8100
  ```

  The last column comes from the PDK's own LVS deck, which names these devices
  in a comment:

  ```bash
  grep "# # RF Inductor" /foss/pdks/sky130A/libs.tech/klayout/lvs/sky130.lvs
  ```

  ```
  # # RF Inductor with 3 turns and internal diameter of 90um
  # # RF Inductor with 5 turns and internal diameter of 125um
  # # RF Inductor with 5 turns and internal diameter of 220um
  ```

  220 µm across the **hole in the middle** is 48,400 µm², and the five turns
  of metal go *outside* that. So 48,400 is a floor, not a footprint.

  `make henry` also leaves `results/ind_sweep.txt` behind — the whole
  100 MHz-to-100 GHz sweep, two columns per device. If you would rather look at
  it than read it, the package ships an optional plotter that needs nothing
  installed:

  ```bash
  python3 src/plot_inductors.py      # -> results/inductors.svg
  ```

  It marks each self-resonance where the apparent inductance crosses zero.
  Above that line the device is a capacitor, and it is still called an
  inductor.

- **Why an engineer cares:** put the three passives side by side, all measured
  by you, all in the same process:

  | you drew | area | in ripple adders |
  |---|---|---|
  | 1 kΩ resistor (Lab 01) | 1.96 µm² | 0.018 |
  | 1 pF MIM capacitor | 492.68 µm² | 4.5 |
  | 9.92 nH inductor | ≥ 48,400 µm² | **≥ 440** |

  On a schematic those three symbols are the same size. **In silicon they span
  a factor of twenty-five thousand.**

  And 9.92 nH is not a useful inductance for anything but radio. A switching
  regulator wants microhenries. Even under the wildly optimistic assumption
  that inductance scales *linearly* with area — it does not; a spiral does
  considerably worse — 10 µH would need 4.9 × 10⁷ µm², which is 49 mm². That
  is larger than most entire chips. **This is why every switching regulator
  you have ever seen has an inductor soldered next to the chip rather than
  inside it, and it is the honest answer to "how do you fabricate an inductor
  at the micro scale?": mostly, you don't.**

### Step 7 — build one resonator anyway

`spice/tank.spice` puts `ind_03_90` in parallel with a MIM capacitor and looks
for the impedance peak. The sizing came from numbers you already have:

$$L(2.4\,\text{GHz}) = 1.554019\;\text{nH} \;\Rightarrow\;
C = \frac{1}{(2\pi f)^2 L} = 2829.85\;\text{fF} \;\Rightarrow\;
s = 37.4508\;\mu\mathrm{m}$$

using the same three-term fit from Step 2.

- **Try this:** do that arithmetic yourself before you run it. Note that
  1.554019 nH is **not** the 1.5208 nH the inductor shows at 100 MHz — you are
  operating at a seventh of its self-resonant frequency and it has already
  gained 2.2 %.
- **What you should see:**

  ```
  fpeak               =  2.40000e+09 with=  2.50130e+02
  ```

  **Resonance at 2.4000 GHz**, exactly where you aimed, with a peak impedance
  of 250.13 Ω.

- **Why an engineer cares:** two closures at once. The resonance landing on
  the digit says your capacitor model, your inductor reading and your
  arithmetic all agree. And $250.13 / (2\pi \times 2.4\text{GHz} \times
  1.554\text{nH}) = 10.7$, which is the inductor's own $Q$ of **10.86** — the
  capacitor contributed essentially no loss, so the entire quality of the
  resonator is the inductor's. That is the general case on silicon, and it is
  why on-chip $Q$ is a number people quote about inductors and nobody quotes
  about capacitors.

  The whole resonator: 8,100 µm² of inductor (floor) plus 1,403 µm² of
  capacitor. **86 ripple adders for one tuned circuit.**

## Expected results

**Golden** — AC operating points contain no randomness.

```
MIM square plate, side s :  C[fF] = 2.000000 s^2 + 0.659991 s - 0.017742
                            (etch bias d = 25.00 nm per side falls out of it)
1 pF                     :  MIM 22.1965 um square = 492.68 um^2
                            MOS 11.2699 um square = 127.01 um^2
                            VPP                     1096.94 um^2
MOS cap, gate at 0 V     :  220.72 fF vs 787.69 fF biased -- x3.57
ind_03_90 at 2.4 GHz     :  L = 1.554019 nH   Q = 10.864   Rs = 2.157 ohm
2.4 GHz tank             :  peak |Z| = 250.13 ohm at 2.4000 GHz
```

## Links

- [Lab package](https://github.com/uoftasic/ad102/tree/main/labs/lab-02-how-big-is-a-picofarad)
- [`solutions/README.md`](https://github.com/uoftasic/ad102/blob/main/labs/lab-02-how-big-is-a-picofarad/solutions/README.md)
  — including the one-line check that proves SKY130 ships no drawn inductor at all
- Next lab: [Lab 03 — A time constant in silicon](labs/lab-03-a-time-constant-in-silicon-overview.md),
  which puts the resistor and the capacitor you designed into the same circuit
  and asks what a microsecond costs
