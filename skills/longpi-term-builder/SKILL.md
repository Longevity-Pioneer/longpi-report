---
name: longpi-term-builder
description: LongPi 建项层。观测里出现项目库没有的指标（或平台/单位/人群不匹配）时，联网检索该指标与全因死亡或疾病发病的证据，写出项规格，由代码逐字核对数字与原文，通过入库标准的计入数值，未通过的写成定性佐证；入库前做人群中性检查并冻结新版本。Use when a LongPi observation code has no registry term, or to add/verify/audit registry terms (ext.*).
---

# LongPi 建项层

接口以 `../longpi-report/references/registry_contract.md` 为准（§1 编码、§3 项规格、§5 来源）。本技能只做"证据 → 项规格 → 核对 → 入库"，不出报告。

**所有命令在本技能目录（`skills/longpi-term-builder/`）下运行**；规格文件可以放在任意位置，用路径传入。

## 铁律

1. **数字不凭记忆写。** 每个 HR、CI、事件数都必须来自本次抓取到的原文，并能被 `verify` 在 `quote` 里逐字找到。记得的数字只能当检索线索。
2. **不自造换算。** 原文只给分类比较（如分组 HR）时，用 `categorical` 形状，或用原文自己的每单位估计、趋势检验估计；**不得自行设定间距把分组结果折成斜率**。允许的换算只有原文已给出依据的：原文写"每降低 1 单位"→ `pow: −1`；原文以 MET 为单位 → 每 3.5 mL/kg/min 为 1 MET；原文给出 SD 数值 → `per` 写该 SD。
3. **个人数据不出本机。** 检索与抓取只发送通用信息：指标名、标准编码、PMID、DOI、PGS 编号。不发送任何人的数值、姓名、病历内容。`term_builder.py` 的网络函数只放行白名单主机和标准标识符。
4. **宁缺毋滥。** 证据达不到门槛就写成定性条目，不为了"有数"放宽规则或抬高系数。

## 流程

输入：一个标准编码（`LOINC:`、`ICD10:`、`UNIPROT:`、`HMDB:`、`NCBITAXON:`、`HGNC:`、`PGS:`、`LP:`）、平台，以及目标结局（`all_cause` 或 `registry/outcomes/` 的疾病 id）。

1. **查重。** `python3 scripts/term_builder.py list` 与 `list --qualitative`。同一编码（同平台）已有条目时，在该条上补结局，不建第二条。`LP:` 编码不在 `../longpi-report/data/observation_codes.json` 的 `lp_codes` 里时，先写进去。
2. **联网检索，并显式排序候选来源。** 用网页搜索、PubMed E-utilities、Europe PMC。先列出全部候选，再按下列顺序选一项，其余写进 `evidence.alternatives_considered`（每条：PMID、估计值、未选原因）：
   1. 东亚（中国优先）的大型前瞻队列合并分析或孟德尔随机化，人群与参考分布一致；
   2. 国际个体数据合并分析、荟萃分析（含东亚人群者优先）；
   3. 单一大型前瞻队列（全因死亡须 ≥1000 例死亡）；
   4. 其余（病例对照只用于遗传项）只作佐证。
   - **混杂与反向因果强的暴露**（饮酒、体重指数、高龄者的 LDL、吸烟以外的生活方式）：优先孟德尔随机化或随机对照试验的因果估计，在 `evidence.estimand_zh` 写明估计的是什么（"遗传预测的长期平均饮酒量每增加 x"还是"现饮酒者对比从不饮酒者的观察性 HR"）。
   - 互相校正过的 HR 优先（研究校正了与本项重叠的已计入项）。
   - 抓取原文（摘要，开放获取时含全文），从原文复制 `quote`；`quote` 必须写出该结局（死亡、具体疾病名）。
