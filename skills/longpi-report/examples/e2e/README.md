# 端到端测试输入

本目录存放两位合成测试对象（P1：男，约 48 岁；P2：女，约 61 岁）的组学输入，供端到端测试使用。
所有文件均为生成或派生数据，不属于任何真实个人。

## 甲基化、蛋白组、代谢组、宏基因组（合成）

以下四个文件由 `skills/longpi-omics/validation/make_e2e_synthetic.py` 以固定随机种子（20261118）生成，可重复再生成。

| 文件 | 对象 | 内容 | 生成方式 |
|---|---|---|---|
| `P1_methylation_beta.csv` | P1 | 甲基化 β 值：Horvath 2013（353 个位点）与 Hannum 2013（71 个位点）全部时钟位点，另加 200 个无关位点 | 以作者公布的位点中位数为基础加小幅随机扰动，再沿系数方向整体平移，使 Horvath 约 50 岁、Hannum 约 48 岁；有意留空 5 个 Horvath 位点与 1 个 Hannum 位点（约 1.4%），用于检验缺失位点处理 |
| `P1_nightingale.csv` | P1 | Nightingale 核磁代谢组 38 项（2016 平台命名，第二行为单位；白蛋白为该平台的信号单位） | 数值按 BBMRI-NL 人群典型水平手工设定，含 MetaboHealth 所需全部 14 项 |
| `P2_somascan.csv` | P2 | SomaScan 风格的 ANML 标准化 RFU，5284 个 SeqId（v4.0 5K 菜单），用于检验版本识别（v4）与 v4→v4.1 换算 | organage 模型蛋白按训练队列均值与标准差加随机偏移生成；其余蛋白按厂商注释中的健康人血浆中位数加扰动生成；NT-proBNP、GDF15、胱抑素 C、CRP、IL-6、瘦素 6 个直通蛋白取合理数值 |
| `P2_species_abundance.tsv` | P2 | MetaPhlAn2 单样本格式的物种相对丰度（30 个物种，合计 100%） | 手工设定，包含 GMHI 的 6 个健康富集物种与 8 个健康稀缺物种 |

说明：

- 文件中的样本列名（如 `SYNTH_P1`）只用于标识合成数据，组学层输出的 observations.json 不写入样本列名。
- 运行示例：`python3 skills/longpi-omics/scripts/omics.py methylation skills/longpi-report/examples/e2e/P1_methylation_beta.csv --age 48 --sex M --person-code P1 --out P1.observations.json`；蛋白组需 `--age 61 --sex F`。
- 这些数值只用于检验流程是否走通与输出是否可复现，不代表任何健康结论。

## 基因组（派生自 1000 Genomes 公开样本）

以下文件由 `skills/longpi-omics/validation/build_e2e_genotypes.py` 从 1000 Genomes 高深度（NYGC 30x，GRCh38）公开、开放授权的东亚样本派生，样本编号已改为 P1、P2，只保留检验所需的区域。

| 文件 | 对象 | 内容 |
|---|---|---|
| `P1_genotypes_GRCh38.vcf` | P1（男，汉族北京样本） | 单样本 VCF，带 contig 头部。保留：祖源信息位点、APOE、药物基因组位点、4 个测试评分的全部位点（含纯合参考的调用）；LDLR 基因区只保留非参考调用（与真实全基因组 VCF 一致）；X 染色体一段（40 kb）内 1000 Genomes 频率 ≥5% 的常见位点连同纯合参考调用一并保留，用于性别核对 |
| `P2_chip_23andme_GRCh37.txt` | P2（女，汉族南方样本 CHS） | 23andMe 格式的芯片文本（GRCh37 坐标，经 UCSC 链文件转换），只含单核苷酸位点 |
| `P2_wgs_LDLR_GRCh38.vcf` | P2 | 小型"全基因组来源"VCF：LDLR 区域的真实调用，另**人为加入**一个 ClinVar 致病（审核 ≥2 星）的 LDLR 杂合单核苷酸变异，用于检验单基因致病变异路径；该变异为合成，不属于原始样本 |
| `genotype_sources.json` | — | 派生说明：来源人群、加入变异的 ClinVar 编号与坐标、测试评分清单 |
| `people/P1/observations.json`、`people/P2/observations.json` | — | 组学层在全部输入上的输出（命令见下节），供引擎端到端运行 |

