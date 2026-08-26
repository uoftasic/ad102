# ngspice decks that actually run

**Question this page answers:** *I want to measure a passive device myself. What is the
smallest deck that does it, and what will ngspice say when I get it wrong?*

AD102 asks five questions of silicon — *how many ohms, how many farads, how many henries, how
long is the time constant, and how much does all of that move?* — and each one has a deck
shape you can memorise. This page is those five shapes, with the exact output each produced in
`hpretl/iic-osic-tools:2026.04`, ngspice **46**, PDK **sky130A**.

Every block below is an **excerpt** from a deck that ships in a lab package, and the path is
named beside it. Nothing here is a file for you to create; run the shipped one and edit that.

## Every deck has the same five parts

In this order, and ngspice does not care about the order except that `.end` is last:

| Part | Looks like | Notes |
|---|---|---|
| 1. title | `* AD102 Lab 01 -- the sheet resistance deck` | **The first line is always a comment**, whatever you put in it. Put a real title there; ngspice will eat a device line that lands in position 1. |
| 2. models | `.lib /foss/pdks/.../sky130.lib.spice tt` | absolute path, so the deck runs anywhere |
| 3. devices and sources | `Xa a 0 0 sky130_fd_pr__res_high_po W=1 L=10` | see [the catalogue](reference/sky130-passive-catalogue.md) |
| 4. what to do | `.control` … `.endc`, or `.op` / `.ac` / `.tran` cards | |
| 5. `.end` | `.end` | |

Run it in batch — run, print, exit:

```bash
ngspice -b spice/sheet.spice
```

Without `-b` you land in an interactive prompt, the terminal looks hung, and you are one
`quit` away from your results.

## 1. How many ohms? — `.op` and Ohm's law

There is no `measure the resistance` command. You push a current you chose through the device
and divide the voltage you got by it.

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

**695.4646 Ω** for one drawn square of a device whose model card says 317.3885 Ω/□ — the whole
subject of [Ohms per square](guide/ohms-per-square.md).

Three things about that idiom:

- **1 µA is a deliberate choice.** Small enough that the resistor's own self-heating and
  voltage coefficient do not move the answer, large enough to be far from numerical noise.
  Push 1 mA through a 100 kΩ and you are asking a different question.
- **`let` before `print`.** `v(l1)/1u` is an *expression*; `r_L1` is a vector. `print` will
  take either, but `meas` will not, and the habit costs nothing.
- **Vector names come back lower-case.** You wrote `r_L1`, ngspice prints `r_l1`. That is not
  a typo in your deck and it matters when you `grep` the log.

If you drive with a voltage source instead, the current comes out of the source and it is
negative, so it is `1m/(-i(va))` — as in
`labs/passives-decks/spice/corners.spice.in`:

```spice
let R_A = 1m/(-i(va))
```

## 2. How many farads? — one `.ac` point

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

**206.5822 fF** for a 10 × 10 µm MIM plate.

- **`ac lin 1 1e6 1e6`** is "one point, at 1 MHz". You do not need a sweep to read one value.
- **`ac 1` on the source is not optional.** `dc 0` alone gives you a silent zero everywhere and
  a capacitance of exactly nothing.
- **1 MHz is arbitrary and it cancels.** Any frequency works, as long as the same number
  appears in `k`. Use a decade either side as a sanity check: if the answer moves, your device
  is not a pure capacitor, which is the entire point of
  [The capacitor you did not draw](guide/the-capacitor-you-did-not-draw.md).

## 3. How many henries? — `.ac`, and complex arithmetic

An on-chip inductor is a resistor with some inductance attached, so you cannot use the trick
above unmodified — you have to separate the imaginary part from the real one.

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

**1.5208 nH, $Q$ = 10.86, and 2.157 Ω of series resistance you did not ask for.**

The outer `real(...)` is not redundant. `imag(v(c))` is still a complex vector as far as
ngspice's type system is concerned, with a zero imaginary part; wrap it in `real()` and you get
a number you can print without a warning.

