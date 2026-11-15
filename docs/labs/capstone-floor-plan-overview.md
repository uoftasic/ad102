# Capstone: Defend a floor plan

You'll read the SKY130 layer stack out of the PDK, look at a resistor, a capacitor and a wire in
cross-section, and then size a 1 MHz on-chip low-pass filter and defend its area. There's no lab
package for this capstone: Part 1 is a single command, Part 2 happens in a browser, and Part 3 is
a page of arithmetic with numbers you've already measured.

## Before you start

- Finish Labs [01](../labs/lab-01-a-resistor-you-designed-overview.md),
  [02](../labs/lab-02-how-big-is-a-picofarad-overview.md) and
  [03](../labs/lab-03-a-time-constant-in-silicon-overview.md) first, because Part 3 uses the
  numbers you measured in them. The corner results from
  [Lab 04](../labs/lab-04-two-resistors-that-disagree-overview.md) help with the last step of
  Part 3, where you decide whether you would build the filter at all.
- Read [From schematic to cross-section](../guide/from-schematic-to-cross-section.md).
- You need a terminal in the workbench for Part 1, a browser tab for Part 2, and paper or a
  spreadsheet for Part 3.

Time: about 1.5 hours.

## Part 1: Read the layer stack

How tall is the SKY130 wiring stack, and what is the resistivity of the poly you used in Lab 01?

1. Print the `height` lines of Magic's technology file for the main layers:

   ```bash
   sed -n '/^ height/,/^$/p' /foss/pdks/sky130A/libs.tech/magic/sky130A.tech | grep -wE 'dnwell|nwell,pwell|alldiff|allpoly|allli|allm1|allm2|allm3|allm4|allm5|mrdl'
   ```

   The first number on each line is how far the bottom of the layer sits above the wafer
   surface, and the second is its thickness, both in µm. (Without the `grep`, the block also
   lists fill, contact, via and MIM layers: 30 lines in all.)

2. Add metal5's bottom height and its thickness to find how high the top of the wiring stack
   sits.

3. Multiply your Lab 01 sheet resistance for `res_high_po` (317.2198 Ω/□) by the poly thickness
   to get its resistivity.

**You should see:** eleven `height` lines, from `dnwell` at −0.1 µm to `mrdl` at 7.2611 µm, with
`allpoly` at `0.3262 0.18` and `allm5` at `5.3711 1.26`. The top of metal5 is 6.6311 µm above the
silicon, and $\rho = 317.2198 \times 0.18\times10^{-6} = 5.7100\times10^{-5}\ \Omega\,\text{m}$.

## Part 2: Look at cross-sections in SiliWiz

Where in the silicon do Lab 01's end resistance, Lab 02's edge term and the capacitor you never
drew come from?

A list of heights from a file doesn't give you much feel for what the layers look like, so in
this part you'll use SiliWiz, which shows a live cross-section under whatever layout you draw.
Open **<https://app.siliwiz.com/?preset=blank>**.

