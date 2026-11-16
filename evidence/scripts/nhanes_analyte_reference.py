#!/usr/bin/env python3
"""Reference value of each PhenoAge analyte for a same-age, same-sex person (system ages, engine 1.1.1).

Same sample, weights and smoother as the PhenoAge reference curve (nhanes_phenoage.py): NHANES cycles with CRP,
MEC weights, weighted quadratic in age by sex, tabulated at ages 20..85 in steps of 5. Because PhenoAge is linear in
its analytes and weighted least squares is linear in the response, these nine curves recombine to the existing
reference PhenoAge curve; the check at the end prints the largest difference. Descriptive statistics only: nothing
is fitted against an outcome.

Usage: nhanes_analyte_reference.py <nhanes_analysis.parquet> <skill data dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from nhanes_phenoage import B, COEF, INTERCEPT, OFFSET, phenoage, wls_poly

src, skill_data = Path(sys.argv[1]), Path(sys.argv[2])
d = pd.read_parquet(src)
need = ["albumin_gL", "creat_umol", "glucose_mmol", "crp_mgdl_h", "lymph_pct", "mcv", "rdw", "alp", "wbc"]
d = d.dropna(subset=need + ["age", "years", "died", "wt_mec"]).copy()
pos_min = d.loc[d.crp_mgdl_h > 0, "crp_mgdl_h"].min()
d["lncrp"] = np.log(d.crp_mgdl_h.clip(lower=pos_min / 2))
d["phenoage"] = phenoage(d)
d = d[np.isfinite(d.phenoage)]
ages = list(range(20, 86, 5))
names = {"albumin_gL": "albumin", "creat_umol": "creatinine", "glucose_mmol": "glucose", "lncrp": "ln_crp_mgdl",
         "lymph_pct": "lymph_pct", "mcv": "mcv", "rdw": "rdw", "alp": "alp", "wbc": "wbc"}
out = {"source": "NHANES 1999-2010 and 2015-2018 (CDC/NCHS), MEC-weighted quadratic in age by sex; same sample and smoother as "
                 "phenoage_reference.json (evidence/scripts/nhanes_analyte_reference.py). Units: albumin g/L, creatinine umol/L, "
                 "glucose mmol/L, ln CRP (mg/dL), lymphocyte %, MCV fL, RDW %, ALP U/L, WBC 10^9/L",
       "ages": ages, "fit": {}, "n": {}}
ref = json.loads((skill_data / "phenoage_reference.json").read_text(encoding="utf-8"))
worst = 0.0
for sex, code in (("M", 1), ("F", 2)):
    g = d[d.sex == code]
    out["n"][sex] = int(len(g))
    out["fit"][sex] = {}
    recomb = np.array([OFFSET + (np.log(0.0055305 * 1.51714 / 0.007692696) + INTERCEPT + COEF["age"] * a) / B for a in ages])
    for col, key in names.items():
        beta = wls_poly(g.age.values, g[col].values, g.wt_mec.values, 2)
        vals = [float(np.polyval(beta, a)) for a in ages]
        out["fit"][sex][key] = [round(v, 5) for v in vals]
        recomb = recomb + COEF[col] * np.array(vals) / B
    diff = np.abs(recomb - np.array(ref["fit"][sex]["phenoage"]))
    worst = max(worst, float(diff.max()))
    print(sex, "n", len(g), "max |recombined - reference PhenoAge| over the age grid:", round(float(diff.max()), 4))
out["check_max_abs_diff_vs_phenoage_reference_years"] = round(worst, 4)
(skill_data / "phenoage_analyte_reference.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", skill_data / "phenoage_analyte_reference.json")
