"""Two independent builds must agree before a term counts (decision 2026-11-20, replaces single-build auto-accept).

Two specs of the same term are built by two builders that did not see each other's work. For every outcome and every
effect component (slope; each hinge side; each categorical level; the indicator effect) both must have it, and the two
point estimates must each lie inside the other's 95% CI, after rescaling to the same unit increment. Outcomes where
the builds agree are counted; the rest are not (shown as qualitative, both specs kept in registry/candidates/ for review).

Standard library only.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple


def _eff(e: dict) -> dict:
    if "hr" in e or not e.get("derived"):
        return e
    d, k = e["derived"], float(e["derived"]["pow"])
    f = d["from"]
    lo, hi = f["lo"] ** k, f["hi"] ** k
    return dict(e, hr=f["hr"] ** k, lo=min(lo, hi), hi=max(lo, hi))


def _per_unit(e: dict) -> Optional[Tuple[float, float, float]]:
    """(log HR, log lo, log hi) per one unit of the input (None if not a per-unit effect)."""
    e = _eff(e)
    if not all(k in e for k in ("hr", "lo", "hi")):
        return None
    per = float(e.get("per") or 1.0)
    return math.log(e["hr"]) / per, math.log(e["lo"]) / per, math.log(e["hi"]) / per


def _point(e: dict) -> Optional[Tuple[float, float, float]]:
    e = _eff(e)
    if not all(k in e for k in ("hr", "lo", "hi")):
        return None
    return math.log(e["hr"]), math.log(e["lo"]), math.log(e["hi"])


def _unit_of(spec: dict, oc: str, comp: str) -> float:
    e = (spec.get("effect") or {}).get(oc) or {}
    if comp in ("hr_below", "hr_above"):
        e = e.get(comp) or {}
    if comp == "slope" or comp in ("hr_below", "hr_above"):
        return float(e.get("per") or 1.0)
    return 1.0


def components(spec: dict, oc: str) -> Dict[str, Tuple[float, float, float]]:
    """Effect components on comparable scales: per-unit log HRs for slopes, log HRs for levels/indicators."""
    shape = spec["transform"]["shape"]
    e = (spec.get("effect") or {}).get(oc) or {}
    out: Dict[str, Tuple[float, float, float]] = {}
    if shape in ("loglinear", "residualized"):
        v = _per_unit(e)
        if v:
            out["slope"] = v
    elif shape == "hinge":
        for side in ("hr_below", "hr_above"):
            if e.get(side):
                v = _per_unit(e[side])
                if v:
                    out[side] = v
    elif shape == "categorical":
        for lvl, s in (e.get("levels") or {}).items():
            if isinstance(s, dict) and s.get("hr") == 1 and "lo" not in s:
                continue
            v = _point(s) if isinstance(s, dict) else None
            if v:
                out["level:" + str(lvl)] = v
    elif shape == "indicator":
        v = _point(e)
        if v:
            out["indicator"] = v
    return out


def _screen(spec: dict) -> Dict[str, Tuple[float, float, float]]:
    mr = (spec.get("screening") or {}).get("mortality_rr")
    v = _point(mr) if mr else None
    return {"mortality_rr": v} if v else {}


def _inside(x: float, lo: float, hi: float) -> bool:
    return min(lo, hi) - 1e-12 <= x <= max(lo, hi) + 1e-12


def compare(a: dict, b: dict) -> dict:
    """{"outcomes": {oc: {"agree": bool, "why": [...] , "components": {...}}}, "agree_any": bool}"""
    res: Dict[str, dict] = {}
    if a["transform"]["shape"] != b["transform"]["shape"]:
        return {"outcomes": {oc: {"agree": False, "why": [f"形状不同：{a['transform']['shape']} 对 {b['transform']['shape']}"]}
                             for oc in set(a.get("effect") or {}) | set(b.get("effect") or {})}, "agree_any": False}
    if a["transform"]["shape"] == "hinge":
        for k in ("knot", "knot_lo", "knot_hi"):
            ka, kb = a["transform"].get(k), b["transform"].get(k)
            if (ka is None) != (kb is None) or (ka is not None and abs(ka - kb) > 0.1 * max(abs(ka), abs(kb), 1e-9)):
                return {"outcomes": {oc: {"agree": False, "why": [f"拐点不同：{k} {ka} 对 {kb}"]} for oc in set(a["effect"]) | set(b["effect"])},
                        "agree_any": False}
    ocs = set(a.get("effect") or {}) | set(b.get("effect") or {})
    if a.get("screening") or b.get("screening"):
        ocs.add("screening")
    for oc in sorted(ocs):
        ca, cb = (_screen(a), _screen(b)) if oc == "screening" else (components(a, oc), components(b, oc))
        why, comps = [], {}
        if not ca or not cb:
            res[oc] = {"agree": False, "why": ["只有一次建项给出了这个结局"]}
            continue
        for k in sorted(set(ca) | set(cb)):
            if k not in ca or k not in cb:
                why.append(f"{k}：只有一次建项给出")
                continue
            (pa, la, ha), (pb, lb, hb) = ca[k], cb[k]
            ok = _inside(pa, lb, hb) and _inside(pb, la, ha)
            unit = _unit_of(a, oc, k)          # show both on build A's increment ("per 10 mmHg"), not per 1 unit
            comps[k] = {"a": round(math.exp(pa * unit), 4), "b": round(math.exp(pb * unit), 4), "per": unit, "agree": ok}
            if not ok:
                why.append(f"{k}：每 {unit:g} 单位 {math.exp(pa * unit):.3g} 与 {math.exp(pb * unit):.3g}，不在彼此的 95% 置信区间内")
        res[oc] = {"agree": not why, "why": why, "components": comps}
    return {"outcomes": res, "agree_any": any(v["agree"] for v in res.values())}


def events(spec: dict) -> int:
    pop = spec.get("population") or {}
    try:
        return int(pop.get("events") or 0)
    except (TypeError, ValueError):
        return 0


def merge(a: dict, b: dict, cmp: dict) -> Tuple[Optional[dict], List[str]]:
    """The accepted spec (the build with more events; the other recorded as replication), restricted to agreeing
    outcomes; None when no outcome agrees. Returns (spec, dropped outcome notes)."""
    keep = [oc for oc, v in cmp["outcomes"].items() if v["agree"]]
    dropped = [f"{oc}：" + "；".join(v["why"]) for oc, v in cmp["outcomes"].items() if not v["agree"]]
    if not keep:
        return None, dropped
    main, other = (a, b) if events(a) >= events(b) else (b, a)
    out = dict(main)
    out["effect"] = {oc: main["effect"][oc] for oc in keep if oc != "screening"}
    if main.get("screening") and "screening" not in keep:
        return None, dropped + ["筛查死亡 RR 两次不一致"]
    ev = dict(out.get("evidence") or {})
    oe = other.get("evidence") or {}
    ev["replication"] = {"pmid": oe.get("pmid"), "doi": oe.get("doi"), "design": oe.get("design"),
                         "effects": {oc: {k: other["effect"][oc].get(k) for k in ("hr", "lo", "hi", "per") if k in other["effect"][oc]}
                                     for oc in keep if oc in (other.get("effect") or {})},
                         "screening_mortality_rr": (other.get("screening") or {}).get("mortality_rr"),
                         "rule_zh": "两次独立建项一致（点估计互在对方 95% 置信区间内）"}
    out["evidence"] = ev
    if dropped:
        out.setdefault("notes_zh", []).append("两次建项不一致、未计入的结局：" + "；".join(dropped))
    return out, dropped
