"""System LongPi Ages: the terms of the whole-body model regrouped by body system (engine 1.1.1).

    system age = age + log E[exp(sum of the terms that belong to the system)] / b

Nothing here draws random numbers or changes the whole-body result: it post-processes the Monte Carlo draws that
`engine.run` already made. Two kinds of terms, both already inside log R:

  domain terms    c_d * l_d of the ten function domains, taken as computed for the whole-body number
  analyte terms   the blood-clock term split over the nine PhenoAge analytes. PhenoAge is linear in its predictor, so
                  the gap G is exactly sum_k w_k (x_k - ref_k(age, sex)) with w_k = coefficient / 0.090165 years per unit.
                  The filtered gap is linear in the tests, so each analyte has its own filtered share m_k (sum = G).
                  The log hazard g(G) is piecewise linear; analyte k gets g(G)/G * m_k, and the uncertainty of the clock
                  term is shared out by each analyte's part of the measurement noise.

In every draw: systems + cross-system domains + unassigned + methylation == whole-body log R (checked, reported).
Which analyte belongs to which system follows Table 1 of Levine 2018 (data/systems.json).
"""
from __future__ import annotations

import json
import math
import statistics
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from . import clock

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ANALYTES = ("albumin", "creatinine", "glucose", "crp", "lymph_pct", "mcv", "rdw", "alp", "wbc")
REF_KEY = {"crp": "ln_crp_mgdl"}


