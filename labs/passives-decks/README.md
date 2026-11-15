# `passives-decks`: the ngspice decks behind the AD102 guide pages

This package is not a lab. It holds the decks whose output the guide pages quote, starting at
[Resistors on a chip](https://uoftasic.com/ad102/guide/a-resistor-you-cannot-buy.html), and `make`
checks every one of those numbers on your machine. The labs run its targets in specific parts:

| Target | Run in |
|---|---|
| `make resistor` | [Lab 01, Part 6](https://uoftasic.com/ad102/labs/lab-01-a-resistor-you-designed-overview.html) |
| `make capacitor` | [Lab 02, Part 5](https://uoftasic.com/ad102/labs/lab-02-how-big-is-a-picofarad-overview.html) |
| `make inductor` | [Lab 02, Part 7](https://uoftasic.com/ad102/labs/lab-02-how-big-is-a-picofarad-overview.html) |
| `make corners` | [Lab 04, Part 1](https://uoftasic.com/ad102/labs/lab-04-two-resistors-that-disagree-overview.html) |
| `make mismatch` | [Lab 04, Going further](https://uoftasic.com/ad102/labs/lab-04-two-resistors-that-disagree-overview.html) (optional) |

## Run it

Inside the workbench `hpretl/iic-osic-tools:2026.08` (ngspice-47, PDK `sky130A` at
`/foss/pdks/sky130A`):

```bash
cd labs/passives-decks
make
```

No environment setup is needed: no `.designinit`, no `PDK` variable, no `mod`. Every deck names
the model library by absolute path, so a bare container works.

Budget about eight minutes for a full `make`, most of it silent. Each ngspice run spends roughly
60 seconds reading 12 MB of SKY130 model cards before it prints anything. It is not hung.

## Targets

| Target | What it does |
|---|---|
| `make` | `resistor`, `capacitor`, `inductor`, `corners`, `mismatch`, then `check` |
| `make resistor` | head and body of one resistor; 1 k / 10 k / 100 k sized; one strip, four implants; 100 k at four widths |
| `make capacitor` | MIM vs VPP vs MOS, then the MOS C–V sweep |
| `make inductor` | L, Q and self-resonance of the three SKY130 spirals |
| `make corners` | one circuit at the `tt`, `ll` and `hh` corners |
| `make mismatch` | 200 Monte Carlo wafers, seed pinned, four resistors |
| `make check` | re-render the verdict from logs already on disk |
| `make catalogue` | the extra devices [The SKY130 passive catalogue](https://uoftasic.com/ad102/reference/sky130-passive-catalogue.html) tabulates (not part of `make`) |
| `make figures` | regenerate the three PNGs the guide pages embed |
| `make clean` | delete the logs in `results/` and the generated corner decks, keep sources |

## Files

| File | Guide page | What it measures |
|---|---|---|
| `spice/r_head_and_body.spice` | [Ohms per square](https://uoftasic.com/ad102/guide/ohms-per-square.html) | Splits one resistor into its contact head and its body. Sizes 1 k / 10 k / 100 k. Builds the same 100 k at four widths. |
| `spice/c_area.spice` | [Capacitors on a chip](https://uoftasic.com/ad102/guide/a-capacitor-is-a-sandwich.html) | MIM vs VPP vs MOS, farads per square micron. |
| `spice/c_moscap_cv.spice` | same | 19 copies of one MOS capacitor at 19 gate voltages. |
| `spice/l_spiral.spice` | [Inductors on a chip](https://uoftasic.com/ad102/guide/the-inductor-problem.html) | L, Q and self-resonance of the three SKY130 spirals. |
| `spice/corners.spice.in` | [Process corners](https://uoftasic.com/ad102/guide/the-value-you-drew-is-not-what-you-get.html) | One circuit, three process corners. `make` writes `corners_tt/ll/hh.spice` from it, so **edit the `.in`, not the generated files.** |
| `spice/mismatch.spice` | [Matching and Pelgrom's law](https://uoftasic.com/ad102/guide/matching-beats-accuracy.html) | 200 Monte Carlo wafers, seed pinned, four resistors. |
| `spice/catalogue.spice` | [The SKY130 passive catalogue](https://uoftasic.com/ad102/reference/sky130-passive-catalogue.html) | The devices no other deck here builds: seven resistor materials at one square, both fixed-width precision families, 10 kΩ four ways, and the MIM/varactor rows. |
| `src/check_passives.py` | — | The verdict: 39 golden values plus six Monte Carlo standard deviations. |
| `src/plot_figures.py` | — | Writes the three PNGs into `docs/assets/img/`. |

## Expected warnings

Every log with a poly resistor in it has blocks of `unrecognized parameter` warnings, which are
harmless ([Getting started](https://uoftasic.com/ad102/guide/getting-started.html) explains them).
The exact counts, which you can confirm with
`grep -c 'unrecognized parameter' results/<file>.log`:

| log | lines |
|---|---:|
| `r_head_and_body.log` | 100 |
| `corners_tt.log`, `_ll`, `_hh` | 50 each |
| `mismatch.log` | **8080** |
| `c_area.log`, `c_moscap_cv.log`, `l_spiral.log` | 0 |

`mismatch.log` has the most because it re-parses the netlist 200 times, so the warnings come back
200 times. Nothing is wrong. An **`Error`** at the start of a line is different; that one is real.

**`IKR too small - model effect disabled!`** appears twice, from the parasitic diodes that model a
diffusion resistor's junction to its well. It is also harmless: a knee-current parameter is below
the value ngspice will act on, so ngspice skips that term.

The three inductor models are **not** part of `sky130.lib.spice`; `l_spiral.spice` `.include`s
them explicitly at the top. Leave one out and you get
`Error: unknown subckt: x1 a 0 ct 0 sky130_fd_pr__ind_05_220`.

## Reproducible numbers

DC operating points and linear AC analyses have no randomness in them, and `mismatch.spice` sets
`setseed 12345` before its first `reset`, so the Monte Carlo is reproducible too. Every value in
`src/check_passives.py` is compared at 0.05 % tolerance, and all of them pass on the pinned image.
If a check fails, the model library has changed, not your work: confirm `ngspice -v` reports
ngspice-47 and that `/foss/pdks/sky130A` exists.

`W` and `L` on a SKY130 device are plain micron numbers: `W=1`, never `W=1u`. There is no `u` in
any deck here.

## Figures produced here

- `docs/assets/img/ad102-moscap-cv.png`: MOS capacitance vs gate voltage
- `docs/assets/img/ad102-spiral-q.png`: Q vs frequency, three spirals
- `docs/assets/img/ad102-mismatch.png`: 200-wafer mismatch histograms

Two more figures in the guide are KLayout renders of
`libs.ref/sky130_fd_pr/gds/sky130_fd_pr.gds`, not plots (`ad102-spiral-inductor.png`,
`ad102-spiral-vs-inverters.png`). They are checked in and do not need regenerating.

Questions: <https://discord.gg/hrJnP5UsGz>
