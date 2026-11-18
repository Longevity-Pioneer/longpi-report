# person.json 输入格式

一个人一个文件。示例：`examples/demo_person.json`（合成数据）。字段可以缺，缺的部分报告里会说明影响。

```jsonc
{
  "schema": "longpi.person/1",
  "synthetic": false,                 // 演示/虚构数据设 true，报告会加演示横幅
  "as_of": "2026-10-20",              // 数据截至日期；LongPi Age 按这一天计算
  "person": {
    "code": "U01",                    // 代号，不写真名
    "label": "U01",                   // 报告页眉显示的名字（可写昵称）
    "sex": "M",                       // M / F
    "birth": "1988-10",               // 出生年月；或直接写 "age": 38.0
    "region": {"north": false, "urban": true}   // 秦岭—淮河以北为 north；城镇为 urban（影响吸烟 RR 与 China-PAR）
  },
  "labs": [ { "date": "2026-05-18", "source": "年度体检", "items": { "albumin": [47.0, "g/L"], ... } } ],
  "vitals": [ { "date": "2026-05-18", "sbp": 133, "dbp": 84, "pulse": 70, "setting": "office" } ],
  "anthropometrics": [ { "date": "2026-05-18", "height_cm": 175, "weight_kg": 76.0, "waist_cm": 92 } ],
  "fitness": [ { "date": "2026-09-01", "vo2max": 41.5, "method": "cpet" }, { "date": "2026-09-01", "grip_kg": 44 } ],
  "lifestyle": {
    "smoking": { "status": "former", "quit_year": 2019 },    // never / former（写 quit_year）/ current
    "alcohol": { "grams_per_week": 50 },                     // 纯酒精克数，换算见下
    "sleep_h": 7.0,                                          // 问卷口径"平时一晚睡几个小时"
    "mvpa_min_week": { "value": 150, "since": "2026-06" },   // 每周中高强度运动分钟（自述，写开始时间）
    "resistance_sessions_week": { "value": 2, "since": "2026-06" }
  },
  "conditions": [ { "name": "高血压", "icd10": "I10", "diagnosed": "2024", "treated": true } ],   // icd10 必填（疾病风险据此判定"已发生"）
  "medications": [ { "name": "氨氯地平", "dose": "5 mg qd", "since": "2024-06", "class": "antihypertensive" } ],   // class + since：判断哪些化验在用药期间
  "family_history": [ { "relation": "father", "condition": "高血压", "disease_id": "htn", "age_at_dx": 52 } ],   // disease_id 见 registry/outcomes
  "imaging": [ { "date": "2026-05-18", "type": "冠脉 CT", "finding": "……", "measures": { "cac_agatston": 0 } } ],   // measures 的键见 observation_codes.json 的 LP: 编码
  "screenings": [ { "test": "crc_fit", "date": "2026-03", "result": "阴性", "report": true } ],   // 按指南完成的筛查，进入 120 指数
  "observations_file": "observations.json",   // 组学层或读入层产出的标准观测（可选）
  "genetic_preferences": { "show_opt_in": false, "secondary_findings": false },   // 遗传结果告知选择，默认都不展示
  "other_tests": [ { "date": "2026-05-18", "name": "尿微量白蛋白/肌酐比", "value": "8 mg/g" } ],
  "genetics": { "date": "2025-02-10", "source": "消费级芯片", "pgx": [ { "gene": "CYP2C19", "result": "*1/*2", "phenotype": "中间代谢型" } ] },
  "methylation": [ { "date": "2026-05-18", "vendor": "某厂商", "clock_type": "first_generation", "bio_age": 36.2, "chrono_age": 37.6,
                     "organs": { "肾": 33.9, "肝": 39.6 } } ],
  "wearables": { "device": "Apple Watch", "apple_health_xml": "apple_health_export/export.xml",
                 "daily_csv": "daily.csv", "cgm_csv": "cgm.csv", "bp_csv": "bp.csv" },
  "meals": [ { "time": "2026-10-01 12:20", "label": "午餐" } ]
}
```

## 化验项目（`labs[].items` 的键）

每项写 `[数值, "单位"]`，**照报告原样**。脚本认识的单位会自动换算（如 mg/dL ↔ mmol/L、g/dL ↔ g/L、IFCC mmol/mol ↔ NGSP %）。

