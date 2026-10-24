"""Input validation, the fact sheet Claude writes from, and narrative checks."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

from . import clock, units
from .engine import parse_date

PHENO = ("albumin", "creatinine", "glucose", "crp", "lymph_pct", "mcv", "rdw", "alp", "wbc")
# plausible ranges in canonical units (catch unit mistakes, not disease)
RANGES = {
    "albumin": (20, 60), "creatinine": (20, 1500), "glucose": (2, 35), "glucose_fasting": (2, 35), "crp": (0.01, 300),
    "lymph_pct": (2, 80), "mcv": (55, 130), "rdw": (9, 30), "alp": (10, 1500), "wbc": (1, 50),
    "ldl": (0.3, 12), "hdl": (0.2, 4), "tc": (1, 20), "tg": (0.1, 50), "hba1c": (3, 18), "alt": (2, 2000),
    "ast": (2, 2000), "ggt": (2, 3000), "uric_acid": (50, 1200), "vitd": (2, 200), "apob": (0.2, 4),
}
LEVELS = {"关注", "留意", "一般"}
BACKEND_TERMS = ("MCP", "skill", "engine.py", "params.json", "Mirobody", "LOINC", "Monte Carlo")


def check(person: dict, base: Path) -> dict:
    errors: List[str] = []
    warn: List[str] = []
    p = person.get("person", {})
    if p.get("sex", "").upper()[:1] not in ("M", "F"):
        errors.append("person.sex 必须是 M 或 F")
    if "age" not in p and "birth" not in p:
        errors.append("person.age 或 person.birth（YYYY-MM）至少给一个")
    if "as_of" not in person:
        errors.append("缺 as_of（数据截至日期）")
    age = None
    try:
        if "age" in p:
            age = float(p["age"])
        elif "birth" in p and "as_of" in person:
            age = (parse_date(person["as_of"]) - parse_date(p["birth"])).days / 365.25
    except Exception as e:  # noqa: BLE001
        errors.append(f"年龄无法解析：{e}")
    if age is not None and not (30 <= age <= 85):
        warn.append(f"年龄 {age:.0f} 岁在模型主要适用范围（30–85 岁）之外，结果只作参考")
    pheno_dates = []
    for l in person.get("labs", []):
        try:
            parse_date(l["date"])
        except Exception:  # noqa: BLE001
            errors.append(f"化验日期无法解析：{l.get('date')}")
            continue
        for k, v in l.get("items", {}).items():
            val, unit = (v[0], v[1] if len(v) > 1 else None) if isinstance(v, list) else (v, None)
            ana = "glucose" if k == "glucose_fasting" else k
            try:
                cv = units.to_canonical(ana, float(val), unit)
            except (TypeError, ValueError) as e:
                errors.append(f"{l['date']} {k}: {e}")
                continue
            lo_hi = RANGES.get(k)
            if lo_hi and not (lo_hi[0] <= cv <= lo_hi[1]):
                warn.append(f"{l['date']} {k}={val} {unit or ''} 换算后 {cv:.3g} 超出常见范围，检查单位")
        have = [k for k in PHENO if k in l.get("items", {})]
        if len(have) >= 8:
            pheno_dates.append((l["date"], [k for k in PHENO if k not in have]))
            canon = {}
            for k in ("crp", "mcv", "rdw"):
                v = l["items"].get(k)
                if v is not None:
                    try:
                        canon[k] = units.to_canonical(k, float(v[0] if isinstance(v, list) else v), v[1] if isinstance(v, list) and len(v) > 1 else None)
                    except (TypeError, ValueError):
                        pass
            ex = l.get("clock_exclude")
            fl = [] if ex is True else clock.analyte_flags(canon, skip=ex or [])
            if "acute_inflammation" in fl:
                warn.append(f"{l['date']} hs-CRP {canon['crp']:.1f} mg/L：高于 10，多半处于急性感染或炎症期，会让血液年龄偏高。"
                            "问用户当时是否生病；是的话在这次 labs 加 \"clock_exclude\": true（报告会同时给出不计入时的结果）")
            if "rbc_abnormal" in fl:
                warn.append(f"{l['date']} MCV {canon.get('mcv', '—')}、RDW {canon.get('rdw', '—')}：红细胞指标超出参考范围（缺铁、贫血恢复期或地中海贫血），"
                            "会让血液年龄偏高。问用户当时的情况；属暂时状态时加 \"clock_exclude\": [\"mcv\", \"rdw\"]（报告会同时给出不计入时的结果）")
    w = person.get("wearables", {}) or {}
    for k in ("apple_health_xml", "daily_csv", "cgm_csv", "bp_csv"):
        if w.get(k) and not (base / w[k]).exists():
            errors.append(f"wearables.{k} 指向的文件不存在：{w[k]}")
    clocks = {"grimage2": "GrimAge2", "grimage": "GrimAge", "dunedinpace": "DunedinPACE", "dnam phenoage": "DNAm PhenoAge",
              "first_generation": "first_generation", "unknown": "unknown"}
    for r in person.get("methylation") or []:
        ct = str(r.get("clock_type", "")).strip().lower()
        if ct not in clocks:
            warn.append(f"甲基化 {r.get('date', '')}：clock_type「{r.get('clock_type', '')}」不认识，可选 " + "、".join(clocks.values()) + "；按不计入处理")
        elif clocks[ct] in ("GrimAge2", "GrimAge") and r.get("bio_age") is None:
            warn.append(f"甲基化 {r.get('date', '')}：写了 {clocks[ct]} 但没有数值（bio_age），不能计入")
    missing = []
    if not pheno_dates:
        missing.append("一次包含 PhenoAge 九项（白蛋白、肌酐、血糖、CRP、淋巴细胞%、MCV、RDW、ALP、白细胞）的血液检测")
    elif any("crp" in m for _, m in pheno_dates):
        missing.append("超敏 C 反应蛋白（hs-CRP）：缺失时按人群中位数补入，区间会变宽")
    life = person.get("lifestyle", {})
    if not life.get("smoking", {}).get("status"):
        missing.append("吸烟史（从不/已戒/现在吸）")
    if not any(f.get("vo2max") for f in person.get("fitness", [])) and not (w.get("apple_health_xml") or w.get("daily_csv")):
        missing.append("心肺适能（手表 VO2max 或实验室 CPET）")
    if not any(f.get("grip_kg") for f in person.get("fitness", [])):
        missing.append("握力")
    return {"errors": errors, "warnings": warn, "missing": missing,
            "phenoage_tests": [d for d, _ in pheno_dates], "age": round(age, 1) if age else None}


def fact_sheet(out: dict) -> str:
    """Plain-text numbers to cite when writing the narrative (no rounding surprises)."""
    r = out["results"]
    la = r["longpi_age"]
    ix = r["index120"]
    lines = [f"# LongPi 事实表（数据截至 {r['as_of']}）", "",
             f"- 日历年龄 {la['chrono']}；LongPi Age 中位 {la['value']['median']}（80% 区间 {la['value']['p10']}–{la['value']['p90']}）；"
             f"差值 {la['delta']['median']:+}（{la['delta']['p10']:+} 至 {la['delta']['p90']:+}）",
             f"- 时钟层 {str(la['clock_delta']['median']) + ' 年' if la['clock']['measured'] else '未测（没有血液检测，只加宽区间）'}；"
             f"甲基化 {format(la['methylation_delta']['median'], '+') + ' 年（' + la['methylation']['clock'] + ' 已计入）' if la['methylation']['counted'] else '未计入（只加宽区间）'}；"
             f"功能领域合计 {la['function_delta']['median']:+} 年；系数组 {la['coef_set']}",
             f"- PhenoAge 测量 {len(la['clock']['phenoage_points'])} 次；当前差值估计 {la['clock']['gap_now_mean']:+}±{la['clock']['gap_now_sd']} 岁；"
             f"PhenoAge 差值 1 岁 ≈ {la['clock']['years_per_gap_year_central']} 风险等效年",
             f"- LongPi Pace：{la['pace'].get('status')}（n={la['pace']['n']}，跨度 {la['pace']['span_years']} 年，信息增益 {la['pace'].get('info_gain')}，还需约 {la['pace'].get('more_annual_tests_needed')} 次年度体检）"
             + (f" pace={la['pace']['pace']}（{la['pace']['pace_p10']}–{la['pace']['pace_p90']}）" if la['pace'].get('status') == 'reported' else ""),
             "", "## 各领域（年，正数=更老）"]
    for d in la["domains"]:
        lines.append(f"- {d['domain']}：{d['years']['median']:+}（{d['years']['p10']:+} 至 {d['years']['p90']:+}）"
                     + (f"；输入 {d['input']}（{d['source']}）" if d["measured"] else "；未测，按同龄人群分布"))
    lines += ["", "## PhenoAge 各次"]
    for p in la["clock"]["phenoage_points"]:
        lines.append(f"- {p['date']}：PhenoAge {p['phenoage']}，参考 {p['ref_phenoage']}，差值 {p['gap']:+}（单次噪声 ±{p['noise_sd']}"
                     + ("，CRP 补入" if p["crp_imputed"] else "") + "）")
    lines += ["", f"## 120 指数（加权 {ix['weighted_index']['median']}，权重 {ix['weights']}）"]
    for k, s in ix["scenarios"].items():
        lines.append(f"- {k} {s['name']}：指数 {s['index']['median']}（{s['index']['p10']}–{s['index']['p90']}）；期望寿命 {s['life_exp']['median']}（人群 {s['ref_life_exp']}）；"
                     f"P(90) {s['milestones']['90']['median']:.3f}（人群 {s['ref_milestones']['90']:.3f}）；P(100) {s['milestones']['100']['median']:.4f}（人群 {s['ref_milestones']['100']:.4f}）")
    lines += ["", "## 干预（按 ΔLongPi Age 排序）"]
    for iv in sorted(r["interventions"], key=lambda i: i["d_longpi_age"]["median"] if i["quantified"] else 9):
        if iv["quantified"]:
            lines.append(f"- [{iv['id']}] {iv['name']}：{iv['d_longpi_age']['median']:+}（{iv['d_longpi_age']['p10']:+} 至 {iv['d_longpi_age']['p90']:+}）；"
                         f"获益概率 {iv['p_benefit']}；Δ120 {iv['d_index_central']['median']:+}；证据 {iv['evidence']}")
        else:
            lines.append(f"- [{iv['id']}] {iv['name']}：证据 {iv['evidence']}，不估算")
    mt = la["methylation"]
    lines += ["", "## 甲基化"]
    if mt["counted"]:
        lines.append(f"- {mt['clock']} {mt['value']}（{mt['date']}，采样时 {mt['age_at_test']} 岁）；相对 NHANES 参考的加速 {mt['accel']:+} 年；"
                     f"按其他指标预期 {mt['expected_accel']:+} 年；超出预期 {mt['resid']:+} 年 → 计入 {la['methylation_delta']['median']:+} 年")
    else:
        lines.append(f"- 未计入：{'现有报告是 ' + '、'.join(x['clock_type'] or '未注明' for x in mt['provided_not_counted']) + '，不是 GrimAge2 / GrimAge' if mt.get('provided_not_counted') else '没有甲基化检测'}；"
                     f"没测时这一块相当于 LongPi Age ±{mt['unmeasured_sd_years']} 年（1 个标准差）的不确定")
    lines.append(f"- NHANES：GrimAge2 在 LongPi 之外每 1 个标准差 HR {mt['nhanes']['hr_per_sd_resid']}，C 指数 +{mt['nhanes']['c_gain']}；"
                 "其他时钟：" + "；".join(f"{k} {v['hr_per_sd_resid']}" for k, v in mt["not_counted"].items()))
    dv = r["data_value"]
    lines += ["", f"## 让结果更准（数据完整度 {dv['completeness_pct']}%）",
              f"- 80% 区间宽度：只知道年龄性别 {dv['width_none']} 岁（±{dv['width_none'] / 2:.1f}）→ 现在 {dv['width_now']} 岁（±{dv['width_now'] / 2:.1f}）"
              f"→ 下面全部做完 {dv['width_all']} 岁（±{dv['width_all'] / 2:.1f}）"]
    for g in dv["items"]:
        lines.append(f"- [{g['id']}] {g['label']}（现状：{g['status']}）：区间 {dv['width_now']} → {g['width_after']} 岁，收窄 {g['narrows_by']}；"
                     f"费用 {g['cost']}；{g['effort']}" + (f"；还能：{g['also']}" if g.get("also") else ""))
    if dv.get("small_items"):
        lines.append("- 收窄不足 0.1 岁（不展示）：" + "、".join(dv["small_items"]))
    lines.append("- 不改变 LongPi Age 但有用的数据：" + "；".join(f"{o['what']}{'（已有）' if o['have'] else ''}：{o['use']}" for o in dv["other_uses"]))
    alt = la.get("clock_alternative")
    flagged = [p for p in la["clock"]["phenoage_points"] if p.get("flags") or p.get("left_out")]
    if flagged or la["clock"].get("excluded_tests"):
        lines += ["", "## 血液检查的异常期"]
        for p in flagged:
            lines.append(f"- {p['date']}：提示 {'、'.join(p.get('flags') or []) or '无'}；未计入 {'、'.join(p.get('left_out') or []) or '无'}；关键值 {p.get('values')}")
        for x in la["clock"].get("excluded_tests", []):
            lines.append(f"- {x['date']}：整次不计入血液时钟（{x['reason'] or '未写原因'}）")
        if alt:
            lines.append(f"- 按提示处理后 LongPi Age {alt['value']['median']}（80% 区间 {alt['value']['p10']}–{alt['value']['p90']}），较主结果 {alt['shift_vs_main']:+} 岁；"
                         "主结果不变。先问用户当时是否生病或贫血；确认后在该次 labs 写 clock_exclude，重新 compute")
    ad = r.get("asks_default")
    if ad:
        lines += ["", "## 默认待补充资料（narrative 不写 asks 时显示这份；可以在它基础上增删改）"]
        lines += [f"- {a['item']}（{a.get('when', '')}）：{a.get('why', '')}" for a in ad["items"]]
    try:
        from .render import exercise_library
        lib = exercise_library()["exercises"]
        lines += ["", "## 动作库（training 里用 {\"ref\": id, \"dose\": ...} 引用，图文自动带出）",
                  "- " + "；".join(f"{e['id']} {e['name']}（{e['category']}，{e['level']}）" for e in lib)]
    except (OSError, ValueError, KeyError):
        pass
    wv = out.get("wearables", {})
    if wv:
        lines += ["", "## 可穿戴摘要", "- " + json.dumps(wv, ensure_ascii=False)]
    cm = out.get("data", {}).get("cgm_metrics")
    if cm:
        lines += ["- CGM：" + json.dumps(cm, ensure_ascii=False)]
    lines += ["", "## 输入缺口", "- " + "；".join(r.get("missing_domains", [])) if r.get("missing_domains") else ""]
    return "\n".join(lines)


def check_narrative(n: dict, out: dict) -> List[str]:
    """Deterministic checks on Claude's narrative before rendering."""
    probs: List[str] = []
    for i, rk in enumerate(n.get("risks", [])):
        for k in ("name", "level", "drivers", "evidence", "action"):
            if not rk.get(k):
                probs.append(f"risks[{i}] 缺 {k}")
        if rk.get("level") not in LEVELS:
            probs.append(f"risks[{i}].level 必须是 {sorted(LEVELS)}")
        txt = json.dumps(rk, ensure_ascii=False)
        if re.search(r"确诊为|诊断为", txt):
            probs.append(f"risks[{i}] 不要写诊断结论（用“风险/提示/建议就医评估”）")
    for i, f in enumerate(n.get("frontier", [])):
        for k in ("title", "grade", "body", "next"):
            if not f.get(k):
                probs.append(f"frontier[{i}] 缺 {k}")
    blob = json.dumps(n, ensure_ascii=False)
    for t in BACKEND_TERMS:
        if t in blob:
            probs.append(f"面向用户的文字里出现了后台术语：{t}")
    la = out["results"]["longpi_age"]["value"]["median"]
    alt = (out["results"]["longpi_age"].get("clock_alternative") or {}).get("value", {}).get("median")
    for m in re.finditer(r"LongPi Age[^0-9]{0,6}(\d{2}\.\d)", blob):
        v = float(m.group(1))
        if abs(v - la) > 0.05 and (alt is None or abs(v - alt) > 0.05):
            probs.append(f"叙述里的 LongPi Age {m.group(1)} 与计算结果 {la} 不一致")
    tr = n.get("training")
    if tr:
        from .render import exercise_library
        lib = {e["id"] for e in exercise_library()["exercises"]}
        for i, se in enumerate(tr.get("sessions", [])):
            if not se.get("name"):
                probs.append(f"training.sessions[{i}] 缺 name")
            for j, ex in enumerate(se.get("exercises", [])):
                if ex.get("ref"):
                    if ex["ref"] not in lib:
                        probs.append(f"training.sessions[{i}].exercises[{j}].ref「{ex['ref']}」不在动作库里（data/exercise_library.json）")
                elif not (ex.get("name") and ex.get("steps")):
                    probs.append(f"training.sessions[{i}].exercises[{j}] 不引用动作库时要写 name 和 steps")
    sp = n.get("supplements")
    if sp:
        for gi, g in enumerate(sp.get("groups", [])):
            for k, it in enumerate(g.get("items", [])):
                miss = [f for f in ("name", "dose", "avoid", "evidence") if not it.get(f)]
                if miss:
                    probs.append(f"supplements.groups[{gi}].items[{k}]（{it.get('name', '')}）缺 {'、'.join(miss)}")
    for k, a in enumerate((n.get("asks") or {}).get("items", [])):
        if not a.get("item") or not (a.get("how") or a.get("why")):
            probs.append(f"asks.items[{k}] 要写 item，以及 how 或 why")
    return probs