3. **写项规格**（§3 格式），要点：
   - `effect` 的键只写结局。**进 LongPi Age 的项必须含 `all_cause`；只为疾病建的项不写 `all_cause`**。
   - **与 1.1.1 核心项同一指标的项**（例如血压、LDL、吸烟、饮酒、BMI）：不重建全因死亡，只为疾病建项；若确需全因死亡，`overlaps_with` 必须如实列出该核心项，系数因此被规则压到 ≤0.3，这是预期结果。
   - 多个结局来自不同文献时，每个结局各写 `effect.<oc>.evidence = {pmid, quote, grade, design}`，以及需要时的 `population`、`transport`、`coef`、`adjusted_for`、`overlaps_with`。
   - 只适用于部分人群的估计（如绝经后、仅男性）：在该结局写 `applies_age` / `applies_sex`（硬性条件）。
   - 原文数值按铁律 2 换算时写 `derived: {"from": {"hr","lo","hi"}, "pow": k}`：`from` 是原文数字（被逐字核对），代码检查 `hr = from.hr^k`（k<0 时上下限互换）。
   - `per` 写成原文的单位间隔（每 1 SD 时 `per` 就写该研究的 SD 数值并在 `per_unit` 注明）。`log_x: true` 时 `per` 用自然对数单位（每翻倍 = 0.6931）。
   - `adjusted_for`：原文模型校正了什么就写什么（用约定词：`age`、`sex`、`core.*`、`ext.*` 或标准编码）。
   - `population.events` 必填（≥100）；只在全文表格里的写 `events_source_zh`。
   - `overlap`（代码对每个结局检查上限；全因死亡对照 `overlap.overlaps_with` 中的核心项，疾病结局对照 `effect.<oc>.overlaps_with` 中同病种已计入的项，无重叠写 `[]`）：

     | 研究校正情况（相对重叠项） | 系数 |
     |---|---|
     | 全部校正 | 0.8（SD 0.2），不超过 1 |
     | 部分校正，或校正了其他混杂 | ≤0.6，写明理由 |
     | 只校正年龄、性别 | ≤0.3，或直接定性 |

     1.1.1 已计入项：10 个领域（`core.crf`、`core.muscle`、`core.rhr`、`core.sleep`、`core.bp`、`core.lipid`、`core.glucose`、`core.adiposity`、`core.smoking`、`core.alcohol`）、`core.phenoage_clock`（已含白蛋白、肌酐、血糖、CRP、淋巴细胞百分比、MCV、RDW、ALP、白细胞）、`core.methylation`（GrimAge2）。
     `mediated_by` 写中介比例（例：步数 `{"core.crf": 0.3}`；PRS `{"LOINC:1558-6": 0.5}`，无文献时默认 0.5 并注明）。
   - `group`：家族史、多基因评分、致病变异、APOE 一律 `genetic`。
   - `transport`：研究人群非东亚时 `shrink` ≤0.8、`sd_inflate` ≥1.25。
   - `reference`：用来归一化（同龄同性别平均倍数为 1）。优先分性别、分年龄的中国人群分布，写 `pmid`+`quote`（代码会核对原句）；`from_norms: "<marker>"` 直接引用 `data/population_norms_china.json`。HR 分性别给出时，参考分布也要分性别。确实找不到可核对来源时写 `estimated: true` 与 `estimated_reason_zh`（报告会标明）。分布偏态用 `lognormal`（`meanlog`/`sdlog`）配合 `log_x`；分类用 `p`；0/1 用 `prevalence`；分档的连续值用 `categorical_mid`（`p` + `mids`）。
   - 形状：`loglinear`、`hinge`（`hr_below`/`hr_above` + `knot_lo`/`knot_hi`）、`categorical`（`levels`，参考组 hr=1）、`residualized`（时钟加速、PRS z 值）、`indicator`（携带/确诊）。分类项中 CI 含 1 的水平改写为 `{"hr": 1}`（不计风险）或整项不入库。
   - 行为项写 `behavior`（含 `target` 指南推荐值与 `target_source`）；筛查项写 `screening`（`mortality_rr` 也被逐字核对；只用随机对照试验意向筛查的该病死亡 RR，CI 不含 1、该病死亡 ≥100 例）。遗传项 `disclosure`：单基因写 `counsel`，APOE ε4 写 `opt_in`。
   - `license.commercial_use` 必填；PGS 评分的许可由代码从 PGS Catalog 读取，非商业许可的不入库。
4. **核对。** `python3 scripts/term_builder.py verify spec.json`，输出：
   - `auto_accept`：全部门槛通过；
   - `qualitative`：列出未达标原因；
   - `invalid`：编码查不到、重复、许可不允许——不能入库，先修正。
   核对失败时回到原文改 `quote` 或换来源；**不得为了通过而改动原文数字**。
