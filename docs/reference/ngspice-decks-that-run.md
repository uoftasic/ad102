# ngspice deck recipes

The smallest deck that measures a passive device, for each kind of measurement in AD102, what
ngspice says when you get it wrong, and the warnings each lab prints that you can ignore.

AD102 asks five questions of silicon: how many ohms, how many farads, how many henries, how long
is the time constant, and how much does all of that move? Each has a deck shape you can reuse.
This page shows those five shapes, with the exact output each produced in
`hpretl/iic-osic-tools:2026.08`, ngspice 47, PDK `sky130A`.

Every block below is an **excerpt** from a deck that ships in a lab package, and the path is
named beside it. Nothing here is a file for you to create; run the shipped deck and edit that.

## The five parts of a deck

Write them in this order. ngspice only cares that `.end` is last:

| Part | Looks like | Notes |
|---|---|---|
| 1. title | `* AD102 Lab 01 -- the sheet resistance deck` | **The first line is always a comment**, whatever you put in it. Put a real title there; ngspice will eat a device line that lands in position 1. |
| 2. models | `.lib /foss/pdks/.../sky130.lib.spice tt` | absolute path, so the deck runs anywhere |
| 3. devices and sources | `Xa a 0 0 sky130_fd_pr__res_high_po W=1 L=10` | see [the catalogue](reference/sky130-passive-catalogue.md) |
| 4. what to do | `.control` … `.endc`, or `.op` / `.ac` / `.tran` cards | |
| 5. `.end` | `.end` | |

Run it in batch mode (run, print, exit):

```bash
ngspice -b spice/sheet.spice
```

Without `-b` you land in an interactive prompt and the terminal looks hung; type `quit` to get
your results.

## 1. Resistance: `.op` and Ohm's law

There is no "measure the resistance" command. You push a current you chose through the device
and divide the resulting voltage by it.

From `labs/lab-01-a-resistor-you-designed/spice/sheet.spice`:

```spice
Il1 0 l1 dc 1u
Xl1 l1 0 0 sky130_fd_pr__res_high_po W=1 L=1
```

```spice
.control
op
let r_L1 = v(l1)/1u
print r_L1
.endc
```

```
r_l1 = 6.954646e+02
```

That is 695.4646 Ω for one drawn square of a device whose model card says 317.3885 Ω/□, which
is the subject of [Ohms per square](guide/ohms-per-square.md).

Three things about that pattern:

- **1 µA is deliberate.** It is small enough that the resistor's own self-heating and voltage
  coefficient do not move the answer, and large enough to be far from numerical noise. Push
  1 mA through 100 kΩ and you are asking a different question.
- **`let` before `print`.** `v(l1)/1u` is an *expression*; `r_L1` is a vector. `print` takes
  either, but `meas` does not, and the habit costs nothing.
- **Vector names come back lower-case.** You wrote `r_L1`, and ngspice prints `r_l1`. That
  matters when you `grep` the log.

If you drive with a voltage source instead, the current comes out of the source and is
negative, so the resistance is `1m/(-i(va))`, as in
`labs/passives-decks/spice/corners.spice.in`:

```spice
let R_A = 1m/(-i(va))
```

## 2. Capacitance: one `.ac` point

A capacitor has no DC behaviour to measure, so ask it at one frequency and undo $Z = 1/(j\omega
C)$.

From `labs/lab-02-how-big-is-a-picofarad/spice/picofarad.spice`:

```spice
V4 a4 0 dc 0 ac 1
X4 a4 0 sky130_fd_pr__cap_mim_m3_1 W=10 L=10
```

```spice
.control
ac lin 1 1e6 1e6
let k = 1/(2*pi*1e6)
let c_s10 = abs(i(v4))*k
print c_s10
.endc
```

```
c_s10 = 2.065822e-13
```

That is 206.5822 fF for a 10 × 10 µm MIM plate.

- **`ac lin 1 1e6 1e6`** means one point, at 1 MHz. You don't need a sweep to read one value.
- **`ac 1` on the source is required.** With `dc 0` alone you get zero everywhere, with no
  warning.
- **1 MHz is arbitrary and cancels out.** Any frequency works, as long as the same number
  appears in `k`. Try a decade either side as a sanity check: if the answer moves, your device
  is not a pure capacitor (see [Parasitic capacitance](guide/the-capacitor-you-did-not-draw.md)).

## 3. Inductance: `.ac` and complex arithmetic

