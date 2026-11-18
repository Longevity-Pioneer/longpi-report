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
