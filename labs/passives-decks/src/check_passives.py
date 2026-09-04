#!/usr/bin/env python3
"""AD102 passives-decks -- read the ngspice logs and render a verdict.

Every reference number below came out of the pinned workbench
(hpretl/iic-osic-tools:2026.08, ngspice 47, sky130A, tt corner, 27 C).
A DC operating point and a linear AC analysis have no randomness in them,
and mismatch.spice pins its seed, so your run matches to every digit.

Usage:  python3 src/check_passives.py results/
Exit 0 = every check passed.
"""
import re
import sys
import math
import statistics
from pathlib import Path

TOL = 5e-4  # 0.05 % -- these are golden, not ballpark

# name -> (log file, ngspice variable, expected value, unit, what it proves)
CHECKS = [
    ("r_head_and_body.log", "head_l1",   299.8915,   "ohm",
     "contact head, 1 um long strip"),
    ("r_head_and_body.log", "head_l10",  299.8915,   "ohm",
     "contact head, 10 um long strip -- SAME number"),
    ("r_head_and_body.log", "body_l1",   395.5731,   "ohm",  "body, L = 1 um"),
    ("r_head_and_body.log", "body_l10",  3250.551,   "ohm",  "body, L = 10 um"),
    ("r_head_and_body.log", "r_10x10",   358.8661,   "ohm",
     "the 10 um x 10 um device mismatch.spice uses"),
    ("r_head_and_body.log", "head_10x10", 34.10354,   "ohm",  "its head"),
    ("r_head_and_body.log", "body_10x10", 324.7625,   "ohm",  "its body"),
    ("r_head_and_body.log", "r_100k",    1.000000e5, "ohm",  "sized 100 k"),
    ("r_head_and_body.log", "r_xhigh",   6.653872e5, "ohm",
     "same strip, res_xhigh_po implant"),
    ("r_head_and_body.log", "r_w0p35",  9.999975e4, "ohm",
     "100 k drawn 0.35 um wide -- 35.68 um^2"),
    ("r_head_and_body.log", "r_w5",      1.000004e5, "ohm",
     "100 k drawn 5 um wide -- 7880.78 um^2, same value"),
    ("c_area.log", "c_mim_10x10", 2.065822e-13, "F", "MIM, 10 um x 10 um"),
    ("c_area.log", "c_mim_30x30", 1.819782e-12, "F", "MIM, 30 um x 30 um"),
    ("c_area.log", "c_vpp",       1.473400e-13, "F", "VPP fringe, 11.5 x 11.7 um"),
    ("c_area.log", "c_mos_1v8",   7.876883e-13, "F", "MOS, 100 um^2, gate at 1.8 V"),
    ("c_area.log", "c_mos_0v0",   2.207182e-13, "F", "MOS, same device, gate at 0 V"),
    ("c_moscap_cv.log", "c_000mv", 2.207182e-13, "F", "MOS C-V, 0.0 V"),
    ("c_moscap_cv.log", "c_180mv", 7.876883e-13, "F", "MOS C-V, 1.8 V"),
    ("corners_tt.log", "r_a",     3.550443e3, "ohm", "R_A, typical corner"),
    ("corners_ll.log", "r_a",     3.106637e3, "ohm", "R_A, low corner"),
    ("corners_hh.log", "r_a",     3.994248e3, "ohm", "R_A, high corner"),
    ("corners_tt.log", "ratio",   3.680396,   "",    "R_B/R_A, typical"),
    ("corners_ll.log", "ratio",   3.680396,   "",    "R_B/R_A, low -- SAME"),
    ("corners_hh.log", "ratio",   3.680396,   "",    "R_B/R_A, high -- SAME"),
    ("corners_tt.log", "divider", 0.3845828,  "V",   "divider output, typical"),
    ("corners_ll.log", "divider", 0.3845828,  "V",   "divider output, low -- SAME"),
    ("corners_hh.log", "divider", 0.3845828,  "V",   "divider output, high -- SAME"),
    ("corners_tt.log", "f3db",    2.15410e8,  "Hz",  "RC corner, typical"),
    ("corners_ll.log", "f3db",    2.82935e8,  "Hz",  "RC corner, low"),
    ("corners_hh.log", "f3db",    1.69052e8,  "Hz",  "RC corner, high"),
    ("l_spiral.log", "l_1khz", 9.91271e-09, "H", "ind_05_220 inductance at 1 kHz"),
    ("l_spiral.log", "q_1khz", 1.50516e-05, "",  "ind_05_220 Q at 1 kHz"),
    ("l_spiral.log", "r_1khz", 4.13800,     "ohm", "ind_05_220 series resistance"),
    ("l_spiral.log", "q_1ghz", 1.16534e+01, "",  "ind_05_220 Q at 1 GHz"),
    ("l_spiral.log", "qpeak_05_220", 1.27198e+01, "", "best Q ind_05_220 ever reaches"),
    ("l_spiral.log", "fpeak_05_220", 1.38835e+09, "Hz", "  ...and the frequency it needs"),
    ("l_spiral.log", "srf_05_220", 3.52777e+09, "Hz", "self-resonance: it stops inducting"),
    ("l_spiral.log", "qpeak_03_90", 2.11268e+01, "", "best Q of the smallest spiral"),
    ("l_spiral.log", "l1_1khz", 1.52074e-09, "H", "ind_03_90 inductance"),
]

