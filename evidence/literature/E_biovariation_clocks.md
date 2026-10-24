# Topic E — Biological variation, PhenoAge and epigenetic clocks

Verification of literature parameters for the LongPi clock layer (Levine PhenoAge from routine blood tests; optional commercial DNA-methylation clocks) and LongPi Pace (rate of change from repeated measurements).

- Retrieval date for every source: **2026-10-24**.
- PMIDs, DOIs and PMCIDs were copied from Europe PMC records retrieved during this session (journal metadata re-checked through the Europe PMC REST API). None come from memory.
- "Verbatim" means text copied from the retrieved full text, abstract or page. Values marked **(figure)** were read from a retrieved figure image and are legible but not machine-extracted text. Values marked **(derived)** are my own arithmetic on retrieved data and are not literature values.
- Status labels: VERIFIED = the number appears in the retrieved source. NOT VERIFIED = it could not be found, with the best lead given.

---

## E1. EFLM Biological Variation Database: CVI, 95% CI and analytical performance specifications

### Source and how it was retrieved

- **Database**: EFLM Biological Variation Database, https://biologicalvariation.eu/ (a JavaScript single-page app; plain WebFetch returns only the title).
- **Data retrieval**: the site's own public JSON API, which the analyte pages call. Endpoints were found in the site's JavaScript bundle (`/packs/js/50-…js`):
  - Global (meta-analysis) estimates: `https://biologicalvariation.eu/api/meta_calculations/meta_by_analyte/<analyte_id>`
  - Per-study datasets (BIVAC records): `https://biologicalvariation.eu/api/analyte_specifications/<analyte_id>` and `https://biologicalvariation.eu/api/bv_specifications/<dataset_id>`
  - Human-readable analyte page (the page that renders these data): `https://biologicalvariation.eu/api/search/by_id?query=<analyte_id>`
