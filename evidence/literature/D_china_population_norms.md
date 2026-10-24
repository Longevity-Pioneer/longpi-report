# Topic D: Chinese adult population distributions by sex and age (LongPi mortality model)

Compiled 2026-10-24 for the LongPi methods paper. The model expresses a person's risk relative to the average Chinese adult of the same age and sex. This file collects the reference distributions: the mean, the SD or percentiles, or the category prevalences, by sex and age group, for each marker.

## How to read this file

- **Verified.** "verified = true" means the number was read in a retrieved full text, table, supplementary file or official table image, never from memory. "Abstract only", "text" or "derived" is stated wherever it applies.
- **Derived values.** Values we computed are labelled "derived" or "our conversion". Examples: never-smokers = 100 − current − former, and mg/dL → mmol/L.
- **Quotes.** All quotes are verbatim from the retrieved source, in Chinese or English. "…" marks an omission.
- **Identifiers.** PMIDs and DOIs are given as shown on the retrieved page or record.
- **Spread vs precision.** A 95% CI or an SE describes the precision of the mean. It is **not** the spread of the population. SDs or percentiles are given wherever a source prints them, and their absence is flagged.
- **Weighting.** CCDRFS estimates are weighted to the 2010 census, or standardised to it, unless stated otherwise. Fitness-surveillance means are unweighted sample means within each cell.

## Summary: best available source per marker

| Item | Marker | Primary source (survey year; n) | Sex x age cells | Spread (SD / percentiles) | Main gaps |
|---|---|---|---|---|---|
| D1 | SBP, DBP, hypertension | CCDRFS 2018 (Zhang M, *Chin J Epidemiol* 2021; *BMJ* 2023 suppl.); n about 180k | Hypertension prevalence by sex x 10-y band, 18 to ≥80. Mean SBP/DBP by sex x 10-y band, 18-69 | 95% CI only for sex x age. SD overall (18.8/11.2 mmHg, 2018), and by sex or by age band from CCDRFS 2013. CHARLS percentiles 50-100 | SD by sex x age; mean BP ≥70 |
| D2 | TC, LDL-C, HDL-C, TG | CANCDS 2015 (Song PK, *BES* 2019): means by sex and by age band separately. CCDRFS 2018: prevalences | Not crossed | TC/HDL-C SD by sex or by age band (CCDRFS 2013); CHARLS 45+ overall | Sex x age means |
| D3 | FPG, HbA1c, diabetes, prediabetes | CCDRFS 2018 (Wang L, *JAMA* 2021): prevalence by sex and by 6 age bands. CNHS 2015-17 (Yu D, *AJPM Focus* 2024): FPG/HbA1c by sex x 3 bands | FPG/HbA1c yes (3 bands). Prevalence not crossed | Percentiles P5-P95 (CNHS); SD by sex or by age band (CCDRFS 2013) | Diabetes prevalence by sex x age |
| D4 | BMI, waist, overweight/obesity | CNHS 2015-17 BMI; CNHS 2015 waist (*BES* 2025); CCDRFS 2018 overweight/obesity by sex x 3 bands x urban/rural | Yes | BMI percentiles; BMI and waist SD by sex | Central obesity by sex x age |
| D5 | Smoking (current/former/never), starting age | CCDRFS 2018 (Zhang M, *PLoS Med* 2022 S3) 18-69, 7 bands; GATS 2018 and NATS 2024 for ≥65 | Yes (≥70 only as ≥65) | not applicable | Sex x 70+ in CCDRFS |
| D6 | Drinking, heavy/harmful drinking | 2024 national survey (Ji N, *China CDC Wkly* 2026); CCDNS 2015 (g/day); CCDRFS 2018 hazardous/harmful by sex x 3 bands x urban/rural (Song S 2023) | Yes | Mean g/day among drinkers | none major |
| D7 | Resting heart rate | 2014 National Physical Fitness Surveillance (healthy volunteers) by sex x 5-y band, 20-69; TIDE 2015-17 by sex; CHARLS 2015 percentiles 50-100 | Partial | CKB SD about 11-12 bpm; CHARLS percentiles | General-population mean (SD) by sex x age |
| D8 | Grip strength | 6th National Physical Fitness Surveillance 2025, by sex x 5-y band, 20-79; CNHS 2012-17 (He H 2023) mean/SD/percentiles; CHARLS + SAGE to 94 | Yes | SD and percentiles (CNHS; CHARLS) | not applicable |
| D9 | Sleep duration | CCDRFS 2018 (Chen Y, *BES* 2026): mean (SD) by sex and by age; short/long sleep by sex x age x residence | Prevalences yes; means not crossed | SD yes | Mean by sex x age |
| D10 | VO2max / cardiorespiratory fitness | 6th National Physical Fitness Surveillance 2025, estimated VO2max (submaximal cycle test) by sex x 5-y band, 20-59; CPET references (regional) | Yes (estimate) | SD only from regional CPET | National SD; the estimation equation |
| D11 | Daily steps | Althoff 2017: China mean 6,189 (smartphone). CKB 2020-21 wrist accelerometer by sex and urban/rural, older adults | No | SD-sized values in CKB Table 2 | Nationally representative device steps by sex x age |

## General caveats

1. **Survey years.** Sources span 2013 to 2025, so secular trends matter. Male smoking fell from 50.5% (2018) to 43.9% (2024). Adiposity rose over 2004-2018. Adult grip strength keeps falling. Prefer the most recent table for each marker, and state its year.
2. **Measurement protocols differ.** BP devices include the Omron HBP-1300, HEM-7430 and A&D UA-779. HbA1c analysers include the Bio-Rad D-10, Variant II and Premier Hb9210, and mean HbA1c differs by 0.4-0.6 percentage points across surveys. Grip uses the 握力计 (best of 2, stronger hand) in some surveys and a Jamar or mechanical dynamometer in others. The national VO2max is a submaximal estimate.
3. **National Physical Fitness Surveillance samples.** These are drawn from institutions, workplaces and villages, not households. The 2014 round admitted only healthy volunteers (D7-A, verbatim footnote). The 2020 and 2025 bulletins state no health criterion. Treat these norms as describing an apparently healthy, testable population.
4. **Unweighted analyses.** The CHARLS percentile analyses (Appendix A; Grgic 2026) and some CNHS SDs are unweighted.

---

## D1. Blood pressure

**Bottom line.** For 2018, the China Chronic Disease and Risk Factor Surveillance (CCDRFS) gives what the model needs:
- hypertension prevalence by sex × 10-year age group from 18 to ≥80 (D1.1, Table D1-a);
- mean SBP and DBP by sex × age for ages 18–69 (D1.2, Table D1-b). These means come with 95% CIs, not SDs.

SDs:
- For 2018, only all-adult SDs are published: SBP 127.7 ± 18.8 and DBP 76.8 ± 11.2 mmHg in CCDRFS 2018.
- CCDRFS 2013 gives SBP SDs by sex and by age band, not crossed (D1.6).
- CHARLS 2015 gives SBP/DBP percentiles by sex at ages 50-100 (Appendix A).
- No SDs exist by sex x age; see D1.5.

We could not open the age × sex table of the China Hypertension Survey 2012–2015 (Wang Z et al., *Circulation* 2018) because it is paywalled. Only its overall figures and its figures by sex are reported here (D1.3).

### D1.1 CCDRFS 2018: hypertension prevalence by sex × age, adults ≥18 y (including 70–79 and ≥80)

**Survey**
- China Chronic Disease and Risk Factor Surveillance 2018 (中国慢性病及危险因素监测), fieldwork August 2018 to June 2019.
- Coverage: 298 counties/districts in 31 provinces, sampled by multistage stratified cluster random sampling.
- Analysed n = 179 873 (men 79 469; women 100 404), aged ≥18 y.
- Estimates are weighted (sampling × non-response × post-stratification weights; post-stratification to the 2010 census).

**Citation**
- Zhang M (张梅), Wu J (吴静), Zhang X (张笑), Hu CH, Zhao ZP, Li C, Huang ZJ, Zhou MG, Wang LM. 2018年中国成年居民高血压患病与控制状况研究 [Prevalence and control of hypertension in adults in China, 2018]. *中华流行病学杂志 (Chin J Epidemiol)* 2021;42(10):1780–1789.
- doi:10.3760/cma.j.cn112338-20210508-00379. PMID 34814612 (from the Europe PMC record).
- Full text: https://html.rhhz.net/zhlxbx/20211008.htm. Table 2 is an image: https://html.rhhz.net/zhlxbx/PIC/zhlxbxzz-42-10-1780-T2.jpg.
- Reproduced in English, with the same numbers except women aged 18–29 printed as "4.55%", in Table 3 of: Hu SS, Writing Committee of the Report on Cardiovascular Health and Diseases in China. Cardiovascular Risk Factors in China. *J Geriatr Cardiol* 2024;21(2):153–199. doi:10.26599/1671-5411.2024.02.008. PMID 38544492. https://pmc.ncbi.nlm.nih.gov/articles/PMC10964013/

**Verified: true.** The numbers below were read from the original Chinese table image (表2) and cross-checked against JGC 2024 Table 3.

**Table D1-a. Weighted prevalence of hypertension, % (95% CI), 2018**

Hypertension was defined as SBP ≥140 and/or DBP ≥90 mmHg, or a history of hypertension with antihypertensive drugs taken in the past 2 weeks.

| Age (y) | Men: n analysed | Men: cases | Men: prevalence | Women: n analysed | Women: cases | Women: prevalence | All: prevalence |
|---|---|---|---|---|---|---|---|
| 18–29 | 4 031 | 513 | 13.4 (11.5–15.2) | 5 385 | 229 | 4.5 (3.4–5.7) | 8.9 (7.7–10.1) |
| 30–39 | 7 243 | 1 393 | 19.0 (17.6–20.5) | 10 501 | 846 | 7.7 (6.8–8.6) | 13.4 (12.6–14.3) |
| 40–49 | 13 548 | 4 342 | 30.9 (29.8–32.1) | 18 855 | 4 258 | 20.4 (19.5–21.4) | 25.7 (24.9–26.6) |
| 50–59 | 20 089 | 8 820 | 45.1 (43.7–46.4) | 27 176 | 11 242 | 41.0 (39.8–42.1) | 43.0 (42.1–44.0) |
| 60–69 | 22 595 | 12 351 | 54.1 (52.8–55.3) | 26 405 | 14 890 | 54.8 (53.5–56.0) | 54.4 (53.4–55.4) |
| 70–79 | 10 051 | 6 275 | 62.1 (60.1–64.1) | 10 136 | 6 862 | 68.0 (66.3–69.7) | 65.2 (63.6–66.7) |
| ≥80 | 1 912 | 1 239 | 62.4 (59.6–65.2) | 1 946 | 1 377 | 70.1 (67.2–72.9) | 66.7 (64.3–69.1) |
| All ≥18 | 79 469 | 34 933 | 30.8 (29.8–31.9) | 100 404 | 39 704 | 24.2 (23.3–25.1) | 27.5 (26.6–28.4) |

The "n analysed" columns come from 表1 (sample characteristics). The cases and prevalences come from 表2.

**Verbatim quotes (CJE 2021)**
- Abstract: "结果 2018年，中国≥18岁居民SBP均值为（127.7±18.8）mmHg（1 mmHg=0.133 kPa），DBP为（76.8±11.2）mmHg。…成年居民高血压患病率为27.5%（95%CI：26.6%~28.4%），男性[30.8%（95%CI：29.8%~31.9%）]高于女性[24.2%（95%CI：23.3%~25.1%）]，农村[29.4%（95%CI：28.4%~30.3%）]高于城市[25.7%（95%CI：24.4%~27.1%）]"
- Definition: "SBP≥140 mmHg和（或）DBP≥90 mmHg，或既往有高血压病史且近2周内服用降压药物的调查对象被定义为高血压患者。"
- Measurement: "统一使用经验证合格的上臂式医用电子血压计（欧姆龙HBP1300）测量SBP和DBP…静坐休息5 min后开始测量。每名调查对象接受3次血压测量，每次测量之间取下袖带休息至少1 min。本研究取第二次和第三次测量值的平均值作为个体血压值。"
- Weighting: "权重由抽样权重、无应答权重和事后分层权重计算所得。其中事后分层权重采用2010年第六次全国人口普查的人口数据进行计算"
- 表2 note: "注：高血压患病率为经过加权计算后的加权率，括号内为高血压患病率的95%CI值；男女性高血压患病率比较，χ2=175.80，P<0.000 1"
- Mean BP by age: "SBP随年龄增长而升高，DBP则以50~59岁组为最高". Means by sex and by age are shown only as bar/line charts with ±SD error bars (图1). No numbers are printed, so they are not transcribed here.

**Official report: same survey, broad age bands**
- Source: 中国疾病预防控制中心, 中国疾病预防控制中心慢性非传染性疾病预防控制中心 编著. 《中国慢性病及危险因素监测报告2018》. 北京: 人民卫生出版社, 2021.10. ISBN 978-7-117-32099-3.
- Web text of 摘要: https://fwdbook.qq.com/read/1053696612/6. English Abstract: https://fwdbook.qq.com/read/1053696612/7.
- 摘要 quote: "2018年我国18岁及以上居民高血压患病率为27.5%，男性（30.8%）高于女性（24.2%），农村（29.4%）高于城市（25.7%），18～44岁组、45～59岁组和60岁及以上组分别为13.3%、37.8%和59.2%，东、中、西部地区分别为27.3%、29.1%、25.9%。"
- Report sample: n = 184 509 analysed. **Verified: true** (text retrieved).

### D1.2 CCDRFS 2004–2018 (six rounds): mean SBP and DBP by sex × age (18–69 y), plus standardised hypertension prevalence

**Citation**
- Zhang M, Shi Y, Zhou B, Huang Z, Zhao Z, Li C, Zhang X, Han G, Peng K, Li X, Wang Y, Ezzati M, Wang L, Li Y. Prevalence, awareness, treatment, and control of hypertension in China, 2004–18: findings from six rounds of a national survey. *BMJ* 2023;380:e071952.
- doi:10.1136/bmj-2022-071952. PMID 36631148. PMCID PMC10498511.
- Supplement file zham071952.ww1.pdf, retrieved through the Europe PMC supplementaryFiles service.

**Sample.** 642 523 adults aged 18–69 across all rounds; 155 049 in 2018. The 2018 round was restricted to 18–69 y because the 2004 survey covered only that range.

**Verified: true** (Supplementary Tables 4 and 11 read in full).

- Methods (main text): "blood pressure was measured in all respondents—three times successively with a one minute interval between measurements, using mercury sphygmomanometers in 2004 and electronic blood pressure monitors from 2007 (Omron, Dalian, China)… The average of the last two readings was used for analyses."
- Devices: "Omron HEM-770A in 2007, HEM-7071 in 2010, and HBP-1300 in 2013, 2015, and 2018".
- Supplement 4: "Overall, mean SBP and mean DBP increased from 121.8 (120.9-122.8) mmHg and 76.8 (76.0-77.5) mmHg in 2004 to 128.7 (127.7-129.7) mmHg and 80.1 (79.6-80.6) mmHg in 2010 (both P<0.001), then declined to 126.4 (125.7-127.1) mmHg and 77.0 (76.6-77.5) mmHg in 2018 (both P<0.001)."

**Table D1-b. Mean SBP, mean DBP and raised-BP prevalence, 2018 round, by sex × age**

Source: Supplementary Table 11, "Trends in SBP, DBP and raised BP prevalence by age group". Footnote: "Results were weighted to the 2010 census population in China." Values are mean or % with 95% CI.

| Sex | Age (y) | SBP, mmHg | DBP, mmHg | Raised BP, % |
|---|---|---|---|---|
| Men | Overall 18–69 | 130.1 (129.4–130.7) | 79.7 (79.3–80.2) | 26.0 (24.2–27.8) |
| Men | 18–29 | 125.3 (124.5–126.1) | 75.2 (74.5–75.9) | 13.0 (10.9–15.0) |
| Men | 30–39 | 127.1 (126.4–127.8) | 79.6 (79.0–80.1) | 18.8 (17.0–20.7) |
| Men | 40–49 | 130.4 (129.6–131.1) | 82.3 (81.8–82.8) | 28.8 (27.0–30.5) |
| Men | 50–59 | 135.8 (134.8–136.7) | 83.3 (82.7–83.8) | 40.4 (38.4–42.4) |
| Men | 60–69 | 139.7 (138.7–140.7) | 80.8 (80.2–81.3) | 46.8 (44.6–49.1) |
| Women | Overall 18–69 | 122.6 (121.5–123.7) | 74.2 (73.6–74.9) | 17.3 (15.7–18.8) |
| Women | 18–29 | 113.2 (112.2–114.2) | 70.2 (69.4–70.9) | 3.9 (2.8–5.0) |
| Women | 30–39 | 116.3 (115.2–117.5) | 72.7 (72.0–73.5) | 7.6 (6.0–9.1) |
| Women | 40–49 | 124.6 (123.4–125.8) | 76.2 (75.5–76.9) | 18.6 (17.0–20.1) |
| Women | 50–59 | 133.5 (132.5–134.4) | 78.4 (77.9–78.9) | 33.8 (31.9–35.6) |
| Women | 60–69 | 139.4 (138.2–140.5) | 77.3 (76.6–77.9) | 44.8 (42.7–46.8) |

The same supplementary table also gives these values for 2004, 2007, 2010, 2013 and 2015. For example, the 2015 values for men aged 60–69 were SBP 141.7 and DBP 81.6.

"Raised BP" is a measured value of ≥140/90 mmHg, regardless of treatment. That definition is inferred from the paper's main definition; the supplement does not define the term separately.

**Table D1-c. Standardised hypertension prevalence, 2018 round, by sex × age**

Source: Supplementary Table 4, "Trends in standardised hypertension prevalence, awareness, treatment, and control rates by age group (%)". Footnote: "Results were weighted to the 2010 census population in China." Hypertension is defined as ≥140/90 mmHg or receiving antihypertensive drugs.

| Age (y) | Men, % (95% CI) | Women, % (95% CI) |
|---|---|---|
| 18–29 | 13.3 (11.2–15.3) | 4.0 (2.9–5.1) |
| 30–39 | 20.4 (18.4–22.3) | 8.4 (6.8–10.1) |
| 40–49 | 31.8 (30.2–33.3) | 20.8 (19.4–22.2) |
| 50–59 | 46.5 (44.3–48.8) | 40.9 (39.4–42.4) |
| 60–69 | 55.3 (53.3–57.2) | 54.6 (53.0–56.3) |

These estimates differ slightly from Table D1-a. The analytic sample (18–69 y), the standardisation and the treatment definition all differ between the two papers. For a model that also covers people aged 70 and over, use D1-a.

### D1.3 China Hypertension Survey (CHS) 2012–2015: overall and by-sex figures only

**Citation**
- Wang Z, Chen Z, Zhang L, Wang X, Hao G, Zhang Z, Shao L, Tian Y, Dong Y, Zheng C, Wang J, Zhu M, Weintraub WS, Gao R; China Hypertension Survey Investigators. Status of Hypertension in China: Results From the China Hypertension Survey, 2012–2015. *Circulation* 2018;137(22):2344–2356.
- doi:10.1161/circulationaha.117.032380. PMID 29449338.
- The full text and supplement are paywalled: the ahajournals.org page showed "Get full access to this article" when opened in a browser, and the supplement download returned 403.

**Sample.** 451 755 adults aged ≥18 y in 31 provinces.

- Abstract (verified): "Blood pressure (BP) was measured after resting for 5 minutes by trained staff using a validated oscillometric BP monitor… Overall, 23.2% (≈244.5 million) of the Chinese adult population ≥18 years of age had HTN, and another 41.3% (≈435.3 million) had pre-HTN according to the Chinese guideline."
- Secondary source (JGC 2024, PMC10964013; verified text): "Results from China Hypertension Survey indicated that the mean weighted SBP and DBP were 126.1 mmHg and 76.0 mmHg, respectively.[1] … The weighted blood pressure levels were 128.0/77.8 mmHg for men and 124.2/74.2 mmHg for women."
- JGC Table 2, weighted prevalence: men 24.5% (n = 216 034); women 21.9% (n = 235 721).
- Crude prevalence by age is shown only as a chart (JGC Fig. 1).

**Prevalence by age × sex (CHS Table 2 in the original paper): NOT FOUND (paywalled).** Lead: the *Circulation* full text, or institutional access.

### D1.4 China Kadoorie Biobank baseline 2004–08: width of the SBP distribution (not nationally representative; 10 areas, ages 30–79)

- Lacey B, et al. Age-specific association between blood pressure and vascular and non-vascular chronic diseases in 0·5 million adults in China: a prospective cohort study. *Lancet Glob Health* 2018;6(6):e641–e649. doi:10.1016/s2214-109x(18)30217-1. PMID 29773120. PMCID PMC5960069.
  - Quote: "Overall, mean systolic blood pressure was 130·6 mm Hg (SD 21·0)".
  - Baseline table, all participants (n = 489 125): SBP 130·6 (21·0), DBP 77·7 (11·1).
  - Device: UA-779 (A&D), mean of the last two readings.
  - Verified: true.
- Chen Z, et al. *Int J Epidemiol* 2011;40:1652–1666. PMID 22158673. Quote: "The mean blood pressure was 132/79 mmHg in men and 130/77 mmHg in women." Verified: true.

### D1.5 SD by sex × age: NOT FOUND

Only overall SDs are published for 2018 (CCDRFS 2018: SBP 18.8, DBP 11.2 mmHg). The CKB SDs are SBP 21.0 and DBP 11.1 mmHg.

Partial alternatives:
- CCDRFS 2013 SBP SDs by sex and by age band, not crossed (D1.6).
- CHARLS 2015 smoothed SBP/DBP percentiles by sex at ages 50-100 (Appendix A).

Leads:
- 张梅 et al., CJE 2021, 图1: x±s by sex and by age, shown graphically only.
- Cao X, et al. *Lancet Public Health* 2022;7:e1027–e1040 (doi:10.1016/S2468-2667(22)00232-8, PMID 36462514). It used "age-, sex-, and province-specific mean values" of CCDRFS 2018 SBP, according to Liu Q et al., *Sci Data* 2026 (PMC13234280), Table 2. The appendix was not retrievable here (thelancet.com and ScienceDirect returned 403).
- Cheng X, et al. 卫生研究 (*Wei Sheng Yan Jiu*) 2025;54(2):181–200 (PMID 40355322). It gives P5/P50/P95 percentile curves of SBP/DBP by sex × age from the 2015 China National Nutrition and Health Surveillance (n = 172 989). Abstract only; full text not accessed.

### D1.6 CCDRFS 2013: SBP mean (SD) by sex and by age band (not crossed), verified

- **Source:** Wang L, Gao P, Zhang M, et al. Prevalence and Ethnic Pattern of Diabetes and Prediabetes in China in 2013. *JAMA* 2017;317(24):2515-2523. doi:10.1001/jama.2017.7596. PMID 28655017; PMCID PMC5815077. Table 1, "General Characteristics of the Chinese Adult Population in 2013 (Weighted Data)". The PMC full text was retrieved.
- **Table 1 row, verbatim:** "Systolic blood pressure, mean (SD), mm Hg | 127.85 (20.00) | 125.78 (21.37) | 129.89 (18.33) | 120.53 (15.93) | 130.22 (19.18) | 142.14 (22.38)". The columns are Overall (N = 170 287) | Women (n = 97 551) | Men (n = 72 736) | <40 (n = 35 466) | 40-59 (n = 85 279) | ≥60 (n = 49 542).

| Group | SBP mean (SD), mmHg |
|---|---|
| Overall | 127.85 (20.00) |
| Women | 125.78 (21.37) |
| Men | 129.89 (18.33) |
| <40 y | 120.53 (15.93) |
| 40-59 y | 130.22 (19.18) |
| ≥60 y | 142.14 (22.38) |

Use: these are the only weighted national SDs by sex and by age band that we retrieved. Applying them to the 2018 sex x age means of D1-b is an approximation. DBP is not reported in this table.

### D1.7 TIDE 2015-2017 (31 provinces, n = 75,880): mean BP by sex, verified

- **Source:** Li Y et al. *BMJ* 2020;369:m997. PMID 32345662; PMCID PMC7186854. Table 2.
- **Verbatim:** "Mean systolic blood pressure (95% CI; mm Hg) | 126.3 (124.9 to 127.7) | 129.9 (128.8 to 131.0) | 122.7 (120.9 to 124.4) | 124.1 (122.8 to 125.5) | 128.7 (126.9 to 130.5)" and "Mean diastolic blood pressure 95% CI; mm Hg) | 78.3 (77.2 to 79.5) | 80.7 (79.3 to 82.1) | 76.0 (74.9 to 77.0) | 77.3 (76.0 to 78.6) | 79.5 (77.4 to 81.5)". The column order is Overall | Men | Women | Urban | Rural.
- **Device:** Omron HEM-7430, two seated readings 10 min apart.

### D1 caveats

- CCDRFS is household-based and representative at national and provincial level. It uses an Omron HBP-1300 oscillometric device, a single visit and the mean of readings 2–3. Single-visit prevalence overstates sustained hypertension.
- The 2018 age-specific means (D1-b) cover only 18–69 y. For ≥70 y, only prevalences are available (D1-a).
- CCDRFS and CHS use different devices, years and treatment definitions ("within 2 weeks"). CHS weighted prevalence (23.2%, 2012–15) is lower than CCDRFS 2018 (27.5%).

> **Cross-references.** Appendix A has CHARLS 2015 smoothed SBP/DBP percentiles by sex at ages 50-100. D7-A has the 2014 National Physical Fitness Surveillance mean SBP/DBP by sex x 5-year age, ages 20-69; those are healthy volunteers only, so the values run low.

---

## D2. Blood lipids

