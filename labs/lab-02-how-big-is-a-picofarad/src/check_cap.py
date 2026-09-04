#!/usr/bin/env python3
"""Read the ngspice logs from this lab and tell you whether you got it right.

    python3 src/check_cap.py --pf results/picofarad.log
    python3 src/check_cap.py --mine results/my_cap.log --pf results/picofarad.log
    python3 src/check_cap.py --henry results/henry.log --sweep results/ind_sweep.txt
    python3 src/check_cap.py --tank results/tank.log

This script is the grader. It fits the two terms that describe a real plate
capacitor -- farads per square micrometre, and farads per micrometre of edge
-- out of the area ladder you simulated, then prices one picofarad in each of
the technologies SKY130 offers, and finally does the same for the only three
inductors in the PDK.

Exit status 0 = every check passed, 1 = something did not.

All reference numbers were measured on hpretl/iic-osic-tools:2026.08
(ngspice 47, sky130A, tt corner, 27 C). AC operating points are deterministic,
so these are GOLDEN: yours match to every digit printed.
"""

import argparse
import math
import re
import sys

ADDER_UM2 = 110.1056       # DD103's 4-bit ripple-carry adder, sky130_fd_sc_hd

REF_PF = {
    "c_s1": 2.642250e-15, "c_s2": 9.302250e-15, "c_s5": 5.328225e-14,
    "c_s10": 2.065822e-13, "c_s20": 8.131822e-13,
    "c_naive": 1.014742e-12, "c_fixed": 1.000001e-12,
    "c_nmos10": 7.876883e-13, "c_nmos11": 9.999739e-13,
    "c_pmos10": 8.429616e-13, "c_vpp": 1.164030e-13,
    "c_nmos_off": 2.207181e-13,
}
# two-term fit from the two end plates, then the three-term fit that also
# uses the 10 um plate. Both in fF, with the side length s in um.
REF_FIT2 = {"area": 2.000887, "edge": 0.641363}
REF_FIT3 = {"area": 2.000000, "edge": 0.659991, "const": -0.017742}
REF_HENRY = {
    "l_220_100m": 9.922032e-09,
    "l_125_100m": 5.785709e-09,
    "l_090_100m": 1.520796e-09,
    "l_090_2g4": 1.554019e-09,
    "q_090_2g4": 1.086413e+01,
}
REF_SWEEP = {           # (Qmax, f of Qmax in GHz, self-resonance in GHz)
    "ind_05_220": (12.718, 1.3717, 3.5236),
    "ind_05_125": (13.083, 2.2539, 6.5212),
    "ind_03_90":  (21.126, 6.3668, 16.5015),
}
REF_TANK = {"fpeak": 2.400e9, "zpeak": 250.130}

TOL = 0.01
TARGETS = {
    "c_mine1": ("C1  cap_mim_m3_1, square", 250e-15),
    "c_mine2": ("C2  cap_mim_m3_1, square",  20e-15),
    "c_mine3": ("C3  nfet_01v8 gate at 1.8 V, square", 250e-15),
}


def read_log(path):
    # `print x` gives "x = 1.0e+00"; `meas ac` gives
    # "zpeak =  2.50130e+02 at=  2.40000e+09" -- take the first number either way.
    out, pat = {}, re.compile(r"^\s*([a-z_0-9]+)\s*=\s*([-+0-9.eE]+)")
    try:
        with open(path) as f:
            for line in f:
                m = pat.match(line)
                if m:
                    out[m.group(1)] = float(m.group(2))
    except FileNotFoundError:
        sys.exit(f"check_cap.py: no such file: {path}\n"
                 f"             Run `make` first.")
    if not out:
        sys.exit(f"check_cap.py: {path} has no printed values in it.\n"
                 f"             ngspice failed. grep it for a line starting "
                 f"'Error'.")
    return out


def close(a, b, tol=TOL):
    return abs(a - b) <= tol * abs(b)


