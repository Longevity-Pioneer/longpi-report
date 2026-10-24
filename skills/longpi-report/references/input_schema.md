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
    "sleep_h": 7.0                                           // 问卷口径"平时一晚睡几个小时"
  },
  "conditions": [ { "name": "高血压", "diagnosed": "2024", "treated": true } ],
  "medications": [ { "name": "氨氯地平", "dose": "5 mg qd", "since": "2024-06", "class": "antihypertensive" } ],
  "family_history": [ { "relation": "father", "condition": "高血压", "age_at_dx": 52 } ],
  "imaging": [ { "date": "2026-05-18", "type": "腹部超声", "finding": "肝脏回声未见明显异常" } ],
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
