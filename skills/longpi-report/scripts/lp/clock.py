"""Clock layer: Levine PhenoAge from routine blood tests, its reference curve and noise.

PhenoAge (Levine et al., Aging 2018) is linear in its Gompertz linear predictor:

    PhenoAge = 141.50225 + (ln(0.0055305 * 1.51714 / 0.007692696) + xb) / 0.090165
             = 141.50225 + (0.08679 + xb) / 0.090165

so each biomarker moves PhenoAge by coefficient / 0.090165 years per unit, and
within-person biological variation propagates analytically.

"PhenoAge gap" here is PhenoAge minus the PhenoAge expected for a reference
person of the same age and sex (NHANES 1999-2010 and 2015-2018, the cycles with CRP;
see evidence/), which is how
phenotypic-age acceleration is defined in the validation literature.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Levine 2018 / BioAge phenoage_calc.R (orig = TRUE). Units: albumin g/L,
# creatinine umol/L, glucose mmol/L, ln CRP (mg/dL), lymphocyte %, MCV fL,
# RDW %, ALP U/L, WBC 10^9/L, age years.
INTERCEPT = -19.90667
COEF = {
    "albumin": -0.03359355,
    "creatinine": 0.009506491,
    "glucose": 0.1953192,
    "ln_crp_mgdl": 0.09536762,
    "lymph_pct": -0.01199984,
    "mcv": 0.02676401,
    "rdw": 0.3306156,
    "alp": 0.001868778,
    "wbc": 0.05542406,
    "age": 0.08035356,
}
GAMMA = 0.007692696
MORT_NUM = -1.51714
B_AGE = 0.090165
OFFSET = 141.50225
LOG_NUM = -0.0055305
INPUTS = ("albumin", "creatinine", "glucose", "crp", "lymph_pct", "mcv", "rdw", "alp", "wbc")


@lru_cache(maxsize=1)
def P_CLOCK() -> dict:
    import json as _json
    return _json.loads((DATA_DIR / "params.json").read_text(encoding="utf-8"))["clock"]


def linear_predictor(v: Dict[str, float], age: float) -> float:
    crp_mgdl = v["crp"] / 10.0  # canonical CRP is mg/L
    if crp_mgdl <= 0:
        raise ValueError("CRP must be positive")
    xb = INTERCEPT + COEF["age"] * age + COEF["ln_crp_mgdl"] * math.log(crp_mgdl)
    for k in ("albumin", "creatinine", "glucose", "lymph_pct", "mcv", "rdw", "alp", "wbc"):
        xb += COEF[k] * v[k]
    return xb


def phenoage(v: Dict[str, float], age: float) -> float:
    """Levine phenotypic age (years) from canonical-unit biomarkers."""
    xb = linear_predictor(v, age)
    mort = 1 - math.exp(MORT_NUM * math.exp(xb) / GAMMA)
    return OFFSET + math.log(LOG_NUM * math.log(1 - mort)) / B_AGE


def years_per_unit(analyte: str) -> float:
    """dPhenoAge / d(analyte) in years per canonical unit (CRP: per unit of ln CRP)."""
    if analyte == "crp":
        return COEF["ln_crp_mgdl"] / B_AGE
    return COEF[analyte] / B_AGE


@lru_cache(maxsize=1)
def _ref() -> dict:
    return json.loads((DATA_DIR / "phenoage_reference.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _bv() -> dict:
    return json.loads((DATA_DIR / "biovariation.json").read_text(encoding="utf-8"))


def reference_phenoage(age: float, sex: str) -> float:
    """Expected PhenoAge of a same-age, same-sex reference person (NHANES-weighted fit)."""
    r = _ref()["fit"][sex.upper()[:1]]
    ages, vals = r["ages"], r["phenoage"]
    if age <= ages[0]:
        return vals[0] + (age - ages[0]) * (vals[1] - vals[0]) / (ages[1] - ages[0])
    if age >= ages[-1]:
        return vals[-1] + (age - ages[-1]) * (vals[-1] - vals[-2]) / (ages[-1] - ages[-2])
    for i in range(1, len(ages)):
        if ages[i] >= age:
            w = (age - ages[i - 1]) / (ages[i] - ages[i - 1])
            return vals[i - 1] * (1 - w) + vals[i] * w
    return vals[-1]


def gap_sd_population(age: float, sex: str) -> float:
    """SD of the observed PhenoAge gap among same-age reference people."""
    r = _ref()["gap_sd"][sex.upper()[:1]]
    ages, sds = r["ages"], r["sd"]
    for i in range(1, len(ages)):
        if ages[i] >= age:
            w = (age - ages[i - 1]) / (ages[i] - ages[i - 1])
            return sds[i - 1] * (1 - w) + sds[i] * w
    return sds[-1] if age > ages[-1] else sds[0]


def noise_sd(v: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    """Within-person SD of one PhenoAge measurement (years) and each analyte's share.

    Each analyte varies by CV = sqrt(CVI^2 + CVA^2) around its value (EFLM
    Biological Variation Database); CRP enters as ln CRP, whose SD is
    sqrt(ln(1 + CV^2)).
    """
    bv = _bv()["analytes"]
    parts = {}
    for k in INPUTS:
        cv = math.hypot(bv[k]["cvi"], bv[k].get("cva", 0.0)) / 100.0
        if k == "crp":
            sd_units = math.sqrt(math.log(1 + cv * cv))
        else:
            sd_units = cv * v[k]
        parts[k] = (years_per_unit(k) * sd_units) ** 2
    tot = sum(parts.values())
    return math.sqrt(tot), {k: p / tot for k, p in parts.items()}


def kalman_gap(points: Sequence[dict], as_of_years: float, prior_sd: float, q_per_year: float) -> Tuple[float, float]:
    """Local-level filter for the true PhenoAge gap.

    points: [{"t": decimal year, "gap": observed gap, "r": observation variance}], sorted by t.
    Returns (mean, sd) of the true gap at `as_of_years`.
    """
    m, p = 0.0, prior_sd ** 2
    t_prev = None
    for pt in points:
        if t_prev is not None:
            p += q_per_year * max(0.0, pt["t"] - t_prev)
        k = p / (p + pt["r"])
        m = m + k * (pt["gap"] - m)
        p = (1 - k) * p
        t_prev = pt["t"]
    if t_prev is not None:
        p += q_per_year * max(0.0, as_of_years - t_prev)
    return m, math.sqrt(p)


def trend_posterior(points: Sequence[dict], prior_slope_sd: float, prior_level_sd: float) -> Optional[Tuple[float, float]]:
    """Bayesian straight line through observed gaps (heteroscedastic, Gaussian priors).

    Returns (slope_mean, slope_sd) in gap-years per calendar year, or None if < 2 points.
    """
    if len(points) < 2:
        return None
    t0 = sum(p["t"] for p in points) / len(points)
    # posterior precision of (level, slope) with independent zero-mean priors
    a11 = 1 / prior_level_sd ** 2
    a22 = 1 / prior_slope_sd ** 2
    a12 = 0.0
    b1 = b2 = 0.0
    for p in points:
        w = 1 / p["r"]
        x = p["t"] - t0
        a11 += w
        a12 += w * x
        a22 += w * x * x
        b1 += w * p["gap"]
        b2 += w * x * p["gap"]
    det = a11 * a22 - a12 * a12
    slope = (a11 * b2 - a12 * b1) / det
    var = a11 / det
    return slope, math.sqrt(var)


def analyte_flags(v: Dict[str, float], skip: Sequence[str] = ()) -> List[str]:
    """States that distort PhenoAge: acute inflammation (CRP mg/L), red-cell abnormalities (MCV, RDW)."""
    fl = P_CLOCK()["flags"]
    out = []
    if "crp" in v and "crp" not in skip and v["crp"] > fl["crp_acute_mg_l"]:
        out.append("acute_inflammation")
    if ("mcv" in v and "mcv" not in skip and not fl["mcv_low"] <= v["mcv"] <= fl["mcv_high"]) or \
            ("rdw" in v and "rdw" not in skip and v["rdw"] > fl["rdw_high"]):
        out.append("rbc_abnormal")
    return out