| 键 | 中文报告常见名称 | 说明 |
|---|---|---|
| albumin | 白蛋白 ALB | g/L |
| creatinine | 肌酐 Cr / CREA | μmol/L |
| glucose | 葡萄糖 GLU | 生化里的血糖；体检空腹抽血时与空腹血糖同值，两个键都填 |
| glucose_fasting | 空腹血糖 FPG | 用于糖代谢分级 |
| crp | **超敏** C 反应蛋白 hs-CRP | mg/L。普通 CRP 只报"<5"时不要填（检测下限太高），脚本会按人群中位数补入并加宽区间 |
| lymph_pct | 淋巴细胞百分比 LYM% | % |
| mcv | 平均红细胞体积 MCV | fL |
| rdw | 红细胞分布宽度 **RDW-CV** | %。不要填 RDW-SD（单位 fL） |
| alp | 碱性磷酸酶 ALP | U/L |
| wbc | 白细胞计数 WBC | 10^9/L |
| ldl / hdl / tc / tg | 低/高密度脂蛋白胆固醇、总胆固醇、甘油三酯 | mmol/L |
| apob、lpa | 载脂蛋白 B、脂蛋白(a) | g/L；Lp(a) 注明 mg/L 或 nmol/L |
| hba1c | 糖化血红蛋白 | % |
| alt / ast / ggt | 谷丙/谷草转氨酶、γ-谷氨酰转移酶 | U/L |
| uric_acid | 尿酸 UA | μmol/L |
| vitd | 25-羟维生素 D | ng/mL（nmol/L 会自动换算） |
| platelets | 血小板 PLT | 10^9/L |

PhenoAge 需要同一次抽血的前 9 项（albumin 到 wbc）。少 hs-CRP 仍可计算（误差更大）；少其他项则这次不算 PhenoAge。

## 血压、体格、体能

- `vitals`：体检/诊室测量 `setting: "office"`；单次家庭测量也可以写 `"home"`，但更推荐把家庭血压整理成 `bp_csv`。
- 家庭血压 CSV：`datetime,sbp,dbp,pulse`，如 `2026-10-01 07:12,132,84,66`。脚本取最近 4 周、去掉第一天，按 2024 中国高血压指南换算为诊室口径。
- 握力 `grip_kg`：优势手最好成绩（kg）。体检中心、社区体测、家用握力计都可以。
- VO2max：实验室心肺运动试验写 `method: "cpet"`；手表估算不必单独写，脚本从可穿戴数据里取近 90 天中位数。

## 生活方式

- 吸烟：`never`、`former`（务必写 `quit_year`，戒烟不满 5 年风险更高）、`current`。
- 饮酒按纯酒精克数/周：啤酒 500 mL（4%）≈ 16 g；葡萄酒 150 mL（12%）≈ 14 g；白酒 50 mL（52%）≈ 21 g；黄酒 250 mL（15%）≈ 30 g。
- 睡眠：问卷口径的"平时一晚睡几个小时"。有手表时脚本优先用手表并换算口径（手表测的是实际睡着的时间，问卷普遍多报）。

## 可穿戴与 CGM

- **Apple 健康**：健康 App →头像→"导出所有健康数据"，解压到工作文件夹，把 `apple_health_export/` 下主 xml 文件（英文系统叫 `export.xml`，文件名随手机语言可能不同）的相对路径写进 `apple_health_xml`。几个 GB 也可以：脚本流式读取，不要用读文件工具打开它；第一次读要几分钟，之后用旁边的 `.longpi-cache.json` 缓存。
- **其他品牌**（华为运动健康、小米/Zepp、佳明、高驰等）：先导出，再整理成通用每日 CSV（可以让 Claude 写一个一次性转换脚本）：

  ```csv
  date,metric,value,source
  2026-10-01,steps,8123,Huawei
  2026-10-01,sleep_h,6.9,Huawei
  2026-10-01,rhr,63,Huawei
  2026-10-01,hrv,38.5,Huawei
  2026-10-01,vo2max,41,Huawei
  ```
  `metric` 可选：steps、sleep_h（实际睡着的小时数）、rhr、hrv、vo2max、weight、body_fat、walking_speed（m/s）。
- `device` 写品牌型号（"Apple Watch"、"华为 Watch GT"、"Garmin"……），决定 VO2max 的校正方式。
- **CGM**：硅基动感、雅培瞬感（LibreView）、Dexcom 等导出的 CSV 都可以，只要有时间列和血糖列（mmol/L 或 mg/dL 自动识别）。
  有用餐时间就写进 `meals`，报告会算每餐的血糖峰值。

## 异常期的血液检查