说明：

- 测试评分：PGS002262（冠心病，540 个位点）、PGS003353（2 型糖尿病，287 个）、PGS000050（乳腺癌，44 个）、PGS000070（肺癌，19 个），均以东亚人群为主建立。
- 同一 P1 调用转换到 GRCh37 的版本（无 contig 头部，用于检验按标记位点识别版本）放在 `skills/longpi-omics/tests/fixtures/genotype/`。
- 运行示例：`python3 skills/longpi-omics/scripts/omics.py genotype skills/longpi-report/examples/e2e/P1_genotypes_GRCh38.vcf --sex M --person-code P1 --pgs PGS002262 --out P1.observations.json`；
  `P2_wgs_LDLR_GRCh38.vcf` 需加 `--source-type wgs`。

## 生成 people/P1、P2 的 observations.json

```bash
python3 skills/longpi-omics/scripts/run_e2e.py            # 写入 examples/e2e/people/P1|P2/observations.json
python3 skills/longpi-omics/scripts/run_e2e.py --print    # 只打印逐条命令
python3 skills/longpi-omics/scripts/run_e2e.py --offline  # 只用本地缓存的参考数据
```

逐条命令（路径相对仓库根目录；每人先删除旧文件再依次运行，保证重复运行逐字节一致）：

```bash
E=skills/longpi-report/examples/e2e; O=skills/longpi-omics/scripts/omics.py
PGS="--pgs PGS002262 --pgs PGS003353 --pgs PGS000050 --pgs PGS000070"
# P1：基因组（GRCh38 VCF）+ 甲基化 + 代谢组
python3 $O genotype     $E/P1_genotypes_GRCh38.vcf --out $E/people/P1/observations.json --person-code P1 --sex M --date 2026-05-18 $PGS
python3 $O methylation  $E/P1_methylation_beta.csv --out $E/people/P1/observations.json --person-code P1 --age 48 --sex M --date 2026-05-18
python3 $O metabolomics $E/P1_nightingale.csv      --out $E/people/P1/observations.json --person-code P1 --date 2026-05-18
# P2：芯片（GRCh37）+ 全基因组来源的 LDLR 小 VCF（只做单基因补充）+ 蛋白组 + 宏基因组
python3 $O genotype     $E/P2_chip_23andme_GRCh37.txt --out $E/people/P2/observations.json --person-code P2 --sex F $PGS
python3 $O genotype     $E/P2_wgs_LDLR_GRCh38.vcf     --out $E/people/P2/observations.json --person-code P2 --source-type wgs --monogenic-only --date 2026-06-02
python3 $O proteomics   $E/P2_somascan.csv            --out $E/people/P2/observations.json --person-code P2 --age 61 --sex F --date 2026-06-02
python3 $O metagenome   $E/P2_species_abundance.tsv   --out $E/people/P2/observations.json --person-code P2 --date 2026-06-02
```

- 参考数据（4 个评分文件、东亚参考分布、ClinVar ACMG 子集）缓存在 `~/longpi/omics-ref/`；缓存为空时从公开站点下载，1000 Genomes 按位点读取，网速慢时耗时较长。
- `--monogenic-only` 把临床全基因组文件中的致病变异追加到已有观测，不覆盖芯片得到的 PRS、APOE、药物基因组结果。
- 当前输出：P1 为男性（X 染色体单倍体调用）、APOE ε3/ε3、PGS000070 因位点覆盖率 0.79 低于 0.8 不出分；
  P2 为女性（芯片 X 杂合比例 0.14）、APOE ε2/ε3、计入 1 个 LDLR 致病变异（`LP:monogenic:HGNC:6547`）。
- P2 的 1000 Genomes 来源样本按 X 染色体片段的杂合位点数选择（片段只有 120 kb，多数女性在其中杂合位点很少），以便性别核对有足够信息。
