# Lab 01 — A resistor you designed

You'll measure the sheet resistance and end resistance of a SKY130 poly resistor from your own
simulation, use those two numbers to size resistors that land within 1 % of their targets, and
work out what a resistance costs in silicon compared with a piece of digital logic.

Package: [`labs/lab-01-a-resistor-you-designed/`](https://github.com/uoftasic/ad102/tree/main/labs/lab-01-a-resistor-you-designed)

## Before you start

- Read [Getting started](guide/getting-started.md),
  [Resistors on a chip](guide/a-resistor-you-cannot-buy.md),
  [Ohms per square](guide/ohms-per-square.md) and
  [What a resistor costs in area](guide/what-a-value-costs-in-area.md).
- You need the workbench from [IC101](https://uoftasic.com/ic101/): the noVNC desktop comes up
  in your browser and the [IC101 smoke test](https://uoftasic.com/ic101/#/guide/smoke-test)
  passes. Part 1 sets up the rest.
- The circuit theory is Ohm's law and a voltage divider. Nothing else.

**Time:** about 2.5 hours. Each ngspice run is silent for anywhere from about 10 seconds to a
minute before it prints anything, depending on your machine (see
[Expected warnings and delays](#expected-warnings-and-delays)).

## Part 1: Set up the workbench

You do this part once. You need the course files from step 5 to go on. If the PDK checks in
steps 2 to 4 go wrong, ask for help, but you can still run the labs: the lab decks name their
model files by absolute path, so `make` works even when the environment is not set up.

1. On your own machine, in your `workspace` clone, start the desktop:

   ```bash
   cd workspace
   ./scripts/start_vnc.sh          # Windows: scripts\start_vnc.bat
   ```

   Open **http://localhost/** and open a terminal on that desktop. Every command in this lab is
   typed in that terminal, not on your laptop. For ports, passwords, resolution, and what to do
   when the page is blank, see
   [IC101 — Launch the noVNC desktop](https://uoftasic.com/ic101/#/guide/launch-novnc).

2. Check which PDK the terminal is on:

   ```bash
   echo "PDK is: $PDK"
   ls $PDK_ROOT/$PDK/libs.tech/xschem/ | grep _pr
   ```

   On the IC101 workbench a new terminal normally loads the course environment by itself, so
   you will probably see SKY130 already (the output in step 4). If you see the image's default,
   IHP, this terminal has not loaded it yet:

   ```
   PDK is: ihp-sg13g2
   sg13g2_pr
   ```

3. Load the course environment. If a terminal ever shows IHP, this is the fix, and running it in
   a terminal that already has it does no harm.

   ```bash
   . /foss/designs/common/.designinit
   ```

   ```
   ASIC-EDU: PDK=sky130A  PDK_ROOT=/foss/pdks  designs=/foss/designs
             run 'mod' to list course modules, or 'mod <name>' to enter one.
   ```

4. Run the two commands from step 2 again. You should see SKY130:

   ```
   PDK is: sky130A
   sky130_fd_pr
   sky130_fd_pr.patch
   ```

   Those directories are the symbol libraries XSchem loads.
   [Getting started](guide/getting-started.md#the-pdk-setting) explains why this matters.

5. Get the course files:

   ```bash
   mod add ad102      # first time only: clones github.com/uoftasic/ad102
   mod ad102          # every time after that
   ```

   ```
   Cloning https://github.com/uoftasic/ad102.git
        into /foss/designs/modules/ad102
   Cloning into '/foss/designs/modules/ad102'...
   OK  module ready: /foss/designs/modules/ad102
       run: mod ad102
   cwd: /foss/designs/modules/ad102
   ```

   If something goes wrong here, it is usually one of these:

   | What you see | What it means |
   |---|---|
   | `bash: mod: command not found` | This terminal has not loaded the course environment. Run step 3 in it. |
   | `mod: no such module: ad102` | You ran `mod ad102` before `mod add ad102`. |
   | `fatal: could not read Username for 'https://github.com'` | git is asking you to log in, which means it could not read the repo anonymously. Check the spelling first. If it is right, ask in [Discord](https://discord.gg/hrJnP5UsGz). Do not type your password. |

6. Check the two tool versions this course depends on:

   ```bash
   ngspice -v | head -3
   xschem -v | head -1
   ```

   ```
   ******
   ** ngspice-47 : Circuit level simulation program
   ** Compiled with KLU Direct Linear Solver
   ```

   ```
   XSCHEM V3.4.8RC
   ```

   If you see different versions, you are on a different image, and commands on these pages may
   fail in ways this course does not describe.

7. (Optional) Check the rest of the image. AD102 doesn't use these; they are the AD104 layout
   tools, listed so you can confirm the image is complete:

   | Tool | Command | Expect |
   |---|---|---|
   | Magic | `magic -dnull -noconsole --version` | `8.3.681` |
   | KLayout | `klayout -v` | `KLayout 0.30.11` |
   | Netgen | `netgen -batch quit \| head -1` | `Netgen 1.5.323 compiled on …` |

   `netgen -batch quit` also prints
   `Warning: netgen command 'format' use fully-qualified name '::netgen::format'` and a second
   line like it. Those are Tcl namespace notices from the tool itself. They are not about your
   design, and there is nothing to fix.

8. Go to this lab's folder and list the packages:

   ```bash
   cd /foss/designs/modules/ad102/labs/lab-01-a-resistor-you-designed
   ls ..
   ```

**You should see:** `echo $PDK` prints `sky130A`, `ngspice -v` says `ngspice-47`, and `ls ..`
lists the four lab packages plus `passives-decks`:

```
lab-01-a-resistor-you-designed     lab-03-a-time-constant-in-silicon  passives-decks
lab-02-how-big-is-a-picofarad      lab-04-two-resistors-that-disagree
```

## Part 2: Measure the material

`spice/sheet.spice` builds twenty-two strips of `sky130_fd_pr__res_high_po`, forces exactly
1 µA through each, and prints the voltage across it. Dividing by 1 µA gives the resistance:
one application of Ohm's law per device, with no curve fitting. The first block is a **length
ladder**, with $W$ fixed at 1 µm and $L$ going from 1 µm to 100 µm.

1. Read the one number the foundry advertises on the model card:

   ```bash
   grep rsheet /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_high_po.model.spice
   ```

   ```
   + rsheet = 317.3885
   + rsh = {rsheet*(1+sky130_fd_pr__res_high_po__var)*(1+res_match)}
   ```

   The first line is the number; the second shows how the model uses it.

2. On paper, predict what the seven strips in the length ladder will measure. At $W = 1$ µm,
   $L/W$ is just $L$, so you are predicting $317.3885 \times 1$, $\times 2$, $\times 5$,
   $\times 10$, $\times 20$, $\times 50$ and $\times 100$.

3. Run the lab:

   ```bash
   make
   ```

   This runs two ngspice decks, `spice/sheet.spice` and `spice/my_resistor.spice`, and then the
   checker script, `src/check_res.py`. It ends in
   `FAIL`, which you fix in Part 7. Leave the output in your terminal, because Parts 2 to 5 read
   from it.

4. Find block A in the output and compare it with your predictions:

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

   Your prediction for the longest strip was 31,739 Ω, and it measured 32,100 Ω: 1 % high.
   Your prediction for the shortest was 317 Ω, and it measured 695 Ω: off by a factor of 2.2,
   from the same formula. Something is being added that does not depend on how long you drew the
   strip.

   A model that is right at one end of your design range and wrong at the other is worse than
   one that is wrong everywhere, because it passes every check you run on the big case.

5. The steps between consecutive lengths are steady, so $R$ is a straight line in $L$, but the
   line does not go through the origin. Write it with an intercept:

   $$R = R_{\text{end}} + R_\square \, \frac{L}{W}$$

   Use the two extremes to solve for both unknowns:

   $$
   R_\square = \frac{32100.22 - 695.4646}{100 - 1} = 317.2198 \;\Omega/\square
   \qquad
   R_{\text{end}} = 695.4646 - 317.2198 = 378.2448 \;\Omega
   $$

6. Check those two numbers against measurements you did not use. At $L = 10$:
   $378.2448 + 3172.198 = 3550.4428$, against a measured 3550.443. At $L = 20$: $6722.6408$,
   against 6722.641.

**You should see:** your line matches every point to the last printed digit, across a 100-to-1
range of lengths. The checker prints the same extraction, with the course's own reference run
in the last column for comparison (the `xhigh_po` row is the other material, which you extract
yourself in Part 5):

```
  the two numbers that define the device
    device          ohm/square    end ohms                 reference
    high_po           317.2198    378.2448      317.2198 / 378.2448
    xhigh_po         2118.7619     34.2111      2118.7619 / 34.2111
```

The 378 Ω is a fixed overhead on every resistor: the contact heads where metal meets poly, plus
a little length the strip has that you did not draw. On a 100 kΩ resistor it is 0.4 % and you
can ignore it. On a 500 Ω resistor it is most of the device.

> **Where the 378 Ω comes from, if you want it.** Open the model card from step 1,
> `sky130_fd_pr__res_high_po.model.spice`. The body is declared
> `l = {leff}` with `leff = {l + 0.247}`, so the strip is electrically 0.247 µm longer than you
> drew it, worth $317.2198 \times 0.247 = 78.35\ \Omega$. The head is a second resistor,
> `rsh = 345.8312` over a width of `weff + 0.1558 = 1.1548` (`weff` is the effective width,
> 0.999 µm for a strip drawn 1 µm wide; Part 4 has more on it), giving
> $345.8312 / 1.1548 = 299.47\ \Omega$. Its temperature coefficients (`tc1 = -4.3e-4`,
> `tc2 = 12e-6`, `tnom = 30`) scale that by
> $1 + (-4.3{\times}10^{-4})(-3) + (12{\times}10^{-6})(9) = 1.001398$ at the 27 °C ngspice
> simulated at ($27 - 30 = -3$, and $(-3)^2 = 9$), giving 299.89 Ω. And
> $299.89 + 78.35 = 378.24$, against the 378.2448 you measured. The arithmetic closes to five
> figures using only constants in a text file you can `cat`.

## Part 3: Size a 10 kΩ resistor

The deck already contains two 10 kΩ designs at $W = 1$ µm.

1. Work out the naive length, using only the sheet resistance on the card:
   $L = 10000 / 317.3885 = 31.5074$ µm. This is `r_naive` in the deck.

2. Work out the corrected length, using both numbers you extracted:

   $$L = \frac{10000 - 378.2448}{317.2198} = 30.3315 \;\mu\mathrm{m}$$

   This is `r_fixed`.

3. Find block B in the output.

**You should see:**

```
--- B. the 10 kohm design, naive vs fixed (ohms) ---
r_naive = 1.037302e+04
r_fixed = 9.999997e+03
```

The naive design is 10,373 Ω, 3.7 % too big. The corrected one is 9999.997 Ω, three parts in ten
million.

3.7 % sounds small until you remember what resistors are for. A resistor that sets a bias
current sets it 3.7 % wrong. A pair of them setting a gain of 10 gets the gain wrong too, because
the fixed 378 Ω is a different fraction of a long resistor and a short one. And the
error is systematic: every chip on every wafer gets the same 3.7 %, so no amount of averaging
finds it. A random spread is a tolerance, which you budget for; an error that is the same on every
chip is a mistake, which you fix.

## Part 4: Change the width

The length ladder was all at $W = 1$ µm. Blocks C and C2 sweep four other widths at two lengths,
$L = 10$ µm and $L = 5$ µm.

1. For each width, fit a slope (Ω per µm of length) and an intercept (end Ω) from the two
   lengths, the same way you did in Part 2. That is two subtractions per width.
2. Multiply each slope by its width to get Ω per square.
3. For the last column, work out the body area for 1 kΩ: $1000 / (\Omega \text{ per µm}) \times W$.

**You should see:**

| W (µm) | Ω per µm of length | end Ω | Ω per square | µm² of body per kΩ |
|---|---|---|---|---|
| 0.35 | 971.641 | 958.562 | **340.074** | **0.3602** |
| 0.69 | 459.946 | 523.544 | 317.362 | 1.5002 |
| 1 | 317.220 | 378.245 | 317.220 | 3.1524 |
| 2 | 158.530 | 199.875 | 317.061 | 12.6159 |
| 5 | 63.393 | 82.841 | 316.966 | 78.8728 |

Read the Ω-per-square column from the bottom up: 316.966, 317.061, 317.220, 317.362. Sheet
resistance is a property of the material, constant to a tenth of a percent, until the top row,
0.35 µm, where it jumps 7 % to 340.074. Below 0.69 µm the model applies
`weff = w - 0.001 - 0.0672 * (0.69 - w)`, so a strip drawn 0.35 µm wide conducts as though it
were 0.326 µm wide. Lithography and etch do not give you the width you drew. The end resistance
changes with width as well, from 82.841 Ω at 5 µm to 958.562 Ω at 0.35 µm, because the contact
head is as wide as the strip (the note in Part 2 shows its resistance is `rsh` divided by a
width).

Now read the last column: 0.36 µm² per kΩ at the narrowest width against 78.9 at the widest.
Same material, same sheet resistance, a factor of 219 in area. You win twice by going narrow,
once on width and again on the length you no longer need, so area per ohm goes as $W^2$. That
makes "just draw it narrow" look free. It isn't: Lab 04 measures what narrow costs you in
matching.

## Part 5: Change the recipe

Block D repeats the length ladder on `sky130_fd_pr__res_xhigh_po`: the same layer and drawing
rules, with a different implant dose.

1. Extract $R_\square$ and $R_{\text{end}}$ from block D, using the two extremes as in Part 2.

2. Compare with what its model card advertises:

   ```bash
   grep rsheet /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_xhigh_po__base.model.spice
   ```

   ```
   .param  rsheet = 2000.0
   + rbody = {(l*rsheet+rbody_var)*(1+res_match)/w}
   ```

3. Price your resistors in digital logic. In [DD103](https://uoftasic.com/dd103/), a 4-bit
   ripple-carry adder (twelve SKY130 standard cells that add two nibbles) synthesises to
   110.11 µm². At $W = 1$ µm a strip's area is its length in µm². Work out the length for each
   row of the table below from your design equation (the checker prints the 10 kΩ and 100 kΩ
   lengths in its `the design that follows from them` block), then divide each area by 110.11.

**You should see:** the card says `rsheet = 2000.0`. Your extraction says 2118.7619 Ω/□, 5.9 %
higher, with only 34.21 Ω of ends. Compared with `res_high_po`, that is 6.7 times the ohms per
square and a tenth of the fixed overhead. Your price list should match this one:

| you drew | area | in adders |
|---|---|---|
| 1 kΩ, `res_high_po`, W = 1 µm | 1.96 µm² | 0.018 |
| 10 kΩ, `res_high_po`, W = 1 µm | 30.33 µm² | 0.28 |
| 100 kΩ, `res_high_po`, W = 1 µm | 314.05 µm² | **2.85** |
| 100 kΩ, `res_xhigh_po`, W = 1 µm | 47.18 µm² | 0.43 |

The headline number on a model card is a nominal; the device that gets fabricated is what the
model computes, so design against the simulation. And the implant is the only knob in this lab
that is not geometry. The foundry gives you a short menu of implant doses, and choosing from it
is the one way to change ohms per square instead of buying more area.

The areas above are the strip only. A drawn resistor also needs its two contact heads, spacing
to whatever is beside it, and usually a guard ring (call it half as much area again), so treat them as a
floor, not a quote. Even so, at 100 kΩ one of the cheapest things in the analog toolbox
outweighs a working arithmetic unit. That is why analog blocks look enormous next to digital
ones in a die photograph, and why a chip designer never answers "just add a resistor" straight
away.

## Part 6: Split a resistor into head and body

[Resistors on a chip](guide/a-resistor-you-cannot-buy.md) and
[Ohms per square](guide/ohms-per-square.md) quote a different deck from the one you ran in
Part 2: `labs/passives-decks/spice/r_head_and_body.spice`. `sky130_fd_pr__res_high_po` is a
subcircuit (`.subckt`), and inside it a node called `rb` sits between the contact head and the
resistive body. This deck measures the voltage at that node too, so one measured resistance
splits into its two parts.

1. Go to the `passives-decks` package and run the resistor deck:

   ```bash
   cd ../passives-decks
   make resistor
   ```

2. Before you look at block A, predict: when the strip goes from $L = 1$ µm to $L = 10$ µm,
   which part changes, the head or the body?

3. Read block A:

   ```
   --- A. one strip, split into head and body (ohms) ---
   r_l1 = 6.954646e+02
   head_l1 = 2.998915e+02
   body_l1 = 3.955731e+02
   r_l10 = 3.550443e+03
   head_l10 = 2.998915e+02
   body_l10 = 3.250551e+03
   ```

   The head is 299.8915 Ω at both lengths, the same to seven digits, because you did not change
   the contacts. Take the bodies, which do scale:

   $$\frac{3250.551 - 395.5731}{10 - 1} = \frac{2854.978}{9} = 317.2198\ \Omega/\square$$

   That is the sheet resistance you extracted in Part 2, from a different deck.

4. Read block C. It is one 314.046454 µm × 1 µm strip (the length that gives 100 kΩ of
   `res_high_po`) simulated as four different resistor models: the two poly implants, and the
   p+ and n+ diffusion resistors:

   ```
   --- C. one 314 um x 1 um strip, four implants (ohms) ---
   r_high = 1.000000e+05
   r_xhigh = 6.653872e+05
   r_pdiff = 6.138915e+04
   r_ndiff = 3.689775e+04
   ```

   The drawing and the silicon area are the same, and the values spread over 18:1.

5. Blocks B and D are the worked examples on
   [What a resistor costs in area](guide/what-a-value-costs-in-area.md): 1 k, 10 k and 100 k
   sized with the design equation, and the same 100 kΩ at four widths. Check that each lands on
   its target.

6. Count the model warnings in the log. They are the harmless ones described under
   [Expected warnings and delays](#expected-warnings-and-delays); this deck has fewer resistors
   than `sheet.spice`, so it has fewer of them.

   ```bash
   grep -c 'unrecognized parameter' results/r_head_and_body.log
   ```

7. Go back to the lab folder:

   ```bash
   cd ../lab-01-a-resistor-you-designed
   ```

**You should see:** `head_l1` and `head_l10` both `2.998915e+02`, a body slope of
317.2198 Ω/□, and `100` from the `grep`.

The 378.2448 Ω end resistance you extracted in Part 2 is this 299.89 Ω head plus the
78.35 Ω body extension from the model's `leff`.

## Part 7: Size your own resistors

`spice/my_resistor.spice` contains two devices and two `L=` numbers. You edit only those two
numbers.

| | device | W | target |
|---|---|---|---|
| R1 | `sky130_fd_pr__res_high_po` | 1 µm | **2.2 kΩ** |
| R2 | `sky130_fd_pr__res_xhigh_po` | 1 µm | **50 kΩ** |

1. Print the verdict from Part 2 again (it has probably scrolled away):

   ```bash
   make check
   ```

   The file ships with the naive lengths, so the check failed:

   ```
     R1  sky130_fd_pr__res_high_po  W=1
       target     2200.0 ohm
       got        2577.1 ohm   (+17.14 %)   FAIL
     R2  sky130_fd_pr__res_xhigh_po W=1
       target    50000.0 ohm
       got       53001.1 ohm   (+6.00 %)   FAIL
   ```

   Below that, the checker explains each failure, and it ends with:

   ```
     ^ On a fresh clone this FAIL is the lab, not a broken
       package. spice/my_resistor.spice ships with the naive
       sizing on purpose. Edit the two L= numbers and run
       `make mine check` again.
   ```

   On a 2.2 kΩ resistor, the 378 Ω of ends is no longer a rounding error; it is a sixth of the
   device.

2. Work out both lengths from the $R_\square$ and $R_{\text{end}}$ you extracted for each device
   in Parts 2 and 5.

3. Edit the two `L=` numbers in `spice/my_resistor.spice`. Write them as plain microns, with no
   `u` suffix.

4. Re-run your file and the checker. `make mine` simulates only `spice/my_resistor.spice`, and
   `make check` prints the verdict again:

   ```bash
   make mine check
   ```

**You should see:** both resistors marked `PASS` (each must land within 1 % of its target), then

```
PASS -- every number matches the reference run.
```

## Part 8 (optional): The `u` suffix trap

`spice/u_trap.spice` holds the same resistor written twice, once as `W=1 L=10` and once as
`W=1u L=10u`. [Getting started](guide/getting-started.md#the-u-suffix-trap) explains what goes
wrong.

1. Run it:

   ```bash
   make utrap
   ```

**You should see:**

```
--- the same device, written two ways (ohms) ---
good = 3.550443e+03
bad = 3.193812e+03

   and the one line that told you, buried in the log:
Warning: r.xb.rbody: resistance too low or not given, set to 1 mOhm
   ngspice exit status: 0
```

The wrong spelling gives 3193.812 Ω instead of 3550.443 Ω, 10 % off, with no error and exit
status 0. There is no `u` suffix anywhere in this package, and there should be none in yours.

## Part 9 (optional): Draw a resistor in SiliWiz

SiliWiz is a browser layout tool from the Tiny Tapeout project. It shows a cross-section of your
drawing while you draw it, which makes "a strip of poly with two contacts" concrete.

1. Open **<https://app.siliwiz.com/?preset=blank>**.
2. Pick the **polyres** layer from the palette on the left and draw a long thin rectangle.
3. Pick **metal1 via** and drop one square at each end of it.
4. Pick **metal1** and put a contact pad over each via.
5. Click each metal1 pad, choose **Set Label** (or press `S`), and name them `in` and `out`.
6. Tick **Show SPICE** at the bottom. Find the line starting `R0 in out`; that is your
   resistance.
7. Watch the **cross-section** view as you drag the rectangle longer and thinner.

**You should see:** a line starting `R0 in out` in the SPICE output, and its value changing as
you reshape the strip.

There is a guided version of this exercise at <https://tinytapeout.com/siliwiz/resistors/>.

> **Warning:** SiliWiz is not SKY130, and its numbers are not the ones in this lab. Its
> `polyres` layer is documented as *"400 ohms per square"*. SKY130's `res_high_po` is
> 317.2198 Ω/□ measured, and 319.8 Ω/□ in the Magic layout tool's tables (see
> [Ohms per square](guide/ohms-per-square.md)). SiliWiz uses round numbers chosen
> for teaching. Use it for the cross-section and ngspice for the value.

## Finishing

You are done when `make mine check` prints `PASS -- every number matches the reference run.`
Your two resistors pass if each is within 1 % of its target. The checker also compares every
simulated resistance with the reference run (within 0.5 %) and the two extracted constants
(within 1 %), which is what "matches the reference run" means.

A DC operating point has no randomness in it, so on the pinned image (ngspice-47, `sky130A`, `tt`
corner, 27 °C) your numbers match these to every digit shown:

| | `res_high_po` | `res_xhigh_po` |
|---|---|---|
| Ω per square | 317.2198 | 2118.7619 |
| end resistance | 378.2448 Ω | 34.2111 Ω |
| card advertises | 317.3885 | 2000.0 |
| L for 10 kΩ at W = 1 µm | 30.3315 µm | 4.7036 µm |
| L for 100 kΩ at W = 1 µm | 314.0465 µm | 47.1812 µm |

After your own numbers pass, read
[`solutions/README.md`](https://github.com/uoftasic/ad102/blob/main/labs/lab-01-a-resistor-you-designed/solutions/README.md)
for the reference sizing and some questions worth arguing about.

Next on the [Course path](README.md#course-path): read the four pages in row 3, starting with
[Capacitors on a chip](guide/a-capacitor-is-a-sandwich.md), then do
[Lab 02 — How big is a picofarad?](labs/lab-02-how-big-is-a-picofarad-overview.md).

## Expected warnings and delays

**Silence.** Every ngspice run in this lab loads
`.lib /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice tt`, which pulls in 12 MB of model
cards for every device in SKY130, mostly MOSFETs you are not using. ngspice prints nothing while
it loads, for anywhere from about 10 seconds to a minute per run depending on your machine (the
comment at the top of the Makefile records 55–65 s). `make` runs the simulator twice, so allow up
to about two minutes. It is not hung.

**170 `unrecognized parameter` lines, in 34 blocks**, in `results/sheet.log`. A `rhead_model`
block has four of these lines and a `rbody_model` block has six; here is a head block:

```
Warning: Model issue on line 4842 :
  .model xl1:rhead_model r sw_et=0 isnoisy=0 rsh=    3.458312000000000e+02 ...
unrecognized parameter (sw_et) - ignored
unrecognized parameter (isnoisy) - ignored
unrecognized parameter (p2) - ignored
unrecognized parameter (q2) - ignored
```

SkyWater writes one set of model cards for several simulators. `sw_et`, `isnoisy` and
`p2`/`q2`/`p3`/`q3` are Spectre-flavoured keywords for self-heating, noise and voltage
coefficients, which ngspice does not implement. ngspice says so and carries on with the parameters it does understand, which
are the ones this lab measures. There are thirty-four blocks for twenty-two resistors because
most of these devices expand into more than one `.model` card.

**A line that starts with `Error`** is different. That one stops the run, and your log will
contain no `r_` lines at all; the checker, `src/check_res.py`, tells you to look for exactly
that.
