# 项目库与观测的接口约定（引擎 1.1.2）

本文件是 `longpi-report`（引擎）、`longpi-term-builder`（建项）、`longpi-omics`（组学层）三者之间的接口。
改动这里的字段要同时改三处代码和测试。

## 1. 标准编码

所有观测和项的 `code` 用 `命名空间:值`：

| 命名空间 | 用于 | 例 |
|---|---|---|
| `LOINC` | 化验、生命体征、体测 | `LOINC:1884-6`（ApoB） |
| `ICD10` | 已确诊疾病 | `ICD10:E11` |
| `UNIPROT` | 单个蛋白（加平台探针号写进 `platform_probe`） | `UNIPROT:P16860` |
| `HMDB` | 代谢物 | `HMDB:HMDB0000161` |
| `NCBITAXON` | 微生物 | `NCBITAXON:853` |
| `HGNC` | 基因 | `HGNC:1100`（BRCA1） |
| `PGS` | 多基因评分 | `PGS:PGS002308` |
| `LP` | LongPi 自定义的派生量（工具或引擎算出，非国际编码） | `LP:apoe_e4_count`、`LP:steps_daily_mean`、`LP:clock.grimage2_accel`、`LP:screen.crc_fit` |

`LP:` 编码的清单与含义在 `data/observation_codes.json`；新增 `LP:` 编码须先写进该文件。
`person.json` 原有字段到编码的映射也在该文件（`from_person`），引擎据此把老格式输入转成观测。

## 2. observations.json（组学层与读入层的输出）

```json
{
  "schema": "longpi.observations/1",
  "person_code": "U01",
  "observations": [
    {"obs_id": "o1", "code": "LOINC:1884-6", "value": 1.12, "unit": "g/L", "datetime": "2026-05-18",
     "method": "lab", "platform": null, "specimen": "serum",
     "source_file": "体检2026.pdf", "source_locator": "第 3 页",
     "sd": null, "flags": [], "tool": null, "vendor_derived": false,
     "sustained_weeks": null}
  ],
  "genetics": {
    "build": "GRCh38", "source_type": "wgs|wes|chip|vendor_report",
    "qc": {"n_variants": 0, "call_rate": 0.0, "het_rate": 0.0, "sex_check": "ok", "notes": []},
    "ancestry": {"EAS": 0.97, "EUR": 0.01, "AFR": 0.0, "AMR": 0.01, "SAS": 0.01, "method": "...", "panel": "..."},
    "prs": [{"pgs_id": "PGS002308", "trait": "...", "disease_id": "t2d", "raw": 0.0, "z": 0.0, "percentile": 0.0,
             "coverage": 0.0, "min_coverage": 0.0, "scored": true, "ref": "1000G EAS (n 504)", "license": "..."}],
    "apoe": {"genotype": "e3/e4", "e4_count": 1, "rs429358": "C/T", "rs7412": "C/C"},
    "monogenic": [{"gene": "BRCA2", "hgnc": "HGNC:1101", "spdi": "NC_000013.11:32340300:A:", "clnsig": "Pathogenic",
                   "review_stars": 3, "condition": "...", "disease_ids": ["breast_ca"], "acmg_sf": true,
                   "source_type": "wgs", "confirmed_clinical": false, "clinvar_version": "2026-11"}],
    "pgx": [{"gene": "CYP2C19", "diplotype": "*1/*2", "phenotype": "中间代谢型", "rule": "CPIC", "snps": {}}]
  },
  "provenance": [{"step": "prs", "tool": "prs_score", "version": "0.1.0", "ref_data": {"pgs_scoring_file": "PGS002308 hmPOS GRCh38 2025-xx"}}]
}
```

- `method`：`lab` 实验室测量 · `tool` 本地工具由原始矩阵算出 · `vendor` 厂商报告的结果 · `device` 设备 · `self_report` 自述。
  同一编码多来源时优先级 `lab > tool > vendor > device > self_report`，同级取最近。
- `flags`：`treated`（用药下的值）、`acute_illness`、`pregnancy`、`post_exercise`、`non_fasting`、`antibiotics_3m`、`transfusion`。
- `sustained_weeks`：行为类观测已持续的周数（由数据计算；自述的写自述周数并 `method: self_report`）。
- 组学工具只把**有对应项或定性条目**的特征写成观测；不要把成百上千个无结局证据的特征倒进来。
- 原始数据中的个人信息（样本名、条码）不写入 observations.json。

## 3. 项规格（`registry/terms/ext.*.json`）