@lru_cache(maxsize=1)
def spec() -> dict:
    return json.loads((DATA_DIR / "systems.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _aref() -> dict:
    return json.loads((DATA_DIR / "phenoage_analyte_reference.json").read_text(encoding="utf-8"))


def analyte_reference(analyte: str, age: float, sex: str) -> float:
    """Reference value for a same-age, same-sex person; interpolated exactly like clock.reference_phenoage."""
    r = _aref()
    ages, vals = r["ages"], r["fit"][sex.upper()[:1]][REF_KEY.get(analyte, analyte)]
    if age <= ages[0]:
        return vals[0] + (age - ages[0]) * (vals[1] - vals[0]) / (ages[1] - ages[0])
    if age >= ages[-1]:
        return vals[-1] + (age - ages[-1]) * (vals[-1] - vals[-2]) / (ages[-1] - ages[-2])
    for i in range(1, len(ages)):
        if ages[i] >= age:
            w = (age - ages[i - 1]) / (ages[i] - ages[i - 1])
            return vals[i - 1] * (1 - w) + vals[i] * w
    return vals[-1]


def analyte_gaps(v: Dict[str, float], age: float, sex: str) -> Dict[str, float]:
    """Years of PhenoAge gap carried by each analyte of one test (CRP in mg/L, entered as ln mg/dL)."""
    out = {}
    for k in ANALYTES:
        x = math.log(v["crp"] / 10.0) if k == "crp" else v[k]
        out[k] = clock.years_per_unit(k) * (x - analyte_reference(k, age, sex))
    return out


def _tests(m) -> List[dict]:
    """The blood tests behind m.pheno with the values the clock used (same rules as engine.phenoage_points)."""
    from .engine import _val, decimal_year, parse_date
    cl, typical = m.pp["clock"], m.pp["data_menu"]["typical_blood"]
    out = []
    for l in sorted(m.person.get("labs", []), key=lambda x: x["date"]):
        excl = l.get("clock_exclude")
        if excl is True:
            continue
        it = {k: _val(v) for k, v in l["items"].items()}
        drop = [k for k in (excl or []) if k in typical and k != "crp"]
        for k in drop:
            it[k] = typical[k]
        if not all(k in it for k in ("albumin", "creatinine", "glucose", "lymph_pct", "mcv", "rdw", "alp", "wbc")):
            continue
        d = parse_date(l["date"])
        if d > m.at:
            continue
        imputed = "crp" not in it or "crp" in (excl or [])
        v = {k: it[k] for k in ANALYTES if k != "crp"}
        v["crp"] = max(cl["crp_impute_mg_l"] if imputed else it["crp"], 0.1)
        out.append({"date": d.isoformat(), "age": decimal_year(d) + m.birth_offset, "v": v,
                    "not_measured": sorted(drop + (["crp"] if imputed else []))})
    return out


def _sources(sp: dict) -> str:
    found: List[str] = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("source"), str) and o["source"] not in found:
                found.append(o["source"])
            for x in o.values():
                walk(x)
    walk(sp)
    return "；".join(found)


def _years(lhs: List[float], b: float, nd: int = 2) -> dict:
    from .engine import q
    pt = math.log(statistics.fmean(math.exp(x) for x in lhs)) / b
    return {"median": round(pt, nd), "p10": round(q([x / b for x in lhs], 0.1), nd), "p90": round(q([x / b for x in lhs], 0.9), nd)}


def _vendor_organs(m) -> Optional[dict]:
    """Latest methylation report that prints organ ages (any clock type); gap is taken against the age at sampling."""
    from .engine import decimal_year, parse_date
    best = None
    for r in m.person.get("methylation") or []:
        if not r.get("organs") or not r.get("date"):
            continue
        d = parse_date(r["date"])
        if d > m.at:
            continue
        if best is None or d > best[0]:
            best = (d, r)
    if best is None:
        return None
    d, r = best
    chrono = float(r["chrono_age"]) if r.get("chrono_age") is not None else decimal_year(d) + m.birth_offset
    return {"date": d.isoformat(), "vendor": r.get("vendor", ""), "chrono_at_sampling": round(chrono, 1),
            "organs": {str(k): float(v) for k, v in r["organs"].items()}}


def compute(m, draws: List[dict]) -> dict:
    from .engine import gap_loghr
    sp, b = spec(), m.b
    n = len(draws)
    dom_lh = {did: [d["parts"][did] for d in draws] for did in m.specs}
    # ---- analyte terms of the blood clock
    an_lh: Dict[str, List[float]] = {}
    an_info: Dict[str, dict] = {}
    unassigned = [0.0] * n
    tests = _tests(m) if m.has_clock else []
    clock_ok = m.has_clock and len(tests) == len(m.pheno)
    if clock_ok:
        prior_var = max(clock.gap_sd_population(m.age, m.sex) ** 2 - statistics.fmean(p["r"] for p in m.pheno), 1.0)
        qy = m.pp["clock"]["q_per_year"]
        per_test = [analyte_gaps(t["v"], t["age"], m.sex) for t in tests]
        share = {k: clock.kalman_gap([{"t": p["t"], "gap": g[k], "r": p["r"]} for p, g in zip(m.pheno, per_test)],
                                     m.year0, math.sqrt(prior_var), qy)[0] for k in ANALYTES}
        gc = m.pp["calibration"]["gap"]
        g0 = gap_loghr(m.gap_mean, {"knots": gc["knots"], "slopes": gc["slopes"]})
        s0 = g0 / m.gap_mean if abs(m.gap_mean) > 0.05 else gc["slopes"][1]
        resid = m.gap_mean - sum(share.values())          # rounding of the reference curves; ~0
        noise = clock.noise_sd(tests[-1]["v"])[1]
        last = tests[-1]
        for k in ANALYTES:
            an_lh[k] = [s0 * share[k] + noise[k] * (d["parts"]["clock"] - g0) for d in draws]
            an_info[k] = {"value": round(last["v"][k], 2), "reference": round(math.exp(analyte_reference(k, last["age"], m.sex)) * 10 if k == "crp"
                                                                              else analyte_reference(k, last["age"], m.sex), 2),
                          "measured": k not in last["not_measured"], "gap_years_share": round(share[k], 2), "date": last["date"]}
        unassigned = [s0 * resid] * n
    else:
        unassigned = [d["parts"]["clock"] for d in draws]   # no blood clock: the residual draw stays whole-body only
    vend = _vendor_organs(m)
    tol = sp["methylation_organ"]["tolerance_s_lab_multiple"] * m.pp["methylation"]["s_lab"]
    systems, total = [], [0.0] * n
    for s in sp["systems"]:
        doms = [d for d in s["domains"] if d in m.specs]
        ans = [k for k in s["analytes"] if k in an_lh]
        measured_dom = [d for d in doms if d in m.I.values]
        measured_an = [k for k in ans if an_info[k]["measured"]]
        ok = not s.get("never") and (
            (any(d in m.I.values for d in s["require_domains_any"]) or (s.get("clock_satisfies") and bool(measured_an)))
            if s["require_domains_any"] else True) and (not s["require_clock"] or bool(measured_an))
        if not doms and not ans:
            ok = False
        lh = [sum(dom_lh[d][i] for d in doms) + sum(an_lh[k][i] for k in ans) for i in range(n)]
        for i in range(n):
            total[i] += lh[i]
        contrib = []
        for d in doms:
            v = m.I.values.get(d)
            contrib.append({"id": d, "kind": "domain", "label": m.specs[d]["name_zh"], "measured": v is not None,
                            "input": None if v is None else (round(v["x"], 2) if isinstance(v["x"], float) else v["x"]),
                            "input_source": None if v is None else v["src"], "years": _years(dom_lh[d], b),
                            "evidence": _sources(m.specs[d])})
        for k in ans:
            contrib.append({"id": k, "kind": "analyte", "label": sp["analyte_labels"][k], "measured": an_info[k]["measured"],
                            "input": an_info[k]["value"], "reference_same_age_sex": an_info[k]["reference"],
                            "input_source": f"血液检测 {an_info[k]['date']}", "phenoage_gap_share_years": an_info[k]["gap_years_share"],
                            "years": _years(an_lh[k], b), "evidence": sp["analyte_source"]})
        missing = [m.specs[d]["name_zh"] for d in doms if d not in m.I.values]
        if s["analytes"] and not ans:
            missing.append("九项血液检测")
        missing += [sp["analyte_labels"][k] + "（未实测，按典型值计）" for k in ans if not an_info[k]["measured"]]
        yrs = _years(lh, b, 1) if ok else None
        aliases = [a.lower() for a in s["methylation_aliases"]]
        vlines = []
        if vend:
            for name, age in vend["organs"].items():
                if name.lower() in aliases:
                    vlines.append({"label": name, "age": round(age, 1), "gap": round(age - vend["chrono_at_sampling"], 1),
                                   "date": vend["date"], "vendor": vend["vendor"], "counted": False})
        agreement = None
        if vlines and ok:
            agreement = "consistent" if all(abs(v["gap"] - yrs["median"]) <= tol for v in vlines) else "inconsistent"
        systems.append({"id": s["id"], "name": s["name_zh"], "status": "estimated" if ok else "insufficient",
                        "age": None if not ok else {k: round(m.age + v, 1) for k, v in yrs.items()}, "delta": yrs,
                        "contributions": contrib, "inputs_used": [c["label"] for c in contrib if c["measured"]],
                        "inputs_missing": missing, "missing_zh": None if ok else s["missing_zh"], "note": s.get("note_zh"),
                        "not_counted": s["not_counted"], "vendor_methylation": vlines, "vendor_agreement": agreement})
    cross = [d for d in sp["cross_system"]["domains"] if d in m.specs]
    cross_lh = [sum(dom_lh[d][i] for d in cross) for i in range(n)]
    err = max(abs(total[i] + cross_lh[i] + unassigned[i] + draws[i]["parts"].get("methylation", 0.0) - draws[i]["lr"]) for i in range(n))
    left = [d for d in m.specs if d not in cross and not any(d in s["domains"] for s in sp["systems"])]
    return {
        "version": sp["version"], "chrono": round(m.age, 1), "gompertz_b": round(b, 4), "has_blood_clock": bool(clock_ok),
        "systems": systems,
        "cross_system": {"name": sp["cross_system"]["name_zh"], "delta": _years(cross_lh, b),
                         "contributions": [{"id": d, "label": m.specs[d]["name_zh"], "measured": d in m.I.values,
                                            "years": _years(dom_lh[d], b), "evidence": _sources(m.specs[d])} for d in cross]},
        "unassigned": {"delta": _years(unassigned, b), "what": "参考曲线取整的余项" if clock_ok else "没有血液检测：全身模型里“看不到的那一块”，不分到任何系统"},
        "methylation_rule": {"rule": sp["methylation_organ"]["rule"], "tolerance_years": round(tol, 1), "text": sp["methylation_organ"]["rule_zh"],
                             "report": None if not vend else {k: vend[k] for k in ("date", "vendor", "chrono_at_sampling")}},
        "consistency": {"identity": "systems + cross_system + unassigned + methylation == whole-body log R in every draw",
                        "max_abs_log_hazard_error": float(f"{err:.3e}"), "domains_not_assigned": left},
    }
