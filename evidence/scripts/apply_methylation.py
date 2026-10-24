#!/usr/bin/env python3
"""Copy the NHANES blood-clock residual and methylation-clock estimates into the skill's params.json,
and add the matching rows to data/evidence_summary.json.

Usage: apply_methylation.py <results_dir> <skill_data_dir>

Counted in LongPi Age: GrimAge2 and GrimAge, the clocks whose information on top of the LongPi model
is large and estimated precisely in NHANES. The other clocks are listed with their (small) increments
so the report can say why they are not counted.
"""
import json
import sys
from pathlib import Path

res_dir, data = Path(sys.argv[1]), Path(sys.argv[2])
r = json.loads((res_dir / "nhanes_methylation.json").read_text(encoding="utf-8"))
params = json.loads((data / "params.json").read_text(encoding="utf-8"))

a = r["blood_clock_residual"]
params["clock_residual"] = {
    "age_mid": [round((b["age_lo"] + b["age_hi"]) / 2, 1) for b in a["by_age"]],
    "sd": [b["sd"] for b in a["by_age"]],
    "source": (f"NHANES 1999-2018 PhenoAge sample with core domains (n {a['n']:,}, {a['deaths']:,} deaths): residual SD of the "
               "with-PhenoAge LongPi log HR given the no-blood-test log HR, age and sex (evidence/scripts/nhanes_methylation.py)"),
    "note": "drawn as N(-sd^2/2, sd^2) so the population average risk stays 1; added only when no blood clock is available",
}

mm = r["methylation"]
COUNTED = ["GrimAge2", "GrimAge"]
S_LAB = 2.4
clocks = {}
for name in COUNTED:
    c = mm["clocks"][name]
    other = c["race_groups"].get("Other (incl. Asian)", {}).get("mean_m_years", 0.0)
    clocks[name] = {
        "ref": c["reference"], "resid_on": c["resid_on"], "sd_resid": c["sd_resid"],
        "beta": round(c["beta_per_unit_resid"], 5), "beta_se": round(c["se_per_unit_resid"], 5),
        "s_pop": round(abs(other), 2),
        "hr_per_sd_resid": round(c["hr_per_sd_resid"], 3), "c_gain": round(c["c_with_clock"] - c["c_base"], 4),
        "hr_per_sd_alone": round(c["hr_per_sd_alone"], 3), "r2_explained_by_lp": c["r2_explained_by_lp"],
        "weighted_hr_per_sd_resid": round(2.718281828459045 ** c["weighted_beta_per_sd_resid"], 3),
    }
params["methylation"] = {
    "counted": COUNTED,
    "default_unmeasured": "GrimAge2",
    "max_age_years": 3,
    "s_lab": S_LAB,
    "s_lab_source": ("McEwen LM, et al. Clin Epigenetics 2018;10:123: the same samples on 450K vs EPIC across preprocessing methods "
                     "differed by a median absolute 1.44-3.10 years (systematic offsets). As a normal SD of a difference that is "
                     "2.1-4.6 years, i.e. 1.5-3.3 years per pipeline; mid-point 2.4 (derived)"),
    "s_pop_source": "NHANES: mean residual of the 'Other race (incl. Asian)' group (n 74), used as the scale of a population offset",
    "clocks": clocks,
    "not_counted": {name: {"hr_per_sd_resid": round(c["hr_per_sd_resid"], 3), "c_gain": round(c["c_with_clock"] - c["c_base"], 4),
                           "p": c["p_resid"]}
                    for name, c in mm["clocks"].items() if name not in COUNTED},
    "source": (f"NHANES 1999-2002 DNA methylation epigenetic biomarkers (dnmepi, released 2024-07-31) linked to mortality to 2019: "
               f"{mm['n']:,} adults aged {mm['age_range'][0]:.0f}-{mm['age_range'][1]:.0f}, {mm['deaths']:,} deaths, median follow-up "
               f"{mm['median_follow_up_years']:.1f} y; residual of each clock's age acceleration given the LongPi log HR, age and sex "
               "(evidence/scripts/nhanes_methylation.py)"),
}
(data / "params.json").write_text(json.dumps(params, ensure_ascii=False, indent=1), encoding="utf-8")

ev = json.loads((data / "evidence_summary.json").read_text(encoding="utf-8"))
g2 = mm["clocks"]["GrimAge2"]
first = [mm["clocks"][k] for k in ("Horvath", "Hannum")]
ev["validation"]["没有抽血时差多少"] = (f"没有血液检测时，风险里有一块看不到：在 NHANES {a['n']:,} 人中，这一块的大小相当于风险高低相差 "
                                 f"±{100 * (2.718281828 ** a['sd_overall'] - 1):.0f}%（1 个标准差），一次抽血就能补上")
ev["validation"]["甲基化检测有没有用"] = (
    f"在 NHANES {mm['n']:,} 名 50 岁以上成人（随访约 {mm['median_follow_up_years']:.0f} 年，{mm['deaths']:,} 人去世）中，"
    f"GrimAge2 在 LongPi 已有信息之外，每高 1 个标准差死亡风险再高 {100 * (g2['hr_per_sd_resid'] - 1):.0f}%；"
    f"第一代时钟（Horvath、Hannum）只再高 {100 * (min(c['hr_per_sd_resid'] for c in first) - 1):.0f}–{100 * (max(c['hr_per_sd_resid'] for c in first) - 1):.0f}%，所以只计入 GrimAge2 / GrimAge")
for s in ("美国国家健康调查 1999–2002 DNA 甲基化时钟（2024 年发布）", "McEwen 2018 甲基化年龄的平台与预处理差异"):
    if s not in ev["sources"]:
        ev["sources"].append(s)
(data / "evidence_summary.json").write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"clock_residual": params["clock_residual"], "methylation": {k: v for k, v in params["methylation"].items() if k != "not_counted"}},
                 ensure_ascii=False, indent=1))
