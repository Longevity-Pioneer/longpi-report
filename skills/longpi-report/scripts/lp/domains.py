"""Function domains: dose-response hazard ratios normalised to same-age, same-sex peers.

Each domain maps one measurement x to a log hazard ratio f(x) for all-cause
mortality taken from published meta-analyses (params.json -> "domains").
The value shown to the person is normalised so that the average same-age,
same-sex Chinese adult scores zero:

    logHR(x) = f(x) - log E_pop[exp f(X)]

which keeps the population-average hazard equal to the life-table hazard.
X follows the population distribution of the marker for that age and sex
(population_norms_china.json). A domain with no measurement is drawn from that
distribution, so missing data widen the interval instead of being assumed average.

Shapes (x is first clipped to the spec's `clip` range)
  loglinear     f = beta * x                                          (beta = ln RR / per)
  hinge         f = b_lo * max(0, k_lo - x) + b_hi * max(0, x - k_hi)  (J/U shapes, flat between knots)
  categorical   f = log RR[level]; `pop_levels` hold the population categories used for
                normalisation and for people whose category is unknown ("pop:<level>")
  norm_kind "categorical_mid": a continuous person value (alcohol g/week) normalised against
                a population given as category shares with one mid-point per category
"""
from __future__ import annotations

import json
import math
import random
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Gauss-Hermite nodes and normalised weights (probabilists', 20 points; numpy hermegauss / sqrt(2 pi)):
# E[g(X)] = sum w_i g(mu + sd x_i) for X ~ N(mu, sd^2)
_GH_X = [-7.619048541679758, -6.510590157013654, -5.5787388058932015, -4.734581334046055, -3.9439673506573163,
         -3.1890148165533896, -2.458663611172368, -1.7452473208141268, -1.042945348802751, -0.346964157081356,
         0.346964157081356, 1.042945348802751, 1.7452473208141268, 2.458663611172368, 3.1890148165533896,
         3.9439673506573163, 4.734581334046055, 5.5787388058932015, 6.510590157013654, 7.619048541679758]
_GH_W = [1.2578006724379264e-13, 2.4820623623151797e-10, 6.127490259982928e-08, 4.4021210902308646e-06,
         0.00012882627996192942, 0.0018301031310804924, 0.013997837447100996, 0.06150637206397696,
         0.16173933398400003, 0.2607930634495548, 0.2607930634495548, 0.16173933398400003, 0.06150637206397696,
         0.013997837447100996, 0.0018301031310804924, 0.00012882627996192942, 4.4021210902308646e-06,
         6.127490259982928e-08, 2.4820623623151797e-10, 1.2578006724379264e-13]


def expect_normal(g, mu: float, sd: float) -> float:
    """E[g(X)] for X ~ N(mu, sd^2), probabilists' Gauss-Hermite (exact for low-order polynomials)."""
    if sd <= 0:
        return g(mu)
    return sum(w * g(mu + sd * x) for x, w in zip(_GH_X, _GH_W))


@lru_cache(maxsize=1)
def _params() -> dict:
    return json.loads((DATA_DIR / "params.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _norms() -> dict:
    return json.loads((DATA_DIR / "population_norms_china.json").read_text(encoding="utf-8"))


def domain_specs() -> List[dict]:
    return _params()["domains"]


def spec(domain_id: str) -> dict:
    for d in domain_specs():
        if d["id"] == domain_id:
            return d
    raise KeyError(domain_id)


# ----------------------------------------------------------------------------- parameters

def draw_log_rr(rr: dict, rng: Optional[random.Random]) -> float:
    """log RR per `per` units; with rng, a draw from the lognormal implied by the 95% CI."""
    m = math.log(rr["value"])
    if rng is None:
        return m
    se = (math.log(rr["hi"]) - math.log(rr["lo"])) / (2 * 1.959964)
    return rng.gauss(m, se)


def _log_rr_or_zero(rr, rng: Optional[random.Random]) -> float:
    return 0.0 if rr in (1, 1.0) else draw_log_rr(rr, rng)


def draw_params(sp: dict, rng: Optional[random.Random], region: Optional[str] = None) -> dict:
    """Concrete slopes for one Monte Carlo draw (or point values when rng is None).

    Categorical domains carry two RR sets: `levels` (the person's own category, optionally
    by region via `levels_by_region`) and `pop_levels` (population categories, used to
    normalise to the national average and for people whose category is unknown).
    """
    shape = sp["shape"]
    if shape == "loglinear":
        return {"beta": draw_log_rr(sp["rr"], rng) / sp["rr"]["per"]}
    if shape == "hinge":
        return {"b_lo": draw_log_rr(sp["rr_below"], rng) / sp["rr_below"]["per"],
                "b_hi": draw_log_rr(sp["rr_above"], rng) / sp["rr_above"]["per"]}
    if shape == "categorical":
        pop = sp.get("pop_levels", sp["levels"])
        lp = {lvl: _log_rr_or_zero(rr, rng) for lvl, rr in pop.items()}
        levels = dict(sp["levels"])
        if region and region in sp.get("levels_by_region", {}):
            levels.update(sp["levels_by_region"][region])
        # a level present in both sets shares one draw, so normalisation and person stay coherent
        lr = {lvl: (lp[lvl] if lvl in lp and levels[lvl] == pop.get(lvl) else _log_rr_or_zero(rr, rng))
              for lvl, rr in levels.items()}
        return {"log_rr": lr, "log_rr_pop": lp}
    raise ValueError(shape)


def f_raw(sp: dict, p: dict, x) -> float:
    """Un-normalised log HR of value x (number, or level name for categorical).

    A categorical value "pop:<level>" is a population draw and uses the population RR.
    """
    shape = sp["shape"]
    if shape == "categorical":
        if isinstance(x, str) and x.startswith("pop:"):
            return p["log_rr_pop"][x[4:]]
        return p["log_rr"][x]
    lo, hi = sp.get("clip", [None, None])
    if lo is not None:
        x = max(x, lo)
    if hi is not None:
        x = min(x, hi)
    if shape == "loglinear":
        return p["beta"] * x
    k_lo = sp.get("knot_lo", sp.get("knot"))
    k_hi = sp.get("knot_hi", sp.get("knot"))
    return p["b_lo"] * max(0.0, k_lo - x) + p["b_hi"] * max(0.0, x - k_hi)


# ----------------------------------------------------------------------------- population norms

def _band(table: List[dict], age: float) -> dict:
    for row in table:
        if row["age_lo"] <= age <= row["age_hi"]:
            return row
    return table[0] if age < table[0]["age_lo"] else table[-1]


def norm_for(sp: dict, sex: str, age: float, norms: Optional[dict] = None) -> dict:
    """Population distribution of the domain's marker for this sex and age.

    `norms` overrides the bundled Chinese norms (the NHANES validation passes its own).
    """
    t = (norms or _norms())["markers"][sp["norm"]]
    rows = t[sex.upper()[:1]]
    return _band(rows, age)


@lru_cache(maxsize=4096)
def _lme_cont(key: str, sex: str, band_lo: int, mean: float, sd: float, b_lo: float, b_hi: float, beta: float) -> float:
    sp = spec(key)
    p = {"beta": beta, "b_lo": b_lo, "b_hi": b_hi}
    return math.log(expect_normal(lambda x: math.exp(f_raw(sp, p, x)), mean, sd))


def log_mean_exp_pop(sp: dict, p: dict, sex: str, age: float, norms: Optional[dict] = None, shift: float = 0.0) -> float:
    """log E_pop[exp f(X)] for the person's sex/age group (population mean moved by `shift`)."""
    nb = norm_for(sp, sex, age, norms)
    if sp["shape"] == "categorical":
        return math.log(sum(prob * math.exp(p["log_rr_pop"][lvl]) for lvl, prob in nb["p"].items()))
    if sp.get("norm_kind") == "categorical_mid":   # continuous person value, population in bands
        mids = sp["mids"][sex.upper()[:1]]
        return math.log(sum(prob * math.exp(f_raw(sp, p, mids[lvl])) for lvl, prob in nb["p"].items()))
    if sp["shape"] == "loglinear":   # closed form, with clipping handled by quadrature only if it binds
        lo, hi = sp.get("clip", [None, None])
        mu, sd = nb["mean"] + shift, nb["sd"]
        if (lo is None or mu - 4 * sd > lo) and (hi is None or mu + 4 * sd < hi):
            return p["beta"] * mu + 0.5 * (p["beta"] * sd) ** 2
    if norms is None:
        return _lme_cont(sp["id"], sex, nb["age_lo"], round(nb["mean"] + shift, 6), nb["sd"],
                         round(p.get("b_lo", 0.0), 9), round(p.get("b_hi", 0.0), 9), round(p.get("beta", 0.0), 9))
    return math.log(expect_normal(lambda x: math.exp(f_raw(sp, p, x)), nb["mean"] + shift, nb["sd"]))


def log_hr(sp: dict, p: dict, x, sex: str, age: float, norms: Optional[dict] = None, shift: float = 0.0) -> float:
    """Normalised log HR: zero mean hazard ratio for same-age, same-sex peers."""
    return f_raw(sp, p, x) - log_mean_exp_pop(sp, p, sex, age, norms, shift)


def draw_from_population(sp: dict, sex: str, age: float, rng: random.Random, norms: Optional[dict] = None):
    nb = norm_for(sp, sex, age, norms)
    if sp.get("norm_kind") == "categorical_mid":
        u, acc = rng.random(), 0.0
        mids = sp["mids"][sex.upper()[:1]]
        for lvl, prob in nb["p"].items():
            acc += prob
            if u <= acc:
                return float(mids[lvl])
        return float(mids[list(nb["p"])[-1]])
    if sp["shape"] == "categorical":
        u, acc = rng.random(), 0.0
        for lvl, prob in nb["p"].items():
            acc += prob
            if u <= acc:
                return "pop:" + lvl
        return "pop:" + list(nb["p"].keys())[-1]
    return rng.gauss(nb["mean"], nb["sd"])
