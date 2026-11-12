# Getting started

AD102 uses two tools from the workbench you set up in IC101. **ngspice**, the open-source
descendant of Berkeley SPICE, simulates a circuit and tells you what it would do. **XSchem** is
the schematic editor that draws circuits for it. Both are already in the image, so nothing on
this page installs anything. This page explains how the pieces fit together, the warnings you
will see every day, and the one mistake that costs students the most time. You'll do the setup
itself in [Lab 01, Part 1](labs/lab-01-a-resistor-you-designed-overview.md#part-1-set-up-the-workbench).

## What this course assumes

| Requirement | Notes |
|-------------|-------|
| **[IC101](https://uoftasic.com/ic101/) completed** | The workbench comes up in your browser and the smoke test passes |
| **[AD101](https://uoftasic.com/ad101/) completed** | You can read a waveform, a spectrum, and a Bode plot |
| ECE110-level circuit analysis | Helpful, not required: $V=IR$, series and parallel, and what an RC corner is. AD101 covers the last one. |

AD102 does not re-teach linear circuit analysis. Node equations, Thévenin equivalents and phasors
belong to ECE110. This course asks two questions that course doesn't: where did the component
come from, and what did it cost?

## The PDK setting

A **Process Design Kit (PDK)** is the foundry's description of what a process can build: the
device models, the schematic symbols, and the drawing rules. Think of it as the parts catalogue
for a chip.

The workbench image can simulate more than one process, and the environment variable `PDK` picks
which one. The image's default is `ihp-sg13g2`, a real 130 nm process from IHP in Germany. It is
a perfectly good process, but it is not the one this course measures. AD102 uses SKY130
(`sky130A`).

The workspace repo from IC101 has a setup script, `/foss/designs/common/.designinit`, that
switches you to SKY130. You load it with a leading `.`:

```bash
. /foss/designs/common/.designinit
```

The `.` is the shell's `source` command. It runs the file in your current shell rather than in
a child process, which is the only way a script can change your environment. Typing the path
without the dot and the space does nothing useful. Because it only changes the current shell,
every new terminal needs it. On the IC101 workbench the image does this for you when a terminal
opens (the `workspace` repo's own `.designinit` chains to this file), so you will usually find
`PDK` already set to `sky130A`. Loading it again does no harm.

XSchem reads `$PDK` when it starts to decide which symbol library to load. Before
`.designinit`, its settings come from `~/.xschem/xschemrc`, which does this:

```
# Source the PDK xschemrc file
source $env(PDK_ROOT)/$env(PDK)/libs.tech/xschem/xschemrc
```

After `.designinit`, XSchem uses the workspace's own `common/xschemrc` instead, and that reads
`$PDK` too. Either way, the `PDK` variable picks the parts catalogue. On the default you get a library called
`sg13g2_pr`; after `.designinit` you get `sky130_fd_pr`. (`_pr` is the foundry's shorthand for
**primitive devices**: the transistors, resistors and capacitors themselves, as opposed to logic
gates built from them.) If you launch XSchem on the default, you get a schematic editor full of
`sg13g2_*` devices and no SKY130 resistor anywhere, and there is no error message, because
nothing is broken. You opened a different foundry's catalogue.

The habit to build: run `echo $PDK` before you launch XSchem. It should say `sky130A`.

The lab decks don't need the PDK setting; XSchem does (see
[How the labs work](#how-the-labs-work) below). You still need `.designinit` to get the course
files, because it also defines `mod`.

## Where your files live

`.designinit` also defines a shell function called `mod`. `mod add ad102` clones this course into
`/foss/designs/modules/ad102`, and `mod ad102` takes you there afterwards. `/foss/designs` inside
the container is your `workspace` clone on your own computer, shared into the container (a bind
mount), so the course files are in `workspace/modules/ad102` on your disk, and deleting the
container does not delete your work.

## The `u` suffix trap

This mistake produces no error message, which is why it is described here before you meet it
in Lab 01.

In an ngspice deck, most numbers take SI suffixes: `1k` is a thousand ohms, `0.7p` is 0.7
picofarads, `3n` is three nanoseconds. So it seems reasonable to write a device one micron wide
as `W=1u`.

SKY130 device widths and lengths do not work that way. In this PDK, `W` and `L` are already
plain micron numbers. `W=1` means one micron. `W=1u` means one micron × 10⁻⁶, which is smaller
than an atom.

Here are the two ways of writing a SKY130 high-sheet poly resistor, one micron wide and ten long.
This is an excerpt, not a file to save; the complete deck ships as
`labs/lab-01-a-resistor-you-designed/spice/u_trap.spice`.

```spice
Xa a 0 0 sky130_fd_pr__res_high_po W=1  L=10
Xb b 0 0 sky130_fd_pr__res_high_po W=1u L=10u
```

The deck pushes exactly 1 µA through each and reads the resistance as $V/I$. The right one
gives 3550.443 Ω and the wrong one gives 3193.812 Ω. The wrong one does not blow up, and it does
not return zero, infinity or a negative number you would notice. It returns an ordinary
resistance 10 % away from the right answer, which is the size of error you would blame on a
model, a corner, or yourself.

One line in the log tells you, buried in the middle of the run:

```
Warning: r.xb.rbody: resistance too low or not given, set to 1 mOhm
```

ngspice still exits with status 0. You'll run this deck yourself in
[Lab 01, Part 8](labs/lab-01-a-resistor-you-designed-overview.md#part-8-optional-the-u-suffix-trap).

Transistors fail louder. The same mistake on a MOSFET, which you'll meet again in
[AD103](https://uoftasic.com/ad103/), stops the simulator:

```
could not find a valid modelname
    Simulation interrupted due to error!

Error: incomplete or empty netlist
       or no ".plot", ".print", or ".fourier" lines in batch mode;
no simulations run!
```

A foundry's model table is split into **bins**: each row is valid over a stated range of widths
and lengths. A device whose geometry nobody characterised matches no bin, so it is rejected. That
error is the good outcome. The resistor's quiet 3193.812 Ω is the bad one.

The rule: in any SKY130 deck, `W`, `L`, `w` and `l` carry no unit suffix. If a resistance is
close but not right, look for a stray `u` before you look anywhere else.

## Expected warnings

Run any deck containing a SKY130 poly resistor and ngspice prints this before it has done a
single calculation:

```
Warning: Model issue on line 4842 :
  .model xa:rhead_model r sw_et=0 isnoisy=0 rsh=    3.458312000000000e+02  ...
unrecognized parameter (sw_et) - ignored
unrecognized parameter (isnoisy) - ignored
unrecognized parameter (p2) - ignored
unrecognized parameter (q2) - ignored

Warning: Model issue on line 4843 :
  .model xa:rbody_model r sw_et=0 isnoisy=0 rsh=    3.173885000000000e+02  ...
unrecognized parameter (sw_et) - ignored
unrecognized parameter (isnoisy) - ignored
unrecognized parameter (p2) - ignored
unrecognized parameter (q2) - ignored
unrecognized parameter (p3) - ignored
unrecognized parameter (q3) - ignored
```

That is ten `unrecognized parameter` lines and two `Warning:` headers for one resistor. A deck
with many resistors repeats the block (Lab 01's 22-strip deck prints 170 such lines), and nothing
is wrong. SkyWater's resistor model cards carry parameters for noise and self-heating that this
build of ngspice does not implement. ngspice names them, skips them, and carries on, and your
resistance is unaffected.

The block does tell you something useful. Each resistor has two models, not one: a
`rhead_model` at `rsh = 345.8312` Ω per square and a `rbody_model` at `rsh = 317.3885` Ω per
square. ("Ohms per square" is the unit chip designers use for a material's resistance;
[Ohms per square](guide/ohms-per-square.md) explains it.) The ends of a drawn resistor are not made of the same material as the middle. That is
why one drawn square of this device measures 695.4646 Ω rather than the 317.3885 Ω on the card,
and explaining that gap is the first job in
[Lab 01](labs/lab-01-a-resistor-you-designed-overview.md).

To tell a warning from a real failure: a genuine ngspice failure starts a line with `Error:`, and
the run ends with `no simulations run!`. `Warning:` lines like the ones above can be ignored.

## How the labs work

Every AD102 lab is a package with a `Makefile`. You go to the lab folder and type `make`, and it
ends by printing a verdict: a line that says whether what you built matches what the lab
expected, rather than a wall of numbers to squint at. `make` runs everything; each lab also has
smaller targets, such as `make mine` (simulate only the file you edit) and `make check` (print
the verdict again from the logs already written). Each package's README lists them.

All four lab packages run in a bare container with no environment setup: no `.designinit`, no
`mod`, and `$PDK` still `ihp-sg13g2`. Every deck names its SKY130 model file by absolute path,
so the PDK setting above cannot affect them. If your setup went wrong, run `make` anyway; it will
still work, by design.

The exception is an optional GUI step. `make edit` in
[Lab 03](labs/lab-03-a-time-constant-in-silicon-overview.md) opens the RC circuit in XSchem, and
XSchem does read `$PDK` from your environment, so that step needs `.designinit` to have worked.
The `make` that produces Lab 03's verdict does not.

### Why the first `make` fails

Every AD102 lab package ships the design a first-year student would draw: the naive one, sized
straight off the model card. The checker rejects it on purpose, and says so:

```
  ^ On a fresh clone this FAIL is the lab, not a broken
    package. spice/my_resistor.spice ships with the naive
    sizing on purpose. Edit the two L= numbers and run
    `make mine check` again.
```

You read your own wrong number, work out where the missing ohms went, and fix the one line that
was wrong. `make` exits non-zero on a `FAIL`, so a red exit code at this point is expected, not a
sign of a broken clone.

## SiliWiz

Part of this course is looking at a **cross-section**: what a resistor or capacitor looks like
sliced through, layer by layer. [SiliWiz](https://tinytapeout.com/siliwiz/) does that in a
browser with nothing to install. You draw shapes on a simplified SKY130 layer stack, and it shows
you the silicon underneath and simulates it. You'll use it in optional parts of Labs 01 and 02
and in the [capstone](labs/capstone-floor-plan-overview.md).

## Launch GUI tools from a terminal

These tools print their error messages to the terminal you launched them from, not into their
own window. So launch GUI tools by typing their name in a terminal, never from a desktop icon. If
you start XSchem from the applications menu and something goes wrong, the explanation is written
to a terminal that does not exist, and you see a program that silently does nothing.

## Getting help

The course is self-paced, but you don't have to work alone.

- Ask in the [team Discord](https://discord.gg/hrJnP5UsGz). No question is too basic; most of
  what looks like your mistake here is a tool being unhelpful.
- Quote the exact error and the exit code. ngspice's first `Error:` line is the real one, and
  everything after it is fallout. Paste that line, the command you ran, and what
  `ngspice -v | head -2` says.
- Say what the number was. Analog debugging is mostly comparing a number you got against a
  number you expected. "The filter is wrong" is hard to help with; "I expected 3550.443 Ω and got
  3193.812 Ω" can be answered in one reply.
- If a command on these pages does not do what the page says, that is a bug in the course, so
  please report it. Every command here was run before it was written, so a mismatch means
  something has drifted and we want to know.

Next: [Resistors on a chip](guide/a-resistor-you-cannot-buy.md).
