#!/usr/bin/env python3
"""PhenoAge in NHANES 1999-2010 and 2015-2018: reference curve, gap SD, mortality calibration.

Usage: nhanes_phenoage.py <nhanes_parquet> <skill_data_dir> <results_dir>

Writes
  <skill_data_dir>/phenoage_reference.json   expected PhenoAge by age/sex + SD of the gap
  <results_dir>/phenoage_validation.json     Cox estimates, C-index, per-year HRs
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

warnings.filterwarnings("ignore")

COEF = dict(albumin_gL=-0.03359355, creat_umol=0.009506491, glucose_mmol=0.1953192, lncrp=0.09536762,
            lymph_pct=-0.01199984, mcv=0.02676401, rdw=0.3306156, alp=0.001868778, wbc=0.05542406, age=0.08035356)
INTERCEPT, GAMMA, MORT_NUM, B, OFFSET, LOGNUM = -19.90667, 0.007692696, -1.51714, 0.090165, 141.50225, -0.0055305


def phenoage(df: pd.DataFrame) -> pd.Series:
    xb = INTERCEPT + sum(COEF[k] * df[k] for k in COEF)
    mort = 1 - np.exp(MORT_NUM * np.exp(xb) / GAMMA)
    return OFFSET + np.log(LOGNUM * np.log(1 - mort)) / B


def wls_poly(x, y, w, deg=2):
    X = np.vander(x, deg + 1)
    W = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * W[:, None], y * W, rcond=None)
    return beta


def main() -> int:
    src, skill_data, results = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    results.mkdir(parents=True, exist_ok=True)
    d = pd.read_parquet(src)
    need = ["albumin_gL", "creat_umol", "glucose_mmol", "crp_mgdl_h", "lymph_pct", "mcv", "rdw", "alp", "wbc"]
    d = d.dropna(subset=need + ["age", "years", "died", "wt_mec"]).copy()
    pos_min = d.loc[d.crp_mgdl_h > 0, "crp_mgdl_h"].min()
    d["lncrp"] = np.log(d.crp_mgdl_h.clip(lower=pos_min / 2))
    d["phenoage"] = phenoage(d)
    d = d[np.isfinite(d.phenoage)]
    out_ref = {"source": "NHANES 1999-2010 and 2015-2018 (CDC/NCHS), MEC-weighted; see evidence/scripts/nhanes_phenoage.py",
               "fit": {}, "gap_sd": {}, "n": {}}
    ages = list(range(20, 86, 5))
    d["ref"] = np.nan
    for sex, code in (("M", 1), ("F", 2)):
        g = d[d.sex == code]
        beta = wls_poly(g.age.values, g.phenoage.values, g.wt_mec.values, 2)
        ref = np.polyval(beta, g.age.values)
        d.loc[g.index, "ref"] = ref
        resid2 = (g.phenoage.values - ref) ** 2
        beta_v = wls_poly(g.age.values, resid2, g.wt_mec.values, 2)
        out_ref["fit"][sex] = {"ages": ages, "phenoage": [round(float(np.polyval(beta, a)), 3) for a in ages],
                               "poly_coef_high_to_low": [float(b) for b in beta]}
        out_ref["gap_sd"][sex] = {"ages": ages, "sd": [round(float(np.sqrt(max(np.polyval(beta_v, a), 1.0))), 3) for a in ages]}
        out_ref["n"][sex] = int(len(g))
    d["gap"] = d.phenoage - d.ref
    (skill_data / "phenoage_reference.json").write_text(json.dumps(out_ref, indent=1), encoding="utf-8")

    # Mortality calibration: is one year of PhenoAge gap worth one year of age?
    d["male"] = (d.sex == 1).astype(int)
    res = {"n": int(len(d)), "deaths": int(d.died.sum()), "person_years": round(float(d.years.sum()))}
    fits = {}
    for name, cov in {"age_sex": ["age", "male"], "age_sex_gap": ["age", "male", "gap"],
                      "age_sex_phenoage": ["phenoage", "male"]}.items():
        cph = CoxPHFitter()
        cph.fit(d[["years", "died"] + cov], "years", "died")
        s = cph.summary
        fits[name] = {k: {"coef": round(float(s.loc[k, "coef"]), 5), "se": round(float(s.loc[k, "se(coef)"]), 5),
                          "hr": round(float(s.loc[k, "exp(coef)"]), 4)} for k in cov}
        fits[name]["c_index"] = round(float(cph.concordance_index_), 4)
    res["cox"] = fits
    b_age = fits["age_sex_gap"]["age"]["coef"]
    b_gap = fits["age_sex_gap"]["gap"]["coef"]
    res["gap_years_to_mortality_years"] = round(b_gap / b_age, 3)
    # per age band
    bands = {}
    for lo, hi in ((20, 39), (40, 59), (60, 85)):
        g = d[(d.age >= lo) & (d.age <= hi)]
        cph = CoxPHFitter().fit(g[["years", "died", "age", "male", "gap"]], "years", "died")
        s = cph.summary
        bands[f"{lo}-{hi}"] = {"n": int(len(g)), "deaths": int(g.died.sum()),
                               "hr_gap_per_year": round(float(s.loc["gap", "exp(coef)"]), 4),
                               "hr_age_per_year": round(float(s.loc["age", "exp(coef)"]), 4)}
    res["by_age_band"] = bands
    # by follow-up window (does the association fade with time?)
    windows = {}
    for t0, t1 in ((0, 5), (5, 10), (10, 21)):
        g = d[d.years > t0].copy()
        g["t"] = np.minimum(g.years, t1) - t0
        g["e"] = ((g.died == 1) & (g.years <= t1)).astype(int)
        cph = CoxPHFitter().fit(g[["t", "e", "age", "male", "gap"]], "t", "e")
        s = cph.summary
        windows[f"{t0}-{t1}y"] = {"deaths": int(g.e.sum()), "hr_gap_per_year": round(float(s.loc["gap", "exp(coef)"]), 4),
                                  "se": round(float(s.loc["gap", "se(coef)"]), 5),
                                  "hr_age_per_year": round(float(s.loc["age", "exp(coef)"]), 4)}
    res["by_followup"] = windows
    res["gap_sd_overall"] = round(float(d.gap.std()), 3)
    res["corr_gap_crp"] = round(float(np.corrcoef(d.gap, d.lncrp)[0, 1]), 3)
    # Asian participants (2015-2018 only have both CRP and the Asian category)
    a = d[d.asian == 1]
    res["asian_2015_2018"] = {"n": int(len(a)), "mean_gap": round(float(np.average(a.gap, weights=a.wt_mec)), 3) if len(a) else None,
                              "deaths": int(a.died.sum())}
    (results / "phenoage_validation.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    d[["cycle", "sex", "age", "phenoage", "ref", "gap", "years", "died", "wt_mec"]].to_parquet(results.parent / "derived" / "nhanes_phenoage.parquet")
    print(json.dumps(res, indent=1))
    print(json.dumps(out_ref["fit"], indent=0)[:800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
