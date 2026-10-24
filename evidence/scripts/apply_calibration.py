#!/usr/bin/env python3
"""Copy the NHANES calibration into the skill's params.json and write data/evidence_summary.json.

Usage: apply_calibration.py <results_dir> <skill_data_dir>
"""
import json
import sys
from pathlib import Path

res_dir, data = Path(sys.argv[1]), Path(sys.argv[2])
cal = json.loads((res_dir / "nhanes_calibration.json").read_text())
ph = json.loads((res_dir / "phenoage_validation.json").read_text())
hist = json.loads((res_dir / "scenario_history.json").read_text())
params = json.loads((data / "params.json").read_text())

c = cal["calibration"]
params["calibration"] = {
    "source": "NHANES 1999-2018 with mortality follow-up to 2019 (evidence/scripts/nhanes_calibration.py)",
    "gap": {k: c["gap"][k] for k in ("knots", "slopes", "slopes_sd")},
    "with_clock": {k: {"value": v["value"], "sd": v["sd"], "rule": v["rule"], "basis": v["basis"]} for k, v in c["with_clock"].items()},
    "without_clock": {k: {"value": v["value"], "sd": v["sd"], "rule": v["rule"], "basis": v["basis"]} for k, v in c["without_clock"].items()},
}
(data / "params.json").write_text(json.dumps(params, ensure_ascii=False, indent=1), encoding="utf-8")

vw, vo = cal["validation"]["with_clock"], cal["validation"]["without_clock"]
comp = cal["validation"]["comparators"]
summary = {
    "validation": {
        "数据": f"美国国家健康调查 1999–2018 年成人 {cal['n_total']:,} 人，随访到 2019 年，期间 {cal['deaths_total']:,} 人去世",
        "检验方法": f"只用前 10 年的数据定参数，再拿后 10 年没用过的 {vw['n']:,} 人来检验",
        "LongPi 的 1 岁准不准": f"LongPi 每老 1 岁，死亡风险高 {100 * (vw['hr_per_longpi_year'] - 1):.1f}%；真实年龄每大 1 岁，风险高 {100 * (vw['hr_per_age_year'] - 1):.1f}%。按美国人的吸烟危害计算时两者完全一致（中国人吸烟的相对危害较低，所以略偏保守）",
        "能不能分出风险高低": f"预测谁先去世的准确度（满分 1）：只看年龄和性别 {vw['c_age_sex']:.3f}，加入 LongPi 后 {vw['c_with_longpi']:.3f}",
        "没有血液检测时": f"只用血压、心率、BMI、吸烟等也能用，准确度 {vo['c_age_sex']:.3f} → {vo['c_with_longpi']:.3f}，结果同样偏保守",
        "为什么要校准": f"如果把血液年龄直接 1:1 加进来，1 岁只值约 {comp['pheno_only']['slope_ratio']:.1f} 岁；校准后血液年龄差 1 岁 ≈ 风险差 {c['gap']['slopes'][1] / c['gap']['b_age_nhanes']:.2f} 岁，比同龄人年轻 5 岁以上后基本不再加分",
        "三种情景的权重": f"过去 50 年 28 个统计完善的国家和地区里，60–89 岁死亡率平均每年下降约 {hist['r60_89']['median'] * 100:.1f}%；死亡率停滞不降的时期很少见",
    },
    "sources": [
        "联合国《世界人口展望 2024》中国生命表", "美国国家健康调查（NHANES）1999–2018 及死亡随访", "Levine 2018 血液表型年龄（PhenoAge）",
        "欧洲检验医学联合会生物学变异数据库", "中国慢性病及危险因素监测 2018", "第六次全国国民体质监测公报（2025）",
        "心肺适能、握力、静息心率、睡眠的荟萃分析（Laukkanen 2022、Leong 2015、Zhang 2016、Yin 2017）",
        "降压、降脂的随机对照试验汇总（Ettehad 2016、BPLTTC 2021、CTT 2012）", "中国慢性病前瞻性研究：吸烟与饮酒（Chen 2015、Chan 2022、Millwood 2023）",
        "超百岁老人死亡率（Barbi 2018、Gampe 2021）", "脆弱性模型（Vaupel & Missov 2014）", "延缓衰老情景（Goldman 2013）",
    ],
}
(data / "evidence_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=1))
