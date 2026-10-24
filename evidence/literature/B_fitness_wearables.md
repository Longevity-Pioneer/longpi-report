# Topic B: Fitness, function and wearable domains (all-cause mortality): verified parameters

Retrieved 2026-10-24 by a literature-verification subagent for the LongPi methods paper.

## How each number was checked

- Bibliographic records (PMID, DOI, PMCID) come from the Europe PMC REST API. Every PMID and DOI below was re-checked with `query=EXT_ID:<pmid> AND SRC:MED` (`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:<pmid>%20AND%20SRC:MED&resultType=core&format=json`). Abstracts were read from the same records.
- Full texts were read from one of three places:
  - Europe PMC full-text XML (`https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`);
  - NCBI E-utilities PMC XML (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=<id>&rettype=xml`);
  - the PMC article page through WebFetch (`https://pmc.ncbi.nlm.nih.gov/articles/<PMCID>/`). WebFetch returns a model-rendered summary and limits verbatim quotes to about 125 characters, so quotes obtained this way are tagged **[WF]**.
- Status tags used below:

| Tag | Meaning |
|---|---|
| **FT** | Value read in the full text or its table. |
| **ABS** | Value read in the abstract only. |
| **WF** | Value read through a WebFetch rendering of the PMC page. |
| **DERIVED** | My own arithmetic on verified numbers. It is not a published value and is labelled wherever it appears. |
| **NOT VERIFIED** | Could not be confirmed from a retrieved source. |

- Some publisher sites returned 403 or a bot-check page: JAMA, The Lancet, Mayo Clinic Proceedings/ScienceDirect, and one repository. Those papers are verified at abstract level only, and this is stated in each entry.

---

## B1. Cardiorespiratory fitness (CRF) and all-cause mortality

### B1a. Kodama 2009 (JAMA): per 1-MET higher maximal aerobic capacity (ABS)

- **Value:** RR **0.87** (95% CI **0.84–0.90**) for all-cause mortality per 1-MET (3.5 mL·kg⁻¹·min⁻¹) higher maximal aerobic capacity (MAC).
  - For CHD/CVD events the RR is 0.85 (0.82–0.88).
  - Categorical: low CRF (<7.9 METs) vs high CRF (≥10.9 METs) RR 1.70 (1.51–1.92). Low vs intermediate CRF (7.9–10.8 METs) RR 1.40 (1.32–1.48).
- **Population and design:** meta-analysis of 33 observational cohorts of healthy men and women. All-cause mortality: 102,980 participants and 6,910 cases. Random-effects pooling. CRF was measured or estimated as MAC in METs.
- **Adjustment:**
  - The abstract describes study-level estimates pooled by random effects. The categorical RRs are "adjusting for heterogeneity of study design".
  - The covariate sets of the contributing studies were not verified, because the full text returned 403.
  - Lang 2024 (B1b) rates this review AMSTAR-2 "critically low" and lists its per-1-MET analysis as 18 studies with 85,315 participants.
- **Source:** Kodama S, Saito K, Tanaka S, et al. *JAMA* 2009;301(19):2024–2035. DOI 10.1001/jama.2009.681. PMID 19454641.
- **URL retrieved:** Europe PMC REST record for PMID 19454641. The publisher page https://doi.org/10.1001/jama.2009.681 returned 403.
- **Quote (abstract):** "Pooled RRs of all-cause mortality and CHD/CVD events per 1-MET higher level of MAC (corresponding to 1-km/h higher running/jogging speed) were 0.87 (95% confidence interval [CI], 0.84-0.90) and 0.85 (95% CI, 0.82-0.88), respectively."
- **Caveats:**
  - The contributing cohorts are mostly male and Western. Whether they include Japanese cohorts was not verified.
  - **DERIVED:** per 1 mL·kg⁻¹·min⁻¹, 0.87^(1/3.5) ≈ 0.961.

### B1b. Lang 2024 (BJSM) overview of meta-analyses (FT)

- **Value:** per 1-MET higher CRF, all-cause mortality HR **0.89 (0.86–0.92)** and **0.83 (0.78–0.88)**, which the authors express as "11%–17%".
  - High vs low CRF: HR 0.47 (0.39–0.56).
  - These figures are the overview's re-extraction of individual meta-analyses, matched by value:
    - 0.89 (0.86–0.92) is **Laukkanen 2022** (B1c);
    - 0.83 (0.78–0.88) is **Qiu 2021**, which used *non-exercise estimated* CRF (B1e);
    - 0.47 (0.39–0.56) is **Han 2022**, highest vs lowest CRF (B1d).
- **Design:** 26 systematic reviews, more than 20.9 million observations, 199 cohorts. Certainty of evidence by GRADE ranged from very low to moderate.
- **Adjustment:** inherits that of each meta-analysis. RRs were treated as HRs, and dose-response values were rescaled to 1 MET on the log scale.
- **Source:** Lang JJ, Prince SA, Merucci K, et al. *Br J Sports Med* 2024;58(10):556–566. DOI 10.1136/bjsports-2023-107849. PMID 38599681. PMCID PMC11103301.
- **URL retrieved:** https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11103301/fullTextXML
- **Quotes:**
  - "A dose–response relationship for every 1-metabolic equivalent of task (MET) higher level of CRF was associated with a 11%–17% reduction in all-cause mortality (HR=0.89; 95% CI 0.86 to 0.92, and HR=0.83; 95% CI 0.78 to 0.88)."
  - Text: "For example, there were 1 858 274 male participants compared with 180 202 female participants for all-cause mortality."
- **Caveat:** the evidence is male-dominated, as the second quote shows.

### B1c. Laukkanen 2022 (Mayo Clin Proc): per 1-MET (ABS)

- **Value:** RR **0.89 (0.86–0.92)** per 1-MET increase. Top vs bottom tertile RR 0.55 (0.50–0.61).
- **Design:** 37 cohorts, 2,258,029 participants, 108,613 deaths. Objectively assessed CRF. The per-1-MET analysis used 10 studies with n = 360,131, according to Lang 2024 Table 1.
- **Adjustment:** "pooled multivariable-adjusted RR". The association did not differ by publication year, age, sex, follow-up, CRF method or risk of bias. Region is not reported in the abstract.
- **Source:** Laukkanen JA, Isiozor NM, Kunutsor SK. *Mayo Clin Proc* 2022;97(6):1054–1073. DOI 10.1016/j.mayocp.2022.02.029. PMID 35562197.
- **Quote:** "For every 1-MET increase in CRF, the RR for all-cause mortality was 0.89 (95% CI, 0.86 to 0.92)."

### B1d. Han 2022 (BJSM, authors based in China): per 1-MET (ABS)

- **Value:** RR **0.88 (0.83–0.93)** for all-cause mortality per 1-MET. Highest vs lowest CRF 0.47 (0.39–0.56).
- **Design:** 34 cohorts. CRF measured by exercise test. Dose-response by generalised least squares.
- **Source:** Han M, Qie R, Shi X, et al. *Br J Sports Med* 2022;56(13):733–739. DOI 10.1136/bjsports-2021-104876. PMID 35022163.
- **Quote:** "The pooled relative risks (RRs) for all-cause, CVD and cancer mortality per one-metabolic equivalent increase in CRF were 0.88 (95% CI 0.83 to 0.93)..."

### B1e. Qiu 2021 (Atherosclerosis): non-exercise estimated CRF (ABS)

- **Value:** HR **0.83 (0.78–0.88)** per 1-MET higher eCRF for all-cause mortality (14 datasets).
- **Design:** 8 cohorts, more than 170,000 participants. eCRF is computed by algorithm from age, sex, BMI, resting heart rate and physical activity.
- **Source:** Qiu S, Cai X, Sun Z, Wu T, Schumann U. *Atherosclerosis* 2021;330:22–28. DOI 10.1016/j.atherosclerosis.2021.06.904. PMID 34225102.
- **Caveat:** this is not measured CRF. If LongPi also uses resting heart rate (B5), an eCRF-based HR would partly double-count it.

### B1f. East Asian cohorts with measured CRF

- **Korean men, Park 2009 (ABS).** n = 18,775, 547 deaths, mean follow-up 6.4 years. Fitness was measured as maximal oxygen uptake.
  - Middle vs lowest tertile HR 0.58 (0.47–0.70); highest vs lowest HR 0.58 (0.45–0.75).
  - J Korean Med Sci 2009;24(1):13–19. DOI 10.3346/jkms.2009.24.1.13. PMID 19270807.
- **Hong Kong Chinese, aged 69–94, Lu 2018 (ABS).** n = 1,242, with VO2max measured on a cycle ergometer. The abstract gives no per-unit HR. J Gerontol A 2018;73(8):1132–1137. DOI 10.1093/gerona/glx180. PMID 29029009.
- **NOT VERIFIED:** I found no East Asian per-MET all-cause mortality HR based on measured CRF.

---

## B2. VO2max reference values by age decade and sex

### B2a. Chinese adults, community-based cycle-ergometer CPET: Wang Y 2022 (FT, first choice)

- **Population and design:** cross-sectional study, 2017–2018, in four communities (urban and rural) in Beijing and Hezhou, Guangxi. 1,114 healthy adults were included out of 1,642 screened. Graded exercise test on a cycle ergometer (Ergosana 320F) with expired-gas analysis (printed as "expired gas (cosmed, software: Onimia)"). The study reports VO2peak.
- **Source:** Wang Y, Li H, Wang J, Zhao W, Zeng Z, Hao L, Yuan Y, Lin Y, Wu Y, Wang Z. *J Clin Med* 2022;11(16):4904. DOI 10.3390/jcm11164904. PMID 36013143. PMCID PMC9409785.
- **URL retrieved:** https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9409785/fullTextXML (Table 4).

**Table 4, VO2peak (mL·kg⁻¹·min⁻¹), copied exactly:**

| Sex | Age (y) | n | Mean | SD | P5 | P10 | P25 | **P50** | P75 | P90 | P95 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Men | 20–29 | 88 | 35.8 | 9.7 | 19.1 | 24.1 | 28.1 | **35.7** | 44.9 | 48.9 | 50.7 |
| Men | 30–39 | 88 | 28.8 | 6.6 | 19.0 | 20.8 | 24.3 | **27.7** | 33.2 | 37.9 | 41.6 |
| Men | 40–49 | 76 | 27.4 | 5.5 | 18.9 | 21.0 | 23.4 | **26.7** | 31.5 | 34.6 | 36.7 |
| Men | 50–59 | 102 | 24.4 | 5.1 | 17.2 | 17.6 | 20.6 | **24.4** | 27.1 | 31.0 | 33.5 |
| Men | 60–69 | 89 | 22.9 | 5.1 | 14.9 | 15.8 | 19.3 | **22.4** | 26.0 | 29.4 | 31.9 |
| Men | 70–79 | 47 | 20.5 | 5.5 | 13.5 | 14.2 | 15.8 | **19.7** | 22.9 | 29.1 | 31.1 |
| Women | 20–29 | 92 | 29.2 | 7.0 | 20.9 | 21.8 | 25.3 | **27.7** | 32.8 | 37.5 | 41.7 |
| Women | 30–39 | 105 | 25.6 | 4.8 | 18.4 | 19.6 | 22.1 | **26.0** | 28.8 | 31.8 | 34.2 |
| Women | 40–49 | 114 | 24.9 | 5.0 | 16.7 | 20.1 | 22.1 | **24.7** | 27.5 | 30.7 | 32.7 |
| Women | 50–59 | 122 | 22.6 | 4.7 | 16.5 | 17.8 | 20.0 | **22.0** | 25.2 | 28.5 | 31.0 |
| Women | 60–69 | 114 | 21.1 | 4.9 | 12.3 | 13.8 | 17.7 | **21.2** | 24.4 | 28.0 | 29.2 |
| Women | 70–79 | 64 | 17.0 | 4.1 | 9.5 | 11.6 | 14.4 | **17.0** | 20.0 | 21.9 | 22.8 |

The table also gives P2 and P98:

| Sex | Age (y) | P2 | P98 |
|---|---|---|---|
| Men | 20–29 | 17.9 | 51.9 |
| Men | 30–39 | 14.3 | 43.9 |
| Men | 40–49 | 18.6 | 40.1 |
| Men | 50–59 | 15.9 | 35.5 |
| Men | 60–69 | 13.9 | 34.7 |
| Men | 70–79 | 11.5 | 34.5 |
| Women | 20–29 | 16.0 | 49.8 |
| Women | 30–39 | 15.7 | 34.6 |
| Women | 40–49 | 12.5 | 36.8 |
| Women | 50–59 | 14.0 | 33.8 |
| Women | 60–69 | 11.1 | 30.8 |
| Women | 70–79 | 8.2 | 23.1 |

Subtotals: men n 490, mean 27.0 (SD 8.1); women n 611, mean 23.7 (SD 6.2).

- **Quote (abstract):** "The mean V·O2peak decreased with age in both sexes, from 35.8 mL·min−1·kg−1 in age 20–29 years to 20.5 mL·min−1·kg−1 in 70–79 years in men and from 29.2 mL·min−1·kg−1 to 17.0 mL·min−1·kg−1 in women."
- **Caveats (FT):**
  1. **Effort was largely submaximal.** Mean peak RER was 1.00 in men and 1.04 in women, and only 236 of 1,114 participants (21.2%) reached RER ≥1.1 (Tables 2–3). Termination criteria were strict (85% of predicted HRmax, RPE). These are VO2peak values, not VO2max.
  2. **Cycle ergometer.** The authors write: "V·O2peak is typically 5–20% lower during a maximal exercise test performed on a cycle ergometer compared to a treadmill, and a 10% difference is typically used by clinicians when comparing peak exercise responses between cycle ergometry and treadmill exercise." Smartwatch VO2max is calibrated on running, so it is not directly comparable with these values.
  3. **Small strata.** Each age-sex cell has 47–122 participants.
  4. **Gap with FRIEND.** The authors state that the difference from FRIEND was largest at age 20–29 (14 mL·kg⁻¹·min⁻¹ in men, 10 in women) and smallest at 70–79 (4 in men, 1 in women).

### B2b. Chinese adults under 60, treadmill CPET: Huang 2024 (ABS)

- **Value (mean VO2peak, mL·kg⁻¹·min⁻¹):** men 20–29, 30–39, 40–49 and 50–59: **42.6, 41.2, 38.7, 35.9**. Women in the same groups: **37.1, 34.7, 32.0, 30.3**. n = 4,199 healthy participants.
- **Source:** Huang J, Yin L, Li X, et al. *J Cardiopulm Rehabil Prev* 2024;44(3):212–218. DOI 10.1097/HCR.0000000000000856. PMID 38488145.
- **Quote:** "The mean V˙O2peak values of four age groups (20-29, 30-39, 40-49, and 50-59 yr) were 42.6, 41.2, 38.7, and 35.9 mL/kg/min, respectively, for men, and 37.1, 34.7, 32.0, and 30.3 mL/kg/min, respectively, for women."
- **NOT VERIFIED:** SDs, percentiles and recruitment setting. The full text is not open access; the abstract describes "Healthy participants (n = 4199) who completed a CPX using a treadmill".

### B2c. Other Chinese CPET reference sets (context)

- **Wang J 2025, Peking University Third Hospital (FT).** Hospital-based "healthy" adults on a cycle ergometer, derivation cohort n = 4,531. VO2peak was **24.0 ± 6.4** in men (mean age 48.4) and **19.3 ± 4.7** in women (mean age 53.0).
  - *Sci Rep* 2025;15:10876. DOI 10.1038/s41598-025-94207-7. PMID 40157952.
- **Dun 2021, Xiangya Hospital (ABS).** Cycle ergometer, n = 964. The paper gives regression equations only.
  - *Int J Cardiol* 2021;332:15–21. DOI 10.1016/j.ijcard.2021.03.013. PMID 33716041.
- **Cui 2026, JACC Asia (FT).** CVD patients only. It uses Wang Y 2022 as the healthy Chinese reference: "Reference values for healthy Chinese adults were obtained from Wang et al, the only multicenter study providing age- and sex-specific VO2peak reference standards based on cycle ergometer CPET".
  - DOI 10.1016/j.jacasi.2026.05.008. PMID 42360249.

### B2d. FRIEND, United States, treadmill (FT for 2015; ABS only for 2022)

**FRIEND 2015** (Kaminsky LA, Arena R, Myers J. *Mayo Clin Proc* 2015;90(11):1515–1523. DOI 10.1016/j.mayocp.2015.07.026. PMID 26455884. PMCID PMC4919021).

- Retrieved from PMC XML via E-utilities (`db=pmc&id=4919021`). Population: 7,783 maximal treadmill tests, RER ≥1.0, adults aged 20–79 without CVD.

**Table 3, measured VO2max percentiles (mL·kg⁻¹·min⁻¹), copied exactly:**

| Sex | Age (y) | P5 | P10 | P25 | **P50** | P75 | P90 | P95 |
|---|---|---|---|---|---|---|---|---|
| Men | 20–29 | 29.0 | 32.1 | 40.1 | **48.0** | 55.2 | 61.8 | 66.3 |
| Men | 30–39 | 27.2 | 30.2 | 35.9 | **42.4** | 49.2 | 56.5 | 59.8 |
| Men | 40–49 | 24.2 | 26.8 | 31.9 | **37.8** | 45.0 | 52.1 | 55.6 |
| Men | 50–59 | 20.9 | 22.8 | 27.1 | **32.6** | 39.7 | 45.6 | 50.7 |
| Men | 60–69 | 17.4 | 19.8 | 23.7 | **28.2** | 34.5 | 40.3 | 43.0 |
| Men | 70–79 | 16.3 | 17.1 | 20.4 | **24.4** | 30.4 | 36.6 | 39.7 |
| Women | 20–29 | 21.7 | 23.9 | 30.5 | **37.6** | 44.7 | 51.3 | 56.0 |
| Women | 30–39 | 19.0 | 20.9 | 25.3 | **30.2** | 36.1 | 41.4 | 45.8 |
| Women | 40–49 | 17.0 | 18.8 | 22.1 | **26.7** | 32.4 | 38.4 | 41.7 |
| Women | 50–59 | 16.0 | 17.3 | 19.9 | **23.4** | 27.6 | 32.0 | 35.9 |
| Women | 60–69 | 13.4 | 14.6 | 17.2 | **20.0** | 23.8 | 27.0 | 29.4 |
| Women | 70–79 | 13.1 | 13.6 | 15.6 | **18.3** | 20.8 | 23.1 | 24.1 |

**Tables 2 and 4, mean ± SD (n):**

| Age (y) | Men | Women |
|---|---|---|
| 20–29 | 47.6 ± 11.3 (513) | 37.6 ± 10.2 (410) |
| 30–39 | 43.0 ± 9.9 (963) | 30.9 ± 8.0 (608) |
| 40–49 | 38.8 ± 9.6 (1,327) | 27.9 ± 7.7 (843) |
| 50–59 | 33.8 ± 9.1 (1,078) | 24.2 ± 6.1 (805) |
| 60–69 | 29.4 ± 7.9 (593) | 20.7 ± 5.0 (408) |
| 70–79 | 25.8 ± 7.1 (137) | 18.3 ± 3.6 (98) |

- **Quote (2015 abstract):** "In FRIEND, the 50th percentile VO2max of men and women aged 20 to 29 years decreased from 48.0 and 37.6 mLO2 · kg(-1) · min(-1) to 24.4 and 18.3 mLO2 · kg(-1) · min(-1) for ages 70 to 79 years, respectively."

**FRIEND 2022** (Kaminsky LA, Arena R, Myers J, et al. *Mayo Clin Proc* 2022;97(2):285–293. DOI 10.1016/j.mayocp.2021.08.020. PMID 34809986).

- **ABS only.** 22,379 tests (16,278 treadmill and 6,101 cycle) from 34 US laboratories, 1968–2021, adults aged 20–89.
- **Quotes (abstract):**
  - "The average rate of decline per decade over a 6-decade period was 13.5%, 4.0 mLO2·kg-1·min-1 for treadmill CPX and 16.4%, 4.3 mLO2·kg-1·min-1 for cycle CPX."
  - "The updated reference standards for treadmill CPX were 1.5 - 4.6 mLO2·kg-1·min-1 lower compared with the previous 2015 standards whereas the updated cycling standards were generally comparable to the original 2017 standards."
- **NOT VERIFIED:** the 2022 per-decade percentile tables. The Mayo Clinic Proceedings and ScienceDirect pages returned 403, the paper has no PMC copy, and no open repository copy was found. **Lead:** obtain the PDF through institutional access, using DOI 10.1016/j.mayocp.2021.08.020, Tables 2–3.

---

## B3. Smartwatch VO2max accuracy against laboratory CPET

**Sign convention:** I report bias as **watch minus criterion** unless stated otherwise. A negative value means the watch underestimates.

| Device | Study (n) | Criterion | Mean bias (mL·kg⁻¹·min⁻¹) | SD of difference / 95% LoA | MAPE | Status |
|---|---|---|---|---|---|---|
| Apple Watch (Series 5–9) | Lambe 2025 *PLoS One* (n=30) | Treadmill, indirect calorimetry | **−6.07** (95% CI 3.77–8.38, reported as criterion minus watch = +6.07) | LoA −6.11 to 18.26 (criterion − watch); SD ≈ 6.2 (DERIVED) | **13.31%** (10.01–16.61); MAE 6.92 | ABS |
| Apple Watch Series 10 | Lambe 2026 *Mayo Clin Proc Digit Health* (n=40; 71% at or above the FRIEND 80th percentile) | Treadmill | **−6.25** (−8.28 to −4.23) | SD 6.11; LoA −18.23 to 5.73 | **13.2%** (9.6–16.8); MAE 6.79 | FT |
| Apple Watch Series 7 | Caserman 2024 *JMIR Biomed Eng* (n=19) | Cycle ergometer | **−4.51** (DERIVED: 41.37 − 45.88) | RMSE 8.85; ICC 0.47 | **15.79%** | ABS |
| Exercise-based algorithms (Garmin/Firstbeat, Fitbit) | Molina-Garcia 2022 *Sports Med* meta-analysis | Lab CPET | **−0.09** (−1.66 to 1.48) | LoA −9.92 to 9.74 (±9.83); SD ≈ 5.0 (DERIVED) | not pooled | FT |
| Resting-based algorithms (Polar) | Same meta-analysis | Lab CPET | **+2.17** (0.28–4.07) | LoA −13.07 to 17.41 | not pooled | FT |
| Garmin fēnix 6 | Carrier 2025 *Sensors* (n=19 in abstract, 20 in table) | Treadmill, 30-s averaging | +0.75 (95% CI of bias −1.28 to 2.78; sign convention not stated) | CCC 0.73 | **7.05%** | FT |
| Garmin Forerunner 245 | Engel 2026 *Eur J Appl Physiol* (n=35 trained athletes) | Treadmill | **−4.73** / −4.05 (two runs) | ICC 0.71 / 0.75 | 7.9% / 7.2% | ABS |
| **Huawei Watch GT Runner** (Firstbeat-licensed) | Ye 2023 *JMIR mHealth* (n=46 Chinese adults, low altitude) | **Cycle** ergometer | **+1.11** (SD 1.73) | LoA ≈ −2.28 to 4.50 (DERIVED) | **6%**; MAE 1.76 | FT |

**Sources** (all records verified by EXT_ID):

- Lambe R, O'Grady B, Baldwin M, Doherty C. *PLoS One* 2025;20(5):e0323741. DOI 10.1371/journal.pone.0323741. PMID 40373042.
- Lambe R, Schumann M, Donnelly L, et al. *Mayo Clin Proc Digit Health* 2026;4(2):100357. DOI 10.1016/j.mcpdig.2026.100357. PMID 42094313. Full text: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13141568/fullTextXML
- Caserman P, Yum S, Göbel S, Reif A, Matura S. *JMIR Biomed Eng* 2024;9:e59459. DOI 10.2196/59459. PMID 39083800.
- Molina-Garcia P, Notbohm HL, Schumann M, et al. *Sports Med* 2022;52(7):1577–1597. DOI 10.1007/s40279-021-01639-y. PMID 35072942. Full text from Europe PMC XML (PMC9213394).
  - A 2026 correction (DOI 10.1007/s40279-026-02547-9, PMID 42867627) changes only duplicated reference-list entries. Read at link.springer.com.
- Carrier B, Marten Chaves S, Navalta JW. *Sensors* 2025;25(1):275. DOI 10.3390/s25010275. PMID 39797066. Full text from Europe PMC XML (Table 1).
- Engel FA, Masur L, Sperlich B, Düking P. *Eur J Appl Physiol* 2026;126(1):591–603. DOI 10.1007/s00421-025-05923-x. PMID 40770433.
- Ye X, Sun M, Yu S, et al. *JMIR mHealth uHealth* 2023;11:e43340. DOI 10.2196/43340. PMID 37410528. Full text from Europe PMC XML (PMC10360014), Table 2.

**Quotes:**

- Lambe 2025: "Overall, Apple Watch underestimated VO2 max, with a mean difference of 6.07 mL/kg/min (95% CI 3.77-8.38). Limits of agreement indicated variability between measurement methods (lower -6.11 mL/kg/min; upper 18.26 mL/kg/min). MAPE was calculated as 13.31% (95% CI 10.01-16.61)"
- Lambe 2026: "Apple Watch underestimated VO2 max overall, with wide limits of agreement indicating measurement variability (mean difference, -6.25 mL/kg per minute [95% CI, -8.28 to -4.23]; limits of agreement, -18.23 to 5.73)."
- Molina-Garcia: "wearables using resting condition information in their algorithms significantly overestimated VO2max (bias 2.17 ml·kg-1·min-1; limits of agreement - 13.07 to 17.41 ml·kg-1·min-1), while devices using exercise-based information in their algorithms showed a lower systematic and random error (bias - 0.09 ml·kg-1·min-1; limits of agreement - 9.92 to 9.74 ml·kg-1·min-1)."
- Ye 2023 (FT): "the Bland–Altman plots demonstrated a small bias of the VO2max-SWT values compared to the VO2max-CPET at low (bias=1.11 mL·kg–1·min–1...) and high (bias=1.00 mL·kg–1·min–1...) altitudes"
- Ye 2023 methods: "The signal processing by Huawei Watch GT Runner is licensed by the Firstbeat Technology's Fitness Test".

**Caveats:**

1. **Fitness-dependent bias.** Apple Watch and Garmin tend to underestimate VO2max in fit people and overestimate it in unfit people. The Lambe 2026 sample was very fit. Caserman writes: "the Apple Watch also overestimates or underestimates the VO2max in individuals with poor or excellent fitness levels, respectively."
2. **Criterion modality.** Ye 2023 used a cycle-ergometer criterion. Cycle VO2peak is lower, which likely contributes to the watch's apparent positive bias.
3. **Conflict of interest.** Huawei Technologies (Finland) is a member of the INTERLIVE consortium that wrote the meta-analysis. The paper says: "one technology company, Huawei Technologies (Finland)".
4. **Apple Watch living review.** The 2026 *npj Digit Med* living systematic review (PMID 41513748) found only one Apple Watch VO2max study (Lambe 2025).
5. **No other Huawei study.** No other peer-reviewed Huawei VO2max validation was found in Europe PMC or a web search.

---

## B4. Grip strength and all-cause mortality

### B4a. Leong 2015 (Lancet, PURE) (ABS)

- **Value:** HR **1.16 (1.13–1.20)** per **5-kg lower** grip strength, all-cause mortality. Cardiovascular mortality 1.17 (1.11–1.24); non-cardiovascular mortality 1.17 (1.12–1.21).
- **Population and design:** 139,691 participants aged 35–70 in 17 countries. Jamar dynamometer. Median follow-up 4.0 years; 3,379 deaths.
- **Adjustment:** the abstract says "After adjustment, the association... was similar across country-income strata". The covariate list was **NOT VERIFIED**, because The Lancet returned 403.
- **China's inclusion: indirectly verified.** The PubMed author-affiliation list (E-utilities efetch, PMID 25982160) includes co-authors from 17 countries, among them Gu H and Li W of Fuwai Hospital, National Center for Cardiovascular Diseases, Beijing, the PURE-China site. A country-by-country participant list was not retrieved.
- **Source:** Leong DP, Teo KK, Rangarajan S, et al. *Lancet* 2015;386(9990):266–273. DOI 10.1016/S0140-6736(14)62000-6. PMID 25982160.
- **Quote:** "Grip strength was inversely associated with all-cause mortality (hazard ratio per 5 kg reduction in grip strength 1.16, 95% CI 1.13-1.20; p<0.0001)... Grip strength was a stronger predictor of all-cause and cardiovascular mortality than systolic blood pressure."
- **Caveat:** short follow-up (4 years), so reverse causation from subclinical illness is possible.

### B4b. Wu 2017 (JAMDA) meta-analysis (ABS): corroboration

- **Value:** HR **1.16 (1.12–1.20)** per 5-kg decrease, all-cause mortality.
- **Design:** 42 studies, 3,002,203 participants, community-dwelling. Most-adjusted HRs pooled. Linear relationship within grip strength of 56 kg.
- **Source:** Wu Y, Wang W, Liu T, Zhang D. *J Am Med Dir Assoc* 2017;18(6):551.e17–551.e35. DOI 10.1016/j.jamda.2017.03.011. PMID 28549705.

### B4c. Chinese cohorts

- **CHARLS, PLoS One 2022 (FT, Table 2).** n = 17,167, aged 45–96, 2011–2018, 1,453 deaths ("During the follow-up, 1,453 death events had occurred"). Handgrip strength in 5-kg bands, with the band median in brackets; reference band <20 kg (median 16.5):

| Band (median) | Model 1: age, sex | Model 3: + education, marriage, household registration, BMI, smoking, drinking | Model 4: all 20 covariates |
|---|---|---|---|
| 20–25 kg (23) | 0.62 (0.52–0.73) | 0.63 (0.53–0.74) | 0.70 (0.59–0.83) |
| 25–30 kg (28) | 0.57 (0.48–0.67) | 0.59 (0.50–0.70) | 0.68 (0.57–0.81) |
| 30–35 kg (33) | 0.46 (0.38–0.55) | 0.48 (0.40–0.58) | 0.58 (0.48–0.71) |
| >35 kg (42) | 0.39 (0.32–0.47) | 0.42 (0.35–0.51) | 0.52 (0.43–0.64) |

  - **DERIVED:** an ordinary least-squares log-linear slope on the Model 3 band medians gives HR ≈ **1.18 per 5 kg lower**; Model 1 gives ≈ 1.19. This is my approximation, not a published estimate. Sexes were pooled.
  - Source: Xie K, Lu Z, Han X, et al. *PLoS One* 2022;17(10):e0274832. DOI 10.1371/journal.pone.0274832. PMID 36227843. Full text: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9560503/fullTextXML
- **CHARLS, J Sci Med Sport 2022 (ABS).** n = 11,618, follow-up about 8 years, 1,290 deaths. Logistic ORs for highest vs lowest tertile: men 0.47 (0.35–0.64), women 0.51 (0.24–1.08). DOI 10.1016/j.jsams.2022.08.005. PMID 36064503.
- **CHARLS, Front Med 2023 (ABS).** n = 6,762. Low grip strength, defined as <32 kg in men and <19 kg in women, HR 1.77 (1.49–2.11). DOI 10.3389/fmed.2023.1304181. PMID 38105886.
- **NOT VERIFIED:** I found no Chinese cohort, CKB or CLHLS included, that publishes an HR per 5 kg or per SD. Note also that CHARLS used a different dynamometer from PURE's Jamar.

---

## B5. Resting heart rate (RHR) and all-cause mortality

### B5a. Zhang 2016 (CMAJ) (ABS + WF)

- **Value:** RR **1.09 (1.07–1.12)** per 10 bpm higher RHR, all-cause mortality. Cardiovascular mortality 1.08 (1.06–1.10). RHR >80 vs the lowest category: 1.45 (1.34–1.57).
- **Asia subgroup [WF, Table 2]:** **1.13 (1.07–1.19)** from 6 estimates, I² 62.5%. The region difference had p = 0.04. Europe 1.09 (1.06–1.11); United States 1.05 (1.03–1.08).
- **Chinese cohorts included [WF, Table 1]:**
  - Mai et al. 2009 (China, n = 9,856, ECG);
  - Wang et al. 2014, the Kailuan study (n = 92,562, ECG).
- **Design:** 46 studies, 1,246,203 participants, 78,349 deaths.
- **Adjustment:** the relative risks "that reflected the greatest degree of control for potential confounders" [WF].
- **Source:** Zhang D, Shen X, Qi X. *CMAJ* 2016;188(3):E53–E63. DOI 10.1503/cmaj.150535. PMID 26598376. PMCID PMC4754196.
- **URL retrieved:** Europe PMC record, plus https://pmc.ncbi.nlm.nih.gov/articles/PMC4754196/ via WebFetch.
- **Quote:** "The relative risk with 10 beats/min increment of resting heart rate was 1.09 (95% CI 1.07-1.12) for all-cause mortality and 1.08 (95% CI 1.06-1.10) for cardiovascular mortality."
- **Caveat:** the authors report substantial heterogeneity and publication bias.

### B5b. Aune 2017 (NMCD) (ABS)

- **Value:** RR **1.17 (1.14–1.19)** per 10 bpm, all-cause mortality, from 48 studies with I² = 94.0%.
- **Source:** Aune D, Sen A, ó'Hartaigh B, et al. *Nutr Metab Cardiovasc Dis* 2017;27(6):504–517. DOI 10.1016/j.numecd.2017.04.004. PMID 28552551.
- **Quote:** "...and 1.17 (95% CI: 1.14-1.19, I2 = 94.0%, n = 48) for all-cause mortality."

### B5c. Chinese cohorts

- **Kailuan, Wang A 2014 (FT, Table 2).**
  - Per 10 bpm all-cause death HR **1.18 (1.13–1.23)** in Model 3. Model 3 adjusts for age, sex, income, education, marital status, BMI, waist circumference, smoking, drinking, physical activity, hs-CRP, hypertension, diabetes and dyslipidaemia.
  - Q5 (≥81 bpm) vs Q1 (≤66 bpm): HR 1.51 (1.29–1.77).
  - **Abstract error:** the abstract labels 1.18 (1.13–1.23) as "highest quintile... compared with the lowest quintile". Table 2 shows that figure is the **per-10-bpm** estimate. Cite the table.
  - **Population and measurement:** 92,562 participants aged 18–98 (73,938 men), mean follow-up 4 years, 1,589 deaths. RHR was measured from a 10-s 12-lead ECG after 5 minutes **supine**.
  - Source: Wang A, Chen S, Wang C, et al. *PLoS One* 2014;9(10):e110985. DOI 10.1371/journal.pone.0110985. PMID 25343354. Full text: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4208799/fullTextXML
- **Shanghai older adults, Li FK 2019 (ABS).** n = 4,051, age ≥60.
  - Supine HR per 1-SD increase: total mortality HR 1.19 (1.11–1.29).
  - Supine HR was **72.2 ± 13.9 bpm vs 76.3 ± 11.9 bpm sitting**. Sitting HR did not predict mortality.
  - Li FK, Sheng CS, Zhang DY, et al. *J Hypertens* 2019;37(10):2024–2031. DOI 10.1097/HJH.0000000000002134. PMID 31107358.

### B5d. Wearable RHR vs clinic seated RHR

- **NOT VERIFIED:** I found no study that directly compares a consumer wearable's daily RHR with a clinic seated RHR and reports a mean difference. The anchors below come from retrieved sources.
  - **Same moment, sensor accuracy only.**
    - Project Baseline Health Study (n = 875): Verily Study Watch vs 12-lead ECG, bias **+0.76 bpm (0.52–1.00)**, ICC 0.946. *J Med Internet Res* 2024;26:e60493. DOI 10.2196/60493. PMID 39705694. Full text via Europe PMC XML.
    - Apple Watch living systematic review: RHR bias **+0.21 bpm (−0.65 to 1.07)**, LoA −8.14 to 8.56. *npj Digit Med* 2026;9:63. DOI 10.1038/s41746-025-02238-1. PMID 41513748. Full text read.
  - **Definition effect.**
    - A wrist PPG device in 433 healthy adults gave RHR **54.5 (SD 8.0) bpm by day vs 50.5 (SD 7.6) at night**. Speed C, Arneil T, Harle R, et al. 2023, *PLOS Digit Health* 2(4):e0000236. DOI 10.1371/journal.pdig.0000236. PMID 37115739. Google-funded.
    - In a Fitbit-authored preprint (DOI 10.1101/19008771; not peer-reviewed), Fitbit's daily RHR was closest to a lying measurement before waking (mean error 0.0 bpm), with the highest values in the middle of the day.
  - **Posture effect in clinic.** Supine is about 4 bpm lower than sitting (Li 2019 above).
  - **Implication (my inference):** a wearable daily or sleeping RHR is likely several bpm (about 4 or more) below a seated clinic RHR. This direction would understate risk if cohort HRs are applied without calibration. The cohort HRs themselves mix supine, seated and ECG-derived measurements.

---

## B6. Sleep duration and all-cause mortality

### B6a. Yin 2017 (JAHA) dose-response meta-analysis (FT)

- **Value:**
  - Nadir **≈7 h/day**.
  - Below 7 h: RR **1.06 (1.04–1.07) per 1-h reduction**.
  - Above 7 h: RR **1.13 (1.11–1.15) per 1-h increment**.
- **Design:** prospective cohorts published before 1 December 2016. 67 articles: Europe 22, USA 16, **Asia 27**, Australia 2. They include Chinese cohorts such as Shanghai and Kailuan. Sleep duration was self-reported in all studies (48 by questionnaire, 19 by interview).
- **Adjustment:** "When studies had several adjustment models, we extracted those that reflected the maximum extent of adjustment."
- **Source:** Yin J, Jin X, Shan Z, et al. *J Am Heart Assoc* 2017;6(9):e005947. DOI 10.1161/JAHA.117.005947. PMID 28889101. PMCID PMC5634263. Full text via Europe PMC XML.
- **Quote:** "For all-cause mortality, when sleep duration was <7 hours per day, the pooled relative risk (RR) was 1.06 (95% CI, 1.04-1.07) per 1-hour reduction; when sleep duration was >7 hours per day, the pooled RR was 1.13 (95% CI, 1.11-1.15) per 1-hour increment."

### B6b. Cappuccio 2010 (Sleep) (ABS + WF)

- **Value:** short sleep RR **1.12 (1.06–1.18)**; long sleep RR **1.30 (1.22–1.38)**.
- **Design:** 16 studies, 27 cohort samples, 1,382,999 participants, 112,566 deaths. Sleep duration by questionnaire.
- **Definitions [WF fragments]:**
  - Reference: "being 7 h per night in the majority of studies".
  - Short: "Short sleep was ≤ 5 h per night", also "commonly < 7 h per night, often < 5 h per night".
  - Long: "Long sleep was defined as > 8 h per night".
- **Region [WF]:** the long-sleep association "appeared stronger in studies carried out in East Asian countries (Japan and Taiwan)".
- **Source:** Cappuccio FP, D'Elia L, Strazzullo P, Miller MA. *Sleep* 2010;33(5):585–592. DOI 10.1093/sleep/33.5.585. PMID 20469800. PMCID PMC2864873.
- **Quote (abstract):** "short duration of sleep was associated with a greater risk of death (RR: 1.12; 95% CI 1.06 to 1.18; P < 0.01)... Long duration of sleep was also associated with a greater risk of death (1.30; [1.22 to 1.38]; P < 0.0001)"

### B6c. East Asian pooled cohort: Svensson 2021, Asia Cohort Consortium (FT)

- **Value:**
  - Nadir at **7 h** for both sexes.
  - ≥10 h vs 7 h, multivariable HR: **men 1.34 (1.26–1.44)**, **women 1.48 (1.36–1.61)**.
  - Other categories (≤5, 6, 8, 9 h) are in Figure 1 and eTables 2–3, not in the text. Their values were NOT VERIFIED.
- **Population:** 322,721 participants from 9 Asia Cohort Consortium cohorts in Japan, China, Singapore and Korea. The cohorts include the Shanghai Men's and Women's Health Studies and the Singapore Chinese Health Study. Self-reported sleep.
- **Adjustment:** age, marital status, BMI, smoking, alcohol, physical activity, history of diabetes and hypertension, and menopausal status in women.
- **Source:** Svensson T, Saito E, Svensson AK, et al. *JAMA Netw Open* 2021;4(9):e2122837. DOI 10.1001/jamanetworkopen.2021.22837. PMID 34477853. PMCID PMC8417759.
- **Quote:** "Multivariable adjustment only slightly attenuated these associations (men: HR, 1.34, 95% CI, 1.26-1.44; women: HR, 1.48, 95% CI, 1.36-1.61)."

### B6d. China Kadoorie Biobank: Chen 2026 (ABS)

- **Value:** sleep <7 or >9 h/day vs 7–9 h: all-cause mortality HR **1.07 (1.04–1.09)**.
- **Population:** 461,046 adults, about 10 years of follow-up, 33,259 deaths. The abstract does not give finer categories.
- **Source:** Chen Y, Zou Y, Su Y, et al. *Sleep Med* 2026;146:109073. DOI 10.1016/j.sleep.2026.109073. PMID 42269188.

### B6e. Consumer wearable total sleep time (TST) vs polysomnography

- **Chinoy 2021, Table 1 (FT).** Healthy young adults (28.1 ± 3.9 years), 3 laboratory nights including one disrupted night, time in bed fixed at 8 h. Bias is device minus PSG, in minutes; limits of agreement are ±2 SD.

| Device | Bias (min) | LoA |
|---|---|---|
| Actiwatch (research actigraph) | +23.9 | −40.5 to 88.3 |
| Fitbit Alta HR | +2.6 | −42.0 to 47.1 |
| Garmin Fenix 5S | +43.7 | −47.0 to 134.4 |
| Garmin Vivosmart 3 | +46.8 | −39.5 to 133.1 |
| Fatigue Science Readiband | +13.3 | −93.2 to 119.8 |

  - Source: *Sleep* 2021;44(5):zsaa291. DOI 10.1093/sleep/zsaa291. PMID 33378539. PMCID PMC8120339.
- **Schyvens 2025, Table 3 (FT).** 62 adults (52 men), mean age 46, single PSG night. The sample included people with suspected sleep apnoea.
  - **Apple Watch Series 8 (n=20): TST bias +19.60 min** (p = 0.004); MAE 27.75 min; MAPE 6.50%; LoA −38.35 to 77.55. Cohen's κ for staging 0.53.
  - Fitbit Sense +6.31; Fitbit Charge 5 +11.12 in the table but −5.74 in the text (an internal inconsistency in the paper); Whoop 4.0 +24.46; Withings Scanwatch +39.87; Garmin Vivosmart 4 +38.44.
  - Source: *Sleep Adv* 2025;6(2):zpaf021. DOI 10.1093/sleepadvances/zpaf021. PMID 40303381. PMCID PMC12038347.
- **Korean multicentre study, Lee 2023 (FT).** 75 participants, 11 consumer trackers. TST minutes were not tabulated in the text. Sleep-efficiency bias ranged from −3.49 to +12.80 percentage points. Apple Watch 8 staging agreement was only "fair" (κ 0.2–0.4).
  - *JMIR mHealth uHealth* 2023;11:e50983. DOI 10.2196/50983. PMID 37917155.
- **Quote, Schyvens:** "on average, the wearables overestimated TST by 6.31–39.87 minutes compared to PSG."

### B6f. Self-reported vs actigraphy-measured sleep: Lauderdale 2008 (ABS)

- **Value:** self-report was **6.8 h** vs **6.0 h** measured, a mean over-report of **0.8 h**.
  - Correlation r = 0.47.
  - Subjective reports rose by 34 minutes per additional hour of measured sleep.
  - People who slept 5 h over-reported by 1.2 h; those who slept 7 h over-reported by 0.4 h.
- **Population:** CARDIA Chicago site, n = 669, middle-aged. Wrist actigraphy over 3 days in 2 waves.
- **Source:** Lauderdale DS, Knutson KL, Yan LL, Liu K, Rathouz PJ. *Epidemiology* 2008;19(6):838–845. DOI 10.1097/EDE.0b013e318187a7b0. PMID 18854708. PMCID PMC2785092.
- **Quote:** "Average measured sleep was 6 hours, whereas the average from subjective reports was 6.8 hours... persons sleeping 5 hours over-reported their sleep duration by 1.2 hours, and those sleeping 7 hours over-reported by 0.4 hours."
- **Modelling note (my inference):**
  - The mortality curves in B6a–d come from *self-reported* sleep.
  - A wearable TST is likely to sit nearer actigraphy or PSG and *below* the matching self-report, by up to about 1 h in short sleepers.
  - Applying self-report-based HRs to wearable TST without calibration would therefore over-penalise short sleep. Actigraphy itself overestimates PSG sleep by about 24 min (Chinoy).

---

## B7. Daily steps and all-cause mortality

### B7a. Paluch 2022 (Lancet Public Health) (ABS + FT via PMC XML)

- **Value (adjusted HR vs quartile 1, median 3,553 steps/day):**
  - Q2 (5,801): **0.60 (0.51–0.71)**
  - Q3 (7,842): **0.55 (0.49–0.62)**
  - Q4 (10,901): **0.47 (0.39–0.57)**
- **Plateau:** at age **≥60, 6,000–8,000 steps/day**; at age **<60, 8,000–10,000 steps/day**. The age interaction in the spline model had p = 0.012 [WF].
- **Design:** individual-participant meta-analysis of 15 cohorts with 47,471 adults and 3,013 deaths, median follow-up 7.1 years. Cohorts: 4 in Europe, **1 in Japan**, 1 in Australia, 8 in the USA, and 1 covering 40 countries. None was from mainland China.
- **Adjustment (FT):** "Model 2 also adjusted for age, sex, race and ethnicity, education or income, body-mass index, and study-specific covariates for chronic disease (eg, diabetes, blood pressure, history of cardiovascular disease or cancer, and medications), self-rated health or functional status, acc[elerometer wear time, and lifestyle factors]".
- **Source:** Paluch AE, Bajpai S, Bassett DR, et al. *Lancet Public Health* 2022;7(3):e219–e228. DOI 10.1016/S2468-2667(21)00302-9. PMID 35247352. PMCID PMC9289978. Full text: E-utilities `db=pmc&id=9289978`.
- **Quote:** "Restricted cubic splines showed progressively decreasing risk of mortality among adults aged 60 years and older with increasing number of steps per day until 6000-8000 steps per day and among adults younger than 60 years until 8000-10 000 steps per day."

### B7b. Banach 2023 (Eur J Prev Cardiol) (ABS + WF)

- **Value:** HR **0.85 (0.81–0.91) per 1,000-step increment**, all-cause mortality, i.e. 15% lower risk. Cardiovascular mortality: HR 0.93 (0.91–0.95) per 500 steps.
- **Design:** 17 cohorts, 226,889 participants, median follow-up 7.1 years. Two cohorts were Japanese [WF]. The authors used models "adjusted for demographic and clinical indices" [WF].
- **Age [WF]:** "the RRs in older adults (≥60 years) were lower compared with younger participants (<60 years; P = 0.009)".
- **Corrigendum:** DOI 10.1093/eurjpc/zwad263 (PMID 37595090) corrects the all-cause cut-off from 3,967 to 3,867 steps/day. Read at https://academic.oup.com/eurjpc/article/30/18/2045/7245928.
- **Source:** Banach M, Lewek J, Surma S, et al. *Eur J Prev Cardiol* 2023;30(18):1975–1985. DOI 10.1093/eurjpc/zwad229. PMID 37555441. URL https://academic.oup.com/eurjpc/article/30/18/1975/7226309.
- **Quote:** "A 1000-step increment was associated with a 15% decreased risk of all-cause mortality [hazard ratio (HR) 0.85; 95% confidence interval (CI) 0.81-0.91; P < 0.001]"
- **Caveat:** the dose-response is non-linear, with the largest gains at low step counts. A constant per-1,000-step HR overstates benefit at high step counts.

### B7c. Chinese smartphone users' average daily steps: Althoff 2017 (Nature)

- **Value:**
  - **China: 6,189 steps/day** (mean 6,188.65; N = 17,427 users).
  - Hong Kong 6,880 (N = 4,754); Japan 6,010 (N = 20,386); Taiwan 5,000 (N = 4,821).
  - All users: 4,961 steps/day (SD 2,684).
- **Sources:**
  - The country values are **not printed in the paper's text**. They come from the authors' public data repository: https://raw.githubusercontent.com/timalthoff/activityinequality/master/data/countries_by_steps.csv ("2,China,6189") and `country_statistics_n46_20170511.csv` (N and steps_mean).
  - Althoff T, Sosič R, Hicks JL, King AC, Delp SL, Leskovec J. *Nature* 2017;547(7663):336–339. DOI 10.1038/nature23018. PMID 28693034. PMCID PMC5774986. Full text via E-utilities.
- **Quotes (paper):**
  - "The average user recorded 4961 steps per day (standard deviation σ = 2684) over an average span of 14 hours."
  - Limitation: "our sample is cross-sectional and potentially biased towards individuals of higher socioeconomic status, particularly in lower income countries, and people interested in their activity and health."
- **Caveats:**
  - Data are from iPhone users of the Argus app.
  - Steps are counted only while the phone is carried, so totals are lower than those of a wrist-worn device.
  - China was classed as a middle-income country.

---

## B8. Gait speed and survival: Studenski 2011 (JAMA) (FT via PMC XML)

- **Value:** pooled HR **0.88 (0.87–0.90) per 0.1 m/s faster** usual gait speed. This is pooled from **age-adjusted** study HRs.
  - Further adjustment for sex, BMI, smoking, systolic blood pressure, diseases, prior hospitalisation and self-reported health gave HR 0.90 (0.89–0.91).
- **Population:** pooled individual data from 9 cohorts (8 US and 1 Italian, InCHIANTI). 34,485 community-dwelling adults aged ≥65 (mean 73.5), followed 6–21 years, 17,528 deaths. Mean gait speed 0.92 (SD 0.27) m/s. Usual pace from a standing start; walks of 8 ft to 6 m were converted to a 4-m equivalent.
- **Source:** Studenski S, Perera S, Patel K, et al. *JAMA* 2011;305(1):50–58. DOI 10.1001/jama.2010.1923. PMID 21205966. PMCID PMC3080184. Full text: E-utilities `db=pmc&id=3080184`.
- **Quotes:**
  - "Age-adjusted HRs were pooled from all studies using standard meta-analytic statistical methodology."
  - "The overall HR for survival per each 0.1 m/s faster gait speed was 0.88 (95% CI, 0.87–0.90; P <.001)"
  - "Further adjustment for sex, BMI, smoking status, systolic blood pressure, diseases, prior hospitalization, and self-reported health did not change the results (overall HR, 0.90; 95% CI, 0.89–0.91; P <.001)."
  - "In our data, predicted life expectancy at the median for age and sex occurs at about 0.8 m/s".
- **Caveat:** the cohorts include no Asian participants and cover only people aged 65 and over. Extrapolating to younger adults is not supported.

---

## Not verified, with leads

1. **FRIEND 2022 per-decade percentile tables.** Publisher returned 403 and there is no PMC copy. Lead: institutional PDF, DOI 10.1016/j.mayocp.2021.08.020. FRIEND 2015 tables are given instead (FT).
2. **Leong 2015 covariate set and per-country participant counts.** Lead: Lancet full text and appendix. China's inclusion is supported only by co-author affiliations.
3. **Kodama 2009 adjustment details.** Lead: JAMA full text.
4. **A Chinese per-5-kg or per-SD grip HR.** None found. The CHARLS band HRs are tabulated above; the per-5-kg slope is DERIVED.
5. **An East Asian per-MET HR from measured CRF.** None found. Korean tertile HRs are given above.
6. **A direct comparison of wearable RHR with clinic seated RHR.** None found. Indirect anchors are given in B5d.
7. **Huang 2024 SDs and percentiles** for Chinese adults under 60 on treadmill. Lead: full text, *J Cardiopulm Rehabil Prev* 2024;44:212.
8. **Svensson 2021 category HRs** for ≤5, 6, 8 and 9 h. Lead: eTables 2–3 of the supplement.
