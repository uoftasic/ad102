#!/usr/bin/env python3
"""Read the ngspice logs from this lab and tell you whether you got it right.

    python3 src/check_res.py --sheet results/sheet.log
    python3 src/check_res.py --mine  results/mine.log
    python3 src/check_res.py --sheet results/sheet.log --mine results/mine.log

Nobody is grading this lab. This script is the grader. It pulls the printed
resistances out of the log, fits the two numbers that actually define a
fabricated resistor -- ohms per square, and the fixed end resistance -- and
compares them to a run on hpretl/iic-osic-tools:2026.04 (ngspice 46, sky130A).

Exit status 0 = every check passed, 1 = something did not. Usable from a
Makefile.
"""

import argparse
import re
import sys

# ---------------------------------------------------------------- reference
# Measured on the pinned image. These are what `make sheet` should print.
# GOLDEN: deterministic. A DC operating point has no randomness in it, so if
# your ngspice is the one in the workbench these match to every digit shown.
REF_SHEET = {
    "high_po":  {"rsq": 317.2198, "rend": 378.2448},
    "xhigh_po": {"rsq": 2118.7619, "rend": 34.2111},
}
REF_RAW = {
    "r_l1": 695.4646, "r_l2": 1012.684, "r_l5": 1964.344,
    "r_l10": 3550.443, "r_l20": 6722.641, "r_l50": 16239.23,
    "r_l100": 32100.22,
    "r_naive": 10373.02, "r_fixed": 9999.997,
    "r_w0p35": 10674.97, "r_w0p69": 5123.000,
    "r_w2": 1785.180, "r_w5": 716.7730,
    "r_x1": 2152.973, "r_x2": 4271.620, "r_x10": 21220.88,
    "r_x50": 105969.4, "r_x100": 211910.4,
}
RAW_TOL = 0.005          # 0.5 % on any single printed resistance
FIT_TOL = 0.01           # 1 % on the two extracted numbers

# What `make mine` has to hit.
# name -> (label, target ohms, the sheet resistance printed on the model card)
TARGETS = {
    "r_mine1": ("R1  sky130_fd_pr__res_high_po  W=1", 2200.0, 317.3885),
    "r_mine2": ("R2  sky130_fd_pr__res_xhigh_po W=1", 50000.0, 2000.0),
}
MINE_TOL = 0.01          # 1 % of target


def read_log(path):
    """Every `name = value` line ngspice printed, as a dict of floats."""
    out = {}
    pat = re.compile(r"^\s*([a-z_0-9]+)\s*=\s*([-+0-9.eE]+)\s*$")
    try:
        with open(path) as f:
            for line in f:
                m = pat.match(line)
                if m:
                    out[m.group(1)] = float(m.group(2))
    except FileNotFoundError:
        sys.exit(f"check_res.py: no such file: {path}\n"
                 f"             Run `make sheet` (or `make mine`) first.")
    if not out:
        sys.exit(f"check_res.py: {path} contains no printed values.\n"
                 f"             ngspice usually failed. Look for a line "
                 f"starting with 'Error' in it.")
    return out


def fit(r_short, l_short, r_long, l_long):
    """Two lengths, one straight line. Slope is ohms per square; the
    intercept is everything that does not depend on how long you drew it."""
    rsq = (r_long - r_short) / (l_long - l_short)
    rend = r_short - rsq * l_short
    return rsq, rend


def close(got, want, tol):
    return abs(got - want) <= tol * abs(want)


