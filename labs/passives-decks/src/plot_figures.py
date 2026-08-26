#!/usr/bin/env python3
"""Regenerate the three figures the AD102 guide pages embed.

Reads only files this package produced, so the pictures and the printed
numbers cannot drift apart.

Usage:  python3 src/plot_figures.py results/ ../../docs/assets/img
"""
import re
import sys
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Validated categorical slots 1-3 (light surface #fcfcfb).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
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


def dress(ax, title, sub, xlabel, ylabel):
    ax.set_title(title, color=INK, fontsize=13, fontweight="bold",
                 loc="left", pad=22)
    ax.text(0, 1.02, sub, transform=ax.transAxes, color=INK2, fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="both", alpha=0.7)
    ax.set_axisbelow(True)


def fig_moscap(res, out):
    log = (res / "c_moscap_cv.log").read_text(errors="replace")
    pts = []
    for m in re.finditer(r"^\s*c_(\d{3})mv\s*=\s*([-+0-9.eE]+)\s*$", log, re.M):
        pts.append((int(m.group(1)) / 100.0, float(m.group(2)) * 1e15))
    pts.sort()
    if not pts:
        print("  skip moscap: no data"); return
    v = [p[0] for p in pts]; c = [p[1] for p in pts]

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(v, c, color=BLUE, marker="o", markersize=4.5,
            markerfacecolor=SURFACE, markeredgewidth=1.6, zorder=3)
    ax.axhline(832.46, color=INK2, linewidth=1.2, linestyle=(0, (5, 4)), zorder=2)
    ax.text(0.05, 852, "832.46 fF = the oxide alone, "
                       r"$\varepsilon_0\varepsilon_r A/t_{ox}$",
            color=INK2, fontsize=9.5)
    ax.annotate(f"{c[0]:.1f} fF at 0 V", xy=(v[0], c[0]),
                xytext=(0.13, 300), color=INK, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=INK2, linewidth=1))
    ax.annotate(f"{c[-1]:.1f} fF at 1.8 V", xy=(v[-1], c[-1]),
                xytext=(1.02, 690), color=INK, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=INK2, linewidth=1))
    dress(ax, "A MOS capacitor's value depends on the voltage across it",
          "sky130_fd_pr__nfet_01v8, 10 um x 10 um, S/D/body grounded",
          "Gate voltage (V)", "Capacitance (fF)")
    ax.set_ylim(0, 900)
    fig.tight_layout()
    fig.savefig(out / "ad102-moscap-cv.png", dpi=170)
    plt.close(fig)
    print("  wrote", out / "ad102-moscap-cv.png")


def fig_spiral_q(res, out):
    path = res / "l_spiral.txt"
    if not path.exists():
        print("  skip spiral: no l_spiral.txt"); return
    rows = [[float(x) for x in ln.split()] for ln in path.read_text().splitlines() if ln.strip()]
    # wrdata column order: f L1 f Q1 f L2 f Q2 f L3 f Q3 f R3
    f = [r[0] for r in rows]
    series = [("ind_03_90  (1.52 nH)", [r[3] for r in rows], [r[1] for r in rows], BLUE),
              ("ind_05_125  (5.78 nH)", [r[7] for r in rows], [r[5] for r in rows], ORANGE),
              ("ind_05_220  (9.91 nH)", [r[11] for r in rows], [r[9] for r in rows], AQUA)]

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for label, q, l, col in series:
        xs = [ff for ff, qq, ll in zip(f, q, l) if qq > 0 and ll > 0]
        ys = [qq for qq, ll in zip(q, l) if qq > 0 and ll > 0]
        ax.plot(xs, ys, color=col, label=label, zorder=3)
        ax.annotate(label, xy=(xs[-1], ys[-1]), xytext=(7, 0),
                    textcoords="offset points", color=col, fontsize=9,
                    fontweight="bold", va="center")
    ax.axhline(1.0, color=INK2, linewidth=1.2, linestyle=(0, (5, 4)), zorder=2)
    ax.text(1.4e3, 1.6, "Q = 1: reactance equals resistance",
            color=INK2, fontsize=9.5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1e3, 3e11); ax.set_ylim(1e-6, 90)
    dress(ax, "Below a gigahertz, an on-die spiral is a resistor",
          "Q into one port, other end grounded  ·  sky130A, tt corner",
          "Frequency (Hz)", "Q  =  Im(Z) / Re(Z)")
    leg = ax.legend(frameon=False, loc="lower right", fontsize=9.5)
    for t in leg.get_texts():
        t.set_color(INK2)
    fig.tight_layout()
    fig.savefig(out / "ad102-spiral-q.png", dpi=170)
    plt.close(fig)
    print("  wrote", out / "ad102-spiral-q.png")


def fig_mismatch(res, out):
    log = res / "mismatch.log"
    if not log.exists():
        print("  skip mismatch: no log"); return
    cols = {}
    for line in log.read_text(errors="replace").splitlines():
        m = re.match(r"^\s*1m/\(-i\((v[abcd])\)\)\s*=\s*([-+0-9.eE]+)\s*$", line)
        if m:
            cols.setdefault(m.group(1), []).append(float(m.group(2)))
    if not all(k in cols for k in "va vb vc vd".split()):
        print("  skip mismatch: incomplete data"); return
    n = min(len(cols[k]) for k in ("va", "vb", "vc", "vd"))
    small = [100 * (a / b - 1) for a, b in zip(cols["va"][:n], cols["vb"][:n])]
    big = [100 * (a / b - 1) for a, b in zip(cols["vc"][:n], cols["vd"][:n])]

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    bins = [x * 0.5 - 15 for x in range(61)]
    ax.hist(small, bins=bins, color=BLUE, alpha=0.85, label="drawn 1 um x 1 um",
            edgecolor=SURFACE, linewidth=1.0, zorder=3)
    ax.hist(big, bins=bins, color=ORANGE, alpha=0.85,
            label="drawn 10 um x 10 um", edgecolor=SURFACE, linewidth=1.0,
            zorder=4)
    s_small = statistics.stdev(small)
    s_big = statistics.stdev(big)
    ax.annotate(f"1 um x 1 um\nsigma = {s_small:.2f} %", xy=(-7.2, 12),
                color=BLUE, fontsize=10, fontweight="bold", ha="center")
    ax.annotate(f"10 um x 10 um\nsigma = {s_big:.2f} %", xy=(6.4, 30),
                color=ORANGE, fontsize=10, fontweight="bold", ha="center")
    dress(ax, "One hundred times the area, "
              f"{s_small / s_big:.1f} times the matching",
          f"{n} Monte Carlo wafers, seed 12345  ·  two res_high_po per wafer",
          "Mismatch between the pair,  100 x (R_A / R_B - 1)   (%)",
          "Wafers")
    ax.set_xlim(-15, 15)
    leg = ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    for t in leg.get_texts():
        t.set_color(INK2)
    fig.tight_layout()
    fig.savefig(out / "ad102-mismatch.png", dpi=170)
    plt.close(fig)
    print("  wrote", out / "ad102-mismatch.png")


def main(argv):
    res = Path(argv[1] if len(argv) > 1 else "results")
    out = Path(argv[2] if len(argv) > 2 else "../../docs/assets/img")
    out.mkdir(parents=True, exist_ok=True)
    fig_moscap(res, out)
    fig_spiral_q(res, out)
    fig_mismatch(res, out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