def fit_plate(c_small, s_small, c_big, s_big):
    """Two square plates, two unknowns.  C = area*s^2 + edge*s  (fF, um)."""
    d = s_small * s_small * s_big - s_big * s_big * s_small
    area = (c_small * s_big - c_big * s_small) / d
    edge = (c_big * s_small * s_small - c_small * s_big * s_big) / d
    return area, edge


def fit_plate3(c1, c10, c20):
    """Three plates (sides 1, 10 and 20 um), three unknowns.
    C = area*s^2 + edge*s + const."""
    r1, r2 = c10 - c1, c20 - c10
    area = (10 * r1 - 9 * r2) / (990 - 2700)
    edge = (r2 - 300 * area) / 10
    const = c1 - area - edge
    return area, edge, const


def side_for(c_ff, area, edge, const=0.0):
    """Invert the fit: what side length gives c_ff femtofarads?"""
    disc = edge * edge - 4 * area * (const - c_ff)
    return (-edge + math.sqrt(disc)) / (2 * area)


def check_pf(path):
    v = read_log(path)
    bad = []
    missing = [k for k in REF_PF if k not in v]
    if missing:
        return [f"missing from the log: {', '.join(sorted(missing))}"]
    for k, ref in REF_PF.items():
        if not close(v[k], ref, 0.005):
            bad.append(f"{k} = {v[k]:.6e} F, reference {ref:.6e} F "
                       f"({100*(v[k]-ref)/ref:+.2f} %)")

    area, edge = fit_plate(v["c_s1"] * 1e15, 1.0, v["c_s20"] * 1e15, 20.0)
    print("  two plates, two terms:  C[fF] = area*s^2 + edge*s")
    print(f"    area term  {area:9.6f} fF per um^2       reference "
          f"{REF_FIT2['area']:.6f}")
    print(f"    edge term  {edge:9.6f} fF per um of side  reference "
          f"{REF_FIT2['edge']:.6f}")
    if not close(area, REF_FIT2["area"]):
        bad.append(f"two-term area {area:.6f}, reference {REF_FIT2['area']}")
    if not close(edge, REF_FIT2["edge"], 0.05):
        bad.append(f"two-term edge {edge:.6f}, reference {REF_FIT2['edge']}")

    print()
    print("    against the three plates it was not fitted to")
    for k, sd in (("c_s2", 2.0), ("c_s5", 5.0), ("c_s10", 10.0)):
        pred = area * sd * sd + edge * sd
        got = v[k] * 1e15
        print(f"      side {sd:5.1f} um   fit {pred:10.4f} fF   "
              f"measured {got:10.4f} fF   ({100*(pred-got)/got:+.4f} %)")
    print("      -- every residual is negative. Something small and constant")
    print("         is missing, and it does not scale with the plate at all.")

    a3, e3, g3 = fit_plate3(v["c_s1"] * 1e15, v["c_s10"] * 1e15,
                            v["c_s20"] * 1e15)
    print()
    print("  three plates, three terms:  C[fF] = area*s^2 + edge*s + const")
    print(f"    area  {a3:10.6f}    edge {e3:10.6f}    const {g3:10.6f}")
    print(f"    reference {REF_FIT3['area']:.6f}   {REF_FIT3['edge']:.6f}"
          f"   {REF_FIT3['const']:.6f}")
    print("    against all five plates")
    for k, sd in (("c_s1", 1.0), ("c_s2", 2.0), ("c_s5", 5.0),
                  ("c_s10", 10.0), ("c_s20", 20.0)):
        pred = a3 * sd * sd + e3 * sd + g3
        got = v[k] * 1e15
        print(f"      side {sd:5.1f} um   fit {pred:10.4f} fF   "
              f"measured {got:10.4f} fF   ({100*(pred-got)/got:+.4f} %)")
    for nm, gotv, refv in (("area", a3, REF_FIT3["area"]),
                           ("edge", e3, REF_FIT3["edge"])):
        if not close(gotv, refv, 0.01):
            bad.append(f"three-term {nm} {gotv:.6f}, reference {refv}")

    d = (0.76 - e3) / 4
    print()
    print(f"    the edge term implies a metal etch bias of "
          f"{d*1000:.2f} nm per side,")
    print(f"    which predicts a constant term of "
          f"{2*d*d - 0.76*d:.6f} fF against the {g3:.6f} you measured.")

    print()
    print("  what one picofarad costs")
    print(f"    {'recipe':<34}{'fF/um^2':>10}{'um^2 for 1 pF':>16}"
          f"{'adders':>9}")
    s1p = side_for(1000.0, a3, e3, g3)
    rows = [
        ("MIM  cap_mim_m3_1", 1000.0 / (s1p * s1p), s1p * s1p),
        ("MOS  nfet_01v8 gate at 1.8 V",
         v["c_nmos11"] * 1e15 / (11.2699 ** 2),
         1000.0 / (v["c_nmos11"] * 1e15 / (11.2699 ** 2))),
        ("MOS  pfet_01v8 gate at 1.8 V",
         v["c_pmos10"] * 1e15 / 100.0,
         1000.0 / (v["c_pmos10"] * 1e15 / 100.0)),
        ("VPP  m1-m4 wafflecap",
         v["c_vpp"] * 1e15 / (11.3 ** 2),
         1000.0 / (v["c_vpp"] * 1e15 / (11.3 ** 2))),
    ]
    for name, dens, a in rows:
        print(f"    {name:<34}{dens:>10.4f}{a:>16.2f}{a/ADDER_UM2:>9.2f}")

    off = v["c_nmos_off"] / v["c_nmos10"]
    print()
    print(f"  and the MOS capacitor with its bias removed: "
          f"{v['c_nmos_off']*1e15:.2f} fF instead of "
          f"{v['c_nmos10']*1e15:.2f} fF")
    print(f"    -- a factor of {1/off:.2f} for the identical piece of layout.")
    return bad


