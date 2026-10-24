# Topic C — Cardiometabolic and lifestyle domains (all-cause mortality): verified parameters

Retrieved 2026-10-24. Every PMID/DOI below was shown in a Europe PMC REST record (or on the page cited) that was retrieved in this session. Numbers were read from the retrieved abstract, full text (PMC / Europe PMC XML / publisher PDF), supplementary appendix, or a figure image downloaded from the article. They were not taken from memory.

Conventions
- **95% CI** unless marked otherwise. Several CKB and CTT tables use **group-specific ("floating") CIs** or **99% CIs** for subgroups. This is flagged wherever it applies.
- **DERIVED** marks a number I calculated (for example a rescaled contrast). It is not a source value and must not be cited as one.
- **NOT VERIFIED / NOT REPORTED** means the number was not found in any source I could open.
- "Usual" BP or alcohol means the exposure corrected for regression dilution. A per-unit HR for a usual level is steeper than the HR for a single measured value.

---

## C1. Blood pressure

### C1a. Ettehad 2016 (RCT meta-analysis): all-cause mortality per 10 mmHg SBP reduction
- **Value:** RR **0.87** (95% CI **0.84–0.91**) per 10 mmHg lower SBP. Other outcomes: major CVD 0.80 (0.77–0.83), CHD 0.83 (0.78–0.88), stroke 0.73 (0.68–0.77), heart failure 0.72 (0.67–0.78).
- **Design:** 123 RCTs (613,815 participants) with at least 1000 patient-years per arm. Summary-level data pooled with inverse-variance fixed effects. Effects standardised per 10 mmHg by meta-regression. All-cause I² = 35%.
- **Adjustment:** randomised comparison (no covariate adjustment needed).
- **Source:** Ettehad D, Emdin CA, Kiran A, et al. *Lancet* 2016;387(10022):957–967. DOI 10.1016/S0140-6736(15)01225-8. PMID 26724178.
- **URL retrieved:** Europe PMC abstract (https://europepmc.org/article/MED/26724178).
- **Quote:** "Every 10 mm Hg reduction in systolic blood pressure significantly reduced the risk of major cardiovascular disease events (relative risk [RR] 0·80, 95% CI 0·77-0·83) … which, in the populations studied, led to a significant 13% reduction in all-cause mortality (0·87, 0·84-0·91)."
- **Caveats:** The populations are trial populations (mostly hypertensive or high-risk). The per-10 mmHg standardisation assumes proportionality. This estimate is steeper than the IPD result in C1b (see caveat there).

### C1b. Blood Pressure Lowering Treatment Trialists' Collaboration (BPLTTC) 2021 (IPD meta-analysis): per 5 mmHg SBP reduction
- **Major cardiovascular events, HR per 5 mmHg:**
  - overall **0.90 (0.88–0.92)**
  - no previous CVD 0.91 (0.89–0.94)
  - previous CVD 0.89 (0.86–0.92)
- **All-cause death, HR per 5 mmHg:**
  - overall **0.98 (0.96–1.01)**
  - previous CVD 0.97 (0.94–1.01)
  - no previous CVD 0.98 (0.95–1.02)
  - deaths: 13,021/161,477 intervention vs 15,874/182,126 comparator
- **CV death, HR per 5 mmHg:** 0.95 (0.92–0.99).
- **Design:** IPD from 48 RCTs, 344,716 participants, median follow-up 4.15 years. One-stage stratified Cox model, with effects standardised per 5 mmHg. Trials done only in heart-failure patients or in acute settings were excluded.
- **Source:** Blood Pressure Lowering Treatment Trialists' Collaboration. *Lancet* 2021;397(10285):1625–1636. DOI 10.1016/S0140-6736(21)00590-0. PMID 33933205. PMC8102467. The erratum (PMID 34022983) only updates the group list.
- **URL retrieved:** Europe PMC full-text XML of PMC8102467. Figure 3 image read directly from https://pmc.ncbi.nlm.nih.gov/articles/instance/8102467/bin/gr3.jpg.
- **Quotes:**
  - Abstract: "Hazard ratios (HR) associated with a reduction of systolic blood pressure by 5 mm Hg for a major cardiovascular event were 0·91, 95% CI 0·89-0·94 for partipants without previous cardiovascular disease and 0·89, 0·86-0·92, for those with previous cardiovascular disease."
  - Methods: "The secondary outcomes were all-cause death, death due to cardiovascular disease…"
  - All-cause values: Figure 3, row "All-cause death … Overall … 0·98 (0·96–1·01)".
- **Caveats:**
  - The all-cause effect over about 4 years is small and not statistically significant.
  - DERIVED: 0.98² ≈ 0.96 per 10 mmHg if log-linear. This is clearly weaker than Ettehad's 0.87. The difference comes from different trial sets, IPD versus tabular data, and different standardisation.
  - The methods paper should state which estimate is used and why.

### C1c. Lacey 2018 (China Kadoorie Biobank): usual SBP and vascular death
- **Vascular death:** HR **1.49 (1.47–1.51)** per 10 mmHg higher usual SBP at ages 40–79 years. Mean age at death 68; 10,480 vascular deaths.
- **Non-vascular mortality:** HR **1.07 (1.06–1.08)** per 10 mmHg.
- **All-cause mortality: NOT REPORTED** (no all-cause HR in the main text or appendix).
- **Age-specific HRs:** given for **incident major vascular disease**, not for vascular death. Per 10 mmHg usual SBP (Fig 2B):

  | Age at risk | HR (95% CI) |
  |---|---|
  | 40–49 | 1.67 (1.63–1.72) |
  | 50–59 | 1.44 (1.42–1.46) |
  | 60–69 | 1.36 (1.34–1.37) |
  | 70–79 | 1.22 (1.21–1.24) |
  | All ages | 1.36 (1.35–1.37) |

- **Cause-specific vascular death, per 10 mmHg (appendix Figure S2):**
  - intracerebral haemorrhage 1.67 (1.64–1.71)
  - ischaemic stroke 1.49 (1.43–1.56)
  - IHD 1.36 (1.32–1.39)
- **Design:** 512,891 adults aged 30–79 from 10 areas, recruited 2004–08. Median follow-up 9 years. Regression-dilution corrected using an approximately 5% resurvey; overall regression dilution ratio about 0.6.
- **Adjustment:** stratified or adjusted for age at risk (5-year groups), sex, area, education, smoking, alcohol and BMI.
- **Source:** Lacey B, Lewington S, Clarke R, et al. *Lancet Glob Health* 2018;6(6):e641–e649. DOI 10.1016/S2214-109X(18)30217-1. PMID 29773120. PMC5960069.
- **URL retrieved:** Europe PMC full-text XML. Figure 2 image. Appendix mmc1.pdf via the Europe PMC supplementaryFiles endpoint.
- **Quotes:**
  - "For vascular mortality at ages 40–79 years, each 10 mm Hg higher usual systolic blood pressure was associated with about a 50% higher risk of vascular death (HR 1·49 [95% CI 1·47–1·51]; mean age at death 68 years [SD 9]; appendix p 10). Non-vascular mortality was also positively associated with usual systolic blood pressure, although the risks were much weaker than those for vascular mortality 1·07 [1·06–1·08])."
  - "HRs for vascular disease were twice as steep at ages 40–49 years than at ages 70–79 years."
  - "At resurvey, about 3 years after the baseline survey, the overall regression dilution ratio for systolic blood pressure was 0·6…"
- **Caveats:**
  - HRs are per 10 mmHg of **usual** SBP. Applied to one measured SBP they overstate the association. DERIVED, approximate: 1.49^0.6 ≈ 1.27 per 10 mmHg of a single measurement.
  - These are observational associations.
  - Adjusting for BMI may partly block the BMI→BP pathway, but this is not a concern for a BP parameter.

### C1d. Lewington 2002 (Prospective Studies Collaboration)
- **Value:** At ages 40–69, each 20 mmHg higher usual SBP (≈10 mmHg usual DBP) is associated with:
  - **more than a twofold** difference in the stroke death rate
  - **twofold** differences in IHD and other vascular death rates
  - Proportional differences are **about half as extreme at 80–89 as at 40–49**.
  - No threshold down to 115/75 mmHg.
- **Design:** IPD from 61 prospective studies. About 1 million adults without vascular disease; 12.7 million person-years; about 56,000 vascular deaths. "Time-dependent" correction for regression dilution.
- **Source:** Lewington S, Clarke R, Qizilbash N, Peto R, Collins R; Prospective Studies Collaboration. *Lancet* 2002;360(9349):1903–1913. DOI 10.1016/S0140-6736(02)11911-8. PMID 12493255.
- **URL retrieved:** Europe PMC abstract (full text is not open access).
- **Quote:** "At ages 40-69 years, each difference of 20 mm Hg usual SBP (or, approximately equivalently, 10 mm Hg usual DBP) is associated with more than a twofold difference in the stroke death rate, and with twofold differences in the death rates from IHD and from other vascular causes. All of these proportional differences in vascular mortality are about half as extreme at ages 80-89 years as at ages 40-49 years…"
- **Caveats:** The age-specific numeric HRs (tables and figures of the full text) are **NOT VERIFIED** because the full text was not accessible. The data are mostly from Western cohorts.

---

## C2. Home versus office blood pressure

### C2a. 2018 ESC/ESH guidelines
- **Value:** home BP mean **≥135 and/or ≥85 mmHg** defines hypertension and corresponds to office **≥140/90 mmHg**.
- Other thresholds: ambulatory daytime ≥135/85, night ≥120/70, 24 h ≥130/80.
- **Source:** Williams B, Mancia G, Spiering W, et al. *Eur Heart J* 2018;39(33):3021–3104. DOI 10.1093/eurheartj/ehy339. PMID 30165516.
- **URL retrieved:** https://academic.oup.com/eurheartj/article/39/33/3021/5079119 (read with the WebFetch tool; direct download was blocked).
- **Quotes:**
  - Table 9 "Definitions of hypertension according to office, ambulatory, and home blood pressure levels": "Home BP mean ≥135 and/or ≥85". "Office BP ≥140 and/or ≥90" (footnote: "Refers to conventional office BP rather than unattended office BP.").
  - Section 4.4: "Compared with office BP, HBPM values are usually lower, … the diagnostic threshold for hypertension is ≥135/85 mmHg (equivalent to office BP ≥140/90 mmHg)".
- **Caveat:** The 2018 guideline text was read with a summarising web tool. The two fragments above were returned verbatim, but the tool split the sentence. Re-check against the PDF before quoting.

### C2b. Chinese guideline, 2018 revision (English version)
- **Value:** HBPM ≥135/85 mmHg corresponds to clinic 140/90 mmHg.
- **Source:** Joint Committee for Guideline Revision. 2018 Chinese Guidelines for Prevention and Treatment of Hypertension — A report of the Revision Committee of Chinese Guidelines for Prevention and Treatment of Hypertension. *J Geriatr Cardiol* 2019;16(3):182–241. DOI 10.11909/j.issn.1671-5411.2019.03.014. PMID 31080465. PMC6500570.
- **URL retrieved:** Europe PMC full-text XML.
- **Quote:** "The diagnostic thresholds of hypertension based on HBPM ≥ 135/85 mmHg, which is corresponding to 140/90 mmHg of clinic BP."

### C2c. 中国高血压防治指南（2024年修订版）
- **Value:** home BP (mean of all readings over 5–7 days) **≥135 and/or ≥85 mmHg** = hypertension.
- **Table 10, "与诊室血压对应的家庭血压和动态血压" (mmHg):**

  | Office | Home | 24 h ABPM | Daytime | Night |
  |---|---|---|---|---|
  | 140/90 | 135/85 | 130/80 | 135/85 | 120/70 |
  | 130/80 | **130/80** | 125/75 | 130/80 | 110/65 |

- **Source:** 中国高血压防治指南修订委员会, 高血压联盟（中国）, et al. 中华高血压杂志（中英文）2024;32(7):603–700. DOI 10.16439/j.issn.1673-7245.2024.07.002. No PMID found in Europe PMC.
- **URL retrieved:** PDF https://cjournal.hep.com.cn/1673-7245/CN/PDF/10.16439/j.issn.1673-7245.2024.07.002. Pages 613 and 617 were rendered and read.
- **Quotes:**
  - p.613: "根据诊室血压、家庭血压和动态血压以及患者服药情况，高血压的定义如下：在未使用降压药的情况下，非同日3次测量诊室血压≥140/90 mmHg；或连续5~7 d测量家庭血压≥135/85 mmHg；或24 h动态血压≥130/80 mmHg，白天血压≥135/85 mmHg，夜间血压≥120/70 mmHg。"
  - Table 7, 家庭血压 row: "连续5~7 d规范化测量家庭血压，所有测量血压读数的平均值 ≥135 和/或 ≥85".
  - p.617: "基于人群事件发生风险的与诊室血压140/90 mmHg相对应的家庭血压和动态血压数值[144]（表10），可考虑家庭血压目标<135/85 mmHg，24 h动态血压目标<130/80 mmHg。"
- **Modelling caveat:** The guideline's own equivalence table converges at lower levels: home 130/80 ≈ office 130/80. A fixed "office = home + 5/5" conversion is therefore supported only around the 135/85 ↔ 140/90 point.

---

## C3. LDL cholesterol

### C3a. CTT 2010: per 1.0 mmol/L LDL-C reduction
- **All-cause mortality:** RR **0.90 (0.87–0.93)** per 1.0 mmol/L, across all 26 trials.
- **Cause-specific deaths:**
  - CHD 0.80 (99% CI 0.74–0.87)
  - other cardiac 0.89 (99% CI 0.81–0.98)
  - stroke 0.96 (95% CI 0.84–1.09)
  - cancer and other non-vascular causes 0.97 (95% CI 0.92–1.03)
- **Major vascular events:** 0.78 (0.76–0.80).
- **Design:** IPD from 26 RCTs (21 statin vs control, n=129,526; 5 more vs less intensive, n=39,612). Median follow-up about 5 years.
- **Source:** Cholesterol Treatment Trialists' (CTT) Collaboration; Baigent C, Blackwell L, Emberson J, et al. *Lancet* 2010;376(9753):1670–1681. DOI 10.1016/S0140-6736(10)61350-5. PMID 21067804. PMC2988224.
- **URL retrieved:** Europe PMC abstract.
- **Quote:** "Across all 26 trials, all-cause mortality was reduced by 10% per 1·0 mmol/L LDL reduction (RR 0·90, 95% CI 0·87-0·93; p<0·0001)…"

### C3b. CTT 2012: low-risk individuals
- **All-cause mortality per 1.0 mmol/L, people without a history of vascular disease:** RR **0.91 (0.85–0.97)**, p=0.007.
  - Also excluding diabetes and CKD: 0.87 (0.78–0.95).
- **Any death, all participants (27 trials; appendix):** **0.91 (0.88–0.93)**. By 5-year major vascular event (MVE) risk, all participants (subgroup CIs are **99%**):
  - <5%: 0.97 (0.76–1.24)
  - 5–<10%: 0.89 (0.77–1.03)
  - 10–<20%: 0.91 (0.84–0.98)
  - 20–<30%: 0.92 (0.86–0.99)
  - ≥30%: 0.89 (0.83–0.96)
- **Major vascular events:** 0.79 (0.77–0.81).
- **Source:** Cholesterol Treatment Trialists' (CTT) Collaborators; Mihaylova B, Emberson J, Blackwell L, et al. *Lancet* 2012;380(9841):581–590. DOI 10.1016/S0140-6736(12)60367-5. PMID 22607822. PMC3437972.
- **URL retrieved:** Europe PMC full-text XML and appendix (supplementaryFiles; Webfigure 9).
- **Quote:** "In participants with no history of vascular disease, reduction of LDL cholesterol with statin therapy reduced the risk of vascular mortality (RR per 1·0 mmol/L reduction 0·85, 95% CI 0·77–0·95, p=0·004…) and, since there was no increase in the risk of non-vascular causes of death (RR 0·97, 95% CI 0·88–1·07…), reduced the risk of all-cause mortality (RR 0·91, 95% CI 0·85–0·97, p=0·007; appendix p 14)."

### C3c. Ference 2017 EAS consensus (context only: cumulative exposure)
- **Value:** about 20–25% lower ASCVD per mmol/L over 5 years of treatment, versus about 50–55% per mmol/L over 40 years of exposure. The 54% figure comes from Mendelian randomisation.
- **Source:** Ference BA, Ginsberg HN, Graham I, et al. *Eur Heart J* 2017;38(32):2459–2472. DOI 10.1093/eurheartj/ehx144. PMID 28444290. PMC5837225.
- **URL retrieved:** Europe PMC full-text XML.
- **Quotes:**
  - "…5 years of treatment with a lipid-lowering agent should reduce the relative risk of ASCVD by ∼20–25% per millimole per litre reduction in LDL-C, while 40 years of treatment (or approximately equivalently 40 years of exposure to lower LDL-C) would be expected to reduce ASCVD events by ∼50–55% per millimole per litre lower LDL-C."
  - Box 1: "Cumulative LDL arterial burden is a central determinant for the initiation and progression of atherosclerotic cardiovascular disease."
- **Caveat:** The outcome is ASCVD events, not all-cause mortality. Do not use as a mortality HR.

---

## C4. Glucose

### C4a. Bragg 2017 (China Kadoorie Biobank): diabetes versus no diabetes
- **All-cause mortality:** adjusted RR **2.00 (1.93–2.08)**.
- **By area:** rural 2.17 (2.07–2.29); urban 1.83 (1.73–1.94).
- **By age at risk:** 35–59: 2.41 (2.22–2.62); 60–69: 2.01 (1.88–2.14); 70–79: 1.84 (1.75–1.95).
- **By how diabetes was found:** previously diagnosed 2.20 (2.11–2.30); screen-detected 1.76 (1.67–1.86).
- **Duration:** each further 5 years since diagnosis, RR 1.13 (1.09–1.17).
- **Design:** 512,869 adults aged 30–79 from 10 areas, about 7 years of follow-up, 24,909 deaths. Diabetes = self-reported diagnosis, or screen-detected by random plasma glucose (≥7.0 mmol/L if fasted ≥8 h, or ≥11.1 mmol/L) or fasting glucose ≥7.0 mmol/L.
- **Adjustment:** education, smoking, alcohol, physical activity and BMI; stratified by area, age at risk and sex. **Not adjusted for BP or lipids.**
- **Source:** Bragg F, Holmes MV, Iona A, et al. *JAMA* 2017;317(3):280–289. DOI 10.1001/jama.2016.19720. PMID 28114552. PMC6520233.
- **URL retrieved:** Europe PMC abstract and PMC HTML (https://pmc.ncbi.nlm.nih.gov/articles/PMC6520233/).
- **Quote:** "Compared with adults without diabetes, individuals with diabetes had a significantly increased risk of all-cause mortality (1373 vs 646 deaths per 100 000; adjusted RR, 2.00 [95% CI, 1.93-2.08])…"

### C4b. Cai 2020 (meta-analysis): prediabetes, general population, all-cause mortality

| Definition | Range | RR (95% CI) | Comparisons |
|---|---|---|---|
| IFG-ADA | FPG 5.6–6.9 mmol/L | **1.07 (1.03–1.12)** | 20 |
| IFG-WHO | FPG 6.1–6.9 mmol/L | **1.13 (1.05–1.20)** | 19 |
| IGT | — | **1.25 (1.17–1.32)** | 15 |
| HbA1c-ADA | 5.7–6.4% | **1.09 (0.96–1.23)**, not significant | 8 |
| HbA1c-IEC | 6.0–6.4% | **1.21 (1.06–1.38)** | 4 |
| Overall prediabetes | — | 1.13 (1.10–1.17) | 87 |

- Also FPG 6.1–6.9 vs <5.6 mmol/L: 1.26 (1.16–1.36). FPG 5.6–6.05 was not associated with all-cause mortality.
- **Design:** 129 studies, 10,069,955 individuals. Random-effects pooling of adjusted RRs (maximally adjusted models).
- **Source:** Cai X, Zhang Y, Li M, et al. *BMJ* 2020;370:m2297. DOI 10.1136/bmj.m2297. PMID 32669282. PMC7362233.
- **URL retrieved:** Europe PMC full-text XML. Figure 2 image (PMC instance caix056552.f2.jpg) read directly.
- **Quote:** "…the risk of all cause mortality was significantly increased when prediabetes was defined as IFG-ADA (relative risk 1.07, 95% CI 1.03 to 1.12), IFG-WHO (1.13, 1.05 to 1.20), impaired glucose tolerance (1.25, 1.17 to 1.32), HbA1c-IEC (1.21, 1.06 to 1.38)… but not in studies with other definitions of prediabetes (fig 2)." The HbA1c-ADA value 1.09 (0.96–1.23), I² 78%, is from Figure 2.
- **Caveat:** Heterogeneity is high (overall I² 64%). The adjustment sets of the source cohorts differ.

### C4c. Selvin 2010 (ARIC): HbA1c and death from any cause, adults without diabetes
- **Design:** 11,092 Black and White US adults with no diabetes or CVD, followed for 15 years.
- **HR for death from any cause (reference HbA1c 5.0–<5.5%):**

  | HbA1c | Model 1a | Model 2a |
  |---|---|---|
  | <5.0% | 1.43 (1.17–1.74) | **1.48 (1.21–1.82)** |
  | 5.5–<6.0% | 1.34 (1.18–1.52) | **1.18 (1.04–1.35)** |
  | 6.0–<6.5% | 1.92 (1.63–2.27) | **1.59 (1.34–1.89)** |
  | ≥6.5% | 1.92 (1.54–2.40) | **1.65 (1.31–2.08)** |
  | per 1 percentage point | 1.21 (1.13–1.28) | 1.12 (1.05–1.21) |

  - Model 3a (adds fasting glucose): <5.0% 1.48 (1.21–1.81); 5.5–<6.0% 1.19 (1.05–1.35); 6.0–<6.5% 1.61 (1.35–1.91); ≥6.5% 1.71 (1.30–2.25). Per 1 point 1.18 (1.05–1.32).
  - Association is J-shaped.
- **Adjustment:**
  - Model 1a: age, sex and race.
  - Model 2a: Model 1a plus LDL-C, HDL-C, triglycerides, BMI, waist-to-hip ratio, hypertension, family history of diabetes, education, alcohol, physical activity and smoking.
- **Source:** Selvin E, Steffes MW, Zhu H, et al. *N Engl J Med* 2010;362(9):800–811. DOI 10.1056/NEJMoa0908359. PMID 20200384. PMC2872990 (author manuscript).
- **URL retrieved:** https://pmc.ncbi.nlm.nih.gov/articles/PMC2872990/ (Table 2).
- **Quote:** "For death from any cause, we observed a J-shaped association. Participants with glycated hemoglobin values in the lowest category (<5.0%) had a significantly higher risk of death from any cause as compared with those with glycated hemoglobin levels of 5.0 to less than 5.5%…"

---

## C5. BMI

### C5a. Global BMI Mortality Collaboration (GBMC) 2016
- **HR per 5 kg/m² above 25:**
  - overall **1.31 (1.29–1.33)**
  - **East Asia 1.39 (1.34–1.44)**
  - Europe 1.39 (1.34–1.43); North America 1.29 (1.26–1.32); Australia/New Zealand 1.31 (1.27–1.35)
  - by age at baseline: 1.52 (1.47–1.56) at 35–49 vs 1.21 (1.17–1.25) at 70–89
  - by sex: men 1.51 (1.46–1.56), women 1.30 (1.26–1.33)
- **Nadir:** 20.0–<25.0 kg/m². By age at baseline: BMI 22 (35–49), 23 (50–69), 24 (70–89).
- **All regions, reference 22.5–<25.0:**
  - 15.0–<18.5: **1.51 (1.43–1.59)**
  - 18.5–<20.0: 1.13 (1.09–1.17)
  - 20.0–<22.5: 1.00 (0.98–1.02)
  - 25–<27.5: 1.07 (1.07–1.08)
  - 27.5–<30: 1.20 (1.18–1.22)
  - 30–<35: 1.45 (1.41–1.48)
  - 35–<40: 1.94 (1.87–2.01)
  - 40–<60: 2.76 (2.60–2.92)
- **East Asia (Table 3; 46 studies, 1,074,385 participants, 100,784 deaths; floating CIs), reference 22.5–<25:**
  - 15–<18.5: **1.36 (1.25–1.49)**
  - 18.5–<20: 1.11 (1.04–1.18)
  - 20–<22.5: 0.99 (0.97–1.02)
  - 25–<27.5: 1.07 (1.04–1.11)
  - 27.5–<30: 1.28 (1.21–1.35)
  - 30–<35: 1.54 (1.42–1.67)
  - 35–<40: 2.01 (1.59–2.54)
  - 40–<60: 2.38 (1.33–4.24)
- **Design:** IPD from 239 studies (10.6 million people). The primary analysis was limited to 3.95 million never-smokers without chronic disease, excluding the first 5 years; 385,879 deaths.
- **Adjustment:** study, age and sex only.
- **Source:** Global BMI Mortality Collaboration; Di Angelantonio E, Bhupathiraju ShN, Wormser D, et al. *Lancet* 2016;388(10046):776–786. DOI 10.1016/S0140-6736(16)30175-1. PMID 27423262. PMC4995441.
- **URL retrieved:** Europe PMC full-text XML.
- **Quote:** "…with HR per 5 kg/m2 units higher BMI 1·31 (95% CI 1·29–1·33) overall, 1·39 (1·34–1·44) in east Asia, 1·39 (1·34–1·43) in Europe, 1·29 (1·26–1·32) in North America, and 1·31 (1·27–1·35) in Australia and New Zealand."
- **Caveat:** Restricting to healthy never-smokers limits reverse causation but makes the sample mostly women (stated by the authors).

### C5b. Zheng 2011 (Asia Cohort Consortium): East Asians
- **Lowest risk:** BMI **22.6–27.5**.
- **East Asians, all subjects, HR vs 22.6–25.0:**

  | BMI | HR (95% CI) |
  |---|---|
  | ≤15.0 | **2.76 (1.88–4.07)** |
  | 15.1–17.5 | 1.84 (1.65–2.05) |
  | 17.6–20.0 | 1.35 (1.25–1.45) |
  | 20.1–22.5 | 1.09 (1.05–1.14) |
  | 25.1–27.5 | 0.98 (0.95–1.01) |
  | 27.6–30.0 | 1.07 (1.02–1.12) |
  | 30.1–32.5 | 1.20 (1.10–1.32) |
  | 32.6–35.0 | 1.50 (1.31–1.71) |
  | 35.1–50.0 | **1.49 (1.31–1.69)** |

- **East Asian lifetime non-smokers:** ≤15.0: 2.43 (2.06–2.87); 35.1–50.0: 1.56 (1.31–1.86).
- **Design:** 19 cohorts, more than 1.1 million people (779,537 East Asians), about 120,700 deaths, mean follow-up 9.2 years. The first 3 years were excluded.
- **Adjustment:** age, sex, education, urban/rural residence, marital status and baseline illnesses.
- **Source:** Zheng W, McLerran DF, Rolland B, et al. *N Engl J Med* 2011;364(8):719–729. DOI 10.1056/NEJMoa1010679. PMID 21345101. PMC4008249 (author manuscript).
- **URL retrieved:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4008249/ (Table 2).
- **Quote:** "In the cohorts of East Asians, including Chinese, Japanese, and Koreans, the lowest risk of death was seen among persons with a BMI … in the range of 22.6 to 27.5. The risk was elevated among persons with BMI levels either higher or lower than that range — by a factor of up to 1.5 among those with a BMI of more than 35.0 and by a factor of 2.8 among those with a BMI of 15.0 or less."
- **Caveat:** The non-smoker ≤15.0 CI (2.06–2.87) is narrower than the all-subject CI despite fewer deaths. This is as printed in the author manuscript; check it against the NEJM version before citing.

---

## C6. Waist circumference (Jayedi 2020, BMJ)

- **Per 10 cm waist:** HR **1.11 (1.08–1.13)**, I² 88%, 50 studies.
  - **BMI-adjusted studies 1.17 (1.13–1.22)** (n=15); not BMI-adjusted 1.08 (1.05–1.10)
  - Asia 1.06 (1.01–1.12) (n=13)
  - age >60: 1.03 (0.98–1.08)
  - adjusted for BP, cholesterol and diabetes: 1.06 (0.99–1.13)
  - men 1.08 (1.04–1.13); women 1.12 (1.09–1.16)
- **Shape:** J-shaped, with risk lowest near 90 cm in men and flat to 80 cm in women.
- **Per 0.1 waist-to-height ratio (WHtR):** HR **1.24 (1.12–1.36)**, I² 94%, n=11.
  - BMI-adjusted 1.42 (1.16–1.69) (n=2)
  - men 1.13 (1.01–1.24); women 1.20 (1.07–1.32)
  - lowest risk at WHtR 0.50
- **Source:** Jayedi A, Soltani S, Zargar MS, Khan TA, Shab-Bidar S. *BMJ* 2020;370:m3324. DOI 10.1136/bmj.m3324. PMID 32967840. PMC7509947.
- **URL retrieved:** Europe PMC full-text XML (Table 1 and Results).
- **Quotes:**
  - "waist circumference (10 cm, 3.94 inch increase): 1.11 (95% confidence interval 1.08 to 1.13, I2=88%, n=50)…"
  - "waist-to-height ratio (0.1 unit increase): 1.24 (1.12 to 1.36, I2=94%, n=11)"
  - "…strengthened when we controlled for body mass index: hazard ratio 1.17 (1.13 to 1.22, I2=86%, n=15)."
- **Caveats:** Heterogeneity is very high. If BMI is already in the model, use the BMI-adjusted estimate. The attenuation with BP, lipid and diabetes adjustment shows mediation, which creates a double-counting risk when those markers are also scored.

---

## C7. Smoking

### C7a. Chen 2015 (CKB second study, deaths 2006–14, men aged 40–79)
- **Smokers vs never-smokers, all-cause RR:**
  - all men **1.33 (1.28–1.39)**
  - urban **1.65 (1.53–1.79)**
  - rural **1.22 (1.16–1.29)**
  - urban men who started before age 20: **1.98 (1.79–2.19)**; before 15: 2.64 (2.19–3.19)
  - rural men who started before 20: 1.39 (1.34–1.45), group-specific CI (Table 1)
- **Women:** RR 1.51 (1.40–1.63).
- **Attributable fraction:** PAF in the second study about 18% (urban 26%, rural 14%). "smoking will cause about 20% of all male deaths at ages 40–79 years during the 2010s".
- **Ex-smokers who stopped by choice:** overall RR 1.02 (0.95–1.10). By time since quitting:
  - <5 years: 1.21 (1.07–1.37)
  - 5–14 years: 1.00 (0.90–1.11)
  - ≥15 years: 0.98 (0.87–1.11)
- **Adjustment:** stratified by area and 5-year age at risk; adjusted for education and alcohol. "Smokers" includes people who stopped because of illness.
- **Source:** Chen Z, Peto R, Zhou M, et al. *Lancet* 2015;386(10002):1447–1456. DOI 10.1016/S0140-6736(15)00340-2. PMID 26466050. PMC4691901.
- **URL retrieved:** Europe PMC full-text XML.
- **Quotes:**
  - "urban male smokers who had started before age 20 years … had twice the never-smoker mortality rate (RR 1·98, 1·79-2·19…)"
  - "For men who had stopped by choice less than 5 years, 5–14 years, and 15 or more years before baseline, the RRs were 1·21 (1·07–1·37), 1·00 (0·90–1·11), and 0·98 (0·87–1·11) (trend p=0·01)."

### C7b. Chan 2022 (CKB, about 11 years of follow-up, ages 35–84)
- **Men:**
  - ever-regular smokers **1.33 (1.29–1.37)**
  - current smokers **1.33 (1.31–1.35)** (eTable 11, prior cancer not excluded; group-specific CI)
  - urban 1.50 (1.42–1.58); rural 1.25 (1.20–1.30)
  - urban men who started before 18: 2.06 (1.89–2.24)
  - ≥25 cigarettes/day: 1.50 (1.45–1.55)
- **Women:** 1.44 (1.36–1.52).
- **Ex-smokers:**
  - quit by choice: 1.06 (1.01–1.11)
  - quit because of illness: 1.61 (1.55–1.66)
  - by years since quitting (eFigure 26, point estimates only):
    - by choice: <5 y 1.17, 5–14 y 1.04, ≥15 y 0.99
    - illness: <5 y 1.93, 5–14 y 1.53, ≥15 y 1.29
- **Attributable fraction:** 19.6% of male deaths and 2.8% of female deaths.
- **Adjustment:** stratified by age at risk, area (and sex); adjusted for education and alcohol.
- **Source:** Chan KH, Wright N, Xiao D, et al. *Lancet Public Health* 2022;7(12):e1014–e1026. DOI 10.1016/S2468-2667(22)00227-4. PMID 36462513. PMC7613927.
- **URL retrieved:**
  - Europe PMC abstract (published version)
  - full text of the accepted manuscript (Europe PMC XML)
  - supplement docx (Europe PMC supplementaryFiles; eTable 11, eFigure 26)
- **Quote:** "those who had stopped voluntarily (i.e. before developing major diseases) only had small excess risks for overall mortality (1·06, 1·01-1·11) … with the risks approaching those among never smokers after about 5-10 years of quitting."
- **Answer to "when does excess risk largely disappear?":** after about 5–10 years for people who quit while healthy. People who quit because they were ill keep their excess risk beyond 15 years.

### C7c. Jha 2013 (US NHIS): years of life gained by quitting
- **Value:** quitting at 25–34 gains about **10** years; 35–44 about **9**; 45–54 about **6**; 55–64 about **4**. Current smokers lose more than 10 years of life expectancy.
- **HR for current vs never smokers (ages 25–79):** women 3.0 (99% CI 2.7–3.3); men 2.8 (99% CI 2.4–3.1).
- **Adjustment:** age, education, adiposity and alcohol.
- **Source:** Jha P, Ramasundarahettige C, Landsman V, et al. *N Engl J Med* 2013;368(4):341–350. DOI 10.1056/NEJMsa1211128. PMID 23343063.
- **URL retrieved:** publisher PDF hosted at https://www.dcp-3.org/sites/default/files/resources/NEJMsa1211128.pdf (nejm.org returned 403). Abstract also checked on Europe PMC.
- **Quotes:**
  - "Adults who had quit smoking at 25 to 34, 35 to 44, or 45 to 54 years of age gained about 10, 9, and 6 years of life, respectively…"
  - "Smokers who stopped smoking at 45 to 54 years of age and those who stopped at 55 to 64 years of age (median, 49 and 59 years, respectively) gained about 6 and 4 years of life, respectively."
- **Caveat:** This is a US population with Western, mature-epidemic hazards. Chinese RRs are lower at present (C7a, C7b).

---

## C8. Alcohol (China Kadoorie Biobank)

### C8a. Im 2023 (*Nature Medicine*): does not report all-cause mortality
- **Value:** **All-cause mortality NOT REPORTED.** The paper reports **all-cause morbidity** (hospitalised events) in male current drinkers: HR **1.12 (1.10–1.14)** per 280 g/week.
- **Other estimates, per 280 g/week:** WHO alcohol-related diseases 1.22 (1.19–1.25). Genotype-predicted intake and WHO-defined alcohol-related diseases: 1.14 (1.09–1.20).
- **Adjustment:** stratified by age at risk and area; adjusted for education and smoking.
- **Source:** Im PK, Wright N, Yang L, et al. *Nat Med* 2023;29(6):1476–1486. DOI 10.1038/s41591-023-02383-8. PMID 37291211. PMC10287564.
- **URL retrieved:** Europe PMC full-text XML.
- **Quote:** "Overall, for all-cause morbidity, the HR per 280 g per week higher intake was 1.12 (1.10–1.14) in male current drinkers."

### C8b. Millwood 2023 (*Lancet Public Health*): the CKB all-cause mortality paper
- **Per 100 g/week usual intake (male current drinkers):**
  - observational **1.18 (1.15–1.20)**
  - genetic (ALDH2/ADH1B) **1.07 (1.05–1.10)**
  - polygenic score 1.10 (1.05–1.16) in the main text. Appendix Webtable 16 prints 1.10 (1.04–1.15) per 100 g/week, a minor discrepancy.
- **Men, all causes (Webtable 9; 19,899 deaths; reference <140 g/week; group-specific CIs):**

  | Group | HR (95% CI) |
  |---|---|
  | Non-drinkers | 1.34 (1.30–1.38) |
  | Ex-drinkers | 1.41 (1.35–1.48) |
  | Occasional | 1.02 (0.99–1.04) |
  | <140 g/wk | 1.00 (0.95–1.05) |
  | 140–279 g/wk | **1.21 (1.16–1.27)** |
  | 280–419 g/wk | **1.38 (1.31–1.47)** |
  | ≥420 g/wk | **1.69 (1.60–1.78)** |

- **Adjustment:** stratified by age at risk and area; adjusted for education, household income, smoking, physical activity and fruit intake. Participants with prior chronic disease were excluded.
- **Source:** Millwood IY, Im PK, Bennett D, et al. *Lancet Public Health* 2023;8(12):e956–e967. DOI 10.1016/S2468-2667(23)00217-7. PMID 38000378. PMC7615754.
- **URL retrieved:** Europe PMC abstract and full-text XML. Appendix: https://ars.els-cdn.com/content/image/1-s2.0-S2468266723002177-mmc1.pdf.
- **Quotes:**
  - "Among current drinkers, each 100 g/week higher alcohol intake was associated with higher mortality risks from … all causes (HR 1·18 [95% CI 1·15-1·20])."
  - "Genotype-predicted alcohol intake was uniformly and positively associated with risks of death from all causes (n=12 939; HR 1·07 [95% CI 1·05-1·10])"
  - "There was no genetic evidence of protection from moderate drinking…"
- **DERIVED, not reported (log-linear rescaling to 280 g/week):** observational 1.18^2.8 ≈ 1.59 (1.48–1.67); genetic 1.07^2.8 ≈ 1.21 (1.15–1.31).
- **Caveat:** The Webtable 9 footnote says "per 280 g/week", but the column header and the main text say per 100 g/week. I have used per 100 g/week.

### C8c. Im 2020 (*Addiction*): heavy and problem drinking
- **Men who are current regular drinkers without chronic disease (n=57,166), all-cause HR vs low-risk drinkers (<200 g/week, no heavy episodic drinking, no problem indicators):**
  - high-risk drinkers (≥200 g/week or heavy episodic drinking): **1.28 (1.21–1.35)**
  - 1 problem-drinking indicator: 1.37 (1.28–1.46)
  - 2 or more indicators: **1.91 (1.71–2.13)**
- **Adjustment:** stratified by age at risk and region; adjusted for education, income, smoking, fruit intake, physical activity and BMI.
- **Source:** Im PK, Millwood IY, Chen Y, et al. *Addiction* 2020;115(5):850–862. DOI 10.1111/add.14873. PMID 31692116. PMC7156287.
- **Quote:** "…adjusted HRs of 1.00 (95% CI = 0.94–1.06) for low‐risk drinkers, 1.28 (95% CI = 1.21–1.35) for high‐risk drinkers, 1.37 (95% CI = 1.28–1.46) and 1.91 (95% CI = 1.71–2.13) for drinkers with one and two or more problem drinking indicators".

---

## C9. eGFR (CKD Prognosis Consortium; Matsushita 2010) — context only

- **All-cause HR vs eGFR 95 (mL/min/1.73 m²):**
  - eGFR 60: **1.18 (1.05–1.32)**
  - eGFR 45: **1.57 (1.39–1.78)**
  - eGFR 15: **3.14 (2.39–4.13)**
  - **eGFR 30: NOT REPORTED.** The spline knots are at 15, 45, 60, 75, 90, 105 and 120. The text says risk "was 2-fold higher around eGFR 30-45". DERIVED geometric interpolation between 15 and 45: √(3.14×1.57) ≈ 2.2; do not cite as a source value.
- **Risk shape:** flat from eGFR 75 to 105; U-shaped above 105.
- **ACR (vs 5 mg/g):** 10 mg/g 1.20 (1.15–1.26); 30 mg/g 1.63 (1.50–1.77); 300 mg/g 2.22 (1.97–2.51).
- **Design:** 14 general-population cohorts with ACR (n=105,872).
- **Adjustment:** age, sex, race, CVD history, SBP, diabetes, total cholesterol and smoking; eGFR and ACR adjusted for each other.
- **Source:** Chronic Kidney Disease Prognosis Consortium; Matsushita K, van der Velde M, Astor BC, et al. *Lancet* 2010;375(9731):2073–2081. DOI 10.1016/S0140-6736(10)60674-5. PMID 20483451. PMC3993088.
- **URL retrieved:** https://pmc.ncbi.nlm.nih.gov/articles/PMC3993088/ (text and Figure 2).
- **Quote:** "As compared to eGFR 95 ml/min/1·73 m2, HRs for all-cause mortality at eGFR 60, 45, and 15 ml/min/1·73 m2 were 1·18 (95% CI: 1·05-1·32), 1·57 (1·39-1·78), and 3·14 (2·39-4·13) for all-cause mortality."

---

## Cross-cutting caveats for the methods paper

1. **RCT versus cohort slopes differ:**
   - For BP, the cohort association with vascular death (usual SBP, 1.49 per 10 mmHg) is far steeper than the trial effect on all-cause mortality (0.87 per 10 mmHg in Ettehad; 0.98 per 5 mmHg in BPLTTC).
   - For LDL-C, trials give about 0.90 per mmol/L over about 5 years. Ference argues the lifetime effect is larger, but for ASCVD, not all-cause mortality.
2. **Regression dilution:** Lacey HRs (and Millwood dose-response) are per **usual** exposure. A user's single reading should not be scored with the usual-exposure slope without correction.
3. **Adjustment sets and double counting:**
   - Bragg (diabetes) and Lacey (BP) adjust for BMI.
   - Jayedi's waist estimate attenuates after BP, lipid and diabetes adjustment.
   - Selvin adjusts HbA1c for lipids, BMI and hypertension.
   - Multiplying domain HRs that are each mediated through BP or glucose risks double counting.
4. **Reference groups:**
   - The CKB alcohol reference is light drinkers (<140 g/week) or occasional drinkers, not never-drinkers. Non-drinkers and ex-drinkers have high observational HRs from sick-quitter effects.
   - CKB smoking "smokers" include people who quit because of illness.
5. **CI types:** CKB tables, CTT subgroups and GBMC regional tables use floating (group-specific) or 99% CIs. Cite them as such.
