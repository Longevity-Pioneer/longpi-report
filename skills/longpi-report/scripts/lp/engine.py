"""LongPi engine: LongPi Age, the 120 Index, survival, interventions, LongPi Pace.

Model (methods and evidence: docs/方法学白皮书.md)

  log R      = g(G) + sum_d c_d * l_d(x_d)
  LongPi Age = age + log E[R] / b            (80% interval from the Monte Carlo quantiles)

  G     true PhenoAge gap in years (PhenoAge minus the NHANES reference for the same age
        and sex), filtered over all blood tests with noise from biological variation
  g     piecewise-linear log hazard of the gap, calibrated in NHANES 1999-2018
  l_d   literature dose-response log HR of domain d, normalised so the average same-age,
        same-sex Chinese adult has E[exp l_d] = 1; an unmeasured domain is drawn from
        that population distribution
  c_d   domain coefficient: NHANES recalibration, or 1 where the literature effect is
        causal (blood pressure and LDL from trials, smoking, alcohol from genetics)
  b     Gompertz slope of the UN WPP 2024 China life table (the rate of ageing)

  Survival: gamma-frailty identity on each scenario's reference cohort path.
  120 Index = 100 + 10 log10(P_you(120) / P_peer(120)).

Point estimates use the expected hazard multiplier E[R] across draws, so an unmeasured
domain is exactly neutral; intervals are the 10th-90th percentiles of the draws.
"""
from __future__ import annotations

import json
import math
import random
import statistics
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import clinical, clock, domains as DM, mortality as M

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ENGINE_VERSION = "1.1"
MILESTONES = (80, 90, 100, 110, 120)


