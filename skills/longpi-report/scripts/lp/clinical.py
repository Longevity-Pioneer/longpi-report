"""Deterministic clinical calculators the risk cards cite (not part of the mortality model).

China-PAR 10-year ASCVD risk is vendored from longevity-skills/china-par-ascvd-risk (MIT,
same author), which reproduces Yang X, et al. Circulation 2016;134:1430 Table 2 within 1%.
CKD-EPI 2021 creatinine equation: Inker LA, et al. N Engl J Med 2021;385:1737.
FIB-4: Sterling RK, et al. Hepatology 2006;43:1317.
"""
from __future__ import annotations

import math
from datetime import date
from typing import Dict, Optional

# ---- China-PAR (Supplemental Table 1 coefficients; men's continuous terms recovered from the
# worked example, women's S10 solved from the women's example; see the source skill's contract)
_MEN = {"ln_age": 130.88 / math.log(60), "ln_sbp_treated": 27.39, "ln_sbp_untreated": 127.28 / math.log(130),
        "ln_tc": 3.32 / math.log(210), "ln_hdl": -2.78 / math.log(55), "ln_waist": -3.12 / math.log(80),
        "smoker": 3.96, "diabetes": 0.36, "north": 0.48, "urban": -0.16, "family_history": 6.22,
        "ln_age_x_ln_sbp_treated": -6.02, "ln_age_x_ln_sbp_untreated": -114.21 / (math.log(60) * math.log(130)),
        "ln_age_x_smoker": -0.94, "ln_age_x_family_history": -1.53}
_WOMEN = {"ln_age": 24.87, "ln_sbp_treated": 20.71, "ln_sbp_untreated": 19.98, "ln_tc": 0.06, "ln_hdl": -0.22,
          "ln_waist": 1.48, "smoker": 0.49, "diabetes": 0.57, "north": 0.54,
          "ln_age_x_ln_sbp_treated": -4.53, "ln_age_x_ln_sbp_untreated": -4.36}
_MEAN = {"M": 140.68, "F": 117.26}
_S10 = {"M": 0.9707, "F": 0.9851}
MG_PER_MMOL = 1 / 0.0259


def china_par(sex: str, age: float, sbp: float, treated: bool, tc_mmol: float, hdl_mmol: float, waist: float,
              smoker: bool, diabetes: bool, north: bool, urban: bool, family_history: bool) -> Optional[dict]:
    if not 35 <= age <= 74:
        return None
    la, ls = math.log(age), math.log(sbp)
    tc, hdl = tc_mmol * MG_PER_MMOL, hdl_mmol * MG_PER_MMOL
    key = "treated" if treated else "untreated"
    if sex == "M":
        c = _MEN
        tot = (c["ln_age"] * la + c[f"ln_sbp_{key}"] * ls + c["ln_tc"] * math.log(tc) + c["ln_hdl"] * math.log(hdl)
               + c["ln_waist"] * math.log(waist) + c["diabetes"] * diabetes + c["north"] * north + c["urban"] * urban
               + c[f"ln_age_x_ln_sbp_{key}"] * la * ls + c["smoker"] * smoker + c["family_history"] * family_history
               + c["ln_age_x_smoker"] * la * smoker + c["ln_age_x_family_history"] * la * family_history)
    else:
        c = _WOMEN
        tot = (c["ln_age"] * la + c[f"ln_sbp_{key}"] * ls + c["ln_tc"] * math.log(tc) + c["ln_hdl"] * math.log(hdl)
               + c["ln_waist"] * math.log(waist) + c["smoker"] * smoker + c["diabetes"] * diabetes + c["north"] * north
               + c[f"ln_age_x_ln_sbp_{key}"] * la * ls)
    risk = 100 * (1 - _S10[sex] ** math.exp(tot - _MEAN[sex]))
    cat = "低危" if risk < 5 else ("中危" if risk < 10 else "高危")
    return {"risk_10y_pct": round(risk, 1), "category": cat,
            "note": "China-PAR 10 年动脉粥样硬化性心血管病风险（中国心血管病风险评估和管理指南 2019：<5% 低危，5%–9.9% 中危，≥10% 高危）"}