An on-chip inductor is a resistor with some inductance attached, so you cannot use the trick
above unchanged; you have to separate the imaginary part from the real one.

From `labs/lab-02-how-big-is-a-picofarad/spice/henry.spice`:

```spice
.control
ac lin 1 1e8 1e8
let l_090_100M = real(imag(v(c))/(2*pi*1e8))
print l_090_100M
.endc
```

```
l_090_100M = 1.520796e-09
```

and at 2.4 GHz, the quality factor as well:

```spice
let q_090_2G4 = real(imag(v(c))/real(v(c)))
let r_090_2G4 = real(real(v(c)))
```

```
q_090_2g4 = 1.086413e+01
r_090_2g4 = 2.157013e+00
```

That is 1.5208 nH, $Q$ = 10.86, and 2.157 Ω of series resistance you did not ask for.

The outer `real(...)` is needed. `imag(v(c))` is still a complex vector as far as ngspice's type
system is concerned, with a zero imaginary part; wrap it in `real()` and you get a number you can
print without a warning.

## 4. Time constant: `.tran` and `meas`

From `labs/lab-03-a-time-constant-in-silicon/spice/rc.spice`:

```spice
Vb bi 0 PULSE(0 1.8 1n 10p 10p 200n 400n)
```

```spice
.tran 2p 80n

.control
run
meas tran t_ideal  WHEN v(bo)=1.137816 RISE=1
.endc
```

1.137816 V is $0.632120 \times 1.8$, so the crossing time is $\tau$ by definition.

**The `.tran` is a card, not a control command, and `run` executes it.** That looks like extra
work until you want the same analysis at another temperature: `set temp` only takes effect on the
next `run`, so a `tran` typed inside `.control` runs immediately and ignores any temperature you
set afterwards. `rc.spice` runs −40 °C and +125 °C from this one card. If you restructure the
deck and your cold and hot numbers come out identical to the 27 °C one, this is why.

That `meas` line has two traps, which together cost 1.005 ns:

- `meas ... when` returns an **absolute time**, not an interval. The pulse starts at
  $t = 1$ ns, so subtract 1 ns.
- The pulse has a **10 ps rise time**, and a first-order system behaves as though the step
  arrived at the ramp's midpoint. Subtract another 5 ps.

The total offset is 1.005 ns, and `src/check_rc.py` subtracts exactly that. Forget it and a
10 ns time constant reads 11.005 ns: 10 % high, and *constant*. That is the clue: an error that
does not scale with the thing you are measuring is an artefact of the measurement, not a property
of the device.

## 5. Variation: corners and Monte Carlo

These are two different questions, with two different mechanisms. Confusing them is the most
common mistake in this half of the course.

### Corners: the whole wafer lot is high or low

One extra word on the `.lib` line picks a section of the model file:

```spice
.lib /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice tt
```

| Section | Means |
|---|---|
| `tt` | typical — the middle of the distribution |
| `ll` | low resistance, low capacitance |
| `hh` | high resistance, high capacitance |

`labs/passives-decks/` builds one deck per corner from `spice/corners.spice.in` and gets:

| | `ll` | `tt` | `hh` |
|---|---:|---:|---:|
| $R_A$, drawn 1 × 10 µm | 3106.637 Ω | 3550.443 Ω | 3994.248 Ω |
| $R_B$, drawn 1 × 40 µm | 11433.66 Ω | 13067.04 Ω | 14700.42 Ω |
| MIM, 10 × 10 µm | 179.7322 fF | 206.5822 fF | 233.8667 fF |
| RC corner frequency | 282.935 MHz | 215.410 MHz | 169.052 MHz |
| **$R_B/R_A$** | **3.680396** | **3.680396** | **3.680396** |
| **divider tap** | **0.3845828 V** | **0.3845828 V** | **0.3845828 V** |

