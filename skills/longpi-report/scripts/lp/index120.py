"""120 Index, state + behaviour (engine 1.1.2, PRD §7).

  state part      unchanged from 1.1.1: the person's risk multiplier R from LongPi Age
  behaviour part  sustained behaviours from the registry (kind "behavior"): R_index = R * exp(sum_b l_b)
                  - dose-response behaviours (steps, exercise minutes, ...): l_b as any registry term, discounted
                    when the marker they act through is already measured (mediation), x 0.5 when self-reported,
                    counted only after `min_weeks` (default 8)
                  - guideline screening (up to date, eligible): l = ln(1 - share_d x (1 - RR_screen)), share_d = the
                    disease's share of all deaths at this age and sex in China
  120 Index      = 100 + 10 log10(P_you(120 | R_index) / P_peer(120)), weighted over the same three scenarios.

`how_to_gain` lists, for behaviours not yet counted, the points they would add if adopted at their target level.
"""
from __future__ import annotations

import math
import statistics
from typing import Dict, List

from . import registry as RG
from . import terms as TM


def _weighted(m, R: float, s2: float) -> float:
    w = m.pp["scenarios"]["weights"]
    return sum(w[k] * m.outcomes(R, s2, k)["index"] for k in w)


def compute(m, draws: List[dict], res: dict, n_max: int = 300) -> dict:
    ext = m.ext
    s2_bar = statistics.fmean(d["th"]["s2"] for d in draws)
    R_state = statistics.fmean(math.exp(d["lr"]) for d in draws)
    beh = ext.behavior_terms()
    tot_draw, per_term = [], {T.id: [] for T in beh}
    bound = 0
    for d in draws:
        parts, b = ext.behavior_parts(d["th"]["ext"]) if (beh and d["th"].get("ext")) else ({}, False)
        bound += b
        tot_draw.append(d["lr"] + sum(parts.values()))
        for k, v in parts.items():
            per_term[k].append(v)
    R_total = statistics.fmean(math.exp(x) for x in tot_draw)
    idx_state = _weighted(m, R_state, s2_bar)
    idx_total = _weighted(m, R_total, s2_bar)
    step = max(1, len(draws) // n_max)
    sub_idx = [_weighted(m, math.exp(tot_draw[j]), draws[j]["th"]["s2"]) for j in range(0, len(draws), step)]
    from .engine import summ
    rows = []
    for T in beh:
        v = per_term[T.id]
        lv = math.log(statistics.fmean(math.exp(x) for x in v)) if v else 0.0
        without = statistics.fmean(math.exp(x - y) for x, y in zip(tot_draw, v)) if v else R_total
        rows.append({"id": T.id, "name": T.spec["name_zh"], "points": round(idx_total - _weighted(m, without, s2_bar), 2),
                     "hr": round(math.exp(lv), 3), "level": None if T.level is None else round(T.level, 2),
                     "value": T.value, "notes": T.notes, "screening": T.screening,
                     "evidence": {"pmid": (T.spec.get("evidence") or {}).get("pmid"), "grade": (T.spec.get("evidence") or {}).get("grade")}})
    rows.sort(key=lambda r: -r["points"])
    # behaviours that would add points: not counted yet (absent, not sustained, overdue), or counted below the target
    gain = []
    status = {T.id: T for T in ext.terms}
    contrib_now = {r["id"]: r for r in rows}
    for sp in RG.ext_terms(ext.reg):
        if sp["kind"] != "behavior":
            continue
        T0 = status.get(sp["id"])
        bh = sp.get("behavior") or {}
        tgt = bh.get("target")
        coef = float((sp.get("overlap") or {}).get("coef", 1.0))
        med = (sp.get("overlap") or {}).get("mediated_by") or {}
        coef *= max(0.0, 1 - sum(v for k, v in med.items() if TM._mediator_measured(k, m)))
        if sp.get("screening"):
            if T0 is not None and T0.status == "counted":
                continue                                   # already up to date
            st = TM._screening_state(sp, m, None)
            if not st["eligible"]:
                continue
            share = TM.screening_share(ext.reg, sp["screening"]["disease_id"], m.sex, m.age)
            u = TM.screening_uptake(sp, m.sex, m.age)
            red = share * (1 - sp["screening"]["mortality_rr"]["hr"])
            l_new = coef * (math.log(max(1e-6, 1 - red)) - math.log(max(1e-6, 1 - u * red)))
            l_now = 0.0
        elif tgt is not None and "all_cause" in (sp.get("effect") or {}):
            p = TM.draw_effect(sp, "all_cause", None)
            l_new = TM.normalised(sp, p, tgt, m.sex, m.age, coef)
            cur = None if T0 is None else (T0.level if T0.level is not None else T0.value)
            if cur is not None and isinstance(cur, (int, float)):
                if TM.normalised(sp, p, cur, m.sex, m.age, coef) <= l_new:
                    continue                               # already at or beyond the target
            counted_now = contrib_now.get(sp["id"])
            l_now = math.log(counted_now["hr"]) if counted_now else 0.0
        else:
            continue
        l_new = max(-ext.bcap_single, min(ext.bcap_single, l_new))
        d = l_new - l_now
        if d >= 0:
            continue
        pts = _weighted(m, R_total * math.exp(d), s2_bar) - idx_total
        gain.append({"id": sp["id"], "name": sp["name_zh"], "target": tgt, "target_source": bh.get("target_source"),
                     "current": None if T0 is None else (T0.level if T0.level is not None else T0.value),
                     "points_if_adopted": round(pts, 2), "screening": bool(sp.get("screening")),
                     "status": None if T0 is None else T0.status, "why_not_now": None if T0 is None else T0.reasons,
                     "min_weeks": bh.get("min_weeks", 8), "evidence_grade": (sp.get("evidence") or {}).get("grade")})
    gain.sort(key=lambda r: -r["points_if_adopted"])
    return {"state_index": round(idx_state, 1), "total_index": summ(sub_idx, 1, idx_total),
            "behavior_points": round(idx_total - idx_state, 1), "behaviors": rows, "how_to_gain": gain[:8],
            "guardrail": {"single_cap_log_hr": ext.bcap_single, "total_cap_log_hr": ext.bcap_total,
                          "draws_bound_share": round(bound / max(1, len(draws)), 3)},
            "note": "身体状态部分基于 LongPi Age 的风险倍数（含已计入的新增指标）；行为部分只计入已持续的行为与按指南按期完成的筛查"}
