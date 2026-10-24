#!/usr/bin/env python3
"""What a blood test and a DNA-methylation clock add to LongPi, measured in NHANES.

Usage: nhanes_methylation.py <nhanes_parquet> <phenoage_parquet> <dnam_sas7bdat> <skill_dir> <results_dir>

A  Blood clock missing (NHANES 1999-2018 PhenoAge sample, core domains complete):
   residual SD of the full LongPi linear predictor (with PhenoAge) given the no-blood-test predictor,
   age and sex, by age band. This is the uncertainty carried by someone without a blood test, and
   what one blood test removes.
B  Methylation clocks (NHANES 1999-2002 DNAm subsample, adults 50+, public file released 2024-07-31):
   per clock, acceleration A = clock - expected at age (sex-specific weighted linear fit), residual
   M = A - E[A | LongPi LP, age, sex]; Cox HR per year of M on top of age, sex and the LongPi LP
   (the clock's incremental information), C-index gain, likelihood-ratio test, a survey-weighted
   sensitivity (WTDN4YR, robust SE), and the spread of mean M across race/ethnicity groups.
C  How much a methylation clock tells about a missing blood clock: residual SD of the with-PhenoAge
   predictor given the no-blood predictor, with and without the clock.

Engine coefficients (params.json calibration) and NHANES's own peer norms are used exactly as in
nhanes_calibration.py, so "LP" is the engine's log hazard ratio versus same-age, same-sex peers.
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nhanes_calibration as NC  # noqa: E402

warnings.filterwarnings("ignore")
CORE = ["l_bp", "l_rhr", "l_adiposity", "l_glucose", "l_smoking"]
AGE_BANDS = [(20, 39), (40, 59), (60, 74), (75, 85)]
CLOCKS = {  # file variable -> (label, unit)
    "GrimAge2Mort": ("GrimAge2", "years"), "GrimAgeMort": ("GrimAge", "years"), "PhenoAge": ("DNAm PhenoAge", "years"),
    "DunedinPoAm": ("DunedinPoAm", "years of ageing per year"), "HorvathAge": ("Horvath", "years"),
    "HannumAge": ("Hannum", "years"), "SkinBloodAge": ("Skin & blood", "years"), "ZhangAge": ("Zhang", "years"),
    "LinAge": ("Lin", "years"), "WeidnerAge": ("Weidner", "years"), "VidalBraloAge": ("Vidal-Bralo", "years"),
    "HorvathTelo": ("DNAm telomere length", "kb"),
}
RACE = {1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White", 4: "Non-Hispanic Black", 5: "Other (incl. Asian)"}


def wls(y, X, w):
    """Weighted least squares: coefficients, residuals, weighted residual SD."""
    W = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * W[:, None], y * W, rcond=None)
    r = y - X @ beta
    return beta, r, float(np.sqrt(np.average(r ** 2, weights=w)))


def wsd(x, w):
    m = np.average(x, weights=w)
    return float(np.sqrt(np.average((x - m) ** 2, weights=w)))


def cox_fit(df, cols, weights=None):
    c = CoxPHFitter()
    if weights is None:
        c.fit(df[["years", "died"] + cols], "years", "died")
    else:
        c.fit(df[["years", "died", weights] + cols], "years", "died", weights_col=weights, robust=True)
    return c


def part_a(d, cal):
    g = d.dropna(subset=["gap"] + CORE).copy()
    g["lp_with"] = NC.score(g, cal, True)
    g["lp_without"] = NC.score(g, cal, False)
    X = np.column_stack([np.ones(len(g)), g.lp_without, g.age, g.male])
    beta, r, sd_all = wls(g.lp_with.values, X, g.wt_mec.values)
    g["resid"] = r
    bands = []
    for lo, hi in AGE_BANDS:
        s = g[g.age.between(lo, hi)]
        bands.append({"age_lo": lo, "age_hi": hi, "n": int(len(s)), "sd": round(wsd(s.resid.values, s.wt_mec.values), 4),
                      "sd_lp_with": round(wsd(s.lp_with.values, s.wt_mec.values), 4),
                      "sd_lp_without": round(wsd(s.lp_without.values, s.wt_mec.values), 4)})
    # does the residual carry mortality information? (it should: it is what the blood clock adds)
    base = cox_fit(g, ["age", "male", "lp_without"])
    full = cox_fit(g.assign(resid_std=g.resid / sd_all), ["age", "male", "lp_without", "resid_std"])
    s = full.summary
    return {"n": int(len(g)), "deaths": int(g.died.sum()), "regression": {"intercept": float(beta[0]), "lp_without": float(beta[1]),
            "age": float(beta[2]), "male": float(beta[3])}, "sd_overall": round(sd_all, 4), "by_age": bands,
            "cox_resid_per_sd": {"coef": float(s.loc["resid_std", "coef"]), "se": float(s.loc["resid_std", "se(coef)"])},
            "c_without": float(base.concordance_index_), "c_with_resid": float(full.concordance_index_)}


def part_b(d, cal, dnam):
    m = d.join(dnam.rename(columns={"PhenoAge": "DNAmPhenoAge"}), how="inner")
    m = m[(m.WTDN4YR > 0) & m.GrimAge2Mort.notna() & m.years.notna() & (m.age >= 50)]
    m = m.dropna(subset=["gap"] + CORE).copy()
    m["lp"] = NC.score(m, cal, True)
    m["lp_without"] = NC.score(m, cal, False)
    w = m.WTDN4YR.values
    base = cox_fit(m, ["age", "male", "lp"])
    out = {"n": int(len(m)), "deaths": int(m.died.sum()), "median_follow_up_years": float(m.years.median()),
           "age_range": [float(m.age.min()), float(m.age.max())],
           "lp_coef_in_base": float(base.summary.loc["lp", "coef"]), "lp_se_in_base": float(base.summary.loc["lp", "se(coef)"]),
           "c_base": float(base.concordance_index_), "clocks": {}}
    for var, (label, unit) in CLOCKS.items():
        col = "DNAmPhenoAge" if var == "PhenoAge" else var
        k = m.dropna(subset=[col]).copy()
        wk = k.WTDN4YR.values
        ref = {}
        acc = np.zeros(len(k))
        for sex, code in (("M", 1), ("F", 2)):
            sel = (k.sex == code).values
            b, r, _ = wls(k[col].values[sel], np.column_stack([np.ones(sel.sum()), k.age.values[sel]]), wk[sel])
            ref[sex] = [round(float(b[0]), 4), round(float(b[1]), 5)]
            acc[sel] = r
        k["acc"] = acc
        sd_a = wsd(acc, wk)
        X = np.column_stack([np.ones(len(k)), k.lp, k.age, k.male])
        bm, resid, sd_m = wls(acc, X, wk)
        k["m_std"] = resid / sd_m
        k["a_std"] = acc / sd_a
        alone = cox_fit(k, ["age", "male", "a_std"])
        full = cox_fit(k, ["age", "male", "lp", "m_std"])
        base_k = cox_fit(k, ["age", "male", "lp"])
        wfull = cox_fit(k.assign(w=wk), ["age", "male", "lp", "m_std"], weights="w")
        sf, sw, sa = full.summary, wfull.summary, alone.summary
        r2 = 1 - sd_m ** 2 / sd_a ** 2
        groups = {}
        for code, name in RACE.items():
            s = k.race1 == code
            if s.sum() >= 30:
                groups[name] = {"n": int(s.sum()), "mean_m_years": round(float(np.average(resid[s.values], weights=wk[s.values])), 3)}
        gm = np.array([v["mean_m_years"] for v in groups.values()])
        out["clocks"][label] = {
            "variable": var, "unit": unit, "n": int(len(k)), "deaths": int(k.died.sum()),
            "reference": ref, "sd_acceleration": round(sd_a, 4),
            "resid_on": {"intercept": round(float(bm[0]), 4), "lp": round(float(bm[1]), 4), "age": round(float(bm[2]), 5), "male": round(float(bm[3]), 4)},
            "r2_explained_by_lp": round(float(r2), 4), "sd_resid": round(sd_m, 4),
            "hr_per_sd_alone": float(np.exp(sa.loc["a_std", "coef"])), "se_alone": float(sa.loc["a_std", "se(coef)"]),
            "beta_per_sd_resid": float(sf.loc["m_std", "coef"]), "se_per_sd_resid": float(sf.loc["m_std", "se(coef)"]),
            "hr_per_sd_resid": float(np.exp(sf.loc["m_std", "coef"])),
            "p_resid": float(sf.loc["m_std", "p"]),
            "beta_per_unit_resid": float(sf.loc["m_std", "coef"]) / sd_m, "se_per_unit_resid": float(sf.loc["m_std", "se(coef)"]) / sd_m,
            "lp_coef_with_clock": float(sf.loc["lp", "coef"]),
            "c_base": float(base_k.concordance_index_), "c_with_clock": float(full.concordance_index_),
            "lr_chi2": float(2 * (full.log_likelihood_ - base_k.log_likelihood_)),
            "weighted_beta_per_sd_resid": float(sw.loc["m_std", "coef"]), "weighted_se": float(sw.loc["m_std", "se(coef)"]),
            "race_groups": groups, "race_group_sd_years": round(float(gm.std()), 3) if len(gm) > 1 else None,
        }
    # C: methylation as partial substitute for a missing blood test (GrimAge2)
    acc = out["clocks"]["GrimAge2"]
    g2 = m.copy()
    g2["acc"] = g2.GrimAge2Mort - np.where(g2.sex == 1, acc["reference"]["M"][0] + acc["reference"]["M"][1] * g2.age,
                                          acc["reference"]["F"][0] + acc["reference"]["F"][1] * g2.age)
    X0 = np.column_stack([np.ones(len(g2)), g2.lp_without, g2.age, g2.male])
    X1 = np.column_stack([X0, g2.acc])
    _, _, sd0 = wls(g2.lp.values, X0, w)
    b1, _, sd1 = wls(g2.lp.values, X1, w)
    out["blood_clock_given_methylation"] = {"sd_without_methylation": round(sd0, 4), "sd_with_grimage2": round(sd1, 4),
                                            "coef_grimage2_acc": round(float(b1[4]), 5)}
    return out


def main() -> int:
    src, pheno_src, dnam_src, skill_dir, results = map(Path, sys.argv[1:6])
    sys.path.insert(0, str(skill_dir / "scripts"))
    from lp import domains as DM  # noqa: E402
    cal = json.loads((skill_dir / "data" / "params.json").read_text(encoding="utf-8"))["calibration"]
    d = NC.prepare(src, pheno_src)
    norms = NC.build_norms(d)
    d = d.join(NC.lhr_columns(d, DM, norms))
    d = NC.add_gap_terms(d)
    dnam = pd.read_sas(dnam_src, format="sas7bdat", encoding="latin-1")
    dnam["SEQN"] = dnam.SEQN.astype(int)
    dnam = dnam.set_index("SEQN")
    res = {"source": "NHANES 1999-2018 with mortality follow-up to 2019; DNAm epigenetic biomarkers 1999-2002 (dnmepi, released 2024-07-31)",
           "blood_clock_residual": part_a(d, cal), "methylation": part_b(d, cal, dnam)}
    (results / "nhanes_methylation.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    a = res["blood_clock_residual"]
    print("A blood clock residual:", {k: a[k] for k in ("n", "deaths", "sd_overall", "c_without", "c_with_resid")}, a["regression"])
    for b in a["by_age"]:
        print("   ", b)
    mm = res["methylation"]
    print("B methylation sample:", {k: mm[k] for k in ("n", "deaths", "median_follow_up_years", "age_range", "lp_coef_in_base", "c_base")})
    print(f"   {'clock':22s} {'HRsd alone':>10s} {'R2 by LP':>8s} {'sd_res':>7s} {'HRsd resid':>10s} {'p':>9s} {'dC':>7s} {'LR':>6s} {'wHR':>6s} {'raceSD':>6s}")
    for name, c in mm["clocks"].items():
        print(f"   {name:22s} {c['hr_per_sd_alone']:10.3f} {c['r2_explained_by_lp']:8.3f} {c['sd_resid']:7.3f} {c['hr_per_sd_resid']:10.3f} "
              f"{c['p_resid']:9.2e} {c['c_with_clock'] - c['c_base']:7.4f} {c['lr_chi2']:6.1f} {np.exp(c['weighted_beta_per_sd_resid']):6.3f} "
              f"{c['race_group_sd_years'] if c['race_group_sd_years'] is not None else float('nan'):6.3f}")
    print("C", mm["blood_clock_given_methylation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
