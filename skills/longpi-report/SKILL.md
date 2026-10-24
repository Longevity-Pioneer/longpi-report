---
name: longpi-report
description: >-
  Generate a LongPi personal longevity report (LongPi Age 死亡风险等效年龄, 120 指数, survival curves,
  disease-risk cards, intervention predictions, N-of-1 design) from a person's own data: checkup reports,
  wearable exports (Apple Health, Huawei, Garmin), CGM, home blood pressure, genetic and methylation reports.
  Use when someone asks for a LongPi report, 长寿报告, 生物年龄报告, LongPi Age, 120 指数, "我能活到多少岁",
  "我的身体比实际年龄老还是年轻", or wants their health data turned into this report. Every number comes from a
  calibrated, validated model (UN WPP 2024 China life tables, NHANES 1999-2018 mortality calibration,
  published meta-analyses); Claude writes only the narrative around the numbers.
---

# LongPi 报告

把一个人的体检、可穿戴、连续血糖、家庭血压、基因、甲基化等数据，变成一份和 LongPi Demo 同样结构的
网页报告：总览、数据、疾病风险、前沿生物分析、干预、方法六个页签。

**分工**：数字全部由脚本算（可复现、可检验）；Claude 负责读资料、整理输入、写叙述、向用户解释。
不要自己估算 LongPi Age、120 指数或干预效果，也不要改写脚本给出的数字。

只需要 Python 3.9+ 标准库。

- **脚本**在本 Skill 目录里，下面写作 `<SKILL>`。命令里要换成加载本 Skill 时显示的 Base directory 绝对路径（每次调用都写全，shell 变量不会保留）。
- **个人资料和产出**（体检文件、导出数据、person.json、results.json、narrative.json、report.html）放在单独的工作文件夹：
  用用户指定的位置；用户没指定时，在当前目录下新建 `longpi-<代号>/`。
- **不要**把任何个人资料放进 Skill 目录。那里是代码库，更新时会被覆盖，也可能被提交上传。
- 命令在工作文件夹里运行：

```bash
python3 <SKILL>/scripts/longpi_report.py check   person.json                 # 检查输入
python3 <SKILL>/scripts/longpi_report.py compute person.json -o results.json # 计算（约 30 秒；第一次读大的 Apple 导出另需几分钟）
python3 <SKILL>/scripts/longpi_report.py facts   results.json                # 写叙述用的事实表
python3 <SKILL>/scripts/longpi_report.py render  results.json narrative.json -o report.html
python3 <SKILL>/scripts/longpi_report.py demo    -o /tmp/longpi_demo         # 合成示例，端到端
```

## 工作流程

### 1. 收集资料
向用户要（有多少用多少，缺的报告里会说明影响）：
- 体检报告（PDF/照片均可，越多年越好）：血常规、生化、血脂、HbA1c、hs-CRP、尿酸、肝功能、血压、身高体重腰围、超声/心电图结论
- 可穿戴导出：Apple 健康"导出所有健康数据"的 `export.xml`；其他品牌导出的 CSV
- 连续血糖（CGM）导出 CSV、家庭血压记录、饮食或用餐时间记录
- 基因检测报告（药物基因组部分）、甲基化/生物年龄报告
- 问卷：性别、出生年月、城市/农村、南方/北方；吸烟（从不/已戒+戒烟年份/正在吸）；饮酒（每周大约喝什么、多少）；
  平时睡几个小时；已确诊疾病；在用药物；父母兄弟姐妹的重大疾病及发病年龄

不需要姓名、身份证号；用一个代号（如 U01）即可。

### 2. 整理成 person.json
格式见 `references/input_schema.md`，示例见 `examples/demo_person.json`。要点：
- 化验值**照报告原样**填数值和单位，脚本会统一换算；不要自己换算、不要四舍五入、不要补没有的值。
- 一次体检一个 `labs` 条目；血压放 `vitals`（体检测的 `setting: "office"`）。
- 可穿戴/CGM/血压文件放在 person.json 旁边，用相对路径写进 `wearables`；写清 `device`（如 "Apple Watch"），
  不同品牌的 VO2max 偏差不同，脚本按品牌校正。
- Apple 健康导出：
  - 导出的是 zip，解压到工作文件夹，数据在 `apple_health_export/` 下的 xml 文件里（文件名随手机语言可能不同，以解压出来的为准；用主文件，不用带 `_cda` 的）。
  - 这个文件常有几百 MB 到几 GB。**不要用读文件工具打开或整个打印**，只把相对路径写进 `apple_health_xml`，由脚本流式读取。
  - 第一次读要几分钟，之后用旁边自动生成的 `.longpi-cache.json`，导出文件不变时只需几秒。
- CGM、家庭血压的时间如果写成 `24-10-2026` 或 `10/24/2026`，脚本会按整列判断日月顺序；判断不了时会报错，按提示改成 `YYYY-MM-DD HH:MM`。
- 甲基化报告：
  - **计入 LongPi Age 的只有 GrimAge2 / GrimAge**。报告里写明是 GrimAge2 或 GrimAge 并给出数值时，`clock_type` 写 `GrimAge2` / `GrimAge`，`bio_age` 填数值，`chrono_age` 填采样时年龄。
  - 其他情况照实写：以日历年龄为训练目标的写 `first_generation`；明确是 DunedinPACE、DNAm PhenoAge 的写对应名称；不清楚的写 `unknown`。这些只在前沿页展示，不计入。
  - 不计入的依据：在美国国家健康调查的随访里，它们在 LongPi 之外几乎分辨不出额外的风险。
