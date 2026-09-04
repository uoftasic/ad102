#!/usr/bin/env python3
"""Read the Monte Carlo logs from this lab and tell you whether you got it right.

    python3 src/check_mm.py --mm results/mismatch.log
    python3 src/check_mm.py --mine results/my_divider.log

Every `print` in these decks is one imaginary die off one imaginary wafer.
This script collects them, reports mean and standard deviation, and compares
both against a run on hpretl/iic-osic-tools:2026.08 (ngspice 47, sky130A).

The decks call `setseed 1`, so Monte Carlo here is **reproducible**: your two
hundred dies are the same two hundred dies, in the same order, as the ones in
the writeup. Statistics you cannot reproduce are not evidence.

Exit status 0 = every check passed, 1 = something did not.
"""

import argparse
import math
import re
import statistics as st
import sys

N_RUNS = 200
BODY_PELGROM = 0.03552          # straight off the res_high_po model card

# key -> (label, drawn area of ONE device in um^2)
SINGLES = {
    "s1": ("W=1  L=1", 1.0),
    "s2": ("W=1  L=4", 4.0),
    "s3": ("W=2  L=8", 16.0),
    "s4": ("W=4  L=16", 64.0),
}
# key -> (label, nominal volts, sigma volts) measured on the pinned image
REF_DIV = {
    "ta": ("1:1  two devices W=0.42 L=2    0.84 um^2 each",
           0.900000, 2.507870e-02),
    "tb": ("1:1  two devices W=2 L=20        40 um^2 each",
           0.900000, 3.232131e-03),
    "tc": ("3:1  one L=6 and one L=18        24 um^2 total",
           1.309327, 5.643323e-03),
    "td": ("3:1  four identical L=6 units    24 um^2 total",
           1.350000, 5.729023e-03),
}
REF_SINGLE_SIGMA = {"s1": 2.5852, "s2": 1.6046, "s3": 0.8391, "s4": 0.4007}

TAP_TARGET = 0.4500
TAP_TOL = 0.002          # 0.2 %
SIGMA_BUDGET = 3.0e-3
AREA_BUDGET = 150.0


def read_runs(path):
    """Everything printed before the NOMINAL banner is a Monte Carlo die;
    everything after it is the nominal."""
    mc, nom, after = {}, {}, False
    pat = re.compile(r"^v\((\w+)\)\s*=\s*([-+0-9.eE]+)")
    try:
        lines = open(path).read().splitlines()
    except FileNotFoundError:
        sys.exit(f"check_mm.py: no such file: {path}\n"
                 f"            Run `make` first.")
    for line in lines:
        if "NOMINAL" in line:
            after = True
            continue
        m = pat.match(line)
        if not m:
            continue
        k, v = m.group(1), float(m.group(2))
        if after:
            nom[k] = v
        else:
            mc.setdefault(k, []).append(v)
    if not mc:
        sys.exit(f"check_mm.py: {path} has no Monte Carlo results in it.\n"
                 f"            grep it for 'vector run is not available' -- "
                 f"that means the\n"
                 f"            loop counter was destroyed and only one die "
                 f"was simulated.")
    return mc, nom


def close(a, b, tol):
    return abs(a - b) <= tol * abs(b)


def check_mm(path):
    mc, nom = read_runs(path)
    bad = []
    n = len(next(iter(mc.values())))
    if n != N_RUNS:
        bad.append(f"{n} dies in the log, expected {N_RUNS}")
    print(f"  {n} Monte Carlo dies, seed 1.")
    print()

    print("  A. one resistor, four sizes -- does sigma halve when area quadruples?")
    print(f"    {'geometry':<14}{'area':>8}{'sigma/R':>11}"
          f"{'0.03552/sqrt(A)':>18}{'ratio to previous':>20}")
    prev = None
    for k, (label, area) in SINGLES.items():
        if k not in mc:
            bad.append(f"{k} missing from {path}")
            continue
        v = mc[k]
        rel = 100 * st.pstdev(v) / st.mean(v)
        pel = 100 * BODY_PELGROM / math.sqrt(area)
        r = f"{prev/rel:>19.3f}" if prev else f"{'--':>19}"
        print(f"    {label:<14}{area:>7.0f} {rel:>10.4f}%{pel:>17.4f}%{r}")
        prev = rel
        if not close(rel, REF_SINGLE_SIGMA[k], 0.02):
            bad.append(f"{k}: sigma/R {rel:.4f} %, reference "
                       f"{REF_SINGLE_SIGMA[k]} %")
    print("    (the 1 um^2 device is the odd one out on purpose -- see the writeup)")
    print()

    print("  B and C. four dividers")
    print(f"    {'circuit':<46}{'nominal':>12}{'sigma':>12}")
    for k, (label, rnom, rsig) in REF_DIV.items():
        if k not in mc:
            bad.append(f"{k} missing from {path}")
            continue
        v = mc[k]
        sig = st.pstdev(v)
        got_nom = nom.get(k, float("nan"))
        print(f"    {label:<46}{got_nom:>10.6f} V{sig*1e3:>9.4f} mV")
        if not close(got_nom, rnom, 0.002):
            bad.append(f"{k}: nominal {got_nom:.6f} V, reference {rnom:.6f} V")
        if not close(sig, rsig, 0.03):
            bad.append(f"{k}: sigma {sig*1e3:.4f} mV, "
                       f"reference {rsig*1e3:.4f} mV")

    if all(k in mc for k in ("tc", "td")) and "tc" in nom and "td" in nom:
        print()
        print(f"    the 3:1 ratio you asked for is 1.350000 V.")
        print(f"      two devices  : {nom['tc']:.6f} V  "
              f"({100*(nom['tc']-1.35)/1.35:+.2f} %)")
        print(f"      four units   : {nom['td']:.6f} V  "
              f"({100*(nom['td']-1.35)/1.35:+.2f} %)")
        sc, sd = st.pstdev(mc["tc"]), st.pstdev(mc["td"])
        sos = 100 / math.sqrt(2 * len(mc["tc"]))
        print(f"    and the spread is {sc*1e3:.4f} mV against {sd*1e3:.4f} mV "
              f"-- a {100*abs(sc-sd)/sc:.1f} % difference,")
        print(f"    where 200 samples only pin sigma down to +/- {sos:.1f} %. "
              f"Those are the same number.")
    return bad