Compare the last two rows with the first four. Absolute values move by ±12.5 % and the corner
frequency by ±31 %, while **the ratio does not move in the seventh decimal place.** That is
[Matching and Pelgrom's law](guide/matching-beats-accuracy.md) in one table, and it is why analog
designers build ratios.

### Mismatch: two devices on the same die differ

Corners move every device together. Mismatch moves them apart, and needs a different switch.

From `labs/lab-04-two-resistors-that-disagree/spice/mismatch.spice`:

```spice
.lib /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.param mc_mm_switch=1
```

```spice
.control
setseed 1
op
* ... measure ...
mc_source
op
* ... measure again: a different imaginary die ...
.endc
```

- **`mc_mm_switch=1`** turns on the per-instance `AGAUSS` term in SkyWater's model cards.
  Without it, every instance of the same device is identical and mismatch is invisible.
- **`mc_source` re-evaluates the netlist**, drawing a fresh sample for every instance. Loop it
  200 times and you have 200 imaginary dies.
- **`setseed 1`** makes the sequence reproducible, which is why your Lab 04 numbers match the
  writeup to the digit.

## Why the decks are slow

Every AD102 deck spends a while doing nothing visible before it prints. It is reading model
cards: `.lib /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice tt` walks a tree of
`.include`s covering every device in SKY130, about 12 MB, nearly all of it MOSFET models a
passive deck never uses.

| `.lib` line | wall clock, `spice/sheet.spice` |
|---|---:|
| `sky130.lib.spice tt` | 55–66 s on the pinned image; about 10 s on the machine this page was last checked on |

Those are wall-clock seconds, so they move with machine load, unlike the resistances, which do
not.

Earlier workbench images also shipped pre-flattened files such as `sky130.lib.spice.tt.red`,
which loaded about thirty times faster. The 2026.08 image does not ship them, so every deck in
this course, including `spice/bode.spice` in Lab 03, now loads `sky130.lib.spice`. If a deck or
a tutorial you find elsewhere names a `.red` file, ngspice on this image stops with
`Could not find library file`. If you are editing a lab's shipped deck, leave the `.lib` line
alone: the reference numbers were taken with it.

## Warnings and delays in each lab

What each lab prints that is not an error, and how long it stays silent. A line that starts with
`Error` is different: it stops the run, and [Error messages](#error-messages) says what it means.

### Lab 01

Every ngspice run loads `.lib /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice tt`, 12 MB
of model cards for every device in SKY130, mostly MOSFETs you are not using, and prints nothing
while it loads. That takes anywhere from about 10 seconds to just over a minute per run,
depending on your machine (the comment at the top of the Makefile records 55–65 s). `make` runs
the simulator twice, so allow up to about two minutes. It is not hung.

`results/sheet.log` holds 170 `unrecognized parameter` lines, in 34 blocks. `make` writes them
to the log; from this deck, your terminal shows only the `---` and `r_` lines. A `rhead_model`
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
coefficients, which ngspice does not implement. ngspice says so and carries on with the
parameters it does understand, which are the ones the lab measures. There are thirty-four blocks
for twenty-two resistors because most of these devices expand into more than one `.model` card.

`make resistor` in `passives-decks` (Lab 01, Part 6) prints fewer of them, because its deck has
fewer resistors: `grep -c 'unrecognized parameter' results/r_head_and_body.log` prints `100`.

A line that starts with `Error` stops the run, and your log will contain no `r_` lines at all;
the checker, `src/check_res.py`, tells you to look for exactly that.

### Lab 02

`pf`, `mine` and `tank` each load SKY130's model cards before printing anything. `henry` does
not: the inductor models live in three small files outside the corner library, so it finishes
almost immediately. The Makefile budgets about three and a half minutes for the whole `make` on
the pinned image. It is not hung.

### Lab 03

Each of the two runs in `make` is silent while ngspice loads 12 MB of SKY130 model cards.

`Doing analysis at TEMP = ... and TNOM = 27.000000` appears five times in `results/rc.log`, at
27 °C, −40 °C and +125 °C. That is Part 4: the deck runs the same `.tran` card at three
temperatures. `TNOM` staying at 27 is correct; it is the temperature the model parameters were
extracted at, not the one you are simulating.

`Warning: command 'plot' is not available during batch simulation, ignored!` comes from the
XSchem part's schematic, which asks for a picture that batch mode cannot draw. The `meas` line
under it is still the answer.

### Lab 04

Each of the two decks loads the SKY130 model cards (about 55 s on the pinned image) and then
evaluates 200 operating points (about 23 s for the bigger of the two), printing nothing while it
works. Most of the time is model loading, not Monte Carlo.

`results/mismatch.log` holds 28,280 `unrecognized parameter (...) - ignored` lines, of which
5,656 are `(sw_et)`. They are the same harmless lines as in Lab 01. Two hundred re-evaluations
of the netlist repeat the whole block two hundred times, so the log is 1.8 MB. `make` sends it
to the log rather than to your terminal.

**The loop counter must exist before the first `mc_source`.** `mc_source` discards the previous
analysis's vectors, and a counter created after an analysis has run goes with them. If you get
this wrong, you see the following, buried in the usual model warnings:

```
Warning from checkvalid: vector run is not available or has zero length.
Error: RHS "run + 1" invalid
```

After that the loop stops at one die and every σ you compute is zero, silently, with exit status
0. That is why `make` prints the operating-point count first: you are looking for 201, and if you
see 2, this is the cause. The shipped decks create the counter immediately after `setseed 1`,
before anything has been simulated:

```
setseed 1
let run = 0          <- here
dowhile run < 200
  mc_source
  ...
```

## `X` lines and `R` lines

Most SKY130 passives are **subcircuits**, so their lines start with `X` and take capital
`W=` / `L=`:

```spice
XR1 a 0 0 sky130_fd_pr__res_high_po W=1 L=10 mult=1
```

A few (`res_generic_nw`, `res_generic_l1`, and all the metal resistors) are bare `.model`
cards, so their lines start with `R` and take lower-case `w=` / `l=`:

```spice
r1 b 0 sky130_fd_pr__res_generic_m1 w=1 l=1
```

Get it backwards and ngspice tells you, with a different message for each direction; both are
in the table below. The catalogue lists [which device takes which](reference/sky130-passive-catalogue.md).

## Units of W and L

In a SKY130 deck, `W`, `L`, `w` and `l` carry **no unit suffix**. `W=1` means one micron. Every
other number on the line takes SI suffixes as usual (`1k`, `0.7p`, `3n`), which is why this
mistake is so easy to make.

On a resistor it gives no error. [Getting started](guide/getting-started.md#the-u-suffix-trap)
goes through it: the same device gives 3550.443 Ω written `W=1 L=10` and 3193.812 Ω written
`W=1u L=10u`, an ordinary-looking answer 10 % away from the right one, with ngspice exiting `0`.

If a resistance is close but not right, look for a stray `u` before you look anywhere else.

## Error messages

| ngspice says | You did |
|---|---|
| `Warning: r.xb.rbody: resistance too low or not given, set to 1 mOhm` | put a `u` on `W`/`L` of a resistor. **The run continues and the answer is wrong.** This is the quiet version of the trap. |
| `could not find a valid modelname` … `Simulation interrupted due to error!` | put a `u` on `W`/`L` of a *transistor*, or asked for a size no model bin covers. This is the loud version, and it is the good outcome. |
| `Error: unknown subckt: xr6 f 0 sky130_fd_pr__res_generic_l1 w=1 l=1` | started the line with `X` for a device that is a plain `.model`. Use `r6 f 0 …`. |
| `Too many parameters for subcircuit type "sky130_fd_pr__res_generic_po" (instance: xxr1)` | passed `mult=1` to a device whose subcircuit has no `mult`. Not every resistor takes the same parameters. |
| `Too few parameters for subcircuit type "sky130_fd_pr__cap_var_lvt" (instance: xxcv)` | gave the wrong number of *nodes*. The varactor has three terminals, not two. |
| `Error: no such vector as -i(vds).` | put an expression where `meas` wanted a vector. `let id = -i(Vds)` first. |
| `Error: incomplete or empty netlist` / `no simulations run!` | nothing on its own. It is the second message; the real error is a few lines above it. |
| `Warning: command 'plot' is not available during batch simulation, ignored!` | asked a batch run for a picture. Harmless: the `meas` lines still ran. Comes up when you netlist a schematic that has `plot` in its control block. |
| ten × `unrecognized parameter (sw_et) - ignored` | nothing. Every deck with a poly resistor in it prints this. See [Getting started](guide/getting-started.md#expected-warnings). |

## Exit codes

| Deck | exit |
|---|---:|
| a correct run | `0` |
| `W=1u` on a transistor — `could not find a valid modelname` | `1` |
| `W=1u` on a **resistor** — silently 10 % wrong | `0` |
| a deck whose `meas` failed | `0` |

`$?` catches a deck that would not build, and nothing else. So every AD102 `Makefile` reads the
log and prints its own `PASS` or `FAIL`, and any script of yours should too.

---

Related: [The SKY130 passive catalogue](reference/sky130-passive-catalogue.md): which devices
exist, which line type each takes, and what each measures.
[AD103's ngspice survival card](https://uoftasic.com/ad103/#/reference/ngspice-errors) covers
the same tool from the transistor side.
