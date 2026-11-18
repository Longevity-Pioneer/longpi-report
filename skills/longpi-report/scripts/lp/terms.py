"""Registry terms beyond the 1.1.1 model (ext.*): matching, coefficients, overlap groups, guardrails, draws.

For a counted term i and outcome o, in one Monte Carlo draw:

    l_i,o = c_i,o * ( f_o(x_i) - ln E_ref[exp f_o(X)] )

  f_o      log HR curve of the term for outcome o (shape: loglinear, hinge, categorical, residualized, indicator);
           slopes drawn from the reported 95% CI, shrunk for transport from non-East-Asian cohorts
  E_ref    expectation over the term's reference distribution for the person's sex and age (keeps peers at R = 1)
  x_i      current level from lp.longitudinal (all usable observations), drawn with its uncertainty
  c_i,o    overlap coefficient (term spec, 0-1, drawn), x (1 - mediated fraction) when mediators are measured,
           x 0.7 outside the study's age range, x self-report discount for behaviours; then the overlap-group rule

Unmeasured ext terms are not in the model at all (no population draw), so a growing registry never widens anyone's
interval. Guardrails (registry/groups.json): for LongPi Age each ext term is clamped to +-0.15 and their sum to +-0.30 on
the log-hazard scale; behaviour terms of the 120 Index have their own caps.
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Tuple

from . import domains as DM
from . import longitudinal as LG
from . import registry as RG

Z95 = 1.959964
DEFAULT_EXCLUDE = {"state": ["acute_illness", "pregnancy", "transfusion"], "exposure": [], "behavior": [], "genetic": []}


def _band(rows: List[dict], sex: str, age: float) -> Optional[dict]:
    cand = [r for r in rows if r.get("sex", sex) in (sex, "both")]
    if not cand:
        return None
    for r in cand:
        if r.get("age_lo", -1) <= age <= r.get("age_hi", 999):
            return r
    return min(cand, key=lambda r: min(abs(age - r.get("age_lo", age)), abs(age - r.get("age_hi", age))))


def ref_moments(t: dict, sex: str, age: float) -> Optional[Tuple[float, float]]:
    """(mean, sd) of the reference distribution on the scale the curve is applied to (ln x when log_x / lognormal)."""
    ref = t["reference"]
    if ref.get("by_sex_age"):
        b = _band(ref["by_sex_age"], sex, age)
        if not b:
            return None
        if "meanlog" in b:
            return b["meanlog"], b["sdlog"]
        if "mean" in b:
            return b["mean"], b["sd"]
        return None
    if "meanlog" in ref:
        return ref["meanlog"], ref["sdlog"]
    if "mean" in ref and "sd" in ref:
        return ref["mean"], ref["sd"]
    return None


def _eff(e: dict) -> dict:
    """An effect block, with `derived` (hr = from.hr ** pow; bounds swap when pow < 0) resolved."""
    if "hr" in e or not e.get("derived"):
        return e
    d = e["derived"]
    k = float(d["pow"])
    f = d["from"]
    lo, hi = f["lo"] ** k, f["hi"] ** k
    return dict(e, hr=f["hr"] ** k, lo=min(lo, hi), hi=max(lo, hi))


def _se(e: dict, inflate: float) -> float:
    return (math.log(e["hi"]) - math.log(e["lo"])) / (2 * Z95) * inflate


def _draw_log(e: dict, rng: Optional[random.Random], shrink: float, inflate: float) -> float:
    m = math.log(e["hr"]) * shrink
    return m if rng is None else rng.gauss(m, _se(e, inflate) * shrink)


def draw_effect(t: dict, oc: str, rng: Optional[random.Random]) -> dict:
    e = t["effect"][oc]
    tr = e.get("transport") or t.get("transport") or {}
    shrink, infl = float(tr.get("shrink", 1.0)), float(tr.get("sd_inflate", 1.0))
    e = _eff(e)
    shape = t["transform"]["shape"]
    if shape in ("loglinear", "residualized"):
        return {"beta": _draw_log(e, rng, shrink, infl) / e["per"]}
    if shape == "hinge":
        side = lambda k: (_draw_log(_eff(e[k]), rng, shrink, infl) / _eff(e[k])["per"]) if e.get(k) else 0.0
        return {"b_lo": side("hr_below"), "b_hi": side("hr_above")}
    if shape == "categorical":
        return {"log_rr": {lvl: (0.0 if (v in (1, 1.0) or (isinstance(v, dict) and v.get("hr") == 1 and "lo" not in v))
                                 else _draw_log(_eff(v), rng, shrink, infl))
                           for lvl, v in e["levels"].items()}}
    if shape == "indicator":
        return {"log_rr": _draw_log(e, rng, shrink, infl)}
    raise ValueError(shape)


def f_raw(t: dict, p: dict, x) -> float:
    shape, tf = t["transform"]["shape"], t["transform"]
    if shape == "categorical":
        return p["log_rr"].get(x, 0.0)
    if shape == "indicator":
        return p["log_rr"] * (1.0 if x else 0.0)
    x = float(x)
    if tf.get("log_x"):
        x = math.log(max(x, 1e-9))
    lo, hi = (tf.get("clip") or [None, None])
    if lo is not None:
        x = max(x, lo if not tf.get("log_x") else math.log(max(lo, 1e-9)))
    if hi is not None:
        x = min(x, hi if not tf.get("log_x") else math.log(max(hi, 1e-9)))
    if shape in ("loglinear", "residualized"):
        return p["beta"] * x
    klo = tf.get("knot_lo", tf.get("knot"))
    khi = tf.get("knot_hi", tf.get("knot"))
    return (p["b_lo"] * max(0.0, klo - x) if klo is not None else 0.0) + (p["b_hi"] * max(0.0, x - khi) if khi is not None else 0.0)


def _expect(g, mu: float, sd: float, n: int = 240) -> float:
    """E[g(X)], X ~ N(mu, sd^2), composite Simpson on mu +- 8 sd (robust to clipping kinks, unlike Gauss-Hermite)."""
    if sd <= 0:
        return g(mu)
    a, h = -8.0, 16.0 / n
    tot = 0.0
    for i in range(n + 1):
        z = a + i * h
        w = 1 if i in (0, n) else (4 if i % 2 else 2)
        tot += w * g(mu + sd * z) * math.exp(-0.5 * z * z)
    return tot * h / 3 / math.sqrt(2 * math.pi)


def log_mean_exp_ref(t: dict, p: dict, sex: str, age: float, scale: float = 1.0) -> float:
    """ln E_ref[exp(scale * f(X))]; with scale = the overlap coefficient this keeps E_ref[exp(l)] = 1 exactly."""
    shape, ref = t["transform"]["shape"], t["reference"]
    if shape == "categorical":
        probs = ref["p"] if "p" in ref else (_band(ref["by_sex_age"], sex, age) or {}).get("p", {})
        return math.log(sum(pr * math.exp(scale * p["log_rr"].get(lvl, 0.0)) for lvl, pr in probs.items()))
    if ref.get("kind") == "categorical_mid":
        probs = ref["p"] if "p" in ref else (_band(ref["by_sex_age"], sex, age) or {}).get("p", {})
        mids = ref["mids"]
        if isinstance(next(iter(mids.values())), dict):
            mids = mids.get(sex, next(iter(mids.values())))
        return math.log(sum(pr * math.exp(scale * f_raw(t, p, mids[lvl])) for lvl, pr in probs.items()))
    if shape == "indicator":
        prev = ref.get("prevalence")
        if prev is None and ref.get("by_sex_age"):
            prev = (_band(ref["by_sex_age"], sex, age) or {}).get("prevalence", 0.0)
        prev = float(prev or 0.0)
        return math.log(1 - prev + prev * math.exp(scale * p["log_rr"]))
    mu, sd = ref_moments(t, sex, age)
    tf = t["transform"]
    tt = dict(t, transform=dict(tf, log_x=False, clip=_clip_scale(tf)))   # mean/sd are of ln x when log_x
    if shape in ("loglinear", "residualized"):
        lo, hi = (tt["transform"].get("clip") or [None, None])
        if (lo is None or mu - 6 * sd > lo) and (hi is None or mu + 6 * sd < hi):
            b = scale * p["beta"]
            return b * mu + 0.5 * (b * sd) ** 2                       # closed form when clipping cannot bind
    return math.log(_expect(lambda z: math.exp(scale * f_raw(tt, p, z)), mu, sd))


def _clip_scale(tf: dict):
    c = tf.get("clip")
    if not c or not tf.get("log_x"):
        return c
    return [math.log(max(c[0], 1e-9)) if c[0] is not None else None, math.log(max(c[1], 1e-9)) if c[1] is not None else None]


def normalised(t: dict, p: dict, x, sex: str, age: float, scale: float = 1.0) -> float:
    """scale * f(x) - ln E_ref[exp(scale * f(X))]: coefficient applied before normalising, so peers average R = 1."""
    if t["reference"].get("kind") == "categorical_mid":
        return scale * f_raw(t, p, x) - log_mean_exp_ref(t, p, sex, age, scale)
    if t["transform"].get("log_x") and t["transform"]["shape"] not in ("categorical", "indicator"):
        xx = math.log(max(float(x), 1e-9))
        tf = t["transform"]
        tt = dict(t, transform=dict(tf, log_x=False, clip=_clip_scale(tf)))
        return scale * f_raw(tt, p, xx) - log_mean_exp_ref(t, p, sex, age, scale)
    return scale * f_raw(t, p, x) - log_mean_exp_ref(t, p, sex, age, scale)


# ----------------------------------------------------------------------------- matching

class Term:
    """One ext term as it applies to this person."""

    def __init__(self, spec: dict):
        self.spec, self.id = spec, spec["id"]
        self.kind = spec["kind"]
        self.status = "unmeasured"     # counted / overlap / not_counted / unmeasured / not_sustained / not_eligible
        self.reasons: List[str] = []
        self.level = self.level_sd = self.slope = self.slope_sd = None
        self.value = None              # categorical or indicator value
        self.obs_used: List[dict] = []
        self.coef: Dict[str, Tuple[float, float]] = {}   # outcome -> (mean, sd) after multipliers
        self.notes: List[str] = []
        self.screening: Optional[dict] = None

    def outcomes(self) -> List[str]:
        return list((self.spec.get("effect") or {}).keys())


def _meas_sd(t: dict, o: dict, ref_sd: float) -> float:
    if o.get("sd"):
        return float(o["sd"])
    m = t.get("measurement") or {}
    if m.get("sd_abs"):
        return float(m["sd_abs"])
    if m.get("cv"):
        return float(m["cv"]) * abs(float(o["value"]))
    return 0.05 * abs(float(o["value"])) or 0.05 * ref_sd


def _units_ok(t: dict, o: dict) -> bool:
    want = (t["input"].get("unit") or "").replace(" ", "").lower()
    have = (o.get("unit") or "").replace(" ", "").lower()
    return not want or not have or want == have


def _mediator_measured(key: str, model) -> bool:
    if key.startswith("core."):
        k = key[5:]
        if k == "phenoage_clock":
            return model.has_clock
        if k == "methylation":
            return getattr(model, "meth", None) is not None
        return k in model.I.values
    return model.obs.has(key)


def match(model, reg: Optional[dict] = None) -> List[Term]:
    """All ext terms with a usable observation for this person, with status and coefficients."""
    from .engine import decimal_year, parse_date
    reg = reg or RG.load()
    out: List[Term] = []
    prefs = preferences(model.person)
    for spec in RG.ext_terms(reg):
        T = Term(spec)
        code = spec["input"]["code"]
        if not model.obs.has(code):
            if _absent_means_no(spec, model.person):
                T.value, T.status = 0, "counted"
                T.notes.append("资料中未列出，按“没有”计")
                T.obs_used = [{"code": code, "value": 0, "method": "self_report", "source_file": "问卷（未列出）"}]
                if _finish_coef(T, spec, model, None):
                    out.append(T)
            continue
        if code.startswith("LP:monogenic:") and not prefs["secondary_findings"]:
            T.status, T.reasons = "hidden", ["未选择接收次要发现"]
            out.append(T)
            continue
        if spec.get("disclosure") == "opt_in" and not prefs["show_opt_in"]:
            rule = spec.get("disclosure_rule") or {}
            v = (model.obs.by_code[code][-1] or {}).get("value")
            if "opt_in_if_value_ge" not in rule or (isinstance(v, (int, float)) and v >= rule["opt_in_if_value_ge"]):
                T.status, T.reasons = "hidden", ["该结果默认不展示，本人选择查看后才计入"]
                out.append(T)
                continue
        methods = [{"measured": "lab"}.get(x, x) for x in (spec["input"].get("methods") or [])] or None
        excl = spec.get("exclude_if_flags", DEFAULT_EXCLUDE.get(spec["kind"], []))
        persistent = code.startswith(PERSISTENT_PREFIXES)
        max_years = float("inf") if persistent else float(spec["input"].get("max_age_years", 10))
        rows_all = model.obs.series(code, model.at, methods, (), max_years=max_years)
        rows = [o for o in rows_all if not any(f in excl for f in o.get("flags") or [])]
        if rows_all and not rows:
            T.status, T.reasons = "not_counted", ["可用的数据都处于暂时状态（" + "、".join(sorted({f for o in rows_all for f in o.get("flags") or []})) + "），不计入"]
            out.append(T)
            continue
        if not rows:
            continue
        if spec["input"].get("platform"):
            ok = [o for o in rows if (o.get("platform") or "") in spec["input"]["platform"]]
            if not ok:
                T.status, T.reasons = "not_counted", ["检测平台与研究不一致（研究：" + "、".join(spec["input"]["platform"]) + "）"]
                out.append(T)
                continue
            rows = ok
        if not spec.get("screening"):
            rows = [o for o in rows if _units_ok(spec, o)]
        if not rows:
            T.status, T.reasons = "not_counted", [f"单位与研究不一致（需要 {spec['input'].get('unit')}）"]
            out.append(T)
            continue
        if spec.get("treated_policy", "use_pretreatment") == "use_pretreatment" and "treated" in (rows[-1].get("flags") or []):
            untreated = [o for o in rows if "treated" not in (o.get("flags") or [])]
            if untreated:
                rows = untreated
                T.notes.append("最近的值在用药期间测得，按用药前的值计算")
            else:
                T.notes.append("只有用药期间的值，按测得值计算（可能低估未治疗时的风险）")
        shape = spec["transform"]["shape"]
        T.obs_used = [{k: o.get(k) for k in ("code", "value", "unit", "datetime", "method", "source_file", "flags")} for o in rows]
        if spec.get("screening"):
            T.value = float(rows[-1]["value"])          # years since the last test
        elif shape in ("categorical", "indicator"):
            T.value = rows[-1]["value"]
            if shape == "indicator":
                T.value = 1 if float(T.value) >= 0.5 else 0
        else:
            mo = ref_moments(spec, model.sex, model.age)
            if mo is None and spec["reference"].get("kind") == "categorical_mid":
                mo = _mid_moments(spec, model.sex, model.age)
            if mo is None:
                T.status, T.reasons = "not_counted", ["该性别年龄没有参考分布"]
                out.append(T)
                continue
            ref_sd = mo[1]
            dense = len(rows) > 60
            LG_rows = rows
            if dense:
                from .observations import weekly
                LG_rows = weekly(rows)
            pts = [dict(o, t=decimal_year(parse_date(o["datetime"])) if o.get("datetime") else model.year0) for o in LG_rows]
            sds = [_meas_sd(spec, o, ref_sd) for o in pts]
            if spec["transform"].get("log_x"):   # on the log scale an absolute SD becomes a relative one
                sds = [s / max(abs(float(o["value"])), 1e-9) for s, o in zip(sds, pts)]
                pts = [dict(o, value=math.log(max(float(o["value"]), 1e-9))) for o in pts]
            lg = LG.level_and_slope(pts, sds, model.year0, ref_sd)
            if spec["transform"].get("log_x"):
                T.level, T.level_sd = math.exp(lg["level"]), lg["level_sd"] * math.exp(lg["level"])
            else:
                T.level, T.level_sd = lg["level"], lg["level_sd"]
            if lg.get("slope_informed"):
                T.slope, T.slope_sd = lg["slope"], lg["slope_sd"]
        # behaviour: must be sustained
        if spec["kind"] == "behavior":
            bh = spec.get("behavior") or {}
            weeks = rows[-1].get("sustained_weeks")
            if spec.get("screening"):
                T.screening = _screening_state(spec, model, T.value if T.value is not None else T.level)
                if not T.screening["eligible"]:
                    T.status, T.reasons = "not_eligible", [T.screening["why"]]
                    out.append(T)
                    continue
                if not T.screening["up_to_date"]:
                    T.status, T.reasons = "not_counted", [T.screening["why"]]
                    out.append(T)
                    continue
            elif weeks is None or weeks < bh.get("min_weeks", 8):
                T.status = "not_sustained"
                T.reasons = [f"已持续 {weeks or 0} 周，满 {bh.get('min_weeks', 8)} 周后计入"]
                out.append(T)
                continue
        _finish_coef(T, spec, model, rows[-1])
        out.append(T)
    _apply_groups(out, model, reg)
    return out


def preferences(person: dict) -> dict:
    """Genetic result preferences (PRD §5b.4); both default to False (not shown unless the person chose)."""
    g = person.get("genetic_preferences") or {}
    return {"show_opt_in": bool(g.get("show_opt_in", False)), "secondary_findings": bool(g.get("secondary_findings", False))}


def _finish_coef(T: Term, spec: dict, model, last: Optional[dict]) -> bool:
    """Coefficients (overlap, mediation, age range, sex scope, self-report). Sets T.status; returns True."""
    ov = spec.get("overlap") or {}
    base_m, base_sd = float(ov.get("coef", 1.0)), float(ov.get("coef_sd", 0.0))
    mult, why = 1.0, []
    oc_mult: Dict[str, float] = {}
    med = ov.get("mediated_by") or {}
    frac = sum(v for k, v in med.items() if _mediator_measured(k, model))
    if frac > 0:
        mult *= max(0.0, 1 - frac)
        why.append(f"中介指标已测，按 {1 - frac:.2f} 计")
    for oc in T.outcomes():
        e = spec["effect"][oc]
        pop = dict(spec.get("population") or {}, **(e.get("population") or {}))
        scope = pop.get("sex_scope") or (pop.get("sex") if pop.get("sex") in ("M", "F") else None)
        if scope in ("M", "F") and scope != model.sex:
            oc_mult[oc] = 0.0
            continue
        ar = pop.get("age_range")
        k = 1.0
        if ar and not (ar[0] <= model.age <= ar[1]):
            k = 0.7
            msg = f"年龄不在研究范围 {ar[0]}–{ar[1]} 岁，按 0.7 计"
            if msg not in why:
                why.append(msg)
        oc_mult[oc] = k
    if oc_mult and all(v == 0.0 for v in oc_mult.values()):
        T.status, T.reasons = "not_counted", ["研究只适用于另一性别"]
        return True
    if spec["kind"] == "behavior" and (last or {"method": "self_report"}).get("method") == "self_report":
        d = float((spec.get("behavior") or {}).get("self_report_discount", 0.5))
        mult *= d
        why.append(f"自述行为，按 {d} 计")
    for oc in T.outcomes():
        if oc_mult.get(oc, 1.0) == 0.0:
            continue
        e = spec["effect"][oc]
        cm = float(e["coef"]) if e.get("coef") is not None else base_m
        cs = float(e.get("coef_sd", base_sd)) if e.get("coef") is not None else base_sd
        k = mult * oc_mult.get(oc, 1.0)
        T.coef[oc] = (cm * k, cs * k)
    T.notes += why
    T.status = "counted"
    return True


GRACE = 1.25   # a screening a few weeks past its interval still counts (appointments slip); beyond 1.25x it does not
PERSISTENT_PREFIXES = ("ICD10:", "LP:fh:", "LP:monogenic:", "PGS:", "LP:apoe", "LP:hpylori")


def _requirement_met(req: str, model) -> bool:
    """`CODE` (present) or `CODE=v1|v2` (latest value is one of them)."""
    code, _, vals = req.partition("=")
    if not model.obs.has(code):
        return False
    if not vals:
        return True
    latest = sorted(model.obs.by_code[code], key=lambda o: o.get("datetime") or "")[-1]
    return str(latest.get("value")) in vals.split("|")


def _absent_means_no(spec: dict, person: dict) -> bool:
    """A diagnosis / family-history indicator not listed counts as 0 when the person filled that list."""
    code = spec["input"]["code"]
    if spec["transform"]["shape"] != "indicator":
        return False
    if code.startswith("ICD10:"):
        return "conditions" in person
    if code.startswith("LP:fh:"):
        return "family_history" in person
    return False


def _mid_moments(spec: dict, sex: str, age: float) -> Optional[Tuple[float, float]]:
    ref = spec["reference"]
    probs = ref["p"] if "p" in ref else (_band(ref.get("by_sex_age") or [], sex, age) or {}).get("p")
    if not probs:
        return None
    mids = ref["mids"]
    if isinstance(next(iter(mids.values())), dict):
        mids = mids.get(sex, next(iter(mids.values())))
    mu = sum(pr * mids[k] for k, pr in probs.items())
    var = sum(pr * (mids[k] - mu) ** 2 for k, pr in probs.items())
    return mu, max(var, 1e-6) ** 0.5


def _screening_state(spec: dict, model, years_since) -> dict:
    sc = spec["screening"]
    el = sc.get("eligible") or {}
    ok, why = True, ""
    if el.get("age") and not (el["age"][0] <= model.age <= el["age"][1]):
        ok, why = False, f"适用年龄 {el['age'][0]}–{el['age'][1]} 岁"
    if el.get("sex") in ("M", "F") and el["sex"] != model.sex:
        ok, why = False, "不适用于该性别"
    for req in el.get("requires") or []:
        if not _requirement_met(req, model):
            ok, why = False, el.get("requires_zh") or "只适用于高危人群"
    up = years_since is not None and float(years_since) <= GRACE * float(sc.get("interval_years", 1))
    if ok and not up:
        why = (f"上次筛查距今 {float(years_since):.1f} 年，超过推荐间隔 {sc.get('interval_years')} 年" if years_since is not None
               else "没有筛查记录")
    return {"eligible": ok, "up_to_date": bool(ok and up), "why": why, "years_since": years_since,
            "disease_id": sc.get("disease_id"), "interval_years": sc.get("interval_years")}


def _info(T: Term, oc: str, model) -> float:
    e = _eff(T.spec["effect"][oc])
    if "hr" not in e:
        return 0.5
    shape = T.spec["transform"]["shape"]
    if shape in ("loglinear", "residualized"):
        mo = ref_moments(T.spec, model.sex, model.age)
        return abs(math.log(e["hr"]) / e["per"]) * (mo[1] if mo else 1.0)
    if shape == "indicator":
        return abs(math.log(e["hr"]))
    return 0.5


def _core_coef(cid: str, model) -> Optional[float]:
    if not _mediator_measured(cid, model):
        return None
    k = cid[5:]
    if k in ("phenoage_clock", "methylation"):
        return 1.0
    return float(model.pp["calibration"][model.coef_set][k]["value"])


def _adjusted(T: Term, key: str) -> bool:
    return key in (T.spec.get("adjusted_for") or []) or key in [x.split(":", 1)[-1] for x in (T.spec.get("adjusted_for") or [])]


def _apply_groups(terms: List[Term], model, reg: dict) -> None:
    """PRD §4.2: within a mechanism group, ext terms are ranked by information; a lower-ranked term counts only if its
    study adjusted for every higher-ranked counted ext term; the group's summed coefficients (core + ext) are capped."""
    groups = reg["groups"].get("groups", {})
    for gid, g in groups.items():
        members = [T for T in terms if T.status == "counted" and T.spec.get("group") == gid]
        if not members:
            continue
        ocs = sorted({oc for T in members for oc in T.coef})
        for oc in ocs:
            mem = [T for T in members if oc in T.coef]
            mem.sort(key=lambda T: -_info(T, oc, model) * T.coef[oc][0])
            counted: List[Term] = []
            for T in mem:
                if all(_adjusted(T, U.id) or _adjusted(T, U.spec["input"]["code"]) for U in counted):
                    counted.append(T)
                else:
                    T.coef.pop(oc)
                    T.notes.append(f"与已计入的{counted[0].spec['name_zh']}同属一组，研究未校正它，此结局只作佐证")
            core_sum = 0.0
            if oc == "all_cause":
                core_sum = sum(c for c in (_core_coef(cid, model) for cid in g.get("members_core", [])) if c is not None)
            room = max(0.0, float(g.get("cap", 1.5)) - core_sum)
            tot = sum(T.coef[oc][0] for T in counted)
            if tot > room and tot > 0:
                k = room / tot
                for T in counted:
                    m, s = T.coef[oc]
                    T.coef[oc] = (m * k, s * k)
                    T.notes.append(f"{g['name_zh']}组系数合计超上限，按比例压缩到 {k:.2f}")
        for T in members:
            if not T.coef:
                T.status = "overlap"
                T.reasons = T.reasons or ["与已计入的项重叠，只作佐证"]