## 4. How long is the time constant? — `.tran` and `meas`

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

1.137816 V is $0.632120 \times 1.8$, so the crossing time *is* $\tau$ — by definition, not by
approximation.

**The `.tran` is a card, not a control command, and `run` executes it.** That looks like extra
ceremony until you want the same analysis at another temperature: `set temp` only takes effect
on the next `run`, so a `tran` typed inside `.control` runs immediately and ignores any
temperature you set afterwards. `rc.spice` sweeps −40 °C and +125 °C off this one card.

**Two traps live in that one line, and both cost the same 1.005 ns.**

- `meas ... when` returns an **absolute time**, not an interval. The pulse starts at
  $t = 1$ ns, so subtract 1 ns.
- The pulse has a **10 ps rise time**, and a first-order system behaves as though the step
  arrived at the ramp's midpoint. Subtract another 5 ps.

Total offset **1.005 ns**, and `src/check_rc.py` subtracts exactly that. Forget it and a 10 ns
time constant reads 11.005 ns — 10 % high, and *constant*, which is the clue: an error that
does not scale with the thing you are measuring is an artefact of the measurement, not a
property of the device.

## 5. How much does it move? — corners and Monte Carlo

These are two different questions and they take two different mechanisms. Confusing them is the
most common thing to get wrong in this half of the course.

### Corners — the whole wafer lot is high or low

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

Read the last two rows against the first four. Absolute values move by ±12.5 %, the corner
frequency by ±31 %, and **the ratio does not move in the seventh decimal place.** That is
[Matching beats accuracy](guide/matching-beats-accuracy.md) in one table, and it is why analog
designers build ratios.

### Mismatch — two devices on *the same* die differ

Corners move every device together. Mismatch moves them apart, and it takes a different switch.

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
  Without it every instance of the same device is byte-identical and mismatch is invisible.
- **`mc_source` re-evaluates the netlist**, drawing a fresh sample for every instance. Loop it
  200 times and you have 200 imaginary dies.
- **`setseed 1`** makes the sequence reproducible, which is why your Lab 04 numbers match the
  writeup to the digit rather than being "about right".

## Why your labs are slow, and when you are allowed to fix it

Every AD102 deck spends about a minute doing nothing visible before it prints. It is reading
model cards, and there are two files it could read:

| `.lib` line | wall clock, `spice/sheet.spice` |
|---|---:|
| `sky130.lib.spice tt` | **55–66 s** |
| `sky130.lib.spice.tt.red tt` | **2.1 s** |

Those are wall-clock seconds on one machine, so they move with load — unlike the resistances,
which do not. The ratio is the durable part: **about thirty times faster**, with **identical
output to the last digit**. The `.red` file is the same tree of `.include`s already flattened
into one file, so ngspice opens one 12 MB file instead of walking hundreds.

**AD102's decks deliberately use the slow one anyway, and you should understand why before you
change it.**

- **The `.red` files only exist for the transistor corners** — `tt`, `ff`, `ss`, `fs`, `sf`.
  There is no `sky130.lib.spice.ll.red`, so the corner decks in `labs/passives-decks/` cannot
  use them at all.
- **The Monte Carlo numbers come out different.** Run `mismatch.spice`'s statistics against
  `.tt.red` and the samples do not match the ones in the writeup. Lab 04's whole point is that
  your numbers reproduce, so it stays on the file the numbers were taken from.

