"""Disease risk (engine 1.1.2): 10-year ("current") and lifetime risk from one model on two horizons (PRD §6).

For disease d and a person aged a0, year t = 0, 1, ...:

    h_d(t) = h0_d(age_t, sex) * exp( sum_i w_i(t) * l_i,d )       incidence hazard
    risk(H) = sum_{t < H} S(t) * D(t) * (1 - exp(-h_d(t)))          S: the person's all-cause survival (LongPi model)
                                                                   D: still free of d
  h0_d     Chinese incidence by sex and age (registry/outcomes/<d>.json)
  l_i,d    registry terms with an effect for d (lp.terms), drawn per Monte Carlo draw
  w_i(t)   persistence: genetic and exposure terms constant; a current state (glucose, lipids, blood pressure ...)
           fades toward the population average with the term's half-life (default 10 years), so it raises the
           10-year risk more than the lifetime risk; genetic risk acts on the whole curve

Horizons: 10 years ("current risk") and to age `horizon_lifetime_age` (default 90, "lifetime"). A disease already
diagnosed is reported as such, with no risk. Peers: the same calculation with all terms at the population average
(R = 1) and the reference survival.
"""
from __future__ import annotations

import math
import statistics
from typing import Dict, List, Optional

from . import mortality as M
from . import terms as TM


def _rate(oc: dict, sex: str, age: float) -> Optional[float]:
    rows = (oc.get("incidence") or {}).get("by_sex_age") or []
    cand = [r for r in rows if r.get("sex", sex) in (sex, "both")]
    if not cand:
        return None
    if age < min(r["age_lo"] for r in cand):
        return 0.0                        # below the youngest band there is no baseline: counted as 0, not extrapolated
    b = TM._band(rows, sex, age)
    if b is None:
        return None
    unit = (oc.get("incidence") or {}).get("unit", "per_100k_py")
    scale = {"per_100k_py": 1e-5, "per_1000_py": 1e-3, "per_py": 1.0}[unit]
    return float(b["rate"]) * scale


def _weight(T, t: float) -> float:
    """Persistence of a term over the horizon: genetic terms constant; exposures constant unless the spec gives a
    half-life (e.g. smoking risk that fades after quitting); current states fade with their half-life (default 10 y)."""
    hl = (T.spec.get("persistence") or {}).get("half_life_years")
    if T.kind == "genetic" or (T.kind == "exposure" and hl is None):
        return 1.0
    return 0.5 ** (t / float(hl if hl is not None else 10.0))


def _risk(oc: dict, sex: str, age0: float, surv_ages: List[float], surv: List[float], log_rr_t, horizon: float) -> float:
    acc, free = 0.0, 1.0
    t = 0
    while t < horizon:
        a = age0 + t
        h0 = _rate(oc, sex, a)
        if h0 is None:
            break
        step = min(1.0, horizon - t)
        h = h0 * math.exp(log_rr_t(t)) * step
        s = M.at_age(surv_ages, surv, a)
        p = 1 - math.exp(-h)
        acc += s * free * p
        free *= 1 - p
        t += 1
    return acc


def _persistence_label(T) -> str:
    hl = (T.spec.get("persistence") or {}).get("half_life_years")
    if T.kind == "genetic" or (T.kind == "exposure" and hl is None):
        return "整个余生"
    if T.spec["transform"]["shape"] == "indicator":
        return "持续存在" if hl is None else f"半衰期约 {hl:g} 年"
    return f"半衰期约 {(hl if hl is not None else 10):g} 年"


def _summ(vals: List[float], point: float, nd: int = 4) -> dict:
    """median / p10 / p90 of the draws; `mean` is the expected risk (the number a probability statement should use)."""
    from .engine import q
    return {"median": round(q(vals, 0.5), nd), "mean": round(point, nd), "p10": round(q(vals, 0.1), nd), "p90": round(q(vals, 0.9), nd)}


