---
name: longpi-term-builder
description: LongPi 建项层。观测里出现项目库没有的指标（或平台/单位/人群不匹配）时，联网检索该指标与全因死亡或疾病发病的证据，写出项规格，由代码逐字核对数字与原文，通过入库标准的计入数值，未通过的写成定性佐证；入库前做人群中性检查并冻结新版本。Use when a LongPi observation code has no registry term, or to add/verify/audit registry terms (ext.*).
---

# LongPi 建项层

接口以 `../longpi-report/references/registry_contract.md` 为准（§1 编码、§3 项规格、§5 来源）。本技能只做"证据 → 项规格 → 核对 → 入库"，不出报告。

## 铁律

1. **数字不凭记忆写。** 每个 HR、CI、事件数都必须来自本次抓取到的原文，并能被 `verify` 在 `quote` 里逐字找到。记得的数字只能当检索线索。
2. **个人数据不出本机。** 检索与抓取只发送通用信息：指标名、标准编码、PMID、DOI、PGS 编号。不发送任何人的数值、姓名、病历内容。`term_builder.py` 的网络函数只放行白名单主机和标准标识符。
3. **宁缺毋滥。** 证据达不到门槛就写成定性条目，不为了"有数"放宽规则或抬高系数。

## 流程

输入：一个标准编码（`LOINC:`、`ICD10:`、`UNIPROT:`、`HMDB:`、`NCBITAXON:`、`HGNC:`、`PGS:`、`LP:`）、平台，以及目标结局（`all_cause` 或 `registry/outcomes/` 的疾病 id）。

1. **查重。** `python3 scripts/term_builder.py list` 与 `list --qualitative`。同一编码（同平台）已有条目时，在该条上补结局，不建第二条。`LP:` 编码不在 `../longpi-report/data/observation_codes.json` 的 `lp_codes` 里时，先写进去。
2. **联网检索。** 用网页搜索、PubMed E-utilities、Europe PMC。优先级：
   - 荟萃分析、大型前瞻队列（结局事件 ≥100）、孟德尔随机化；随机对照试验用于筛查和行为项；
   - **东亚队列优先**：中国慢性病前瞻性研究（CKB）、中国其他大型队列、日本（JPHC、JACC）、韩国（NHIS）队列；
   - 互相校正过的 HR 优先（研究校正了与本项重叠的已计入项）；
   - 抓取原文（摘要，开放获取时含全文），从原文复制 `quote`。
3. **写项规格**（§3 格式），要点：
   - `effect` 的键只写结局。**进 LongPi Age 的项必须含 `all_cause`；只为疾病建的项不写 `all_cause`**。
   - 多个结局来自不同文献时，每个结局各写 `effect.<oc>.evidence = {pmid, quote, grade, design}`，以及需要时的 `population`、`transport`、`coef`。
   - 原文数值需要换算（例如原文是"每降低 1 SD"或分位组比较）时，写 `derived: {"from": {"hr","lo","hi"}, "pow": k}`：`from` 是原文数字（被逐字核对），代码检查 `hr = from.hr^k`（k<0 时上下限互换）。
   - `per` 写成原文的单位间隔（每 1 SD 时 `per` 就写该研究的 SD 数值并在 `per_unit` 注明）。`log_x: true` 时 `per` 用自然对数单位（每翻倍 = 0.6931）。
   - `adjusted_for`：原文模型校正了什么就写什么（用约定词：`age`、`sex`、`core.*`、`ext.*` 或标准编码）。
   - `overlap`（代码按下表检查上限）：

     | 研究校正情况（相对 `overlap.overlaps_with` 列出的已计入项） | `overlap.coef` |
     |---|---|
     | 全部校正 | 0.8（SD 0.2），不超过 1 |
     | 部分校正 | 0.4–0.6，写明理由 |
     | 只校正年龄、性别 | ≤0.3，或直接定性 |

     1.1.1 已计入项：10 个领域（`core.crf`、`core.muscle`、`core.rhr`、`core.sleep`、`core.bp`、`core.lipid`、`core.glucose`、`core.adiposity`、`core.smoking`、`core.alcohol`）、`core.phenoage_clock`（已含白蛋白、肌酐、血糖、CRP、淋巴细胞百分比、MCV、RDW、ALP、白细胞）、`core.methylation`（GrimAge2）。
     `mediated_by` 写中介比例（例：步数 `{"core.crf": 0.3}`；PRS `{"LOINC:1558-6": 0.5}`，无文献时默认 0.5 并注明）。
   - `transport`：研究人群非东亚时 `shrink` ≤0.8、`sd_inflate` ≥1.25。
   - `reference`：用来归一化（同龄同性别平均倍数为 1）。优先中国人群分布；`from_norms: "<marker>"` 直接引用 `data/population_norms_china.json`；有文献时写 `pmid`+`quote`（代码会核对原句）。分布偏态用 `lognormal`（`meanlog`/`sdlog`）配合 `log_x`；分类用 `p`；0/1 用 `prevalence`；分档的连续值用 `categorical_mid`（`p` + `mids`）。
   - 形状：`loglinear`、`hinge`（`hr_below`/`hr_above` + `knot_lo`/`knot_hi`）、`categorical`（`levels`，参考组 hr=1）、`residualized`（时钟加速、PRS z 值）、`indicator`（携带/确诊）。
   - 行为项写 `behavior`；筛查项写 `screening`（`mortality_rr` 也被逐字核对）。遗传项 `disclosure`：单基因写 `counsel`，APOE ε4 写 `opt_in`。
   - `license.commercial_use` 必填；PGS 评分的许可由代码从 PGS Catalog 读取，非商业许可的不入库。