# ----------------------------------------------------------------------------- draws

class ExtModel:
    """Counted ext terms and their per-draw contributions. Uses its own random stream."""

    def __init__(self, model, reg: Optional[dict] = None):
        self.m = model
        self.reg = reg or RG.load()
        self.terms = match(model, self.reg)
        self.counted = [T for T in self.terms if T.status == "counted"]
        self.prefs = preferences(model.person)
        gr = self.reg["groups"].get("guardrails", {})
        self.cap_single = float(gr.get("ext_single_abs_log_hr", 0.15))
        self.cap_total = float(gr.get("ext_total_abs_log_hr", 0.30))
        self.bcap_single = float(gr.get("behavior_single_abs_log_hr", 0.35))
        self.bcap_total = float(gr.get("behavior_total_abs_log_hr", 0.50))
        self.dcap_single = float(gr.get("disease_single_abs_log_hr", 1.1))

    def life_terms(self) -> List[Term]:
        """Terms that enter LongPi Age: state/exposure with an all-cause effect."""
        return [T for T in self.counted if T.kind in ("state", "exposure") and "all_cause" in T.coef]

    def behavior_terms(self) -> List[Term]:
        return [T for T in self.counted if T.kind == "behavior" and ("all_cause" in T.coef or T.screening)]

    def draw(self, rng: random.Random) -> dict:
        th = {}
        for T in self.counted:
            d = {"eff": {}, "c": {}}
            for oc, (cm, cs) in T.coef.items():
                d["eff"][oc] = draw_effect(T.spec, oc, rng)
                d["c"][oc] = min(1.0, max(0.0, rng.gauss(cm, cs))) if cs else min(1.0, max(0.0, cm))
            if T.level is not None:
                d["x"] = rng.gauss(T.level, T.level_sd or 0.0)
            else:
                d["x"] = T.value
            if T.screening:
                sc = T.spec["screening"]["mortality_rr"]
                d["screen_log_rr"] = rng.gauss(math.log(sc["hr"]), _se(sc, 1.0))
            th[T.id] = d
        return th

    def contribution(self, T: Term, th: dict, oc: str) -> float:
        d = th[T.id]
        return normalised(T.spec, d["eff"][oc], d["x"], self.m.sex, self.m.age, d["c"][oc])

    def life_parts(self, th: dict) -> Tuple[Dict[str, float], bool]:
        raw = {T.id: self.contribution(T, th, "all_cause") for T in self.life_terms()}
        return _clamp(raw, self.cap_single, self.cap_total)

    def behavior_parts(self, th: dict, age: Optional[float] = None) -> Tuple[Dict[str, float], bool]:
        raw = {}
        for T in self.behavior_terms():
            if T.screening:
                share = screening_share(self.reg, T.screening["disease_id"], self.m.sex, age or self.m.age)
                rr = math.exp(th[T.id]["screen_log_rr"])
                c = th[T.id]["c"].get("all_cause", 1.0) if T.coef else 1.0
                raw[T.id] = c * math.log(max(1e-6, 1 - share * (1 - rr)))
            else:
                raw[T.id] = self.contribution(T, th, "all_cause")
        return _clamp(raw, self.bcap_single, self.bcap_total)

    def disease_parts(self, th: dict, oc: str) -> Dict[str, float]:
        out = {}
        for T in self.counted:
            if oc not in T.coef or T.kind == "behavior":
                continue
            v = self.contribution(T, th, oc)
            if T.spec["transform"]["shape"] != "indicator":
                v = max(-self.dcap_single, min(self.dcap_single, v))
            out[T.id] = v
        return out