def compute(m, draws: List[dict], n_max: int = 300) -> dict:
    reg = m.ext.reg
    central = m.scen["central"]
    sub = draws[:: max(1, len(draws) // n_max)]
    R_bar = statistics.fmean(math.exp(d["lr"]) for d in draws)
    s2_bar = statistics.fmean(d["th"]["s2"] for d in draws)
    surv_pt = m.outcomes(R_bar, s2_bar, central, curve=True)["surv"]
    surv_ref = m.s_ref[central]
    out = []
    genetics = m.obs.genetics or {}
    for did, oc in sorted(reg["outcomes"].items()):
        row = {"id": did, "name": oc.get("name_zh", did), "status": "estimated", "notes": [],
               "baseline": {"source": (oc.get("incidence") or {}).get("source"), "year": (oc.get("incidence") or {}).get("year"),
                            "quality": (oc.get("incidence") or {}).get("quality_zh")}}
        if oc.get("sex") in ("M", "F") and oc["sex"] != m.sex:
            row["status"] = "not_applicable"
            out.append(row)
            continue
        if (oc.get("license") or {}).get("commercial_use") is False:
            row["status"] = "no_baseline"
            row["notes"].append("基线发病率来源不允许商业使用，暂不计算")
            out.append(row)
            continue
        dx = sorted({c for c in oc.get("diagnosed_codes", []) for have in m.obs.by_code
                     if have == c or (c.startswith("ICD10:") and have.startswith(c + "."))})
        if dx:
            row["status"] = "diagnosed"
            row["diagnosed_codes"] = dx
            out.append(row)
            continue
        if _rate(oc, m.sex, m.age) is None:
            row["status"] = "no_baseline"
            row["notes"].append("该性别没有基线发病率")
            out.append(row)
            continue
        lo_band = min(r["age_lo"] for r in (oc.get("incidence") or {}).get("by_sex_age", []) if r.get("sex", m.sex) in (m.sex, "both"))
        if m.age < lo_band:
            row["notes"].append(f"{lo_band} 岁以下没有基线发病率，这段年龄按 0 计")
        horizon_age = max(float(oc.get("horizon_lifetime_age", 90)), math.ceil(m.age) + 10)   # lifetime >= 10-year window
        horizon_life = horizon_age - m.age
        terms = [T for T in m.ext.counted if did in T.coef and T.kind != "behavior"]
        r10, rl, rr_now = [], [], []
        parts_acc: Dict[str, List[float]] = {T.id: [] for T in terms}
        for d in sub:
            parts = m.ext.disease_parts(d["th"]["ext"], did) if d["th"].get("ext") else {}
            for k, v in parts.items():
                parts_acc[k].append(v)
            wt = {T.id: T for T in terms}
            f = (lambda t, parts=parts: sum(v * _weight(wt[k], t) for k, v in parts.items()))
            surv = M.individual_survival(surv_ref, math.exp(d["lr"]), d["th"]["s2"])
            r10.append(_risk(oc, m.sex, m.age, m.ages, surv, f, 10.0))
            rl.append(_risk(oc, m.sex, m.age, m.ages, surv, f, horizon_life))
            rr_now.append(math.exp(sum(parts.values())))
        zero = lambda t: 0.0
        row["risk10"] = _summ(r10, statistics.fmean(r10))
        row["lifetime"] = _summ(rl, statistics.fmean(rl))
        if oc.get("report_lifetime") is False:
            row["lifetime"] = None
            row["notes"].append(oc.get("report_lifetime_why_zh", "只报告 10 年风险"))
        row["horizon_lifetime_age"] = int(horizon_age)
        row["peer10"] = round(_risk(oc, m.sex, m.age, m.ages, surv_ref, zero, 10.0), 4)
        row["peer_lifetime"] = None if oc.get("report_lifetime") is False else round(_risk(oc, m.sex, m.age, m.ages, surv_ref, zero, horizon_life), 4)
        if row["lifetime"] is not None:
            for k in ("median", "mean"):
                row["lifetime"][k] = max(row["lifetime"][k], row["risk10"][k])
        row["rr_now"] = _summ(rr_now, statistics.fmean(rr_now), 2)
        drivers = []
        for T in terms:
            v = parts_acc[T.id]
            if not v:
                continue
            if T.spec["transform"]["shape"] == "indicator" and T.value == 0:
                continue          # "does not have it" only re-centres against peers; not shown as a factor
            lv = math.log(statistics.fmean(math.exp(x) for x in v))
            drivers.append({"id": T.id, "name": T.spec["name_zh"], "kind": T.kind, "hr": round(math.exp(lv), 2),
                            "persistence": _persistence_label(T),
                            "evidence": {"pmid": (T.spec.get("evidence") or {}).get("pmid"), "grade": (T.spec.get("evidence") or {}).get("grade")},
                            "disclosure": T.spec.get("disclosure", "standard"), "notes": T.notes})
        drivers.sort(key=lambda r: -abs(math.log(r["hr"])))
        row["drivers"] = drivers
        have = {T.id for T in terms} | {T.id for T in m.ext.terms}
        missing = []
        for sp in TM.RG.ext_terms(reg):
            if did in (sp.get("effect") or {}) and sp["id"] not in have and sp["kind"] != "behavior":
                if sp.get("disclosure") == "opt_in" and not m.ext.prefs.get("show_opt_in"):
                    continue
                if sp["input"]["code"].startswith("LP:monogenic:") and not m.ext.prefs.get("secondary_findings"):
                    continue
                missing.append({"id": sp["id"], "name": sp["name_zh"], "kind": sp["kind"], "test": sp.get("test")})
        row["missing_inputs"] = missing
        if m.ext.prefs.get("secondary_findings"):
            for q in reg["qualitative"].values():
                qc = (q.get("input") or {}).get("code", "")
                if qc.startswith("LP:monogenic:") and did in (q.get("effect") or {}) and any(
                        (o.get("value") == 1) for o in m.obs.rows(qc)):
                    row["notes"].append(f"本人携带{q.get('name_zh', qc).replace('携带', '')}：现有证据不足以折算成数值，未计入上面的风险，"
                                        "实际风险可能明显更高，建议遗传咨询与专科评估")
        chip = [v for v in genetics.get("monogenic") or [] if isinstance(v, dict) and did in (v.get("disease_ids") or [])
                and v.get("source_type") == "chip" and not v.get("confirmed_clinical")]
        if chip and m.ext.prefs.get("secondary_findings"):
            row["notes"].append("消费级芯片检出 " + "、".join(sorted({v["gene"] for v in chip})) +
                                " 的疑似致病变异：芯片对罕见变异的假阳性很高，需临床级检测确认，未计入数值")
        out.append(row)
    return {"method": "同一风险模型在 10 年与终身两个时间窗上积分；终身风险扣除因其他原因先去世的概率",
            "draws": len(sub), "diseases": out,
            "preferences": dict(m.ext.prefs)}