**Bottom line**
- The most recent nationally representative lipid data, CCDRFS 2018–19 (n = 178 558), are published openly only as prevalences, by sex and by broad age band. They are not crossed by sex × age, and no means are given (D2.1).
- The most recent open means are from the China Adults Chronic Diseases and Nutrition Surveillance 2015 (CANCDS 2015, n = 179 728; D2.2). That survey gives weighted mean TC, TG, HDL-C, LDL-C and non-HDL-C, with 95% CIs, by sex and by age group separately, not crossed.
- **Means by sex x age from a recent national survey: NOT FOUND (open access).** Leads are in D2.6.
- Partial substitutes:
  - Weighted TC/HDL-C SDs by sex and by age band, not crossed (CCDRFS 2013, D2.7).
  - TC/LDL-C/HDL-C/TG means by sex (TIDE 2015-17, D2.8).

### D2.1 CCDRFS 2018: prevalence of lipid abnormalities

**Official report (verified text)**
- Source: 《中国慢性病及危险因素监测报告2018》 (人民卫生出版社 2021; ISBN 978-7-117-32099-3). 摘要: https://fwdbook.qq.com/read/1053696612/6
- Quotes:
  - "2018年我国18岁及以上居民高胆固醇血症患病率为8.2%，男性（8.4%）和女性（8.0%）接近，18～44岁组（5.5%）、45～59岁组（11.2%）和60岁及以上组（12.7%）逐渐上升，城市（8.1%）和农村（8.3%）接近"
  - "2018年我国18岁及以上居民高低密度脂蛋白胆固醇血症患病率为8.0%，男性（8.1%）和女性（7.8%）差别不大，18～44岁组（5.5%）、45～59岁组（10.6%）和60岁及以上组（12.4%）逐渐上升"
  - "2018年我国18岁及以上居民低高密度脂蛋白胆固醇血症患病率为20.9%，男性（28.9%）高于女性（13.0%），18～44岁组（22.4%）、45～59岁组（20.6%）和60岁及以上组（16.4%）逐渐下降"
  - "2018年我国18岁及以上居民高甘油三酯血症患病率为18.4%，男性（23.6%）高于女性（13.2%），45～59岁组（22.0%）高于18～44岁组（17.1%）和60岁及以上组（17.1%）"

**Table D2-a. CCDRFS 2018 prevalence, % (official report 摘要)**

| Marker | Men | Women | 18–44 y | 45–59 y | ≥60 y | All ≥18 y |
|---|---|---|---|---|---|---|
| High TC | 8.4 | 8.0 | 5.5 | 11.2 | 12.7 | 8.2 |
| High LDL-C | 8.1 | 7.8 | 5.5 | 10.6 | 12.4 | 8.0 |
| Low HDL-C | 28.9 | 13.0 | 22.4 | 20.6 | 16.4 | 20.9 |
| High TG | 23.6 | 13.2 | 17.1 | 22.0 | 17.1 | 18.4 |

**Peer-reviewed paper (verified text)**
- Citation: Zhang M, Peng K, Zhang X, Liu YS, Liu XY, Han GY, Shi Y, Huang ZJ, Li C, Zhao ZP, Wang LM, Li YC. Geographic Variations in the Prevalence, Awareness, Treatment, and Control of Dyslipidemia among Chinese Adults in 2018–2019: A Cross-sectional Study. *Biomed Environ Sci* 2023;36(4):313–323. doi:10.3967/bes2023.037. PMID 37105906. https://www.besjournal.com/en/article/doi/10.3967/bes2023.037
- Sample: n = 178 558 (mean age 55.1 ± 13.8 y).
- Table 1 (standardised to the 2010 census), % (95% CI): high TC 8.2 (7.7–8.7); high LDL-C 8.0 (7.4–8.5); low HDL-C 20.9 (19.9–21.9); high TG 18.4 (17.4–19.3). Overall dyslipidaemia is printed as "38.2 (27.1–39.2)", while the abstract states "The overall prevalence of dyslipidemia was 35.6%". The CI in Table 1 looks like a typesetting error.
- Definitions: "Dyslipidemia was defined as any of the following conditions: TC of ≥ 6.22 mmol/L or LDL-C of ≥ 4.14 mmol/L or HDL-C of < 1.04 mmol/L, or TG of ≥ 2.26 mmol/L or currently under antihyperlipidemic treatment"
- Assay: "Blood samples were obtained in the morning after a 10-h overnight fast… measured using a ROCHE COBAS C702 automated clinical chemistry analyzer"

### D2.2 CANCDS 2015: weighted mean lipids by sex and by age group (separately)

**Citation**
- Song PK, Man QQ, Li H, Pang SJ, Jia SS, Li YQ, He L, Zhao WH, Zhang J. Trends in Lipids Level and Dyslipidemia among Chinese Adults, 2002–2015. *Biomed Environ Sci* 2019;32(8):559–570.
- doi:10.3967/bes2019.074. PMID 31488232.
- PDF: https://www.besjournal.com/fileSWYXYHJKX/journal/article/swyxyhjkx/2019/8/PDF/bes-32-8-559.pdf
- Tables are images: bes-32-8-559-T2.jpg and T3.jpg.

**Survey.** CANCDS 2015, n = 179 728 aged ≥18 y in 302 surveillance sites. The 2002 and 2010 rounds are also in the paper.

**Verified: true** (values read from the published table images).

**Methods (verbatim)**
- "An overnight fasting blood sample was collected… Serum TC, LDL-c, HDL-c, and TG were measured by a Hitachi 7600 automatic biochemical analyzer… with reagents obtained from Wako Pure Chemical Industries"
- "we calculated standardized age and gender values, respectively, based on the 2010 national census data"
- Table note: "The data represented as mean (95% CI)."

**Table D2-b. 2015 weighted means, mmol/L (95% CI)**

Columns are Table 2 (TC, TG, HDL-C, LDL-C) and Table 3 (non-HDL-C).

| Group | TC | TG | HDL-C | LDL-C | non-HDL-C |
|---|---|---|---|---|---|
| Total | 4.63 (4.59–4.67) | 1.47 (1.45–1.50) | 1.26 (1.24–1.27) | 2.87 (2.84–2.90) | 3.37 (3.34–3.40) |
| Male | 4.63 (4.58–4.67) | 1.62 (1.59–1.65) | 1.20 (1.19–1.22) | 2.90 (2.87–2.93) | 3.42 (3.39–3.46) |
| Female | 4.63 (4.59–4.67) | 1.33 (1.30–1.35) | 1.31 (1.30–1.32) | 2.83 (2.80–2.86) | 3.32 (3.29–3.35) |
| Age 18–44 | 4.42 (4.38–4.46) | 1.39 (1.37–1.42) | 1.24 (1.22–1.25) | 2.71 (2.68–2.74) | 3.18 (3.15–3.22) |
| Age 45–54 | 4.84 (4.80–4.88) | 1.62 (1.58–1.65) | 1.27 (1.26–1.29) | 3.03 (3.00–3.06) | 3.56 (3.53–3.60) |
| Age 55–64 | 4.97 (4.94–5.01) | 1.59 (1.55–1.63) | 1.30 (1.28–1.31) | 3.13 (3.10–3.17) | 3.68 (3.65–3.71) |
| Age 65–74 | 4.93 (4.89–4.97) | 1.52 (1.49–1.56) | 1.29 (1.28–1.31) | 3.09 (3.06–3.12) | 3.64 (3.60–3.67) |
| Age ≥75 | 4.87 (4.82–4.93) | 1.45 (1.39–1.51) | 1.29 (1.27–1.31) | 3.04 (2.99–3.08) | 3.58 (3.53–3.63) |

The age rows are labelled "18-, 45-, 55-, 65-, 75-" in the source.

Abstract quote: "The weighted means of TC, TG, and LDL-c significantly increased linearly from 3.93, 1.12, and 2.12 mmol/L in 2002 to 4.59, 1.41, and 2.78 mmol/L in 2010 and then to 4.63, 1.47, and 2.87 mmol/L in 2015, respectively; by contrast, HDL-c levels decreased significantly from 1.30 mmol/L to 1.26 mmol/L over the same period."

### D2.3 CCDRFS 2013–14: national weighted means (abstract only)

- Citation: Zhang M, Deng Q, Wang L, et al. Prevalence of dyslipidemia and achievement of low-density lipoprotein cholesterol targets in Chinese adults: A nationally representative survey of 163,641 adults. *Int J Cardiol* 2018;260:196–203. doi:10.1016/j.ijcard.2017.12.069. PMID 29622441.
- Quote (Europe PMC abstract and publisher page): "Nationally, the population-weighted means of TC, HDL-C, and LDL-C, and median of TG were 4.70, 1.35, 2.88, and 1.49mmol/L, respectively. The prevalence of high TC, high LDL-C, low HDL-C and high TG was 6.9%, 8.1%, 20.4% and 13.8%."
- Verified: true (abstract). The corrigendum (PMID 29759591) only fixes two category labels in Table 1.
- Age-specific and sex-specific means are in the paywalled full text. Liu Q et al., *Sci Data* 2026 (PMC13234280), Table 2, describes them as "National age-specific mean values; national sex-specific mean values". NOT accessed.

### D2.4 CHARLS 2015 (≥45 y): weighted distribution, mean (SD) and percentiles, all participants

**Citation.** Chen X, Crimmins E, Hu PP, et al. Venous Blood-Based Biomarkers in the China Health and Retirement Longitudinal Study: Rationale, Design, and Results From the 2015 Wave. *Am J Epidemiol* 2019;188(11):1871–1877. doi:10.1093/aje/kwz170. PMID 31364691. PMCID PMC6825825.

**Verified: true.** Source table: Table 4, "Descriptive Statistics of Blood-Based Biomarkers in Entire Wave 3 (Weighted)".

**Table D2-c. Weighted distribution, CHARLS 2015, mg/dL**

| Marker | n | Mean (SD) | P5 | P25 | Median | P75 | P95 |
|---|---|---|---|---|---|---|---|
| TC | 12 949 | 185.63 (37.77) | 131.27 | 161.00 | 182.63 | 206.95 | 245.17 |
| HDL-C | 12 949 | 50.70 (11.37) | 34.75 | 42.86 | 49.42 | 57.14 | 70.66 |
| LDL-C | 12 948 | 103.77 (30.34) | 60.23 | 83.40 | 101.93 | 121.24 | 153.67 |
| TG | 12 949 | 146.81 (92.83) | 57.52 | 85.84 | 118.58 | 174.34 | 347.79 |

Caveat: the sample mixes fasting and non-fasting specimens. Quote: "The medians for fasting specimens were 183 mg/dL for total cholesterol, 49 mg/dL for HDL cholesterol, 102 mg/dL for LDL cholesterol, 115 mg/dL for triglyceride". Results are not by sex × age. The same table has HbA1c 5.99 (0.99)% and glucose 104.91 (36.64) mg/dL, which may help D3.

### D2.5 China PEACE Million Persons Project 2014–2019 (35–75 y; purposive sample, point-of-care lipids)

- Citation: Lu Y, et al. Prevalence of Dyslipidemia and Availability of Lipid-Lowering Medications Among Primary Health Care Settings in China. *JAMA Netw Open* 2021;4(9):e2127573. doi:10.1001/jamanetworkopen.2021.27573. PMID 34586366. PMCID PMC8482054.
- Sample: n = 2 314 538.
- Measurement: "a rapid lipid analyzer using whole blood samples (CardioChek PA Analyzer…)", with LDL-C calculated by Friedewald.
- **Table D2-d. Prevalence, % (95% CI), from Table 2:**

| Group | Overall dyslipidaemia | LDL-C ≥160 mg/dL |
|---|---|---|
| 35–44 y | 29.95 (29.79–30.10) | 1.75 (1.70–1.79) |
| 45–54 y | 32.69 | 3.40 |
| 55–64 y | 34.10 | 5.01 |
| 65–75 y | 31.86 | 4.73 |
| Men | 36.67 | 2.62 |
| Women | 29.80 | 4.84 |

- Verified: true. Not nationally representative ("purposeful, rather than random, sampling strategy").

### D2.6 NOT FOUND, and leads, for lipid means (and SDs) by sex × age

- 《中国慢性病及危险因素监测报告2018》, 第二章第三节 "主要慢性病患病情况": app-only on QQ阅读; print edition ISBN 978-7-117-32099-3.
- Zhang M et al., *Int J Cardiol* 2018 (CCDRFS 2013–14), full text.
- Yang W, et al. Serum lipids and lipoproteins in Chinese men and women. *Circulation* 2012;125(18):2212–2221 (doi:10.1161/circulationaha.111.065904, PMID 22492668). Its title suggests sex-specific (and possibly age-specific) means, but we could not confirm which survey it uses or what its tables contain. It is paywalled; the browser showed "Get full access".
- Li F, et al. 卫生研究 2025;54(1):60–66 (PMID 39943650). Remnant cholesterol only, CNHS 2015–17.

### D2.7 CCDRFS 2013: TC and HDL-C mean (SD) by sex and by age band (not crossed), verified

- **Source:** Wang L et al. *JAMA* 2017;317(24):2515-2523 (citation in D1.6). Table 1, "Laboratory findings, mean (SD)" (weighted).
- **Verbatim:** "Total cholesterol, mg/dL | 181.6 (39.1) | 181.1 (39.4) | 182.1 (38.9) | 172.7 (37.5) | 187.7 (38.5) | 192.0 (39.4)" and "HDL cholesterol, mg/dL | 52.3 (14.9) | 54.5 (14.4) | 50.0 (15.0) | 51.5 (14.0) | 52.2 (15.2) | 54.5 (16.0)". The columns are Overall | Women | Men | <40 | 40-59 | ≥60.
- **Unit conversion, verbatim:** "To convert cholesterol, multiply values by 0.0259". The mmol/L column below applies that factor.

| Group | TC mg/dL mean (SD) | TC mmol/L (×0.0259) | HDL-C mg/dL mean (SD) | HDL-C mmol/L (×0.0259) |
|---|---|---|---|---|
| Overall | 181.6 (39.1) | 4.70 (1.01) | 52.3 (14.9) | 1.35 (0.39) |
| Women | 181.1 (39.4) | 4.69 (1.02) | 54.5 (14.4) | 1.41 (0.37) |
| Men | 182.1 (38.9) | 4.72 (1.01) | 50.0 (15.0) | 1.30 (0.39) |
| <40 y | 172.7 (37.5) | 4.47 (0.97) | 51.5 (14.0) | 1.33 (0.36) |
| 40-59 y | 187.7 (38.5) | 4.86 (1.00) | 52.2 (15.2) | 1.35 (0.39) |
| ≥60 y | 192.0 (39.4) | 4.97 (1.02) | 54.5 (16.0) | 1.41 (0.41) |

The mmol/L values are our conversion; the source prints mg/dL. LDL-C and TG are not in this table. These are the only weighted national lipid SDs we retrieved.

### D2.8 TIDE 2015-2017 (31 provinces, n = 75,880): mean lipids by sex, verified

- **Source:** Li Y et al. *BMJ* 2020;369:m997, Table 2, "Laboratory tests (mean (95% CI))".
- **Verbatim:**
  - "Cholesterol (mmol/L) | 4.8 (4.7 to 4.8) | 4.8 (4.8 to 4.9) | 4.8 (4.7 to 4.8)"
  - "Low density lipoprotein (mmol/L) | 2.8 (2.8 to 2.9) | 2.9 (2.8 to 3.0) | 2.8 (2.7 to 2.8)"
  - "High density lipoprotein (mmol/L) | 1.5 (1.5 to 1.5) | 1.4 (1.4 to 1.4) | 1.6 (1.5 to 1.6)"
  - "Triglycerides (mmol/L) | 1.6 (1.5 to 1.6) | 1.8 (1.7 to 1.8) | 1.4 (1.3 to 1.4)"
  - The columns are Overall | Men | Women.

| Marker (mmol/L) | Overall | Men | Women |
|---|---|---|---|
| TC | 4.8 (4.7-4.8) | 4.8 (4.8-4.9) | 4.8 (4.7-4.8) |
| LDL-C | 2.8 (2.8-2.9) | 2.9 (2.8-3.0) | 2.8 (2.7-2.8) |
| HDL-C | 1.5 (1.5-1.5) | 1.4 (1.4-1.4) | 1.6 (1.5-1.6) |
| TG | 1.6 (1.5-1.6) | 1.8 (1.7-1.8) | 1.4 (1.3-1.4) |

### D2 caveats

- Thresholds differ between sources:
  - CCDRFS, CANCDS and China PEACE use Chinese 2016 cut-offs (TC ≥6.22, LDL-C ≥4.14, HDL-C <1.04, TG ≥2.26 mmol/L).
  - CHARLS Table 5 uses US-style cut-offs.
- Assay platforms differ:
  - CCDRFS 2018: Roche Cobas c702, central labs.
  - CANCDS 2015: Hitachi 7600 with Wako reagents.
  - China PEACE: CardioChek point-of-care.
- LDL-C in CANCDS and CCDRFS was measured directly on a chemistry analyser. China PEACE LDL-C was calculated with Friedewald.
- The CANCDS age-group means pool both sexes. Sex × age cells would need microdata or a model.

---

## D3. Glucose, HbA1c, diabetes

### D3.0 Bottom line for the model

| Need | Best verified source | Cells available |
|---|---|---|
| Diabetes / prediabetes prevalence | CCDRFS 2018–19 (Wang L, JAMA 2021) | by sex (all ages) and by 6 age bands (both sexes); **no sex × age cross-tab** |
| Diabetes prevalence, official Chinese figure | 中国慢性病及危险因素监测报告（2018） | by sex; 18–44 / 45–59 / ≥60 |
| FPG and HbA1c **distribution by sex × age** (mean, SE, P5–P95) | CNHS 2015–2017 (Yu D, AJPM Focus 2024, Appendix Tables 2–3) | M/F × 20–39 / 40–59 / ≥60: **the only sex × age cross-tab found** |
| FPG and HbA1c mean **(SD)** | CCDRFS 2013 (Wang L, JAMA 2017, Table 1) | by sex; by <40 / 40–59 / ≥60 |
| Second national survey, ADA criteria | TIDE 2015–2017 (Li Y, BMJ 2020) | by sex; by 6 age bands |

