# The SKY130 passive catalogue

**Question this page answers:** *I need a resistor. I need a capacitor. Which ones exist,
what do they cost me in area, and where did those numbers come from?*

This is the page you keep open while designing. Every resistance and capacitance below was
**measured**, in `hpretl/iic-osic-tools:2026.04` with ngspice 46, by instantiating the device
at a stated geometry and dividing — not copied from a datasheet. Every parameter is quoted
with the file it lives in, so you can check any line of this page yourself in one `grep`.

## First, the rule that breaks everyone once

`W` and `L` on a SKY130 device are **plain micron numbers with no unit suffix**. `W=1` is one
micrometre. `W=1u` is not, and it fails. Same for a capacitor's `W`/`L` and a diode's
`area`/`perim`. The full explanation, and the exact error text, is in AD103's
[Reading a SKY130 device model](https://uoftasic.com/ad103/#/reference/sky130-device-guide).

## Resistors

### The catalogue

Thirteen devices in nine rows, spanning **five orders of magnitude** of sheet resistance.
`R measured` is one square — a strip drawn W = 1 µm, L = 1 µm — at 0.1 V:

| Device | What it is physically | $R_\square$ from the PDK | `R` measured, W=1 L=1 |
|---|---|---:|---:|
| `res_xhigh_po` | poly with the ultra-high-resistance implant | 2000 Ω/□ | 2152.022 Ω |
| `res_high_po` | poly with the high-resistance implant | 317.3885 Ω/□ | 695.4646 Ω |
| `res_generic_pd` | p+ diffusion | 197 Ω/□ | 195.4779 Ω |
| `res_generic_nd` | n+ diffusion | 120 Ω/□ | 117.4914 Ω |
| `res_generic_po` | ordinary silicided poly — the gate material | 48.2 Ω/□ | 50.92314 Ω |
| `res_generic_nw` | the n-well itself | 1700 Ω/□ | 1692.556 Ω |
| `res_iso_pw` | isolated p-well | 3816 Ω/□ | 14969.38 Ω at W=2.65 L=10 |
| `res_generic_l1` | local interconnect | 12.2 Ω/□ | 11.97427 Ω |
| `res_generic_m1` … `m5` | metal 1–5 | 0.125 / 0.125 / 0.047 / 0.047 / 0.0285 Ω/□ | 0.1288327 Ω (m1), 0.04770963 Ω (m3) |

The first five and `res_iso_pw` are subcircuits, so they go on `X` lines with `W=` and `L=`
in capitals. `res_generic_nw`, `res_generic_l1` and the metal resistors are bare `.model`
cards, so they go on `R` lines with lower-case `w=` and `l=`:

```spice
XR1 a 0 0 sky130_fd_pr__res_high_po W=1 L=10 mult=1
r1  b 0   sky130_fd_pr__res_generic_m1 w=1 l=1
```

Get that backwards and ngspice says `Error: unknown subckt:` or
`warning, can't find model`. Sources, in the image:

```
/foss/pdks/sky130A/libs.tech/ngspice/r+c/res_typical__cap_typical.spice
        rp1=48.2  rdn=120  rdp=197  rnw=1700  rl1=12.2
        rm1=0.125  rm2=0.125  rm3=0.047  rm4=0.047  rm5=0.0285
        rspwres=3816
/foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_high_po.model.spice
        rsheet = 317.3885     rhead_ps = 345.8312
/foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_xhigh_po.model.spice
        rsheet = 2000.0
```

Magic's extraction technology file
`/foss/pdks/sky130A/libs.tech/magic/sky130A.tech` carries its own copy in milliohms per
square — `xhrpoly 319800`, `uhrpoly 2000000`, `mrp1 48200` — and it does not agree with the
ngspice file everywhere. [Ohms per square](guide/ohms-per-square.md) explains which one to
believe when.

### Why one square of `res_high_po` is 695 Ω and not 317 Ω

Because a real resistor has to be contacted. The device is a strip of resistive poly with a
**fat head** at each end holding a row of contacts, and the head is not free. Increase the
length by 10 µm and watch what the *body* costs:

| Device | R at L = 1 | R at L = 11 | slope (Ω per µm of L) |
|---|---:|---:|---:|
| `res_high_po`, W=1 | 695.4646 Ω | 3867.662 Ω | **317.2198** |
| `res_xhigh_po`, W=1 | 2152.022 Ω | — | — |

317.2198 Ω per micron of length, at W = 1 µm, against `rsheet = 317.3885` on the model card —
**0.05 % apart**. The body is exactly the sheet resistance you were promised. The other
$695.4646 - 317.2198 = 378.24\ \Omega$ is the two contact heads, and it does not shrink when
you shorten the resistor. A one-square `res_high_po` is more head than resistor.

Design consequence: **never draw a short precision resistor.** The head is 378 Ω whatever you
do, so at one square it is 54 % of the value, at five squares 19 %, at ten squares 11 %. Below
about five squares a serious fraction of your resistor is contact resistance, which matches
far worse than sheet resistance does.

### The fixed-width precision family

`res_high_po` and `res_xhigh_po` also ship as five pre-characterised widths each. These are
the ones a layout tool will actually give you, because the contact head geometry is fixed:

| Width (µm) | `res_high_po_*` Ω/µm of length | `res_xhigh_po_*` Ω/µm of length |
|---:|---:|---:|
| 0.35 | 1085.483 | 5713.715 |
| 0.69 | 472.111 | 2898.261 |
| 1.41 | 219.662 | 1418.298 |
| 2.85 | 105.534 | 701.684 |
| 5.73 | 56.460 | 349.005 |

Each figure is `(R at L=11 − R at L=1) / 10` from a measured pair, so the contact heads are
already subtracted out.

**Multiply the `xhigh` column by its width and you get 1999.80 Ω/□ at every one of the five**
— $0.35 \times 5713.715 = 1999.80$, $5.73 \times 349.005 = 1999.80$ — against `rsheet = 2000.0`
in the model file. One material, one number, five widths.

Do the same on the `high` column and you get 379.9, 325.8, 309.7, 300.8, 323.5 Ω/□. **These
are not one number.** The narrow-width flavours are separately fitted devices, and a 0.35 µm
strip behaves like a 380 Ω/□ material, not a 317 Ω/□ one. If you scale a design from one
width to another, re-simulate; do not scale by hand.

### What 10 kΩ costs, measured four ways

Same target, four flavours, each length tuned until the simulator agrees:

| Device | W (µm) | L (µm) | R measured | **area** |
|---|---:|---:|---:|---:|
| `res_xhigh_po_0p35` | 0.35 | 1.647 | 9998.007 Ω | **0.576 µm²** |
| `res_high_po_0p35` | 0.35 | 8.351 | 10000.90 Ω | **2.923 µm²** |
| `res_generic_nd` | 1 | 85.1 | 9998.521 Ω | **85.1 µm²** |
| `res_generic_po` | 1 | 196.4 | 10001.30 Ω | **196.4 µm²** |

**A factor of 341 in area for the same 10 kΩ.** This is the whole argument for having a
high-resistance implant in the process: without it, a modest bias resistor is bigger than a
logic gate.

For scale, from `/foss/pdks/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef`:

```
MACRO sky130_fd_sc_hd__inv_1
  SIZE 1.380 BY 2.720 ;
```

3.7536 µm² for the smallest inverter in the standard-cell library. So the 10 kΩ
`res_xhigh_po_0p35` is **smaller than one inverter**, and the `res_generic_po` version is
**fifty-two of them**. Scale that to 100 kΩ in poly — 1964 µm², about 520 inverters — and the
resistor is bigger than the circuit it biases. Picking the flavour is a design decision, not
a detail.

## Capacitors

### The catalogue

All measured with a 1 V AC source at 1 kHz, $C = |I| / (2\pi f V)$ with $V = 1$ V:

| Device | Geometry | C measured | density |
|---|---|---:|---:|
| `cap_mim_m3_1` | 2 × 2 µm | 9.302250 fF | 2.326 fF/µm² |
| `cap_mim_m3_1` | 10 × 10 µm | 206.5822 fF | 2.066 fF/µm² |
| `cap_mim_m3_1` | 22.2 × 22.2 µm | 1000.314 fF | 2.030 fF/µm² |
| `cap_mim_m3_2` | 10 × 10 µm | 206.5822 fF | 2.066 fF/µm² |
| `cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5` | 11.5 × 11.7 µm (fixed) | 147.3400 fF | 1.095 fF/µm² |
| `nfet_01v8` as a MOS cap, gate at 1.8 V | 10 × 10 µm gate | 787.6883 fF | 7.877 fF/µm² |
| the **same** device, gate at 0 V | 10 × 10 µm gate | 220.7182 fF | 2.207 fF/µm² |
| `cap_var_lvt` at 1.8 V | 10 × 10 µm | 817.8665 fF | 8.179 fF/µm² |
| the **same** varactor at 0 V | 10 × 10 µm | 99.51349 fF | 0.995 fF/µm² |

Four things to take from that table.

**1. `m3_1` and `m3_2` are the same capacitor on different metals.** `cap_mim_m3_1` sits
between met3 and the `capm` plate; `cap_mim_m3_2` between met4 and `cap2m`. Identical
capacitance to seven digits — the choice is about what you need to route underneath.

**2. MIM density rises as the plate shrinks**, because the perimeter term is fixed per micron
of edge and edge/area grows. 2.326 fF/µm² at 2 × 2, 2.030 at 22.2 × 22.2.

**3. A MOS capacitor is 3.8× denser than a MIM, and it is not a capacitor.** 787.6883 fF at
1.8 V and 220.7182 fF at 0 V — **the same physical device, a factor of 3.57 apart.** Use it
for supply decoupling, where one plate is always at the rail; never in a filter whose corner
frequency you care about.

**4. The varactor is that nonlinearity on purpose.** 99.5 fF to 817.9 fF, a **factor of 8.22**
over the supply range. That is the tuning element in an oscillator.

### The arithmetic behind the MIM, closing exactly

The model is three lines of file, at
`/foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__cap_mim_m3_1.model.spice`:

```spice
.param wc = 'w+m3_dw*1e6+tol_m3*1e6'
.param carea  = 'camimc*(wc)*(lc)'
.param cperim = 'cpmimc*((wc)+(lc))*2'
```

(`lc` is defined the same way as `wc`, on the line immediately after it.)

and three constants, at
`/foss/pdks/sky130A/libs.tech/ngspice/r+c/res_typical__cap_typical__lin.spice` and
`.../sky130_fd_pr__model__r+c.model.spice`:

```
+ camimc=  2.00e-15  ; Units: farad/micrometer^2
+ cpmimc = 0.19e-15 ; Units: farad/micrometer
+ m3_dw = -0.025u
```

So for a plate you drew 10 µm square, the metal etches back 0.025 µm and the real plate is
9.975 µm:

$$2.00 \times 9.975^2 \;+\; 0.19 \times 2 \times (9.975 + 9.975) = 199.00125 + 7.581 = \boxed{206.582\ \text{fF}}$$

ngspice measured `2.065822e-13`. **Six significant figures, from three constants and a
subtraction.** When a PDK number and your arithmetic agree like that, you have understood
the device.

### What 1 pF costs

| Device | Area for 1 pF | Caveat |
|---|---:|---|
| MOS cap at 1.8 V | 127 µm² | only if one plate stays at a rail |
| MIM | **493 µm²** — 22.2 × 22.2 µm, measured at 1000.314 fF | the honest answer |
| VPP fringe | 913 µm² | but it lives *under* your MIM, so it can be free |

493 µm² is about 130 inverters. This is the number that ends every "just put a 1 nF cap on
it" conversation: a nanofarad is half a square millimetre, which is most of a small chip.
[What a picofarad costs](guide/what-a-picofarad-costs.md) is the long version.

### The capacitors you did not draw

Every layer has capacitance to the substrate whether you asked for one or not. From Magic's
`defaultareacap` lines in `/foss/pdks/sky130A/libs.tech/magic/sky130A.tech`, in aF/µm²:

| Layer to substrate | aF/µm² | as fF/µm² |
|---|---:|---:|
| poly | 106.13 | 0.106 |
| local interconnect (li) | 36.99 | 0.037 |
| met1 | 25.78 | 0.026 |
| met2 | 17.5 | 0.018 |
| met3 | 12.37 | 0.012 |
| met4 | 8.42 | 0.008 |
| met5 | 6.32 | 0.006 |
| n-well / deep n-well | 120 | 0.120 |

A 100 µm × 1 µm met1 wire carries 2.6 fF to ground for free. That is more than a quarter of
the 10 fF you may have deliberately drawn elsewhere.
[The capacitor you did not draw](guide/the-capacitor-you-did-not-draw.md) is the page for
this.

## The one you cannot have

There is no good inductor. SKY130 ships three spiral models
(`sky130_fd_pr__ind_03_90`, `ind_05_125`, `ind_05_220`). `ind_05_220` is 9.92 nH, occupies
tens of thousands of µm², and has **Q = 0.0000150516 at 1 kHz**; the best Q any of the three
ever reaches is **21.1, at 6.38 GHz**, and above 3.52777 GHz `ind_05_220`'s reactance changes
sign entirely. [The inductor problem](guide/the-inductor-problem.md) and
[What analog builds instead](guide/what-analog-builds-instead.md) cover why, and what
replaces it.

## Corners

`tt` is the transistor corner. Passives have their own, selected by the second word on the
`.lib` line: `ll` (low resistance, low capacitance) and `hh` (high, high), plus `hl` and `lh`.

Measured, not read off a parameter file — the same four devices simulated three times with
only the corner name changed:

| Device | `ll` | `tt` | `hh` | spread about `tt` |
|---|---:|---:|---:|---:|
| `res_high_po` W=1 L=10 | 3106.637 Ω | 3550.443 Ω | 3994.248 Ω | **±12.5 %** |
| `res_xhigh_po` W=1 L=10 | 18037.95 Ω | 21221.12 Ω | 24404.29 Ω | **±15.0 %** |
| `res_generic_po` W=1 L=10 | 451.1426 Ω | 509.2314 Ω | 583.1667 Ω | −11.4 % / +14.5 % |
| `cap_mim_m3_1` 10 × 10 | 179.7322 fF | 206.5822 fF | 233.8667 fF | −13.0 % / +13.2 % |

The parameters behind those runs, if you want to see where the numbers come from —
`/foss/pdks/sky130A/libs.tech/ngspice/r+c/res_low__cap_low.spice`,
`res_typical__cap_typical.spice`, `res_high__cap_high.spice` and their `__lin` siblings:

| Parameter | `ll` | `tt` | `hh` |
|---|---:|---:|---:|
| `rp1` — ordinary poly | 44 | 48.2 | 53.52 |
| `rdn` — n+ diffusion | 111.6 | 120 | 128.4 |
| `rdp` — p+ diffusion | 175.3 | 197 | 218.7 |
| `rl1` — local interconnect | 10.31 | 12.2 | 14.02 |
| `rm1` — metal 1 | 0.111 | 0.125 | 0.139 |
| `rnw` — n-well | 1378 | 1700 | 2022 |
| `sky130_fd_pr__res_high_po__var` | −0.125 | 0.0 | +0.125 |
| `camimc` — MIM | 1.778e-15 | 2.00e-15 | 2.231e-15 |

Note that the device does not always move by exactly the parameter's percentage: `rp1` shifts
−8.7 % / +11.0 %, but a real `res_generic_po` moves −11.4 % / +14.5 %, because the corner also
changes the etch bias that sets the strip's effective width. **Simulate the corner; do not
scale the typical answer by hand.**

**Every absolute value on this page moves by roughly ±10 % between corners.** A *ratio* of
two of the same device does not, and that is the entire reason analog design is built on
ratios — [Matching beats accuracy](guide/matching-beats-accuracy.md).

## Re-run everything on this page

```bash
cd labs/passives-decks
make
```

No environment setup: every deck names the model library by absolute path, so a bare
container works. Related labs:
[Lab 01 — A resistor you designed](labs/lab-01-a-resistor-you-designed-overview.md),
[Lab 02 — How big is a picofarad?](labs/lab-02-how-big-is-a-picofarad-overview.md),
[Lab 04 — Two resistors that disagree](labs/lab-04-two-resistors-that-disagree-overview.md).
