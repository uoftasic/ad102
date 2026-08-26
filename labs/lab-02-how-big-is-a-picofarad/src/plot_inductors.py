#!/usr/bin/env python3
"""Draw results/ind_sweep.txt as inductance and Q against frequency.

    python3 src/plot_inductors.py            # -> results/inductors.svg
    python3 src/plot_inductors.py PATH.svg

Optional. The lab's verdict does not depend on it, and matplotlib is already
in the workbench image so it needs nothing installed. The figure shipped with
the writeup was produced by this script from an unmodified `make henry` run.

Columns in ind_sweep.txt are ngspice `wrdata` pairs: (f, L220) (f, Q220)
(f, L125) (f, Q125) (f, L090) (f, Q090).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "results/ind_sweep.txt"
OUT = sys.argv[1] if len(sys.argv) > 1 else "results/inductors.svg"
COLS = {"ind_05_220": (1, 3), "ind_05_125": (5, 7), "ind_03_90": (9, 11)}
COLOUR = {"ind_05_220": "#1f6feb", "ind_05_125": "#bf5b04", "ind_03_90": "#117a4e"}

rows = [list(map(float, l.split())) for l in open(SRC) if l.strip()]
f = [r[0] / 1e9 for r in rows]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 6.4), sharex=True)
for name, (li, qi) in COLS.items():
    L = [r[li] * 1e9 for r in rows]
    Q = [r[qi] for r in rows]
    ax1.plot(f, L, color=COLOUR[name], lw=1.8, label=name)
    ax2.plot(f, Q, color=COLOUR[name], lw=1.8, label=name)
    # self-resonance: where the reactance stops being inductive
    for i in range(1, len(L)):
        if L[i - 1] > 0 >= L[i]:
            srf = f[i - 1] + (f[i] - f[i - 1]) * L[i - 1] / (L[i - 1] - L[i])
            ax1.axvline(srf, color=COLOUR[name], ls=":", lw=1.1)
            ax1.annotate(f"{srf:.2f} GHz", (srf, 1.0), rotation=90,
                         fontsize=8, color=COLOUR[name],
                         ha="right", va="bottom")
            break

ax1.set_xscale("log")
ax1.set_ylim(-2, 25)
ax1.axhline(0, color="#888", lw=0.8)
ax1.set_ylabel("apparent inductance (nH)")
ax1.set_title("SKY130's three inductors: everything SkyWater will sell you")
ax1.legend(loc="upper left", fontsize=9, frameon=False)
ax1.grid(alpha=0.25)

ax2.set_xscale("log")
ax2.set_ylim(0, 25)
ax2.set_xlabel("frequency (GHz)")
ax2.set_ylabel("quality factor Q")
ax2.grid(alpha=0.25)
ax2.annotate("Q peaks, then the loss in the substrate wins",
             (0.35, 0.9), xycoords="axes fraction", fontsize=9, color="#555")

fig.tight_layout()
fig.savefig(OUT)
print(f"wrote {OUT}")
