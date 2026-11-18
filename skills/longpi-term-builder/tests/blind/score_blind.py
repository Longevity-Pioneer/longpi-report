#!/usr/bin/env python3
"""Blind self-test scorer: does a builder-produced spec reproduce the 1.1.1 core term?

    python3 score_blind.py <task.json> <produced_spec.json> [--json]
    python3 score_blind.py --all <dir_with_produced_specs>      # expects <task_id>.json per task

Pass rule (per compared effect): the produced all-cause HR, rescaled to the core term's increment, lies inside the
core term's 95% CI, and has the same direction. Hinge terms compare both sides; categorical terms compare every
non-reference level named in the task; the GrimAge2 task compares the HR per year of acceleration.
The scorer reads registry/terms/core.*.json only here, never shows it to the builder.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE_DIR = HERE.parents[2] / "longpi-report" / "registry" / "terms"


def core_targets(core_id: str) -> dict:
    """{label: (hr, lo, hi, per)} for the core term (per = the increment its HR refers to; None for categorical)."""
    t = json.loads((CORE_DIR / f"{core_id}.json").read_text(encoding="utf-8"))
    if t.get("engine") == "methylation":
        c = t["spec"]["clocks"]["GrimAge2"]
        b, se = c["beta"], c["beta_se"]
        return {"per_year": (math.exp(b), math.exp(b - 1.959964 * se), math.exp(b + 1.959964 * se), 1.0)}
    s = t["spec"]
    out = {}
    if s["shape"] == "loglinear":
        r = s["rr"]
        out["slope"] = (r["value"], r["lo"], r["hi"], r["per"])
    elif s["shape"] == "hinge":
        for side in ("rr_below", "rr_above"):
            r = s[side]
            out[side.replace("rr_", "hr_")] = (r["value"], r["lo"], r["hi"], r["per"])
    elif s["shape"] == "categorical":
        for lvl, r in s["levels"].items():
            if isinstance(r, dict):
                out[lvl] = (r["value"], r["lo"], r["hi"], None)
            else:
                out[lvl] = (float(r), float(r), float(r), None)
    return out


def _rescale(hr: float, per: float, to_per: float) -> float:
    return math.exp(math.log(hr) / per * to_per)


def produced_effects(spec: dict, task: dict) -> dict:
    e = (spec.get("effect") or {}).get("all_cause")
    if not e:
        return {}
    shape = (spec.get("transform") or {}).get("shape")
    if (spec.get("transform") or {}).get("log_x"):
        return {"_error": "log_x 形状无法与线性核心项直接比较"}
    out = {}
    if shape in ("loglinear", "residualized"):
        out["slope"] = (e["hr"], e["per"])
        out["per_year"] = (e["hr"], e["per"])
    elif shape == "hinge":
        for side in ("hr_below", "hr_above"):
            if e.get(side):
                out[side] = (e[side]["hr"], e[side]["per"])
    elif shape == "categorical":
        for lvl, r in (e.get("levels") or {}).items():
            out[lvl] = (r["hr"], None)
    return out


def score(task: dict, spec: dict) -> dict:
    targets = core_targets(task["compare_to"])
    got = produced_effects(spec, task)
    rows, ok_all = [], bool(got) and "_error" not in got
    for label, (hr, lo, hi, per) in targets.items():
        if task.get("levels") and label not in task["levels"]:
            continue
        if lo == hi == hr == 1.0:   # reference level
            continue
        if label not in got:
            rows.append({"effect": label, "pass": False, "why": "规格中缺这一项效应"})
            ok_all = False
            continue
        phr, pper = got[label]
        val = phr if per is None else _rescale(phr, pper, per)
        same_dir = (math.log(val) >= 0) == (math.log(hr) >= 0) or abs(math.log(hr)) < 1e-9
        inside = lo <= val <= hi
        rows.append({"effect": label, "core": [hr, lo, hi], "per": per, "produced_rescaled": round(val, 4),
                     "inside_ci": inside, "same_direction": same_dir, "pass": inside and same_dir})
        ok_all &= inside and same_dir
    return {"task": task["task_id"], "pass": ok_all, "rows": rows, "error": got.get("_error")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task", nargs="?")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--all")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    results = []
    if a.all:
        for tp in sorted(HERE.glob("*.task.json")):
            task = json.loads(tp.read_text(encoding="utf-8"))
            sp = Path(a.all) / f"{task['task_id']}.json"
            if not sp.exists():
                results.append({"task": task["task_id"], "pass": False, "rows": [], "error": "未产出规格"})
                continue
            results.append(score(task, json.loads(sp.read_text(encoding="utf-8"))))
    else:
        results.append(score(json.loads(Path(a.task).read_text(encoding="utf-8")),
                             json.loads(Path(a.spec).read_text(encoding="utf-8"))))
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    else:
        for r in results:
            print(f"{r['task']:12s} {'通过' if r['pass'] else '未通过'} {r.get('error') or ''}")
            for row in r["rows"]:
                print("   ", json.dumps(row, ensure_ascii=False))
        print(f"合计：{sum(r['pass'] for r in results)}/{len(results)} 通过")
    return 0 if all(r["pass"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