def _clamp(raw: Dict[str, float], single: float, total: float) -> Tuple[Dict[str, float], bool]:
    bound = False
    out = {}
    for k, v in raw.items():
        c = max(-single, min(single, v))
        bound |= c != v
        out[k] = c
    s = sum(out.values())
    if abs(s) > total and s != 0:
        k = total / abs(s)
        out = {kk: v * k for kk, v in out.items()}
        bound = True
    return out, bound


def screening_share(reg: dict, disease_id: str, sex: str, age: float) -> float:
    oc = reg["outcomes"].get(disease_id) or {}
    ms = (oc.get("mortality_share") or {}).get("by_sex_age") or []
    b = _band(ms, sex, age)
    return float(b["share"]) if b else 0.0


def spread_years(spec: dict, sex: str, age: float, b: float) -> Optional[float]:
    """How far an unmeasured all-cause term could move LongPi Age (1 SD of its contribution, years)."""
    e = (spec.get("effect") or {}).get("all_cause")
    if not e or spec["transform"]["shape"] not in ("loglinear", "residualized") or spec["kind"] not in ("state", "exposure"):
        return None
    e = _eff(e)
    if "hr" not in e:
        return None
    mo = ref_moments(spec, sex, age)
    if not mo:
        return None
    sh = float((spec.get("transport") or {}).get("shrink", 1.0))
    c = float((spec.get("overlap") or {}).get("coef", 1.0))
    sd = mo[1]
    if spec["transform"].get("log_x"):
        sd = mo[1]
    return round(c * abs(math.log(e["hr"]) * sh / e["per"]) * sd / b, 2)