def check_mine(path, pf_path=None):
    v = read_log(path)
    bad = []
    fit = None
    if pf_path:
        p = read_log(pf_path)
        if all(k in p for k in ("c_s1", "c_s10", "c_s20")):
            fit = fit_plate3(p["c_s1"] * 1e15, p["c_s10"] * 1e15,
                             p["c_s20"] * 1e15)
    for key, (label, target) in TARGETS.items():
        if key not in v:
            bad.append(f"{key} is not in {path}; the deck did not finish.")
            continue
        got = v[key]
        err = 100 * (got - target) / target
        ok = close(got, target)
        print(f"  {label}")
        print(f"    target {target*1e15:>9.2f} fF")
        print(f"    got    {got*1e15:>9.2f} fF   ({err:+.2f} %)   "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            hint = ""
            if fit and "mim" in label.lower():
                a, e, g = fit
                want = side_for(target * 1e15, a, e, g)
                naive = math.sqrt(target * 1e15 / a)
                hint = (f"\n      A square plate of side s holds "
                        f"{a:.4f}*s^2 + {e:.4f}*s {g:+.4f} femtofarads --\n"
                        f"      your own area ladder said so. Dropping "
                        f"everything but the area term gives\n"
                        f"      s = {naive:.4f} um; keeping it all gives "
                        f"s = {want:.4f} um. The smaller the\n"
                        f"      plate, the more the edge is worth.")
            bad.append(f"{label}: {got*1e15:.2f} fF is {err:+.2f} % from "
                       f"{target*1e15:.0f} fF.{hint}")
    return bad


def check_henry(path):
    v = read_log(path)
    bad = []
    print("  the only three inductors in SKY130")
    for k, ref in REF_HENRY.items():
        if k not in v:
            bad.append(f"{k} missing from {path}")
            continue
        unit = "nH" if k.startswith("l_") else ""
        scale = 1e9 if k.startswith("l_") else 1.0
        print(f"    {k:<14}{v[k]*scale:12.4f} {unit:<3} reference "
              f"{ref*scale:.4f}")
        if not close(v[k], ref, 0.005):
            bad.append(f"{k} = {v[k]:.6e}, reference {ref:.6e}")
    return bad


def check_sweep(path):
    try:
        rows = [list(map(float, l.split())) for l in open(path) if l.strip()]
    except FileNotFoundError:
        sys.exit(f"check_cap.py: no such file: {path}\n"
                 f"             Run `make henry` first.")
    bad = []
    cols = {"ind_05_220": (1, 3), "ind_05_125": (5, 7), "ind_03_90": (9, 11)}
    print()
    print(f"    {'inductor':<14}{'L @100 MHz':>12}{'Q max':>9}{'at GHz':>9}"
          f"{'self-res GHz':>15}{'inner um^2':>12}")
    inner = {"ind_05_220": 220.0 ** 2, "ind_05_125": 125.0 ** 2,
             "ind_03_90": 90.0 ** 2}
    for name, (li, qi) in cols.items():
        f = [r[0] for r in rows]
        L = [r[li] for r in rows]
        Q = [r[qi] for r in rows]
        srf = float("nan")
        for i in range(1, len(L)):
            if L[i - 1] > 0 >= L[i]:
                srf = f[i - 1] + (f[i] - f[i - 1]) * L[i - 1] / (L[i - 1] - L[i])
                break
        j = max(range(len(Q)), key=lambda i: Q[i])
        print(f"    {name:<14}{L[0]*1e9:>10.4f} nH{Q[j]:>9.3f}"
              f"{f[j]/1e9:>9.4f}{srf/1e9:>15.4f}{inner[name]:>12.0f}")
        rq, rf, rs = REF_SWEEP[name]
        if not close(Q[j], rq, 0.02):
            bad.append(f"{name}: Q max {Q[j]:.3f}, reference {rq}")
        if not close(srf, rs * 1e9, 0.02):
            bad.append(f"{name}: self-resonance {srf/1e9:.4f} GHz, "
                       f"reference {rs} GHz")
    return bad


def check_tank(path):
    v = read_log(path)
    bad = []
    for k in ("fpeak", "zpeak"):
        if k not in v:
            bad.append(f"{k} missing from {path}")
    if bad:
        return bad
    print(f"  parallel resonance found at {v['fpeak']/1e9:.4f} GHz, "
          f"|Z| = {v['zpeak']:.3f} ohm")
    print(f"    you aimed at 2.4000 GHz.")
    if not close(v["fpeak"], REF_TANK["fpeak"], 0.01):
        bad.append(f"resonance at {v['fpeak']/1e9:.4f} GHz, expected 2.4000")
    if not close(v["zpeak"], REF_TANK["zpeak"], 0.02):
        bad.append(f"peak |Z| {v['zpeak']:.3f} ohm, reference "
                   f"{REF_TANK['zpeak']}")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pf", metavar="LOG")
    ap.add_argument("--mine", metavar="LOG")
    ap.add_argument("--henry", metavar="LOG")
    ap.add_argument("--sweep", metavar="TXT")
    ap.add_argument("--tank", metavar="LOG")
    args = ap.parse_args()
    if not any(vars(args).values()):
        ap.error("give me at least one of --pf --mine --henry --sweep --tank")

    bad = []
    if args.pf:
        print("=" * 66)
        print(" CHECKING  picofarad.spice  -- what does a farad cost?")
        print("=" * 66)
        bad += check_pf(args.pf)
        print()
    if args.mine:
        print("=" * 66)
        print(" CHECKING  my_cap.spice  -- did you size yours right?")
        print("=" * 66)
        bad += check_mine(args.mine, args.pf)
        print()
    if args.henry:
        print("=" * 66)
        print(" CHECKING  henry.spice  -- and the inductor?")
        print("=" * 66)
        bad += check_henry(args.henry)
        if args.sweep:
            bad += check_sweep(args.sweep)
        print()
    if args.tank:
        print("=" * 66)
        print(" CHECKING  tank.spice  -- one resonator, built for real")
        print("=" * 66)
        bad += check_tank(args.tank)
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