- **What the page displays**: the front-end code shows a "Meta Analysis" table with columns `Matrix | BV Estimate | Median CV | Lower CI | Higher CI | Comments | Updated`. It fills these from the JSON fields `median`, `lower` and `upper`, rounded to 1 decimal.
- **Recommended citation** (verbatim from the site's JavaScript bundle): "Aarsand AK, Webster C, Fernandez-Calle P, Jonker N, Diaz-Garzon J, Coskun A, Sufrate-Vergara B, Moreno-Parro I, Galior K, Topcu D, Gonzales-Lao E, Carobene A, Bartlett WA, Sandberg S. The EFLM Biological Variation Database. https://biologicalvariation.eu/ [time of access]."
- **Quality-appraisal standard**: Aarsand AK, et al. The Biological Variation Data Critical Appraisal Checklist (BIVAC). *Clin Chem* 2018;64(3):501–514. doi:10.1373/clinchem.2017.281808. PMID 29222339.
- **APS formula background** (the site cites "Clin Chem Lab Med 2024;62:1483–9"): Sandberg S, Coskun A, Carobene A, et al. Analytical performance specifications based on biological variation data – considerations, strengths and limitations. *Clin Chem Lab Med* 2024;62(8):1483–1489. doi:10.1515/cclm-2024-0108. PMID 38501489.

**Methodology, verbatim** from the "Background and Methodology" CMS page (https://cms.biologicalvariation.eu/background/, page id 10, modified 2025-10-20):

> "Only studies receiving an overall BIVAC grade A, B or C are considered fit to be considered for the meta-analysis. Meta-analysis is thereafter performed for studies with similar study characteristics, which include the relevant data for calculations of CI and where a minimum of 3 samples have been collected. For most measurands, and as a first step, meta-analysis is performed based on estimates from studies performed in healthy adults where sampling is bi-weekly, weekly or monthly. For the meta-analysis, the associated BIVAC grade and the width of the CI are used as weight, with the global estimate being delivered by a weighted median approach. For the meta-analysis the BIVAC grades are arbitrarily given weights A = 4, B =3 and C = 1. Percentile bootstrap with the weighted median performed on each of the resampled data sets were used for calculating the CI, which for < 10 estimates will be equal to the range."

**APS formulas, verbatim** from the site's JavaScript bundle (the APS panel text):

> "Imprecision … CVA < 0.5 × CVI … The factor 0.5 refers to desirable APS. The factor for optimum and minimum performance specifications are arbitrarily set to 0.25 and 0.75 respectively."
>
> "Bias < 0.25 × (CVI² + CVG²)¹/²"

The site's `calculateAPS` function first rounds CVI to 1 decimal, computes `desirableCV = 0.5·CVI`, then rounds the result to 1 decimal. The desirable-imprecision column below reproduces that function exactly; it was run on the retrieved values with Node.js.

**CRP caveat, verbatim** (same APS panel):

> "BV-based APS may be used for measurands with stable concentrations or activities. However, we advise against applying BV-based APS for measurands that are present at low concentrations in healthy individuals but which may increase markedly in disease states, such as inflammatory markers (e.g. CRP) and tumour markers. It is also important to note that some currently available BV estimates are based on limited datasets and may therefore be associated with a high degree of uncertainty."

### Global estimates, retrieved 2026-10-24 (healthy adults, weekly to monthly sampling)

Column notes:
- **CVI and CVG** are the database values (median, lower, upper), shown to 2 decimals.
- **n est.** is the API field `number_used`. Sex-stratified datasets from one study appear to be pooled, so it can be smaller than the number of datasets.
- **Des. CVA** is the desirable imprecision APS from the site's function (Min / Opt in brackets).
- **Typical reported CVA (derived)** is the median and range of the analytical CVs reported by the datasets included in the meta-analysis (field `analytical_cv`). It is my summary, not an EFLM output.

| Measurand (EFLM name, id) | Matrix | CVI % (95% CI) | n est. (datasets) | CVG % (95% CI) | Des. CVA % [min / opt] | Typical reported CVA (derived) | Meta updated |
|---|---|---|---|---|---|---|---|
| Albumin (1515) | Serum/plasma | **2.47 (1.21–3.00)** | 14 (16) | 4.13 (3.00–5.18) | **1.3** [1.9 / 0.6] | 1.45 (0.54–3.3), n=16 | 2026-10-20 |
| Creatinine (1501) | Serum/plasma | **4.39 (2.30–4.73)** | 15 (17) | 16.11 (12.41–17.10) | **2.2** [3.3 / 1.1] | 2.60 (1.1–5.56), n=17 | 2026-10-08 |
| Glucose (1518) | Serum/plasma | **4.89 (3.07–6.74)** | 11 (12) | 8.10 (2.70–10.80) | **2.5** [3.7 / 1.2] | 1.65 (0.58–2.5), n=12 | 2026-10-08 |
| C-reactive protein (CRP) (1635) | Serum/plasma | **34.68 (29.40–74.40)** | 6 (6) | 87.08 (71.30–94.00) | 17.4 [26 / 8.7] (EFLM advises against BV-APS for CRP) | 5.20 (2.0–11.1), n=6 | 2026-10-08 |
| CRP – high-sensitive (1634) | Serum | **No global estimate** (BIVAC records only) | 0 (5) | — | — | 2.50 (1.63–5.0), n=3 | — |
| Lymphocytes (1534) | Whole blood | **10.87 (9.81–14.70)** | 7 (8) | 22.41 (21.30–35.30) | **5.5** [8.2 / 2.7] | 2.45 (1.8–6.9), n=8 | 2026-10-08 |
| Mean corpuscular volume (MCV) (1527) | Whole blood | **0.80 (0.60–1.65)** | 9 (12) | 3.90 (3.40–4.70) | **0.4** [0.6 / 0.2] | 0.40 (0.17–1.0), n=12 | 2026-10-08 |
| Red cell distribution width SD (RDW-SD) (1528) | Whole blood | **1.70 (1.42–3.70)** | 5 (8) | 4.29 (3.63–6.83) | **0.9** [1.3 / 0.4] | 0.68 (0.57–2.1), n=8 | 2026-10-08 |
| Alkaline phosphatase (ALP) – total (1690) | Serum/plasma | **5.25 (2.60–6.00)** | 10 (11) | 22.57 (17.80–26.50) | **2.6** [3.9 / 1.3] | 2.20 (1.22–4.8), n=11 | 2026-10-08 |
| Leukocytes (WBC) (1532) | Whole blood | **11.10 (8.90–15.90)** | 9 (12) | 17.28 (15.00–32.70) | **5.6** [8.3 / 2.8] | 1.50 (1.1–7.9), n=12 | 2026-10-08 |
| LDL cholesterol (1498) | Serum/plasma | **7.56 (7.00–8.46)** | 14 (21) | 23.81 (17.60–37.68) | **3.8** [5.7 / 1.9] | 2.10 (1.3–5.3), n=21 | 2026-10-08 |
| Haemoglobin A1c (IFCC, mmol/mol) (1497) | Whole blood | **1.63 (1.30–2.50)** | 2 (2) | 7.30 (7.10–7.50) | **0.8** [1.2 / 0.4] | 1.55 (0.7–2.4), n=2 | 2026-10-08 |
| Haemoglobin A1c (NGSP, %) (1641) | Whole blood | **1.17 (0.29–7.00)** | 6 (6) | 5.35 (4.30–7.50) | **0.6** [0.9 / 0.3] | 1.05 (0.4–2.2), n=6 | 2026-10-08 |

**Verbatim API values** (CVI `median` / `lower` / `upper`, exactly as returned) in the order of the table:
- Albumin: 2.473462309945139 / '1.2092587900195075' / '3.0'
- Creatinine: 4.392143969990116 / '2.3' / '4.725325766187275'
- Glucose: 4.88930939748159 / '3.072130119400876' / '6.743594313041439'
- CRP: 34.676714428835304 / '29.4' / '74.4'
- Lymphocytes: 10.867419550452162 / '9.81' / '14.7'
- MCV: 0.7987225607627971 / '0.6' / '1.6500672947510093'
- RDW-SD: 1.6977231289114796 / '1.416263670755474' / '3.7'
- ALP: 5.245001763881076 / '2.6' / '6.004953560371517'
- Leukocytes: 11.1 / '8.9' / '15.9'
- LDL-C: 7.5551713657981185 / '7.0' / '8.46'
- HbA1c IFCC: 1.6297968397291196 / '1.3' / '2.5'
- HbA1c NGSP: 1.173036806548661 / '0.29' / '7.0'

All are from `…/api/meta_calculations/meta_by_analyte/<id>`; each record carries `"engine":"ruby","calculator_version":"1.0.0"`. The site displays them rounded to 1 decimal.

### Analyte-specific notes and caveats

1. **Recalculated this month.** Every global estimate was recalculated on 2026-10-08 (albumin on 2026-10-20). The values can differ from earlier versions of the database and from older printed tables. Cite them as "EFLM BVD, accessed 2026-10-24".
2. **CI construction.** For fewer than 10 estimates the 95% CI is by definition the range of the included estimates. That applies to CRP, lymphocytes, MCV, RDW, WBC and both HbA1c measurands, so these CIs are wide and asymmetric. Albumin, creatinine, glucose, ALP and LDL-C (10 or more estimates) use percentile bootstrap.
3. **Creatinine, enzymatic vs Jaffe.** The EFLM global estimate pools methods. Method-specific values come from the EuBIVAS study. Carobene A, et al. *Clin Chem* 2017;63(9):1527–1536. doi:10.1373/clinchem.2017.275115. PMID 28720681. Abstract, verbatim:
   > "The within-subject BV estimates [CVI (95% CI)] were similar for enzymatic [4.4% (4.2-4.7)] and alkaline picrate [4.7% (4.4-4.9)] methods … CVA was 1.1% for the enzymatic and 4.4% for alkaline picrate methods, indicating that alkaline picrate methods fail to fulfill analytical performance specifications for imprecision."

   Design: 91 healthy adults, 10 weekly samples, 6 European laboratories.
4. **Glucose, fasting.** Fasting status is not a database field. The included datasets record morning sampling times (07:30–11:00). The estimate is for morning samples from healthy adults, not explicitly fasting.
5. **CRP and hs-CRP.**
   - The CRP global estimate rests on 6 datasets: Clark & Fraser 1993, Sakkinen 1999, Corte & Venta 2020, Nunes 2010, Macy 1997, and EuBIVAS (Carobene 2019, CVI 29.4%).
   - "CRP – high-sensitive" has 5 BIVAC records and no global estimate: CVI 26.87%, 58.9%, 54.9%, 39.0% and 71.1%; the last is a non-healthy group. All are graded C and flagged `include_in_meta_analysis: false`.
   - EFLM explicitly advises against BV-based APS for CRP (quote above).
6. **Lymphocytes.**
   - The global estimate is essentially for **absolute count**: 7 of 8 datasets are in ×10⁹/L (means about 2.0–2.25) or cells/µL.
   - One included dataset is **lymphocyte percentage**: Costongs 1985, unit "%", mean 32.0%, CVI 10.8%.
   - The database has **no separate lymphocyte % measurand**. PhenoAge uses lymphocyte %, so no EFLM global CVI exists for that exact input (NOT VERIFIED). The single lymphocyte % dataset (CVI 10.8%) is the only database figure.
7. **RDW.**
   - The database lists only "Red cell distribution wide standard deviation (RDW-SD)".
   - Its meta-analysis mixes 6 RDW-SD-type datasets (means 39.3–43.3, recorded as "mL/mL"; this is fL scale) with 2 RDW-CV-type datasets: Nunes 2010 (mean 12.7%, CVI 2.0%) and Costongs 1985 (mean 15.5%, CVI 3.7%).
   - PhenoAge uses **RDW-CV (%)**, which has **no EFLM global estimate** (NOT VERIFIED). The global 1.70% (1.42–3.70) is dominated by RDW-SD data and should be used for RDW-CV only with that caveat.
8. **HbA1c.** The IFCC (mmol/mol) estimate rests on only 2 datasets. The NGSP (%) CI is very wide (0.29–7.0) because it is the range of 6 estimates.
9. **Typical CVA.** The "typical reported CVA" column is descriptive and derived. A laboratory's own CVA should replace it in modelling.

---

## E2. Levine 2018 phenotypic-age equation; Liu 2018 mortality association

### E2a. Equation and constants — VERIFIED (with a discrepancy to flag)

**Primary source**: Levine ME, Lu AT, Quach A, et al. An epigenetic biomarker of aging for lifespan and healthspan. *Aging (Albany NY)* 2018;10(4):573–591. doi:10.18632/aging.101414. PMID 29676998. PMCID PMC5940111.
- Full text: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5940111/fullTextXML
- Supplement 1 (`aging-10-101414-s001.pdf`): from the Europe PMC supplementaryFiles bundle, https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5940111/supplementaryFiles

**Supplement 1, verbatim** (math rendered from the PDF):

> "we estimated the 10-year (120 months) mortality risk of the j-the individual based on the cumulative distribution function MortalityScore_j = CDF(120, x_j) = 1 − e^(−e^(x_j b) (exp(120∗γ)−1)/γ)"
>
> "PhenotypicAge_j = 141.50225 + ln(−.00553 ∗ ln(1 − MortalityScore_j)) / 0.090165"
>
> "The Gompertz regression analysis resulted in coefficient values and parameter values (Table 1, Table S1) and γ =0.0076927."
>
> "In step 4, we solved the equation CDF(120,xj)=CDF.univariate(120,agej) for the variable agej."

**Supplementary Table S1 / main-text Table 1, verbatim** (variable | units | weight):

| Variable | Unit | Weight |
|---|---|---|
| Albumin | g/L | −0.0336 |
| Creatinine | umol/L | 0.0095 |
| Glucose, serum | mmol/L | 0.1953 |
| C-reactive protein (log) | mg/dL | 0.0954 |
| Lymphocyte percent | % | −0.0120 |
| Mean cell volume | fL | 0.0268 |
| Red cell distribution width | % | 0.3306 |
| Alkaline phosphatase | U/L | 0.0019 |
| White blood cell count | 1000 cells/uL | 0.0554 |
| Age | Years | 0.0804 |
| Constant | — | −19.9067 |
| Gamma | — | 0.0077 |

**Resulting equation** (Levine Supplement 1 constants; my arithmetic check: exp(120 × 0.0076927) − 1 = 1.51714, matching the correction below):

- xb = −19.9067 − 0.0336·Alb + 0.0095·Creat + 0.1953·Glu + 0.0954·ln(CRP) − 0.0120·Lymph% + 0.0268·MCV + 0.3306·RDW + 0.0019·ALP + 0.0554·WBC + 0.0804·Age
- M = 1 − exp(−exp(xb) · (exp(120γ) − 1)/γ), with γ = 0.0076927
- PhenoAge = 141.50225 + ln(−0.00553 · ln(1 − M)) / 0.090165

**Liu 2018 and its correction.**

Liu Z, Kuo PL, Horvath S, Crimmins E, Ferrucci L, Levine M. *PLoS Med* 2018;15(12):e1002718. doi:10.1371/journal.pmed.1002718. PMID 30596641. PMCID PMC6312200.

Correction: *PLoS Med* 2019;16(2):e1002760. doi:10.1371/journal.pmed.1002760. PMID 30802240. PMCID PMC6388911. Verbatim:

> "The equation in the subsection of the Methods section titled "Phenotypic Age" is missing a step which makes it impossible to resolve. The equation should read: PhenotypicAge=141.50+ln[−0.00553×ln(1−M)]/0.09165 Where: M=1−exp(−1.51714×exp(xb)/0.0076927) and: xb=−19.907−0.0336×Albumin+0.0095×Creatinine+0.1953×Glucose+0.0954×ln(CRP)−0.0120×LymphocytePercent+0.0268×MeanCellVolume+0.3306×RedCellDistributionWidth+0.00188×AlkalinePhosphatase+0.0554×WhiteBloodCellCount+0.0804×ChronologicalAge"

**Discrepancies between published versions (must be addressed in the methods paper):**

| Item | Levine 2018 Supplement 1 (primary derivation) | Liu 2018 as originally printed | Liu correction 2019 |
|---|---|---|---|
| Intercept constant | **141.50225** | 141.50 | 141.50 |
| Divisor | **0.090165** | 0.09165 | **0.09165** (differs from 0.090165) |
| Log multiplier | 0.00553 | 0.00553 | 0.00553 |
| Mortality-score step | given | **missing** (ln(1 − xb)) | restored with 1.51714 and 0.0076927 |
| Glucose weight | 0.1953 | **0.0195** (typo) | 0.1953 |
| RDW weight | 0.3306 | **0.3356** | 0.3306 |
| ALP weight | 0.0019 (rounded) | 0.00188 | 0.00188 |
| xb constant | −19.9067 | −19.907 | −19.907 |

- 0.090165 versus 0.09165 is not a rounding difference. For a typical healthy 50-year-old input set the two divisors give PhenoAge values about 1.5 years apart (derived).
- The constants requested in this task (141.50225, 0.00553, 0.090165, γ 0.0076927) match **Levine 2018 Supplement 1**. Cite that supplement as the source and note the Liu/correction printing (141.50; 0.09165).
- **Implementation cross-check (lead, not peer-reviewed)**: the BioAge R package (Kwon & Belsky), `R/phenoage_calc.R` at https://raw.githubusercontent.com/dayoonkwon/BioAge/master/R/phenoage_calc.R, implements `m_orig = 1 - (exp((-1.51714 * exp(xb_orig)) / 0.007692696))` and `phenoage0 = ((log(-.0055305 * (log(1 - m_orig))) / .090165) + 141.50225)`, with xb coefficients at higher precision (e.g., −19.90667, −0.03359355, 0.009506491, 0.1953192, 0.09536762, −0.01199984, 0.02676401, 0.3306156, 0.001868778, 0.05542406, 0.08035356). It uses 0.090165, consistent with Levine's supplement.
- **Units caveat**: Levine's table states CRP as "(log) … mg/dL". Using mg/L shifts ln(CRP) by ln(10) = 2.303 and xb by 0.22 (derived). Albumin is g/L, creatinine µmol/L, glucose mmol/L, WBC 10³/µL.

### E2b. Mortality association of phenotypic age — VERIFIED

**Levine 2018** (NHANES IV validation). Main text, verbatim:

> "Validation data for phenotypic age came from NHANES IV, and included up to 12 years of mortality follow-up for n=6,209 national representative US adults. … adjusting for chronological age (Table 2), show that a one-year increase in phenotypic age is associated with a 9% increase in the risk of all-cause mortality (HR=1.09, p=3.8E-49)"

Table 2: "All-Cause | 1052 | 1.09 | 3.8E-49". No 95% CI is reported.

Caveat: Supplement 1 says NHANES IV "had available mortality follow-up for up to 17 years", which is inconsistent with "up to 12 years" in the main text.

**Liu 2018** (NHANES IV 1999–2010; 11,432 adults aged 20–84; NDI follow-up to 31 Dec 2011; parametric Gompertz proportional-hazards model adjusted for chronological age and sex). Verbatim:

> "In the full sample, each 1-year increase in Phenotypic Age (after adjusting for chronological age) increased the risk of mortality by 9% (hazard ratio [HR] = 1.09, 95% CI = 1.08–1.10)."

Table 1:
- "All-cause | Full sample | 871 | 1.09 (1.08–1.10)"
- 5+ years survival: 1.08 (1.06–1.10)
- Ages 20–39: 1.13 (1.09–1.18)
- Ages 40–64: 1.10 (1.08–1.12)
- Ages 65–84: 1.08 (1.06–1.09)
- Footnote: "All models were adjusted for chronological age and sex."

**PhenoAgeAccel definition**, verbatim (Liu 2018):

> "Phenotypic Age Acceleration (PhenoAgeAccel), defined as the residual resulting from a linear model when regressing Phenotypic Age on chronological age."

Caveats:
- (i) Liu's HR is for Phenotypic Age with chronological age as a covariate, not for PhenoAgeAccel entered directly. Because PhenoAgeAccel is the linear residual on age and age is in the model, the per-year coefficient is equivalent (my inference).
- (ii) The abstract reports 1,012 deaths overall (including the 185 participants aged 85+), whereas Table 1 analyses 871 deaths in ages 20–84.
- (iii) The Fig 3B legend states PhenoAgeAccel had "a mean of 0 …, a standard deviation of 1, and a median of −0.13". The standard deviation of 1 does not match a scale in years; do not use it to convert per-SD to per-year.

---

## E3. PhenoAge in Chinese populations

**No study was found that applies the original 9-biomarker Levine PhenoAge to a Chinese general-population cohort and reports an all-cause-mortality HR per year or per SD of acceleration.** The original formula: NOT VERIFIED. The closest evidence:

1. **Wang K, Gao J, Liu Y, et al.** Biological age construction for prediction of mortality in the Chinese population. *GeroScience* 2025;47(4):5869–5880. doi:10.1007/s11357-025-01612-x. PMID 40148729. PMCID PMC12397035. Retrieved via Europe PMC abstract and https://pmc.ncbi.nlm.nih.gov/articles/PMC12397035/.
   - Design: Kailuan Study I (n=83,571, development) and Kailuan Study II (n=21,229, validation); 1,443,857 person-years; 12,679 deaths.
   - Verbatim: "The pooled multivariable-adjusted HRs (95% CIs) for per standard deviation increment of baseline Pheno-Age acceleration and mortality was **1.24 (1.18, 1.30)**".
   - Method, verbatim: "Using Levine's methods [12], we separately created two Gompertz proportional hazard models for men and women to estimate the 15-year mortality risk predicted by CA and the selected markers."
   - Caveat: the markers were *re-selected*. Men: SBP, WC, hs-CRP, ALT, urea nitrogen, RBC, PLT, eGFR, LYM. Women: 13 markers. This is a re-derived, Levine-method variant, not the original equation. The SD of acceleration in years is not reported, so the HR cannot be converted to per-year.
2. **Zhang JJ, Yu HC, Geng TT, et al.** Changes in accelerated aging and risk of cardiovascular disease and mortality: three cohort studies. *BMC Med* 2025;23(1):533. doi:10.1186/s12916-025-04365-8. PMID 41044581. PMCID PMC12495707.
   - Design: Kailuan (n=107,830), Dongfeng-Tongji (n=14,032) and UK Biobank.
   - Verbatim (abstract): "baseline accelerated aging was significantly associated with increased risks of CVD (pooled HR: 1.41, 95% CI: 1.25, 1.60) and mortality (pooled HR: **1.47, 95% CI: 1.33, 1.63**)".
   - Caveat: acceleration is **binary** (residual > 0). In the Chinese cohorts, "PhenoAge" was re-derived from "fasting blood glucose, waist circumference, systolic blood pressure, high-density lipoprotein cholesterol, total cholesterol, blood urea nitrogen, mean corpuscular hemoglobin, platelets, red blood cell count" (verbatim). The pooled HR also includes UK Biobank.
3. **Zhu Z, Lyu J, Hao X, et al.** Estimation of physiological aging based on routine clinical biomarkers: a prospective cohort study in elderly Chinese and the UK Biobank. *BMC Med* 2024;22(1):552. doi:10.1186/s12916-024-03769-2. PMID 39578829. PMCID PMC11583456.
   - Dongfeng-Tongji testing set (n=15,904).
   - Verbatim: "When calculating PhenoAge (Additional file 1: Table S3), we ignored albumin and C-reactive protein because these two biomarkers were not measured in the DFTJ cohort."
   - Mortality discrimination for PhenoAge: C-index **0.799 (0.784, 0.814)**.
   - HRs for ΔPhenoAge appear only in Supplementary Table S7 (not retrieved; NOT VERIFIED).
4. **CHARLS lacks the inputs.** Tan MY, et al. *Cardiovasc Diabetol* 2025;24(1):402. doi:10.1186/s12933-025-02940-0. PMID 41126270. Verbatim: "PhenoAgeAccel was excluded from the analysis due to incomplete data in CHARLS."
5. **China Kadoorie Biobank**: no blood-chemistry PhenoAge study found. A 2026 *Heart* paper (Wu Z et al., doi:10.1136/heartjnl-2026-327950, PMID 42144279) used DNAm PhenoAge in an n=980 CKB subsample; its abstract gives no HR.
6. **Hong Kong**: Tang TH, et al. *J Gerontol A* 2026;81(11):glag221. doi:10.1093/gerona/glag221. PMID 42691214 (people with HIV, Queen Elizabeth Hospital). Original PhenoAge, but stability only, no mortality (see E4).

Best lead for a per-year HR with the original formula in Chinese adults: contact Zhu et al. (DFTJ, Table S7, 7-marker variant), or compute it in Kailuan or Hong Kong EHR data.

---

## E4. Short-term within-person variability or test–retest of blood-based PhenoAge

**NOT VERIFIED: no published study found** quantifying test–retest reliability, ICC or within-person CV of blood-based PhenoAge from repeated draws days to months apart.
- Searches: Europe PMC (PhenoAge or phenotypic age × reliability, test–retest, intraclass, within-person, intra-individual, biological variation, EuBIVAS, reference change value, second examination) and a web search (extended mode).
- Related evidence (long intervals only):

1. **Levine 2018 (InCHIANTI, 1998 → 2007, about 9 years)**, verbatim:
   > "participants' clinical phenotypic age (adjusting for chronological age) at the two time-points was correlated at r=0.50, whereas participants' DNAm PhenoAge (adjusting for chronological age) at the two time-points was correlated at r=0.68"
2. **Tang TH et al. 2026** (Hong Kong, 728 people with HIV on suppressive ART, about 5 years apart), verbatim:
   > "the median PAA values at T0 and T5 were -0.38 and -0.47 years, indicating non-significant change over five years … However, interindividual variability in PAA exists"

   No ICC is reported.
3. **Lin WY 2026**, Taiwan Biobank, 4.9-year ΔPhenoAge in 69,462 participants. *Front Aging* 2026. doi:10.3389/fragi.2026.1802176. PMID 42179442. Determinants of change only; no reliability statistic in the abstract.

**Recommended approach (derived, not literature)**: propagate the E1 CVI and CVA values through the PhenoAge equation to estimate the expected short-term SD of PhenoAge. Label the result as model-based. The lymphocyte % and RDW-CV inputs lack EFLM global estimates (E1 notes 6–7).

---

## E5. Epigenetic clocks and all-cause mortality

| Clock | HR (95% CI) | Contrast | Population / model | Source and quote |
|---|---|---|---|---|
| Horvath AgeAccel | **1.024 (1.017–1.031)** | per 1-year AgeAccel | 13 cohorts, 13,089 people; age-adjusted, fixed-effect meta-analysis | Chen 2016 Fig 2A (figure): "Meta (FE) 1.024 [1.017, 1.031]"; P=1.9e-11 |
| Horvath AgeAccel, multivariable | 1.016 (1.008–1.023) | per year | Adjusted for BMI, education, alcohol, pack-years, diabetes, cancer, hypertension, physical activity | Chen 2016 Fig 3A (figure); P=5.4e-05 |
| Hannum AgeAccel | **1.038 (1.032–1.045)** | per year | Age-adjusted | Chen 2016 Suppl. Fig 1A (figure); P=1.4e-34 |
| Hannum AgeAccel, multivariable | 1.027 (1.020–1.034) | per year | As above | Chen 2016 Suppl. Fig 2A (figure); P=6e-15 |
| EEAA (Hannum-based, extrinsic) | 1.040 (1.034–1.046) | per year | Age-adjusted | Chen 2016 Fig 2C; text: "The HR of EEAA is 1.040 if EEAA=1" |
| DNAm PhenoAge (AgeAccel) | **1.045 (1.039–1.051)** | per year | 5 validation samples (WHI ×2, FHS, NAS, JHS); age-adjusted Cox, fixed-effect meta | Levine 2018 text: "a one-year increase in DNAm PhenoAge is associated with a 4.5% increase in the risk of all-cause mortality (Meta(FE)=1.045, Meta p=7.9E-47, Fig. 2)". CI from Fig 2A (figure). Same figure: Hannum 1.041 (1.032–1.049); Horvath 1.017 (1.009–1.025) |
| GrimAge (AgeAccelGrim) | **1.10 (1.09–1.12)** | per year | Validation data, N=7,375 arrays (FHS, WHI, InCHIANTI, JHS strata) | Lu 2019 text: "AgeAccelGrim (P=2.0E-75, HR=1.10), AgeAccel (Meta P=8.9E-5, HR=1.02 …), AgeAccelHannum (Meta P=6.8E-16, HR=1.04), AgeAccelPheno (Meta P=3.5E-36, HR=1.05)". CI from Fig 3A (figure): "FE model 1.10 [1.09, 1.12]". Horvath, Hannum and Pheno CIs not in the text |
| McCrory 2021 (TILDA) | GrimAge **2.05 (1.45–2.90)**; PhenoAge 1.26 (0.92–1.74); Horvath 0.97 (0.70–1.36); Hannum 0.89 (0.64–1.24) | **per SD** (z-score) of cell-intrinsic AA | n=489, 35 deaths, up to 10 years; adjusted for age, sex and WBC. Model 2 GrimAge: 1.91 (1.23–2.96) | Verbatim: "a standard unit increase in GrimAgeAA was associated with a 2-fold increase (hazard ratio [HR] = 2.05, 95% CI = 1.45, 2.90; p < .001)… None of the other epigenetic AA measures significantly predicted mortality." |
| DunedinPACE | **1.26 (1.14–1.40)** (NAS); **1.65 (1.51–1.79)** (FHS Offspring) | **per SD** | NAS: n=771 men, mean age 77, 46% died. FHS: n=2,471, mean age 66, 23% died. Adjusted for age and sex | Belsky 2022, verbatim: "for mortality, DunedinPACE HR = 1.26 95% CI [1.14–1.40]"; "mortality HR = 1.65 95% CI [1.51–1.79]" |

Sources:
- Chen BH, Marioni RE, Colicino E, et al. *Aging (Albany NY)* 2016;8(9):1844–1865. doi:10.18632/aging.101020. PMID 27690265. PMCID PMC5076441. Text verbatim: "All of our Cox models were adjusted for the age at baseline (blood draw)."
- Lu AT, Quach A, Wilson JG, et al. *Aging (Albany NY)* 2019;11(2):303–327. doi:10.18632/aging.101684. PMID 30669119. PMCID PMC6366976.
- McCrory C, Fiorito G, Hernandez B, et al. *J Gerontol A Biol Sci Med Sci* 2021;76(5):741–749. doi:10.1093/gerona/glaa286. PMID 33211845. PMCID PMC8087266 (https://pmc.ncbi.nlm.nih.gov/articles/PMC8087266/).
- Belsky DW, Caspi A, Corcoran DL, et al. *eLife* 2022;11:e73420. doi:10.7554/eLife.73420. PMID 35029144. PMCID PMC8853656.

Caveats:
- Per-year HRs are not comparable across clocks, because AgeAccel SDs differ. Chen 2016, verbatim: "It is not appropriate to compare the hazard ratios and confidence intervals of the different measures directly because the measures have different scales/distributions."
- Values marked (figure) are legible readings of the published forest plots.

---

## E6. Technical reliability of epigenetic clocks

**Higgins-Chen AT, Thrush KL, Wang Y, et al.** A computational solution for bolstering reliability of epigenetic clocks: implications for clinical trials and longitudinal tracking. *Nat Aging* 2022;2(7):644–661. doi:10.1038/s43587-022-00248-2. PMID 36277076. PMCID PMC9586209 (author manuscript; https://pmc.ncbi.nlm.nih.gov/articles/PMC9586209/). Data: 36 pairs of blood technical replicates (GSE55763). Verbatim:

- "Here we show technical noise produces deviations up to 9 years between replicates for six prominent epigenetic clocks … Our retrained principal-component versions of six clocks show agreement between most replicates within 1.5 years"
- "We find significant unreliability in epigenetic clock measurements, resulting in up to 3 to 9 years difference between technical replicates depending on the clock. For comparison, the standard deviation of epigenetic age acceleration is 3 to 5 years."
- "Horvath1, Horvath2, Hannum, and PhenoAge maximum deviations exceeded 1 SD of age acceleration, while GrimAge and DNAmTL maximum deviations were 0.57 and 0.69 SD respectively. The high reliability of GrimAge (ICC = 0.989) …"
- "Most replicates (>90%) show agreement within 1–1.5 years. The median deviation ranges from 0.3–0.8 years (improvement from 0.9–2.4 years for CpG clocks). … all PC clocks show ICC>0.99 for epigenetic age and ICC>0.97 for age acceleration"
- "CpG-trained PhenoAge has a median deviation of 2.4 years and maximum of 8.6 years. In contrast, PCPhenoAge has a median deviation of 0.6 years, and maximum of 1.6 years."
- "Training clocks using principal components … consistently producing clock ICCs 0.99–0.998 and age acceleration ICCs 0.97–0.99."
- Original-clock ICCs other than GrimAge appear only in figures and supplementary tables. Approximate readings:
  - Fig 3g, epigenetic age: Horvath1 ≈0.95, Horvath2 ≈0.98, Hannum ≈0.98, PhenoAge ≈0.92, GrimAge ≈0.99.
  - Fig 3h, age acceleration: Horvath1 ≈0.83, Horvath2 ≈0.89, Hannum ≈0.86, PhenoAge ≈0.76, DNAmTL ≈0.95, GrimAge ≈0.96.
  - Exact values: NOT VERIFIED (Supplementary Tables 3–4 not retrieved).

**Biological (short-interval) reliability is lower than technical reliability.** Sehgal R, Borrus D, Gonzalez J, et al. *Aging Cell* 2026;25(8):e70635. doi:10.1111/acel.70635. PMID 42525215. PMCID PMC13418614. Verbatim:

> "Pooled estimates … from four independent studies revealed that most clocks achieved only "moderate" to "good" reliability (ICC ≈ 0.4–0.7), with no clock reaching the "excellent" range. Clocks such as GrimAge (versions I and II), DNAmEMRAge, and DunedinPACE generally clustered near the lower end of this spectrum"

Perturbations studied: meals, acute stress, pollution, altitude.

**Two-year behaviour.** Hamaya R, et al. *GeroScience* 2026;48(4):5843–5857. doi:10.1007/s11357-025-01990-2. PMID 41217671 (COSMOS, n=899, mean age 70). Verbatim:

> "Baseline values strongly predicted the same measure at years 1 and 2 (R2 ≈ 0.71-0.88 for PC clocks) … first-year increases tended to be followed by second-year decreases, consistent with regression to the mean"

**DunedinPACE technical ICCs** (Belsky 2022), verbatim:

> "For DunedinPACE, reliability was excellent (ICC = 0.96 [0.93–0.98]; Figure 2) … DunedinPACE ICCs were 0.97 [0.94–0.98] in the EPIC-EPIC database and 0.87 [0.82–0.90] in the 450k-EPIC database."

The Figure 2 legend gives "0.96 95% CI [0.92–0.98]", a minor internal inconsistency in the lower bound.

Implications for LongPi:
- Commercial DNAm clock results should be treated as having technical SD on the order of years, unless the clock is PC-based or DunedinPACE.
- Short-interval biological fluctuation (ICC about 0.4–0.7) limits single-draw change detection even for technically reliable clocks.

---

## E7. DunedinPACE definition, distribution and test–retest

Source: Belsky DW, et al. *eLife* 2022;11:e73420 (see E5).

- **Definition (VERIFIED)**, verbatim: "The resulting Pace of Aging was then scaled to a mean of 1, so that it could be interpreted with reference to an average rate of 1 year of biological aging per year of chronological aging. Study members showed wide variation in their Pace of Aging (Mean = 1 biological year per chronological year, SD = 0.29)." Also: "Pace of Aging was scaled in units representing the mean trend in the cohort, that is the average physiological change occurring during one calendar year (N = 955, M = 1, SD = 0.29). Of the N = 818 Dunedin Study members with methylation data at age 45, N = 817 had measured Pace of Aging (M = 0.99, SD = 0.30)."
- **Criterion design**: "19 indicators of organ-system integrity across four time points spanning two decades" (ages 26, 32, 38, 45). DunedinPACE has 173 CpGs; in-sample correlation with 20-year Pace of Aging r = 0.78.
- **Distribution of DunedinPACE values**: the mean and SD of DunedinPACE itself are not stated in the main text (NOT VERIFIED). The paper's NAS result implies an SD of about 0.1 (derived: 0.021/0.2). Verbatim: "DunedinPACE increased by b = 0.021 (SE = 0.003) per 5 years of follow-up, or approximately 0.2 standard deviation units"
- **Normalization**: "the algorithm to implement DunedinPACE includes a normalization step that allows DunedinPACE values for individual samples to be compared to the Dunedin Study cohort in which the measure was developed."
- **Test–retest ICC**: 0.96 (0.93–0.98), 450k–450k, n=36; 0.97 (0.94–0.98), EPIC–EPIC, n=28; 0.87 (0.82–0.90), 450k–EPIC, n=350. Biological short-interval reliability is lower (Sehgal 2026, E6).

---

## E8. How many repeated measurements are needed to estimate an individual's rate of ageing

**No formal guidance was found specific to blood-chemistry clocks such as PhenoAge** (NOT VERIFIED). Verified design precedents and methods literature:

1. **Belsky DW, Caspi A, Houts R, et al.** Quantification of biological aging in young adults. *PNAS* 2015;112(30):E4104–E4110. doi:10.1073/pnas.1506264112. PMID 26150497. PMCID PMC4522793. Verbatim:
   - "We studied aging in 954 young humans … tracking multiple biomarkers across three time points spanning their third and fourth decades of life."
   - "Of the 51,516 potential observations (n = 954 study members × 18 biomarkers × 3 time points), 44,475 (86.3%) were present … We calculated Pace of Aging from slopes … An additive model reduces the influence of temporary change isolated to any specific organ system, e.g., as might arise from a transient infection."
   - Waves at ages 26, 32 and 38 (12 years). Scaled so "the central tendency in the cohort indicates 1 y of physiological change for every one chronological year."
2. **Elliott ML, Caspi A, Houts RM, et al.** *Nat Aging* 2021;1(3):295–308. doi:10.1038/s43587-021-00044-4. PMID 33796868. PMCID PMC8009092. Verbatim: "Second, we report 4 biomarker waves, which increases statistical power for growth-curve models of biomarker-decline slopes and improves precision of the Pace of Aging." Design: 19 biomarkers at 26, 32, 38 and 45 (20 years). Mean 1, SD 0.29.
3. **DunedinPACE (Belsky 2022)** attributes its precision gain to longer follow-up plus the additional wave. Verbatim: "The longer follow-up period … and the additional measurement occasion included in analysis improve the power and precision of our modeling of longitudinal change in system integrity (Brandmaier et al., 2018; Rast and Hofer, 2014)."
4. **Brandmaier AM, von Oertzen T, Ghisletta P, Lindenberger U, Hertzog C.** *Front Psychol* 2018;9:294. doi:10.3389/fpsyg.2018.00294. PMID 29755377. PMCID PMC5932409. Verbatim: "design precision can be expressed as the inverse of effective error. Effective error is determined by instrument reliability and the temporal arrangement of measurement occasions."
5. **Rast P, Hofer SM.** *Psychol Methods* 2014;19(1):133–154. doi:10.1037/a0034524. PMID 24219544. Verbatim: "We performed simulations to investigate the interplay among number and spacing of occasions, total duration of the study, effect size, and error variance on power … Power to detect change is generally low in the early phases (i.e., first years) of longitudinal studies but can substantially increase if the design is optimized. We recommend additional assessments, including embedded intensive measurement designs".
6. **Hamaya 2026** (E6): over 2 years, annual changes in clocks were "statistically detectable but numerically small" and showed regression to the mean. "Current epigenetic measures … appear stable on average … implying limited sensitivity to short-term change."

Implication for LongPi Pace (my reading, not a literature value):
- The Dunedin precedents are 3 waves over 12 years and 4 waves over 20 years.
- Slope precision depends on the ratio of within-person noise (E1 CVIs plus CVA, and E6 for DNAm) to true slope variance, and on the total time span.
- A short-interval "pace" from 2–3 draws will mostly reflect noise unless the draws are averaged or span years. A simulation using the E1 CVIs is the defensible way to set a minimum number of draws and span.

---

## Search log (for audit)

- **EFLM**: biologicalvariation.eu HTML → JS bundle → API endpoints (`/api/measurands`, `/api/meta_calculations/meta_by_analyte/{id}`, `/api/analyte_specifications/{id}`, `/api/bv_specifications/{id}`); CMS pages `/wp-json/wp/v2/pages/{2,10,25,40}`.
- **Europe PMC queries**:
  - PhenoAge × China/Kailuan/CHARLS/Dongfeng-Tongji/CKB/Hong Kong/CLHLS/Taiwan × mortality
  - PhenoAge × reliability/test–retest/within-person/biological variation
  - Title searches for every named paper
- **Full texts**: Europe PMC fullTextXML (PMC5940111, PMC6312200, PMC6388911, PMC5076441, PMC6366976, PMC8853656, PMC8009092, PMC12495707, PMC11583456, PMC12542049, PMC13418614, PMC7012595) and PMC HTML (PMC8087266, PMC9586209, PMC4522793, PMC12397035).
- **Supplements and figures**: Europe PMC supplementaryFiles bundles for PMC5940111, PMC5076441 and PMC6366976.
- **Not retrieved**: Higgins-Chen Supplementary Tables 3–4; Zhu 2024 Table S7; Coskun 2018 CCLM full text (download blocked).
