---
name: longpi-omics
description: >-
  LongPi 组学层：把个人的二级组学数据（VCF 或 23andMe 类芯片原始基因型、甲基化 β 值矩阵、SomaScan/Olink
  蛋白组矩阵、Nightingale 核磁代谢组表、宏基因组物种丰度表）用已入库、已验证的确定性工具转换成
  标准观测文件 observations.json（longpi.observations/1），供 longpi-report 引擎使用。用于"分析我的基因数据"、
  "算多基因风险评分/PRS"、"APOE 分型"、"致病变异筛查"、"药物基因组"、"甲基化时钟"、"蛋白组年龄"、
  "代谢组评分"、"肠道菌群指数"，或 longpi-report 需要把组学原始结果变成观测时。
  不处理一级数据（FASTQ、IDAT、质谱原始文件）。
---

# LongPi 组学层

**定位**：读二级数据 → 质控 → 用工具库（`tools/REGISTRY.json`）里已验证的工具计算 → 写 `observations.json`。
所有数值由脚本算出；Claude 只负责选择命令、核对输入、向用户解释结果，**不得**临时编写代码分析用户数据并把结果当作数值使用。

## 命令

```bash
S=skills/longpi-omics/scripts/omics.py
python3 $S genotype     <vcf|芯片txt> --out obs.json --person-code U01 [--sex M|F] [--pgs PGS002262] [--build auto]
python3 $S methylation  <beta.csv>   --out obs.json --age 48
python3 $S proteomics   <somascan.csv|olink.csv> --out obs.json --age 61
python3 $S metabolomics <nightingale.csv> --out obs.json
python3 $S metagenome   <species.tsv> --out obs.json
```

- 每个子命令把自己的结果并入 `--out`，重复运行会替换本工具上次写入的内容，不影响其他工具的观测。
- `--person-code` 只写编码，不写姓名；样本名、条码不会写入输出。
- 参考数据缓存在 `~/longpi/omics-ref/`（环境变量 `LONGPI_OMICS_REF` 可改）。首次运行会下载公开资源；
  加 `--offline` 时只用缓存，缺数据即报错。

## 基因组（`genotype`）

1. 识别参考基因组版本（VCF 头部 contig 长度，或固定标记位点在两个版本中的位置）、样本缺失率、杂合率、X 染色体性别核对。
2. 族裔估计：Kidd 55 个祖源信息位点，以 1000 Genomes 五个大洲人群频率做受监督混合比例估计。
3. PRS：PGS Catalog 统一坐标评分文件（按用户版本）；位点覆盖率低于 0.8 不出分；
   以 1000 Genomes 东亚 504 人在同一组位点上的得分分布换算 z 值与百分位。许可不允许商业使用的评分拒绝计算并记录。
   评分来源：`--pgs` 参数，以及 `longpi-report/registry/terms/*.json` 中输入编码为 `PGS:` 的项。
4. APOE：rs429358 + rs7412 → `LP:apoe_e4_count`；ε4/ε4 标 `disclosure: opt_in`（默认不展示）。
5. 单基因致病变异：ClinVar（按版本下载，记录发布日期），仅 ACMG SF v3.2 基因、仅"致病/可能致病"且审核 ≥2 星；
   意义不明变异不报告。WGS/WES 来源输出 `LP:monogenic:<HGNC>`；**芯片来源只列出、不计入**，
   并注明需临床级检测确认（消费级芯片对罕见变异假阳性率很高）。确认后可加 `--confirmed`。
6. 药物基因组：CYP2C19、CYP2C9、VKORC1、SLCO1B1、TPMT、NUDT15、DPYD、CYP3A5，按 CPIC 规则判读；数据未分相，结果附说明。
7. 填补（可选）：`--impute --panel <目录>` 调用 Beagle 5.x；只接受用户自备的分染色体参考面板，本技能不下载全基因组面板。

## 甲基化、蛋白组、代谢组、宏基因组

- 甲基化：识别 450K / EPIC v1 / EPIC v2，计算 Horvath 2013、Hannum 2013、DNAm PhenoAge（系数公开）；
  输出时钟值与 `LP:clock.<name>_accel`。GrimAge、GrimAge2、DunedinPACE 为商业授权，只接收厂商结果（`--vendor-json`）。
- 蛋白组：识别 SomaScan 版本或 Olink；只实现系数公开且许可允许商业使用的时钟；有结局证据的单个蛋白以 `UNIPROT:` 观测透传。
- 代谢组：Nightingale 核磁平台 → MetaboHealth（`LP:metab.metabohealth`）。
- 宏基因组：区分 16S 与宏基因组，检查深度 → GMHI（`LP:micro.gmhi`）、Shannon 指数（`LP:micro.shannon`）。

## 规则

- 只把有对应项或定性条目的特征写成观测，不倾倒大量无结局证据的特征。
- 每一步的工具名、版本、参考数据版本写进 `provenance`；同一输入、同一版本重复运行，输出逐字节一致。
- 外发请求只用于下载公开参考资源（PGS 评分文件、ClinVar、1000 Genomes 位点），从不携带个人基因型、数值、样本名或文件内容。
- 工具入库门槛与验证记录见 `tools/REGISTRY.json` 与 `VALIDATION.md`；未入库的工具产出最多作定性佐证。
- 遗传结果的展示须经宿主产品的告知同意流程；本技能只按 `disclosure` 字段分级。

## 测试

```bash
python3 -m unittest discover -s skills/longpi-omics/tests        # 离线快速测试
LONGPI_OMICS_SLOW=1 python3 -m unittest discover -s skills/longpi-omics/tests   # 含联网验证
```

## 同一个人有两份基因数据

例如消费级芯片 + 临床 WGS/WES：两个文件都用 `genotype` 跑，写进同一个 `observations.json`，顺序不限。
位点更多的一份作为主数据（多基因评分、APOE、药物基因组、族裔），另一份作为补充（只加入它的致病变异）；
一个文件重跑只替换它自己上次的结果。只含少数基因区域的小文件（如 LDLR 区段）建议加 `--monogenic-only`。
每次都写 `--sex`（与 person.json 一致），小文件没有足够的 X 染色体位点时无法自行判断性别。

## 离线运行

`--offline` 只用 `~/longpi/omics-ref` 里已缓存的参考数据。没缓存的评分文件或东亚参考分布会标为"未计算"并写明原因，其余步骤照常完成。
缓存的压缩文件在第一次使用时做完整性检查，下载中断留下的残缺文件会被删除并重新下载。
