#!/usr/bin/env python3
"""Read the ngspice logs from this lab and tell you whether you got it right.

    python3 src/check_rc.py --rc results/rc.log
    python3 src/check_rc.py --mine results/my_rc.log
    python3 src/check_rc.py --rc results/rc.log --mine results/my_rc.log

Every `meas` in this lab reports the time at which the output crosses 63.2 %
of its final value, counted from t = 0. The step happens at t = 1 ns and it
has a 10 ps edge, so the time constant is

    tau = t_measured - 1 ns - 5 ps

The 5 ps is half the edge, and it is worth understanding rather than
tolerating -- see the writeup. This script subtracts it, so what it prints is
tau.

Reference numbers measured on hpretl/iic-osic-tools:2026.04 (ngspice 46,
sky130A, tt corner). GOLDEN: transient analysis of a linear circuit has no
randomness in it, so yours match to every digit.

Exit status 0 = every check passed, 1 = something did not.
"""

import argparse
import math
import re
import sys

STEP = 1.005e-9          # 1 ns of pulse delay + half of the 10 ps edge
STEP_SLOW = 100.005e-9   # the microsecond circuits step at 100 ns

# name -> (label, tau in seconds, how it is offset)
REF_RC = {
    "t_ece334":    ("A  ECE334 deck: 1k/2k divider + 0.7 pF, ideal",
                    466.67e-12, STEP),
    "t_ideal":     ("B  ideal 10 kohm + ideal 1 pF",
                    10.0000e-9, STEP),
    "t_realr":     ("C  YOUR Lab 01 resistor + ideal 1 pF",
                    10.0361e-9, STEP),
    "t_realc":     ("D  ideal 10 kohm + YOUR Lab 02 capacitor",
                    10.0000e-9, STEP),
    "t_real":      ("E  both of yours, no ideal parts anywhere",
                    10.0362e-9, STEP),
    "t_naive":     ("F  the same circuit sized without Labs 01 and 02",
                    10.5647e-9, STEP),
    "t_cold":      ("   E again at -40 C",
                    9.7849e-9, STEP),
    "t_hot":       ("   E again at +125 C",
                    10.6544e-9, STEP),
    "t_us_ideal":  ("G  ideal 1 Mohm + ideal 1 pF",
                    0.999995e-6, STEP_SLOW),
    "t_us_real":   ("H  real 1 Mohm of xhigh poly + your 1 pF",
                    1.049955e-6, STEP_SLOW),
}
REF_CPAR = {"cpar_10k": 7.233642e-15, "cpar_1m": 9.527787e-14}
LEN_10K, LEN_1M = 30.3315, 471.9814      # um of poly behind those two

TAU_TARGET = 20.0e-9
TAU_TOL = 0.01
AREA_BUDGET = 400.0


def read_log(path):
    out, pat = {}, re.compile(r"^\s*([a-z_0-9]+)\s*=\s*([-+0-9.eE]+)")
    try:
        with open(path) as f:
            for line in f:
                m = pat.match(line)
                if m:
                    out[m.group(1)] = float(m.group(2))
    except FileNotFoundError:
        sys.exit(f"check_rc.py: no such file: {path}\n"
                 f"            Run `make` first.")
    if not out:
        sys.exit(f"check_rc.py: {path} has no measured values in it.\n"
                 f"            ngspice failed. grep it for 'Error'.")
    return out


def close(a, b, tol):
    return abs(a - b) <= tol * abs(b)