def egfr_ckd_epi_2021(scr_umol: float, age: float, sex: str) -> float:
    scr = scr_umol / 88.4
    k, a1 = (0.9, -0.302) if sex == "M" else (0.7, -0.241)
    e = 142 * min(scr / k, 1) ** a1 * max(scr / k, 1) ** -1.200 * 0.9938 ** age
    return round(e * (1.012 if sex == "F" else 1.0), 1)


def fib4(age: float, ast: float, alt: float, platelets: float) -> float:
    return round(age * ast / (platelets * math.sqrt(alt)), 2)


def summary(person: dict, sex: str, age: float, inputs: dict) -> Dict[str, object]:
    """Latest-value calculators; each entry is omitted when its inputs are missing."""
    labs = sorted(person.get("labs", []), key=lambda l: l["date"])
    last: Dict[str, float] = {}
    for l in labs:
        for k, v in l["items"].items():
            last[k] = v[0] if isinstance(v, list) else v
    out: Dict[str, object] = {}
    if "creatinine" in last:
        e = egfr_ckd_epi_2021(last["creatinine"], age, sex)
        stage = "G1" if e >= 90 else "G2" if e >= 60 else "G3a" if e >= 45 else "G3b" if e >= 30 else "G4" if e >= 15 else "G5"
        out["egfr"] = {"value": e, "kdigo": stage, "note": "CKD-EPI 2021 肌酐公式（不含种族系数）"}
    if all(k in last for k in ("ast", "alt", "platelets")):
        f = fib4(age, last["ast"], last["alt"], last["platelets"])
        out["fib4"] = {"value": f, "band": "低（<1.3）" if f < 1.3 else ("不确定（1.3–2.67）" if f <= 2.67 else "高（>2.67）")}
    anth = sorted(person.get("anthropometrics", []), key=lambda a: a["date"])
    waist = next((a["waist_cm"] for a in reversed(anth) if a.get("waist_cm")), None)
    vit = sorted([v for v in person.get("vitals", []) if v.get("sbp") and v.get("setting", "office") == "office"], key=lambda v: v["date"])
    sbp = inputs.get("bp", {}).get("value") if inputs.get("bp") else (vit[-1]["sbp"] if vit else None)
    if all(k in last for k in ("tc", "hdl")) and sbp and waist:
        life = person.get("lifestyle", {})
        conds = " ".join(c.get("name", "") for c in person.get("conditions", []))
        fam = any(("冠心病" in f.get("condition", "") or "心梗" in f.get("condition", "") or "卒中" in f.get("condition", "")
                   or "脑梗" in f.get("condition", "")) for f in person.get("family_history", []))
        treated = any("降压" in m.get("name", "") or m.get("class") == "antihypertensive" for m in person.get("medications", []))
        region = person["person"].get("region", {})
        cp = china_par(sex, age, float(sbp), treated, last["tc"], last["hdl"], float(waist),
                       (life.get("smoking") or {}).get("status") == "current",
                       inputs.get("glucose", {}).get("value") == "diabetes" or "糖尿病" in conds,
                       bool(region.get("north", False)), bool(region.get("urban", True)), fam)
        if cp:
            out["china_par"] = cp
    if waist:
        out["central_obesity"] = waist >= (90 if sex == "M" else 85)
    if "uric_acid" in last:
        out["uric_acid"] = {"value": last["uric_acid"], "high": last["uric_acid"] > 420}
    if "ldl" in last:
        l = last["ldl"]
        out["ldl_band"] = "≥4.9 很高" if l >= 4.9 else ("4.1–4.9 升高" if l >= 4.1 else ("3.4–4.1 边缘升高" if l >= 3.4 else "<3.4"))
    return out
