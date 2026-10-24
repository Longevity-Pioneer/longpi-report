#!/usr/bin/env python3
"""Calibrate and externally validate LongPi in NHANES 1999-2018 (mortality follow-up to 2019).

Usage: nhanes_calibration.py <nhanes_parquet> <phenoage_parquet> <skill_dir> <results_dir>

Uses the engine's own domain code (skills/longpi-report/scripts/lp/domains.py) and parameters
(data/params.json). Population norms are NHANES's own: "peers" here are US adults of the same
age and sex, exactly as the engine uses Chinese peers for Chinese users.

Steps
  1  per-domain transport check: slope of the literature log HR, age/sex adjusted (ideal 1)
  2  PhenoAge gap calibration: piecewise-linear log hazard, knots at -5 and +5 years
  3  joint recalibration -> domain coefficients c_d with and without PhenoAge; causal domains fixed at 1
  4  temporal validation of the final configuration: fit on 1999-2008, test on 2009-2018
  5  writes the calibration block for params.json and a summary for the report's methods tab
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

warnings.filterwarnings("ignore")
BANDS = [(20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 85)]
KNOTS = (-5.0, 5.0)
CAUSAL = {"bp", "lipid", "smoking", "alcohol"}
PRIOR_SD = 0.30   # prior on c_d = 1 for domains NHANES cannot calibrate well


def wmean_sd(x, w):
    m = np.average(x, weights=w)
    return float(m), float(np.sqrt(np.average((x - m) ** 2, weights=w)))


def build_norms(d):
    cont = {"sbp": "sbp_office", "rhr": "rhr_clinic", "ldl": "ldl", "bmi": "bmi", "sleep": "sleep_selfreport_h",
            "vo2max": "vo2max", "grip": "grip_kg"}
    cats = {"smoking": ("smoke3", ["never", "former", "current"]), "glycemic": ("glycemic_status", ["normal", "prediabetes", "diabetes"])}
    out = {"markers": {}}
    for key, col in cont.items():
        out["markers"][key] = {}
        for sex, code in (("M", 1), ("F", 2)):
            rows = []
            for lo, hi in BANDS:
                g = d[(d.sex == code) & d.age.between(lo, hi) & d[col].notna()]
                if len(g) < 30:
                    g = d[(d.sex == code) & d[col].notna()]
                m, s = wmean_sd(g[col].values, g.wt_mec.values)
                rows.append({"age_lo": lo, "age_hi": hi, "mean": m, "sd": s})
            out["markers"][key][sex] = rows
    for key, (col, levels) in cats.items():
        out["markers"][key] = {}
        for sex, code in (("M", 1), ("F", 2)):
            rows = []
            for lo, hi in BANDS:
                g = d[(d.sex == code) & d.age.between(lo, hi) & d[col].isin(levels)]
                tot = g.wt_mec.sum()
                rows.append({"age_lo": lo, "age_hi": hi, "p": {l: float(g.loc[g[col] == l, "wt_mec"].sum() / tot) for l in levels}})
            out["markers"][key][sex] = rows
    return out


def lhr_columns(d, DM, norms):
    out = pd.DataFrame(index=d.index)
    for sp in DM.domain_specs():
        col = sp["input"]
        if col not in d.columns:
            continue
        p = DM.draw_params(sp, None)
        vals = np.full(len(d), np.nan)
        cache = {}
        for i, (x, sex, age) in enumerate(zip(d[col].values, d.sex.values, d.age.values)):
            if sp["shape"] == "categorical":
                if not isinstance(x, str):
                    continue
                xx = "pop:" + x
            else:
                if not np.isfinite(x):
                    continue
                xx = float(x)
            s = "M" if sex == 1 else "F"
            band = next(j for j, (lo, hi) in enumerate(BANDS) if lo <= age <= hi)
            if (s, band) not in cache:
                cache[(s, band)] = DM.log_mean_exp_pop(sp, p, s, BANDS[band][0], norms)
            vals[i] = DM.f_raw(sp, p, xx) - cache[(s, band)]
        out[f"l_{sp['id']}"] = vals
    return out


def add_gap_terms(d):
    g = d.gap
    d["g_lo"] = np.minimum(g - KNOTS[0], 0.0)
    d["g_mid"] = g.clip(KNOTS[0], KNOTS[1])
    d["g_hi"] = np.maximum(g - KNOTS[1], 0.0)
    return d


def cox(df, cols, dur="years", ev="died"):
    c = CoxPHFitter()
    c.fit(df[[dur, ev] + cols], dur, ev)
    s = c.summary
    r = {k: {"coef": float(s.loc[k, "coef"]), "se": float(s.loc[k, "se(coef)"]),
             "lo": float(s.loc[k, "coef lower 95%"]), "hi": float(s.loc[k, "coef upper 95%"])} for k in cols}
    r["_c"], r["_n"], r["_deaths"] = float(c.concordance_index_), int(len(df)), int(df[ev].sum())
    return r


def shrink(est, se, prior=1.0, prior_sd=PRIOR_SD):
    """Normal-normal combination of the NHANES estimate with a literature prior (c = 1)."""
    w1, w2 = 1 / se ** 2, 1 / prior_sd ** 2
    m = (est * w1 + prior * w2) / (w1 + w2)
    return m, (w1 + w2) ** -0.5


def prepare(src, pheno_src):
    d = pd.read_parquet(src).join(pd.read_parquet(pheno_src)[["gap", "phenoage"]], how="left")
    d["rhr_clinic"] = d.pulse60.where(d.pulse60.between(35, 160))
    d["sbp_office"] = d.sbp
    d["ldl"] = d.ldl * 0.02586
    d["sleep_selfreport_h"] = d.sleep_h.where(d.sleep_h.between(2, 16))
    d["grip_kg"] = d.grip_max
    d["smoke3"] = d.smoke.where(d.smoke != "")
    d["smoking_status"] = d["smoke3"]
    dm = (d.hba1c >= 6.5) | (d.diq010 == 1)
    pre = (d.hba1c >= 5.7) & (d.hba1c < 6.5) & ~dm
    d["glycemic_status"] = np.where(d.hba1c.isna() & (d.diq010 != 1), None, np.where(dm, "diabetes", np.where(pre, "prediabetes", "normal")))
    return d


def final_coefs(d, prefix=""):
    """Coefficients for the engine, estimated on data frame d."""
    res = {}
    core = ["l_bp", "l_rhr", "l_adiposity", "l_glucose", "l_smoking"]
    g = d.dropna(subset=["gap"] + core)
    j = cox(g, ["age", "male", "g_lo", "g_mid", "g_hi"] + core)
    res["joint_with_clock"] = j
    gs = d.dropna(subset=["gap", "l_sleep"] + core)
    js = cox(gs, ["age", "male", "g_lo", "g_mid", "g_hi"] + core + ["l_sleep"])
    res["joint_with_clock_sleep"] = js
    w = d.dropna(subset=core)
    jw = cox(w, ["age", "male"] + core)
    res["joint_without_clock"] = jw
    ws = d.dropna(subset=core + ["l_sleep"])
    jws = cox(ws, ["age", "male"] + core + ["l_sleep"])
    res["joint_without_clock_sleep"] = jws
    crf = d.dropna(subset=["gap", "l_crf"] + core)
    res["crf_with_clock"] = cox(crf, ["age", "male", "g_mid"] + core + ["l_crf"]) if len(crf) > 500 else None
    crfw = d.dropna(subset=["l_crf"] + core)
    res["crf_without_clock"] = cox(crfw, ["age", "male"] + core + ["l_crf"]) if len(crfw) > 500 else None
    grip = d.dropna(subset=["l_muscle"] + core)
    res["grip_without_clock"] = cox(grip, ["age", "male"] + core + ["l_muscle"]) if len(grip) > 500 else None
    ldl = d.dropna(subset=["gap", "l_lipid"] + core)
    res["ldl_with_clock"] = cox(ldl, ["age", "male", "g_mid"] + core + ["l_lipid"]) if len(ldl) > 500 else None

    def est(r, k):
        return (r[k]["coef"], r[k]["se"]) if r is not None else (None, None)

    def overlap(r, k):
        """Overlap with PhenoAge or other domains: use the joint NHANES estimate (a discount)."""
        e, se = est(r, k)
        return {"value": round(max(e, 0.0), 4), "sd": round(se, 4), "rule": "overlap", "nhanes": e,
                "basis": f"NHANES joint estimate {e:.2f} (SE {se:.2f}): overlap discount"}

    def capped(r, k):
        """Literature effect, discounted if NHANES says it transports weakly, never inflated."""
        e, se = est(r, k)
        if e is None:
            return {"value": 1.0, "sd": PRIOR_SD, "rule": "literature", "nhanes": None, "basis": "literature (not estimable in NHANES)"}
        m, sd = shrink(e, se)
        if m >= 1.0:
            return {"value": 1.0, "sd": PRIOR_SD, "rule": "literature", "nhanes": e,
                    "basis": f"literature; NHANES {e:.2f} (SE {se:.2f}) is at least as strong, not used to inflate"}
        return {"value": round(m, 4), "sd": round(sd, 4), "rule": "discounted", "nhanes": e,
                "basis": f"NHANES {e:.2f} (SE {se:.2f}) combined with literature prior 1 (SD {PRIOR_SD})"}

    def causal(r=None, k=None):
        e = est(r, k)[0] if r is not None else None
        return {"value": 1.0, "sd": 0.1, "rule": "causal", "nhanes": e, "basis": "causal effect size (trials or genetics), coefficient 1"}

    wc = {"rhr": overlap(j, "l_rhr"), "glucose": overlap(j, "l_glucose"), "adiposity": overlap(j, "l_adiposity"),
          "sleep": capped(js, "l_sleep"), "crf": capped(res["crf_with_clock"], "l_crf"), "muscle": capped(None, None),
          "bp": causal(j, "l_bp"), "smoking": causal(j, "l_smoking"), "lipid": causal(res["ldl_with_clock"], "l_lipid"), "alcohol": causal()}
    woc = {"rhr": capped(jw, "l_rhr"), "glucose": overlap(jw, "l_glucose"), "adiposity": overlap(jw, "l_adiposity"),
           "sleep": capped(jws, "l_sleep"), "crf": capped(res["crf_without_clock"], "l_crf"), "muscle": capped(res["grip_without_clock"], "l_muscle"),
           "bp": causal(jw, "l_bp"), "smoking": causal(jw, "l_smoking"), "lipid": causal(), "alcohol": causal()}
    gap = {"knots": list(KNOTS), "slopes": [round(j[k]["coef"], 5) for k in ("g_lo", "g_mid", "g_hi")],
           "slopes_sd": [round(j[k]["se"], 5) for k in ("g_lo", "g_mid", "g_hi")], "b_age_nhanes": round(j["age"]["coef"], 5)}
    return {"gap": gap, "with_clock": wc, "without_clock": woc}, res


def score(d, cal, with_clock):
    """Engine linear predictor (log HR vs peers) with coefficients `cal`."""
    cs = cal["with_clock" if with_clock else "without_clock"]
    lp = np.zeros(len(d))
    if with_clock:
        s_lo, s_mid, s_hi = cal["gap"]["slopes"]
        lp += s_lo * d.g_lo.values + s_mid * d.g_mid.values + s_hi * d.g_hi.values
    for k, c in cs.items():
        col = f"l_{k}"
        if col in d:
            lp += c["value"] * d[col].fillna(0.0).values   # missing domain -> neutral (0) as in the engine's expectation
    return lp


def validate(dev, val, with_clock, label):
    cal, _ = final_coefs(dev)
    b = cal["gap"]["b_age_nhanes"]
    v = val.copy()
    v["lp_gap"] = score(v, cal, with_clock) / b
    base = cox(v, ["age", "male"])
    r = cox(v, ["age", "male", "lp_gap"])
    out = {"label": label, "n": r["_n"], "deaths": r["_deaths"], "hr_per_longpi_year": float(np.exp(r["lp_gap"]["coef"])),
           "hr_per_age_year": float(np.exp(r["age"]["coef"])), "slope_ratio": r["lp_gap"]["coef"] / r["age"]["coef"],
           "slope_ratio_lo": r["lp_gap"]["lo"] / r["age"]["coef"], "slope_ratio_hi": r["lp_gap"]["hi"] / r["age"]["coef"],
           "c_age_sex": base["_c"], "c_with_longpi": r["_c"], "gap_sd": float(v.lp_gap.std())}
    v["dec"] = pd.qcut(v.lp_gap, 10, labels=False, duplicates="drop")
    dm = pd.get_dummies(v.dec, prefix="d").astype(float)
    ref = "d_4"
    cols = [c for c in dm.columns if c != ref]
    rr = cox(pd.concat([v[["years", "died", "age", "male"]], dm[cols]], axis=1), ["age", "male"] + cols)
    means = v.groupby("dec").lp_gap.mean()
    out["deciles"] = [{"decile": int(k) + 1, "mean_gap": float(means[k]),
                       "pred": float((means[k] - means[4]) * rr["age"]["coef"]),
                       "obs": 0.0 if f"d_{k}" == ref else rr[f"d_{k}"]["coef"],
                       "lo": 0.0 if f"d_{k}" == ref else rr[f"d_{k}"]["lo"],
                       "hi": 0.0 if f"d_{k}" == ref else rr[f"d_{k}"]["hi"]} for k in sorted(means.index)]
    return out


def main() -> int:
    src, pheno_src, skill_dir, results = map(Path, sys.argv[1:5])
    sys.path.insert(0, str(skill_dir / "scripts"))
    from lp import domains as DM  # noqa: E402
    d = prepare(src, pheno_src)
    norms = build_norms(d)
    d = d.join(lhr_columns(d, DM, norms))
    d = add_gap_terms(d)
    res = {"n_total": int(len(d)), "deaths_total": int(d.died.sum())}

    # 1 transport check per domain
    q1 = {}
    for sp in DM.domain_specs():
        col = f"l_{sp['id']}"
        if col not in d or d[col].notna().sum() < 500:
            continue
        g = d.dropna(subset=[col])
        r = cox(g, ["age", "male", col])
        q1[sp["id"]] = {"n": r["_n"], "deaths": r["_deaths"], "slope": r[col]["coef"], "lo": r[col]["lo"], "hi": r[col]["hi"]}
        if g.gap.notna().sum() > 500:
            r2 = cox(g.dropna(subset=["gap"]), ["age", "male", "g_lo", "g_mid", "g_hi", col])
            q1[sp["id"]].update({"slope_adj_phenoage": r2[col]["coef"], "lo_adj": r2[col]["lo"], "hi_adj": r2[col]["hi"]})
    res["q1_transport"] = q1

    # 2-3 final coefficients on all data
    cal, fits = final_coefs(d)
    res["calibration"] = cal
    res["fits"] = {k: ({kk: vv for kk, vv in v.items()} if v else None) for k, v in fits.items()}

    # 4 temporal validation
    dev, val = d[d.cycle <= 2007], d[d.cycle >= 2009]
    res["validation"] = {
        "with_clock": validate(dev.dropna(subset=["gap"]), val.dropna(subset=["gap"]), True, "PhenoAge + domains"),
        "without_clock": validate(dev, val, False, "domains only (no PhenoAge)"),
    }
    # comparators on the with-clock validation sample
    vv = val.dropna(subset=["gap"]).copy()
    b = res["calibration"]["gap"]["b_age_nhanes"]
    comps = {}
    vv["demo"] = vv.gap + 0.5 * vv[["l_bp", "l_rhr", "l_adiposity", "l_glucose"]].fillna(0).sum(axis=1) / 0.09
    vv["pheno_only"] = vv.gap
    for name in ("demo", "pheno_only"):
        r = cox(vv, ["age", "male", name])
        comps[name] = {"hr_per_year": float(np.exp(r[name]["coef"])), "slope_ratio": r[name]["coef"] / r["age"]["coef"], "c": r["_c"]}
    res["validation"]["comparators"] = comps
    (results / "nhanes_calibration.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({"q1": q1, "calibration": cal}, indent=1))
    for k in ("with_clock", "without_clock"):
        v = res["validation"][k]
        print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "deciles"})
    print("comparators", comps)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