def check_rc(path):
    v = read_log(path)
    bad = []
    print(f"  {'circuit':<52}{'tau':>14}{'reference':>14}")
    for k, (label, ref, off) in REF_RC.items():
        if k not in v:
            bad.append(f"{k} missing from {path}")
            continue
        tau = v[k] - off
        unit, sc = ("ps", 1e12) if abs(ref) < 1e-9 else ("ns", 1e9)
        print(f"  {label:<52}{tau*sc:>10.4f} {unit:<3}{ref*sc:>11.4f} {unit}")
        if not close(tau, ref, 0.005):
            bad.append(f"{k}: tau {tau*sc:.4f} {unit}, "
                       f"reference {ref*sc:.4f} {unit}")

    if all(k in v for k in ("t_ideal", "t_real", "t_naive", "t_cold", "t_hot")):
        ideal = v["t_ideal"] - STEP
        real = v["t_real"] - STEP
        naive = v["t_naive"] - STEP
        cold = v["t_cold"] - STEP
        hot = v["t_hot"] - STEP
        print()
        print(f"  designing with Labs 01 and 02 : "
              f"{100*(real-ideal)/ideal:+.2f} % from the 10.0000 ns you asked for")
        print(f"  designing without them        : "
              f"{100*(naive-ideal)/ideal:+.2f} %")
        print(f"  and the SAME silicon over -40 C to +125 C spans "
              f"{100*(hot-cold)/real:.2f} %")

    if all(k in v for k in ("t_us_ideal", "t_us_real")) \
            and "cpar_1m" in v:
        ex = (v["t_us_real"] - v["t_us_ideal"])
        pred = 1e6 * v["cpar_1m"] / 2
        print()
        print(f"  the microsecond ran {ex*1e9:.2f} ns long.")
        print(f"    a 471.98 um strip of poly carries "
              f"{v['cpar_1m']*1e15:.3f} fF to the substrate, and half of it")
        print(f"    adds to the time constant: R*Cpar/2 = "
              f"{pred*1e9:.2f} ns, which is "
              f"{100*pred/ex:.0f} % of what you measured.")

    for k, ref in REF_CPAR.items():
        if k in v and not close(v[k], ref, 0.005):
            bad.append(f"{k} = {v[k]:.6e} F, reference {ref:.6e} F")
    if all(k in v for k in REF_CPAR):
        b = (v["cpar_1m"] - v["cpar_10k"]) / (LEN_1M - LEN_10K)
        a = v["cpar_10k"] - b * LEN_10K
        print(f"    fitting both strips: {b*1e15:.4f} fF per um of "
              f"1 um-wide poly, plus {a*1e15:.4f} fF of ends.")
    return bad


def check_mine(path):
    v = read_log(path)
    if "t_mine" not in v:
        return [f"t_mine is not in {path}; the deck did not finish."]
    tau = v["t_mine"] - STEP
    lr, side = geometry_from_deck()
    area = lr + side * side
    err = 100 * (tau - TAU_TARGET) / TAU_TARGET
    ok_tau = close(tau, TAU_TARGET, TAU_TOL)
    ok_area = area < AREA_BUDGET
    print(f"  resistor  L = {lr:8.4f} um at W = 1 um   ->  {lr:9.2f} um^2")
    print(f"  capacitor s = {side:8.4f} um square       ->  {side*side:9.2f} um^2")
    print(f"  total drawn area                         ->  {area:9.2f} um^2"
          f"   (budget {AREA_BUDGET:.0f})   {'PASS' if ok_area else 'FAIL'}")
    print(f"  tau = {tau*1e9:.4f} ns   target 20.0000 ns   ({err:+.2f} %)"
          f"   {'PASS' if ok_tau else 'FAIL'}")
    bad = []
    if not ok_tau:
        bad.append(f"tau is {tau*1e9:.4f} ns, {err:+.2f} % from 20 ns.\n"
                   f"      If you pushed the resistor up and the capacitor "
                   f"down, tau came out LONG,\n"
                   f"      not short -- the strip of poly you added has its "
                   f"own capacitance to the\n"
                   f"      substrate, about 0.2 fF per micrometre. Shrink the "
                   f"capacitor to pay for it.")
    if not ok_area:
        bad.append(f"total area {area:.2f} um^2 is over the "
                   f"{AREA_BUDGET:.0f} um^2 budget.\n"
                   f"      Area is L + s^2, tau is R*C, and R is linear in L "
                   f"while C is quadratic\n"
                   f"      in s. Work out which way to move, then find out "
                   f"how far you can go\n"
                   f"      before the resistor's own capacitance stops you.")
    return bad


def geometry_from_deck(path="spice/my_rc.spice"):
    """Read the two shapes back out of the deck the student edited."""
    lr = side = None
    for line in open(path):
        t = line.strip()
        if t.lower().startswith("xrm"):
            m = re.search(r"L=([0-9.]+)", t, re.I)
            lr = float(m.group(1))
        if t.lower().startswith("xcm"):
            m = re.search(r"W=([0-9.]+)", t, re.I)
            side = float(m.group(1))
    if lr is None or side is None:
        sys.exit("check_rc.py: could not find Xrm/Xcm in spice/my_rc.spice.\n"
                 "            Keep the two instance names as shipped.")
    return lr, side


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rc", metavar="LOG")
    ap.add_argument("--mine", metavar="LOG")
    args = ap.parse_args()
    if not args.rc and not args.mine:
        ap.error("give me --rc, --mine, or both")

    bad = []
    if args.rc:
        print("=" * 82)
        print(" CHECKING  rc.spice  -- does the silicon keep the schematic's promise?")
        print("=" * 82)
        bad += check_rc(args.rc)
        print()
    if args.mine:
        print("=" * 82)
        print(" CHECKING  my_rc.spice  -- 20 ns, and what did it cost?")
        print("=" * 82)
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