5. **入库。** `python3 scripts/term_builder.py add spec.json [...]`（定性：`add --qualitative --why "原因"`；替换已有条目加 `--replace`）。`add` 会：再核对一遍、写入 `registry/terms/` 或 `registry/qualitative/`、把核对记录写进 `registry/sources/`、按 `YYYY.MM.DD-N` 升版本、做人群中性检查（不通过不冻结）、冻结 `MANIFEST.json`。
6. **自查。** `python3 scripts/term_builder.py check-population`；`show <id>` 看入库结果；`build-log` 重新生成 `BUILD_LOG.md` 的逐项明细，汇总与决定部分手写。

联网失败时：PubMed 不通会自动改由 Europe PMC 取同一摘要；字典或原文仍取不到时 `add` 拒绝写入并提示重试，不会把项悄悄降为定性。

## 入库标准（方案 A，代码检查）

- 设计：人体前瞻队列 / 荟萃 / 孟德尔随机化（遗传项另允许大型病例对照；回顾性队列不入库）；**全因死亡项须为合并分析、孟德尔随机化，或单一队列死亡 ≥1000 例**。
- 事件：结局事件 ≥100 且写明（`n` ≥1 万的合并分析可豁免）。
- 数字：HR 与 95% CI 逐字、成组出现在 `quote`，`quote` 是原文子串（空白归一化后）且写出该结局；主估计与每个计入的分类水平 95% CI 不含 1；换算只按铁律 2。
- 其他：等级 ≥B；方向与 HR 一致；参考分布覆盖所有适用的性别 × 年龄段且有出处（或明示估计）；许可允许商业使用；每个结局的重叠系数不超过规则上限；非东亚人群已收缩；行为项有目标值；遗传项归 `genetic` 组。

## 命令（在 `skills/longpi-term-builder/` 下运行）

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

归一化与引擎一致：先乘系数再归一化，`l = c·f(x) − ln E_ref[exp(c·f(X))]`（各形状的 f 见脚本文件头）。`check-population` 逐段与引擎的 `lp.terms.log_mean_exp_ref` 比对。

## 在项目库副本上试建

正式项目库在 `longpi-report/registry/`。想先在副本上试（不影响正式库）：

```bash
cp -R <skills>/longpi-report/registry /tmp/reg-copy
export LONGPI_REGISTRY_DIR=/tmp/reg-copy      # verify / add / compute 都读写这个目录
# ……建项、重新 compute……
unset LONGPI_REGISTRY_DIR
```

用副本算出的事实表会提示"不是技能自带的项目库"，不能作为正式报告。

> **来源排序（补充）**：中国人群的暴露或状态，先查超大前瞻队列与合并分析——中国慢性病前瞻性研究（CKB，约 50 万人）、China-PAR、亚洲队列联盟（ACC）、日本与韩国全国队列；
> 同一估计目标下，优先结局事件（死亡）最多的来源。两个都合格时取事件多的那个，另一个写进 `alternatives_considered`。

## 计入数值须两次独立建项一致（2026-11-20 起）

单次建项对"选哪个合格来源"不稳定（盲测三轮 6/11、7/11、6/11），所以：

1. 同一个项由两个**互不知情**的建项者各建一份规格（不同会话或不同子代理，彼此看不到对方的检索与规格），文件分别为 `A.json`、`B.json`，`id` 与 `input.code` 相同。
2. 运行 `python3 scripts/term_builder.py add-consensus A.json B.json`：
   - 两份都须 `verify` 通过；
   - 每个结局、每个效应分量（斜率、折线两侧、各分组、携带效应、筛查死亡 RR）两份都要给出，且点估计互在对方 95% 置信区间内（换算到同一单位增量）；
   - 一致的结局计入（取结局事件更多的一份，另一份记为 `evidence.replication`）；不一致的结局不计入；
   - 一个结局都不一致时，该项写成定性佐证，两份规格存到 `registry/candidates/<id>.json` 等团队审核。
3. `add` 只用于 `--qualitative`；直接 `add` 计入数值会被拒绝。