def geometry(path="spice/my_divider.spice"):
    """Total drawn area: sum of W*L over every X-line in the student's deck."""
    total, devs = 0.0, []
    for line in open(path):
        t = line.strip()
        if not t or t.startswith("*") or not t[0] in "xX":
            continue
        w = re.search(r"\bW\s*=\s*([0-9.]+)", t, re.I)
        l = re.search(r"\bL\s*=\s*([0-9.]+)", t, re.I)
        if w and l:
            a = float(w.group(1)) * float(l.group(1))
            devs.append((t.split()[0], float(w.group(1)), float(l.group(1)), a))
            total += a
    if not devs:
        sys.exit("check_mm.py: found no X-lines with W= and L= in "
                 "spice/my_divider.spice.")
    return devs, total


def check_mine(path):
    mc, nom = read_runs(path)
    bad = []
    if "tap" not in mc:
        return ["the deck never printed v(tap). Keep the node named `tap`."]
    v = mc["tap"]
    sig = st.pstdev(v)
    got_nom = nom.get("tap", float("nan"))
    devs, area = geometry()

    print(f"  {len(devs)} device(s):")
    for name, w, l, a in devs:
        print(f"    {name:<8} W={w:<8.4f} L={l:<8.4f}  {a:8.2f} um^2")
    print()
    ok_nom = close(got_nom, TAP_TARGET, TAP_TOL)
    ok_sig = sig <= SIGMA_BUDGET
    ok_area = area < AREA_BUDGET
    print(f"  1. nominal tap  {got_nom:9.6f} V    target 0.450000 V "
          f"({100*(got_nom-TAP_TARGET)/TAP_TARGET:+6.2f} %)      "
          f"{'PASS' if ok_nom else 'FAIL'}")
    print(f"  2. sigma        {sig*1e3:9.4f} mV   budget 3.0000 mV"
          f"                    {'PASS' if ok_sig else 'FAIL'}")
    print(f"  3. drawn area   {area:9.2f} um^2 budget {AREA_BUDGET:6.0f} um^2"
          f"                 {'PASS' if ok_area else 'FAIL'}")

    if not ok_nom:
        bad.append(f"nominal tap is {got_nom:.6f} V, "
                   f"{100*(got_nom-TAP_TARGET)/TAP_TARGET:+.2f} % off.\n"
                   f"      This is a SYSTEMATIC error and no amount of area "
                   f"will fix it. Every\n"
                   f"      resistor carries the same fixed end resistance "
                   f"regardless of length --\n"
                   f"      Lab 01 measured it at 378.2448 ohm -- so a long "
                   f"device and a short one\n"
                   f"      are not in the ratio of their lengths. Ask "
                   f"yourself what shape of\n"
                   f"      divider makes that overhead cancel.")
    if not ok_sig:
        bad.append(f"sigma is {sig*1e3:.4f} mV against a 3.0000 mV budget.\n"
                   f"      This one IS an area problem: sigma goes as "
                   f"1/sqrt(W*L). Quadrupling\n"
                   f"      the area of every device halves it.")
    if not ok_area:
        bad.append(f"total drawn area {area:.2f} um^2 is over the "
                   f"{AREA_BUDGET:.0f} um^2 budget.")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mm", metavar="LOG")
    ap.add_argument("--mine", metavar="LOG")
    args = ap.parse_args()
    if not args.mm and not args.mine:
        ap.error("give me --mm, --mine, or both")

    bad = []
    if args.mm:
        print("=" * 78)
        print(" CHECKING  mismatch.spice  -- how alike are two identical resistors?")
        print("=" * 78)
        bad += check_mm(args.mm)
        print()
    if args.mine:
        print("=" * 78)
        print(" CHECKING  my_divider.spice  -- 0.45 V, accurately, precisely, cheaply")
        print("=" * 78)
        bad += check_mine(args.mine)
        print()

    if bad:
        print("FAIL")
        for b in bad:
            print(f"    - {b}")
        print()
        return 1
    print("PASS -- every number matches the reference run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
