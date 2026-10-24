#!/usr/bin/env python3
"""Fill the generated blocks of docs/技术文档.md from the code and data files.

Usage:
  python3 docs/tools/gen_tech_tables.py           rewrite every <!-- BEGIN GEN:name --> ... <!-- END GEN:name --> block
  python3 docs/tools/gen_tech_tables.py --check   exit 1 if any block differs from what the files say now

Standard library only. Reads skills/longpi-report/{data,scripts,examples/output} and evidence/results.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "longpi-report"
DATA = SKILL / "data"
RES = ROOT / "evidence" / "results"
DOC = ROOT / "docs" / "技术文档.md"
sys.path.insert(0, str(SKILL / "scripts"))


def J(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def fmt(x, nd=4):
    if isinstance(x, float):
        return f"{x:.{nd}g}"
    return str(x)


def rr_txt(rr):
    if rr in (1, 1.0):
        return "1"
    return f"{fmt(rr['value'])}（{fmt(rr['lo'])}–{fmt(rr['hi'])}）/ {fmt(rr.get('per', 1))}"


# --------------------------------------------------------------------------- blocks

def block_function_index() -> str:
    rows = ["| 文件 | 行 | 函数 / 类 | 作用 |", "|---|---|---|---|"]
    roles = {
        "units.py": {"norm_unit": "单位写法归一", "to_canonical": "换算到规范单位"},
        "mortality.py": {"Reference": "参考死亡率（WPP + 极高龄外推）", "_old_fit": "Gamma-Gompertz 极高龄拟合", "mu_period": "整岁年龄的年死亡率",
                         "mu_at": "小数年龄的年死亡率", "gompertz_slope": "Gompertz 斜率 b", "cohort_hazards": "情景下的队列死亡率路径",
                         "survival_from": "参考生存曲线", "individual_survival": "Gamma 脆弱性恒等式", "at_age": "活到某年龄的概率",
                         "life_expectancy": "期望寿命"},
        "clock.py": {"linear_predictor": "PhenoAge 线性预测值", "phenoage": "PhenoAge", "years_per_unit": "每单位指标对应的年数",
                     "reference_phenoage": "同龄参考 PhenoAge", "gap_sd_population": "同龄差值 SD", "noise_sd": "单次测量噪声",
                     "kalman_gap": "多次检测合并（卡尔曼）", "trend_posterior": "Pace 的贝叶斯直线"},
        "domains.py": {"expect_normal": "正态期望（Gauss-Hermite）", "draw_log_rr": "按 95% CI 抽 ln RR", "draw_params": "单次抽样的剂量反应参数",
                       "f_raw": "未归一化的对数风险比", "norm_for": "取人群分布", "log_mean_exp_pop": "归一化常数",
                       "log_hr": "归一化的对数风险比", "draw_from_population": "未测领域按人群抽样"},
        "engine.py": {"office_from_home": "家庭血压→诊室口径", "selfreport_from_watch": "手表睡眠→问卷口径", "device_kind": "设备品牌",
                      "glycemic_status": "糖代谢分级（ADA）", "smoking_level": "吸烟分级（按日期）", "collect_inputs": "每个领域取一个输入值",
                      "phenoage_points": "每次体检的 PhenoAge", "gap_loghr": "PhenoAge 差值的分段对数风险", "Model": "单人模型（抽样、合成、生存）",
                      "_adhere": "依从性抽样", "intervention_effect": "单次抽样的干预效果", "applicable": "干预适用条件", "run": "主流程",
                      "summarise": "汇总为 results", "trajectory": "历年快照与 LongPi Pace",
                      "methylation_input": "甲基化输入（GrimAge2 / GrimAge，算加速）", "_interp": "按年龄线性插值",
                      "gap_posterior": "PhenoAge 差值后验（卡尔曼）", "_set_methylation_residual": "甲基化残差（相对 LongPi 点估计）",
                      "meth_term": "甲基化项（未测抽样 / 已测收缩）", "methylation_summary": "甲基化结果汇总",
                      "_dom_mod": "补测假设：测一个领域", "_patch_blood_panel": "补测假设：抽一次血", "_patch_hs_crp": "补测假设：补 hs-CRP",
                      "_patch_blood_repeat": "补测假设：再抽一次血", "_patch_methylation": "补测假设：做 GrimAge2",
                      "_actions": "列出可补测的项目", "_width": "同一组抽样下的区间宽度", "data_value": "补测清单与数据完整度"},
        "clinical.py": {"china_par": "China-PAR 10 年风险", "egfr_ckd_epi_2021": "eGFR", "fib4": "FIB-4", "summary": "临床指标汇总"},
        "wearables.py": {"read_apple_health": "读 Apple 健康", "read_daily_csv": "读通用每日 CSV", "read_cgm_csv": "读 CGM", "cgm_metrics": "CGM 指标",
                         "cgm_meal_peaks": "餐后峰值", "read_bp_csv": "读家庭血压", "home_bp_summary": "家庭血压 4 周均值"},
        "derive.py": {"normalise_labs": "化验单位换算", "derive": "可穿戴摘要与图表数据"},
        "schema.py": {"check": "输入检查", "fact_sheet": "事实表", "check_narrative": "叙述检查"},
        "render.py": {"methods_cards": "方法页内容", "render": "生成 HTML"},
    }
    for fname, names in roles.items():
        lines = (SKILL / "scripts" / "lp" / fname).read_text(encoding="utf-8").splitlines()
        for name, role in names.items():
            pat = re.compile(rf"^\s*(def|class) {re.escape(name)}\b")
            ln = next((i + 1 for i, l in enumerate(lines) if pat.match(l)), None)
            rows.append(f"| `scripts/lp/{fname}` | {ln} | `{name}` | {role} |")
    return "\n".join(rows)


def block_lifetable() -> str:
    from lp import mortality as M
    t = J(DATA / "lifetable_china_wpp2024.json")
    rows = ["| 项目 | 男 | 女 |", "|---|---|---|"]
    refs = {s: M.Reference(s) for s in "MF"}
    rows.append(f"| 年份范围 | {t['years'][0]}–{t['years'][-1]} | 同左 |")
    rows.append(f"| 2026 年出生时期望寿命 e0（WPP） | {t['e0']['M']['2026']} | {t['e0']['F']['2026']} |")
    rows.append(f"| Gompertz 斜率 b（2026，35–90 岁） | {refs['M'].gompertz_slope(2026):.4f} | {refs['F'].gompertz_slope(2026):.4f} |")
    fm, ff = refs["M"]._old_fit(2026), refs["F"]._old_fit(2026)
    rows.append(f"| 极高龄拟合 a / b / s²（2026，60–94 岁，平台 0.70） | {fm[0]:.4f} / {fm[1]:.4f} / {fm[2]:.4f} | {ff[0]:.4f} / {ff[1]:.4f} / {ff[2]:.4f} |")
    for x in (40, 60, 80, 90, 95, 100, 105, 110):
        rows.append(f"| 2026 年 {x} 岁年死亡率 μ | {refs['M'].mu_period(x, 2026):.5f} | {refs['F'].mu_period(x, 2026):.5f} |")
    return "\n".join(rows)


def block_phenoage_ref() -> str:
    r = J(DATA / "phenoage_reference.json")
    rows = ["| 性别 | 参考 PhenoAge 多项式（a·age² + b·age + c） | 样本量 |", "|---|---|---|"]
    for s in "MF":
        a, b, c = r["fit"][s]["poly_coef_high_to_low"]
        rows.append(f"| {s} | {a:.6f}·age² + {b:.5f}·age {c:+.4f} | {r['n'][s]:,} |")
    rows += ["", "| 年龄 | " + " | ".join(str(a) for a in r["gap_sd"]["M"]["ages"]) + " |",
             "|---|" + "---|" * len(r["gap_sd"]["M"]["ages"])]
    for s in "MF":
        rows.append(f"| 参考 PhenoAge（{s}） | " + " | ".join(f"{v:.1f}" for v in r["fit"][s]["phenoage"]) + " |")
    for s in "MF":
        rows.append(f"| 同龄差值 SD（{s}） | " + " | ".join(f"{v:.2f}" for v in r["gap_sd"][s]["sd"]) + " |")
    return "\n".join(rows)


def block_biovariation() -> str:
    from lp import clock
    bv = J(DATA / "biovariation.json")["analytes"]
    rows = ["| 指标 | CVI % | CVA % | 每单位对应 PhenoAge 年数 | 备注 |", "|---|---|---|---|---|"]
    for k in clock.INPUTS:
        ypu = clock.years_per_unit(k)
        unit = "每 1 个 ln 单位" if k == "crp" else "每 1 个规范单位"
        rows.append(f"| {k} | {bv[k]['cvi']} | {bv[k].get('cva', 0)} | {ypu:.4f}（{unit}） | {bv[k].get('note', '')} |")
    s = J(RES / "sensitivity.json")["phenoage_noise"]
    rows.append("")
    rows.append(f"典型值（白蛋白 45、肌酐 80、血糖 5.2、hs-CRP 1.0 mg/L、淋巴 31%、MCV 90、RDW 13.0、ALP 70、WBC 6.2）下单次噪声 SD = **{s['sd_years']} 年**，"
                f"两次测量 95% 参考变化值 = **{s['rcv95_two_tests']} 年**；方差占比：" + "、".join(f"{k} {v * 100:.1f}%" for k, v in s["shares"].items()) + "。")
    return "\n".join(rows)


def block_domains() -> str:
    p = J(DATA / "params.json")
    rows = ["| id | 名称 | 输入键 | 形状 | 剂量反应（值（95% CI）/ 每多少单位） | clip | 人群分布键 | 因果 | 文献编号 |", "|---|---|---|---|---|---|---|---|---|"]
    for d in p["domains"]:
        if d["shape"] == "loglinear":
            dr = "RR " + rr_txt(d["rr"])
        elif d["shape"] == "hinge":
            dr = f"拐点 {d.get('knot_lo', d.get('knot'))}/{d.get('knot_hi', d.get('knot'))}；下方 RR {rr_txt(d['rr_below'])}；上方 RR {rr_txt(d['rr_above'])}"
        else:
            lv = "；".join(f"{k} {rr_txt(v) if v not in (1, 1.0) else '1'}" for k, v in d["levels"].items())
            if d.get("levels_by_region"):
                lv += "；地区：" + "；".join(f"{reg}.{k} {rr_txt(v)}" for reg, m in d["levels_by_region"].items() for k, v in m.items())
            if d.get("pop_levels"):
                lv += "；人群：" + "；".join(f"{k} {rr_txt(v) if v not in (1, 1.0) else '1'}" for k, v in d["pop_levels"].items())
            dr = lv
        if d.get("norm_kind") == "categorical_mid":
            dr += "；人群分档中点 " + "，".join(f"{s}:" + "/".join(str(x) for x in d["mids"][s].values()) for s in "MF")
        specs = [d["rr"]] if d["shape"] == "loglinear" else ([d["rr_below"], d["rr_above"]] if d["shape"] == "hinge" else
                 list(d["levels"].values()) + [v for m in d.get("levels_by_region", {}).values() for v in m.values()] + list(d.get("pop_levels", {}).values()))
        lit = ",".join(sorted({x for v in specs if isinstance(v, dict) for x in str(v.get("lit", "")).split(",") if x}))
        rows.append(f"| {d['id']} | {d['name_zh']} | `{d['input']}` | {d['shape']} | {dr} | {d.get('clip', '')} | {d['norm']} | {'是' if d.get('causal') else ''} | {lit or ''} |")
    rows.append("")
    def sources(d):
        if d["shape"] == "loglinear":
            return d["rr"]["source"]
        if d["shape"] == "hinge":
            return f"下方：{d['rr_below']['source']}；上方：{d['rr_above']['source']}"
        vals = list(d["levels"].values()) + [v for m in d.get("levels_by_region", {}).values() for v in m.values()] + list(d.get("pop_levels", {}).values())
        seen, out = set(), []
        for v in vals:
            if isinstance(v, dict) and v["source"] not in seen:
                seen.add(v["source"])
                out.append(v["source"])
        return " / ".join(out)
    rows.append("出处原文：")
    rows.append("")
    rows += [f"- **{d['id']}**：{sources(d)}" for d in p["domains"]]
    return "\n".join(rows)


def block_devices() -> str:
    dv = J(DATA / "params.json")["devices"]
    rows = ["| 项目 | 参数 | 说明 |", "|---|---|---|"]
    for k, v in dv["watch_vo2max"].items():
        rows.append(f"| 手表 VO2max · {k} | 偏差 {v['bias']:+} ± {v['bias_sd']}，随机 SD {v['sd']} | {v['source']} |")
    rows.append(f"| 实验室 CPET VO2max | 随机 SD {dv['cpet_vo2max_sd']} | 测量误差 |")
    w = dv["watch_rhr"]
    rows.append(f"| 手表静息心率 → 诊室 | +{w['to_clinic']} ± {w['to_clinic_sd']} bpm，随机 SD {w['sd']} | {w['source']} |")
    rows.append(f"| 体检脉搏 | 随机 SD {dv['office_pulse_sd']} | 单次测量 |")
    s = dv["watch_sleep"]
    rows.append(f"| 手表睡眠 → 问卷口径 | 多报 = max({s['min_overreport']}, {s['overreport_at_5h']} {s['overreport_slope']:+}×(TST−5))，SD {s['to_selfreport_sd']}；随机 SD {s['sd']} | {s['source']} |")
    rows.append(f"| 问卷睡眠 | 随机 SD {dv['selfreport_sleep_sd']} | |")
    rows.append(f"| 家庭血压 4 周均值 | 随机 SD {dv['home_bp_sd']}；换算点 {dv['home_to_office_sbp']} | {dv['home_to_office_source']} |")
    rows.append(f"| 体检收缩压 | 单次随机 SD {dv['office_sbp_sd']}（最近 n≤2 次均值，SD/√n） | |")
    rows.append(f"| LDL-C | 随机 CV {dv['ldl_cv']} | EFLM CVI 7.56% |")
    rows.append(f"| BMI | 随机 SD {dv['bmi_sd']} | |")
    rows.append(f"| 握力 | 随机 SD {dv['grip_sd']} kg | |")
    return "\n".join(rows)


def block_calibration() -> str:
    c = J(DATA / "params.json")["calibration"]
    g = c["gap"]
    rows = [f"PhenoAge 差值分段：拐点 {g['knots']}；斜率（低段 / 中段 / 高段）= {g['slopes']}，SE = {g['slopes_sd']}。", "",
            "| 领域 | 有 PhenoAge：c（SD） | 规则 | 无 PhenoAge：c（SD） | 规则 |", "|---|---|---|---|---|"]
    for k in c["with_clock"]:
        a, b = c["with_clock"][k], c["without_clock"][k]
        rows.append(f"| {k} | {a['value']}（{a['sd']}） | {a['rule']} | {b['value']}（{b['sd']}） | {b['rule']} |")
    rows.append("")
    rows.append("各系数的依据（`basis` 字段原文）：")
    for k in c["with_clock"]:
        rows.append(f"- **{k}**：有 PhenoAge — {c['with_clock'][k]['basis']}；无 PhenoAge — {c['without_clock'][k]['basis']}")
    return "\n".join(rows)


def block_norms() -> str:
    n = J(DATA / "population_norms_china.json")["markers"]
    out = []
    cont = [k for k, v in n.items() if "mean" in v["M"][0]]
    cat = [k for k, v in n.items() if "p" in v["M"][0]]
    bands = [f"{r['age_lo']}–{r['age_hi']}" for r in n[cont[0]]["M"]]
    out.append("连续指标（均值 / SD；带 mean_se 的表示人群均值本身的不确定性）：")
    out.append("")
    out.append("| 指标 | 性别 | " + " | ".join(bands) + " |")
    out.append("|---|---|" + "---|" * len(bands))
    for k in cont:
        for s in "MF":
            cells = [f"{r['mean']:g}/{r['sd']:g}" + (f"±{r['mean_se']:g}" if r.get("mean_se") else "") for r in n[k][s]]
            out.append(f"| {k} | {s} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("分类指标（各类别占比）：")
    out.append("")
    out.append("| 指标 | 性别 | " + " | ".join(bands) + " |")
    out.append("|---|---|" + "---|" * len(bands))
    for k in cat:
        for s in "MF":
            cells = ["/".join(f"{v:.3f}" for v in r["p"].values()) for r in n[k][s]]
            out.append(f"| {k}（{'/'.join(n[k][s][0]['p'].keys())}） | {s} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("出处：" + "；".join(f"**{k}** {n[k]['source']}" for k in n))
    return "\n".join(out)


def block_scenarios() -> str:
    s = J(DATA / "params.json")["scenarios"]
    rows = ["| 情景 | 名称 | 类型与参数 | 权重 |", "|---|---|---|---|"]
    for k, d in s["defs"].items():
        params = {kk: vv for kk, vv in d.items() if kk not in ("name_zh", "desc_zh")}
        rows.append(f"| {k} | {d['name_zh']} | `{json.dumps(params, ensure_ascii=False)}` | {s['weights'][k]} |")
    rows.append("")
    rows.append(f"中心情景：{s['central']}。权重依据：{s['weights_rationale']}")
    return "\n".join(rows)


def block_interventions() -> str:
    p = J(DATA / "params.json")
    rows = ["| id | 名称 | 证据 | 依从性 | 效应（完全坚持时） | 适用条件 | 核心 | 处方 |", "|---|---|---|---|---|---|---|---|"]
    for iv in p["interventions"]:
        eff = []
        for e in iv["effects"]:
            if e.get("type") == "direct":
                eff.append(f"直接 RR {rr_txt(dict(e['rr'], per=1))}")
            elif e.get("set") is not None:
                eff.append(f"{e['domain']} → {e['set']}")
            else:
                eff.append(f"{e['domain']} {'×(1' if e.get('relative') else ''}{e['mean']:+}{')' if e.get('relative') else ''} ± {e['sd']}"
                           + (f"，下限 {e['floor']}" if e.get("floor") is not None else "") + (f"，上限 {e['ceiling']}" if e.get("ceiling") is not None else ""))
        rows.append(f"| {iv['id']} | {iv['name_zh']} | {iv['evidence']} | {iv.get('adherence')}（{iv.get('adherence_kind', 'fraction')}） | {'；'.join(eff) or '—'} | "
                    f"{json.dumps(iv.get('when', {}), ensure_ascii=False) if iv.get('when') else '—'} | {'是' if iv.get('core') else ''} | {'是' if iv.get('medical') else ''} |")
    rows.append("")
    rows.append("各干预的来源（`sources` 字段原文）：")
    for iv in p["interventions"]:
        rows.append(f"- **{iv['id']}**：" + "；".join(iv.get("sources", [])))
    return "\n".join(rows)


def block_misc_params() -> str:
    p = J(DATA / "params.json")
    rows = ["| 参数 | 值 | 位置 |", "|---|---|---|"]
    rows.append(f"| 参数版本 | {p['version']} | `params.json: version` |")
    rows.append(f"| 极高龄拟合年龄 / 过渡年龄 | {p['old_age']['fit_ages']} / {p['old_age']['blend_ages']} | `old_age` |")
    rows.append(f"| 死亡率平台 | {p['old_age']['plateau_hazard']['value']}（SD {p['old_age']['plateau_hazard']['sd']}；参考曲线只用点值） | `old_age.plateau_hazard` |")
    rows.append(f"| 脆弱性方差 s² | {p['frailty']['s2']['value']}（SD {p['frailty']['s2']['sd']}，抽样截断在 [0.06, 0.35]） | `frailty.s2` |")
    rows.append(f"| hs-CRP 缺失时补入 | {p['clock']['crp_impute_mg_l']} mg/L，额外方差 {p['clock']['crp_impute_extra_var']} 年² | `clock` |")
    rows.append(f"| PhenoAge 差值随机游走 | 每年 {p['clock']['q_per_year']} 年² | `clock.q_per_year` |")
    pc = p["pace"]
    rows.append(f"| LongPi Pace | 先验 SD {pc['prior_slope_sd']}，截距先验 SD {pc['prior_level_sd']}，快照噪声 {pc['obs_sd_years']} 年，至少 {pc['min_n']} 次且信息增益 ≥ {pc['min_info_gain']} | `pace` |")
    rows.append(f"| 获益阈值 | ΔLongPi Age ≤ −{p['benefit_threshold_years']} 年 | `benefit_threshold_years` |")
    return "\n".join(rows)


def block_validation() -> str:
    c = J(RES / "nhanes_calibration.json")
    ph = J(RES / "phenoage_validation.json")
    vw, vo, comp = c["validation"]["with_clock"], c["validation"]["without_clock"], c["validation"]["comparators"]
    rows = [f"NHANES 分析表：{c['n_total']:,} 人，{c['deaths_total']:,} 例死亡。PhenoAge 子样本：{ph['n']:,} 人，{ph['deaths']:,} 例死亡，{ph['person_years']:,} 人年。", "",
            "| PhenoAge 单变量检验 | 值 |", "|---|---|",
            f"| HR / 年（年龄 + 性别 + 差值） | 差值 {ph['cox']['age_sex_gap']['gap']['hr']}，年龄 {ph['cox']['age_sex_gap']['age']['hr']} |",
            f"| 差值年 → 风险年（线性） | {ph['gap_years_to_mortality_years']} |",
            f"| C 指数：年龄 + 性别 → 加入差值 | {ph['cox']['age_sex']['c_index']} → {ph['cox']['age_sex_gap']['c_index']} |",
            f"| 亚裔（2015–2018）平均差值 | {ph['asian_2015_2018']['mean_gap']}（n = {ph['asian_2015_2018']['n']}） |", "",
            "| 时间外推验证（1999–2008 定系数，2009–2018 检验） | 有 PhenoAge | 无 PhenoAge |", "|---|---|---|",
            f"| 人数 / 死亡 | {vw['n']:,} / {vw['deaths']:,} | {vo['n']:,} / {vo['deaths']:,} |",
            f"| HR / LongPi 年 | {vw['hr_per_longpi_year']:.4f} | {vo['hr_per_longpi_year']:.4f} |",
            f"| HR / 年龄年 | {vw['hr_per_age_year']:.4f} | {vo['hr_per_age_year']:.4f} |",
            f"| 斜率比（95% CI） | {vw['slope_ratio']:.3f}（{vw['slope_ratio_lo']:.3f}–{vw['slope_ratio_hi']:.3f}） | {vo['slope_ratio']:.3f}（{vo['slope_ratio_lo']:.3f}–{vo['slope_ratio_hi']:.3f}） |",
            f"| C 指数 | {vw['c_age_sex']:.4f} → {vw['c_with_longpi']:.4f} | {vo['c_age_sex']:.4f} → {vo['c_with_longpi']:.4f} |",
            f"| LongPi 差值 SD（年） | {vw['gap_sd']:.2f} | {vo['gap_sd']:.2f} |",
            f"| 对照：Demo 拼法 / PhenoAge 1:1 的斜率比 | {comp['demo']['slope_ratio']:.3f} / {comp['pheno_only']['slope_ratio']:.3f} | — |", "",
            "| 可迁移性（文献 ln HR 的斜率，1 = 成立） | n | 死亡 | 调整年龄性别 | 再调整 PhenoAge |", "|---|---|---|---|---|"]
    for k, v in c["q1_transport"].items():
        adj = f"{v['slope_adj_phenoage']:.2f}（{v['lo_adj']:.2f}–{v['hi_adj']:.2f}）" if "slope_adj_phenoage" in v else "—"
        rows.append(f"| {k} | {v['n']:,} | {v['deaths']:,} | {v['slope']:.2f}（{v['lo']:.2f}–{v['hi']:.2f}） | {adj} |")
    return "\n".join(rows)


def block_sensitivity() -> str:
    s = J(RES / "sensitivity.json")
    h = J(RES / "scenario_history.json")
    rows = [f"- 年龄换算核对：40–80 岁 `年龄 + ln R/b` 与生命表精确反解最大差 "
            f"{max(abs(r['diff']) for r in s['age_equivalence_check']['rows'] if r['age'] >= 40):.2f} 岁；30–35 岁最大差 "
            f"{max(abs(r['diff']) for r in s['age_equivalence_check']['rows'] if r['age'] < 40):.2f} 岁（生命表在此年龄段被意外伤害拉平）。",
            f"- 120 指数（40 岁男性，R = 1.25）：脆弱性假设下 {s['index_R125_range_frailty'][0]:.1f}–{s['index_R125_range_frailty'][1]:.1f}；比例风险下 {s['index_R125_range_PH'][0]:.1f}–{s['index_R125_range_PH'][1]:.1f}。",
            "- LongPi Pace 功效（年度体检，后验 SD 比先验窄的百分比）：" + "；".join(
                f"{r['annual_tests']} 次 {r['reduction_vs_prior_pct']}%" + ("" if r["draws_per_test"] == 1 else "（每次两管）")
                for r in s["pace_power"] if r["annual_tests"] in (4, 6, 8, 10)),
            f"- 死亡率改善历史：{h['countries']} 个国家/地区、{h['windows']:,} 个 20 年窗口；60–89 岁中位 {h['r60_89']['median'] * 100:.2f}%/年（P10 {h['r60_89']['p10'] * 100:.2f}%，P90 {h['r60_89']['p90'] * 100:.2f}%）；"
            f"<0.5% 占 {h['r60_89']['share_lt_0.5pct'] * 100:.1f}%，0.5–2.5% 占 {h['r60_89']['share_0.5_2.5pct'] * 100:.1f}%，≥2.5% 占 {h['r60_89']['share_ge_2.5pct'] * 100:.1f}%；"
            f"90–99 岁中位 {h['r90_99']['median'] * 100:.2f}%/年，<0.5% 占 {h['r90_99']['share_lt_0.5pct'] * 100:.1f}%。",
            f"- 中国（WPP）60–89 岁年改善：男 2000–2019 {h['china']['M']['2000_2019_r60_89'] * 100:.2f}%、2026–2050 {h['china']['M']['2026_2050_r60_89'] * 100:.2f}%；"
            f"女 2000–2019 {h['china']['F']['2000_2019_r60_89'] * 100:.2f}%、2026–2050 {h['china']['F']['2026_2050_r60_89'] * 100:.2f}%。"]
    return "\n".join(rows)


def block_demo() -> str:
    o = J(SKILL / "examples" / "output" / "results.json")
    r = o["results"]
    la = r["longpi_age"]
    rows = [f"- 日历年龄 {la['chrono']}；LongPi Age {la['value']['median']}（80% 区间 {la['value']['p10']}–{la['value']['p90']}）；时钟层 {la['clock_delta']['median']:+} 年；功能领域 {la['function_delta']['median']:+} 年；系数组 {la['coef_set']}。",
            "- 各领域（点估计，年）：" + "；".join(f"{d['domain']} {d['years']['median']:+}" + ("" if d["measured"] else "（未测）") for d in la["domains"]) + "。",
            "- 120 指数：加权 " + str(r["index120"]["weighted_index"]["median"]) + "；" + "；".join(
                f"{k} {v['name']} {v['index']['median']}（{v['index']['p10']}–{v['index']['p90']}），期望寿命 {v['life_exp']['median']}（人群 {v['ref_life_exp']}）"
                for k, v in r["index120"]["scenarios"].items()) + "。",
            "- 干预（预期 ΔLongPi Age）：" + "；".join(
                f"{i['id']} {i['d_longpi_age']['median']:+}" + ("（作用很小，不展示）" if i.get("small_effect") else "")
                for i in r["interventions"] if i["quantified"]) + "。",
            f"- LongPi Pace：{la['pace']['status']}（{la['pace']['n']} 次，信息增益 {la['pace']['info_gain']}，还需约 {la['pace']['more_annual_tests_needed']} 次年度体检）。",
            f"- 甲基化：{'计入 ' + la['methylation']['clock'] if la['methylation']['counted'] else '未计入（' + ('现有报告为 ' + '、'.join(x['clock_type'] for x in la['methylation'].get('provided_not_counted', [])) if la['methylation'].get('provided_not_counted') else '未做') + '）'}，"
            f"{la['methylation_delta']['median']:+} 年；未测时约 ±{la['methylation']['unmeasured_sd_years']} 年（1 SD）。",
            f"- 数据完整度 {r['data_value']['completeness_pct']}%：80% 区间宽度 只知道年龄性别 {r['data_value']['width_none']} → 现在 {r['data_value']['width_now']} → 全部做完 {r['data_value']['width_all']} 岁。",
            "- 补测清单：" + "；".join(f"{g['id']}（{g['status']}）{r['data_value']['width_now']} → {g['width_after']} 岁" for g in r["data_value"]["items"]) + "。",
            "- 临床计算器：" + json.dumps(r["clinical"], ensure_ascii=False)]
    return "\n".join(rows)


def block_units() -> str:
    from lp import units
    rows = ["| 指标 | 规范单位 |", "|---|---|"]
    for k, v in units.CANONICAL.items():
        rows.append(f"| {k} | {v} |")
    rows += ["", "| 指标 | 输入单位 | 乘以 |", "|---|---|---|"]
    for (k, u), f in units._FACTORS.items():
        rows.append(f"| {k} | {u} | {f:.6g} |")
    rows.append("| hba1c | mmol/mol（IFCC） | NGSP% = IFCC/10.929 + 2.15 |")
    rows.append("")
    rows.append("可识别的单位写法（不区分大小写、忽略空格）：" + "、".join(f"`{k}`→{v}" for k, v in units._ALIASES.items()) + "。")
    return "\n".join(rows)


def block_worked_example() -> str:
    import math as _m
    from lp import domains as DM, engine as EN, mortality as M
    o = J(SKILL / "examples" / "output" / "results.json")
    r = o["results"]
    p = J(DATA / "params.json")
    b = M.Reference("M").gompertz_slope(2026)
    age = r["person"]["chrono_age"]
    out = [f"演示用户 D01：男，{age} 岁，Gompertz 斜率 b = {b:.4f}。下面用参数点值手算，结果与 results.json 中蒙特卡洛期望值对照。", ""]
    # blood pressure
    home = o["wearables"]["home_bp"]["sbp"]
    office = EN.office_from_home(home)
    sp = DM.spec("bp")
    pr = DM.draw_params(sp, None)
    nb = DM.norm_for(sp, "M", age)
    lme = DM.log_mean_exp_pop(sp, pr, "M", age)
    lhr = DM.log_hr(sp, pr, office, "M", age)
    eng = next(d for d in r["longpi_age"]["domains"] if d["id"] == "bp")["years"]["median"]
    out += ["**血压**",
            f"1. 家庭血压 4 周均值 {home} → 诊室口径：在换算点 (130,130)–(135,140) 之间线性插值 = {office:.1f} mmHg。",
            f"2. β = ln(RR)/per = ln({sp['rr']['value']})/{sp['rr']['per']} = {pr['beta']:.6f} /mmHg；clip {sp['clip']}。",
            f"3. 同龄（{nb['age_lo']}–{nb['age_hi']} 岁）男性 SBP ~ N({nb['mean']}, {nb['sd']}²)；clip 下限在 ±4 SD 内，用 20 点 Gauss-Hermite：ln E[exp f(X)] = {lme:.4f}"
            f"（若不截断，解析值为 {pr['beta'] * nb['mean'] + 0.5 * (pr['beta'] * nb['sd']) ** 2:.4f}）。",
            f"4. l = β·x − ln E = {pr['beta']:.6f}×{office:.1f} − {lme:.4f} = {lhr:.4f}；c = {p['calibration']['with_clock']['bp']['value']}；换算年数 = {lhr:.4f}/{b:.4f} = **{lhr / b:+.2f} 年**"
            f"（引擎蒙特卡洛期望值 {eng:+.2f} 年）。", ""]
    # smoking
    sp = DM.spec("smoking")
    pr = DM.draw_params(sp, None, "urban")
    nb = DM.norm_for(sp, "M", age)
    terms = " + ".join(f"{nb['p'][k]:.3f}×{_m.exp(pr['log_rr_pop'][k]):.3f}" for k in nb["p"])
    tot = sum(nb["p"][k] * _m.exp(pr["log_rr_pop"][k]) for k in nb["p"])
    eng = next(d for d in r["longpi_age"]["domains"] if d["id"] == "smoking")["years"]["median"]
    out += ["**吸烟（从不吸烟）**",
            f"1. 同龄男性类别占比（从不/已戒/现吸）与人群 RR：Σ p·RR = {terms} = {tot:.4f}。",
            f"2. l(从不) = ln 1 − ln {tot:.4f} = {-_m.log(tot):.4f}；换算 = **{-_m.log(tot) / b:+.2f} 年**（引擎 {eng:+.2f} 年）。", ""]
    # clock
    g = p["calibration"]["gap"]
    gm = r["longpi_age"]["clock"]["gap_now_mean"]
    gl = EN.gap_loghr(gm, g)
    out += ["**时钟层**",
            f"1. 四次 PhenoAge 差值经卡尔曼合并，当前差值后验 {gm:+.2f} ± {r['longpi_age']['clock']['gap_now_sd']} 岁。",
            f"2. 位于拐点 {g['knots']} 之间，g(G) = {g['slopes'][1]}×({gm:+.2f}) = {gl:.4f}；换算 = **{gl / b:+.2f} 年**"
            f"（引擎对后验分布取期望：{r['longpi_age']['clock_delta']['median']:+.2f} 年）。", ""]
    # total
    out += ["**合计**",
            f"LongPi Age = {age} + ln E[R]/b = {r['longpi_age']['value']['median']}（各领域点估计之和 {sum(d['years']['median'] for d in r['longpi_age']['domains']) + r['longpi_age']['clock_delta']['median']:+.2f} 年，"
            f"与总差值 {r['longpi_age']['delta']['median']:+.2f} 年的差别来自对数与期望不可交换）。"]
    return "\n".join(out)


def block_tests() -> str:
    lines = (SKILL / "tests" / "test_engine.py").read_text(encoding="utf-8").splitlines()
    rows = ["| 测试类 | 测试 | 检查什么 |", "|---|---|---|"]
    cls = ""
    desc = {
        "test_matches_bioage_phenoage_calc": "与 BioAge phenoage_calc(orig=TRUE) 结果 50.475248839667486 一致（9 位小数）",
        "test_linear_in_predictor": "RDW +1% 使 PhenoAge 增加 0.3306156/0.090165 年（线性）",
        "test_noise_is_plausible": "典型值单次噪声在 1–3 年之间，方差占比之和为 1",
        "test_conversions": "mg/dL、g/dL、IFCC 换算正确；未知单位报错",
        "test_chinese_unit_spellings_and_passthrough": "×10^9/L、×10⁹/L 写法可识别；Lp(a) 原样保留",
        "test_levels_by_date": "戒烟前为现吸、戒烟 <5 年、≥5 年、未知戒烟年份、缺失",
        "test_gompertz_slope": "2026 年男性 b 在 0.09–0.11 之间",
        "test_life_expectancy_matches_wpp": "从 0 岁按 2026 年死亡率算出的期望寿命与 WPP e0 相差 <0.6 岁",
        "test_frailty_identity": "R=1 时个人生存曲线与参考曲线逐点一致",
        "test_hazard_ratio_attenuates_at_extreme_age": "起始风险比 ≈ R，约 115 岁时风险比 <R 且 >1",
        "test_old_age_hazard_below_plateau": "96–130 岁死亡率不超过平台 0.70",
        "test_index_monotone_in_risk": "120 指数随 R 单调下降，R=1 时为 100",
        "test_population_mean_hazard_is_one": "每个领域、每个性别：按人群分布抽样时 E[exp l] ≈ 1（±0.03）",
        "test_quadrature_matches_closed_form": "Gauss-Hermite 与正态对数矩母函数解析值一致（10 位小数）",
        "test_china_par_table2": "China-PAR 复现论文 Table 2（男女各 4 个年龄，±0.15 个百分点）",
        "test_apple_health_export": "Apple 健康 export.xml（含 DTD、元数据子元素、控制字符）：步数取较大来源、睡眠只算睡着的分期、lb→kg、mph→m/s；缓存与直接读取结果一致",
        "test_numeric_dates_resolved_per_file": "CGM、家庭血压的 日-月-年 / 月-日-年 按整列判断；无法判断时报错而不是猜",
        "test_blood_test_offered_and_narrows": "只有年龄性别时完整度为 0、首选抽血；加一次血检后区间至少窄 1 岁，所有补测项收窄为正",
        "test_grimage_counted_and_shrunk": "第一代时钟不计入；GrimAge2 计入，加速按 NHANES 参考算对，计入量为正且小于不收缩时的值",
        "test_exercise_library_complete": "动作库 ≥20 个、id 唯一、必填字段齐全、每张图片文件存在",
        "test_abnormal_blood_test_flagged_and_excluded": "MCV 65 / RDW 19 被标记；不计入 MCV、RDW 后差值减少 >3 岁、噪声变大；整次不计入时不出点",
        "test_demo_report_has_modules": "演示叙述（含训练、补充剂）通过检查；默认补充资料非空；动作库引用带出步骤和内嵌图片；未知引用报错",
        "test_outputs": "演示用户端到端：区间顺序正确、三个情景、有干预；补测后区间 < 现在 < 只知道年龄性别，完整度在 0–100",
        "test_missing_everything_is_neutral": "没有任何数据的 45 岁男性，LongPi Age = 45 ± 0.35",
        "test_demo_narrative_passes_checks": "演示叙述通过叙述检查",
    }
    for l in lines:
        m = re.match(r"^class (\w+)\(", l)
        if m:
            cls = m.group(1)
        m = re.match(r"^\s+def (test_\w+)\(", l)
        if m:
            rows.append(f"| {cls} | `{m.group(1)}` | {desc.get(m.group(1), '')} |")
    return "\n".join(rows)


def block_schema_rules() -> str:
    from lp import schema
    rows = ["换算到规范单位后的合理范围（超出只报警告，提示多半是单位填错）：", "",
            "| 指标 | 下限 | 上限 |", "|---|---|---|"]
    for k, (lo, hi) in schema.RANGES.items():
        rows.append(f"| {k} | {lo} | {hi} |")
    rows += ["", f"风险卡等级只能是：{'、'.join(sorted(schema.LEVELS))}。叙述中禁止出现的后台术语：{'、'.join(schema.BACKEND_TERMS)}。",
             f"PhenoAge 九项：{'、'.join(schema.PHENO)}。"]
    return "\n".join(rows)


def block_clock_residual() -> str:
    from lp import mortality as M
    p = J(SKILL / "data" / "params.json")["clock_residual"]
    res = J(ROOT / "evidence" / "results" / "nhanes_methylation.json")["blood_clock_residual"]
    bm, bf = M.Reference("M").gompertz_slope(2026), M.Reference("F").gompertz_slope(2026)
    rows = ["| 年龄段中点 | 残差 SD（对数风险） | 约合 LongPi 年（男 / 女，1 SD） | NHANES 人数 |", "|---|---|---|---|"]
    for a, sd, b in zip(p["age_mid"], p["sd"], res["by_age"]):
        rows.append(f"| {a} | {sd} | {sd / bm:.1f} / {sd / bf:.1f} | {b['n']:,} |")
    rows += ["", f"样本：{res['n']:,} 人、{res['deaths']:,} 例死亡；回归 有时钟 LP = {res['regression']['intercept']:.3f} + {res['regression']['lp_without']:.3f} × 无时钟 LP + 年龄、性别项；"
                 f"残差加入无时钟模型后 C 指数 {res['c_without']:.3f} → {res['c_with_resid']:.3f}（残差确有死亡信息）。引擎按年龄线性插值，抽样 N(−σ²/2, σ²)。"]
    return "\n".join(rows)


def block_methylation() -> str:
    pm = J(SKILL / "data" / "params.json")["methylation"]
    res = J(ROOT / "evidence" / "results" / "nhanes_methylation.json")["methylation"]
    rows = [f"样本：{res['n']:,} 人（{res['age_range'][0]:.0f}–{res['age_range'][1]:.0f} 岁），{res['deaths']:,} 例死亡，随访中位 {res['median_follow_up_years']:.1f} 年；"
            f"LongPi LP 在此样本中的 Cox 系数 {res['lp_coef_in_base']:.3f}，C 指数（年龄 + 性别 + LP）{res['c_base']:.4f}。", "",
            "| 时钟 | 单独 HR/SD | 被 LP 解释的方差 | 残差 SD | LongPi 之外 HR/SD 残差 | p | C 指数增加 | LR χ² | 加权 HR | 种族组均值 SD | 计入 |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, c in res["clocks"].items():
        import math
        rows.append(f"| {name} | {c['hr_per_sd_alone']:.3f} | {c['r2_explained_by_lp']:.1%} | {c['sd_resid']:.3g} {c['unit']} | {c['hr_per_sd_resid']:.3f} | {c['p_resid']:.1e} | "
                    f"{c['c_with_clock'] - c['c_base']:+.4f} | {c['lr_chi2']:.1f} | {math.exp(c['weighted_beta_per_sd_resid']):.3f} | "
                    f"{c['race_group_sd_years'] if c['race_group_sd_years'] is not None else '—'} | {'是' if name in pm['counted'] else ''} |")
    rows += ["", "引擎参数（`params.json: methylation`）：", "", "| 时钟 | 参考曲线 男 / 女（值 = a + b·年龄） | 残差回归 | σ_M（年） | β（/年，SE） | s_pop | 收缩系数 k |", "|---|---|---|---|---|---|---|"]
    for name, c in pm["clocks"].items():
        k = c["sd_resid"] ** 2 / (c["sd_resid"] ** 2 + pm["s_lab"] ** 2 + c["s_pop"] ** 2)
        ro = c["resid_on"]
        rows.append(f"| {name} | {c['ref']['M'][0]} + {c['ref']['M'][1]}·age / {c['ref']['F'][0]} + {c['ref']['F'][1]}·age | "
                    f"{ro['intercept']} + {ro['lp']}·LP + {ro['age']}·age + {ro['male']}·男 | {c['sd_resid']} | {c['beta']}（{c['beta_se']}） | {c['s_pop']} | {k:.3f} |")
    rows += ["", f"s_lab = {pm['s_lab']} 年：{pm['s_lab_source']}。", f"s_pop：{pm['s_pop_source']}。",
             f"未测时默认时钟 {pm['default_unmeasured']}；结果有效期 {pm['max_age_years']} 年。"]
    return "\n".join(rows)


def block_data_menu() -> str:
    dm = J(SKILL / "data" / "params.json")["data_menu"]
    rows = [f"每项比较 {dm['n_draws']} 次同一组抽样（种子 7）；收窄 < {dm['show_min_years']} 年不展示。典型血检值（算单次噪声）：" +
            "、".join(f"{k} {v}" for k, v in dm["typical_blood"].items()) + "。", "",
            "| id | 文案（未测 / 设备 / 换更准方法） | 做了以后剩下的测量误差 | 难度 | 费用 |", "|---|---|---|---|---|"]
    for aid, a in dm["actions"].items():
        did = aid.split(":", 1)[1] if aid.startswith("dom:") else None
        err = (f"SD {dm['after_sd'][did]}" if did in dm["after_sd"] else (f"CV {dm['after_cv'][did]:.1%}" if did in dm["after_cv"] else "分类，无")) if did else \
            {"blood_panel": "单次 PhenoAge 噪声（典型值）", "hs_crp": "去掉 CRP 补入的额外方差", "blood_repeat": "加一次同样噪声的测量（卡尔曼合并）",
             "methylation": "残差取 0，按 s_lab、s_pop 收缩"}.get(aid, "")
        labels = " / ".join(x for x in (a.get("label"), a.get("label_missing"), a.get("label_device"), a.get("label_better")) if x)
        rows.append(f"| `{aid}` | {labels} | {err} | {a.get('effort', '')} | {a.get('cost', '')} |")
    rows += ["", "不改变 LongPi Age 的数据：" + "；".join(f"{o['what']}：{o['use']}" for o in dm["other_uses"])]
    return "\n".join(rows)


BLOCKS = {
    "function_index": block_function_index, "lifetable": block_lifetable, "phenoage_ref": block_phenoage_ref,
    "biovariation": block_biovariation, "domains": block_domains, "devices": block_devices, "calibration": block_calibration,
    "norms": block_norms, "scenarios": block_scenarios, "interventions": block_interventions, "misc_params": block_misc_params,
    "validation": block_validation, "sensitivity": block_sensitivity, "demo": block_demo,
    "units": block_units, "worked_example": block_worked_example, "tests": block_tests, "schema_rules": block_schema_rules,
    "clock_residual": block_clock_residual, "methylation": block_methylation, "data_menu": block_data_menu,
}


def main() -> int:
    check = "--check" in sys.argv
    doc = DOC.read_text(encoding="utf-8")
    new = doc
    for name, fn in BLOCKS.items():
        pat = re.compile(rf"(<!-- BEGIN GEN:{name} -->\n)(.*?)(<!-- END GEN:{name} -->)", re.S)
        if not pat.search(new):
            print(f"missing block {name}", file=sys.stderr)
            return 2
        new = pat.sub(lambda m: m.group(1) + fn() + "\n" + m.group(3), new)
    if check:
        if new != doc:
            print("generated blocks are out of date; run without --check", file=sys.stderr)
            return 1
        print("all generated blocks match the code and data")
        return 0
    DOC.write_text(new, encoding="utf-8")
    print(f"updated {DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
