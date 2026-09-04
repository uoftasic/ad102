# Getting started

**Question this page answers:** *How do I get from a browser tab to a prompt where a SKY130
resistor simulates?*

AD102 adds two tools to the workbench you already have: **ngspice**, the open-source descendant
of Berkeley SPICE, which answers "what would this circuit actually do?"; and **XSchem**, the
schematic editor that draws circuits for it. Both are already inside the image. Nothing on this
page installs anything.

Four steps, one version check, and one trap that is worth reading before you meet it.

## What this course assumes

| Requirement | Notes |
|-------------|-------|
| **[IC101](https://uoftasic.com/ic101/) completed** | The workbench comes up in your browser and the smoke test passes |
| **[AD101](https://uoftasic.com/ad101/) completed** | You can read a waveform, a spectrum, and a Bode plot |
| ECE110-level circuit analysis | Helpful, not required. $V=IR$, series/parallel, and what an RC corner is. AD101 covers the last one. |

**What this course does not do** is re-teach linear circuit analysis. Node equations, Thévenin
equivalents and phasors belong to ECE110 and stay there. AD102 starts one step behind that
material — at the question *where did the component come from?* — and one step ahead of it —
*what did it cost?*

## 1. Start the desktop

On your own machine, in your `workspace` clone:

```bash
cd workspace
./scripts/start_vnc.sh          # Windows: scripts\start_vnc.bat
```

Open **http://localhost/** and open a terminal on that desktop. Every command below is typed
*inside* that terminal, not on your laptop.

Ports, passwords, resolution, and what to do when the page is blank:
[IC101 — Launch the noVNC desktop](https://uoftasic.com/ic101/#/guide/launch-novnc).

## 2. Load the environment

```bash
. /foss/designs/common/.designinit
```

```
ASIC-EDU: PDK=sky130A  PDK_ROOT=/foss/pdks  designs=/foss/designs
          run 'mod' to list course modules, or 'mod <name>' to enter one.
```

That leading `.` is the shell's `source` command: it runs the file *in your current shell*
rather than in a child process, which is the only way a script can change your environment.
Typing the path without the dot and the space does nothing useful.

You must do this **in every new terminal.** It does not stick.

### Try this — find out what PDK you were on

**Process Design Kit (PDK):** the foundry's description of what a process can build — the
device models, the symbols, the drawing rules. It is the parts catalogue for a chip.

Open a fresh terminal, and *before* sourcing anything, ask which device library XSchem would
load. (`_pr` is the foundry's shorthand for **primitive devices** — the transistors, resistors
and capacitors themselves, as opposed to logic gates built out of them.)

```bash
echo "PDK is: $PDK"
ls $PDK_ROOT/$PDK/libs.tech/xschem/ | grep _pr
```

**What you should see:**

```
PDK is: ihp-sg13g2
sg13g2_pr
```

Now source `.designinit` and run exactly the same two commands:

```
PDK is: sky130A
sky130_fd_pr
sky130_fd_pr.patch
```

**Why an engineer cares:** those two directory listings are the symbol libraries XSchem loads.
The image's default PDK is `ihp-sg13g2` — a real 130 nm process from IHP in Germany, and a
perfectly good one, but not the one this course measures. The wiring is one file:

```bash
cat ~/.xschem/xschemrc
```

```
# Source the PDK xschemrc file
source $env(PDK_ROOT)/$env(PDK)/libs.tech/xschem/xschemrc
```

XSchem reads whatever `$PDK` says, and so does the workspace's own `common/xschemrc`, which
`.designinit` switches you to. Either way, the PDK variable picks the parts catalogue. Launch
XSchem on the default and you get a schematic editor full of `sg13g2_*` devices and **no SKY130
resistor anywhere** — with no error message, because nothing is broken. You opened a different
foundry's catalogue, which is a thing you are allowed to do.

**Reflex check:** `echo $PDK` before you launch XSchem. It should say `sky130A`.

## 3. Get the course files

```bash
mod add ad102      # first time only — clones github.com/uoftasic/ad102
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

`mod` is a shell function that `.designinit` defines. Everything lands under
`/foss/designs/modules/`, which is your `workspace` folder bind-mounted into the container.
Your files are on **your** disk; deleting the container does not delete your work.

### Three errors you will see at least once

| What you see | What it means |
|---|---|
| `bash: mod: command not found` | You did not run step 2 *in this terminal*. Every new tab starts clean. |
| `mod: no such module: ad102` | You ran `mod ad102` before `mod add ad102`. |
| `fatal: could not read Username for 'https://github.com'` | git is being asked to log in, which means it could not read the repo anonymously. Check the spelling first; if it is right, ask in [Discord](https://discord.gg/hrJnP5UsGz) — do not type your password. |

## 4. Check your versions

Two tools carry this course:

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

**`ngspice-47` and `V3.4.8RC` are the numbers that matter.** If you see something else you are
on a different image, and commands on these pages may fail in ways this course does not
describe.

The rest of the image, if you want to confirm it is all there. You do not need these for AD102 —
they are the AD104 layout toolchain, and they are listed so you know the image is complete:

| Tool | Command | Expect |
|---|---|---|
| ngspice | `ngspice -v \| head -2` | `** ngspice-47 : Circuit level simulation program` |
| XSchem | `xschem -v \| head -1` | `XSCHEM V3.4.8RC` |
| Magic | `magic -dnull -noconsole --version` | `8.3.681` |
| KLayout | `klayout -v` | `KLayout 0.30.11` |
| Netgen | `netgen -batch quit \| head -1` | `Netgen 1.5.323 compiled on …` |

> **Scary-but-normal:** `netgen -batch quit` also prints
> `Warning: netgen command 'format' use fully-qualified name '::netgen::format'` and a second
> line like it. Those are Tcl namespace notices from the tool talking to itself. They are not
> about your design, and there is nothing to fix.

## 5. The trap that will cost you an afternoon: `u`

This one is worth five minutes now, because it will otherwise cost you an evening — and
because **it does not announce itself.**

In an ngspice deck, most numbers take SI suffixes: `1k` is a thousand ohms, `0.7p` is 0.7
picofarads, `3n` is three nanoseconds. So it is completely reasonable to write a device one
micron wide as `W=1u`.

**SKY130 device widths and lengths do not work that way.** In this PDK, `W` and `L` are already
plain micron numbers. `W=1` *means* one micron. `W=1u` means one micron × 10⁻⁶, which is smaller
than an atom.

Here are the two device lines — a SKY130 high-sheet poly resistor, one micron wide and ten
long — written the right way and the wrong way. **This is an excerpt, not a file to save.**
The complete deck ships as
`labs/lab-01-a-resistor-you-designed/spice/u_trap.spice`, and
[Lab 01](labs/lab-01-a-resistor-you-designed-overview.md) runs it for you.

```spice
Xa a 0 0 sky130_fd_pr__res_high_po W=1  L=10
Xb b 0 0 sky130_fd_pr__res_high_po W=1u L=10u
```

Both are in one deck, with exactly 1 µA pushed through each, and the resistance read off as
$V/I$. When you get to Lab 01:

```bash
cd labs/lab-01-a-resistor-you-designed && make utrap
```

```
--- the same device, written two ways (ohms) ---
good = 3.550443e+03
bad = 3.193812e+03

   and the one line that told you, buried in the log:
Warning: r.xb.rbody: resistance too low or not given, set to 1 mOhm
   ngspice exit status: 0
```

**3550.443 Ω and 3193.812 Ω.** Look at what the wrong one did. It did not blow up. It did not
return zero, or infinity, or a negative number you would have spotted across the room. It
returned a perfectly ordinary resistance **10 % away from the right answer** — exactly the
size of error you would blame on a model, a corner, or yourself.

There is one line that tells you, and it is the one `make utrap` digs out of the middle of the
run — `Warning: r.xb.rbody: resistance too low or not given, set to 1 mOhm`. ngspice still
**exits 0**.

Transistors fail louder. The same mistake on a MOSFET — which is where you meet it again in
[AD103](https://uoftasic.com/ad103/) — stops the simulator outright:

```
could not find a valid modelname
    Simulation interrupted due to error!

Error: incomplete or empty netlist
       or no ".plot", ".print", or ".fourier" lines in batch mode;
no simulations run!
```

A device with a geometry nobody characterised has no model **bin** to fall into, so it is
rejected. (A *bin* is one row of the foundry's model table, valid over a stated range of widths
and lengths; a device outside every row matches nothing.) That message is the good outcome.
The resistor's quiet 3193.812 Ω is the bad one.

**Reflex check:** in any SKY130 deck, `W`, `L`, `w` and `l` carry **no unit suffix**. If a
resistance is close-but-not-right, look for a stray `u` before you look anywhere else.

## Scary-but-normal: the warning block every resistor prints

Run *any* deck containing a SKY130 poly resistor and ngspice greets you with this, before it
has done a single calculation:

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

Ten `unrecognized parameter` lines and two `Warning:` headers, every single run. **Nothing is
wrong.** SkyWater's resistor model cards carry parameters for noise and self-heating that this
build of ngspice does not implement; it names them, skips them, and carries on. Your resistance
is unaffected.

Two things in that block are worth a second look, because they are the whole of Part I in
advance. There are **two** models per resistor, not one — a `rhead_model` at
`rsh = 345.8312` Ω per square and a `rbody_model` at `rsh = 317.3885` Ω per square. The ends of
a drawn resistor are not made of the same stuff as the middle. That is why one drawn square of
this device measures **695.4646 Ω** rather than the 317.3885 Ω on the card, and it is the first
thing [Lab 01](labs/lab-01-a-resistor-you-designed-overview.md) makes you explain.

**How to tell this from a real failure:** a genuine ngspice failure starts a line with
`Error:` and the run ends with `no simulations run!`. `Warning:` lines are scenery.

## How the labs work

Every lab in AD102 is a package with a `Makefile`, and every one of them ends by printing a
**verdict** — not a wall of numbers for you to squint at, but a line that says whether what you
built matches what the lab expected.

```bash
cd labs/lab-01-a-resistor-you-designed
make
```

**All four labs run in a bare container with no environment setup at all** — no `.designinit`,
no `mod`, `$PDK` still `ihp-sg13g2`. Every deck names its SKY130 model file by absolute path, so
the PDK trap in step 2 cannot reach them. If your setup went wrong, run `make` anyway; it will
still work, and that is deliberate.

**The one exception is a GUI step, not a lab.** `make edit` in
[Lab 03](labs/lab-03-a-time-constant-in-silicon-overview.md) opens the same RC in XSchem, and
XSchem *does* read `$PDK` from your environment. That step needs step 2 to have worked. The
`make` that produces Lab 03's verdict does not.

### Your first `make` will say FAIL, and that is the lab

Every AD102 lab package ships the design a first-year actually draws — the naive one, sized
straight off the model card — and the checker rejects it. That is deliberate, and the verdict
says so in as many words:

```
  ^ On a fresh clone this FAIL is the lab, not a broken
    package. spice/my_resistor.spice ships with the naive
    sizing on purpose. Edit the two L= numbers and run
    `make mine check` again.
```

You are meant to read your own wrong number, work out where the missing ohms went, and fix the
one line that was wrong. A package that printed `PASS` before you had touched it would have
taught you nothing. `make` exits non-zero on a `FAIL`, so a red exit code at this point is the
expected outcome, not a broken clone.

## One browser tab: SiliWiz

Part of this course is looking at a **cross-section** — what a resistor or capacitor looks like
sliced through, layer by layer. [SiliWiz](https://tinytapeout.com/siliwiz/) does that in a
browser with nothing to install: you draw shapes on a simplified SKY130 layer stack and it
shows you the silicon underneath and simulates it. It is used in
[From schematic to cross-section](guide/from-schematic-to-cross-section.md) and it is genuinely
worth the tab.

## Where the error messages actually are

**These tools print to the terminal you launched them from, not into their own window.** So:
**launch GUI tools by typing their name in a terminal**, never from a desktop icon. Start
XSchem from the applications menu and something goes wrong, and the explanation is written to a
terminal that does not exist — you get a program that silently does nothing.

## You are ready when

```bash
. /foss/designs/common/.designinit
mod ad102
echo $PDK                      # sky130A
ngspice -v | head -2           # ** ngspice-47 : Circuit level simulation program
ls labs/                       # the four lab packages, plus passives-decks
```

Next: [A resistor you cannot buy](guide/a-resistor-you-cannot-buy.md), where the component you
have used a hundred times turns out to have no drawer to come out of — and its value turns out
to be a decision about shape.

## Getting help

This course is self-paced, which is not the same as alone.

- **Ask in the [team Discord](https://discord.gg/hrJnP5UsGz).**
  There is no such thing as a question too basic — most of what looks like a mistake here is
  the tool being unhelpful, not you.
- **Quote the exact error, and the exit code.** ngspice's first `Error:` line is the real one;
  everything after it is fallout. Paste that line, the command you ran, and what
  `ngspice -v | head -2` says.
- **Say what the number was.** Analog debugging is mostly comparing a number you got against a
  number you expected. "The filter is wrong" is hard to help with; "I expected 3550.443 Ω and
  got 3193.812 Ω" is one reply long.
- **If a command in these pages does not do what the page says it does, that is a bug in the
  course.** Report it. Every command here was run before it was written, so a mismatch means
  something drifted and we want to know.