血液年龄（PhenoAge）会被急性感染和红细胞异常带偏。脚本自动标记：hs-CRP > 10 mg/L（急性炎症），MCV 不在 82–100 fL 或 RDW > 15.5%（缺铁、贫血恢复期、地中海贫血等）。`check` 会提示，报告首页会同时给出"按异常期处理后"的结果，主结果不变。

问清用户当时的情况后，在那一次 `labs` 里写：
- `"clock_exclude": true`：整次不用于血液年龄（例如急性感染期），可加 `"clock_exclude_reason": "感冒发热期"`；
- `"clock_exclude": ["mcv", "rdw"]`：只去掉这几项，用典型值代替并相应加大误差（例如贫血恢复期）。地中海贫血等长期状态不要排除。

## 甲基化

- 每份报告一条：`date`（采样日期）、`vendor`、`clock_type`、`bio_age`（时钟给出的年龄数值）、`chrono_age`（采样时的日历年龄）、`organs`（器官年龄，可选）。
- `clock_type` 照报告写：`GrimAge2`、`GrimAge`、`DunedinPACE`、`DNAm PhenoAge`；以日历年龄为训练目标的普通"生物学年龄"写 `first_generation`；不清楚写 `unknown`。同一份报告有几个时钟就写几条。
- **只有 `GrimAge2` / `GrimAge` 计入 LongPi Age**，而且要在计算日之前 3 年内采样。它们在 NHANES 随访里有明显的额外信息；其他时钟和器官年龄只展示在前沿页，增量见 `params.json: methylation.not_counted`。
- 计入时，先按 NHANES 参考曲线算"加速"，再减去按这个人其他指标预期的加速，剩下的部分才计入，并且按实验室之间可能的系统差异打折（`s_lab` 2.4 岁）。


## 引擎 1.1.2 新增的输入

- **标准观测 `observations_file`**：组学层（`longpi-omics`）把基因组 VCF、甲基化 β 值、蛋白组、代谢组、宏基因组等二级数据算成
  标准观测，写进 `observations.json`；读入时整理出的其他指标（不在上面化验表里的）也可以写进这个文件。格式见
  `references/registry_contract.md` 第 2 节。每条观测都要有标准编码（`LOINC:`、`ICD10:`、`PGS:`、`LP:` 等）。
- **已确诊疾病**：`conditions[].icd10` 由读入时根据诊断名称填写（例如 2 型糖尿病 `E11`、高血压 `I10`）。没有编码的诊断不参与疾病风险判定，`check` 会提示。
- **家族史**：`family_history[].disease_id` 取 `registry/outcomes/` 里的 id（`t2d`、`chd`、`stroke`、`htn`、`ckd`、`masld`、`crc`、`lung_ca`、`liver_ca`、`gastric_ca`、`breast_ca`、`prostate_ca`、`ad`）。只计一级亲属。
- **用药**：`medications[].class` 用 `antihypertensive`、`statin`、`lipid_lowering`、`antidiabetic`、`urate_lowering`，并写 `since`（必要时 `until`）。
  用药期间测得的相关指标会标为"用药下的值"，按用药前的值计算（没有用药前的值时如实说明）。
- **暂时状态**：某次化验时正在生病、怀孕、刚剧烈运动、非空腹、近 3 个月用过抗生素（宏基因组）、输过血，在该次 `labs[].flags` 写
  `acute_illness`、`pregnancy`、`post_exercise`、`non_fasting`、`antibiotics_3m`、`transfusion`；相关指标不计入。
- **行为**：手表步数由脚本从可穿戴数据算出并判断已持续几周；自述的运动写在 `lifestyle`，带 `since`。持续满 8 周才计入 120 指数，自述的打五折。
- **筛查**：`screenings[].test` 用 `crc_fit`（粪便免疫化学检测）、`crc_colonoscopy`、`lung_ldct`、`liver_us_afp`、`gastroscopy`、`mammography`；
  有报告的写 `report: true`。
- **明确阴性**：化验确认没有的情况写进 `negative_findings`，例如 `[{"code": "ICD10:B18.1", "date": "2025-06", "report": true}]`（乙肝表面抗原阴性）。
  没有写的不会被当成阴性。
- **输入校验**：`check` 对类型、数值（必须是有限数字）、日期格式、生理范围、ICD-10 编码、`genetic_preferences`（只能是 true/false）做严格检查，有错误时 `compute` 不运行。
- **遗传结果告知**：`genetic_preferences.show_opt_in`（是否查看 APOE ε4 等不可干预的结果）和 `secondary_findings`（是否接收单基因致病变异等次要发现）
  默认都是 `false`；本人选择后才计入和展示。上传前要问清楚。
