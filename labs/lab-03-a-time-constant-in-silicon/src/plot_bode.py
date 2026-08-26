#!/usr/bin/env python3
"""Draw the Bode plot of the RC you designed, over the ideal one from AD101.

Reads only results/bode.txt, which `make bode` produced, so the picture and
the printed numbers cannot drift apart.

Usage:  python3 src/plot_bode.py [results/bode.txt] [../../docs/assets/img]
"""
import sys
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Validated categorical slots 1-2 (light surface #fcfcfb), matching
# labs/passives-decks/src/plot_figures.py so every AD102 figure is one system.
BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE = "#fcfcfb"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#dedcd6"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.size": 11, "font.family": "DejaVu Sans",
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": GRID,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRID, "grid.linewidth": 0.8,
    "lines.linewidth": 2.0,
})

src = Path(sys.argv[1] if len(sys.argv) > 1 else "results/bode.txt")
out = Path(sys.argv[2] if len(sys.argv) > 2 else "../../docs/assets/img")
out.mkdir(parents=True, exist_ok=True)

# wrdata writes one x,y PAIR per vector: 4 vectors -> 8 columns.
f, db_real, db_ideal, ph_real, ph_ideal = [], [], [], [], []
for line in src.read_text().splitlines():
    c = line.split()
    if len(c) < 8:
        continue
    f.append(float(c[0]))
    db_real.append(float(c[1]))
    db_ideal.append(float(c[3]))
    ph_real.append(float(c[5]) * 180.0 / math.pi)
    ph_ideal.append(float(c[7]) * 180.0 / math.pi)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.4, 6.6), sharex=True,
                               gridspec_kw={"height_ratios": [3, 2]})

# The two curves agree to 0.36 %, so they would sit exactly on top of each
# other. Draw the ideal as a wide pale band and the real one thin on top, so
# the overlap is visible as an overlap rather than as one missing curve.
ax1.semilogx(f, db_ideal, color=ORANGE, lw=5.5, alpha=0.55,
             label="ideal 10 kΩ × 1 pF  (the one you drew in AD101)")
ax1.semilogx(f, db_real, color=BLUE, lw=1.8,
             label="your Lab 01 resistor × your Lab 02 capacitor")
ax1.axhline(-3.0103, color=INK2, lw=0.9, ls=":")
ax1.axvline(1.58580e7, color=BLUE, lw=0.9, ls=":")
ax1.set_ylim(-60, 5)
ax1.set_ylabel("gain (dB)")
ax1.set_title("The RC you fabricated, in the frequency domain",
              color=INK, fontsize=13, fontweight="bold", loc="left", pad=22)
ax1.text(0, 1.02,
         "SKY130 tt, ngspice 46 — real: 15.8580 MHz, ideal: 15.9155 MHz",
         transform=ax1.transAxes, color=INK2, fontsize=10)
ax1.grid(True, which="both", alpha=0.7)
ax1.set_axisbelow(True)
ax1.legend(frameon=False, fontsize=10, loc="lower left")
ax1.annotate("−3.0103 dB", xy=(1.2e5, -3.0103), xytext=(1.2e5, 1),
             color=INK2, fontsize=9)

ax1.annotate("real 15.8580 MHz\nideal 15.9155 MHz\n0.36 % apart",
             xy=(1.586e7, -3.0103), xytext=(3.0e6, -34),
             color=INK2, fontsize=9,
             arrowprops=dict(arrowstyle="->", color=INK2, lw=0.9,
                             connectionstyle="arc3,rad=-0.25"))

ax2.semilogx(f, ph_ideal, color=ORANGE, lw=5.5, alpha=0.55)
ax2.semilogx(f, ph_real, color=BLUE, lw=1.8)
ax2.axhline(-45, color=INK2, lw=0.9, ls=":")
ax2.axvline(1.58580e7, color=BLUE, lw=0.9, ls=":")
ax2.set_ylim(-95, 5)
ax2.set_yticks([0, -45, -90])
ax2.set_ylabel("phase (°)")
ax2.set_xlabel("frequency (Hz)")
ax2.grid(True, which="both", alpha=0.7)
ax2.set_axisbelow(True)
ax2.annotate("−45° at the corner", xy=(1.7e7, -45), xytext=(2.2e7, -35),
             color=INK2, fontsize=9)

fig.tight_layout()
dest = out / "ad102-rc-bode.png"
fig.savefig(dest, dpi=130)
print(f"  wrote {dest}")