**Sex × age cross-tab of diabetes/prediabetes prevalence: NOT FOUND in an openly readable nationally representative table.** TIDE (BMJ 2020) Fig 1 plots it by sex × 6 age bands, but as bars without numbers. Best leads are the paywalled sources: the CCDRFS 2018 report book (People's Medical Publishing House, 2021; its results chapters are locked on the e-book site), Xu Y et al. JAMA 2013 (2010 survey; the readable part gives sex and age margins only), and Yang W et al. NEJM 2010 (2007–08). The CNHS sex × age FPG/HbA1c percentiles (D3.3) can be used to derive sex × age shares above thresholds if needed.

---

### D3.1 CCDRFS 2013–14 and 2018–19: diabetes and prediabetes prevalence (verified)

- **Survey:** China Chronic Disease and Risk Factors Surveillance (CCDRFS), national and provincial representative, multistage stratified. Fieldwork 2013-06 to 2014-05 (n = 170 287) and 2018-08 to 2019-06 (n = 173 642), adults ≥18 y. Plasma glucose was measured fasting and 2 h after a 75 g OGTT (OGTT only in people without diagnosed diabetes). HbA1c by HPLC on a Bio-Rad D-10 at a central laboratory. Weighted to the 2010 census.
- **Source:** Wang L, Peng W, Zhao Z, Zhang M, Shi Z, Song Z, Zhang X, Li C, Huang Z, Sun X, Wang L, Zhou M, Wu J, Wang Y. *Prevalence and Treatment of Diabetes in China, 2013-2018.* JAMA 2021;326(24):2498-2506. DOI 10.1001/jama.2021.22208; PMID 34962526; PMCID PMC8715349. URL https://pmc.ncbi.nlm.nih.gov/articles/PMC8715349/ (Tables 2 and 3).
- **Verbatim:** "The estimated prevalence of diabetes increased from 10.9% (95% CI, 10.4%-11.5%) in 2013 to 12.4% (95% CI, 11.8%-13.0%) in 2018 (P < .001). The estimated prevalence of prediabetes was 35.7% (95% CI, 34.2%-37.3%) in 2013 and 38.1% (95% CI, 36.4%-39.7%) in 2018 (P = .07)."
- "The prevalence of diabetes increased with age: 5.0% (95% CI, 4.0%-6.1%) for those aged 18 through 29 years and 20.7% (95% CI, 19.1%-22.3%) for those 79 years or older in 2013; 5.0% (95% CI, 3.9%-6.2%) for those aged 18 through 29 years and 27.3% (95% CI, 25.7%-28.9%) for those 70 years or older in 2018 (P < .001)." (The paper's text says "79 years or older" for 2013; the table row is "≥70".)
- **Definitions (verbatim):** "Diabetes was defined as participants with self-reported diabetes diagnosed by a health professional or with a fasting plasma glucose level of 126 mg/dL or greater, a 2-hour plasma glucose level of 200 mg/dL or greater after a 75-g oral glucose challenge, or HbA1c level of 6.5% or greater. Prediabetes was defined as participants who did not have diabetes but who had a fasting plasma glucose of 100 to 125 mg/dL, a 2-hour plasma glucose of 140-199 mg/dL, or HbA1c level of 5.7% to 6.4%."
- **Lab (verbatim):** "Plasma glucose was measured using hexokinase methods according to the protocol at 290 sites and using standardized glucose oxidase in 8 sites, within 24 hours of sample collection... Hemoglobin A1c (HbA1c) was measured using venous blood samples within 4 weeks of blood collection with quantitative high-performance liquid chromatography and the boronate affinity method (Bio-Rad D-10 Hemoglobin Analyzer) at the central laboratory."

**Table D3-1. Weighted diabetes prevalence, % (95% CI), CCDRFS 2018 [2013 for comparison]. JAMA 2021 Table 2. verified = true**

| Group | n 2018 | Diabetes, ADA (FPG, 2-h PG or HbA1c, or self-report) 2018 | same, 2013 | Diabetes, FPG or 2-h PG or self-report 2018 | Self-reported diagnosis 2018 |
|---|---|---|---|---|---|
| All | 173 642 | 12.4 (11.8-13.0) | 10.9 (10.4-11.5) | 11.9 (11.3-12.5) | 4.5 (4.2-4.8) |
| Men | 76 726 | 13.3 (12.6-14.0) | 11.7 (11.0-12.4) | 12.9 (12.2-13.6) | 4.4 (4.0-4.7) |
| Women | 96 916 | 11.5 (10.8-12.2) | 10.2 (9.7-10.7) | 11.0 (10.3-11.6) | 4.7 (4.4-5.1) |
| 18-29 | 9046 | 5.0 (3.9-6.2) | 5.0 (4.0-6.1) | 4.4 (3.4-5.4) | 0.7 (0.3-1.2) |
| 30-39 | 17 173 | 6.5 (5.9-7.1) | 6.9 (6.3-7.6) | 6.3 (5.6-6.9) | 1.5 (1.2-1.8) |
| 40-49 | 31 466 | 11.1 (10.5-11.8) | 10.6 (9.9-11.2) | 10.9 (10.2-11.6) | 3.6 (3.2-4.0) |
| 50-59 | 45 951 | 19.3 (18.4-20.1) | 16.2 (15.5-16.9) | 18.7 (17.9-19.6) | 8.2 (7.7-8.7) |
| 60-69 | 47 291 | 23.9 (22.9-24.9) | 19.8 (18.8-20.7) | 23.3 (22.3-24.3) | 11.2 (10.6-11.9) |
| ≥70 | 22 715 | 27.3 (25.7-28.9) | 20.7 (19.1-22.3) | 26.6 (24.9-28.2) | 12.0 (11.1-13.0) |
| Urban | 70 790 | 13.1 (12.2-14.0) | 12.6 (11.7-13.5) | 12.7 (11.9-13.5) | 5.2 (4.8-5.7) |
| Rural | 102 852 | 11.6 (10.8-12.4) | 9.5 (9.0-10.1) | 11.1 (10.3-12.0) | 3.8 (3.4-4.1) |

The table also has a "Health professional diagnosis of FPG" column. Its footnote reads "Diabetes was defined as participants with a fasting plasma glucose level of 126 mg/dL or greater". 2018 values: All 9.6 (9.1-10.1), Men 10.3 (9.7-10.9), Women 8.9 (8.4-9.5), 18-29 3.5 (2.5-4.4), 30-39 5.0 (4.5-5.6), 40-49 8.7 (8.1-9.3), 50-59 15.9 (15.2-16.6), 60-69 18.9 (18.0-19.8), ≥70 20.2 (18.9-21.5).

**Table D3-2. Weighted prediabetes prevalence, % (95% CI), CCDRFS 2018 [2013]. JAMA 2021 Table 3. verified = true**

| Group | ADA: FPG, 2-h PG or HbA1c, 2018 | same, 2013 | FPG or 2-h PG, 2018 | FPG only, 2018 |
|---|---|---|---|---|
| All | 38.1 (36.4-39.7) | 35.7 (34.2-37.3) | 35.1 (33.3-36.9) | 31.9 (29.9-33.8) |
| Men | 41.2 (39.3-43.0) | 36.4 (34.7-38.1) | 38.1 (36.2-40.0) | 35.1 (33.0-37.1) |
| Women | 34.9 (33.2-36.7) | 35.0 (33.5-36.6) | 32.1 (30.2-34.0) | 28.7 (26.7-30.6) |
| 18-29 | 27.3 (24.6-29.9) | 26.2 (23.9-28.4) | 25.8 (23.0-28.5) | 22.3 (19.7-24.9) |
| 30-39 | 34.2 (32.0-36.4) | 32.1 (30.2-34.1) | 31.8 (29.6-34.0) | 28.2 (25.8-30.6) |
| 40-49 | 40.3 (38.3-42.3) | 37.8 (36.0-39.7) | 37.4 (35.4-39.5) | 34.2 (32.0-36.3) |
| 50-59 | 45.8 (44.4-47.3) | 42.0 (40.4-43.5) | 41.3 (39.6-42.9) | 38.8 (37.0-40.6) |
| 60-69 | 47.6 (46.3-48.9) | 45.2 (43.8-46.6) | 43.1 (41.6-44.6) | 40.5 (38.7-42.4) |
| ≥70 | 48.9 (47.4-50.4) | 46.5 (44.4-48.6) | 44.7 (43.1-46.3) | 40.8 (38.9-42.8) |
| Urban | 36.5 (34.2-38.8) | 34.3 (32.3-36.2) | 33.4 (31.0-35.9) | 30.4 (27.9-33.0) |
| Rural | 39.8 (37.7-41.9) | 37.0 (35.1-38.8) | 36.9 (34.6-39.2) | 33.4 (30.8-35.9) |

---

### D3.2 Official CCDRFS 2018 report (Chinese): diabetes prevalence (verified, summary text)

- **Source:** 中国疾病预防控制中心, 中国疾病预防控制中心慢性非传染性疾病预防控制中心 编著. 《中国慢性病及危险因素监测报告（2018）》. Book: 人民卫生出版社 2021. The EClinicalMedicine 2023 paper below cites it as "Report on chronic disease risk factor surveillance in China 2018. Beijing: People's Medical Publishing House; 2021". The 摘要 (summary) was read on the official e-book edition: https://fwdbook.qq.com/read/1053696612/6 (Chinese) and /7 (English Abstract). The results chapters are locked (app only).
- **Sample (verbatim):** "2018年中国慢性病及危险因素监测报告纳入分析的18岁及以上有效样本为184 509人，其中男性81 918人，占44.4%，女性102 591人，占55.6%……18～44岁、45～59岁、60岁及以上人群的样本量分别为41 213人（22.3%）、68 870人（37.3%）、74 426人（40.3%）。"
- **Verbatim:** "2018年我国18岁及以上居民糖尿病患病率为11.9%，男性（12.9%）高于女性（10.9%），18～44岁组（6.2%）、45～59岁组（16.1%）和60岁及以上组（24.6%）随年龄增长呈上升趋势，城市（12.6%）高于农村（11.1%），东、中、西部地区分别为12.4%、12.8%和10.0%。"

**Table D3-3. Diabetes prevalence (%), CCDRFS 2018 official report. verified = true**

| All | Men | Women | 18–44 | 45–59 | ≥60 | Urban | Rural |
|---|---|---|---|---|---|---|---|
| 11.9 | 12.9 | 10.9 | 6.2 | 16.1 | 24.6 | 12.6 | 11.1 |

The summary does not state the definition. The 11.9% total equals the JAMA 2021 2018 estimate for "FPG or 2-h PG or self-report", that is without HbA1c: 11.9 (11.3-12.5), and men 12.9 match too. This suggests the official figure excludes HbA1c, but that is an inference, not stated in the summary.

---

### D3.3 CNHS 2015–2017: FPG and HbA1c distributions by sex × age (verified). The key cross-tab

- **Survey:** China Nutrition and Health Surveillance 2015–2017 (CNHS), nationally representative, 31 provinces, 571 survey sites. Analysis sample: adults ≥20 y, n = 176 223 (unweighted). Estimates are weighted ("All CNHS analyses used sample weights to adjust for noncoverage and unequal probability of selection").
- **Source:** Yu D, Martin CB, Fryar CD, Hales CM, Eberhardt MS, Carroll MD, Zhao L, Ogden CL. *Prevalence of Diabetes by BMI: China Nutrition and Health Surveillance (2015-2017) and U.S. National Health and Nutrition Examination Survey (2015-2018).* AJPM Focus 2024;3(3):100215. DOI 10.1016/j.focus.2024.100215; PMID 38638940; PMCID PMC11024921. Supplement mmc1.docx: Appendix Table 2 (HbA1c) and Appendix Table 3 (FPG). URL https://pmc.ncbi.nlm.nih.gov/articles/PMC11024921/
- **Lab (verbatim):** "In CNHS, FPG was tested using the glucose oxidase method within 3 hours in the survey site laboratories... Sample participants had venous HbA1c measured by the same laboratory using quantitative high-performance liquid chromatography and the boronate affinity method (Premier Hb9210 Analyzer)."
- **Verbatim:** "Mean HbA1c was 5.0% (SE=0.02) in China, lower than the mean of 5.7% (SE=0.02) in the U.S. Mean FPG was 96.4 mg/dL (SE=0.38) in China... Similar patterns between countries were seen for men and women and each age group."

**Table D3-4. Fasting plasma glucose (mg/dL), CNHS 2015–2017. Appendix Table 3: "Distribution of fasting plasma glucose (mg/dL) among adults 20 and over". verified = true**

| Sex | Age | n | Mean | SE | P5 | P25 | P50 | P75 | P95 |
|---|---|---|---|---|---|---|---|---|---|
| Both | ≥20 total | 176223 | 96.4 | 0.38 | 74.3 | 86.2 | 93.4 | 102.1 | 138.1 |
| Men | total | 81983 | 97.5 | 0.41 | 73.8 | 86.8 | 94.1 | 103.1 | 139.5 |
| Men | 20-39 | 15659 | 92.9 | 0.45 | 70.7 | 83.5 | 90.5 | 97.6 | 115 |
| Men | 40-59 | 37517 | 100.4 | 0.47 | 74 | 86.9 | 94.5 | 103.5 | 140.6 |
| Men | ≥60 | 28807 | 102.3 | 0.54 | 76.1 | 88.4 | 96.1 | 106 | 149.2 |
| Women | total | 94240 | 95.3 | 0.38 | 74.7 | 86 | 92.9 | 101.2 | 136.4 |
| Women | 20-39 | 19810 | 89.6 | 0.4 | 70.9 | 82.1 | 88.2 | 94.1 | 107.1 |
| Women | 40-59 | 45144 | 97.5 | 0.36 | 75.2 | 86.2 | 92.9 | 100.8 | 131.2 |
| Women | ≥60 | 29286 | 104.5 | 0.57 | 78.1 | 89.5 | 96.8 | 107.1 | 158.9 |

**Table D3-5. HbA1c (%), CNHS 2015–2017. Appendix Table 2: "Distribution of HbA1c among adults aged 20 and over". verified = true**

| Sex | Age | n | Mean | SE | P5 | P25 | P50 | P75 | P95 |
|---|---|---|---|---|---|---|---|---|---|
| Both | ≥20 total | 176223 | 5.0 | 0.02 | 4 | 4.5 | 5 | 5.4 | 6.4 |
| Men | total | 81983 | 5.0 | 0.02 | 4.1 | 4.5 | 5 | 5.4 | 6.4 |
| Men | 20-39 | 15659 | 4.8 | 0.02 | 4 | 4.4 | 4.8 | 5.2 | 5.7 |
| Men | 40-59 | 37517 | 5.1 | 0.02 | 4.1 | 4.5 | 5 | 5.4 | 6.4 |
| Men | ≥60 | 28807 | 5.2 | 0.03 | 4.1 | 4.6 | 5.1 | 5.5 | 6.7 |
| Women | total | 94240 | 4.9 | 0.02 | 4 | 4.5 | 5 | 5.4 | 6.4 |
| Women | 20-39 | 19810 | 4.7 | 0.02 | 3.9 | 4.3 | 4.7 | 5.1 | 5.6 |
| Women | 40-59 | 45144 | 5.0 | 0.02 | 4.1 | 4.5 | 5 | 5.4 | 6.3 |
| Women | ≥60 | 29286 | 5.3 | 0.03 | 4.2 | 4.7 | 5.2 | 5.6 | 7.2 |

**CNHS diabetes prevalence (main-text Table 2; verified = true).** The definition is self-report, or FPG ≥126 mg/dL, or HbA1c ≥6.5%, with no OGTT. Total and sex rows are age-adjusted to the US 2000 projected population (20–39 / 40–59 / ≥60).
- Total 7.8 (7.4, 8.3); crude 9.6 (9.4, 9.7).
- Men 8.2 (7.7, 8.7); Women 7.4 (7.0, 7.9).
- 20–39: 3.1 (2.7, 3.4); 40–59: 8.7 (8.2, 9.2); ≥60: 14.6 (13.6, 15.5).

**Caveat.** CNHS HbA1c (Premier Hb9210; mean 5.0%) runs about 0.4–0.6 percentage points below CCDRFS 2013 (Bio-Rad D-10; 5.38%) and TIDE (Bio-Rad Variant II; 5.6%). Diabetes prevalence is also lower in CNHS (no OGTT). Inter-assay differences matter when a user's HbA1c is placed on a population distribution.

---

### D3.4 CCDRFS 2013: FPG and HbA1c mean (SD) by sex and by age (verified)

- **Source:** Wang L, Gao P, Zhang M, Huang Z, Zhang D, Deng Q, Li Y, Zhao Z, Qin X, Jin D, Zhou M, Tang X, Hu Y, Wang L. *Prevalence and Ethnic Pattern of Diabetes and Prediabetes in China in 2013.* JAMA 2017;317(24):2515-2523. DOI 10.1001/jama.2017.7596; PMID 28655017; PMCID PMC5815077. Table 1 is "General Characteristics of the Chinese Adult Population in 2013 (Weighted Data)". URL https://pmc.ncbi.nlm.nih.gov/articles/PMC5815077/
- **Lab (verbatim):** "HbA1c was directly measured from venous blood samples in the 2013 survey in a single laboratory using quantitative high-performance liquid chromatography and the boronate affinity method (Bio-Rad D-10 Hemoglobin Analyzer)."

**Table D3-6. Mean (SD), CCDRFS 2013 (weighted). JAMA 2017 Table 1. verified = true**

| Measure | Overall (n=170 287) | Women (n=97 551) | Men (n=72 736) | <40 (n=35 466) | 40-59 (n=85 279) | ≥60 (n=49 542) |
|---|---|---|---|---|---|---|
| Fasting plasma glucose, mg/dL | 100.5 (26.1) | 99.8 (25.0) | 101.4 (27.0) | 96.2 (21.1) | 103.2 (28.8) | 106.3 (29.4) |
| 2-h plasma glucose, mg/dL | 114.2 (44.0) | 115.5 (42.2) | 113.0 (45.6) | 106.7 (36.2) | 116.6 (46.8) | 130.1 (51.7) |
| HbA1c, % | 5.38 (0.83) | 5.38 (0.83) | 5.38 (0.84) | 5.19 (0.66) | 5.47 (0.90) | 5.68 (0.96) |
| BMI, kg/m² | 24.0 (3.72) | 24.0 (3.79) | 24.1 (3.65) | 23.5 (3.84) | 24.7 (3.49) | 23.9 (3.65) |
| Age, y | 43.5 (16.2) | 43.7 (16.3) | 43.3 (16.0) | 29.2 (6.4) | 49.0 (5.7) | 69.7 (7.1) |

**JAMA 2017 Table 2 (weighted prevalence, %, 2010 ADA criteria; verified = true):**

| Group | Total diabetes | Prediabetes |
|---|---|---|
| Overall | 10.9 (10.4-11.5) | 35.7 (34.1-37.4) |
| <40 | 5.9 (5.1-6.6) | 28.8 (26.8-30.9) |
| 40-59 | 12.9 (12.3-13.5) | 39.5 (37.8-41.2) |
| ≥60 | 20.2 (19.1-21.2) | 45.8 (44.3-47.2) |
| Women | 10.2 (9.7-10.7) | 35.0 (33.4-36.7) |
| Men | 11.7 (10.9-12.4) | 36.4 (34.6-38.2) |

Unit note (JAMA): "To convert glucose from mg/dL to mmol/L, multiply by 0.0555".

---

### D3.5 TIDE 2015–2017: ADA and WHO prevalence; means by sex (verified)

- **Survey:** Thyroid disorders, Iodine status and Diabetes Epidemiological survey (TIDE), 31 provinces, 2015–2017. n = 75 880 adults ≥18 y. Response rate 92.1%. Measures: OGTT plus HbA1c (Bio-Rad VARIANT II). Weighted to the 2010 census.
- **Source:** Li Y, Teng D, Shi X, Qin G, Qin Y, Quan H, Shi B, Sun H, Ba J, Chen B, Du J, He L, Lai X, Li Y, Chi H, Liao E, Liu C, Liu L, Tang X, Tong N, Wang G, Zhang JA, Wang Y, Xue Y, Yan L, Yang J, Yang L, et al. *Prevalence of diabetes recorded in mainland China using 2018 diagnostic criteria from the American Diabetes Association: national cross sectional study.* BMJ 2020;369:m997. DOI 10.1136/bmj.m997; PMID 32345662; PMCID PMC7186854.
- **Verbatim:** "The weighted prevalence of total diabetes (n=9772), self-reported diabetes (n=4464), newly diagnosed diabetes (n=5308), and prediabetes (n=27 230) diagnosed by the ADA criteria were 12.8% (95% confidence interval 12.0% to 13.6%), 6.0% (5.4% to 6.7%), 6.8% (6.1% to 7.4%), and 35.2% (33.5% to 37.0%), respectively". Also: "The prevalence of total diabetes and prediabetes increased with age in both men and women and increased more sharply after age 50 (table 3 and fig 1)."

**Table D3-7. "Age and sex standardised prevalence", % (95% CI). BMJ 2020 Table 3. verified = true**

| Group | n | Self-reported | Total diabetes, WHO (self-report, FPG ≥7.0 or 2hPG ≥11.1) | Total diabetes, ADA (adds HbA1c ≥6.5%) | Prediabetes (ADA) |
|---|---|---|---|---|---|
| Overall | 75 880 | 6.0 (5.4-6.7) | 11.2 (10.5-11.9) | 12.8 (12.0-13.6) | 35.2 (33.5-37.0) |
| Men | 36 819 | 6.4 (5.6-7.2) | 12.1 (11.3-13.0) | 13.7 (12.8-14.7) | 37.0 (35.2-38.9) |
| Women | 39 061 | 5.6 (5.1-6.2) | 10.3 (9.5-11.1) | 11.8 (10.9-12.7) | 33.4 (31.6-35.3) |
| 18-29 | 17 873 | 0.8 (0.5-1.2) | 1.5 (1.0-2.1) | 2.0 (1.5-2.7) | 20.2 (18.2-22.40) |
| 30-39 | 15 082 | 2.6 (2.1-3.2) | 5.4 (4.6-6.3) | 6.3 (5.4-7.3) | 29.9 (27.4-32.5) |
| 40-49 | 16 686 | 4.8 (4.1-5.7) | 10.6 (9.6-11.6) | 12.1 (11.1-13.3) | 40.0 (38.0-41.9) |
| 50-59 | 12 736 | 10.6 (9.6-11.7) | 18.9 (17.8-20.1) | 21.1 (19.8-22.6) | 47.1 (44.9-49.4) |
| 60-69 | 8205 | 14.9 (12.8-17.3) | 25.5 (23.3-27.9) | 28.8 (26.5-31.3) | 47.8 (45.0-50.6) |
| ≥70 | 5298 | 16.5 (13.8-19.5) | 28.8 (25.7-32.1) | 31.8 (28.8-35.1) | 47.6 (44.3-51.0) |

"22.40" is printed as such in the source.

TIDE supplementary Table 2 (verified = true) gives isolated IFG (WHO) / IGT (WHO) by age:
- 18-29: 0.9 / 4.1
- 30-39: 1.7 / 8.7
- 40-49: 2.9 / 13.2
- 50-59: 3.9 / 15.9
- 60-69: 3.8 / 19.1
- ≥70: 3.1 / 21.5
- Men: 3.0 / 11.2; Women: 1.8 / 11.9

**TIDE Table 2: means (95% CI) by sex. verified = true**

| Measure | Overall | Men | Women |
|---|---|---|---|
| FPG, mmol/L | 5.4 (5.4-5.5) | 5.5 (5.4-5.6) | 5.3 (5.3-5.4) |
| 2-h PG, mmol/L | 6.5 (6.4-6.6) | 6.5 (6.4-6.6) | 6.5 (6.4-6.6) |
| HbA1c, % | 5.6 (5.4-5.7) | 5.6 (5.5-5.7) | 5.5 (5.4-5.6) |

Sex × age is shown only in BMJ Fig 1 (bars, no numeric labels). Not transcribed.

**D3 caveats.**
1. The surveys differ in criteria (ADA with HbA1c vs WHO OGTT-only vs FPG/HbA1c without OGTT), so prevalence ranges from 7.8% (CNHS, age-adjusted to the US population) to 12.8% (TIDE).
2. All prevalence figures rest on a single measurement, with no confirmatory repeat.
3. HbA1c assays differ across surveys (Bio-Rad D-10, Bio-Rad Variant II, Premier Hb9210), and so do mean levels (5.0–5.6%).
4. CCDRFS 2018 age bands are crude (unstandardised within band). The JAMA 2021 sex rows are weighted, not age-standardised.

---

## D4. BMI and waist circumference

### D4.0 Bottom line for the model

| Need | Best verified source |
|---|---|
| BMI distribution by sex × age (mean, SE, P5–P95) | CNHS 2015–2017 (AJPM Focus 2024, Appendix Table 1): M/F × 20–39/40–59/≥60 |
| BMI SD | CCDRFS 2013 (JAMA 2017): SD 3.65 men, 3.79 women; 3.49–3.84 by age. CNHS 2015: SD 3.8 both sexes |
| Waist by sex × age (10-y bands, with 95% CI) | CNHS 2015 (Nan J, BES 2025): 18–29 … ≥70 |
| Waist by sex × 5-y age, newest | 第六次国民体质监测 2025 (附表2-1, 3-1); 第五次 2020 (表2, 表3). Fitness-monitoring sample, see caveat |
| Waist SD | CNHS 2015 (Nutrients 2026, Table 1): men 84.7 (10.4), women 81.3 (10.1) cm |
| Overweight/obesity (Chinese cut-offs) by sex × age | CCDRFS 2018, via Song S et al., EClinicalMedicine 2023, Table S4: sex × 18–44/45–59/≥60 × urban/rural |
| Central obesity | CCDRFS 2018 report: by sex; by 3 age bands. CNHS 2015: by sex; by 6 age bands. No sex × age cross-tab found |

**Chinese criteria as defined in the sources:**
- 国民体质监测公报 2020 (注[8]): "BMI＜18.5为“低体重”，18.5≤BMI＜24.0为“体重正常”，24.0≤BMI＜28.0为“超重”，BMI≥28.0为“肥胖”".
- Nutrients 2024 / BES 2025: "According to the criteria of Weight for Adults promulgated by China in 2013, pre-central obesity was defined as 80 ≤ WC < 85 cm for female and 85 ≤ WC < 90 cm for male, central obesity was defined as WC ≥ 85 cm for female and WC ≥ 90 cm for male."
- JAMA 2021: "Central obesity was defined as waist circumference of 90 cm or greater for men and 85 cm or greater for women."
- Note: TIDE (BMJ 2020) used WC ≥90/≥80 and WHO BMI cut-offs, so it is not comparable.

---

### D4.1 CNHS 2015–2017: BMI distribution by sex × age (verified)

- Source as in D3.3 (Yu D et al., AJPM Focus 2024; PMID 38638940; DOI 10.1016/j.focus.2024.100215). Supplement Appendix Table 1: "Distribution of body mass index among adults 20 and over, China 2015-2017 and United States 2015-2018". Height measured by stadiometer; weight by beam scale, light clothing.

**Table D4-1. BMI (kg/m²), CNHS 2015–2017, weighted. verified = true**

| Sex | Age | n | Mean | SE | P5 | P25 | P50 | P75 | P95 |
|---|---|---|---|---|---|---|---|---|---|
| Both | ≥20 total | 176223 | 24.1 | 0.07 | 18.9 | 21.7 | 24 | 26.5 | 30.5 |
| Men | total | 81983 | 24.3 | 0.08 | 18.9 | 21.6 | 23.9 | 26.4 | 30.2 |
| Men | 20-39 | 15659 | 24.1 | 0.15 | 18.6 | 21.4 | 23.9 | 26.7 | 31.1 |
| Men | 40-59 | 37517 | 24.7 | 0.06 | 19.4 | 22.1 | 24.3 | 26.6 | 30.4 |
| Men | ≥60 | 28807 | 23.8 | 0.09 | 18.6 | 21.2 | 23.5 | 25.9 | 29.6 |
| Women | total | 94240 | 23.9 | 0.07 | 18.9 | 21.7 | 24 | 26.5 | 30.8 |
| Women | 20-39 | 19810 | 23.1 | 0.08 | 18.2 | 20.5 | 22.7 | 25.2 | 30.3 |
| Women | 40-59 | 45144 | 24.7 | 0.06 | 19.5 | 22.2 | 24.4 | 26.8 | 31 |
| Women | ≥60 | 29286 | 24.2 | 0.09 | 18.6 | 21.8 | 24.1 | 26.7 | 30.8 |

### D4.2 CCDRFS 2013: BMI mean (SD) by sex and by age (verified)

From JAMA 2017 Table 1 (see D3.4):

| Overall | Women | Men | <40 | 40–59 | ≥60 |
|---|---|---|---|---|---|
| 24.0 (3.72) | 24.0 (3.79) | 24.1 (3.65) | 23.5 (3.84) | 24.7 (3.49) | 23.9 (3.65) |

### D4.3 CCDRFS 2004–2018: standardised mean BMI and Chinese-cut-off prevalence by sex (verified)

- **Source:** Wang L, Zhou B, Zhao Z, Yang L, Zhang M, Jiang Y, Li Y, Zhou M, Wang L, Huang Z, Zhang X, Zhao L, Yu D, Li C, Ezzati M, Chen Z, Wu J, Ding G, Li X. *Body-mass index and obesity in urban and rural China: findings from consecutive nationally representative surveys during 2004-18.* Lancet 2021;398(10294):53-63. DOI 10.1016/s0140-6736(21)00798-4; PMID 34217401; PMCID PMC7617101. Appendix Tables 1 and 3 (Europe PMC author-manuscript supplement).
- Ages **18–69 only**, standardised to the 2010 census. 2018 survey: 184 876 participants; analysed n = 155 413.
- **Verbatim:** "Overall the standardised mean BMI levels rose from 22.7 (95% CI: 22.5-22.9) kg/m2 in 2004 to 24.4 (24.3-24.6) kg/m2 in 2018 (Appendix Table 1)". "In both sexes the lowest mean BMI was in those aged 18-29 years (Figure 2)... among men there was a more complex pattern, with middle-aged men (30-49 years) having the highest mean BMI and prevalence of obesity at each survey".

**Table D4-2. 2018, standardised, 18–69 y (Appendix Tables 1 and 3). verified = true**

| Sex | Mean BMI (95% CI) | Urban | Rural | Obesity ≥28 (Chinese) | BMI ≥24 (Chinese; includes obesity) | Obesity ≥30 (WHO) |
|---|---|---|---|---|---|---|
| Men | 24.7 (24.6, 24.9) | 25.1 (24.8, 25.3) | 24.5 (24.3, 24.7) | 18.8 (17.6, 20.0) | 55.2 (53.4, 56.9) | 9.0 (8.3, 9.7) |
| Women | 24.1 (24.0, 24.2) | 23.9 (23.6, 24.1) | 24.3 (24.1, 24.5) | 14.8 (13.9, 15.8) | 47.1 (45.4, 48.8) | 7.2 (6.7, 7.8) |
| Both | 24.4 (24.3, 24.6) | 24.5 (24.3, 24.7) | 24.4 (24.2, 24.5) | 16.8 (15.9, 17.8) | 51.2 (49.7, 52.7) | 8.1 (7.6, 8.7) |

Mean BMI by sex × age (18–29 … 60–69) × urban/rural is shown only graphically (Figure 2). Not transcribed.

---

### D4.4 CNHS 2015: waist circumference by sex × age (verified)

- **Survey:** CNHS 2015–2017, adult component (China Adult Chronic Disease and Nutrition Surveillance 2015), 31 provinces. n = 145 298 adults ≥18 y (67 535 men, 77 763 women). Weighted ("PROC SURVEYMEANS... weight derived from the data published by the China National Bureau of Statistics in 2010").
- **Protocol (verbatim):** "WC measurement followed the WHO suggestions, measuring at the midway point between the superior border of the iliac crest and the lowest rib, using a flexible tape of 1.5 meters in length, 1 cm in width, and 0.1 cm in minimum scale."
- **Source:** Nan J, Chen ML, Yuan HT, Cao QY, Yu DM, Piao W, Li FS, Yang YX, Zhao LY, Cai SY. *Waist Circumference Status and Distribution in Chinese Adults: China Nutrition and Health Surveillance (2015-2017).* Biomed Environ Sci 2025;38(6):757-762. DOI 10.3967/bes2025.059; PMID 40616491. URL https://www.besjournal.com/en/article/doi/10.3967/bes2025.059 (Table 2).
- **Verbatim:** "The standardized average WC of adults aged 18 years or older in China was 82.21 ± 0.23 cm, of which 84.68 ± 0.27 cm for males, 79.71 ± 0.24 cm for females."

**Table D4-3. Mean waist circumference, cm (95% CI), CNHS 2015. BES 2025 Table 2. verified = true**

| Age | Men | Women | Total |
|---|---|---|---|
| All ≥18 | 84.68 (84.15, 85.21) | 79.71 (79.25, 80.18) | 82.21 (81.75, 82.66) |
| 18– | 81.48 (80.61, 82.34) | 75.33 (74.68, 75.98) | 78.42 (77.73, 79.11) |
| 30– | 85.48 (84.44, 86.52) | 78.29 (77.64, 78.94) | 81.93 (81.16, 82.69) |
| 40– | 86.58 (86.15, 87.02) | 80.87 (80.50, 81.25) | 83.76 (83.40, 84.11) |
| 50– | 85.75 (85.29, 86.22) | 83.22 (82.79, 83.64) | 84.50 (84.12, 84.87) |
| 60– | 84.95 (84.37, 85.54) | 83.65 (83.19, 84.11) | 84.31 (83.83, 84.78) |
| ≥70 | 84.26 (83.51, 85.01) | 82.11 (81.30, 82.92) | 83.12 (82.45, 83.78) |

**SD (by sex only).** Wang Z, Du W, Wei X, Li S, Zhang J, Ju L, Gong W, Guo Q, Xu X, Cheng X, Xing Y, Wang H. *Clinical Obesity Among Chinese Adults: Prevalence, Multimorbidity Burden, and Associations with Physical Activity.* Nutrients 2026;18(6):983. DOI 10.3390/nu18060983; PMID 41901157; PMCID PMC13029350. Table 1, CNHS 2015, 18–79 y, n = 180 480. Values are mean (SD) and appear unweighted. verified = true.
- WC (cm): overall 82.9 (10.4), men 84.7 (10.4), women 81.3 (10.1).
- BMI: 24.3 (3.8), 24.2 (3.8), 24.3 (3.8).
- Chinese BMI categories (n, %): 24.0–27.9: 35.2% overall (men 35.7, women 34.7); ≥28: 14.6% (13.9, 15.3).

### D4.5 National Physical Fitness Surveillance 2020 and 2025: waist by sex × 5-year age (verified from the official table images)

- **2025 (第六次全国国民体质监测公报, released 2025-12-28, 国家体育总局群众体育司).** URL https://www.sport.gov.cn/n315/n20001395/c29322125/content.html. Images part/29323208.jpg (附表2-1, adults) and part/29323210.jpg (附表3-1, older adults).
- **Verbatim (bulletin page image 1):** "本次监测对象为3～6岁幼儿、20～59岁成年人、60～79岁老年人，采用多阶段分层整群随机抽样的方法，于2025年3月至6月从我国大陆31个省（区、市）的108个市（区、县）中抽取1815个幼儿园、机关、企事业单位、社区与行政村，最终纳入有效样本243585人，其中幼儿47523人、成年人147287人、老年人48775人。"
- **2020 (第五次国民体质监测公报).** URL https://www.gov.cn/guoqing/2023-03/12/content_5745851.htm. 表2 = W020230404135669942570.jpg; 表3 = W020230404135670159343.jpg.
- **Verbatim:** "于2020年8月至12月从全国1732个机关、企事业单位、学校、幼儿园及行政村中抽取监测对象，获得有效样本202123人，其中幼儿40222人、成年人121928人、老年人39973人".

**Table D4-4. Mean waist (cm), height (cm), weight (kg), body fat (%). 附表2-1/3-1 (2025) and 表2/表3 (2020). verified = true (read from images, digits checked on enlarged crops)**

| Sex | Age | WC 2025 | WC 2020 | Height 2025 | Weight 2025 | Body fat % 2025 | Height 2020 | Weight 2020 | Body fat % 2020 |
|---|---|---|---|---|---|---|---|---|---|
| M | 20-24 | 82.9 | 82.4 | 173.7 | 72.2 | 21.4 | 172.6 | 70.4 | 20.2 |
| M | 25-29 | 85.7 | 85.3 | 173.1 | 74.7 | 23.7 | 172.1 | 72.8 | 22.5 |
| M | 30-34 | 87.3 | 87.6 | 172.0 | 75.1 | 24.5 | 171.4 | 74.3 | 23.7 |
| M | 35-39 | 87.8 | 88.5 | 171.4 | 74.9 | 24.6 | 170.4 | 74.0 | 23.9 |
| M | 40-44 | 88.5 | 89.0 | 170.4 | 74.3 | 24.7 | 169.4 | 73.2 | 23.9 |
| M | 45-49 | 88.8 | 89.3 | 169.4 | 73.2 | 24.5 | 168.7 | 72.5 | 23.9 |
| M | 50-54 | 88.8 | 89.5 | 168.4 | 72.1 | 24.3 | 167.9 | 71.6 | 23.8 |
| M | 55-59 | 88.9 | 89.8 | 167.8 | 70.9 | 24.0 | 167.5 | 71.0 | 23.8 |
| M | 60-64 | 88.7 | 89.3 | 166.6 | 69.5 | 24.0 | 165.9 | 69.0 | 23.3 |
| M | 65-69 | 87.9 | 89.3 | 165.7 | 67.7 | 23.6 | 165.4 | 68.1 | 23.3 |
| M | 70-74 | 87.9 | 88.7 | 165.3 | 67.1 | 23.6 | 164.6 | 66.7 | 23.1 |
| M | 75-79 | 87.5 | 88.2 | 164.9 | 66.2 | 23.5 | 164.2 | 65.6 | 23.0 |
| F | 20-24 | 72.9 | 72.8 | 161.9 | 57.2 | 26.7 | 160.6 | 55.7 | 24.9 |
| F | 25-29 | 74.0 | 74.4 | 161.0 | 58.2 | 28.7 | 159.8 | 56.7 | 26.5 |
| F | 30-34 | 75.8 | 76.5 | 160.1 | 59.1 | 29.8 | 159.1 | 58.0 | 28.1 |
| F | 35-39 | 77.1 | 78.3 | 159.3 | 59.9 | 30.7 | 158.6 | 59.1 | 29.1 |
| F | 40-44 | 78.5 | 79.3 | 158.9 | 60.6 | 31.4 | 158.0 | 59.7 | 29.9 |
| F | 45-49 | 79.4 | 80.4 | 158.2 | 60.7 | 32.0 | 157.5 | 60.1 | 30.7 |
| F | 50-54 | 80.4 | 82.2 | 157.7 | 60.6 | 32.3 | 157.2 | 60.8 | 31.6 |
| F | 55-59 | 81.6 | 83.7 | 157.4 | 60.5 | 32.7 | 157.0 | 60.7 | 31.9 |
| F | 60-64 | 83.5 | 85.5 | 156.3 | 60.5 | 33.4 | 155.1 | 60.3 | 32.9 |
| F | 65-69 | 84.1 | 86.4 | 155.2 | 59.7 | 33.7 | 154.4 | 59.8 | 33.0 |
| F | 70-74 | 84.9 | 86.8 | 154.6 | 59.1 | 33.7 | 153.4 | 58.9 | 33.0 |
| F | 75-79 | 84.9 | 86.2 | 154.6 | 58.3 | 33.1 | 153.3 | 57.9 | 32.6 |

**2020 overweight/obesity (Chinese cut-offs), verbatim:** "2020年成年人超重率、肥胖率分别为35.0%和14.6%，较2014年分别增长了2.3和4.1个百分点；2020年老年人超重率、肥胖率分别为41.7%和16.7%，较2014年分别增加了0.1和2.8个百分点。" verified = true. Here 成年人 = 20–59 and 老年人 = 60–79. By sex × age only in 图7 (chart, no numbers).

The 2025 bulletin's overweight/obesity rates were NOT FOUND in the readable pages; two page images returned HTTP 403.

**Caveats for 国民体质监测.**
1. The sampling frame is institutions, workplaces and villages (机关、企事业单位、学校、幼儿园及行政村 / 社区), not households.
2. Values are means only (no SD or percentiles in the bulletins). Mean BMI cannot be derived from mean height and weight.
3. Participants must complete a physical test battery. The 2014 bulletin restricted participants to healthy people (footnote [1], quoted verbatim in D7-A). The 2020/2025 bulletins state no health criterion (D8.3). The tables may therefore under-represent sick or frail people.
4. CCDRFS/CNHS should remain the primary anchor.

---

### D4.6 Overweight and obesity prevalence (Chinese cut-offs) by sex × age: CCDRFS 2018 (verified, secondary publication of report data)

- **Source:** Song S, Lei L, Liu H, Yang F, Li N, Chen W, Peng J, Ren J. *Impact of changing the prevalence of smoking, alcohol consumption and overweight/obesity on cancer incidence in China from 2021 to 2050: a simulation modelling study.* EClinicalMedicine 2023;63:102163. DOI 10.1016/j.eclinm.2023.102163; PMID 37662518; PMCID PMC10468350. Supplementary (mmc1.docx) Table S4, citing "Chinese Center for Disease Control and Prevention, Report on chronic disease risk factor surveillance in China 2018. Beijing: People's Medical Publishing House, 2021".
- **Verbatim:** "The age-, area (urban/rural)- and sex-specific prevalence of smoking, alcohol use and overweight/obesity in Chinese adults (population aged 18+ years) was obtained from China Chronic Disease and Risk Factor Surveillance (CCDRFS) in 2018... BMI was categorized as low weight (<18.50 kg/m2), normal weight (18.5–23.9 kg/m2), overweight (24.0–27.9 kg/m2) and obesity (≥28.0 kg/m2)... Our study combined low weight and normal weight into one group called normal body weight."

**Table D4-5. Table S4, "Prevalence (%) of normal body weight, overweight and obesity in the China population aged 18+ years in 2018". verified = true**

| Residence × sex | Age | Normal (incl. underweight) | Overweight 24.0–27.9 | Obesity ≥28.0 |
|---|---|---|---|---|
| Urban men | 18-44 | 42.4 | 34.5 | 23.1 |
| Urban men | 45-59 | 36.4 | 43.9 | 19.7 |
| Urban men | 60+ | 44.9 | 41.0 | 14.1 |
| Urban women | 18-44 | 62.9 | 25.5 | 11.6 |
| Urban women | 45-59 | 42.8 | 39.8 | 17.4 |
| Urban women | 60+ | 41.6 | 40.1 | 18.3 |
| Rural men | 18-44 | 51.1 | 32.5 | 16.4 |
| Rural men | 45-59 | 43.2 | 40.0 | 16.8 |
| Rural men | 60+ | 59.2 | 31.8 | 9.0 |
| Rural women | 18-44 | 56.7 | 29.2 | 14.1 |
| Rural women | 45-59 | 38.2 | 42.5 | 19.3 |
| Rural women | 60+ | 50.7 | 35.2 | 14.1 |

There is no national (urban + rural combined) sex × age row. Combining requires urban/rural weights by sex and age, which the source does not give. It is not computed here.

### D4.7 CCDRFS 2018: official report and JAMA 2021, by sex and by age band (verified)

**Official report (Chinese summary, https://fwdbook.qq.com/read/1053696612/6), verbatim:**
- "2018年我国18岁及以上居民超重率为34.3%，男性（36.1%）高于女性（32.5%），45～59岁组（41.6%）高于18～44岁组（30.4%）和60岁及以上组（36.6%），城市（34.4%）和农村（34.2%）相近".
- "2018年我国18岁及以上居民肥胖率为16.4%，男性（18.2%）高于女性（14.7%），45～59岁组（18.3%）高于18～44岁组（16.4%）和60岁及以上组（13.6%）".
- "2018年我国18岁及以上居民中心型肥胖率为35.2%，男性（37.2%）高于女性（33.3%），45～59岁组（42.7%）高于18～44岁组（30.0%）和60岁及以上组（41.5%），城市（36.4%）高于农村（34.0%）".

**Table D4-6. CCDRFS 2018 official report, prevalence %. verified = true**

| Measure | All | Men | Women | 18–44 | 45–59 | ≥60 | Urban | Rural |
|---|---|---|---|---|---|---|---|---|
| Overweight (24.0–27.9) | 34.3 | 36.1 | 32.5 | 30.4 | 41.6 | 36.6 | 34.4 | 34.2 |
| Obesity (≥28) | 16.4 | 18.2 | 14.7 | 16.4 | 18.3 | 13.6 | 17.5 | 15.3 |
| Central obesity | 35.2 | 37.2 | 33.3 | 30.0 | 42.7 | 41.5 | 36.4 | 34.0 |
| Healthy weight | 45.0 | 41.8 | 48.2 | — | — | — | — | — |

**JAMA 2021 Table 1 (CCDRFS 2018; n analysed 173 642; weighted %). verified = true**

| 2018 | All | Men | Women |
|---|---|---|---|
| Underweight <18.5 | 4.2 | 3.8 | 4.5 |
| Normal 18.5–23.9 | 44.8 | 41.6 | 48.0 |
| Overweight 24–27.9 | 34.5 | 36.4 | 32.7 |
| Obesity ≥28 | 16.5 | 18.2 | 14.8 |
| Central obesity (M ≥90, W ≥85 cm) | 35.4 | 37.3 | 33.5 |
| WHO overweight 25–29.9 / obesity ≥30 | 32.8 / 7.9 | 35.8 / 8.6 | 29.8 / 7.2 |

The corresponding 2013 values are overweight 32.5, obesity 14.1 and central obesity 31.6.

### D4.8 CNHS 2015: central obesity by sex; by 6 age bands (verified)

- **Source:** Nan J, Chen M, Yuan H, Cai S, Piao W, Li F, Yang Y, Zhao L, Yu D. *Prevalence and Influencing Factors of Central Obesity among Adults in China: China Nutrition and Health Surveillance (2015-2017).* Nutrients 2024;16(16):2623. DOI 10.3390/nu16162623; PMID 39203759; PMCID PMC11357308. Table 2; n = 145 298; standardised to the 2010 population.
- **Verbatim:** "The standardized prevalence of central obesity among Chinese adults aged 18 years or older was 29.9%, with a significantly higher prevalence in men than in women (31.0% vs. 28.8%)."

| Total | Men | Women | 18–29 | 30–39 | 40–49 | 50–59 | 60–69 | ≥70 |
|---|---|---|---|---|---|---|---|---|
| 29.9 (28.4–31.4) | 31.0 (29.2–32.8) | 28.8 (27.3–30.3) | 18.4 (16.6–20.2) | 28.1 (25.5–30.7) | 33.5 (32.0–35.0) | 37.9 (36.2–39.6) | 38.0 (36.1–39.9) | 34.9 (32.5–37.4) |

Central obesity by sex × age: NOT FOUND as a numeric table. Lead: Zhang L et al., Obesity (Silver Spring) 2019;27:1898-1905 (China Hypertension Survey 2012–15; PMID 31549787; paywalled; abstract gives 29.1% overall, 28.6% men, 29.6% women).

**D4 caveats.**
1. CCDRFS 2018 (34.3% overweight, 16.4% obese) and CNHS 2015 (35.2% / 14.6%, unweighted sample %) are the main national anchors. 国民体质监测 2020 gives 35.0% / 14.6% for ages 20–59.
2. The Lancet 2021 "overweight" = BMI ≥24 *including* obesity (Chinese) or ≥25 including obesity (WHO). JAMA 2021 and the CCDRFS report use mutually exclusive 24–27.9 and ≥28.
3. TIDE (BMJ 2020) uses WHO BMI cut-offs and WC ≥90/≥80.
4. The CNHS appendix gives SE (not SD) by sex × age. Use the percentiles, or SDs from CCDRFS 2013 (BMI) and CNHS 2015 (WC, by sex), for the spread.

> **Cross-reference.** Appendix A has CHARLS 2015 smoothed BMI and waist percentiles by sex at ages 50-100.

---

## D5. Smoking

### Sources used (all opened; numbers below copied from the retrieved tables)

| # | Survey (year, design) | Ages | n | Citation | Where the numbers are |
|---|---|---|---|---|---|
| S1 | China Chronic Disease and Risk Factor Surveillance (CCDRFS) 2018, nationally and provincially representative, multistage stratified cluster sample, 31 provinces, face-to-face interview | 18–69 in this analysis | 2018 wave: 69,696 men + 90,254 women aged 18–69 (Table 1); pooled 2007–2018: 624,568 | Zhang M, Yang L, Wang L, Jiang Y, Huang Z, Zhao Z, et al. Trends in smoking prevalence in urban and rural China, 2007 to 2018: Findings from 5 consecutive nationally representative cross-sectional surveys. PLoS Med 2022;19(8):e1004064. DOI 10.1371/journal.pmed.1004064; PMID 36006870; PMCID PMC9409540 | Main Table 2 (both sexes by age); S3 Text Tables B, E, H, K (current/former by sex × age), P (age first started daily smoking), T (cigarettes/day). S3 Text: https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1004064.s003 |
| S2 | CCDRFS 2018 official report (中国慢性病及危险因素监测报告2018), 298 counties/districts, 302 surveillance points | ≥18 (incl. ≥60/≥70) | 184,509 valid records analysed | 中国疾病预防控制中心, 中国疾病预防控制中心慢性非传染性疾病预防控制中心 编著. 中国慢性病及危险因素监测报告（2018）. 摘要 (Chinese) and Abstract (English) chapters. Publisher/year not shown on the retrieved page | https://fwdbook.qq.com/read/1053696612/6 (摘要) ; https://fwdbook.qq.com/read/1053696612/7 (Abstract) |
| S3 | 2018 China Adult Tobacco Survey (GATS China 2018), household survey, 200 counties/districts, tablet face-to-face | ≥15 | 19,376 individuals (overall response 91.5%) | (a) Chinese Center for Disease Control and Prevention. 2018 China Adult Tobacco Survey Report (English), WHO NCD Microdata Repository catalog 803; (b) 肖琳, 南奕, 邸新博, 孟子达. 2018年中国15岁及以上人群吸烟现况及变化趋势研究. 中华流行病学杂志 2022;43(6):811-817. DOI 10.3760/cma.j.cn112338-20211130-00934 | (a) https://extranet.who.int/ncdsmicrodata/index.php/catalog/803/download/5569 , Tables 4.1, 4.3 (Cont'd), 4.5, 4.7, 5.1; (b) https://html.rhhz.net/zhlxbx/20220604.htm 表1 (table image zhlxbxzz-43-6-811-T1.jpg) |
| S4 | 2024 China Adult Tobacco Survey (2024中国成人烟草调查 / China National Adult Tobacco Survey, NATS 2024), 31 provinces + XPCC, 320 surveillance points | ≥15 | 199,684 valid questionnaires (official report); 193,007 valid responses in the journal paper | (a) 中国疾病预防控制中心. 2024中国成人烟草调查主要结果和发现. 2025年5月; (b) Zeng X, Liu S, Liu Y, Xiao L. Smoking Prevalence in Urban and Rural Areas — China, 2024. China CDC Wkly 2025;7(22):751-759. DOI 10.46234/ccdcw2025.124; PMID 40621203; PMCID PMC12228068 | (a) https://www.chinacdc.cn/jksj/jksj04/202506/P020250616403576918910.pdf 图1, 图2, 图9 ; (b) https://weekly.chinacdc.cn/en/article/pdf/preview/10.46234/ccdcw2025.124.pdf Tables 1 and 4 |

Definitions:
- S1 (CCDRFS): "Regular smokers were defined as individuals who reported currently smoking tobacco products daily. Occasional smokers were those who currently smoke but not on a daily basis. Former smokers were those who had habitually (i.e., daily or occasional) smoked in the past but had stopped completely for at least 1 month before the survey. We then defined regular and occasional smokers as “current smokers” and current and former smokers as “ever-smokers.”"
- S3 (GATS 2018): "Ex-smokers (people who quit smoking): people who used to smoke but had quit smoking at the time of the Survey. Cessation rate: percentage of ex-smokers out of current and ex-smokers." (report, Definition of indicators). Chinese paper: "通过询问调查对象“您现在吸烟吗？每天吸、不是每天吸、还是不吸？”来界定现在吸烟者、每日吸烟者和偶尔吸烟者；对于现在不吸烟者，通过询问“您以前吸烟吗？每天吸、不是每天吸、还是从不吸？”来界定戒烟者"
- S4 (NATS 2024): "Current smokers were defined as individuals who reported currently smoking tobacco, with daily smokers constituting those who reported daily use."

### D5.1 CCDRFS 2018 — current, former and never smoking by sex × age (18–69) [S1] — verified: true (current, former); never = derived

Values are weighted % (95% CI), 2018 column of S3 Text Tables B (men current), E (men former), H (women current), K (women former). "Never" = 100 − current − former (derived by us; not printed in the source).

| Age (y) | Men current | Men former | Men never (derived) | Women current | Women former | Women never (derived) |
|---|---|---|---|---|---|---|
| 18–19 | 31.6 (23.7–39.6) | 3.1 (0.0–6.1) | 65.3 | 4.3 (0.0–10.6) | 0.9 (0.0–2.2) | 94.8 |
| 20–24 | 45.2 (40.0–50.3) | 2.8 (1.6–4.0) | 52.0 | 1.2 (0.5–1.9) | 0.4 (0.0–0.9) | 98.4 |
| 25–29 | 50.6 (46.4–54.7) | 2.7 (1.8–3.6) | 46.7 | 1.1 (0.6–1.5) | 0.3 (0.0–0.5) | 98.6 |
| 30–39 | 50.8 (48.4–53.3) | 5.2 (4.4–6.0) | 44.0 | 1.3 (0.9–1.6) | 0.3 (0.2–0.5) | 98.4 |
| 40–49 | 53.5 (51.7–55.3) | 7.8 (7.0–8.5) | 38.7 | 2.0 (1.5–2.5) | 0.3 (0.2–0.5) | 97.7 |
| 50–59 | 56.0 (54.5–57.5) | 12.7 (11.8–13.5) | 31.3 | 2.6 (2.0–3.2) | 0.5 (0.4–0.7) | 96.9 |
| 60–69 | 50.1 (48.3–51.8) | 19.5 (18.2–20.7) | 30.4 | 3.2 (2.5–4.0) | 1.0 (0.7–1.3) | 95.8 |
| 18–69 overall | 50.8 (49.1–52.5) | 7.8 (7.3–8.3) | 41.4 | 1.9 (1.5–2.3) | 0.5 (0.3–0.6) | 97.6 |

Both sexes (main Table 2, 2018 column, % (95% CI), n = current smokers): 18–19 19.8 (15.0–24.7); 20–24 22.8 (20.2–25.3); 25–29 25.9 (24.0–27.8); 30–39 26.5 (25.3–27.8); 40–49 28.1 (26.9–29.2); 50–59 29.7 (28.7–30.6); 60–69 26.9 (25.8–28.0); overall 26.7 (25.8–27.6).

Verbatim: "Table B. The prevalence of current smoking among men in China, 2007-2018. Values are weighted percentages (95% CI)." … "60-69 | 54.0（51.1~56.9） | 50.8（48.4~53.3） | 50.4（48.7~52.2） | 50.5（48.9~52.1） | 50.1（48.3~51.8）"; "Table E. The prevalence of former smoking among men in China, 2007-2018." … "60-69 | 17.9（14.7~21.1） | 18.8（17.0~20.7） | 17.8（16.3~19.2） | 20.7（19.4~22.0） | 19.5（18.2~20.7）". Abstract: "In 2018, 25.6% of adults aged ≥18 years smoked, translating into an estimated 282 million smokers (271 million men and 11 million women) in China."

Caveats: ages 18–69 only (the paper restricted all waves to 18–69 for comparability; the 2018 wave itself enrolled ≥18). Self-report, no cotinine validation. CCDRFS "former" requires ≥1 month abstinence. Female cells at 18–19 are imprecise (wide CI).

### D5.2 CCDRFS 2018 official report — ≥18 incl. ≥60 [S2] — verified: true (text, not table)

| Group | Current smoking | Current daily smoking |
|---|---|---|
| All ≥18 | 26.2% | 23.5% |
| Men ≥18 | 50.0% | 44.9% |
| Women ≥18 | 2.1% | 1.8% |
| Men 18–44 | 48.9% | 43.2% |
| Men 45–59 | 55.5% | 51.0% |
| Men ≥60 | 45.5% | 41.6% |

Quit rate among smokers (戒烟率; both sexes): 18–44 8.8%, 45–59 16.7%, ≥60 31.2%; men 15.1%, women 21.5%, all 15.4%. Successful quit rate (成功戒烟率): 18–44 5.1%, 45–59 12.6%, ≥60 25.4%; all 11.2%.

Verbatim (摘要): "2018年我国18岁及以上居民现在吸烟率为26.2%，男性（50.0%）明显高于女性（2.1%）。男性居民中，45～59岁组现在吸烟率（55.5%）高于18～44岁组（48.9%）和60岁及以上组（45.5%）……18岁及以上居民现在每日吸烟率为23.5%，男性（44.9%）明显高于女性（1.8%）。男性居民中，45～59岁组现在每日吸烟率（51.0%）高于18～44岁组（43.2%）和60岁及以上组（41.6%）……女性居民的现在吸烟率和现在每日吸烟率均随年龄增长而升高，城乡和地区间相近。" and "2018年我国18岁及以上吸烟者戒烟率为15.4%，男性（15.1%）低于女性（21.5%），60岁及以上组（31.2%）高于18～44岁组（8.8%）和45～59岁组（16.7%）……吸烟者成功戒烟率为11.2%……60岁及以上组（25.4%）高于18～44岁组（5.1%）和45～59岁组（12.6%）". Female age-specific values are not printed in the summary (NOT FOUND in retrieved text; full chapter "第二节 慢性病危险因素" is app-only).

### D5.3 GATS China 2018 — current smoking and quit rate by sex × age (≥15) [S3] — verified: true; former/never = derived

From 肖琳 et al. 2022 表1 "2018年≥15岁人群吸烟率和戒烟率" (% (95% CI)); identical to report Table 4.3 (Cont'd) "Any type of tobacco" column to one decimal (men 34.0/53.0/57.1/44.0; women 0.9/1.1/2.7/4.1). Daily smoking from report Table 4.5 (Cont'd). Former = current × CR/(100 − CR), never = 100 − current − former (derived; the method reproduces the reported overall male "Never smoke" 37.2% in Table 4.1).

| Age (y) | Men current | Men daily | Men quit rate (CR) | Men former (derived) | Men never (derived) | Women current | Women daily | Women CR | Women former (derived) | Women never (derived) |
|---|---|---|---|---|---|---|---|---|---|---|
| 15–24 | 34.02 (28.14–39.90) | 26.7 | 8.18 (2.64–13.73) | 3.0 | 63.0 | 0.94 (0.21–1.68) | 0.2 | 4.78 (0.00–14.53) | 0.05 | 99.0 |
| 25–44 | 52.95 (50.14–55.76) | 45.5 | 11.86 (9.73–14.00) | 7.1 | 39.9 | 1.14 (0.57–1.72) | 0.8 | 23.21 (8.40–38.02) | 0.3 | 98.5 |
| 45–64 | 57.14 (54.63–59.65) | 52.2 | 22.22 (19.93–24.52) | 16.3 | 26.5 | 2.66 (1.97–3.35) | 2.2 | 27.81 (19.34–36.28) | 1.0 | 96.3 |
| ≥65 | 43.97 (40.63–47.31) | 39.8 | 38.45 (34.68–42.23) | 27.5 | 28.6 | 4.06 (2.71–5.40) | 3.4 | 40.64 (30.88–50.40) | 2.8 | 93.2 |
| All ≥15 | 50.47 (48.61–52.34) | 44.4 | 19.64 (17.85–21.45) | 12.3 (reported ex daily 8.5 + ex occasional 3.9 = 12.4) | 37.2 (reported) | 2.07 (1.65–2.49) | 1.6 | 30.22 (24.60–36.49) | 0.9 | 97.0 (reported) |

Verbatim (report Table 4.1): "Never smoke 66.7 (65.5, 68.0) … 37.2 (35.3, 39.1) … 97.0 (96.4, 97.5)". Verbatim (paper): "不同年龄组男性吸烟率差异较大（P < 0.001），45~64岁最高（57.14%），15~24岁最低（34.02%）" ; "≥65岁人群吸烟率最高，为4.06%" ; "男性吸烟者的戒烟率为19.64%……≥65岁人群戒烟率最高（38.45%），45~岁次之（22.22%），15~和25~岁戒烟率相对较低，分别为8.18%和11.86%".

### D5.4 2024 China Adult Tobacco Survey — most recent [S4] — verified: true

(a) Official report 图1 "不同性别、不同年龄组15岁及以上人群现在吸烟率" (values printed in the figure-table; read from the rendered PDF page):

| Age (y) | Total | Men | Women |
|---|---|---|---|
| 15–24 | 10.7% | 18.7% | 1.7% |
| 25–44 | 26.1% | 48.9% | 1.7% |
| 45–64 | 26.0% | 49.8% | 1.7% |
| ≥65 | 20.6% | 40.6% | 2.5% |
| All ≥15 | 23.2% | 43.9% | 1.8% |

Urban/rural (图2): men 39.5% urban, 47.2% rural; women 2.1%, 1.7%; total 20.9%, 24.9%. Trend (图3), men: 2010 52.9, 2015 52.1, 2018 50.5, 2022 45.3, 2024 43.9; women 2.4, 2.7, 2.1, 2.3, 1.8.
Quit rate (戒烟率, 图9, both sexes only): 15–24 11.2%, 25–44 12.3%, 45–64 23.6%, ≥65 42.1%; men 22.3%, women 30.2%, all 22.6%. Approximate former smoking for men using the both-sex CR: 15–24 ≈2.4%, 25–44 ≈6.9%, 45–64 ≈15.4%, ≥65 ≈29.5% (derived; approximate, flag verified=false).
Verbatim: "中国15岁及以上人群现在吸烟率为23.2%，男性（43.9%）高于女性（1.8%），农村（24.9%）高于城市（20.9%）。与2022年比，现在吸烟率下降了0.9个百分点" ; "我国15岁及以上吸烟人群的戒烟率为22.6%……女性（30.2%）高于男性（22.3%），年龄越大戒烟率越高。"

(b) Zeng et al. 2025, Table 1 (both sexes; current / daily, weighted % (95% CI)): 15–29 14.6 (13.5–15.7) / 11.5 (10.4–12.6); 30–39 25.3 (23.5–27.1) / 21.7 (20.1–23.3); 40–49 27.2 (26.1–28.3) / 23.7 (22.6–24.8); 50–59 26.4 (25.4–27.3) / 23.7 (22.8–24.7); 60–69 25.0 (24.0–25.9) / 22.7 (21.8–23.6); ≥70 19.2 (18.2–20.2) / 17.0 (16.1–17.9); male 43.9 (42.6–45.2) / 38.6 (37.2–40.0); female 1.8 (1.6–2.1) / 1.3 (1.1–1.5). Sex × age prevalence is not tabulated in this paper.
Verbatim: "In 2024, China’s smoking prevalence among adults aged ≥15 years was 23.2% (current) and 20.3% (daily)".

### D5.5 Age of starting smoking — verified: true

CCDRFS 2018, S3 Text Table P (mean age first started daily smoking among current regular smokers, weighted mean (95% CI), 2018 column):

| Age (y) | Men | Women |
|---|---|---|
| 18–19 | 15.7 (15.3–16.1) | – |
| 20–24 | 17.4 (16.9–17.9) | 18.8 (17.4–20.1) |
| 25–29 | 18.2 (17.9–18.6) | 21.9 (20.2–23.5) |
| 30–39 | 19.4 (19.2–19.7) | 22.4 (21.2–23.7) |
| 40–49 | 20.3 (20.1–20.5) | 25.2 (23.9–26.4) |
| 50–59 | 20.9 (20.6–21.1) | 25.9 (24.7–27.1) |
| 60–69 | 21.8 (21.5–22.1) | 27.7 (25.9–29.4) |
| Overall 18–69 | 19.7 (19.6–19.9) | 24.6 (23.8–25.4) |

NATS 2024 (Zeng et al. Table 4), daily smokers' mean age of starting daily smoking, mean (95% CI): men 15–29 18.9 (18.7–19.2), 30–39 21.5 (21.2–21.7), 40–49 22.7 (22.3–23.0), 50–59 22.5 (22.2–22.8), 60–69 23.1 (22.8–23.5), ≥70 24.1 (23.8–24.5), all 22.2 (22.0–22.4); women 20.1, 23.5, 26.8, 30.1, 30.0, 31.0, all 27.2 (26.1–28.3). Current smokers' age of smoking initiation (any smoking): men all 20.6, women all 26.1; by age (men) 18.0, 20.1, 20.9, 20.9, 21.4, 22.5.
CCDRFS 2018 report (≥18): "现在每日吸烟者开始每日吸烟年龄平均为20.0岁，男性（19.8岁）早于女性（24.6岁）。"
GATS 2018: report Table 4.7 mean 21.1 (men 20.9, women 26.6; 15–24 17.2, 25–44 20.1, 45–64 21.6, ≥65 24.0); paper: "现在每日吸烟者开始每日吸烟的平均年龄为20.95岁" ; "男性吸烟者开始每日吸烟的平均年龄为20.92岁" ; "女性吸烟者开始每日吸烟年龄平均为26.62岁".
Caveat: the age of initiation reported by a cross-section of current smokers rises with current age (recall and cohort effects); use the overall sex-specific value unless the model needs age-specific values.

### D5.6 Cigarettes per day — verified: true

CCDRFS 2018 S3 Table T (current regular smokers, weighted mean): men 18–19 12.4, 20–24 13.4, 25–29 14.9, 30–39 16.5, 40–49 18.7, 50–59 19.8, 60–69 17.8, overall 17.2 (16.8–17.5); women overall 14.4 (11.6–17.2) (women's age cells unstable, e.g. 18–19 = 39.8).
NATS 2024 Table 4 (current smokers): men 15–29 11.3, 30–39 14.4, 40–49 16.2, 50–59 17.9, 60–69 18.1, ≥70 15.9, all 16.0; women 6.0, 6.8, 9.9, 11.7, 12.3, 11.7, all 9.7. Daily smokers: men 13.0, 15.8, 17.6, 19.2, 19.4, 17.3, all 17.4; women 7.6, 10.3, 12.9, 13.8, 14.3, 12.8, all 12.1.
CCDRFS 2018 report: "现在吸烟者日均吸烟量为15.4支，男性（15.6支）大于女性（12.2支）；现在每日吸烟者日均吸烟量为17.1支，男性（17.2支）大于女性（14.2支）。"

### D5.7 CCDRFS 2018: current smoking by sex x age x urban/rural, verified (secondary publication of the official report)

- **Source:** Song S, Lei L, Liu H, Yang F, Li N, Chen W, Peng J, Ren J. Impact of changing the prevalence of smoking, alcohol consumption and overweight/obesity on cancer incidence in China from 2021 to 2050: a simulation modelling study. *EClinicalMedicine* 2023;63:102163. doi:10.1016/j.eclinm.2023.102163. PMID 37662518; PMCID PMC10468350.
- **Location:** Supplementary mmc1.docx, Table S2, "Prevalence (%) of non-smokers and current smokers in the China population aged 18+ years in 2018". The table cites "Chinese Center for Disease Control and Prevention. Report on chronic disease risk factor surveillance in China 2018. Beijing: People's Medical Publishing House; 2021".
- **Definition, verbatim (main text):** "Current smokers referred to those who currently smoke, including daily smokers and occasional smokers."
- This fills the women-by-age gap and the ≥60 gap left by the report summary (D5.2).

| Residence x sex | 18-44 current | 45-59 current | 60+ current |
|---|---|---|---|
| Urban men | 44.6 | 54.6 | 40.9 |
| Rural men | 54.3 | 56.4 | 49.1 |
| Urban women | 1.5 | 2.0 | 2.9 |
| Rural women | 1.4 | 2.8 | 4.4 |

Non-smokers = 100 - current, as printed; for example "18-44 years | 55.4 | 44.6" for urban men. Former smoking is not separated. No national (urban + rural) row is printed.

### D5 recommendation for the model
- Ages 18–69: S1 (CCDRFS 2018) gives current, former and (derived) never by sex for every needed band; for 18–29 pool 18–19/20–24/25–29 with population weights (not provided; the three bands are close for men: 31.6/45.2/50.6% current).
- Age 70+: no CCDRFS sex × 70+ table was found. Use GATS 2018 ≥65 (men 43.97% current, ~27.5% former; women 4.06% current, ~2.8% former) or 2024 survey ≥65 (men 40.6%, women 2.5% current). NATS 2024 ≥70 both sexes = 19.2%.
- Recent decline: male current smoking fell from 50.5% (2018) to 43.9% (2024) in the same survey series, so 2018 tables overstate 2024 prevalence in men by ~6 points, most in young men (15–24: 34.0% → 18.7%).

---

## D6. Alcohol

### Sources used (all opened)

| # | Survey | Ages | n | Citation | Where |
|---|---|---|---|---|---|
| A1 | CCDRFS 2018 official report | ≥18 | 184,509 | 中国疾病预防控制中心, 中国疾病预防控制中心慢性非传染性疾病预防控制中心 编著. 中国慢性病及危险因素监测报告（2018）, 摘要/Abstract | https://fwdbook.qq.com/read/1053696612/6 ; /7 |
| A2 | 2015 China Chronic Disease and Nutrition Surveillance (CCDNS 2015; the 2015 national chronic-disease surveillance wave), 298 surveillance points, 31 PLADs | ≥18 | 189,198 included (69,037 past-year drinkers) | Zhao Z, Wang L, Zhang M, Zhang X, Huang Z, Li C, Jia P, Wu J. Geographic Distribution of Alcohol Use Among Chinese Adults — China, 2015. China CDC Wkly 2020;2(7):98-103. DOI 10.46234/ccdcw2020.029 | https://weekly.chinacdc.cn/en/article/pdf/preview/10.46234/ccdcw2020.029.pdf Table 1 |
| A3 | 2024 national survey of alcohol use (same NATS platform; one PLAD sampled per each of 7 regions, PPS within) | ≥15 | 46,376 (response 92.0%) | Ji N, Wang Y, Sang Y, Zeng X, Liu Y, Liu S. Alcohol Use Prevalence Among Chinese People Aged 15 Years and Above — China, 2024. China CDC Wkly 2026;8(2):35-42. DOI 10.46234/ccdcw2026.006; PMID 41551334; PMCID PMC12804769 | https://weekly.chinacdc.cn/en/article/pdf/preview/10.46234/ccdcw2026.006.pdf Table 2 |
| A4 | China National Nutrition and Health Survey (CNNHS) 2010–2012, 150 sites | ≥18 | 135,824 | 李亚茹, 王婧, 赵丽云, 王志宏, 于冬梅, 何宇纳, 丁钢强. 中国成年人饮酒习惯及影响因素. 中华流行病学杂志 2018;39(7):898-903. DOI 10.3760/cma.j.issn.0254-6450.2018.07.007 | https://html.rhhz.net/zhlxbx/20180707.htm 表1, 表4 (table images) |

Definitions (verbatim):
- A1: past-30-day and past-12-month drinking ("30天内饮酒率和12个月内饮酒率"); 危险饮酒率/有害饮酒率 among drinkers; 单次大量饮酒率 among current drinkers. The gram thresholds used for 危险饮酒/有害饮酒/单次大量饮酒 in the 2018 report are NOT FOUND in retrieved text (the methods chapter is app-only). Lead: the full chapter "第二节 慢性病危险因素" of the report; A4 quotes the WHO 2000 thresholds commonly used in Chinese surveillance (below).
- A2: "Current alcohol use was defined as those who self-reported any alcohol intake in the past 12 months."
- A3: "Alcohol use in the past 30 days: The percentage of the population aged 15+ years who consumed alcoholic beverages in the previous 30 days. Alcohol use in the past 12 months: … in the previous 12 months. Heavy episodic drinking (HED): Defined as consuming at least 60 grams of pure alcohol on one occasion once or more in the past month." HED is reported as % of current drinkers.
- A4: "饮酒是指过去1年内每周饮酒≥1次者。采用《中国居民膳食指南（2016）》中建议，过量饮酒为日均酒精摄入量超过推荐量（男性为25 g，女性为15 g）；适量饮酒为日均酒精摄入量不超过推荐量……有害饮酒定义为男性饮酒者日均酒精摄入量≥61 g，女性饮酒者日均酒精摄入量≥41 g".

### D6.1 2024 — drinking by sex × age (≥15) [A3] — verified: true

Table 2, weighted % (95% CI). Past-30-day and past-12-month are % of the whole population; HED is % of current drinkers.

| Sex | Age (y) | Past 30 days | Past 12 months | HED among current drinkers |
|---|---|---|---|---|
| Men | 15–24 | 20.2 (14.8–25.5) | 30.0 (23.5–36.4) | 36.8 (28.7–44.9) |
| Men | 25–44 | 38.6 (33.7–43.6) | 51.3 (47.0–55.6) | 54.2 (49.7–58.7) |
| Men | 45–64 | 37.4 (34.4–40.4) | 46.3 (43.1–49.6) | 49.2 (44.8–53.6) |
| Men | ≥65 | 29.9 (27.0–32.9) | 37.0 (33.5–40.4) | 32.0 (27.2–36.8) |
| Men | All | 34.3 (31.3–37.4) | 44.5 (41.2–47.8) | 48.0 (44.1–52.0) |
| Women | 15–24 | 7.3 (3.7–10.8) | 12.6 (8.0–17.3) | 12.0 (4.3–19.7) |
| Women | 25–44 | 6.7 (5.4–8.0) | 12.4 (10.5–14.4) | 22.1 (17.7–26.6) |
| Women | 45–64 | 4.9 (4.0–5.9) | 8.2 (6.9–9.5) | 22.1 (15.0–29.1) |
| Women | ≥65 | 5.3 (3.9–6.6) | 8.0 (6.3–9.7) | 17.1 (9.1–25.1) |
| Women | All | 5.9 (5.0–6.8) | 10.2 (8.8–11.6) | 19.9 (15.3–24.5) |
| Both | All ≥15 | 20.3 (18.4–22.2) | 27.6 (25.3–29.8) | 42.9 (39.0–46.7) |

Verbatim: "In 2024, among Chinese individuals aged 15+ years, the prevalence of alcohol use was 20.3% in the past 30 days and 27.6% in the past 12 months. Males demonstrated significantly higher rates than females (past-month: 34.3% vs. 5.9%; past-year: 44.5% vs. 10.2%)" ; "42.9% of current drinkers engaged in HED, with males (48.0%) substantially exceeding females (19.9%)". Drinking ≥5 days/week: 17.5% of current drinkers (men 20.1%, women 5.7%).
Caveat: only 7 provinces sampled (one per region) and weighted to the 2020 census; HED population prevalence = past-30-day × HED share (e.g., men 25–44 ≈ 38.6% × 54.2% ≈ 20.9%, derived).

### D6.2 CCDNS/CCDRFS 2015 — past-12-month drinking and mean daily pure alcohol by sex × age (≥18) [A2] — verified: true

Table 1, weighted prevalence % (95% CI); grams = average daily pure alcohol intake among drinkers (95% CI).

| Age (y) | Men prevalence | Men g/day (drinkers) | Women prevalence | Women g/day (drinkers) | Both prevalence | Both g/day |
|---|---|---|---|---|---|---|
| 18–29 | 62.2 (58.0–66.4) | 10.7 (9.3–12.2) | 22.4 (19.4–25.3) | 1.6 (1.0–2.1) | 42.7 (39.3–46.1) | 8.1 (6.8–9.5) |
| 30–39 | 66.3 (63.0–69.7) | 16.8 (15.5–18.1) | 23.8 (20.8–26.7) | 2.4 (1.7–3.0) | 45.6 (42.5–48.7) | 12.6 (11.5–13.8) |
| 40–49 | 66.3 (63.7–68.9) | 23.5 (21.9–25.2) | 22.4 (20.0–24.9) | 3.3 (2.8–3.8) | 44.7 (42.3–47.1) | 17.8 (16.4–19.2) |
| 50–59 | 63.2 (61.4–64.9) | 29.3 (27.5–31.0) | 18.1 (16.5–19.6) | 4.1 (3.6–4.6) | 41.1 (39.6–42.5) | 23.0 (21.6–24.4) |
| 60–69 | 56.7 (54.7–58.6) | 30.1 (28.3–32.0) | 14.7 (13.4–16.0) | 6.0 (4.7–7.2) | 35.9 (34.5–37.3) | 24.4 (22.8–25.9) |
| ≥70 | 40.9 (39.0–42.9) | 24.2 (21.7–26.7) | 13.1 (11.0–15.3) | 6.9 (5.5–8.4) | 26.2 (24.2–28.2) | 18.9 (17.3–20.6) |
| All ≥18 | 61.7 (59.3–64.1) | 20.7 (19.5–21.9) | 20.3 (18.4–22.2) | 3.2 (2.7–3.7) | 41.3 (39.2–43.4) | 15.9 (14.7–17.1) |

Verbatim: "the prevalence of current alcohol use among Chinese adults aged 18 years and above was 41.3% (95% CI: 39.2%–43.4%), with 61.7% (95% CI: 59.3%–64.1%) in men and 20.3% in women (95% CI: 18.4%–22.2%)" ; "In 2015, the average level of daily pure alcohol intake was significantly higher in men than in women (20.7 vs. 3.2 grams)."
Caveat: no heavy-drinking prevalence by sex × age in this paper; g/day is the mean among drinkers (self-reported, beverage-specific ethanol content).

### D6.3 CCDRFS 2018 official report — marginals only (≥18) [A1] — verified: true (text)

| Indicator | All | Men | Women | 18–44 | 45–59 | ≥60 |
|---|---|---|---|---|---|---|
| Drank in past 30 days (% of population) | 28.3 | 46.2 | 10.2 | 28.5 | 31.3 | 23.5 |
| Drank in past 12 months (% of population) | 39.8 | 60.3 | 19.1 | 41.8 | 41.3 | 31.1 |
| Mean daily pure alcohol, drinkers (g) | 20.4 | 25.2 | 4.1 | 15.0 | 27.8 | 30.2 |
| 危险饮酒 (dangerous drinking), % of drinkers | 5.7 | 6.9 | 2.1 | 8.2 | 3.9 | 9.3 |
| 有害饮酒 (harmful drinking), % of drinkers | 8.6 | 10.7 | 1.6 | 5.4 | 12.7 | 15.2 |
| 单次大量饮酒 (heavy single-occasion), % of current drinkers | 39.8 | 46.8 | 17.5 | 41.0 | 42.4 | 29.1 |

Verbatim (摘要): "2018年我国18岁及以上居民30天内饮酒率和12个月内饮酒率分别为28.3%和39.8%。过去30天内饮酒率男性（46.2%）高于女性（10.2%），45～59岁组（31.3%）高于18～44岁组（28.5%）和60岁及以上组（23.5%）……过去12个月内饮酒率男性（60.3%）高于女性（19.1%），18～44岁组（41.8%）、45～59岁组（41.3%）和60岁及以上组（31.1%）逐渐降低" ; "2018年我国18岁及以上饮酒者日均纯酒精摄入量为20.4g，男性（25.2g）明显高于女性（4.1g），60岁及以上年龄组（30.2g）高于18～44岁组（15.0g）和45～59岁组（27.8g）" ; "饮酒者危险饮酒率为5.7%，男性（6.9%）高于女性（2.1%），60岁以及以上组（9.3%）高于18～44岁组（8.2%）和45～59岁组（3.9%）……饮酒者有害饮酒率为8.6%，男性（10.7%）高于女性（1.6%），18～44岁组（5.4%）、45～59岁组（12.7%）和60岁及以上组（15.2%）逐渐上升……现在饮酒者单次大量饮酒率为39.8%，男性（46.8%）高于女性（17.5%），18～44岁、45～59岁和60岁及以上年龄组分别为41.0%、42.4%和29.1%".
Caveats: sex × age cross-tabulation NOT FOUND (full chapter app-only); the dangerous-drinking age pattern (18–44 8.2% > 45–59 3.9%) is printed as such and looks atypical — check against the full table before use; thresholds not shown in retrieved text.

### D6.4 CNNHS 2010–2012 — weekly drinking and excessive drinking by sex × age (≥18) [A4] — verified: true (older data)

表1 "研究对象的饮酒情况（%）" (weighted %; drinker = drank ≥1/week in past year; 过量 = >25 g/day men, >15 g/day women):

| Age (y) | Men non-drinker | Men moderate | Men excessive | Women non-drinker | Women moderate | Women excessive |
|---|---|---|---|---|---|---|
| 18–44 | 44.6 | 44.2 | 11.2 | 87.0 | 12.3 | 0.7 |
| 45–54 | 40.2 | 39.3 | 20.5 | 86.4 | 11.8 | 1.8 |
| 55–64 | 48.4 | 33.9 | 17.6 | 89.0 | 9.3 | 1.8 |
| ≥65 | 63.5 | 24.5 | 12.0 | 91.8 | 6.9 | 1.2 |
| All | 46.3 | 39.8 | 14.0 | 87.8 | 11.1 | 1.1 |

Harmful drinking (≥61 g/day men, ≥41 g/day women) among current drinkers, both sexes (表4): 18–44 4.9%, 45–54 9.9%, 55–64 10.4%, ≥65 9.6%; men 7.9%, women 3.3%; overall 7.1%.
Verbatim: "我国成年人饮酒率为30.5%，其中男性饮酒率为53.8%，女性饮酒率为12.2%。在现在饮酒者中，男性和女性的过量饮酒率分别为14.0%和1.1%" ; "总的有害饮酒率为7.1%，其中男性为7.9%，女性为3.3%。随着年龄增加，有害饮酒率先上升再下降。" (Age bands printed as 18~, 45~, 55~, ≥65.)

### D6.5 China Kadoorie Biobank (context only; not nationally representative)
Im PK, Millwood IY, Guo Y, et al. Patterns and trends of alcohol consumption in rural and urban areas of China: findings from the China Kadoorie Biobank. BMC Public Health 2019;19:217. DOI 10.1186/s12889-019-6502-1; PMID 30786877; PMCID PMC6383236. Baseline 2004–08, 512,891 adults aged 30–79 in 10 regions. Verbatim: "At baseline, 33% of men drank alcohol at least weekly (i.e., current regular), compared to only 2% of women." HED definition: "more than 60 g of alcohol on one occasion for men, and more than 40 g for women". Age patterns are shown by birth cohort in figures only (no sex × age table) — not used for norms.

### D6.6 CCDRFS 2018: drinking categories by sex x age x urban/rural, verified (secondary publication of the official report)

- **Source:** Song S et al. *EClinicalMedicine* 2023;63:102163 (citation in D5.7). Supplementary Table S3, "Prevalence (%) of non-drinkers, moderate use, hazardous use and harmful use of alcohol in the China population aged 18+ years in 2018". Data from the CCDRFS 2018 report.
- **Definitions, verbatim (main text):** "Participants who consumed alcoholic beverage in the past 12 months were defined as drinkers. According to the World Health Organization (WHO) International Guide for Monitoring Alcohol Consumption and Related Harm, alcohol use was divided into moderate (male: 1–40 g, female: 1–20 g), hazardous (male: 41–60 g, female: 21–40 g) and harmful (male: 61 + g, female: 41 + g) using average ethanol intake per day."
- The four categories add to 100% of the population. They are not shares of drinkers.

| Residence x sex | Age | Non-drinkers | Moderate | Hazardous | Harmful |
|---|---|---|---|---|---|
| Urban men | 18-44 | 38.5 | 55.0 | 2.6 | 3.8 |
| Urban men | 45-59 | 35.1 | 50.6 | 5.8 | 8.5 |
| Urban men | 60+ | 48.7 | 38.8 | 4.9 | 7.6 |
| Urban women | 18-44 | 76.2 | 23.2 | 0.4 | 0.2 |
| Urban women | 45-59 | 78.0 | 21.2 | 0.4 | 0.4 |
| Urban women | 60+ | 85.4 | 13.8 | 0.3 | 0.4 |
| Rural men | 18-44 | 37.4 | 54.6 | 3.2 | 4.8 |
| Rural men | 45-59 | 38.4 | 43.6 | 6.7 | 11.3 |
| Rural men | 60+ | 51.3 | 32.9 | 5.7 | 10.1 |
| Rural women | 18-44 | 82.3 | 17.3 | 0.3 | 0.1 |
| Rural women | 45-59 | 84.3 | 14.8 | 0.4 | 0.5 |
| Rural women | 60+ | 88.0 | 10.5 | 0.7 | 0.8 |

Caveats:
- These thresholds are the ones Song et al. state. The CCDRFS report's own 危险饮酒/有害饮酒 thresholds were not seen verbatim (D6.3), but the hazardous/harmful split matches those labels.
- This is the only retrieved sex x age table of heavy (hazardous + harmful) drinking from a post-2015 national survey.

### D6 recommendation for the model
- Sex × age prevalence of any drinking: A3 (2024, past-12-month and past-30-day; 15–24/25–44/45–64/≥65) or A2 (2015, past-12-month; 10-year bands incl. ≥70, with mean g/day among drinkers). A2 has the finer age grid; A3 is more recent but sampled 7 provinces.
- Heavy drinking: use D6.6 (CCDRFS 2018, via Song et al. 2023). It is the only post-2015 sex x age x residence table with g/day thresholds: hazardous M 41-60 / F 21-40; harmful M ≥61 / F ≥41 g/day. Options: A3 HED share of current drinkers by sex × age (≥60 g/occasion in past month); A1 sex and age marginals for 有害饮酒 (harmful) among drinkers (men 10.7%, women 1.6%; 18–44 5.4%, 45–59 12.7%, ≥60 15.2%); A4 (2010–12) excessive (>25/15 g/day) by sex × age.

---

## D7. Resting heart rate

No nationally representative Chinese survey that we could retrieve publishes resting heart rate (RHR) as mean (SD) by sex x age group for the general adult population. Four sources together cover it:
- **D7-F, best national means by sex.** TIDE 2015-2017 (31 provinces, n = 75,880): men 78.9, women 80.8 bpm.
- **D7-A, sex x 5-year age means.** 2014 National Physical Fitness Surveillance, ages 20-69. Healthy volunteers only; no SD.
- **D7-E, smoothed sex x age percentiles, ages 50-100.** CHARLS 2015.
- **D7-B, mean (SD) by sex plus the age slope.** CKB baseline. D7-C (China PEACE) and D7-D (a CHARLS subsample) are overall cross-checks.

### D7-A. 2014 National Physical Fitness Surveillance (第4次国民体质监测), 安静脉搏 by sex x age, verified

- **Source:** 国家体育总局《2014年国民体质监测公报》, released 2015-11-25 (来源：总局政府网站). URL: https://www.sport.gov.cn/n315/n329/c216784/content.html. The tables are images on that page: 表6 = part/392039.png (adults 20-59, 续1) and 表9 = part/392042.png (60-69, 续). Downloading them needs a Referer header.
- **Sample, quoted verbatim:** "采用分层随机整群的抽样原则，从全国 31 个省（区、市）的 2904 个机关单位、企事业、学校、幼儿园、行政村中抽取了 531849 人，其中， 3 ～ 6 岁幼儿 50702 人； 7 ～ 19 岁儿童青少年（学生） 308725 人； 20 ～ 59 岁成年人 146703 人； 60 ～ 69 岁老年人 25719 人。"
- **Eligibility (key caveat), footnote [1] verbatim:** "[1] 监测对象要求身体健康，发育健全，无先天、遗传性疾病（如先天性心脏病、聋哑、痴呆、精神异常、发育迟缓等），以及急、慢性疾病（如心脏病、高血压等），具有一定的生活自理能力、语言表达能力、思维能力和接受能力，具有基本的运动能力。" The means therefore describe apparently healthy adults, not the whole population. People with heart disease or hypertension were excluded, so expect RHR and BP slightly lower than in the general population.
- **What was printed:** means only, with no SD and no percentiles. The column heading is "安静脉搏（次/分）".

Table: 表6 "2014年全国20～59岁成年人各项体质指标平均数（续1）" and 表9 "2014年全国60～69岁老年人各项体质指标平均数（续）". Values were transcribed from the table images. The 2014 SBP and DBP of these healthy volunteers are copied as well because they share the table.

| Sex | Age (y) | 安静脉搏 resting pulse (beats/min) | SBP (mmHg) | DBP (mmHg) |
|---|---|---|---|---|
| Men | 20-24 | 78.3 | 119.4 | 74.8 |
| Men | 25-29 | 78.2 | 120.4 | 76.3 |
| Men | 30-34 | 78.4 | 120.8 | 77.7 |
| Men | 35-39 | 78.4 | 122.3 | 79.0 |
| Men | 40-44 | 78.1 | 123.0 | 80.1 |
| Men | 45-49 | 78.2 | 124.8 | 81.4 |
| Men | 50-54 | 78.1 | 126.4 | 81.8 |
| Men | 55-59 | 77.5 | 127.2 | 81.4 |
| Men | 60-64 | 77.2 | 129.4 | 81.0 |
| Men | 65-69 | 76.8 | 131.0 | 80.2 |
| Women | 20-24 | 79.5 | 109.8 | 70.5 |
| Women | 25-29 | 78.9 | 109.6 | 70.5 |
| Women | 30-34 | 78.4 | 110.7 | 71.3 |
| Women | 35-39 | 78.0 | 112.6 | 72.7 |
| Women | 40-44 | 77.6 | 115.1 | 74.3 |
| Women | 45-49 | 77.2 | 118.0 | 76.0 |
| Women | 50-54 | 76.7 | 120.8 | 77.3 |
| Women | 55-59 | 76.8 | 123.0 | 77.5 |
| Women | 60-64 | 76.4 | 126.8 | 77.7 |
| Women | 65-69 | 76.8 | 129.5 | 78.0 |

Verified: true, transcribed from the official table images. Caveats:
- The bulletin does not describe the measurement protocol for 安静脉搏 (it is a pulse count taken before the step test in the 《国民体质测定标准》 battery).
- No SD is given.
- 2014 is the most recent round that reports pulse. The 2020 (5th) and 2025 (6th) bulletins dropped 安静脉搏 from their published tables: every table image in both bulletins was checked (see D8/D10).

### D7-B. China Kadoorie Biobank baseline (2004-08), verified

- **Citation:** Agbor VN, Chen Y, Clarke R, et al.; China Kadoorie Biobank Collaborative Group. Resting heart rate and risk of left and right heart failure in 0.5 million Chinese adults. *Open Heart* 2022;9(1):e001963. doi:10.1136/openhrt-2022-001963. PMID 35649571; PMCID PMC9161067 (Europe PMC full text).
- **Sample:** 491,785 CKB participants aged 30-79 from 10 regions (5 urban, 5 rural), excluding prior heart disease and beta-blocker use. Mean age 51.7 (SD 10.6) years; 60% women.
- **Protocol, verbatim:** "RHR was measured using calibrated UA-779 digital BP monitor (Omron UA-779; Live Source) to the nearest one beat per minute (bpm) after the participant had been at rest in a seated position for at least 5 min. RHR was measured twice, and the mean of both measurements was used for the present analyses."
- **Numbers, verbatim (Results):** "Overall, the baseline mean (SD) RHR was 79 (12) bpm (men: 78 (12); women 80 (11)), and RHR declined progressively with increasing age (by 0.76 bpm per 10-year increase)." The abstract rounds the slope: "these decreased with increasing age (by about 1 bpm per 10 years)". The Table 1 "Total" column gives "78.7 (11.7)".

| Sex | Age | Mean RHR (bpm) | SD |
|---|---|---|---|
| All | 30-79 | 79 (Table 1: 78.7) | 12 (Table 1: 11.7) |
| Men | 30-79 | 78 | 12 |
| Women | 30-79 | 80 | 11 |
| Age gradient | per +10 y | -0.76 bpm | - |

Caveats: CKB is not nationally representative. The authors write: "the findings of this study cannot be generalised to the Chinese population, as the CKB is not representative of the Chinese population."

### D7-C. China PEACE Million Persons Project (2015-2020), overall only, verified

- **Citation:** Jing FY, Wang XL, Song JL, et al. Association between clustering of cardiovascular risk factors and resting heart rate in Chinese population: a cross-sectional study. *J Geriatr Cardiol* 2022;19(6):418-427. doi:10.11909/j.issn.1671-5411.2022.06.010. PMID 35845154; PMCID PMC9248276.
- **Sample:** 1,045,405 adults aged 35-75 from 31 provinces. Excluded: users of heart-rate-lowering drugs and people with CVD, cancer or COPD. 60.4% women; mean age 55.67 ± 9.86 years.
- **Protocol, verbatim:** "Heart rate readings were also collected using the electronic BP monitor, and the mean value of the two readings was calculated as RHR" (Omron HEM-7430, seated after 5 min rest).
- **Number, Table 1 "Overall (n = 1,045,405)":** "Heart rate, beats/min | 75.19 ± 10.25". The paper gives no means by sex or age.
- **Caveat, verbatim:** "the study cohort was not established on the basis of a random sampling design, so it does not represent the entire Chinese population."

### D7-D. CHARLS (ages 45 and over), overall cross-check only, verified

- **Citation:** Chen H, Zhou T, Wu S, Cao Y, Zong G, Yuan C. Long-term variability in physiological measures in relation to mortality and epigenetic aging: prospective studies in the USA and China. *BMC Med* 2023;21(1):20. doi:10.1186/s12916-022-02674-w. PMID 36647101; PMCID PMC9843964.
- **Sample:** 6,906 CHARLS participants with three measurements in 2011-2015. Mean age 62.5 ± 9.0; 54.2% female.
- **Protocol, verbatim:** "Pulse rate and blood pressure were each assessed three times, 45 to 60 s apart, respectively, in a seated position, by trained interviewers using an automated sphygmomanometer ... The average values of the last two valid measurements were used at each wave."
- **Table 1, verbatim:** "Pulse rate, bpm, mean ± SD | 68.8 ± 10.9 | 67.8 ± 10.6 | 73.9 ± 10.8", in the column order HRS cohort | HRS-VBS | CHARLS.
- **CHARLS value:** 73.9 ± 10.8 bpm.
- **Caveat:** this is a completer subsample, with no sex or age split.

### D7-E. CHARLS 2015 (ages 45+, national), smoothed percentiles by sex x age, verified

- **Citation:** Zhang L, Yu J, Jia X, Su Z, Hu Y, Zhang J, Yang W, Chen X, Hoogendijk EO, Huang H, Liu Z. Delineating Life-Course Percentile Curves and Normative Values of Multi-Systemic Ageing Metrics in the United Kingdom, the United States, and China. *J Cachexia Sarcopenia Muscle* 2025;16(3):e13862. doi:10.1002/jcsm.13862. PMID 40511588; PMCID PMC12163542.
- **Where the numbers are:** Supplementary file JCSM-16-e13862-s003.doc, Table S7 ("Age-specific percentile values of multi-systemic aging metrics for males in three datasets") and Table S8 (females). The column blocks run "CHARLS | NHANES | UKB". Values below are the CHARLS block.
- **Sample, verbatim:** "the China Health and Retirement Longitudinal Study (CHARLS, 2015 wave), with valid data were included ... After excluding participants with missing data on age and all ageing metrics, those who were pregnant or had prevalent cancer during the survey (N = ... 6457 in ... CHARLS ...), the analysis ultimately encompassed ... 15 332 participants". Median age 60.0; 47.7% male.
- **Method, verbatim:** "the Generalized Additive Models for Location, Scale, and Shape (GAMLSS) method [16] (R package 'gamlss') was used to fit the smoothed percentile curves".
- **Measurement (Supplementary Information), verbatim:** "the pulse rate was also measured during the same procedure or using a pulse trace monitor". CHARLS takes 3 seated automated readings.

**Pulse — Men (Table S7), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 52.7 | 58.3 | 67.1 | 73.9 | 81.5 | 94.0 | 104.2 |
| 60 | 51.3 | 57.0 | 65.8 | 72.8 | 80.4 | 93.2 | 103.7 |
| 70 | 50.1 | 55.8 | 64.9 | 72.0 | 79.9 | 93.1 | 104.1 |
| 80 | 49.6 | 55.4 | 64.8 | 72.2 | 80.5 | 94.4 | 106.0 |
| 90 | 49.0 | 54.9 | 64.2 | 71.6 | 79.8 | 93.7 | 105.2 |
| 100 | 47.8 | 53.6 | 63.0 | 70.4 | 78.7 | 92.7 | 104.4 |

**Pulse — Women (Table S8), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 53.9 | 59.5 | 67.6 | 73.5 | 79.9 | 90.9 | 100.9 |
| 60 | 53.3 | 59.0 | 67.2 | 73.2 | 79.8 | 91.2 | 101.5 |
| 70 | 52.6 | 58.7 | 67.6 | 74.1 | 81.3 | 93.9 | 105.5 |
| 80 | 53.1 | 59.5 | 68.8 | 75.6 | 83.3 | 96.6 | 108.9 |
| 90 | 52.4 | 59.1 | 68.8 | 76.1 | 84.1 | 98.4 | 111.5 |
| 100 | 51.3 | 58.2 | 68.2 | 75.8 | 84.3 | 99.3 | 113.4 |

Caveats:
- Values are smoothed percentiles at exact ages, not age-group means.
- The CHARLS sample is unweighted in this analysis.
- Ages 90-100 rest on very few CHARLS participants and are effectively extrapolations.
- The same tables also give SBP, DBP, BMI, waist and grip percentiles; see the Appendix.

### D7-F. TIDE 2015-2017 (nationally representative, 31 provinces), mean heart rate by sex, verified

- **Citation:** Li Y, Teng D, Shi X, et al. Prevalence of diabetes recorded in mainland China using 2018 diagnostic criteria from the American Diabetes Association: national cross sectional study. *BMJ* 2020;369:m997. doi:10.1136/bmj.m997. PMID 32345662; PMCID PMC7186854. Full text retrieved via Europe PMC.
- **Sample:** 75,880 adults aged 18 and over. Table 2 is titled "General characteristics of adults living in mainland China. Data are percentage (95% confidence interval) unless indicated otherwise".
- **Protocol, verbatim:** "Blood pressure was measured by an electronic blood pressure monitor (Omron HEM-7430, Omron Corporation) on the non-dominant arm twice consecutively with a 10 minute interval between measurements and with the participant in a seated position after five minutes of rest." Heart rate comes from the same device.
- **Table 2 row, verbatim:** "Mean heart rate (95% CI; counts per min | 79.8 (79.2 to 80.5) | 78.9 (78.2 to 79.6) | 80.8 (80.1 to 81.5) | 80.0 (78.7 to 81.4) | 79.6 (78.5 to 80.8)". The column order is Overall | Men (n=36 819) | Women (n=39 061) | Urban | Rural.

| Group | Mean HR (bpm) | 95% CI |
|---|---|---|
| Overall | 79.8 | 79.2-80.5 |
| Men | 78.9 | 78.2-79.6 |
| Women | 80.8 | 80.1-81.5 |
| Urban | 80.0 | 78.7-81.4 |
| Rural | 79.6 | 78.5-80.8 |

Caveats:
- No SD and no age breakdown are given. A 95% CI is not a distribution.
- Combine with the CKB SD (about 11-12 bpm) and the CKB age slope (-0.76 bpm per 10 years) if a z-score is needed. That combination is an assumption.

**NOT FOUND:** RHR mean (SD) by sex x age group, for the general population, from CCDRFS or the China Hypertension Survey. Both measured pulse with automated BP monitors, but we found no publication that tabulates it.
- CHARLS: percentiles only, ages 45+ (D7-E).
- 2014 fitness surveillance: means only, healthy volunteers (D7-A).
- Best lead: CKB or CHARLS microdata.

---

## D8. Grip strength

**Bottom line.** The best national source is the **《第六次全国国民体质监测公报》** (the 6th national physical fitness monitoring, data collected 2025, published 2025-12-28). It gives mean grip strength (kg) by sex and 5-year age group for ages 20–59 (附表2-2) and 60–79 (附表3-2). The 5th bulletin (2020 data) is the second source. Neither bulletin publishes SDs or percentiles, so the spread (SD and centiles) has to come from the **China National Health Survey 2012–2017** (He et al. 2023, Jamar dynamometer, 10-year age groups to 80). For older adults, including those 80+, use **CHARLS 2011–2015 + WHO SAGE-China 2007–2010** (Grgic et al. 2026, Supplementary files 18–19).

### D8.1 Primary source: 6th national physical fitness monitoring (第六次全国国民体质监测), 2025 data. verified = true

- **Issuer / citation:** 国家体育总局（群众体育司）. 《第六次全国国民体质监测公报》. Published 2025-12-28. Official page (scanned bulletin pages): https://www.sport.gov.cn/n315/n20001395/c29322125/content.html. The tables are page images `part/29323209.jpg` (附表2-2) and `part/29323210.jpg` (附表3-1/3-2). A text repost with the same tables is at https://c.m.163.com/news/a/KHVIQ8L70529ISSC.html (运动健康网, 2025-12-29). I read the numbers from the official page images and they match the repost cell for cell.
- **Design and sample (verbatim, official page image `part/29323073.jpg`):** "本次监测对象为3～6岁幼儿、20～59岁成年人、60～79岁老年人[1]，采用多阶段分层整群随机抽样的方法，于2025年3月至6月从我国大陆31个省（区、市）的108个市（区、县）中抽取1815个幼儿园、机关、企事业单位、社区与行政村，最终纳入有效样本243585人，其中幼儿47523人、成年人147287人、老年人48775人。"
- **Weighting (verbatim, note [4]):** "本报告中，全国总体合格率和优良率以《第七次全国人口普查》数据为依据，对有效样本按性别、年龄组、城乡、省份等多维度进行了加权处理……为便于各组别间的直接比较，其他分组数据均为基于样本的原始计算率，未进行加权。" The note itself speaks of rates (率). I assume the appendix means by sex × age group are likewise unweighted sample statistics; the bulletin does not say so explicitly. Consistent with that assumption, the pooled 20–59 means in 图3/图4 equal the simple averages of the eight age-group means (D10.3).

**Table D8-a. Mean grip strength (握力, kg), 2025 (附表2-2 adults; 附表3-2 older adults)**

| Age group | Men | Women |
|---|---|---|
| 20–24 | 42.4 | 26.8 |
| 25–29 | 43.1 | 26.3 |
| 30–34 | 43.6 | 26.7 |
| 35–39 | 43.6 | 26.8 |
| 40–44 | 42.6 | 26.7 |
| 45–49 | 41.8 | 26.3 |
| 50–54 | 40.7 | 25.6 |
| 55–59 | 39.3 | 25.0 |
| 60–64 | 36.0 | 23.5 |
| 65–69 | 34.0 | 22.7 |
| 70–74 | 32.0 | 21.8 |
| 75–79 | 30.3 | 21.4 |

SD: not published.

Verbatim support (official page images `part/29323076.jpg`, `29323077.jpg`, `29323206.jpg`):
- "身体素质方面，成年人上肢与背部肌肉力量在40岁前增强、之后减弱……城镇人群在背部肌肉力量、下肢爆发力、肌肉耐力、柔韧性、平衡与反应能力方面优于乡村同龄人，但乡村人群上肢肌肉力量更好。"
- "反映肌肉力量的握力均值在男性中由60～64岁的36.0千克下降至75～79岁的30.3千克，女性中由23.5千克下降至21.4千克（附表3-2）。"
- "（九）成年人群力量素质仍呈持续下降 25年间，中国成年人肌肉力量呈持续下降趋势，其中男性群体下降更为明显。成年男性握力均值从2000年的45.8千克降至2025年的42.1千克，成年女性握力从28.4千克降至26.3千克。各年龄段成年人握力均出现下滑，其中以40～49岁年龄组的下降最为突出。"

### D8.2 Second source: 5th national physical fitness monitoring (第五次国民体质监测), 2020 data. verified = true

- **Citation:** 国家国民体质监测中心. 《第五次国民体质监测公报》. Official page on sport.gov.cn dated 2022-06-07 (来源: 体育科学研究所): https://www.sport.gov.cn/n315/n329/c24335066/content.html. The tables on that page are HTML text, and I extracted the numbers from that text. The gov.cn mirror shows the same tables as images (https://www.gov.cn/guoqing/2023-03/12/content_5745851.htm, images W020230404135670060838.jpg and W020230404135670159343.jpg). Both copies agree.
- **Design (verbatim):** "监测对象为3～6岁幼儿、20～59岁成年人和60～79岁老年人[1]。……采用多阶段分层随机整群抽样的方法，于2020年8月至12月从全国1732个机关、企事业单位、学校、幼儿园及行政村中抽取监测对象，获得有效样本202123人，其中幼儿40222人、成年人121928人、老年人39973人".

**Table D8-b. Mean grip strength (kg), 2020 (表2（续） adults; 表3（续） older adults)**

| Age group | Men | Women |
|---|---|---|
| 20–24 | 43.5 | 26.6 |
| 25–29 | 44.4 | 26.6 |
| 30–34 | 44.7 | 27.0 |
| 35–39 | 44.1 | 27.2 |
| 40–44 | 43.8 | 27.3 |
| 45–49 | 43.1 | 27.0 |
| 50–54 | 41.9 | 26.0 |
| 55–59 | 40.2 | 25.4 |
| 60–64 | 36.5 | 23.6 |
| 65–69 | 35.1 | 22.8 |
| 70–74 | 32.2 | 21.6 |
| 75–79 | 29.9 | 21.1 |

Verbatim support: "身体素质，以握力、背力为代表的最大肌肉力量随年龄增长表现为先升后降，其中男性开始下降的年龄拐点比女性早约5～10年" and "（七）成年人力量素质仍然呈下降趋势 ……男性握力和背力继续下降，女性背力继续下降，但女性握力有所改善。"

### D8.3 Historical context: 2014 national monitoring. verified = true

Read from the official page images `part/392039.png` (表6) and `part/392042.png` (表9) of https://www.sport.gov.cn/n315/n329/c216784/content.html (《2014年国民体质监测公报》, 发布时间 2015-11-25). Sample: adults 20–59 n = 146,703; older adults 60–69 n = 25,719.

**Table D8-c. Mean grip strength (kg), 2014**

| Age group | Men | Women |
|---|---|---|
| 20–24 | 44.9 | 26.3 |
| 25–29 | 45.3 | 26.3 |
| 30–34 | 45.3 | 26.9 |
| 35–39 | 45.4 | 27.3 |
| 40–44 | 44.9 | 27.1 |
| 45–49 | 43.6 | 26.5 |
| 50–54 | 42.4 | 25.6 |
| 55–59 | 40.3 | 24.8 |
| 60–64 | 37.3 | 23.2 |
| 65–69 | 35.0 | 22.3 |

The 2014 bulletin footnote [1] restricts who could be measured (verbatim): "监测对象要求身体健康，发育健全，无先天、遗传性疾病（如先天性心脏病、聋哑、痴呆、精神异常、发育迟缓等），以及急、慢性疾病（如心脏病、高血压等），具有一定的生活自理能力、语言表达能力、思维能力和接受能力，具有基本的运动能力。" I checked the 2020 and 2025 bulletin texts and the 6th-round 统计调查制度 (stats.gov.cn, 2025-06-05). None of them states a health criterion: the 2025 note [1] only says "教育部门负责组织实施学生体质与健康调研工作", and the 统计调查制度 defines 调查对象 only as "3-79周岁的中国公民（不含7-19周岁人群）". The 2020/2025 field protocols (监测工作方案) are not public. Assume the participants are an apparently healthy, ambulatory population that could perform the test, not all adults.

### D8.4 Distribution (SD and percentiles): China National Health Survey 2012–2017. verified = true

- **Citation:** He H, Pan L, Wang D, Liu F, Du J, Pa L, Wang X, Cui Z, Ren X, Wang H, Peng X, Zhao J, Shan G. "Normative values of hand grip strength in a large unselected Chinese population: Evidence from the China National Health Survey." *J Cachexia Sarcopenia Muscle* 2023;14(3):1312–1321. PMID 36999522; PMCID PMC10235885; DOI 10.1002/jcsm.13223. Full text read via Europe PMC.
- **Sample:** n = 39,655 aged 8–80, drawn by multistage stratified cluster sampling in **11 provinces**. The survey is large but does not cover all provinces.
- **Protocol (verbatim):** "using Jamar Hydraulic Hand Evaluation Kit (JAMAR, UK). After completing a practice test, each participant was asked to squeeze the dynamometer twice as hard as possible for 3 seconds, with at least 30 s rests between measurements, using the dominant arm, in a standing position with the arms extended straight down to the side. … Absolute hand grip strength was calculated as the largest reading".

**Table D8-d. Grip strength (kg), adults (Table 2 of He et al. 2023)**

| Age | Sex | n | P5 | P25 | P50 | P75 | P95 | Mean | SD |
|---|---|---|---|---|---|---|---|---|---|
| 20–29 | M | 1922 | 30 | 37 | 42 | 48 | 55 | 42.46 | 7.59 |
| 30–39 | M | 2874 | 30 | 37 | 42 | 47 | 55 | 42.12 | 7.56 |
| 40–49 | M | 4085 | 28 | 36 | 40 | 46 | 53 | 40.75 | 7.56 |
| 50–59 | M | 3362 | 26 | 32 | 37 | 42 | 51 | 37.61 | 7.66 |
| 60–69 | M | 2034 | 20 | 28 | 32.15 | 38 | 46 | 32.91 | 7.32 |
| 70–80 | M | 731 | 16 | 22 | 27 | 32 | 40 | 27.07 | 7.15 |
| 20–29 | F | 2998 | 16 | 21 | 24 | 28 | 33 | 24.44 | 5.02 |
| 30–39 | F | 4631 | 18 | 22 | 26 | 29 | 34 | 25.55 | 5.16 |
| 40–49 | F | 6400 | 16 | 22 | 25 | 28 | 34 | 24.96 | 5.25 |
| 50–59 | F | 4491 | 14 | 19 | 22 | 26 | 30 | 22.34 | 4.92 |
| 60–69 | F | 2521 | 12 | 17 | 20 | 23 | 28 | 19.95 | 4.76 |
| 70–80 | F | 820 | 10 | 14 | 17 | 20 | 25 | 17.31 | 4.75 |

The table labels age groups "20‐, 30‐, … 70–80". Verbatim abstract: "in men and women aged 20-80 were 39 (33, 44) kg and 24 (20, 27) kg, respectively." The same table also gives relative grip strength (HGS/BMI) by sex and age group.

### D8.5 Older adults including 80+: CHARLS + SAGE-China, unweighted percentiles. verified = true

- **Citation:** Grgic J, Tey SL, Huynh DTT, et al. "Asian Reference Values for Handgrip Strength, Gait Speed, Five-Times-Sit-to-Stand Test, Muscle Mass and Calf Circumference." *J Cachexia Sarcopenia Muscle* 2026;17(1):e70216. PMID 41674016; PMCID PMC12894420; DOI 10.1002/jcsm.70216. Supplementary docx (JCSM-17-e70216-s001.docx) downloaded from Europe PMC.
- **Data:** China = CHARLS waves 1–3 (2011, 2013, 2015) plus WHO SAGE-China wave 1 (2007–2010). Pooled n = 20,810 women and 18,944 men.
- **Method (verbatim):** "Reference values for handgrip strength were calculated for the dominant hand … When the dominant hand was not specified in the dataset, the hand with higher handgrip strength was considered as the dominant hand." CHARLS protocol (Suppl. file 3, verbatim): "Handgrip strength was assessed using a mechanical dynamometer with the participant in a standing (preferred), seated, or lying position. The arm was flexed at 90° (handshake position), and two attempts were made with both hands." Limitation (verbatim): "not all provided sampling weights, necessitating the use of unweighted percentiles".

**Table D8-e. Grip strength percentiles (kg), China (Supplementary files 18–19), ages 40–94.** Rows below age 40 have n ≤ 247 and are omitted (CHARLS samples people aged 45+ and their spouses).

| Age | Sex | n | P5 | P10 | P20 | P30 | P40 | P50 | P60 | P70 | P80 | P90 | P95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40–44 | M | 642 | 29.2 | 33.6 | 37.0 | 40.0 | 42.0 | 44.0 | 45.9 | 48.0 | 51.0 | 54.0 | 57.9 |
| 45–49 | M | 2,934 | 30.0 | 33.0 | 37.5 | 40.0 | 42.0 | 44.0 | 45.5 | 48.0 | 50.0 | 54.0 | 57.5 |
| 50–54 | M | 3,052 | 25.0 | 30.0 | 34.0 | 36.5 | 39.0 | 41.0 | 43.0 | 45.0 | 48.1 | 52.0 | 55.0 |
| 55–59 | M | 3,344 | 23.5 | 28.0 | 31.5 | 34.5 | 37.0 | 39.2 | 41.0 | 43.0 | 46.0 | 50.0 | 52.9 |
| 60–64 | M | 3,231 | 22.0 | 26.0 | 30.0 | 33.0 | 35.0 | 37.2 | 39.5 | 41.5 | 44.0 | 48.0 | 51.0 |
| 65–69 | M | 2,290 | 20.0 | 23.5 | 28.0 | 30.0 | 32.5 | 35.0 | 37.0 | 39.0 | 42.0 | 45.0 | 48.0 |
| 70–74 | M | 1,575 | 17.0 | 20.5 | 25.0 | 28.0 | 30.0 | 32.0 | 34.0 | 35.8 | 38.5 | 41.9 | 44.5 |
| 75–79 | M | 1,074 | 14.4 | 18.0 | 22.0 | 25.0 | 27.1 | 29.8 | 31.0 | 33.0 | 36.0 | 39.5 | 41.5 |
| 80–84 | M | 445 | 11.1 | 14.0 | 19.0 | 22.0 | 24.0 | 26.6 | 29.0 | 30.0 | 32.5 | 37.0 | 40.0 |
| 85–89 | M | 125 | 9.2 | 12.0 | 14.9 | 20.0 | 22.0 | 24.0 | 25.8 | 28.0 | 30.0 | 34.4 | 37.9 |
| 90–94 | M | 29 | 8.8 | 10.0 | 12.0 | 16.0 | 18.6 | 20.0 | 22.0 | 25.3 | 29.1 | 31.6 | 36.4 |
| 40–44 | F | 1,419 | 18.1 | 21.0 | 24.0 | 26.0 | 28.0 | 29.5 | 30.7 | 32.5 | 35.0 | 37.9 | 40.0 |
| 45–49 | F | 3,573 | 18.0 | 20.5 | 24.0 | 26.0 | 27.5 | 29.0 | 30.5 | 32.1 | 34.5 | 37.2 | 40.0 |
| 50–54 | F | 3,483 | 13.0 | 17.8 | 21.0 | 23.0 | 25.0 | 27.0 | 28.8 | 30.0 | 32.0 | 35.1 | 38.0 |
| 55–59 | F | 3,745 | 12.1 | 16.0 | 20.0 | 22.0 | 24.0 | 26.0 | 27.5 | 29.5 | 31.0 | 34.5 | 38.0 |
| 60–64 | F | 3,236 | 12.0 | 15.1 | 19.0 | 21.0 | 23.0 | 24.1 | 26.0 | 28.0 | 30.0 | 32.2 | 36.0 |
| 65–69 | F | 2,024 | 10.0 | 13.5 | 17.0 | 19.0 | 20.5 | 22.1 | 24.0 | 26.0 | 28.0 | 31.0 | 34.0 |
| 70–74 | F | 1,379 | 10.0 | 12.0 | 16.0 | 18.0 | 20.0 | 21.0 | 22.1 | 24.0 | 26.0 | 30.0 | 32.0 |
| 75–79 | F | 932 | 6.0 | 10.0 | 12.5 | 15.0 | 18.0 | 19.5 | 20.5 | 22.0 | 24.6 | 28.0 | 30.0 |
| 80–84 | F | 419 | 7.0 | 10.0 | 12.0 | 13.5 | 15.5 | 17.2 | 19.0 | 20.0 | 22.5 | 27.1 | 34.0 |
| 85–89 | F | 146 | 5.6 | 8.0 | 10.5 | 12.0 | 13.0 | 15.2 | 17.2 | 20.0 | 22.0 | 28.8 | 31.5 |
| 90–94 | F | 30 | 6.9 | 8.0 | 10.8 | 11.7 | 13.9 | 15.5 | 16.7 | 21.3 | 25.2 | 28.2 | 30.0 |

The CHARLS women's medians (29.0–29.5 kg at 40–49) are higher than the national monitoring means (26.3–26.8 kg) and the CNHS women 40–49 (P50 25 kg). Possible reasons, which I have not tested, are the dominant (or stronger) hand with the best of 2 attempts on each hand, a mechanical dynamometer in any posture, and unweighted samples. Do not mix sources within one z-score.

### D8.6 Protocol and clinical cut-offs

- **National monitoring grip protocol (2003 manual, latest retrievable).** 国家体育总局群体司《国民体质测定标准手册（成年人部分）》《……（老年人部分）》, 2003年4月. PDF copies are hosted at gh.nankai.edu.cn (…/54db755e-…pdf adult; …/c2695a7d-…pdf older). Verbatim: "使用握力计测试。测试时，受试者转动握力计的握距调节钮，调至适宜握距，然后用有力手持握力计，身体直立，两脚自然分开（同肩宽），两臂自然下垂，开始测试时，用最大力紧握上下两个握柄。测试两次，取最大值，记录以千克为单位，保留小数点一位。……如果受试者分不出有力手，双手各测试两次。" So the bulletin value is the maximum of two trials with the stronger hand, standing, arm hanging straight. The 2023 revised standard (征求意见稿, 国家国民体质监测中心, 2023-06, ciss.cn PDF) keeps 握力 for 20–59 and 60–79 but prints no protocol text, and the 2020/2025 bulletins do not state the device. Assume the protocol is unchanged, but this is unverified.
- **AWGS cut-offs.** AWGS 2019 (Chen LK et al. *J Am Med Dir Assoc* 2020;21(3):300–307.e2; PMID 32033882; DOI 10.1016/j.jamda.2019.12.012; abstract verbatim): "low muscle strength is defined as handgrip strength <28 kg for men and <18 kg for women". AWGS 2025 (as tabulated in Jianghan B et al. *Aging Medicine* 2026;9(2):89–98; PMID 42130757; PMC13163934; Table 1) keeps ≥65 y "Same as 2019" and adds 50–64 y: "M < 34 kg, F < 20 kg". Its text says AWGS 2025 still requires "mechanical spring or hydraulic type dynamometers, measuring 2–3 trials for each hand and recording the maximum value".

### D8 caveats
1. The bulletins give means only. For z-scores, borrow SDs from CNHS (men 7.15–7.66 kg, women 4.75–5.25 kg by decade). CNHS means run lower than the 2025 bulletin means: men by about 0–1 kg at 20–29, 1–2 kg at 30–49 and 2–3 kg at 50–59; women by about 1–3 kg. Pair the bulletin mean with the CNHS SD only as an explicit assumption.
2. The bulletin pooled 20–59 means are men 42.1 kg and women 26.3 kg (2025), and men 43.2 and women 26.6 (2020) (2025 bulletin 图3/图4). Each equals the simple average of the eight age-group means.
3. Secular trend: adult male grip has fallen across rounds (2014 → 2020 → 2025, e.g., men 20–24: 44.9 → 43.5 → 42.4). Use the 2025 table as the current reference.
4. Urban/rural: in 2025, rural adults have better upper-limb strength and urban older adults are weaker than rural ones (quotes above). The bulletin publishes no urban/rural cell means.
5. The national monitoring covers ages 20–79 only. Ages 80+ come from CHARLS/SAGE percentiles, which are unweighted and protocol-different.

> **Cross-reference.** Appendix A has CHARLS 2015 grip-strength percentiles (GAMLSS-smoothed, unweighted) by sex at ages 50-100, from Zhang L et al. 2025. It is a different CHARLS analysis from Grgic 2026 (D8.5).

---

## D9. Self-reported sleep duration

### D9-A. CCDRFS 2018 (nationally representative), verified

- **Citation:** Chen Y, Wang L, Zhang M, Hu SF, Shao Y, Zhang X, Li C, Chen J, Zhao ZP, Dong YH, Lu L, Zhou MG, Wang LM, Yuan JL, Sun HQ. The Increasing Trends of Short and Long Sleep Duration among Chinese Adults from 2010 to 2018: A Repeated Nationally Representative Cross-sectional Survey. *Biomed Environ Sci* 2026;39(1):46-59. doi:10.3967/bes2025.093. PMID 41582545. Full text: https://www.besjournal.com/en/article/doi/10.3967/bes2025.093. Supplementary Materials PDF: https://www.besjournal.com/fileSWYXYHJKX/journal/article/file/cf6224ef-175f-4765-a64b-df34c91e7ffd.pdf
- **Survey:** China Chronic Disease and Risk Factor Surveillance (CCDRFS) 2018, adults aged 18 and over, 184,153 analysed. Earlier rounds: 2010 n=97,741; 2013 175,749; 2015 187,777.
- **Question, verbatim:** "participants were asked, 'How long do you sleep in total on a typical day?' Responses were recorded to the minute." This is total sleep per day, so naps are presumably included.
- **Weighting, verbatim:** "standardized to the 2010 China census population".
- **Definitions, verbatim:** "short sleep duration was defined as ≤ 6 hours per day ... and long sleep duration was defined as > 9 hours per day. Optimal sleep duration was defined as 7–9 hours per day."
- **Headline result, verbatim:** "In 2018, the mean sleep duration among Chinese adults was 7.58 hours per day (SD: 1.45), and the prevalence of short and long sleep durations was 18.5% (95% CI : 17.7%–19.3%) and 9.0% (95% CI : 8.2%–9.9%), respectively ( Table 1 )."
- **Sex difference, verbatim:** "no significant differences were observed by sex or education" (mean sleep).

**Table 1 "Distributions of sleep duration among adults in China in 2018"**, copied exactly. Means are hr/d, mean ± SD; prevalences are % (95% CI).

| Group | Mean ± SD (h/d) | Short sleep ≤6 h, % (95% CI) | Long sleep >9 h, % (95% CI) |
|---|---|---|---|
| Overall | 7.58 ± 1.45 | 18.5 (17.7–19.3) | 9.0 (8.2–9.9) |
| Male | 7.56 ± 1.39 | 18.3 (17.4–19.1) | 8.6 (7.7–9.4) |
| Female | 7.59 ± 1.50 | 18.7 (17.8–19.7) | 9.5 (8.6–10.4) |
| Age 18–29 | 7.91 ± 1.27 | 9.6 (8.5–10.7) | 11.0 (9.5–12.6) |
| Age 30–39 | 7.69 ± 1.20 | 12.4 (11.4–13.3) | 7.4 (6.6–8.3) |
| Age 40–49 | 7.49 ± 1.32 | 19.0 (18.1–20.0) | 6.7 (5.9–7.6) |
| Age 50–59 | 7.29 ± 1.53 | 26.9 (25.7–28.1) | 7.4 (6.6–8.3) |
| Age 60–69 | 7.28 ± 1.75 | 30.2 (28.8–31.6) | 10.3 (9.3–11.4) |
| Age ≥70 | 7.34 ± 2.04 | 32.3 (30.4–34.1) | 15.2 (13.6–16.8) |
| Urban | 7.50 ± 1.33 | 18.5 (17.4–19.6) | 7.1 (6.3–7.8) |
| Rural | 7.66 ± 1.56 | 18.5 (17.4–19.5) | 11.2 (9.9–12.4) |

**Sex x age prevalence, 2018 column**, from Supplementary Table S2 (short sleep ≤6 h) and Supplementary Table S6 (long sleep >9 h): "Trends in prevalence of ... sleep duration among adults in urban and rural China from 2010 to 2018, by sex and age". Values are % (95% CI), standardised to the 2010 census.

| Residence | Sex | Age | Short ≤6 h 2018 | Long >9 h 2018 |
|---|---|---|---|---|
| Urban | Male | 18-29 | 11.6 (8.9, 14.3) | 9.6 (7.1, 12.2) |
| Urban | Male | 30-39 | 13.2 (11.4, 15.0) | 5.3 (4.2, 6.5) |
| Urban | Male | 40-49 | 21.2 (19.6, 22.9) | 4.5 (3.6, 5.4) |
| Urban | Male | 50-59 | 26.6 (24.9, 28.4) | 5.4 (4.5, 6.3) |
| Urban | Male | 60-69 | 28.5 (26.6, 30.4) | 8.5 (7.1, 9.8) |
| Urban | Male | ≥70 | 27.1 (24.7, 29.5) | 12.2 (10.3, 14.1) |
| Urban | Female | 18-29 | 8.9 (6.9, 11.0) | 9.5 (7.5, 11.4) |
| Urban | Female | 30-39 | 11.5 (9.9, 13.2) | 6.8 (5.4, 8.1) |
| Urban | Female | 40-49 | 19.0 (17.3, 20.7) | 5.2 (4.3, 6.0) |
| Urban | Female | 50-59 | 29.1 (27.1, 31.1) | 5.4 (4.5, 6.3) |
| Urban | Female | 60-69 | 35.2 (33.2, 37.1) | 6.4 (5.4, 7.4) |
| Urban | Female | ≥70 | 38.1 (35.7, 40.4) | 9.7 (8.0, 11.4) |
| Rural | Male | 18-29 | 9.2 (7.0, 11.4) | 11.5 (8.4, 14.6) |
| Rural | Male | 30-39 | 13.1 (11.5, 14.7) | 7.9 (6.5, 9.4) |
| Rural | Male | 40-49 | 18.8 (17.0, 20.7) | 7.1 (5.9, 8.3) |
| Rural | Male | 50-59 | 24.2 (22.7, 25.8) | 9.1 (7.8, 10.4) |
| Rural | Male | 60-69 | 26.9 (25.0, 28.8) | 13.1 (11.6, 14.6) |
| Rural | Male | ≥70 | 27.8 (25.6, 30.0) | 19.4 (17.5, 21.3) |
| Rural | Female | 18-29 | 8.1 (6.7, 9.5) | 14.5 (12.1, 16.9) |
| Rural | Female | 30-39 | 11.6 (10.0, 13.2) | 10.6 (9.0, 12.1) |
| Rural | Female | 40-49 | 16.9 (15.7, 18.2) | 10.4 (8.5, 12.3) |
| Rural | Female | 50-59 | 27.8 (25.8, 29.9) | 9.5 (7.9, 11.1) |
| Rural | Female | 60-69 | 30.8 (28.9, 32.8) | 12.2 (10.6, 13.7) |
| Rural | Female | ≥70 | 35.2 (32.4, 38.1) | 17.9 (15.1, 20.7) |

Verified: true. Values were read from the BES HTML full text (Table 1) and the publisher's Supplementary Materials PDF (Tables S2 and S6).

Caveats:
- Sleep is self-reported total sleep per day, naps included, with no separate night-sleep item.
- Mean sleep is not tabulated by sex x age, only by sex and by age separately. Use sex-specific SDs with age-group means, or the sex x age x residence prevalences.
- The ≥70 group has a wide SD (2.04).

### D9-B. Cross-check, CFPS 2018 (abstract only)

- **Citation:** Chu Y, Aune D, Yu C, et al. Temporal trends in sleep pattern among Chinese adults between 2010 and 2018: findings from five consecutive nationally representative surveys. *Public Health* 2023;225:360-368. doi:10.1016/j.puhe.2023.10.004. PMID 37981452. Data: China Family Panel Studies, adults aged 18 and over.
- **Verbatim (abstract):** "In 2018, the estimated average sleep duration in adults was 7.6 h/d. A shorter sleep duration, higher proportion of short sleep, and poor sleep quality were observed in people aged ≥65 years, women..."
- Verified: abstract only. The full text was not retrieved (paywalled).

### D9-C. Official CCDRFS 2018 report summary, consistent with D9-A, verified (text)

- **Source:** 中国疾病预防控制中心, 中国疾病预防控制中心慢性非传染性疾病预防控制中心 编著. 《中国慢性病及危险因素监测报告（2018）》. 人民卫生出版社, 2021. The summary (摘要) is at https://fwdbook.qq.com/read/1053696612/6; the page was retrieved.
- **Verbatim:** "2018年我国18岁及以上居民平均每日睡眠时间为7.6小时，18～44岁组（7.7小时）略高于其他年龄组。男女、城乡、地区差异均不大。"

---

## D10. VO2max / cardiorespiratory fitness

**Bottom line.** China's national fitness monitoring changed its adult cardiorespiratory test.
- **2000–2014:** the **台阶试验** (3-min step test). It reports a **台阶指数** (step index): test duration × 100 divided by the sum of three post-exercise heart rates. This is a heart-rate-recovery score, not a VO2max.
- **From 2020 (5th round) and in 2025 (6th round):** the **功率车二级负荷试验** (two-stage submaximal cycle-ergometer test). It reports a **心肺耐力测试值 in mL/kg/min**, which is an *estimated* VO2max.
- **Older adults (60–79) from 2020:** the **2分钟原地高抬腿** (2-min step-in-place count).

The bulletins publish means by sex × 5-year age group but no SD and not the estimation equation. Measured CPET reference values with SD and percentiles exist only from regional or hospital samples: Wang Y 2022 (community cycle CPET, Beijing + Guangxi, n = 1,114), Huang J 2024 (treadmill, Fujian, n = 4,199; abstract-level means only) and Wang J 2025 (hospital cycle CPET, Beijing, n = 9,155; overall means only).

### D10.1 What the national test measures

- **2020 switch.** 东方体育日报（新民晚报社）, 2020-07-20, A16, 章丽倩, "第五次国民体质监测 上海监测工作即将全面启动" (https://img1.xinmin.cn/dfsports/2020-07-20/A160720.pdf). This is a newspaper preview. Verbatim: "类似指标替代的情况还有，用功率车二级负荷试验代替台阶试验来测试成年人的心肺耐力，用握力代替网球掷远来测试幼儿的肌肉力量等。……老年人增加了２分钟原地高抬腿和３０秒坐站，用以测试心肺耐力和下肢肌肉力量及耐力。"
- **2023 standard.** 国家体育总局 Q&A on the 2023 revision (sport.gov.cn, 2023-06-12, https://www.sport.gov.cn/n20001280/n20001265/n20067533/c25697652/content.html; quoted from a fetched summary): "成年人纳入了BMI、体脂率、肺活量、功率车二级负荷试验、握力、纵跳（50-59岁成年人未纳入）" and "60-79岁老年人纳入了BMI、体脂率、肺活量、2分钟原地高抬腿、握力". The 2023 draft standard (ciss.cn PDF) has "表 2-10 男性成年人功率车二级负荷试验评分表 单位：毫升/千克/分钟".
- **What the number is.** 慧跑, 腾讯新闻, 2022-01-05 (https://news.qq.com/rain/a/20220105A083O000). This is a popular science article, not an official protocol. Verbatim: "这次采用了名为功率车二级负荷试验的心肺耐力测试方法，也即让受试者在功率车上完成2级运动负荷，通过评估做功和心率来评价心肺耐力，最终得到的指标是最大摄氧量。" and "国民体质监测所进行的功率车二级负荷试验虽然不是一个力竭性测试，但通过次极限负荷测试借助数学模型也可以推算得到最大摄氧量". The official load settings and prediction equation were **NOT FOUND** in any public document. The best lead is the 国家国民体质监测中心 test manual (《国民体质测定标准（2023年修订）》 full text or the 第五次/第六次监测工作方案).
- **Step test (2000–2014), 2003 manual, verbatim:** "反映人体心血管系统机能水平。使用台阶(男子台高30厘米,女子台高25厘米)、秒表和节拍器(频率为120次/分)……连续重复3分钟后,受试者立刻静坐在椅子上,记录运动停止后1分到1分半钟、2分到2分半钟、3分到3分半钟的三次脉搏数。……注意事项: 心血管疾病患者,不得进行此项测试。" Formula as given by Liu Y, Tremblay MS, Tomkinson GR, *J Exerc Sci Fit* 2021;19(4):216–222 (PMID 34381518; PMC8319019; DOI 10.1016/j.jesf.2021.07.001), verbatim apart from the fraction, which I rebuilt from the MathML: "STI=100t/(HR1+HR2+HR3) where STI = step test index, t = time (seconds) of the step test, HR1 = heart rate (bpm) at 1.0–1.5 min post-test, HR2 = heart rate (bpm) at 2.0–2.5 min post-test and HR3 = heart rate (bpm) at 3.0–3.5 min post-test." The step index is a recovery-heart-rate fitness score with no direct VO2max unit.

### D10.2 National estimated VO2max, 2025 (附表2-1, official page image `part/29323208.jpg`). verified = true

Source and URL as in D8.1. Verbatim: "身体机能方面，成年人肺活量与心肺耐力水平均随年龄组增加而逐渐下降。其中，……心肺耐力测试均值由46.2毫升/千克/分钟降低至36.9毫升/千克/分钟；……心肺耐力测试均值由41.1毫升/千克/分钟降低至31.0毫升/千克/分钟（附表2-1）。男性肺活量与心肺耐力均优于女性；城镇人群肺活量高于乡村人群，但心肺耐力水平基本相当。"

**Table D10-a. 心肺耐力测试值 (estimated VO2max, mL/kg/min); older adults: 2分钟原地高抬腿 (count/2 min) (附表3-1)**

| Age group | Men | Women |
|---|---|---|
| 20–24 | 46.2 | 41.1 |
| 25–29 | 44.4 | 39.8 |
| 30–34 | 43.6 | 39.0 |
| 35–39 | 43.2 | 38.2 |
| 40–44 | 43.2 | 35.6 |
| 45–49 | 42.7 | 35.3 |
| 50–54 | 37.4 | 31.1 |
| 55–59 | 36.9 | 31.0 |
| 60–64 (2-min step, count) | 57 | 61 |
| 65–69 (count) | 56 | 59 |
| 70–74 (count) | 53 | 55 |
| 75–79 (count) | 50 | 51 |

Older-adult quote (verbatim): "作为评估老年人心肺耐力的典型指标，2分钟原地高抬腿的完成次数在男性中从60～64岁的57次减少至75～79岁的50次，在女性中则从61次减少至51次（附表3-1）。男性肺活量优于女性，但心肺耐力略弱于女性。"

### D10.3 National estimated VO2max, 2020 (表2, sport.gov.cn HTML table; gov.cn image W020230404135669942570.jpg). verified = true

| Age group | Men (mL/kg/min) | Women (mL/kg/min) |
|---|---|---|
| 20–24 | 44.1 | 39.2 |
| 25–29 | 42.5 | 38.3 |
| 30–34 | 41.5 | 37.4 |
| 35–39 | 41.3 | 36.5 |
| 40–44 | 40.1 | 34.1 |
| 45–49 | 39.5 | 33.4 |
| 50–54 | 34.1 | 29.8 |
| 55–59 | 33.6 | 29.5 |
| 60–64 (2-min step, count) | 51.8 | 55.1 |
| 65–69 | 50.7 | 52.3 |
| 70–74 | 47.4 | 48.5 |
| 75–79 | 44.2 | 44.4 |

Verbatim (2020 bulletin): "身体机能，成年人身体机能各指标平均值随年龄增长呈下降趋势。男性身体机能指标平均值大于女性。城镇成年人肺活量高于乡村成年人，心肺耐力的城乡差异不明显。"

**2020 → 2025 comparison in the 2025 bulletin (official page image `part/29323200.jpg`, 图3 and 图4; verbatim text):** "与2020年监测相比，2025年成年男性……肺活量、心肺耐力、纵跳、1分钟仰卧起坐及坐位体前屈等水平均有提高，增幅为2.6%～19.6%；……握力、背力及闭眼单脚站立能力有所下降，降幅为2.5%～6.1%（图3）。" and "与2020年监测相比，2025年成年女性……心肺耐力、握力、背力及闭眼单脚站立能力则出现下降，降幅为0.8%～5.6%（图4）。"

The tables under 图3/图4 give pooled 20–59 means:

| Measure | Sex | 2025 | 2020 |
|---|---|---|---|
| 心肺耐力测试值 (mL/kg/min) | Men | 42.2 | 39.3 |
| 心肺耐力测试值 (mL/kg/min) | Women | 36.4 | 36.7 |
| 握力 (kg) | Men | 42.1 | 43.2 |
| 握力 (kg) | Women | 26.3 | 26.6 |

For older men (60–79, 图5) the pooled 2分钟原地高抬腿 count is 54 (2025) vs 49 (2020), and grip is 33.1 vs 33.5 kg.

**Inconsistency to flag.** Every age-specific 2025 women's CRF mean (Table D10-a) is 1.3–1.9 mL/kg/min higher than the matching 2020 bulletin value (Table above), yet the 2025 bulletin reports a pooled decline for women (36.7 → 36.4). The pooled grip values and the 2025 pooled CRF values equal the simple averages of the eight age-group means. Two numbers do not: the 2020 CRF comparators (women 36.7 vs 34.8 from the 2020 bulletin's own table; men 39.3 vs 39.6). This suggests the 2025 bulletin recomputed the 2020 CRF data (its note [5] says earlier rounds' pass rates were "回溯测算" under the 2023 standard), but it says nothing about how. **Do not splice 2020-bulletin CRF values with 2025 values.** Use the 2025 table as the reference.

### D10.4 Step index (台阶指数), 2014 (表6, sport.gov.cn image `part/392039.png`). verified = true. Historical; a different test

| Age | Men | Women |
|---|---|---|
| 20–24 | 56.1 | 56.8 |
| 25–29 | 55.9 | 57.3 |
| 30–34 | 56.1 | 57.7 |
| 35–39 | 56.6 | 58.5 |
| 40–44 | 57.8 | 59.5 |
| 45–49 | 58.0 | 60.1 |
| 50–54 | 58.0 | 60.5 |
| 55–59 | 58.2 | 60.1 |

Mean step index rises slightly with age, opposite to the expected age decline in VO2max. A plausible reason, which I infer and the source does not state, is lower recovery heart rates at older ages. The step index is therefore a different construct and cannot be mapped onto VO2max. Spread for the pooled 2000–2014 data, from Liu et al. 2021 Table 1 (verbatim): "Men | 302,386 | 57.4 ± 9.4"; "Women | 301,591 | 59.1 ± 9.9"; by age "20–29 years | 153,482 | 56.7 ± 8.8", "30–39 years | 153,107 | 57.5 ± 8.9", "40–49 years | 150,718 | 58.9 ± 9.7", "50–59 years | 146,670 | 58.8 ± 10.4".

### D10.5 Measured CPET VO2peak references (not nationally representative)

**(a) Community cycle CPET, Beijing and Hezhou (Guangxi), 2017–2018. verified = true**
- **Citation:** Wang Y, Li H, Wang J, Zhao W, Zeng Z, Hao L, Yuan Y, Lin Y, Wu Y, Wang Z. "Normal References of Peak Oxygen Uptake for Cardiorespiratory Fitness Measured with Cardiopulmonary Exercise Testing in Chinese Adults." *J Clin Med* 2022;11(16):4904. PMID 36013143; PMC9409785; DOI 10.3390/jcm11164904.
- **Sample and protocol:** n = 1,114 apparently healthy adults aged 20–79 from 4 communities (one urban and one rural in each of Beijing and Hezhou). Cycle ergometer (Ergosana320F), start 25 W, increment 25 W every 3 min, 50 r/min. Termination was conservative (≥85% predicted HRmax, 70% HRR, RPE ≥ 17, RER ≥ 1.1), so values are submaximal-biased. Verbatim limitation: "it would probably lead to a lower level of CRF".

**Table D10-b. Measured VO2peak (mL/kg/min), Table 4 of Wang Y et al. 2022**

| Age | Sex | n | Mean | SD | P2 | P5 | P10 | P25 | P50 | P75 | P90 | P95 | P98 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20–29 | M | 88 | 35.8 | 9.7 | 17.9 | 19.1 | 24.1 | 28.1 | 35.7 | 44.9 | 48.9 | 50.7 | 51.9 |
| 30–39 | M | 88 | 28.8 | 6.6 | 14.3 | 19.0 | 20.8 | 24.3 | 27.7 | 33.2 | 37.9 | 41.6 | 43.9 |
| 40–49 | M | 76 | 27.4 | 5.5 | 18.6 | 18.9 | 21.0 | 23.4 | 26.7 | 31.5 | 34.6 | 36.7 | 40.1 |
| 50–59 | M | 102 | 24.4 | 5.1 | 15.9 | 17.2 | 17.6 | 20.6 | 24.4 | 27.1 | 31.0 | 33.5 | 35.5 |
| 60–69 | M | 89 | 22.9 | 5.1 | 13.9 | 14.9 | 15.8 | 19.3 | 22.4 | 26.0 | 29.4 | 31.9 | 34.7 |
| 70–79 | M | 47 | 20.5 | 5.5 | 11.5 | 13.5 | 14.2 | 15.8 | 19.7 | 22.9 | 29.1 | 31.1 | 34.5 |
| 20–29 | F | 92 | 29.2 | 7.0 | 16.0 | 20.9 | 21.8 | 25.3 | 27.7 | 32.8 | 37.5 | 41.7 | 49.8 |
| 30–39 | F | 105 | 25.6 | 4.8 | 15.7 | 18.4 | 19.6 | 22.1 | 26.0 | 28.8 | 31.8 | 34.2 | 34.6 |
| 40–49 | F | 114 | 24.9 | 5.0 | 12.5 | 16.7 | 20.1 | 22.1 | 24.7 | 27.5 | 30.7 | 32.7 | 36.8 |
| 50–59 | F | 122 | 22.6 | 4.7 | 14.0 | 16.5 | 17.8 | 20.0 | 22.0 | 25.2 | 28.5 | 31.0 | 33.8 |
| 60–69 | F | 114 | 21.1 | 4.9 | 11.1 | 12.3 | 13.8 | 17.7 | 21.2 | 24.4 | 28.0 | 29.2 | 30.8 |
| 70–79 | F | 64 | 17.0 | 4.1 | 8.2 | 9.5 | 11.6 | 14.4 | 17.0 | 20.0 | 21.9 | 22.8 | 23.1 |

**(b) Treadmill CPET, Fujian (Fuzhou), healthy adults under 60. verified = true (abstract only; full text not open access)**
- **Citation:** Huang J, Yin L, Li X, Xie Q, He Y, Wu L, Ni X, Liu Z, Tao L, Tao J, Chen L. "Reference Standards of Cardiorespiratory Fitness Measured With the Cardiopulmonary Exercise Test Using the Treadmill in Chinese Adults Younger Than 60 Years." *J Cardiopulm Rehabil Prev* 2024;44(3):212–218. PMID 38488145; DOI 10.1097/hcr.0000000000000856.
- **Abstract, verbatim:** "Healthy participants (n = 4199) … The mean V˙O2peak values of four age groups (20-29, 30-39, 40-49, and 50-59 yr) were 42.6, 41.2, 38.7, and 35.9 mL/kg/min, respectively, for men, and 37.1, 34.7, 32.0, and 30.3 mL/kg/min, respectively, for women."
- SDs and percentiles are in the paywalled full text: NOT FOUND. The affiliation (Fujian University of Traditional Chinese Medicine) comes from the Europe PMC record.

**(c) Hospital cycle CPET, Peking University Third Hospital, 2017–2023. verified = true (overall only)**
- **Citation:** Wang J, Ren C, Xu S, et al. "A reference equation for peak oxygen uptake for cycle ergometry in Chinese adult participants." *Sci Rep* 2025;15:10876. PMID 40157952; PMC11954922; DOI 10.1038/s41598-025-94207-7.
- **Results:** derivation cohort n = 4,531 (age 18–88). Table 1, verbatim: "V̇O2peak (mL·kg−1·min−1) | 21.6 ± 6.1 | 24.0 ± 6.4 | 19.3 ± 4.7" (all/men/women). Sex × age relative values appear only as a figure (Fig. 2), so they are not tabulated here. Equation, verbatim: "V̇O2peak (mL·min−1) = −24364.9 − 621.3 × Sex (Women = 1, Men = 2) −10.7 × Age + 0.2 × Height2 (cm) + 6464.7 × Log(BMI) −24997.2 × Log(BSA) +12388.6 × Log(LBM)". This is a clinically referred, symptom-limited sample.

### D10 caveats
1. **Scale mismatch.** The national "心肺耐力测试值" is a submaximal-test estimate. For men 20–24 it is 46.2 mL/kg/min (2025), against measured VO2peak of 35.8 (community cycle, 20–29), 42.6 (treadmill, 20–29) and 24.0 overall (hospital cycle). Do not compare a user's measured CPET VO2peak, or a wearable's VO2max estimate, to the bulletin means without calibration. Within-source z-scores are safer. If the national means are used, an SD has to be borrowed (e.g., Wang Y 2022 SDs of about 5–10 mL/kg/min), and that is an assumption.
2. **Step changes at age bands.** In both 2020 and 2025, the adult estimate drops by 4–5 mL/kg/min between 45–49 and 50–54 (men 39.5 → 34.1 in 2020, 42.7 → 37.4 in 2025; women 33.4 → 29.8, 35.3 → 31.1). Women also drop between 35–39 and 40–44. These steps are larger than the neighbouring-age differences and fit age-banded loads or prediction equations, but no public document says so. Smooth across age bands rather than treating them as real physiological steps.
3. **Test changes.** 2000–2014 step-index values cannot be converted to the 2020+ VO2max estimates. Older adults (60–79) have no VO2max-type measure in the national monitoring; only the 2-minute step-in-place count exists.
4. **Population.** The 2014 round required healthy participants (D8.3 footnote), and the 2003 step-test protocol excluded "心血管疾病患者". The 2020/2025 bulletins publish no exclusion criteria, but cycle testing implies ability to exercise. Treat the norms as describing an apparently healthy, testable population.
5. **2020 vs 2025 CRF are not on a verified common scale.** See the inconsistency note in D10.3. Use the 2025 table.
6. **NOT FOUND.**
   - A peer-reviewed paper giving SDs or percentiles of the 2020/2025 national estimated VO2max. Lead: the 国家国民体质监测中心 book 《2020年国民体质监测报告》 (summary statistics with SDs and percentiles were published for 2000–2014 per Liu et al. 2021), or a CNKI search in 中国体育科技/体育科学.
   - A nationally representative measured-CPET norm. A registered study, "A Study on Cardiopulmonary Exercise Tolerance Standards for Healthy Chinese Population" (ClinicalTrials.gov NCT07108296), was seen only as a search-result title.

---

## D11. Average daily steps

### D11-A. Althoff et al. 2017 (smartphone accelerometry, Argus app), China row, verified

- **Citation:** Althoff T, Sosič R, Hicks JL, King AC, Delp SL, Leskovec J. Large-scale physical activity data reveal worldwide activity inequality. *Nature* 2017;547(7663):336-339. doi:10.1038/nature23018. PMID 28693034; PMCID PMC5774986. The China row is in Supplementary Information, Supplementary Table 1: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnature23018/MediaObjects/41586_2017_BFnature23018_MOESM1_ESM.pdf
- **Supplementary Table 1 title, verbatim:** "Summary of dataset statistics for the 46 countries with more than 1000 subjects (693,806 subjects in total; Methods). Countries are ordered by number of subjects in sample."
- **China row, verbatim:** "China 17427 6189 0.245 7553 (61.3) 4769 (38.7) 5105 (29.3) 28 5097 (29.2)". The columns are #subjects, Mean Steps, Activity Inequality, #male, #female, #genderNA, Median Age, #AgeNA.
- **Other rows, for context:** "Hong Kong SAR China 4754 6880 0.222 ..." and "Taiwan 4821 5000 0.262 ...".
- **Whole-sample figure, verbatim (main text):** "The average user recorded 4961 steps per day (standard deviation σ = 2684) over an average span of 14 hours."

| Population | n | Mean steps/day | SD | Notes |
|---|---|---|---|---|
| China (mainland row) | 17,427 | 6,189 | NR | 61.3% male (of known sex); median age 28 |
| Hong Kong SAR | 4,754 | 6,880 | NR | |
| All 111 countries | 717,527 | 4,961 | 2,684 | whole dataset |

Caveats:
- These are smartphone-carried step counts from self-selected app users: young, male-skewed, urban and affluent.
- Phones are not carried all day, so counts are lower than wrist or hip accelerometer counts.
- There is no sex or age breakdown for China.
- Data period, verbatim from Methods: "retrospective data collected between July 2013 and December 2014 from Apple iPhone smartphone users of the Azumio Argus app".

### D11-B. China Kadoorie Biobank 3rd resurvey, wrist accelerometer (Axivity AX3), 2020-2021, verified

- **Citation:** 张欣怡, 赵艺泽, 赵禹碹, 孙点剑一, 潘烺, 裴培, 杜怀东, 陈君石, 陈铮鸣, 吕筠, 李立明, Aiden Doherty, 余灿清. 中国10个地区中老年人步行活动特征分析. 中华流行病学杂志 2026;47(7):1199-1207. doi:10.3760/cma.j.cn112338-20251231-00939. PMID 42503948. Full text, opened in a browser: http://chinaepi.icdc.cn/zhlxbx/article/html/20260702
- **Sample, verbatim:** "共纳入20 246名研究对象，年龄（65.4±9.1）岁，男性7 034名，城市地区人群占41.4%". Measurement period 2020-08 to 2021-12. The device was worn on the dominant wrist for 7 days.
- **Step algorithm:** a self-supervised model trained on UK Biobank wrist data. Steps recorded during sleep or sedentary bouts were removed.

**Table 4** (sex; marginal means adjusted for age, sex and region; SE in parentheses), verbatim: "男 10 024.5（58.1）… 女 11 312.6（42.3）" daily steps.

**Table 2** (raw means, weekday vs weekend). The footnote says "括号内数据为SE", but the magnitudes (about 5,000) are clearly SDs.

| Sex | Weekday steps | Weekend steps | Weekday walking min | Weekend walking min |
|---|---|---|---|---|
| Men (n=7,034) | 9 897.0 (5 063.5) | 10 178.6 (5 684.2) | 160.3 (66.1) | 158.1 (70.2) |
| Women (n=13,212) | 11 248.5 (5 241.1) | 11 546.1 (5 786.3) | 170.0 (66.4) | 167.9 (70.0) |

**Table 3** (urban/rural x sex; adjusted for age and sex; SE in parentheses), daily steps:

| Sex | Urban | Rural |
|---|---|---|
| Men | 9 541.5 (93.9) | 10 262.1 (75.5) |
| Women | 10 472.4 (67.1) | 11 975.4 (57.6) |

**Age pattern, verbatim:** "每日步数与每日步行时间随年龄增长呈现先上升后下降的趋势，分别在60.7岁和62.3岁达到最高值" (Figure 3, restricted cubic spline). No age-group table is printed.

**Age composition (Table 1):**

| Age group | n (%) |
|---|---|
| 40~ | 384 (1.9%) |
| 50~ | 6,318 (31.2%) |
| 60~ | 7,173 (35.4%) |
| 70~ | 5,117 (25.3%) |
| ≥80 | 1,254 (6.2%) |

Caveats:
- Ten CKB areas, older adults (mean age 65). The authors state: "本研究基于中国10个地区的人群，研究样本的代表性有限".
- Wrist-worn counts run higher than smartphone counts; the authors note: "少数不产生身体位移的摆臂动作也可能被记录为步行，从而高估步行活动的水平".
- The abstract's "农村居民 … 每日步数10 262.1步" is the rural-men cell of Table 3, not a rural total.

### D11-C. Commercial wristband users, 2018 (dissertation), verified abstract

- **Citation:** Yan H. Walking steps and patterns of the Chinese adult population: A year-round study. PhD dissertation, University of Illinois Urbana-Champaign, 2024-04-26 (advisor Zhu W). https://hdl.handle.net/2142/124544
- **Verbatim:** "The original data with year-round information (N = 100,000) was obtained from the database of Shenzhen Lifesense Medical Electronics Company and 5,000 participants were randomly selected... data of 4,959 individuals remained... 3,191 participants were males and 1,768 were females, with an average age of 45.64 yr. (SD = 12.49 yr.). Findings revealed that the average daily step counts for the Chinese population in 2018 based on the year-round data was 13,641 ± 3,611, with males averaging 13,743 ± 3,664 steps per day and females 13,455 ± 3,505 steps per day."
- **Caveat:** these are self-selected device buyers ("86.13% of participants met this benchmark" of 10,000 steps). Do not use as a population norm.

**NOT FOUND:** a nationally representative, device-measured daily step count for Chinese adults by sex x age.
- Best lead 1: a CKB accelerometer age-group tabulation (data-access request).
- Best lead 2: WeChat 微信运动 annual reports, which are corporate and non-scientific, so they are not recommended.

---

## Appendix A. CHARLS 2015: smoothed percentiles by sex at ages 50-100 (SBP, DBP, pulse, BMI, waist, grip). verified

- **Source:** Zhang L, Yu J, Jia X, et al. *J Cachexia Sarcopenia Muscle* 2025;16(3):e13862. doi:10.1002/jcsm.13862. PMID 40511588; PMCID PMC12163542.
- **Where the numbers are:** Supplementary file JCSM-16-e13862-s003.doc, Tables S7 (males) and S8 (females), CHARLS column block. The tables were extracted programmatically from the publisher file after conversion to .docx, not retyped.
- **Sample:** CHARLS 2015 wave, n = 15,332, excluding pregnancy and prevalent cancer. Median age 60.0; 47.7% male; unweighted.
- **Method:** GAMLSS smoothing. Values are percentiles at exact age.
- **Caveats:** ages 90 and 100 are extrapolation-prone because few participants are that old. Extreme centiles (P1, P99) can reflect measurement outliers; for example, the waist P1 of about 41-55 cm is implausible.

**Systolic blood pressure, mmHg — Men (Table S7), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 92.9 | 100.8 | 113.7 | 124.0 | 135.8 | 155.9 | 172.8 |
| 60 | 93.3 | 101.9 | 116.0 | 127.4 | 140.6 | 163.3 | 182.8 |
| 70 | 93.8 | 103.0 | 118.4 | 131.0 | 145.7 | 171.4 | 193.9 |
| 80 | 95.4 | 104.9 | 120.8 | 133.9 | 149.1 | 176.0 | 199.5 |
| 90 | 98.6 | 107.9 | 123.5 | 136.2 | 150.8 | 176.4 | 198.5 |
| 100 | 102.1 | 111.1 | 125.9 | 137.9 | 151.5 | 174.9 | 194.9 |

**Diastolic blood pressure, mmHg — Men (Table S7), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 54.0 | 60.3 | 70.1 | 77.6 | 85.8 | 98.9 | 109.2 |
| 60 | 54.1 | 60.1 | 69.6 | 76.8 | 84.6 | 97.1 | 107.0 |
| 70 | 52.2 | 58.1 | 67.3 | 74.3 | 82.0 | 94.2 | 103.8 |
| 80 | 49.4 | 55.1 | 64.2 | 71.1 | 78.7 | 90.8 | 100.3 |
| 90 | 47.3 | 52.8 | 61.4 | 68.0 | 75.2 | 86.8 | 95.9 |
| 100 | 44.9 | 50.1 | 58.2 | 64.4 | 71.2 | 82.0 | 90.5 |

**Pulse — Men (Table S7), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 52.7 | 58.3 | 67.1 | 73.9 | 81.5 | 94.0 | 104.2 |
| 60 | 51.3 | 57.0 | 65.8 | 72.8 | 80.4 | 93.2 | 103.7 |
| 70 | 50.1 | 55.8 | 64.9 | 72.0 | 79.9 | 93.1 | 104.1 |
| 80 | 49.6 | 55.4 | 64.8 | 72.2 | 80.5 | 94.4 | 106.0 |
| 90 | 49.0 | 54.9 | 64.2 | 71.6 | 79.8 | 93.7 | 105.2 |
| 100 | 47.8 | 53.6 | 63.0 | 70.4 | 78.7 | 92.7 | 104.4 |

**Body mass index, kg/m2 — Men (Table S7), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 17.4 | 19.0 | 21.7 | 23.9 | 26.3 | 30.5 | 33.9 |
| 60 | 16.9 | 18.5 | 21.1 | 23.2 | 25.5 | 29.5 | 32.8 |
| 70 | 16.1 | 17.7 | 20.3 | 22.4 | 24.8 | 29.0 | 32.5 |
| 80 | 15.2 | 16.8 | 19.4 | 21.5 | 23.9 | 28.0 | 31.5 |
| 90 | 14.9 | 16.4 | 18.8 | 20.8 | 23.0 | 26.9 | 30.2 |
| 100 | 14.8 | 16.2 | 18.5 | 20.3 | 22.3 | 25.8 | 28.7 |

**Waist circumference, cm — Men (Table S7), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 52.7 | 67.4 | 80.8 | 87.9 | 94.5 | 105.0 | 114.3 |
| 60 | 51.4 | 66.0 | 79.2 | 86.3 | 92.9 | 103.2 | 112.5 |
| 70 | 47.7 | 63.3 | 77.4 | 84.9 | 91.9 | 102.7 | 112.4 |
| 80 | 45.4 | 61.3 | 75.8 | 83.4 | 90.5 | 101.5 | 111.3 |
| 90 | 43.3 | 59.6 | 74.6 | 82.4 | 89.6 | 100.9 | 110.9 |
| 100 | 41.4 | 58.1 | 73.4 | 81.4 | 88.7 | 100.2 | 110.4 |

**Grip strength, kg — Men (Table S7), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 21.4 | 28.5 | 36.9 | 42.1 | 47.2 | 54.8 | 60.7 |
| 60 | 17.7 | 24.7 | 32.8 | 37.9 | 42.8 | 50.1 | 55.9 |
| 70 | 13.8 | 20.4 | 28.1 | 32.8 | 37.5 | 44.4 | 49.7 |
| 80 | 8.1 | 14.5 | 22.4 | 27.3 | 32.0 | 38.9 | 44.3 |
| 90 | 4.4 | 9.7 | 17.3 | 22.1 | 26.7 | 33.4 | 38.7 |
| 100 | 2.3 | 6.2 | 12.8 | 17.2 | 21.4 | 27.6 | 32.4 |

**Systolic blood pressure, mmHg — Women (Table S8), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 89.0 | 96.7 | 109.4 | 119.8 | 131.6 | 151.9 | 168.9 |
| 60 | 91.3 | 99.7 | 113.8 | 125.5 | 138.9 | 162.2 | 182.1 |
| 70 | 95.0 | 104.2 | 119.9 | 132.8 | 147.9 | 174.4 | 197.3 |
| 80 | 97.7 | 107.7 | 124.7 | 139.0 | 155.7 | 185.5 | 211.6 |
| 90 | 98.0 | 109.0 | 128.0 | 144.1 | 163.5 | 198.6 | 230.2 |
| 100 | 96.5 | 108.5 | 129.7 | 148.2 | 170.8 | 213.1 | 252.7 |

**Diastolic blood pressure, mmHg — Women (Table S8), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 52.1 | 57.7 | 66.7 | 73.7 | 81.4 | 93.8 | 103.5 |
| 60 | 52.4 | 58.0 | 67.0 | 74.0 | 81.6 | 94.0 | 103.6 |
| 70 | 51.7 | 57.3 | 66.3 | 73.2 | 80.9 | 93.2 | 102.8 |
| 80 | 50.4 | 56.1 | 65.1 | 72.2 | 80.0 | 92.6 | 102.6 |
| 90 | 48.5 | 54.4 | 64.1 | 71.7 | 80.1 | 93.9 | 104.9 |
| 100 | 47.3 | 53.5 | 63.6 | 71.6 | 80.6 | 95.4 | 107.3 |

**Pulse — Women (Table S8), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 53.9 | 59.5 | 67.6 | 73.5 | 79.9 | 90.9 | 100.9 |
| 60 | 53.3 | 59.0 | 67.2 | 73.2 | 79.8 | 91.2 | 101.5 |
| 70 | 52.6 | 58.7 | 67.6 | 74.1 | 81.3 | 93.9 | 105.5 |
| 80 | 53.1 | 59.5 | 68.8 | 75.6 | 83.3 | 96.6 | 108.9 |
| 90 | 52.4 | 59.1 | 68.8 | 76.1 | 84.1 | 98.4 | 111.5 |
| 100 | 51.3 | 58.2 | 68.2 | 75.8 | 84.3 | 99.3 | 113.4 |

**Body mass index, kg/m2 — Women (Table S8), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 17.4 | 19.3 | 22.3 | 24.5 | 27.0 | 31.1 | 34.5 |
| 60 | 16.7 | 18.7 | 21.7 | 24.1 | 26.6 | 31.0 | 34.6 |
| 70 | 15.9 | 17.9 | 21.0 | 23.4 | 26.1 | 30.6 | 34.5 |
| 80 | 14.8 | 16.8 | 19.8 | 22.2 | 24.8 | 29.3 | 33.1 |
| 90 | 14.2 | 16.0 | 18.7 | 20.8 | 23.2 | 27.1 | 30.5 |
| 100 | 13.8 | 15.4 | 17.8 | 19.6 | 21.6 | 25.0 | 27.8 |

**Waist circumference, cm — Women (Table S8), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 50.9 | 66.4 | 79.4 | 86.1 | 92.2 | 102.2 | 111.7 |
| 60 | 49.1 | 65.7 | 79.8 | 86.9 | 93.5 | 104.1 | 114.2 |
| 70 | 45.9 | 63.8 | 79.3 | 87.0 | 94.1 | 105.6 | 116.4 |
| 80 | 45.0 | 62.9 | 78.4 | 86.1 | 93.3 | 104.7 | 115.5 |
| 90 | 49.2 | 64.4 | 77.3 | 83.8 | 89.9 | 99.7 | 109.0 |
| 100 | 54.7 | 66.2 | 76.0 | 81.0 | 85.7 | 93.5 | 101.0 |

**Grip strength, kg — Women (Table S8), CHARLS 2015 (GAMLSS-smoothed percentiles at exact age)**

| Age (y) | P1 | P5 | P25 | P50 | P75 | P95 | P99 |
|---|---|---|---|---|---|---|---|
| 50 | 11.7 | 17.1 | 23.6 | 27.7 | 31.7 | 37.7 | 42.5 |
| 60 | 9.4 | 14.6 | 20.9 | 24.9 | 28.7 | 34.5 | 39.0 |
| 70 | 6.4 | 11.4 | 17.6 | 21.5 | 25.4 | 31.1 | 35.6 |
| 80 | 3.4 | 7.8 | 13.9 | 17.9 | 21.7 | 27.5 | 31.9 |
| 90 | 1.5 | 4.5 | 10.7 | 15.1 | 19.4 | 25.9 | 31.0 |
| 100 | 0.8 | 2.8 | 8.8 | 14.0 | 19.4 | 27.7 | 34.2 |