# mismatch: (label, expected sigma/mean in percent)
MC_EXPECT = {
    "A (1x1)":      2.7930,
    "B (1x1)":      2.8775,
    "C (10x10)":    0.3045,
    "D (10x10)":    0.3479,
    "A/B ratio":    3.7695,
    "C/D ratio":    0.4496,
}
MC_TOL = 0.02   # percentage points


def grab(path, var):
    """Return the last value ngspice printed for `var` in this log."""
    if not path.exists():
        return None
    pat = re.compile(r"^\s*" + re.escape(var)
                     + r"\s*=\s*([-+0-9.eE]+)(?:\s|$)")
    hit = None
    for line in path.read_text(errors="replace").splitlines():
        m = pat.match(line)
        if m:
            hit = float(m.group(1))
    return hit


def main(argv):
    argv = list(argv)
    # --mc: only the Monte Carlo section, for `make mismatch` on its own.
    mc_only = "--mc" in argv
    if mc_only:
        argv.remove("--mc")
    res = Path(argv[1] if len(argv) > 1 else "results")
    fails, missing = [], []

    if not mc_only:
        print("=" * 70)
        print(" AD102 passives-decks -- checking your numbers against the reference run")
        print("=" * 70)

    for logname, var, want, unit, what in ([] if mc_only else CHECKS):
        got = grab(res / logname, var)
        if got is None:
            missing.append((logname, var))
            print(f"  MISSING  {var:<12} ({logname})  -- {what}")
            continue
        rel = abs(got - want) / abs(want) if want else abs(got - want)
        ok = rel <= TOL
        mark = "ok  " if ok else "FAIL"
        u = f" {unit}" if unit else ""
        print(f"  {mark}     {var:<12} {got: .6e}{u:<5}  (reference {want: .6e})   {what}")
        if not ok:
            fails.append((var, got, want))

    # ---- mismatch statistics -------------------------------------------------
    mclog = res / "mismatch.log"
    if not mc_only:
        print("-" * 70)
    if not mclog.exists():
        missing.append(("mismatch.log", "*"))
        print("  MISSING  mismatch.log")
    else:
        cols = {}
        for line in mclog.read_text(errors="replace").splitlines():
            m = re.match(r"^\s*1m/\(-i\((v[abcd])\)\)\s*=\s*([-+0-9.eE]+)\s*$", line)
            if m:
                cols.setdefault(m.group(1), []).append(float(m.group(2)))
        need = ("va", "vb", "vc", "vd")
        if not all(k in cols and len(cols[k]) >= 2 for k in need):
            print("  FAIL     mismatch.log has no usable Monte Carlo data")
            fails.append(("mismatch", 0, 0))
        else:
            a, b, c, d = (cols[k] for k in need)
            n = min(map(len, (a, b, c, d)))
            print(f"  Monte Carlo: {n} runs, seed 12345")
            series = {
                "A (1x1)": a[:n], "B (1x1)": b[:n],
                "C (10x10)": c[:n], "D (10x10)": d[:n],
                "A/B ratio": [x / y for x, y in zip(a[:n], b[:n])],
                "C/D ratio": [x / y for x, y in zip(c[:n], d[:n])],
            }
            for label, vals in series.items():
                sd = 100 * statistics.stdev(vals) / statistics.mean(vals)
                want = MC_EXPECT[label]
                ok = abs(sd - want) <= MC_TOL
                print(f"  {'ok  ' if ok else 'FAIL'}     sigma/mean {label:<12}"
                      f" {sd:7.4f} %   (reference {want:7.4f} %)")
                if not ok:
                    fails.append((label, sd, want))
            impr = ((statistics.stdev(series["A/B ratio"])
                     / statistics.mean(series["A/B ratio"]))
                    / (statistics.stdev(series["C/D ratio"])
                       / statistics.mean(series["C/D ratio"])))
            print(f"           100x the area bought {impr:.2f}x better matching"
                  f"   (Pelgrom's square root of 100 would be 10x)")

    if not mc_only:
        print("=" * 70)
    if missing:
        print(f"  {len(missing)} value(s) never appeared in a log.")
        print("  Run `make` from labs/passives-decks/ inside the workbench first.")
        return 2
    if fails:
        print(f"  FAIL -- {len(fails)} value(s) disagree with the reference run.")
        print("  These decks are deterministic. A disagreement means the model")
        print("  library moved, not that you did something wrong. Check")
        print("  `ngspice -v` says 46 and that /foss/pdks/sky130A exists.")
        return 1
    if not mc_only:
        print("  PASS -- every number matches the reference run.")
        print("  The guide pages quote exactly these values; you can now read them")
        print("  knowing the arithmetic on the page is the arithmetic on your screen.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