So: if you are writing your own deck, with no corners and no `mc_source` in it, use
`sky130.lib.spice.tt.red tt` and get your afternoon back. If you are editing a lab's shipped
deck, leave the `.lib` line alone. [AD103](https://uoftasic.com/ad103/) uses the fast file
throughout, which is why its labs finish in seconds.

## `X` lines and `R` lines are not interchangeable

Most SKY130 passives are **subcircuits**, so they start with `X` and take capital `W=` / `L=`:

```spice
XR1 a 0 0 sky130_fd_pr__res_high_po W=1 L=10 mult=1
```

A few — `res_generic_nw`, `res_generic_l1`, and all the metal resistors — are bare `.model`
cards, so they start with `R` and take lower-case `w=` / `l=`:

```spice
r1 b 0 sky130_fd_pr__res_generic_m1 w=1 l=1
```

Get it backwards and ngspice tells you, in two different ways depending on which way you got it
backwards. Both are in the table below. The full list of which is which is in
[the catalogue](reference/sky130-passive-catalogue.md).

## The one that costs an afternoon: `W=1`, never `W=1u`

In a SKY130 deck, `W`, `L`, `w` and `l` carry **no unit suffix**. `W=1` *means* one micron.
Every other number on the line takes SI suffixes as usual — `1k`, `0.7p`, `3n` — which is
exactly why this trap works.

**On a resistor it does not announce itself.** [Getting
started](guide/getting-started.md#5-the-trap-that-will-cost-you-an-afternoon-u) has the full
autopsy: the same device gives **3550.443 Ω** written `W=1 L=10` and **3193.812 Ω** written
`W=1u L=10u` — a perfectly ordinary-looking answer 10 % away from the right one, with
`ngspice` exiting `0`.

**Reflex check:** if a resistance is close-but-not-right, look for a stray `u` before you look
anywhere else.

## Error messages, with the exact text

| ngspice says | You did |
|---|---|
| `Warning: r.xb.rbody: resistance too low or not given, set to 1 mOhm` | put a `u` on `W`/`L` of a resistor. **The run continues and the answer is wrong.** This is the quiet version of the trap. |
| `could not find a valid modelname` … `Simulation interrupted due to error!` | put a `u` on `W`/`L` of a *transistor*, or asked for a size no model bin covers. This is the loud version, and it is the good outcome. |
| `Error: unknown subckt: xr6 f 0 sky130_fd_pr__res_generic_l1 w=1 l=1` | started the line with `X` for a device that is a plain `.model`. Use `r6 f 0 …`. |
| `Too many parameters for subcircuit type "sky130_fd_pr__res_generic_po" (instance: xxr1)` | passed `mult=1` to a device whose subcircuit has no `mult`. Not every resistor takes the same parameters. |
| `Too few parameters for subcircuit type "sky130_fd_pr__cap_var_lvt" (instance: xxcv)` | gave the wrong number of *nodes*. The varactor has three terminals, not two. |
| `Error: no such vector as -i(vds).` | put an expression where `meas` wanted a vector. `let id = -i(Vds)` first. |
| `Error: incomplete or empty netlist` / `no simulations run!` | nothing on its own. It is the second message; the real error is a few lines above it. |
| `Warning: command 'plot' is not available during batch simulation, ignored!` | asked a batch run for a picture. Harmless — the `meas` lines still ran. Comes up when you netlist a schematic that has `plot` in its control block. |
| ten × `unrecognized parameter (sw_et) - ignored` | nothing. Every deck with a poly resistor in it prints this. See [Getting started](guide/getting-started.md). |

## Exit codes lie, so read the log

| Deck | exit |
|---|---:|
| a correct run | `0` |
| `W=1u` on a transistor — `could not find a valid modelname` | `1` |
| `W=1u` on a **resistor** — silently 10 % wrong | `0` |
| a deck whose `meas` failed | `0` |

`$?` catches a deck that would not build, and catches nothing else. Every AD102 `Makefile`
therefore reads the log and prints its own `PASS` or `FAIL`, and so should any script of yours.

---

Related: [The SKY130 passive catalogue](reference/sky130-passive-catalogue.md) — which device
exists, which line type it takes, and what it measures at.
[AD103's ngspice survival card](https://uoftasic.com/ad103/#/reference/ngspice-errors) covers
the same tool from the transistor side.
