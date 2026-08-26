# `passives-decks` — the ngspice decks behind the AD102 guide pages

This is **not a lab.** It is the measurement rig for
[Movements I–IV of the guide](https://uoftasic.com/ad102/#/guide/a-resistor-you-cannot-buy).
Every number printed on those pages came out of this directory, and `make` proves
it on your machine.

The labs are next door: [`lab-01-a-resistor-you-designed/`](../lab-01-a-resistor-you-designed/)
and its siblings are where you design something. Here you only re-run what the guide
claims.

## Run it

Inside the workbench `hpretl/iic-osic-tools:2026.04` — ngspice **46**, PDK
**sky130A** at `/foss/pdks/sky130A`:

```bash
cd labs/passives-decks
make
```

No environment setup. No `.designinit`, no `PDK` variable, no `mod`. Every deck
names the model library by absolute path, so a bare container works.

```
make            run all seven decks, then check every number
make check      re-render the verdict from logs already on disk
make catalogue  the extra devices the passive catalogue tabulates
make figures    regenerate the three PNGs the guide pages embed
make clean      delete results/, keep sources
```

`catalogue` is not part of `make`, because nothing in the guide depends on it. It
is there so that every number on
[The SKY130 passive catalogue](https://uoftasic.com/ad102/#/reference/sky130-passive-catalogue)
has a deck you can run.

**Budget about eight minutes, most of it silent.** Each ngspice run spends roughly
60 seconds reading 12 MB of SKY130 model cards before it prints anything. It is not
hung.

## What each deck answers

| File | Guide page | What it measures |
|---|---|---|
| `spice/r_head_and_body.spice` | [Ohms per square](https://uoftasic.com/ad102/#/guide/ohms-per-square) | Splits one resistor into its contact head and its body. Sizes 1 k / 10 k / 100 k. Builds the same 100 k at five widths. |
| `spice/c_area.spice` | [A capacitor is a sandwich](https://uoftasic.com/ad102/#/guide/a-capacitor-is-a-sandwich) | MIM vs VPP vs MOS, farads per square micron. |
| `spice/c_moscap_cv.spice` | same | 19 copies of one MOS cap at 19 gate voltages. |
| `spice/l_spiral.spice` | [The inductor problem](https://uoftasic.com/ad102/#/guide/the-inductor-problem) | L, Q and self-resonance of the three SKY130 spirals. |
| `spice/corners.spice.in` | [The value you drew…](https://uoftasic.com/ad102/#/guide/the-value-you-drew-is-not-what-you-get) | One circuit, three process corners. `make` writes `corners_tt/ll/hh.spice` from it — **edit the `.in`, not the generated files.** |
| `spice/mismatch.spice` | [Matching beats accuracy](https://uoftasic.com/ad102/#/guide/matching-beats-accuracy) | 200 Monte Carlo wafers, seed pinned, four resistors. |
| `spice/catalogue.spice` | [The SKY130 passive catalogue](https://uoftasic.com/ad102/#/reference/sky130-passive-catalogue) | The devices no other deck here builds: seven resistor materials at one square, both fixed-width precision families, 10 kΩ four ways, and the MIM/varactor rows. Run it with `make catalogue`. |
| `src/check_passives.py` | — | The verdict. 39 golden values plus six Monte Carlo standard deviations. |
| `src/plot_figures.py` | — | Writes the three PNGs into `docs/assets/img/`. |

## Reading the output

Two things you will see that are **not** bugs:

**A wall of `unrecognized parameter` warnings.** Blocks of

```
Warning: Model issue on line 4841 :
  .model xa:rbody_model r sw_et=0 isnoisy=0 rsh=    3.173885000000000e+02  ...
unrecognized parameter (sw_et) - ignored
unrecognized parameter (isnoisy) - ignored
unrecognized parameter (p2) - ignored
```

with these exact counts, which you can confirm with
`grep -c 'unrecognized parameter' results/<file>.log`:

| log | lines |
|---|---:|
| `r_head_and_body.log` | 100 |
| `corners_tt.log`, `_ll`, `_hh` | 50 each |
| `mismatch.log` | **8080** |
| `c_area.log`, `c_moscap_cv.log`, `l_spiral.log` | 0 |

`mismatch.log` is the alarming one: it re-parses the netlist 200 times, so the
warnings come back 200 times. Nothing is wrong.

SkyWater writes one model card for several simulators. `sw_et`, `isnoisy`, `p2`,
`q2`, `p3` and `q3` are Spectre-flavoured keywords for self-heating, noise and the
voltage coefficients. ngspice does not implement them, says so, and uses the rest.
An **`Error`** at the start of a line is a different matter — that one is real.

**`IKR too small - model effect disabled!`** Twice, from the parasitic diodes that
model a diffusion resistor's junction to its well. Also harmless: a knee-current
parameter is below the value ngspice will act on, so it skips that term.

## Why the numbers are golden

DC operating points and linear AC analyses have no randomness in them, and
`mismatch.spice` sets `setseed 12345` before its first `reset`, so the Monte Carlo
is reproducible too. Every value in `src/check_passives.py` is compared at **0.05 %**
tolerance and every one of them passes on the pinned image.

If a check fails, the model library has moved — not you. Confirm `ngspice -v`
reports 46 and that `/foss/pdks/sky130A` exists.

## The trap

`W` and `L` on a SKY130 device are **plain micron numbers with no unit suffix**.
`W=1` is one micrometre; `W=1u` is a millionth of that, which is outside every bin
the model was fitted over. On a MOSFET that stops the run with
`could not find a valid modelname`; on a resistor it does not stop at all -- the
same strip reads 3550.443 ohm written `W=1 L=10` and 3193.812 ohm written
`W=1u L=10u`, 10 % off with exit status 0. There is no `u` in any deck here.

One more, specific to `l_spiral.spice`: the three inductor models are **not** part of
`sky130.lib.spice`. They are `.include`d explicitly at the top of the deck. Leave one
out and you get

```
Error: unknown subckt: x1 a 0 ct 0 sky130_fd_pr__ind_05_220
```

## Reference figures produced here

- `docs/assets/img/ad102-moscap-cv.png` — MOS capacitance vs gate voltage
- `docs/assets/img/ad102-spiral-q.png` — Q vs frequency, three spirals
- `docs/assets/img/ad102-mismatch.png` — 200-wafer mismatch histograms

Two more figures in the guide are KLayout renders of
`libs.ref/sky130_fd_pr/gds/sky130_fd_pr.gds` rather than plots
(`ad102-spiral-inductor.png`, `ad102-spiral-vs-inverters.png`); they are checked in
and do not need regenerating.

Questions: <https://discord.gg/hrJnP5UsGz>