- 拿不准的条目先问用户，不要猜。
- `check` 提示某次血检处于急性炎症或红细胞异常时，问用户当时是否生病、贫血；属暂时状态的，在那次 `labs` 写 `clock_exclude`（见 `references/input_schema.md`），再重新计算。

### 3. 检查
`check` 会报单位错误、超出常见范围的数（多半是单位填错）、缺失的关键项。缺项不影响出报告：
没测的项目按同龄人的分布计入，只让区间变宽。补哪一项能让区间缩多少，`compute` 后的补测清单里有数字。

### 4. 计算
`compute` 输出 results.json；`facts` 打印事实表——写叙述时引用的所有数字都从这里抄。

### 5. 写 narrative.json
按 `references/narrative_guide.md` 写：一句话总结、临床待办、风险卡（规则见 `references/risk_rules.md`）、
药物基因组卡（`references/pgx_rules.md`）、前沿分析卡、数据质量与缺口、数据说明、N-of-1 实验设计。
- 用户要运动方案时写 `training`，动作优先用内置动作库引用（`{"ref": "goblet_squat"}`，图文自动带出，见 `references/narrative_guide.md`）。
- 脚本会生成默认的待补充资料清单（`asks_default`）；需要按人调整时写 `asks`（总览页“待补充资料”）：主动提醒拍体型和面部照片、量腰围、测握力、家庭血压、饮食照片、复查抽血等，写清怎么做；交付时也在对话里提一句。
- 风险卡只写资料里有依据的内容，等级用"关注 / 留意 / 一般"，依据写到具体指南。
- 前沿卡只描述 results.json 里真实存在的数据和统计，不编造相关性。
- 数字和事实表保持一致；`render` 会自动检查 LongPi Age 是否一致、是否出现后台术语。

### 6. 渲染并交付
`render` 生成单个 HTML 文件（离线可打开，支持深浅色，`#tab-data`、`#tab-iv` 等锚点可直接跳到页签）。
交付时用 3–5 句话讲清楚：
- LongPi Age 是多少；
- 主要加分和扣分项；
- 最值得做的三件事；
- 数据完整度，以及最值得补的 1–2 项（同等收益先提免费或便宜的）；
- 多久后复测。

### 7. 解释
用户追问时按 `references/explain.md`：用日常的话讲，先结论后原因。

## 必须遵守

- **说法**：LongPi Age 是"死亡风险相当于几岁"，不是"还能活多久"，也不是诊断。报告里的模型估计统一称"AI 预测"，不叠加免责声明。
- **正向反馈要有依据**：变化超过测量波动（报告里有给出）就明确说"年轻了"；还在波动内就讲具体进步和复测时间，不说"无法判断"。
- **补测建议正向、如实**：
  - 先肯定已经提供的资料让区间缩小了多少，再说下一项能再缩多少。
  - 数字只用事实表"让结果更准"里的。不夸大，也不推荐清单以外的高价检测来"提高准确度"。
  - 不改变 LongPi Age 的检测（CGM、基因、影像）讲清楚它们别的用处。
- **建议要具体**（分四级）：非处方补充剂给常用量、上限、试验剂量和禁忌；需要先诊断的（铁剂、甲状腺素等）说清查什么、看哪个科；
  处方药只讲证据和医生会考虑什么，不给个人剂量，不建议自行开始、停止或换药；急症先讲急救和去哪里。
- **面向用户的文字**不出现后台术语（脚本名、参数文件、Monte Carlo、MCP 等），用通顺自然的中文。
- **隐私**：不把姓名、身份证号、电话写进 person.json 或报告；工作文件夹不放进 Skill 目录或任何代码库；演示数据设 `"synthetic": true`。
- 年龄在 30–85 岁之外、孕期、正在急性病或住院时，结果只作参考，要明确告诉用户。

## 模型一览（详见 `references/methods_summary.md`；完整论证在项目仓库的 `docs/方法学白皮书.md`）

- **LongPi Age** = 年龄 + ln E[R] / b。b 是联合国 WPP 2024 中国生命表的 Gompertz 斜率（男约 0.0985/年）；
  R 是相对同龄同性别中国人的死亡风险倍数，由血液时钟层（PhenoAge 差值，NHANES 分段校准）和 10 个功能领域
  （心肺、握力、静息心率、睡眠、血压、LDL、血糖、BMI、吸烟、饮酒）的荟萃分析剂量反应合成。
- **校准与验证**：NHANES 1999–2018（50,819 人，8,279 例死亡）时间外推验证，LongPi 1 岁 ≈ 1 岁真实年龄的风险
  （按美国吸烟危害计斜率比 1.03），C 指数 0.835 → 0.863。
- **120 指数** = 100 + 10·log10(P本人(120)/P同龄人(120))，三种情景（死亡率冻结 / WPP 中位预测 / 延缓衰老），
  个体生存用 Gamma 脆弱性模型（极高龄风险向人群收敛，平台 0.70/年来自超百岁老人数据）。
- **甲基化**：只计入 GrimAge2 / GrimAge。用 NHANES 1999–2002 甲基化数据（2,307 名 50 岁以上成人，随访约 17 年）估计它们在
  LongPi 之外的增量，再按实验室间可能的系统差异打折。
- **区间与数据完整度**：没测的项目（包括没有血液检测、没有 GrimAge2）按同龄人分布计入，只加宽区间。
  补测清单逐项算"做了以后区间缩多少"；数据完整度 =（只知道年龄性别时的区间 − 现在的区间）÷（只知道年龄性别时的区间 − 全部做完的区间）。
- **干预**：随机对照试验的指标变化 × 依从性，放进同一模型；D 级证据不给数值。