> **Warning:** SiliWiz doesn't model SKY130. Its layer stack, permittivities and numbers are
> simplified for teaching, and its cross-section is a cartoon of the table on
> [From schematic to cross-section](../guide/from-schematic-to-cross-section.md#the-layer-stack)
> rather than a rendering of it. Use it for the shape of the answer
> ("the current turns two corners", "the field bends around the edge",
> "there is a plate under everything"), and take the values from the tech file and your ngspice
> runs. There are guided walkthroughs for
> [resistors](https://tinytapeout.com/siliwiz/resistors/) ·
> [capacitors](https://tinytapeout.com/siliwiz/capacitors/) ·
> [parasitics](https://tinytapeout.com/siliwiz/parasitics/).

### The resistor you designed

1. Draw a **polyres** rectangle, long and thin: 20 grid units by 2, roughly the shape of your
   Lab 01 resistor.
2. Put a **metal1 via** (the contact) at each end and a **metal1** pad over each via.
3. Label the two pads `a` and `b` (click a pad, then **Set Label** or press `S`), and tick
   **Show SPICE** at the bottom. The resistance appears on the line that starts with `R0`.
4. Look at the **cross-section** pane and follow the current path: down the metal1 pad, through
   the contact, along the poly strip, up the far contact, and out the far pad.
5. Drag the strip longer and watch what the resistance does.

You should see the resistance climb linearly as the strip gets longer, while the two ends stay as
they were. Where, in that current path, is the 378.2448 Ω of end resistance you accounted for in
Lab 01?

<details>
<summary>Answer</summary>

The current doesn't travel in a straight line through one material: it makes two right-angle
turns through a contact much smaller than the strip. That detour is the end resistance, and in
the cross-section you can point at it. That's why $R = R_\square L/W$ has a constant added to it,
and why the constant doesn't scale with length.

</details>

### The capacitor you designed

1. Start a new drawing. Put down a **metal1** rectangle, and a **metal2** rectangle the same size
   directly over it.
2. Label them and tick **Show SPICE**.
3. Find the capacitance between them, then drag the top plate so it overhangs the bottom one.

As you push the plates out of alignment, does the capacitance fall in proportion to the overlap
area?

<details>
<summary>Answer</summary>

No. It falls more slowly than the overlap does, because the field still bends around the edges
of the plates. That edge field is the perimeter term, which is the middle coefficient of the
$C = 2.000000\,s^2 + 0.659991\,s - 0.017742$ fF fit from Lab 02, Part 2.

</details>

### The parasitic you did not draw

1. Start a new drawing. Draw a single **metal1** wire and nothing else, and label it.
2. Read the SPICE output.

You should see a capacitor from the wire to the substrate in the SPICE output, even though you
didn't draw one. Why is it there?

<details>
<summary>Answer</summary>

The cross-section shows why: the wire is a bar, the substrate is a plane underneath it, and the
field from the wire has nowhere to go but down into that plane. The guide page
[Parasitic capacitance](../guide/the-capacitor-you-did-not-draw.md) is about exactly this.

</details>

## Part 3: Defend a floor plan

What is the smallest 1 MHz low-pass filter you can actually build on this chip, and would you
build it?

Here is the brief. Build a first-order low-pass filter with a corner at 1 MHz, on-die, in SKY130.
You may use `res_high_po`, `res_xhigh_po` and `cap_mim_m3_1`, and you must state the drawn area
and defend it.

Work through it in this order:

1. Fix the product. $RC = 1/(2\pi f_c) = 159.15$ ns is your only hard constraint, and it fixes
   only the product, so you're free to split it between $R$ and $C$ however you like.
2. Price both halves. From Lab 01, `res_high_po` at $W = 1$ µm needs
   $L = (R - 378.2448)/317.2198$ µm of length, and `res_xhigh_po` needs
   $L = (R - 34.2111)/2118.7619$ µm. Because the strip is 1 µm wide, the length in µm is also
   its area in µm². From Lab 02, a MIM plate of side $s$ holds
   $2.000000\,s^2 + 0.659991\,s - 0.017742$ fF and takes up $s^2$ µm². Tabulate the total area
   of the resistor and capacitor together for $R$ = 10 kΩ, 100 kΩ, 1 MΩ and 10 MΩ.
3. Find the minimum, then find the limit. The total area has a minimum somewhere in your table,
   the same shape you found in [Lab 03, Part 6](../labs/lab-03-a-time-constant-in-silicon-overview.md#part-6-your-own-20-ns-time-constant).
   Then check your answer against
   [What a resistor costs in area](../guide/what-a-value-costs-in-area.md), where 1 MΩ of
   `res_high_po` comes to 3.15 mm of poly. Which of your rows could you actually build on a 3 mm
   die?
4. Check the resistor against itself. In
   [Lab 03, Part 5](../labs/lab-03-a-time-constant-in-silicon-overview.md#part-5-a-one-microsecond-rc),
   a bare 471.98 µm strip of 1 µm poly carried 95.278 fF to the substrate, and half of that was
   added to the time constant. Lab 03, Part 2 fitted that capacitance as 0.1994 fF per µm of
   length plus 1.187 fF for the ends. At what resistor length does the parasitic become a visible
   fraction of the capacitor you were planning? That length is the limit, and it's the reason the
   answer isn't simply "use an enormous resistor".
5. Price it in adders. Convert your best area into DD103 ripple-carry adders, at 110.1056 µm²
   each, and write out the sentence "my one filter pole costs N adders."
6. Decide whether you would build it, or whether you would rather do what
   [What to build instead of an inductor](../guide/what-analog-builds-instead.md) describes and
   move the pole off-chip or into the digital domain.

**You should see:** an area table with a minimum in it, at least one row you have ruled out as
unbuildable, and a single number of adders for your chosen design.

## Finishing

You're done when you have the area table from step 2 with its minimum marked and at least one
row ruled out (with the reason), the sentence from step 5 with your number in it, and an answer
to step 6 you can defend.

There is no package and no marking scheme for this capstone.

Submit: nothing. If you'd like to argue about a floor plan, bring your area table to the
[team Discord](https://discord.gg/hrJnP5UsGz).

Next on the [Course path](../index.md#course-path): this capstone is its last row, so you have
finished AD102. The home page lists the [next courses](../index.md#next-courses).
