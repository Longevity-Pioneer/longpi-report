# 组学层工具验证记录（2026-11-18）

入库门槛（PRD §5b.3）：① 用已知答案的公开样本复现原作者或参考实现的结果；② 同一输入运行两次输出逐字节一致；
③ 许可允许商业使用；④ 不联网发送任何个人数据。每项数字由 `validation/` 下的脚本实测，原始结果在
`validation/results/<tool_id>.json`，汇总进 `tools/REGISTRY.json`（`validation/make_registry.py` 生成）。

运行环境：macOS（arm64），Python 3.11，numpy 1.26 / scipy 1.16 / pandas 2.3，bcftools 1.23.1（htslib 1.24），
PLINK v2.0.0-b.1.3。当日网络带宽约 10–40 KB/s，因此全部下载都限制在小文件或按区域读取，见各节说明。

<!-- GENOTYPE -->

## 甲基化

| 工具 | 数据 | 指标 | 实测 | 结论 |
|---|---|---|---|---|
| `meth_horvath2013` | 50 个固定种子生成的伪样本（时钟位点） | 与 biolearn 0.9.1 的最大绝对差 | 0.0103 岁；Pearson 0.99999999987 | 通过（差值全部来自 biolearn 把截距取整为 0.696，作者原值 0.695507258） |
| `meth_hannum2013` | 同上 | 与 biolearn 0.9.1 的最大绝对差 | 3.6e-14 岁；Pearson 1.0 | 通过 |

- 未在真实 GEO 数据上验证：候选数据集 GSE41169 为 193 MB，当日带宽下无法下载；因此**没有**测得与实际年龄的相关系数和平均绝对误差。
- 时钟加速 `*_accel` 采用"时钟值 − 实际年龄"（Horvath 在线计算器的 AgeAccelerationDiff），没有拟合人群回归线。
- DNAm PhenoAge 未实现：论文为 CC BY 3.0，但系数的商业使用须取得授权（biolearn 使用元数据注明 UCLA TDG / Clock Foundation），只接收厂商结果；GrimAge、GrimAge2、DunedinPACE 同样只接收厂商结果。

## 蛋白组

| 工具 | 数据 | 指标 | 实测 | 结论 |
|---|---|---|---|---|
| `prot_organage2023` | organage 作者示例数据（200 例 × SomaScan v4.1，13 个器官模型）及其笔记本中打印的结果 | 与 organage 包的器官年龄差最大绝对差 | 6.5e-13 岁（2600 个比较）；笔记本打印的 5 行完全一致 | 通过 |

- organage 为 MIT 许可（Oh et al. 2023 Nature）。500 个自助抽样 Lasso 模型合并为一个线性模型（数学上等价）；作者的模型文件由不执行代码的受限反序列化读取。
- Olink 时钟（ProtAge，Argentieri 2024）未实现：未能核实系数许可。Olink 输入只做单蛋白透传。

## 代谢组

| 工具 | 数据 | 指标 | 实测 | 结论 |
|---|---|---|---|---|
| `metab_metabohealth2019` | MiMIR 1.5 自带的 500 例合成 Nightingale 数据 | 数据集内标准化下与 MiMIR `comp.mort_score`（R 中运行）的最大绝对差 | 4.2e-15，缺失模式一致 | 通过 |

- 单人计算时无法做数据集内标准化，改用 MiMIR 提供的 BBMRI-NL（荷兰）对数均值与标准差；与数据集内标准化相比 Pearson 0.964、均值偏移 −0.105。这是近似，报告中应注明人群来源。

## 宏基因组

| 工具 | 数据 | 指标 | 实测 | 结论 |
|---|---|---|---|---|
| `micro_gmhi2020` | Gupta 2020 作者示例（25 个 MetaPhlAn2 样本）与作者发布的 GMHI_output.csv | 最大绝对差 | 4.9e-15 | 通过 |
| `micro_shannon` | 同上 | 与 scipy.stats.entropy 的最大绝对差 | 1.8e-15 | 通过 |

<!-- DETERMINISM -->