```json
{
  "id": "ext.apob",
  "name_zh": "载脂蛋白 B",
  "kind": "state",
  "system": "cardiovascular",
  "group": "lipids",
  "input": {"code": "LOINC:1884-6", "unit": "g/L", "platform": null, "methods": ["lab"]},
  "transform": {"shape": "loglinear", "clip": [0.3, 2.5], "log_x": false},
  "reference": {"kind": "normal", "by_sex_age": [{"sex": "M", "age_lo": 18, "age_hi": 99, "mean": 0.95, "sd": 0.25}],
                "source": "..."},
  "effect": {
    "all_cause": {"hr": 1.10, "lo": 1.04, "hi": 1.16, "per": 0.25, "per_unit": "g/L", "direction": "higher_worse"},
    "chd": {"hr": 1.35, "lo": 1.2, "hi": 1.5, "per": 0.25, "per_unit": "g/L", "direction": "higher_worse"}
  },
  "adjusted_for": ["age", "sex", "core.smoking", "core.bp", "core.adiposity", "core.glucose"],
  "overlap": {"coef": 0.5, "coef_sd": 0.2, "rationale_zh": "与 LDL 同一机制，研究未校正 LDL", "mediated_by": {}},
  "transport": {"ancestry": "European", "shrink": 0.8, "sd_inflate": 1.25},
  "population": {"cohort": "...", "n": 0, "events": 0, "ancestry": "European", "age_range": [40, 70], "sex": "both"},
  "measurement": {"sd_abs": null, "cv": 0.05, "source": "..."},
  "persistence": {"half_life_years": 10},
  "exclude_if_flags": ["acute_illness", "pregnancy"],
  "treated_policy": "use_pretreatment",
  "interventions": {"modifiable": true, "note_zh": "..."},
  "test": {"label_zh": "抽血查 ApoB", "cost_level": 1},
  "disclosure": "standard",
  "evidence": {"grade": "B", "design": "meta-analysis", "quote": "原文原句", "pmid": "...", "doi": "...",
               "url": "...", "verified_at": "2026-11-18", "verifier": "longpi-term-builder 0.1.0", "numbers_verified": true},
  "license": {"commercial_use": true, "note": "效应量为文献数据"},
  "status": "active",
  "added_by": "longpi-term-builder",
  "registry_version_added": "2026.11.18-2"
}
```

字段规则：

- `kind`：`state` 身体状态 · `exposure` 暴露（吸烟、饮酒、空气污染） · `behavior` 行为（只进 120 指数） · `genetic` 先天（只进疾病风险）。
- `effect` 的键是结局：`all_cause`，或 `registry/outcomes/` 里的疾病 id。**只有含 `all_cause` 的 state/exposure 项进入 LongPi Age**；
  只为疾病建的项（例如 LDL→冠心病）只写疾病键，不写 `all_cause`，否则会与 1.1.1 原有领域重复。
- `transform.shape`：
  - `loglinear`：log HR = ln(hr)/per × x；
  - `hinge`：`effect.<oc>` 另给 `hr_below`/`hr_above`（各自含 hr/lo/hi/per）与 `transform.knot_lo/knot_hi`；
  - `categorical`：`effect.<oc>.levels = {level: {hr, lo, hi}}`，参考组 hr=1；`reference.p = {level: prob}`；
  - `residualized`：输入已是"相对同龄人"的量（时钟加速、PRS z 值），`reference` 给 `mean`/`sd`；
  - `indicator`：0/1（如携带致病变异、已确诊），`reference.prevalence` 给人群携带率或患病率。
- `transform.log_x: true` 时先取自然对数再代入。
- `reference`：用来归一化，使同龄同性别人群平均风险倍数为 1。`normal` 给 `by_sex_age` 表；没有中国人群分布时可用研究人群分布并在 `source` 说明。
- `overlap.coef`：打折系数（0–1，只打折不放大）；`mediated_by`：`{编码或核心项 id: 比例}`，中介已测时系数乘 (1 − 比例之和)。
- `group`：`registry/groups.json` 里的重叠组；不属于任何组写 `null`。
- `adjusted_for` 用词：`age`、`sex`、核心项 id（`core.lipid`、`core.bp`、`core.adiposity`、`core.glucose`、`core.smoking`、`core.alcohol`、
  `core.crf`、`core.muscle`、`core.rhr`、`core.sleep`、`core.phenoage_clock`、`core.methylation`）、其他 ext 项 id，或标准编码。
- `effect.<oc>.applies_age = [lo, hi]`、`effect.<oc>.applies_sex = "M"|"F"`：硬性适用条件（例如 BMI→乳腺癌只用于 ≥50 岁女性，近似绝经后）；范围外该结局不计入。
  与之区别：`population.age_range` 是研究人群年龄，范围外只打 0.7 折。
- `group: "genetic"`：家族史、多基因评分、致病变异等先天项都归此组（规则 `cap_only`：不按排名剔除，只限制组内系数合计）。
- `behavior.target`：行为项的推荐目标值（指南值），用于"还能加分"的计算；写明 `behavior.target_source`。
- `behavior`（仅 behavior 项）：`{"min_weeks": 8, "self_report_discount": 0.5}`。
- `screening`（仅筛查行为项）：`{"disease_id": "crc", "mortality_rr": {"hr": 0.78, "lo": 0.7, "hi": 0.87}, "eligible": {"age": [50, 75], "sex": "both", "requires": []}, "interval_years": 1}`；
  其 `effect` 可为空，指数贡献 = ln(1 − 死因占比 × (1 − RR))，死因占比取 `outcomes/<disease>.json: mortality_share`。