4. **核对。** `python3 scripts/term_builder.py verify spec.json`，输出：
   - `auto_accept`：全部门槛通过；
   - `qualitative`：列出未达标原因（例如数字不在原句、事件 <100、等级 <B、校正不足而系数超限、参考分布缺失）；
   - `invalid`：编码查不到、重复、许可不允许——不能入库，先修正。
   核对失败时回到原文改 `quote` 或数字；**不得为了通过而改动原文数字**。
5. **入库。** `python3 scripts/term_builder.py add spec.json [...]`（定性：`add --qualitative --why "原因"`）。`add` 会：再核对一遍、写入 `registry/terms/` 或 `registry/qualitative/`、把核对记录写进 `registry/sources/`、按 `YYYY.MM.DD-N` 升版本、做人群中性检查（不通过不冻结）、冻结 `MANIFEST.json`。
6. **自查。** `python3 scripts/term_builder.py check-population`；`show <id>` 看入库结果；`build-log` 重新生成 `BUILD_LOG.md` 的逐项明细（编码、结局、HR（CI）、来源、等级、结论、系数、理由），汇总与决定部分手写。

联网失败（字典或原文抓取超时）时 `add` 拒绝写入并提示重试，不会把项悄悄降为定性。

## 入库标准（方案 A，代码检查）

人体前瞻队列 / 荟萃 / 孟德尔随机化（遗传项另允许大型病例对照）；事件 ≥100（写了就查）；HR 与 95% CI 逐字、成组出现在原句；主估计的 95% CI 不含 1；`quote` 是原文子串（空白归一化后）；等级 ≥B；方向与 HR 一致；参考分布覆盖所有性别 × 年龄段；许可允许商业使用；重叠系数不超过规则上限；非东亚人群已收缩。

## 命令

```
python3 scripts/term_builder.py verify  spec.json [--offline] [--refresh] [--json]
python3 scripts/term_builder.py add     spec.json [...] [--qualitative --why "..."] [--replace]
python3 scripts/term_builder.py check-population [--n 20000]
python3 scripts/term_builder.py list [--qualitative]
python3 scripts/term_builder.py show <id>
python3 scripts/term_builder.py build-log [--out BUILD_LOG.md]
python3 tests/blind/score_blind.py --all <产出目录>   # 建项能力盲测：11 个核心项（由另一模型执行）
python3 -m unittest discover -s tests     # 离线，用录制的响应
```

归一化与引擎一致：`l = f(x) − ln E_ref[exp f(X)]`（各形状的 f 见脚本文件头）。引擎若提供 `lp.terms.log_mean_exp_ref(term, outcome, sex, age)`，`check-population` 会逐段比对两边结果。