def check_sheet(path, verbose=True):
    v = read_log(path)
    bad = []

    missing = [k for k in REF_RAW if k not in v]
    if missing:
        bad.append("these values are missing from the log: "
                   + ", ".join(sorted(missing))
                   + "\n      Did the deck run all the way to the end?")
        return bad

    if verbose:
        print("  raw resistances (ohms)")
        for k in ("r_l1", "r_l10", "r_l100", "r_x1", "r_x10", "r_x100"):
            flag = "" if close(v[k], REF_RAW[k], RAW_TOL) else "   <- off"
            print(f"    {k:10s} {v[k]:14.4f}   reference {REF_RAW[k]:12.4f}{flag}")

    for k, ref in REF_RAW.items():
        if not close(v[k], ref, RAW_TOL):
            bad.append(f"{k} = {v[k]:.4f} ohm, reference {ref:.4f} ohm "
                       f"({100*(v[k]-ref)/ref:+.2f} %)")

    fits = {
        "high_po":  fit(v["r_l1"], 1.0, v["r_l100"], 100.0),
        "xhigh_po": fit(v["r_x1"], 1.0, v["r_x100"], 100.0),
    }
    if verbose:
        print()
        print("  the two numbers that define the device")
        print(f"    {'device':<12}{'ohm/square':>14}{'end ohms':>12}"
              f"{'   reference':>26}")
        for dev, (rsq, rend) in fits.items():
            ref = REF_SHEET[dev]
            print(f"    {dev:<12}{rsq:>14.4f}{rend:>12.4f}"
                  f"      {ref['rsq']:.4f} / {ref['rend']:.4f}")

    for dev, (rsq, rend) in fits.items():
        ref = REF_SHEET[dev]
        if not close(rsq, ref["rsq"], FIT_TOL):
            bad.append(f"{dev}: extracted {rsq:.4f} ohm/square, "
                       f"reference {ref['rsq']:.4f}")
        if not close(rend, ref["rend"], FIT_TOL):
            bad.append(f"{dev}: extracted {rend:.4f} ohm of end resistance, "
                       f"reference {ref['rend']:.4f}")

    if verbose:
        print()
        print("  and the design that follows from them")
        for dev, (rsq, rend) in fits.items():
            for target in (2200, 10000, 100000):
                L = (target - rend) / rsq
                print(f"    {dev:<12}{target:>8} ohm  ->  W=1  L={L:9.4f} um"
                      f"   ({L:8.2f} um^2 of body)")
    return bad


def check_mine(path, sheet_path=None, verbose=True):
    v = read_log(path)
    bad = []
    fits = None
    if sheet_path:
        s = read_log(sheet_path)
        if all(k in s for k in ("r_l1", "r_l100", "r_x1", "r_x100")):
            fits = {
                "r_mine1": fit(s["r_l1"], 1.0, s["r_l100"], 100.0),
                "r_mine2": fit(s["r_x1"], 1.0, s["r_x100"], 100.0),
            }

    for key, (label, target, card_rsq) in TARGETS.items():
        if key not in v:
            bad.append(f"{key} is not in {path}. The deck did not finish.")
            continue
        got = v[key]
        err = 100 * (got - target) / target
        ok = close(got, target, MINE_TOL)
        if verbose:
            print(f"  {label}")
            print(f"    target {target:>10.1f} ohm")
            print(f"    got    {got:>10.1f} ohm   ({err:+.2f} %)"
                  f"   {'PASS' if ok else 'FAIL'}")
        if not ok:
            hint = ""
            if fits and key in fits:
                rsq, rend = fits[key]
                want = (target - rend) / rsq
                naive = target / card_rsq
                hint = (f"\n      You have L = {naive:.4f} um, which is "
                        f"{target:.0f} / {card_rsq} -- the sheet\n"
                        f"      resistance off the model card, and nothing "
                        f"else.\n"
                        f"      Your own `make sheet` measured "
                        f"{rsq:.4f} ohm/square and {rend:.4f} ohm that\n"
                        f"      does not depend on length at all. Use both:\n"
                        f"        L = ({target:.0f} - {rend:.4f}) / "
                        f"{rsq:.4f} = {want:.4f} um")
            bad.append(f"{label}: {got:.1f} ohm is {err:+.2f} % from "
                       f"{target:.0f} ohm.{hint}")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", metavar="LOG", help="results/sheet.log")
    ap.add_argument("--mine", metavar="LOG", help="results/mine.log")
    args = ap.parse_args()
    if not args.sheet and not args.mine:
        ap.error("give me --sheet, --mine, or both")

    bad = []
    if args.sheet:
        print("=" * 62)
        print(" CHECKING  sheet.spice  -- did you measure the device right?")
        print("=" * 62)
        bad += check_sheet(args.sheet)
        print()
    if args.mine:
        print("=" * 62)
        print(" CHECKING  my_resistor.spice  -- did you size yours right?")
        print("=" * 62)
        bad += check_mine(args.mine, args.sheet)
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