@lru_cache(maxsize=1)
def P() -> dict:
    return json.loads((DATA_DIR / "params.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ small helpers

def q(values: Sequence[float], p: float) -> float:
    v = sorted(values)
    if not v:
        return float("nan")
    k = (len(v) - 1) * p
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return v[lo] if lo == hi else v[lo] + (v[hi] - v[lo]) * (k - lo)


def summ(values: Sequence[float], nd: int = 2, point: Optional[float] = None) -> dict:
    mid = q(values, 0.5) if point is None else point
    return {"median": round(mid, nd), "p10": round(q(values, 0.1), nd), "p90": round(q(values, 0.9), nd)}


def decimal_year(d: date) -> float:
    return d.year + (d - date(d.year, 1, 1)).days / 365.25


def parse_date(s) -> date:
    s = str(s)
    if len(s) == 4:
        s += "-07-01"
    elif len(s) == 7:
        s += "-15"
    return datetime.strptime(s[:10], "%Y-%m-%d").date()


def _val(v):
    return v[0] if isinstance(v, list) else v


# ------------------------------------------------------------------ inputs

class Inputs:
    """One value per domain at a given date, with measurement SD and device conversion."""

    def __init__(self, sex: str, age: float, at: date):
        self.sex, self.age, self.at = sex, age, at
        self.values: Dict[str, dict] = {}

    def set(self, did: str, x, sd: float = 0.0, src: str = "", device: Optional[dict] = None, kind: str = "") -> None:
        self.values[did] = {"x": x, "sd": sd, "src": src, "device": device, "kind": kind}


def _latest(items: List[dict], key: str, at: date, max_years: float) -> Optional[Tuple[date, float, dict]]:
    best = None
    for it in items:
        if it.get(key) is None:
            continue
        d = parse_date(it["date"])
        if d > at or (at - d).days > max_years * 365.25:
            continue
        if best is None or d > best[0]:
            best = (d, float(it[key]), it)
    return best


def _lab_rows(person: dict) -> List[dict]:
    return [dict(date=l["date"], **{k: _val(v) for k, v in l["items"].items()}) for l in person.get("labs", [])]


def office_from_home(home_sbp: float) -> float:
    """Office-equivalent SBP from a home average (Chinese 2024 guideline correspondence)."""
    pts = P()["devices"]["home_to_office_sbp"]
    if home_sbp <= pts[0][0]:
        return home_sbp
    for (h0, o0), (h1, o1) in zip(pts, pts[1:]):
        if home_sbp <= h1:
            return o0 + (home_sbp - h0) * (o1 - o0) / (h1 - h0)
    (h0, o0), (h1, o1) = pts[-2], pts[-1]
    return o1 + (home_sbp - h1) * (o1 - o0) / (h1 - h0)


def selfreport_from_watch(tst: float) -> float:
    """Self-report-equivalent sleep from device total sleep time (Lauderdale 2008 over-report)."""
    w = P()["devices"]["watch_sleep"]
    over = max(w["min_overreport"], w["overreport_at_5h"] + w["overreport_slope"] * (tst - 5.0))
    return tst + over


def device_kind(person: dict) -> str:
    dev = ((person.get("wearables") or {}).get("device") or "").lower()
    if "apple" in dev or "苹果" in dev:
        return "apple"
    if "huawei" in dev or "华为" in dev or "honor" in dev or "荣耀" in dev:
        return "huawei"
    if any(k in dev for k in ("garmin", "佳明", "coros", "高驰", "suunto", "fitbit", "firstbeat")):
        return "firstbeat"   # exercise-based estimates (Molina-Garcia 2022); Polar's resting test falls to "unknown"
    return "unknown"


def glycemic_status(person: dict, at: date) -> Optional[Tuple[str, str]]:
    """ADA categories (matching the national prevalence used for normalisation)."""
    conds = " ".join(c.get("name", "") for c in person.get("conditions", []))
    if "糖尿病" in conds and "前期" not in conds:
        return "diabetes", "已诊断糖尿病"
    a1c = fpg = None
    for l in sorted(person.get("labs", []), key=lambda x: x["date"]):
        if parse_date(l["date"]) > at or (at - parse_date(l["date"])).days > 3 * 365.25:
            continue
        it = l["items"]
        if "hba1c" in it:
            a1c = _val(it["hba1c"])
        if "glucose_fasting" in it:
            fpg = _val(it["glucose_fasting"])
    if a1c is None and fpg is None:
        return None
    txt = "；".join(s for s in (f"HbA1c {a1c}%" if a1c is not None else "", f"空腹血糖 {fpg}" if fpg is not None else "") if s)
    if (a1c is not None and a1c >= 6.5) or (fpg is not None and fpg >= 7.0):
        return "diabetes", txt
    if (a1c is not None and a1c >= 5.7) or (fpg is not None and fpg >= 5.6):
        return "prediabetes", txt
    return "normal", txt


def smoking_level(person: dict, at: date) -> Optional[str]:
    """Smoking category as of `at`. A former smoker without a quit year gets the population
    average of former smokers ("pop:former"); before the quit year the person was a smoker."""
    sm = (person.get("lifestyle") or {}).get("smoking") or {}
    st = sm.get("status")
    if st == "former":
        qy = sm.get("quit_year")
        if qy is None:
            return "pop:former"
        if at.year < int(qy):
            return "current"
        return "former_lt5" if at.year - int(qy) < 5 else "former_ge5"
    return st if st in ("never", "current") else None


def collect_inputs(person: dict, derived: dict, at: date, sex: str, age: float, snapshot: bool = False) -> Inputs:
    """Pick one value per domain as of `at`. Snapshots (past dates) use checkup-type data only."""
    I = Inputs(sex, age, at)
    dev = P()["devices"]
    vit, fit, anth = person.get("vitals", []), person.get("fitness", []), person.get("anthropometrics", [])
    w = {} if snapshot else derived.get("wearables", {})
    wk = device_kind(person)

    lc = _latest([f for f in fit if f.get("method") == "cpet"], "vo2max", at, 3)
    if lc:
        I.set("crf", lc[1], dev["cpet_vo2max_sd"], f"实验室 CPET {lc[0]:%Y-%m}", kind="cpet")
    elif w.get("vo2max_recent") is not None:
        d = dev["watch_vo2max"][wk]
        I.set("crf", w["vo2max_recent"], d["sd"], "手表估算 VO2max（近 90 天中位）", {"bias": d["bias"], "bias_sd": d["bias_sd"]}, "watch")
    else:
        lw = _latest([f for f in fit if f.get("method") != "cpet"], "vo2max", at, 2)
        if lw:
            d = dev["watch_vo2max"][wk]
            I.set("crf", lw[1], d["sd"], f"手表估算 VO2max {lw[0]:%Y-%m}", {"bias": d["bias"], "bias_sd": d["bias_sd"]}, "watch")

    lg = _latest(fit, "grip_kg", at, 3)
    if lg:
        I.set("muscle", lg[1], dev["grip_sd"], f"握力 {lg[0]:%Y-%m}")

    if w.get("rhr_30d") is not None:
        d = dev["watch_rhr"]
        I.set("rhr", w["rhr_30d"], d["sd"], "手表静息心率（近 30 天中位）", {"bias": d["to_clinic"], "bias_sd": d["to_clinic_sd"]}, "watch")
    else:
        lp = _latest(vit, "pulse", at, 2)
        if lp:
            I.set("rhr", lp[1], dev["office_pulse_sd"], f"体检脉搏 {lp[0]:%Y-%m}", kind="office")

    if w.get("sleep_h_median") is not None:
        d = dev["watch_sleep"]
        I.set("sleep", selfreport_from_watch(w["sleep_h_median"]), d["sd"],
              f"手表睡眠 {w['sleep_h_median']} 小时（近 90 天中位，换算为问卷口径）", {"bias": 0.0, "bias_sd": d["to_selfreport_sd"]}, "watch")
    elif (person.get("lifestyle") or {}).get("sleep_h") is not None:
        I.set("sleep", float(person["lifestyle"]["sleep_h"]), dev["selfreport_sleep_sd"], "自述睡眠时长", kind="questionnaire")

    hb = w.get("home_bp")
    if hb and hb.get("sbp") is not None:
        I.set("bp", office_from_home(hb["sbp"]), dev["home_bp_sd"], f"家庭血压 {hb['sbp']}（{hb['from']} 至 {hb['to']}，{hb['n']} 次，换算为诊室口径）",
              kind="home")
    else:
        off = sorted([v for v in vit if v.get("sbp") is not None and v.get("setting", "office") == "office"
                      and parse_date(v["date"]) <= at and (at - parse_date(v["date"])).days <= 2 * 365.25], key=lambda v: v["date"])
        if off:
            rec = off[-2:]
            I.set("bp", statistics.fmean(float(v["sbp"]) for v in rec), dev["office_sbp_sd"] / math.sqrt(len(rec)),
                  "体检血压（最近 %d 次均值）" % len(rec), kind="office")

    ll = _latest(_lab_rows(person), "ldl", at, 3)
    if ll:
        I.set("lipid", ll[1], ll[1] * dev["ldl_cv"], f"LDL-C {ll[1]:.2f}（{ll[0]:%Y-%m}）")

    gs = glycemic_status(person, at)
    if gs:
        I.set("glucose", gs[0], 0.0, gs[1])

    la = _latest(anth, "bmi", at, 2)
    if la is None:
        best = None
        for a in anth:
            d0 = parse_date(a["date"])
            if a.get("height_cm") and a.get("weight_kg") and d0 <= at and (at - d0).days <= 2 * 365.25:
                if best is None or d0 > best[0]:
                    best = (d0, a["weight_kg"] / (a["height_cm"] / 100) ** 2, a)
        la = best
    if la:
        I.set("adiposity", la[1], dev["bmi_sd"], f"BMI {la[1]:.1f}（{la[0]:%Y-%m}）")

    sl = smoking_level(person, at)
    if sl:
        I.set("smoking", sl, 0.0, {"never": "从不吸烟", "former_ge5": "已戒烟 ≥5 年", "former_lt5": "戒烟不足 5 年",
                                   "pop:former": "已戒烟（戒烟年份未知）", "current": "目前吸烟"}[sl])
    g = (person.get("lifestyle") or {}).get("alcohol") or {}
    gw = g.get("grams_per_week", 7 * g["grams_per_day"] if g.get("grams_per_day") is not None else None)
    if gw is not None:
        I.set("alcohol", float(gw), 0.15 * float(gw), f"饮酒约 {gw:.0f} 克酒精/周（自述）")
    return I


def methylation_input(person: dict, at: date, sex: str, birth_offset: float, snapshot: bool = False) -> Optional[dict]:
    """Latest counted methylation clock (GrimAge2 preferred, then GrimAge) dated within max_age_years before `at`.

    Acceleration is read against the NHANES reference curve of that clock. Snapshots leave methylation out,
    so the yearly trajectory compares like with like."""
    mp = P()["methylation"]
    if snapshot:
        return None
    best = None
    for r in person.get("methylation") or []:
        ct = str(r.get("clock_type", "")).strip().lower()
        name = next((c for c in mp["counted"] if c.lower() == ct), None)
        if name is None or r.get("bio_age") is None or not r.get("date"):
            continue
        d = parse_date(r["date"])
        if d > at or (at - d).days > mp["max_age_years"] * 365.25:
            continue
        age_test = float(r["chrono_age"]) if r.get("chrono_age") is not None else decimal_year(d) + birth_offset
        key = (d, -mp["counted"].index(name))
        if best is None or key > best[0]:
            best = (key, {"clock": name, "value": float(r["bio_age"]), "age_at_test": round(age_test, 2),
                          "date": d.isoformat(), "vendor": r.get("vendor", "")})
    if best is None:
        return None
    out = best[1]
    a0, a1 = mp["clocks"][out["clock"]]["ref"][sex]
    out["accel"] = round(out["value"] - (a0 + a1 * out["age_at_test"]), 2)
    return out


def _interp(x: float, xs: Sequence[float], ys: Sequence[float]) -> float:
    if x <= xs[0]:
        return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1]


# ------------------------------------------------------------------ clock layer

def phenoage_points(person: dict, sex: str, birth_offset: float, at: date) -> List[dict]:
    """One PhenoAge per blood test with the nine analytes (CRP may be missing: imputed).

    A lab entry may carry "clock_exclude": true (not used for the clock) or a list of analytes to leave out,
    e.g. ["mcv", "rdw"] during iron-deficiency recovery: those are replaced by typical values and their
    population spread is added to that test's noise. Each point is flagged for states that distort PhenoAge."""
    pts = []
    cl = P()["clock"]
    typical = P()["data_menu"]["typical_blood"]
    for l in sorted(person.get("labs", []), key=lambda x: x["date"]):
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
        if d > at:
            continue
        age = decimal_year(d) + birth_offset
        imputed = "crp" not in it or "crp" in (excl or [])
        v = dict(it)
        if imputed:
            v["crp"] = cl["crp_impute_mg_l"]
        v["crp"] = max(v["crp"], 0.1)
        pa = clock.phenoage(v, age)
        ref = clock.reference_phenoage(age, sex)
        sd_noise, shares = clock.noise_sd(v)
        r = sd_noise ** 2 + (cl["crp_impute_extra_var"] if imputed else 0.0)
        r += sum((clock.years_per_unit(k) * cl["analyte_pop_sd"][k]) ** 2 for k in drop)
        flags = clock.analyte_flags(it, skip=drop + (["crp"] if imputed else []))
        pts.append({"date": d.isoformat(), "t": decimal_year(d), "age": round(age, 1), "phenoage": round(pa, 1),
                    "ref_phenoage": round(ref, 1), "gap": round(pa - ref, 2), "r": r, "noise_sd": round(math.sqrt(r), 2),
                    "crp_imputed": imputed, "left_out": drop, "flags": flags,
                    "values": {k: round(it[k], 2) for k in ("crp", "mcv", "rdw", "wbc") if k in it and k not in drop},
                    "top_noise": max(shares, key=shares.get)})
    return pts


def excluded_blood_tests(person: dict, at: date) -> List[dict]:
    return [{"date": l["date"], "reason": l.get("clock_exclude_reason", "")} for l in person.get("labs", [])
            if l.get("clock_exclude") is True and parse_date(l["date"]) <= at]


def gap_loghr(G: float, cal: dict) -> float:
    """Piecewise-linear log HR of the PhenoAge gap (NHANES calibration)."""
    k_lo, k_hi = cal["knots"]
    s_lo, s_mid, s_hi = cal["slopes"]
    if G < k_lo:
        return s_mid * k_lo + s_lo * (G - k_lo)
    if G > k_hi:
        return s_mid * k_hi + s_hi * (G - k_hi)
    return s_mid * G


# ------------------------------------------------------------------ the model

class Model:
    def __init__(self, person: dict, derived: dict, n_draws: int = 2000, seed: int = 20261024,
                 at: Optional[date] = None, snapshot: bool = False):
        self.person, self.derived = person, derived
        self.pp = P()
        pinfo = person["person"]
        self.sex = pinfo["sex"].upper()[:1]
        self.as_of = parse_date(person["as_of"])
        if "age" in pinfo:
            age_asof = float(pinfo["age"])
        else:
            age_asof = (self.as_of - parse_date(pinfo["birth"])).days / 365.25
        self.birth_offset = age_asof - decimal_year(self.as_of)
        self.at = at or self.as_of
        self.age = round(decimal_year(self.at) + self.birth_offset, 2)
        self.year0 = decimal_year(self.at)
        self.region = "urban" if (pinfo.get("region") or {}).get("urban") is True else (
            "rural" if (pinfo.get("region") or {}).get("urban") is False else None)
        self.I = collect_inputs(person, derived, self.at, self.sex, self.age, snapshot)
        self.ref = M.Reference(self.sex)
        self.b = self.ref.gompertz_slope(int(self.year0))
        self.n = n_draws
        self.rng = random.Random(seed)
        self.specs = {d["id"]: d for d in DM.domain_specs()}
        self.pheno = phenoage_points(person, self.sex, self.birth_offset, self.at)
        self.has_clock = bool(self.pheno)
        if self.has_clock:
            self.gap_mean, self.gap_sd = self.gap_posterior(self.pheno)
        else:
            self.gap_mean, self.gap_sd = 0.0, clock.gap_sd_population(self.age, self.sex)
        self.coef_set = "with_clock" if self.has_clock else "without_clock"
        cr = self.pp["clock_residual"]
        self.clock_resid_sd = _interp(self.age, cr["age_mid"], cr["sd"])   # used only without a blood clock
        mp = self.pp["methylation"]
        self.meth = methylation_input(person, self.at, self.sex, self.birth_offset, snapshot)
        self.meth_spec = mp["clocks"][self.meth["clock"] if self.meth else mp["default_unmeasured"]]
        self.meth_mobs: Optional[float] = None   # residual of the measured acceleration given the LongPi point
        self.scen = self.pp["scenarios"]
        self.s_ref: Dict[str, List[float]] = {}
        for k, sc in self.scen["defs"].items():
            self.s_ref[k] = M.survival_from(M.cohort_hazards(self.ref, self.age, self.year0, sc), self.age)
        self.ages = M.survival_ages(self.age, len(next(iter(self.s_ref.values()))))
        if self.meth:
            self._set_methylation_residual()

    def gap_posterior(self, points: List[dict]) -> Tuple[float, float]:
        prior_var = max(clock.gap_sd_population(self.age, self.sex) ** 2 - statistics.fmean(p["r"] for p in points), 1.0)
        return clock.kalman_gap(points, self.year0, math.sqrt(prior_var), self.pp["clock"]["q_per_year"])

    def _set_methylation_residual(self, n: int = 400) -> None:
        """M = acceleration - E[acceleration | LongPi point, age, sex], with the point taken before methylation."""
        saved, self.rng = self.rng, random.Random(97)
        lrs = [self.log_r(self.draw(), meth=False) for _ in range(n)]
        self.rng = saved
        lp = math.log(statistics.fmean(math.exp(x) for x in lrs))
        ro = self.meth_spec["resid_on"]
        expected = ro["intercept"] + ro["lp"] * lp + ro["age"] * self.age + ro["male"] * (1.0 if self.sex == "M" else 0.0)
        self.meth_mobs = self.meth["accel"] - expected
        self.meth.update({"expected_accel": round(expected, 2), "resid": round(self.meth_mobs, 2)})

    def meth_term(self, th: dict) -> float:
        """Methylation clock residual on the log-hazard scale, normalised so the population average risk is 1.

        Not measured: the residual is drawn from its NHANES spread. Measured: the residual is shrunk toward 0
        for a possible offset between the user's laboratory/population and NHANES (s_lab, s_pop)."""
        sp, b = self.meth_spec, th["beta_m"]
        s = sp["sd_resid"]
        if self.meth_mobs is None:
            m = s * th["zm"]
        else:
            s_ref2 = self.pp["methylation"]["s_lab"] ** 2 + sp["s_pop"] ** 2
            k = s * s / (s * s + s_ref2)
            m = k * self.meth_mobs + math.sqrt(k * s_ref2) * th["zm"]
        return b * m - 0.5 * b * b * s * s

    def draw(self) -> dict:
        rng, pp = self.rng, self.pp
        th = {"dom": {}, "zc": {}, "x": {}, "shift": {}, "zx": {}}
        for did, sp in self.specs.items():
            th["dom"][did] = DM.draw_params(sp, rng, self.region)
            th["zc"][did] = rng.gauss(0.0, 1.0)
            nb = DM.norm_for(sp, self.sex, self.age)
            th["shift"][did] = rng.gauss(0.0, nb.get("mean_se", 0.0)) if nb.get("mean_se") else 0.0
            v = self.I.values.get(did)
            if v is None:
                x = DM.draw_from_population(sp, self.sex, self.age, rng)
                th["x"][did] = x + th["shift"][did] if (isinstance(x, float) and sp.get("norm_kind") != "categorical_mid") else x
            elif sp["shape"] == "categorical":
                th["x"][did] = v["x"]
            elif sp.get("norm_kind") == "categorical_mid":
                th["x"][did] = max(0.0, rng.gauss(v["x"], v["sd"])) if v["sd"] else v["x"]
            else:
                x = v["x"]
                if v.get("device"):
                    x += rng.gauss(v["device"]["bias"], v["device"]["bias_sd"])
                th["x"][did] = rng.gauss(x, v["sd"]) if v["sd"] else x
        gc = pp["calibration"]["gap"]
        th["gap_cal"] = {"knots": gc["knots"], "slopes": [rng.gauss(m, s) for m, s in zip(gc["slopes"], gc["slopes_sd"])]}
        s2 = pp["frailty"]["s2"]
        th["s2"] = min(max(rng.gauss(s2["value"], s2["sd"]), 0.06), 0.35)
        th["zG"] = rng.gauss(0.0, 1.0)
        th["zr"] = rng.gauss(0.0, 1.0)
        th["zm"] = rng.gauss(0.0, 1.0)
        th["beta_m"] = rng.gauss(self.meth_spec["beta"], self.meth_spec["beta_se"])
        for did in self.specs:
            th["zx"][did] = rng.gauss(0.0, 1.0)   # measurement noise of a hypothetical new test (data_value)
        return th

    def log_r(self, th: dict, override: Optional[Dict[str, Callable]] = None, direct: float = 0.0, parts: bool = False,
              meth: bool = True):
        cal = self.pp["calibration"][self.coef_set]
        if self.has_clock:
            out = {"clock": gap_loghr(self.gap_mean + th["zG"] * self.gap_sd, th["gap_cal"])}
        else:   # no blood test: what one would show, drawn from its NHANES spread given everything else
            s = self.clock_resid_sd
            out = {"clock": -0.5 * s * s + s * th["zr"]}
        for did, sp in self.specs.items():
            x = th["x"][did]
            if override and did in override:
                x = override[did](x)
            c = cal[did]["value"] + th["zc"][did] * cal[did]["sd"]
            out[did] = c * DM.log_hr(sp, th["dom"][did], x, self.sex, self.age, shift=th["shift"][did])
        if meth:
            out["methylation"] = self.meth_term(th)
        tot = sum(out.values()) + direct
        return (tot, out) if parts else tot

    def outcomes(self, R: float, s2: float, scen: str, curve: bool = False) -> dict:
        s = M.individual_survival(self.s_ref[scen], R, s2)
        sr = self.s_ref[scen]
        p = {m: M.at_age(self.ages, s, m) for m in MILESTONES}
        pr = {m: M.at_age(self.ages, sr, m) for m in MILESTONES}
        idx = 100 + 10 * math.log10(max(p[120], 1e-300) / max(pr[120], 1e-300))
        out = {"p": p, "index": idx, "le": M.life_expectancy(self.ages, s)}
        if curve:
            out["surv"] = s
        return out


# ------------------------------------------------------------------ interventions

def _adhere(iv: dict, rng: random.Random) -> float:
    """Fraction of the full effect achieved in this draw."""
    a = iv["adherence"]
    if iv.get("adherence_kind", "fraction") == "bernoulli":
        return 1.0 if rng.random() < a else 0.0
    k = iv.get("adherence_concentration", 4.0)   # Beta(a*k, (1-a)*k), mean a
    return rng.betavariate(max(a * k, 1e-3), max((1 - a) * k, 1e-3))


def intervention_effect(iv: dict, rng: random.Random) -> Tuple[Dict[str, Callable], float]:
    f = _adhere(iv, rng)
    overrides: Dict[str, Callable] = {}
    direct = 0.0
    for eff in iv["effects"]:
        if eff.get("type") == "direct":
            rr = eff["rr"]
            lr = rng.gauss(math.log(rr["value"]), (math.log(rr["hi"]) - math.log(rr["lo"])) / 3.92)
            direct += f * lr
            continue
        did = eff["domain"]
        if eff.get("set") is not None:
            if f >= 0.5:
                overrides[did] = (lambda v: (lambda x: v))(eff["set"])
            continue
        d = f * rng.gauss(eff["mean"], eff["sd"])
        lo, hi, rel = eff.get("floor"), eff.get("ceiling"), eff.get("relative", False)

        def fn(x, d=d, lo=lo, hi=hi, rel=rel):
            y = x * (1 + d) if rel else x + d
            if lo is not None and x >= lo:
                y = max(y, lo)
            if hi is not None and x <= hi:
                y = min(y, hi)
            return y
        prev = overrides.get(did)
        overrides[did] = (lambda g, h: (lambda x: h(g(x))))(prev, fn) if prev else fn
    return overrides, direct


def applicable(model: Model, iv: dict) -> bool:
    for did, rule in iv.get("when", {}).items():
        v = model.I.values.get(did)
        if v is None:
            if rule.get("require_measured", True):
                return False
            continue
        x = v["x"]
        if "in" in rule and x not in rule["in"]:
            return False
        if "min" in rule and isinstance(x, (int, float)) and x < rule["min"]:
            return False
        if "max" in rule and isinstance(x, (int, float)) and x > rule["max"]:
            return False
    return True


# ------------------------------------------------------------------ run

def run(person: dict, derived: dict, n_draws: int = 2000, seed: int = 20261024) -> dict:
    m = Model(person, derived, n_draws, seed)
    pp = m.pp
    sc_keys = list(m.scen["defs"])
    central = m.scen["central"]
    ivs = [iv for iv in pp["interventions"] if applicable(m, iv)]
    core = [iv for iv in ivs if iv.get("core")]
    rng_iv = random.Random(seed + 1)
    draws = []
    for _ in range(m.n):
        th = m.draw()
        lr, parts = m.log_r(th, parts=True)
        rec = {"th": th, "lr": lr, "parts": parts, "iv": {}}
        combo_ov: Dict[str, Callable] = {}
        combo_direct = 0.0
        for iv in ivs:
            ov, dr = intervention_effect(iv, rng_iv)
            rec["iv"][iv["id"]] = m.log_r(th, ov, dr) if (ov or dr) else lr
            if iv.get("core"):
                for did, fn in ov.items():
                    g = combo_ov.get(did)
                    combo_ov[did] = (lambda g, h: (lambda x: h(g(x))))(g, fn) if g else fn
                combo_direct += dr
        if core:
            rec["iv"]["core"] = m.log_r(th, combo_ov, combo_direct) if (combo_ov or combo_direct) else lr
        draws.append(rec)
    res = summarise(m, draws, ivs, core, sc_keys, central)
    alt = clock_alternative(m, derived, seed)
    if alt:
        alt["shift_vs_main"] = round(alt["value"]["median"] - res["longpi_age"]["value"]["median"], 1)
    res["longpi_age"]["clock_alternative"] = alt
    res["asks_default"] = default_asks(m, res)
    return res


def default_asks(m: Model, res: dict) -> dict:
    """The "please add" list the report shows unless the narrative writes its own (narrative.asks).

    Always: body and face photos, a short questionnaire. Conditional: waist (none in the last 3 months),
    diet photos (no meal log), snoring (BMI >= 28), and the low-cost items of the data-value menu with
    their effect on the interval; a fasting blood test when a test was flagged or the clock is missing."""
    spec = m.pp["asks"]
    it = spec["items"]
    dv = res["data_value"]
    out = [dict(it["body_photo"]), dict(it["face_photo"])]
    anth = [a for a in m.person.get("anthropometrics", []) if a.get("waist_cm")]
    if not any((m.as_of - parse_date(a["date"])).days <= 92 for a in anth):
        out.append(dict(it["waist"]))
    if not m.person.get("meals"):
        out.append(dict(it["diet_photo"]))
    bmi = (m.I.values.get("adiposity") or {}).get("x")
    if isinstance(bmi, float) and bmi >= 28:
        out.append(dict(it["snoring"]))
    hw = lambda w: f"±{w / 2:.1f}"
    by_id = {i["id"]: i for i in dv["items"]}
    for aid in ("dom:muscle", "dom:bp", "dom:crf"):
        if aid in by_id:
            a = dict(it[aid])
            a["why"] = f"做完这一项，LongPi Age 的 80% 区间可从 {hw(dv['width_now'])} 岁缩到约 {hw(by_id[aid]['width_after'])} 岁。"
            out.append(a)
    for aid in ("dom:smoking", "dom:alcohol", "dom:sleep", "dom:adiposity"):
        if aid in by_id:
            out.append({"item": by_id[aid]["label"], "when": "今天", "how": [],
                        "why": f"LongPi Age 的 80% 区间可从 {hw(dv['width_now'])} 岁缩到约 {hw(by_id[aid]['width_after'])} 岁。"})
    alt = res["longpi_age"].get("clock_alternative")
    blood_ids = [x for x in ("blood_panel", "hs_crp", "blood_repeat", "dom:lipid", "dom:glucose") if x in by_id]
    if alt or blood_ids:
        a = dict(it["blood"])
        why = []
        if alt:
            why.append(f"已有血检中有异常期的结果（{'；'.join(sorted({c['date'] for c in alt['changes']}))}），按异常期处理后 LongPi Age 约 {alt['value']['median']} 岁，"
                       f"与首页结果相差 {alt['shift_vs_main']:+} 岁；一次状态正常时的抽血能确定哪个更接近真实")
        if blood_ids:
            best = max(blood_ids, key=lambda x: by_id[x]["narrows_by"])
            why.append(f"LongPi Age 的 80% 区间可从 {hw(dv['width_now'])} 岁缩到约 {hw(by_id[best]['width_after'])} 岁")
        a["why"] = "；".join(why) + "。"
        out.append(a)
    if "methylation" in by_id:
        a = dict(it["methylation"])
        a["why"] = f"80% 区间可从 {hw(dv['width_now'])} 岁缩到约 {hw(by_id['methylation']['width_after'])} 岁；费用较高，可在免费项目之后考虑。"
        out.append(a)
    out.append(dict(it["questionnaire"]))
    return {"title": spec["title"], "subtitle": spec["subtitle"], "note": spec["note"], "items": out}


FLAG_ACTION = {"acute_inflammation": (True, "急性炎症（hs-CRP 高于 10 mg/L），整次不计入血液时钟"),
               "rbc_abnormal": (["mcv", "rdw"], "红细胞指标异常（MCV 或 RDW 超出参考范围，如缺铁、贫血恢复期），不计入 MCV、RDW")}


def clock_alternative(m: Model, derived: dict, seed: int, n: int = 800) -> Optional[dict]:
    """LongPi Age if the flagged blood tests are handled as the flag suggests (main result unchanged).

    Shown next to the main number so a reader sees how much an illness- or anaemia-period test moves it."""
    flagged = [p for p in m.pheno if p["flags"]]
    if not flagged:
        return None
    import copy
    person = copy.deepcopy(m.person)
    changes = []
    for p in flagged:
        lab = next(l for l in person["labs"] if parse_date(l["date"]).isoformat() == p["date"])
        for f in p["flags"]:
            how, why = FLAG_ACTION[f]
            if how is True:
                lab["clock_exclude"] = True
            elif lab.get("clock_exclude") is not True:
                lab["clock_exclude"] = sorted(set(lab.get("clock_exclude") or []) | set(how))
            changes.append({"date": p["date"], "flag": f, "action": why})
    alt = Model(person, derived, n_draws=n, seed=seed + 7)
    lrs = [alt.log_r(alt.draw()) for _ in range(n)]
    pt = math.log(_point_R(lrs)) / alt.b
    vals = [alt.age + x / alt.b for x in lrs]
    return {"changes": changes, "has_clock": alt.has_clock, "value": summ(vals, 1, alt.age + pt),
            "shift_vs_main": None}


def _point_R(lrs: Sequence[float]) -> float:
    return statistics.fmean(math.exp(x) for x in lrs)


def summarise(m: Model, draws: List[dict], ivs: List[dict], core: List[dict], sc_keys: List[str], central: str) -> dict:
    pp = m.pp
    lrs = [d["lr"] for d in draws]
    R_bar = _point_R(lrs)
    s2_bar = statistics.fmean(d["th"]["s2"] for d in draws)
    gap_point = math.log(R_bar) / m.b
    gaps = [x / m.b for x in lrs]
    la_vals = [m.age + g for g in gaps]
    domains = []
    for did, sp in m.specs.items():
        v = m.I.values.get(did)
        yrs = [d["parts"][did] / m.b for d in draws]
        pt = math.log(statistics.fmean(math.exp(d["parts"][did]) for d in draws)) / m.b
        domains.append({"id": did, "domain": sp["name_zh"], "measured": v is not None,
                        "input": None if v is None else (round(v["x"], 2) if isinstance(v["x"], float) else v["x"]),
                        "source": None if v is None else v["src"], "years": summ(yrs, 2, pt),
                        "hr": summ([math.exp(y * m.b) for y in yrs], 3, math.exp(pt * m.b))})
    clock_yrs = [d["parts"]["clock"] / m.b for d in draws]
    clock_pt = math.log(statistics.fmean(math.exp(d["parts"]["clock"]) for d in draws)) / m.b
    meth_yrs = [d["parts"]["methylation"] / m.b for d in draws]
    meth_pt = math.log(statistics.fmean(math.exp(d["parts"]["methylation"]) for d in draws)) / m.b
    # scenarios: point from E[R]; intervals from draws (subsample for speed)
    sub = draws[:: max(1, len(draws) // 600)]
    scen = {}
    weights = pp["scenarios"]["weights"]
    w_idx_draws = [0.0] * len(sub)
    for k in sc_keys:
        sc = pp["scenarios"]["defs"][k]
        pt = m.outcomes(R_bar, s2_bar, k, curve=True)
        dd = [m.outcomes(math.exp(d["lr"]), d["th"]["s2"], k, curve=True) for d in sub]
        for i, o in enumerate(dd):
            w_idx_draws[i] += weights[k] * o["index"]
        sr = m.s_ref[k]
        nA = len(m.ages)
        scen[k] = {
            "name": sc["name_zh"], "desc": sc["desc_zh"],
            "index": summ([o["index"] for o in dd], 1, pt["index"]),
            "p120": summ([o["p"][120] for o in dd], 14, pt["p"][120]),
            "milestones": {str(x): summ([o["p"][x] for o in dd], 6, pt["p"][x]) for x in MILESTONES},
            "ref_milestones": {str(x): M.at_age(m.ages, sr, x) for x in MILESTONES},
            "life_exp": summ([o["le"] for o in dd], 1, pt["le"]),
            "ref_life_exp": round(M.life_expectancy(m.ages, sr), 1),
            "curve": {"ages": [round(a, 1) for a in m.ages],
                      "median": [round(x, 10) for x in pt["surv"]],
                      "p10": [round(q([o["surv"][j] for o in dd], 0.1), 10) for j in range(nA)],
                      "p90": [round(q([o["surv"][j] for o in dd], 0.9), 10) for j in range(nA)],
                      "ref": [round(x, 10) for x in sr]},
        }
    w_point = sum(weights[k] * scen[k]["index"]["median"] for k in sc_keys)
    # interventions: expected change (adherence included), interval and P(benefit)
    thr = pp["benefit_threshold_years"]
    iv_out = []
    base_c = m.outcomes(R_bar, s2_bar, central)
    cp = pp["core_plan"]
    for iv in ivs + ([{"id": "core", "name_zh": cp["name_zh"], "domain": "综合", "evidence": cp["evidence"],
                       "evidence_note_zh": cp["evidence_note_zh"], "verify_zh": cp["verify_zh"], "verify_weeks": 12,
                       "adherence": None, "medical": False, "safety_zh": "", "modifiers": [], "sources": []}] if core else []):
        quant = iv["evidence"] in ("A", "B", "C") and iv["id"] != "nmn"
        out = {"id": iv["id"], "name": iv["name_zh"], "domain": iv["domain"], "evidence": iv["evidence"],
               "evidence_note": iv["evidence_note_zh"], "modifiers": iv.get("modifiers", []), "verify": iv["verify_zh"],
               "verify_weeks": iv.get("verify_weeks"), "safety": iv.get("safety_zh", ""), "medical": iv.get("medical", False),
               "adherence": iv.get("adherence"), "quantified": quant, "sources": iv.get("sources", [])}
        if quant:
            after = [d["iv"][iv["id"]] for d in draws]
            dl = [(a - b) / m.b for a, b in zip(after, lrs)]
            R_after = _point_R(after)
            d_pt = (math.log(R_after) - math.log(R_bar)) / m.b
            o2 = m.outcomes(R_after, s2_bar, central)
            out.update({"d_longpi_age": summ(dl, 2, d_pt),
                        "p_benefit": round(sum(1 for x in dl if x <= -thr) / len(dl), 2),
                        "d_index_central": {"median": round(o2["index"] - base_c["index"], 1)},
                        "d_life_exp_central": round(o2["le"] - base_c["le"], 2)})
        else:
            out.update({"d_longpi_age": None, "p_benefit": None, "d_index_central": None, "d_life_exp_central": None})
        if quant and iv["id"] != "core" and out["d_longpi_age"]["median"] > -0.05 and out["p_benefit"] < 0.2:
            out["small_effect"] = True   # applies, but does almost nothing for this person
        iv_out.append(out)
    pheno = [{k: p[k] for k in ("date", "age", "phenoage", "ref_phenoage", "gap", "noise_sd", "crp_imputed", "left_out", "flags", "values", "top_noise")}
             for p in m.pheno]
    traj = trajectory(m)
    gc = pp["calibration"]["gap"]
    return {
        "engine_version": ENGINE_VERSION, "params_version": pp["version"], "as_of": m.as_of.isoformat(),
        "person": {"code": m.person["person"].get("code", ""), "sex": m.sex, "chrono_age": round(m.age, 1)},
        "gompertz_b": round(m.b, 4),
        "longpi_age": {
            "value": summ(la_vals, 1, m.age + gap_point), "delta": summ(gaps, 1, gap_point), "chrono": round(m.age, 1),
            "clock_delta": summ(clock_yrs, 2, clock_pt),
            "methylation_delta": summ(meth_yrs, 2, meth_pt),
            "function_delta": summ([g - c - x for g, c, x in zip(gaps, clock_yrs, meth_yrs)], 2, gap_point - clock_pt - meth_pt),
            "coef_set": m.coef_set, "domains": domains,
            "clock": {"measured": m.has_clock, "phenoage_points": pheno, "excluded_tests": excluded_blood_tests(m.person, m.at), "gap_now_mean": round(m.gap_mean, 2), "gap_now_sd": round(m.gap_sd, 2),
                      "years_per_gap_year_central": round(gc["slopes"][1] / m.b, 3),
                      "unmeasured_sd_years": None if m.has_clock else round(m.clock_resid_sd / m.b, 2)},
            "methylation": methylation_summary(m),
            "trajectory": traj["points"], "pace": traj["pace"],
        },
        "index120": {"scenarios": scen, "weights": weights, "weighted_index": summ(w_idx_draws, 1, w_point), "central": central},
        "interventions": iv_out,
        "inputs_used": {k: {"value": round(v["x"], 2) if isinstance(v["x"], float) else v["x"], "source": v["src"]} for k, v in m.I.values.items()},
        "clinical": clinical.summary(m.person, m.sex, m.age, {k: {"value": v["x"]} for k, v in m.I.values.items()}),
        "missing_domains": [m.specs[d]["name_zh"] for d in m.specs if d not in m.I.values],
        "data_value": data_value(m),
    }


def trajectory(m: Model) -> dict:
    """LongPi Age at each past blood test (checkup-type inputs as of that date) and LongPi Pace."""
    cfg = m.pp["pace"]
    pts = []
    for i, p in enumerate(m.pheno):
        d = parse_date(p["date"])
        mm = Model(m.person, m.derived, 300, 1000 + i, at=d, snapshot=True)
        lrs = [mm.log_r(mm.draw()) for _ in range(mm.n)]
        gap = math.log(_point_R(lrs)) / mm.b
        sd = statistics.pstdev(x / mm.b for x in lrs)
        pts.append({"date": p["date"], "age": round(mm.age, 1), "longpi_age": round(mm.age + gap, 1), "delta": round(gap, 2),
                    "sd": round(sd, 2), "noise_sd": cfg["obs_sd_years"], "t": decimal_year(d)})
    out = {"n": len(pts), "min_n": cfg["min_n"], "min_info_gain": cfg["min_info_gain"]}
    span = (pts[-1]["t"] - pts[0]["t"]) if len(pts) >= 2 else 0.0
    out["span_years"] = round(span, 1)
    r = max(0.25, cfg["obs_sd_years"] ** 2)

    def post_sd(times):
        if len(times) < 2:
            return cfg["prior_slope_sd"]
        t_bar = sum(times) / len(times)
        sxx = sum((t - t_bar) ** 2 for t in times)
        return (1 / cfg["prior_slope_sd"] ** 2 + sxx / r) ** -0.5

    times = [p["t"] for p in pts]
    gain = 1 - post_sd(times) / cfg["prior_slope_sd"]
    out["info_gain"] = round(gain, 3)
    if len(pts) >= 2:
        obs = [{"t": p["t"], "gap": p["delta"], "r": r} for p in pts]
        slope, sd = clock.trend_posterior(obs, cfg["prior_slope_sd"], cfg["prior_level_sd"])
        out.update({"slope": round(slope, 3), "slope_sd": round(sd, 3), "pace": round(1 + slope, 2),
                    "pace_p10": round(1 + slope - 1.2816 * sd, 2), "pace_p90": round(1 + slope + 1.2816 * sd, 2)})
    need, future = 0, list(times) or [decimal_year(m.as_of)]
    while 1 - post_sd(future) / cfg["prior_slope_sd"] < cfg["min_info_gain"] and need < 30:
        future.append(future[-1] + 1.0)
        need += 1
    out["more_annual_tests_needed"] = need
    out["status"] = "reported" if (len(pts) >= cfg["min_n"] and gain >= cfg["min_info_gain"]) else "insufficient"
    for p in pts:
        p.pop("t", None)
    return {"points": pts, "pace": out}


def methylation_summary(m: Model) -> dict:
    mp = m.pp["methylation"]
    sp = m.meth_spec
    out = {"counted": m.meth_mobs is not None, "counted_clocks": mp["counted"],
           "unmeasured_sd_years": round(sp["beta"] * sp["sd_resid"] / m.b, 2),
           "nhanes": {k: sp[k] for k in ("hr_per_sd_resid", "c_gain", "hr_per_sd_alone")},
           "not_counted": mp["not_counted"]}
    if m.meth:
        out.update({k: m.meth[k] for k in ("clock", "value", "age_at_test", "accel", "expected_accel", "resid", "date", "vendor") if k in m.meth})
    others = [r for r in (m.person.get("methylation") or []) if not (m.meth and r.get("date") == m.meth["date"]
                                                                    and str(r.get("clock_type", "")).lower() == m.meth["clock"].lower())]
    if others:
        out["provided_not_counted"] = [{"clock_type": r.get("clock_type", ""), "date": r.get("date", ""), "vendor": r.get("vendor", "")} for r in others]
    return out


# ------------------------------------------------------------------ value of more data

class _Action:
    """A hypothetical new measurement. `patch` changes model-level state, `mod` changes one draw."""

    def __init__(self, aid: str, status: str, patch: Optional[Callable] = None, mod: Optional[Callable] = None):
        self.id, self.status, self.patch, self.mod = aid, status, patch, mod


def _typical(m: Model, did: str, th: dict):
    """A typical result for a domain not yet measured (its population centre)."""
    sp = m.specs[did]
    nb = DM.norm_for(sp, m.sex, m.age)
    if sp.get("norm_kind") == "categorical_mid":
        return float(sp["mids"][m.sex][max(nb["p"], key=nb["p"].get)])
    if sp["shape"] == "categorical":
        return "pop:" + max(nb["p"], key=nb["p"].get)
    return nb["mean"] + th["shift"][did]


def _dom_mod(did: str) -> Callable:
    """Measure the domain with the best practical method: device error and bias uncertainty go, the method's own
    noise stays; an unmeasured domain takes a typical value. The population-reference uncertainty stays."""
    def mod(m: Model, th: dict) -> None:
        dm = m.pp["data_menu"]
        v = m.I.values.get(did)
        x = _typical(m, did, th) if v is None else v["x"] + (v["device"]["bias"] if v.get("device") else 0.0)
        if isinstance(x, float):
            sd = dm["after_sd"].get(did)
            if sd is None:
                sd = dm["after_cv"].get(did, 0.0) * abs(x)
            x += sd * th["zx"][did]
            if m.specs[did].get("norm_kind") == "categorical_mid":
                x = max(0.0, x)
        th["x"][did] = x
    return mod


def _typical_blood_r(m: Model) -> float:
    return clock.noise_sd(m.pp["data_menu"]["typical_blood"])[0] ** 2


def _patch_blood_panel(m: Model) -> None:
    m.has_clock, m.coef_set = True, "with_clock"
    m.gap_mean, m.gap_sd = m.gap_posterior([{"t": m.year0, "gap": 0.0, "r": _typical_blood_r(m)}])


def _patch_hs_crp(m: Model) -> None:
    extra = m.pp["clock"]["crp_impute_extra_var"]
    pts = [dict(p, r=p["r"] - extra) if p.get("crp_imputed") and i == len(m.pheno) - 1 else p for i, p in enumerate(m.pheno)]
    m.gap_mean, m.gap_sd = m.gap_posterior(pts)


def _patch_blood_repeat(m: Model) -> None:
    last = m.pheno[-1]
    r = last["r"] - (m.pp["clock"]["crp_impute_extra_var"] if last.get("crp_imputed") else 0.0)
    m.gap_mean, m.gap_sd = m.gap_posterior(m.pheno + [{"t": m.year0, "gap": m.gap_mean, "r": r}])


def _patch_methylation(m: Model) -> None:
    mp = m.pp["methylation"]
    m.meth_spec, m.meth_mobs = mp["clocks"][mp["default_unmeasured"]], 0.0


def _actions(m: Model) -> List[_Action]:
    acts = []
    if not m.has_clock:   # the nine-item panel includes fasting glucose, which also gives the glucose domain
        acts.append(_Action("blood_panel", "未做", patch=_patch_blood_panel,
                            mod=_dom_mod("glucose") if m.I.values.get("glucose") is None else None))
    else:
        if m.pheno[-1].get("crp_imputed"):
            acts.append(_Action("hs_crp", "最近一次缺 hs-CRP，按人群中位数补入", patch=_patch_hs_crp))
        acts.append(_Action("blood_repeat", f"已有 {len(m.pheno)} 次", patch=_patch_blood_repeat))
    if m.meth_mobs is None:
        had = bool(m.person.get("methylation"))
        acts.append(_Action("methylation", "已做，但报告里没有 GrimAge2 / GrimAge，不计入" if had else "未做", patch=_patch_methylation))
    for did in m.specs:
        v = m.I.values.get(did)
        if v is None:
            acts.append(_Action("dom:" + did, "未测", mod=_dom_mod(did)))
        elif v.get("device") and did == "crf":   # a watch VO2max can be replaced by CPET; watch RHR/sleep have no better routine method
            acts.append(_Action("dom:" + did, "手表估算", mod=_dom_mod(did)))
        elif did in ("bp", "rhr") and v.get("kind") == "office":
            acts.append(_Action("dom:" + did, "只有体检时测的一两次", mod=_dom_mod(did)))
    return acts


def _width(m: Model, acts: List[_Action], n: int) -> float:
    """80% interval width of LongPi Age if `acts` were done; the same random draws for every call."""
    saved = (m.rng, m.has_clock, m.coef_set, m.gap_mean, m.gap_sd, m.meth_spec, m.meth_mobs)
    m.rng = random.Random(7)
    try:
        for a in acts:
            if a.patch:
                a.patch(m)
        vals = []
        for _ in range(n):
            th = m.draw()
            for a in acts:
                if a.mod:
                    a.mod(m, th)
            vals.append(m.log_r(th) / m.b)
    finally:
        m.rng, m.has_clock, m.coef_set, m.gap_mean, m.gap_sd, m.meth_spec, m.meth_mobs = saved
    return q(vals, 0.9) - q(vals, 0.1)


def data_value(m: Model) -> dict:
    """How much each further test would narrow the 80% interval of LongPi Age, and how complete the data are.

    width_none: age and sex only; width_now: the data given; width_all: every listed test done.
    completeness = (width_none - width_now) / (width_none - width_all): weighted by information, not by count."""
    dm = m.pp["data_menu"]
    n = dm["n_draws"]
    acts = _actions(m)
    w_now = _width(m, [], n)
    items = []
    for a in acts:
        spec = dm["actions"][a.id]
        key = {"未测": "label_missing", "手表估算": "label_device"}.get(a.status, "label_better" if a.id.startswith("dom:") else "label")
        w = _width(m, [a], n)
        items.append({"id": a.id, "status": a.status, "label": spec.get(key) or spec.get("label") or spec.get("label_missing"),
                      "detail": spec.get("detail", ""), "effort": spec.get("effort", ""), "cost": spec.get("cost", ""),
                      "also": spec.get("also", ""), "width_after": round(w, 2), "narrows_by": round(w_now - w, 2)})
    w_all = _width(m, acts, n) if acts else w_now
    none = Model({"as_of": m.as_of.isoformat(), "person": {"sex": m.sex, "age": m.age}}, {}, n_draws=n, seed=7)
    w_none = _width(none, [], n)
    pct = 100.0 if w_none - w_all <= 1e-9 else min(100.0, max(0.0, 100 * (w_none - w_now) / (w_none - w_all)))
    w = m.person.get("wearables") or {}
    have = {"cgm": bool(w.get("cgm_csv")), "genetics": bool(m.person.get("genetics")),
            "imaging": bool(m.person.get("imaging")), "meals": bool(m.person.get("meals"))}
    return {"width_none": round(w_none, 2), "width_now": round(w_now, 2), "width_all": round(w_all, 2),
            "completeness_pct": round(pct), "n_draws": n,
            "items": sorted([i for i in items if i["narrows_by"] >= dm["show_min_years"]], key=lambda i: -i["narrows_by"]),
            "small_items": [i["id"] for i in items if i["narrows_by"] < dm["show_min_years"]],
            "other_uses": [dict(o, have=have.get(o["key"], False)) for o in dm["other_uses"]]}