- `disclosure`：`standard` 正常展示 · `counsel` 展示并提示遗传咨询 · `opt_in` 默认不展示（APOE ε4 纯合等）。
- 建项层补充字段（引擎可忽略不用的字段，但须兼容）：
  - `effect.<oc>.evidence` / `population` / `transport` / `coef`：该结局来自与顶层 `evidence` 不同的文献时，按结局覆盖顶层字段；`coef` 覆盖 `overlap.coef`。
  - `effect.<oc>.derived = {"from": {"hr","lo","hi"}, "pow": k}`：原文数字（被逐字核对）经 `hr = from.hr^k` 换算（k<0 时上下限互换），例如四分位比较折算为每 1000 步。
  - `overlap.overlaps_with`：与本项机制重叠的已计入项 id；代码按 §4.1 规则核对 `coef` 上限（全部已校正 ≤1，部分 ≤0.6，仅年龄性别 ≤0.3）。
  - `reference.kind` 另有：`lognormal`（`by_sex_age` 行给 `meanlog`/`sdlog`，配合 `log_x`）、`prevalence`（指示项）、`categorical_mid`（连续输入、人群按分档给 `p`，`reference.mids = {档: 代表值}`）；`reference.pmid`+`quote` 时代码核对原句。
  - `reference.log_norm = {oc: [{sex, age_lo, age_hi, value}]}`（可选，预先算好的 ln E_ref[exp f]）；人群中性检查会核对它与参考分布一致。
  - `population.sex_scope`：`M`/`F` 只适用于单一性别（乳腺癌、前列腺癌项自动按结局限定）。
  - 来源 `evidence.source = "pgs_perf:PPMxxxxxx"`：PGS Catalog 的表现记录（文本由代码按固定格式生成）。
  - 遗传项（`kind: genetic`）的研究设计另允许大型病例对照（胚系变异先于发病，无反向因果）。
- 自动入库标准（方案 A）：人体前瞻队列/荟萃/孟德尔随机化；结局事件 ≥100；HR 与 95% CI；数值与原文逐字核对通过；等级 ≥B；平台一致或有换算；参考分布可得；
  许可允许商业使用；方向与原文一致。任何一条不满足 → 写进 `registry/qualitative/`（字段相同，另加 `why_qualitative_zh`）。

## 4. 疾病定义（`registry/outcomes/<id>.json`）

```json
{
  "id": "t2d", "name_zh": "2 型糖尿病", "icd10": ["E11"], "sex": "both",
  "incidence": {"unit": "per_100k_py", "by_sex_age": [{"sex": "M", "age_lo": 30, "age_hi": 34, "rate": 0.0}],
                "source": "...", "year": 2018, "region": "China", "quality_zh": "..."},
  "mortality_share": {"by_sex_age": [{"sex": "M", "age_lo": 50, "age_hi": 54, "share": 0.0}], "source": "..."},
  "diagnosed_codes": ["ICD10:E11"],
  "horizon_lifetime_age": 90,
  "license": {"commercial_use": true, "note": "..."},
  "evidence": {"quote": "...", "url": "...", "verified_at": "..."}
}
```

- 已确诊判定：观测中出现 `diagnosed_codes` 任一 → 输出"已发生"，不给发病风险。
- `mortality_share` 只在有筛查项的病种需要（结直肠癌、肺癌、肝癌、胃癌、乳腺癌、宫颈癌可选）。

## 5. 来源记录（`registry/sources/<key>.json`）

`{"key": "pmid:12345678", "url": "...", "fetched_at": "...", "sha256": "...", "text": "抓取到的摘要或全文相关段落", "checks": [{"term": "ext.apob", "number": "1.10", "found": true, "context": "..."}]}`

核对由代码完成：`hr`、`lo`、`hi` 三个数字必须原样出现在 `text` 中，并与 `quote` 同段；`quote` 必须是 `text` 的子串（空白归一化后）。
`verify` 只把抓取结果写进建项层缓存（`skills/longpi-term-builder/.cache/`，不入版本库），不改动已冻结的项目库；`add` 时才把用到的来源连同核对记录写入 `registry/sources/` 并冻结。

## 6. 工具库（`skills/longpi-omics/tools/REGISTRY.json`）

`{"tools": [{"id": "prs_score", "version": "0.1.0", "inputs": ["vcf"], "outputs": ["PGS:*"], "license": "MIT", "deps": ["python>=3.9"],
"validation": {"dataset": "...", "metric": "...", "value": 0.0, "passed": true, "date": "..."}, "deterministic": true}]}`

入库门槛：用已知答案的公开样本复现原作者结果；同一输入两次运行逐位一致；许可允许；不联网发送个人数据。
