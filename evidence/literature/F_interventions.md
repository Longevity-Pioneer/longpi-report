# Topic F: intervention effect sizes, verified against sources

Prepared 2026-10-24 for the LongPi intervention module. Each item gives the value, 95% CI, unit/contrast, population and design, source, the URL actually retrieved, verbatim quotes, and caveats.

**Retrieval rules followed.** Every PMID/DOI below comes from a Europe PMC or NCBI record that was retrieved in this session. Abstracts came from the Europe PMC REST API (`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:<PMID>%20AND%20SRC:MED&format=json&resultType=core`) or NCBI E-utilities (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<PMID>&rettype=abstract&retmode=text`). Full texts came from Europe PMC `.../rest/<PMCID>/fullTextXML` or NCBI `efetch.fcgi?db=pmc&id=<PMCID>`, unless another URL is given. Quotes are verbatim; only whitespace and super/subscript artefacts from the XML/PDF-to-text conversion were normalised. **Derived** marks numbers I calculated, which do not appear in the source. **NOT VERIFIED** marks numbers I could not confirm on a retrieved page.

---

## F1. Aerobic training and VO2max

### F1a. Moderate continuous ("endurance") training vs no-exercise control
- **Value:** +4.9 mL·kg⁻¹·min⁻¹; 95% confidence limits ±1.4, i.e. 95% CI 3.5 to 6.3 (CI derived from the ± limits).
- **Population/design:** meta-analysis of controlled trials. 28 studies, 723 healthy adults aged 18–45 (mean age 25.1 ± 5 y, baseline VO2max 40.8 ± 7.9 mL/kg/min). "Endurance training intensity was classified as moderate-intensity (60-85% HRmax)".
- **Source:** Milanović Z, Sporiš G, Weston M. *Sports Med* 2015;45:1469–1481. DOI 10.1007/s40279-015-0365-0. PMID 26243014.
- **URLs:** Europe PMC REST abstract (PMID 26243014); accepted manuscript PDF https://research.tees.ac.uk/ws/files/6460688/561180.pdf
- **Quotes:**
  - "The meta-analysed effect of endurance training on VO2max was a possibly large beneficial effect (4.9 mL·kg(-1)·min(-1); 95 % confidence limits ±1.4 mL·kg(-1)·min(-1)), when compared with no-exercise controls."
  - Inclusion: "controlled trials, healthy adults aged 18-45 years, training duration ≥2 weeks".
  - Programme (manuscript): "Most of the studies in this particular analysis undertook three moderate-intensity sessions per week lasting 40 to 60 minutes".
  - Between-study SD (manuscript): "The random variation in the overall pooled effect from study to study, expressed as an SD, was 1.3 mL•kg-1•min-1."
- **Caveats:** Programme lengths for each study are in the published Table 1, which I could not open (Springer paywall; the accepted manuscript has no tables). I verified only the inclusion criterion (≥2 weeks) and the 3 × 40–60 min/week description. The manuscript says "the results indicated publication bias for all analyses (P < 0.10)". Results use magnitude-based inference. The cohort is young and fairly fit, not sedentary middle-aged adults.

### F1b. HIIT vs no-exercise control, and HIIT vs continuous training
- **Value:** HIIT vs control +5.5 mL/kg/min (±1.2, i.e. CI 4.3–6.7, derived). HIIT vs endurance +1.2 mL/kg/min (±0.9, i.e. CI 0.3–2.1, derived).
- **Source:** Milanović 2015, as F1a.
- **Quotes:** "When compared with no-exercise controls, there was likely a large beneficial effect of HIT (5.5 mL·kg(-1)·min(-1); ±1.2 mL·kg(-1)·min(-1))". "When compared with endurance training, there was a possibly small beneficial effect for HIT (1.2 mL·kg(-1)·min(-1); ±0.9 mL·kg(-1)·min(-1))". HIIT definition (manuscript): HIT intensity "classified as either “all-out”, “supramaximal”, “maximal” or “high (90-95% HRmax)”".

### F1c. Interval training, pre–post (Bacon 2013)
- **Value:** +0.51 L/min (95% CI 0.43–0.60). Standardised change 0.86 SD (0.72–0.99). Trim-and-fill estimate 0.37 L/min (0.28–0.46). The paper does not report mL/kg/min.
- **Population/design:** 37 studies, 40 training groups, 334 healthy sedentary or recreationally active adults under 45. Programmes ran 6–13 weeks (inclusion); "All subjects trained between 6 and 12 weeks". **Pre–post change in the training arms only; no control groups.**
- **Source:** Bacon AP, Carter RE, Ogle EA, Joyner MJ. *PLoS One* 2013;8:e73182. DOI 10.1371/journal.pone.0073182. PMID 24066036. PMCID PMC3774727.
- **URL:** https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3774727/fullTextXML
- **Quotes:** "An increase in VO2max of 0.51 L·min−1 (95% CI: 0.43 to 0.60 L·min−1) was observed." "Inclusion criteria were: 1)≥3 healthy sedentary/recreationally active humans <45 yrs old, 2) training duration 6–13 weeks, 3) ≥3 days/week..." "the estimated effect using the ‘Trim and Fill’ approach was 0.37 L·min−1 (95% CI: 0.28 to 0.46 L·min−1)".
- **Caveat:** Without a control arm this is an upper-bound estimate (I² = 70).

### F1d. Older adults (adds coverage; relevant to the LongPi age range)
- **Value:** +3.78 mL/kg/min (95% CI 3.24–4.33), a 16.3% improvement vs control.
- **Population/design:** meta-analysis of 41 controlled trials, 2102 sedentary adults with mean age ≥60.
- **Source:** Huang G, Gibson CA, Tran ZV, Osness WH. *Prev Cardiol* 2005;8:217–225. DOI 10.1111/j.0197-3118.2005.04324.x. PMID 16230876.
- **Quote:** "representing a net increase in VO2max (mean +/- SEM) of 3.78+/-0.28 mL.kg-1.min-1; 95% confidence interval, 3.24-4.33; or a 16.3% improvement, compared with control groups. Greater improvement in VO2max was associated with training length more than 20 weeks and training intensity of approximately 60% but less than 70% of VO2max."
- **Caveat:** Fixed-effect model.

### F1e. Spread of individual responses (HERITAGE)
- **Value:** mean gain 384 mL O2/min (SD 202). In completers with no missing data (n = 633), Table 6 gives ΔVO2max 389 ± 204 mL O2, or **17 ± 9%**. Individual responses ranged from no gain to more than 1 L/min.
- **Design:** single-arm standardised programme. 60 supervised cycle-ergometer sessions, 3/week for 20 weeks, starting at 55% and progressing to 75% of baseline VO2max for 50 min. Sedentary adults aged 17–65.
- **Sources:**
  - Bouchard C, An P, Rice T, et al. *J Appl Physiol* 1999;87:1003–1008. DOI 10.1152/jappl.1999.87.3.1003. PMID 10484570. Abstract quote: "The mean increase in VO(2max) reached approximately 400 ml/min, but there was considerable heterogeneity in responsiveness, with some individuals experiencing little or no gain, whereas others gained >1.0 l/min." Also: "481 sedentary adult Caucasians from 98 two-generation families was exercise trained for 20 wk" and "maximal heritability estimate of 47%".
  - Sarzynski MA, et al. *Med Sci Sports Exerc* 2022;54(5S):S1–S43 (HERITAGE review). DOI 10.1249/mss.0000000000002859. PMID 35611651. PMCID PMC9012529. URL https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9012529/fullTextXML. Quotes: "The mean gain in V̇O2max was 384 mL O2 (SD, 202)." Table 6 row "All 633 … 389 ± 204 [ΔVO2max mL O2] 17 ± 9 [ΔVO2max %]". "The training protocol required a total of 60 training sessions, three per week for 20 wk." "We estimated as discussed previously that the measurement error and the day-to-day variation in V̇O2max explained about 20% of the variability in training response." "The within-subject SD for repeated V̇O2max measures was 114 mL before training, 108 mL after training in >700 subjects".
- **Caveat that matters for modelling:** HERITAGE had no control arm. Williamson PJ, Atkinson G, Batterham AM. *Sports Med* 2017;47:1501–1513. DOI 10.1007/s40279-017-0680-8. PMID 28097487. Quote: "For those studies with a comparator sample, we found that the inter-individual differences in training response were not larger than random within-subjects variation in VO2max over the same time period as the training intervention." Their re-analysis of the one controlled pre-HERITAGE study found "The standard deviation of change was, in fact, larger (±5.6 mL/kg/min) for the comparator than the intervention group (±3.7 mL/kg/min)."
- **Derived:** if about 20% of the response variance is measurement noise, the "true" response SD is about 202 × √0.8 ≈ 180 mL/min. Treat this as an upper bound for true heterogeneity.

---

## F2. Salt reduction and blood pressure

### F2a. He, Li & MacGregor 2013 (Cochrane/BMJ)
- **Values (reduced vs usual salt):**
  - Achieved reduction: urinary sodium −75 mmol/24 h (≈4.4 g/day salt).
  - SBP overall −4.18 mmHg (−5.18 to −3.18).
  - Hypertensives −5.39 (−6.62 to −4.15).
  - Normotensives −2.42 (−3.56 to −1.29).
  - Dose–response: −5.8 mmHg SBP per 100 mmol/24 h (2.5 to 9.2).
- **Design:** 34 RCTs, 3230 participants, modest salt reduction for ≥4 weeks; random-effects model.
- **Source:** He FJ, Li J, MacGregor GA. *BMJ* 2013;346:f1325. DOI 10.1136/bmj.f1325. PMID 23558162. Companion Cochrane review: DOI 10.1002/14651858.cd004937.pub2, PMID 23633321.
- **URL:** Europe PMC REST abstract (PMID 23558162)
- **Quotes:** "the mean change in urinary sodium (reduced salt v usual salt) was -75 mmol/24 h (equivalent to a reduction of 4.4 g/day salt), and with this reduction in salt intake, the mean change in blood pressure was -4.18 mm Hg (95% confidence interval -5.18 to -3.18, I(2)=75%) for systolic blood pressure". "A 100 mmol reduction in 24 hour urinary sodium (6 g/day salt) was associated with a fall in systolic blood pressure of 5.8 mm Hg (2.5 to 9.2, P=0.001) after adjustment for age, ethnic group, and blood pressure status." "in people with hypertension the mean effect was -5.39 mm Hg (-6.62 to -4.15, I(2)=61%) for systolic blood pressure … In normotensive people, the figures were -2.42 mm Hg (-3.56 to -1.29, I(2)=66%)".

### F2b. Huang 2020 BMJ: dose and duration
- **Values:**
  - Overall: urinary sodium −130 mmol (115–145); SBP −4.26 mmHg (3.62–4.89).
  - Per 50 mmol/24 h reduction: SBP −1.10 mmHg (0.66–1.54).
  - Per 50 mmol in trials <15 days: −1.05 (0.40–1.70). In longer trials: −2.13 (0.85–3.40).
  - **Derived, assuming linearity:** per 100 mmol ≈ −2.2 mmHg overall, or ≈ −4.3 mmHg in trials longer than 14 days.
- **Design:** 133 RCTs, 12,197 adults; intake measured by 24-h urinary sodium.
- **Source:** Huang L, Trieu K, Yoshimura S, et al. *BMJ* 2020;368:m315. DOI 10.1136/bmj.m315. PMID 32094151. PMCID PMC7190039.
- **URL:** https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7190039/fullTextXML
- **Quotes:** "Each 50 mmol reduction in 24 hour sodium excretion was associated with a 1.10 mm Hg (0.66 to 1.54; P<0.001) reduction in SBP". "In trials of less than 15 days’ duration, each 50 mmol reduction in 24 hour urinary sodium excretion was associated with a 1.05 mm Hg (0.40 to 1.70; P=0.002) SBP fall, less than half the effect observed in studies of longer duration (2.13 mm Hg; 0.85 to 3.40; P=0.002)."
- **Recommendation:** use the ≥15-day slope (≈2.1 mmHg per 50 mmol). It sits close to He 2013 (5.8 per 100 mmol, adjusted).

### F2c. SSaSS salt substitute trial, rural China (Neal 2021 NEJM)
- **Values (salt substitute vs regular salt):**
  - Stroke rate ratio 0.86 (0.77–0.96).
  - Major cardiovascular events 0.87 (0.80–0.94).
  - Death from any cause 0.88 (0.82–0.95).
  - Serious hyperkalaemia 1.04 (0.80–1.37).
  - SBP difference about −3.3 mmHg, with 24-h urinary sodium −15.2 mmol and potassium +20.6 mmol.
- **Design:** open-label cluster RCT in 600 villages, 20,995 people with prior stroke or aged ≥60 with hypertension (mean age 65.4; 72.6% with prior stroke). Mean follow-up 4.74 years. Substitute was 75% NaCl / 25% KCl.
- **Sources:**
  - Neal B, Wu Y, Feng X, et al. *N Engl J Med* 2021;385:1067–1077. DOI 10.1056/NEJMoa2105675. PMID 34459569. Abstract retrieved via Europe PMC REST.
  - SBP and urine values: Huang L, et al. *J Hum Hypertens* 2024;38:298–306. DOI 10.1038/s41371-024-00896-4. PMID 38379029. PMCID PMC11001572. URL https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11001572/fullTextXML
- **Quotes:** "The rate of stroke was lower with the salt substitute than with regular salt (29.14 events vs. 33.65 events per 1000 person-years; rate ratio, 0.86; 95% confidence interval [CI], 0.77 to 0.96; P = 0.006), as were the rates of major cardiovascular events (49.09 events vs. 56.29 events per 1000 person-years; rate ratio, 0.87; 95% CI, 0.80 to 0.94; P<0.001) and death (39.28 events vs. 44.61 events per 1000 person-years; rate ratio, 0.88; 95% CI, 0.82 to 0.95; P<0.001)." (Neal 2021.) "The observed SBP reduction in SSaSS was −3.3 mmHg with a corresponding mean 15.2 mmol reduction in 24-h sodium excretion and a mean 20.6 mmol increase in 24-h potassium excretion." "In every model, the majority of the SBP lowering effect in SSaSS was estimated to be attributable to the increase in dietary potassium rather than the fall in dietary sodium." (Huang 2024.)
- **NOT VERIFIED:** the exact NEJM figure "−3.34 mmHg (95% CI −4.51 to −2.18)". The NEJM full text returned 403. News coverage gives "3.3 mm Hg" (https://blogs.the-hospitalist.org/content/ssass-salt-substitute-shows-clear-reduction-stroke-cv-events-death).
- **Caveat:** SSaSS is a salt-substitute (potassium) trial, not a pure sodium-reduction trial. Do not feed its benefit through the sodium→SBP slope alone.

### F2d. DECIDE-Salt, China elderly care facilities (added: Chinese RCT)
- **Values:**
  - Salt substitute vs usual salt: SBP −7.1 mmHg (−10.5 to −3.8); CV events HR 0.60 (0.38–0.96); total mortality HR 0.84 (0.63–1.13).
  - Progressively restricted salt supply: no effect on SBP or any other outcome.
- **Design:** 2×2 factorial cluster RCT, 48 facilities, 1612 residents aged ≥55, 2 years.
- **Source:** Yuan Y, Jin A, Neal B, et al. *Nat Med* 2023;29:973–981. DOI 10.1038/s41591-023-02286-8. PMID 37055566 (PubMed abstract via E-utilities).
- **Quote:** "Salt substitute compared with usual salt lowered systolic blood pressure (-7.1 mmHg, 95% confidence interval (CI) -10.5 to -3.8), meeting the primary outcome of the trial, whereas restricted supply compared with usual supply of salt or salt substitute had no effect on systolic blood pressure."

---

## F3. Diet and LDL-C

### F3a. Replacing saturated fat (Mensink 2016, WHO)
- **Values:** change in LDL-C per 1% of energy from SFA replaced isocalorically:
  - by cis-PUFA: −0.055 mmol/L (−0.061 to −0.050)
  - by cis-MUFA: −0.042 mmol/L (−0.047 to −0.037)
  - by carbohydrate: −0.033 mmol/L (−0.039 to −0.027)
- **Design:** regression analysis of 84 controlled dietary trials (74 for total SFA). Diets were fed for 13–91 days; 73 crossover and 11 parallel trials; 2353 volunteers; mean age 38. LDL regression: 165 diets / 69 studies.
- **Source:** Mensink RP. *Effects of saturated fatty acids on serum lipids and lipoproteins: a systematic review and regression analysis.* Geneva: World Health Organization; 2016. ISBN 978 92 4 156534 9. No PMID/DOI.
- **URL:** https://iris.who.int/bitstreams/2f760cd7-8b3e-4c10-bafc-6f94f67c5408/download (from https://iris.who.int/handle/10665/246104)
- **Quotes:** "for each 1% of dietary energy as SFA replaced with an equivalent amount of cis–PUFA, there was a significant decrease in total cholesterol of 0.064 mmol/L (95% CI: –0.070, –0.058), in LDL cholesterol of 0.055 mmol/L (95% CI: –0.061, –0.050)". For cis-MUFA: "in LDL cholesterol of 0.042 mmol/L (95% CI: –0.047, –0.037)". For carbohydrates: "in LDL cholesterol of 0.033 mmol/L (95% CI: –0.039, –0.027)". Table 2 row: "ΔLDL cholesterol mmol/L –0.033 –0.042 –0.055 165/69".
- **Caveat:** These are short-term, mostly controlled-feeding trials, so they give efficacy under full adherence. Carbohydrate replacement also lowers HDL (−0.010 mmol/L per 1% energy) and raises triglycerides (+0.011).

### F3b. Soluble fibre (Brown 1999)
- **Value:** LDL-C −0.057 mmol/L per gram of soluble fibre per day (95% CI −0.070 to −0.044), within 2–10 g/d.
- **Design:** meta-analysis of 67 controlled trials (pectin, oat bran, guar, psyllium).
- **Source:** Brown L, Rosner B, Willett WW, Sacks FM. *Am J Clin Nutr* 1999;69:30–42. DOI 10.1093/ajcn/69.1.30. PMID 9925120.
- **Quotes:** "Soluble fiber, 2-10 g/d, was associated with small but significant decreases in total cholesterol [-0.045 mmol L(-1).g soluble fiber(-1) (95% CI: -0.054, -0.035)] and LDL cholesterol [-0.057 mmol.L(-1).g(-1) (95% CI: -0.070, -0.044)]." "3 g soluble fiber from oats (3 servings of oatmeal, 28 g each) can decrease total and LDL cholesterol by approximately 0.13 mmol/L."
- **Caveat:** the authors' worked example (≈0.13 mmol/L for 3 g) is smaller than 3 × 0.057 = 0.17. Cite the slope with its CI, and do not extrapolate beyond 10 g/d.

### F3c. Portfolio diet (Chiavaroli 2018)
- **Value:** LDL-C −0.73 mmol/L (95% CI −0.89 to −0.56), about −17%, vs NCEP Step II diet alone.
- **Design:** 7 trial comparisons, 439 participants with hyperlipidaemia; controlled trials of ≥3 weeks; Portfolio given on an NCEP Step II background.
- **Source:** Chiavaroli L, Nishi SK, Khan TA, et al. *Prog Cardiovasc Dis* 2018;61:43–53. DOI 10.1016/j.pcad.2018.05.004. PMID 29807048.
- **Quote:** "The combination of a portfolio dietary pattern and NCEP Step II diet significantly reduced the primary outcome LDL-C by ~17% (MD, -0.73 mmol/L, [95% CI, -0.89 to -0.56 mmol/L])".

---

## F4. Moderate-intensity statin

### F4a. 2018 AHA/ACC definition
- **Value:** moderate intensity lowers LDL-C by **30%–49%** (high ≥50%, low <30%).
- **Source:** Grundy SM, Stone NJ, Bailey AL, et al. 2018 AHA/ACC/…/PCNA Guideline on the Management of Blood Cholesterol. *Circulation* 2019;139:e1082–e1143. DOI 10.1161/cir.0000000000000625. PMID 30586774. PMCID PMC7403606. Also published as *J Am Coll Cardiol*, DOI 10.1016/j.jacc.2018.11.003.
- **URL:** https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=7403606
- **Quotes:** "High-intensity statin therapy typically lowers LDL-C levels by ≥50%, moderate-intensity statin therapy by 30% to 49%, and low-intensity statin therapy by <30% (Table 3). Of course, the magnitude of LDL-C lowering will vary in clinical practice. Certain Asian populations may have a greater response to certain statins." Table 3, moderate intensity: "Atorvastatin 10 mg (20 mg) … Rosuvastatin (5 mg) 10 mg … Simvastatin 20–40 mg … Pravastatin 40 mg (80 mg) … Lovastatin 40 mg (80 mg) … Fluvastatin XL 80 mg … Fluvastatin 40 mg BID … Pitavastatin 1–4 mg".
- **Caveat:** a 2026 ACC/AHA multisociety *Guideline on the Management of Dyslipidemia* now exists (Blumenthal RS et al., *J Am Coll Cardiol* 2026;87:2624–2757, DOI 10.1016/j.jacc.2025.11.016, PMID 41824590). I did not read it, so **whether it changed the intensity definitions is NOT VERIFIED.**

### F4b. Chinese guideline (中国血脂管理指南 2023)
- **Value:** moderate intensity is "25%–50% reduction in LDL-C at daily dose". Regimens: atorvastatin 10–20 mg, rosuvastatin 5–10 mg, fluvastatin 80 mg, lovastatin 40 mg, pitavastatin 1–4 mg, pravastatin 40 mg, simvastatin 20–40 mg, Xuezhikang 1.2 g. The guideline recommends moderate-intensity statin as initial therapy.
- **Sources:**
  - Chinese original: Joint Committee on the Chinese Guidelines for Lipid Management. 中华心血管病杂志 (Zhonghua Xin Xue Guan Bing Za Zhi) 2023;51(3):221–255. DOI 10.3760/cma.j.cn112148-20230119-00038. PMID 36925135. Only the record was retrieved; I did not read the text.
  - Official English version, read in full: Li JJ, Zhao SP, Zhao D, Lu GP, et al. "2023 Chinese guideline for lipid management." *Front Pharmacol* 2023;14:1190934. DOI 10.3389/fphar.2023.1190934. PMID 37711173. PMCID PMC10498001. URL https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10498001/fullTextXML
- **Quotes:** "TABLE 11 Cholesterol-lowering intensity of statins … High intensity (daily dose reduces LDL-C by ≥ 50%) Atorvastatin 40–80 mg Rosuvastatin 20 mg Moderate intensity (25%–50% reduction in LDL-C at daily dose) Atorvastatin 10–20 mg Rosuvastatin 5–10 mg Fluvastatin 80 mg Lovastatin 40 mg Pitavastatin 1∼4 mg Pravastatin 40 mg Simvastatin 20–40 mg XZK 1.2 g". "These guidelines recommend that moderate intensity statin therapy in adjunct with a heart-healthy lifestyle, be used as an initial line of treatment".

### F4c. Typical absolute LDL-C reduction
- **Efficacy, placebo-controlled trials:** −1.8 mmol/L (−40%) from a pre-treatment LDL-C of 4.8 mmol/L, for atorvastatin 10, lovastatin 40, simvastatin 40 or rosuvastatin 5 mg/day (all moderate intensity). Source: Law MR, Wald NJ, Rudnicka AR. *BMJ* 2003;326:1423. DOI 10.1136/bmj.326.7404.1423. PMID 12829554. Quote: "Reductions in LDL cholesterol (in the 164 trials) were … 1.8 mmol/l (40%) with atorvastatin 10 mg/day, lovastatin 40 mg/day, simvastatin 40 mg/day, or rosuvastatin 5 mg/day, all from pretreatment concentrations of 4.8 mmol/l."
- **Intention-to-treat in outcome trials:** −1.07 mmol/L at 1 year (21 statin-vs-control trials; baseline 3.70 mmol/L). Source: Cholesterol Treatment Trialists' Collaboration. *Lancet* 2010;376:1670–1681. DOI 10.1016/s0140-6736(10)61350-5. PMID 21067804. PMCID PMC2988224. Quotes: "corresponding to a highly significant 22% (95% CI 19–24; p<0·0001) risk reduction with a 1·07 mmol/L LDL cholesterol reduction." "Baseline LDL cholesterol concentrations were substantially higher in the trials of statin versus control (3·70 mmol/L on no statin)".
- **Caveat:** the absolute reduction scales with baseline LDL-C. Model it as percentage × baseline, and use CTT's ITT figure as the real-world anchor because it already includes non-adherence and drop-in.

---

## F5. Sleep interventions: total sleep time (TST)

### F5a. Sleep extension
- **Henst 2019 (systematic review, no pooled estimate):** across 7 studies (n = 138), "all successfully increased total sleep time by between 21 and 177 min". Interventions lasted 3 days to 6 weeks. Henst RHP, Pienaar PR, Roden LC, Rae DE. *J Sleep Res* 2019;28:e12865. DOI 10.1111/jsr.12865. PMID 31166059. Quote: "The durations of the sleep extension interventions ranged from 3 days to 6 weeks, and all successfully increased total sleep time by between 21 and 177 min."
- **Al Khatib 2018 RCT:** 42 short sleepers, free-living, 4 weeks. Time in bed +55 min (37–72); sleep duration **+21 min (6–36)**. Al Khatib HK, Hall WL, Creedon A, et al. *Am J Clin Nutr* 2018;107:43–53. DOI 10.1093/ajcn/nqx030. PMID 29381788. Quote: "The sleep extension group significantly increased time in bed [0:55 hours:minutes (h:mm); 95% CI: 0:37, 1:12 h:mm], sleep period (0:47 h:mm; 95% CI: 0:29, 1:05 h:mm), and sleep duration (0:21 h:mm; 95% CI: 0:06, 0:36 h:mm) compared with the control group."
- **Tasali 2022 RCT:** 80 adults with overweight sleeping <6.5 h. Actigraphy-measured sleep **+1.2 h/night (1.0–1.4)** over a 2-week intervention. Tasali E, Wroblewski K, Kahn E, Kilkus J, Schoeller DA. *JAMA Intern Med* 2022;182:365–374. DOI 10.1001/jamainternmed.2021.8098. PMID 35129580. PMCID PMC8822469. Quote: "Sleep duration was increased by approximately 1.2 hours per night (95% CI, 1.0 to 1.4 hours; P < .001) in the sleep extension group vs the control group."
- **Baron 2019 pilot RCT:** 16 adults with prehypertension; 6 weeks; TST improved more with intervention (P = .027). **Minutes NOT VERIFIED:** they are in Table 2, which I could not read. Baron KG, et al. *J Clin Sleep Med* 2019;15:1587–1597. DOI 10.5664/jcsm.8018. PMID 31739848. Read via https://pmc.ncbi.nlm.nih.gov/articles/PMC6853389/

### F5b. CBT-I
- **Value:** TST **+7.61 min (95% CI −0.51 to 15.74)** after treatment, which is not statistically significant. Over the same period sleep-onset latency fell by 19.03 min and wake after sleep onset by 26.00 min; sleep efficiency rose by 9.91%.
- **Design:** 20 RCTs, 1162 adults with chronic insomnia (no comorbidity); face-to-face multimodal CBT-I vs inactive control; sleep diaries.
- **Source:** Trauer JM, Qian MY, Doyle JS, Rajaratnam SMW, Cunnington D. *Ann Intern Med* 2015;163:191–204. DOI 10.7326/m14-2841. PMID 26054060.
- **Quote:** "At the posttreatment time point, SOL improved by 19.03 (95% CI, 14.12 to 23.93) minutes, WASO improved by 26.00 (CI, 15.48 to 36.52) minutes, TST improved by 7.61 (CI, -0.51 to 15.74) minutes, and SE% improved by 9.91% (CI, 8.09% to 11.73%)."
- **Corroboration:** van Straten A, et al. *Sleep Med Rev* 2018. DOI 10.1016/j.smrv.2017.02.001. PMID 28392168. 87 RCTs. Quote: "The smallest effect was on total sleep time (g = 0.16)."
- **Caveat:** CBT-I mainly improves sleep continuity and efficiency, not duration. Do not model it as a TST-lengthening intervention.

---

## F6. Step-count interventions

- **Bravata 2007:** in 8 RCTs, pedometer users walked **+2491 steps/day vs control (95% CI 1098–3885)**. The 26 included studies had 2767 participants (85% women, mean age 49) and a mean intervention duration of 18 weeks. Bravata DM, Smith-Spangler C, Sundaram V, et al. *JAMA* 2007;298:2296–2304. DOI 10.1001/jama.298.19.2296. PMID 18029834. Abstract via Europe PMC REST; remainder read at https://jamanetwork.com/journals/jama/fullarticle/209526. Quotes: "In the RCTs, pedometer users significantly increased their physical activity by 2491 steps per day more than control participants (95% confidence interval [CI], 1098-3885 steps per day". "The mean intervention duration was 18 weeks." "Whether these changes are durable over the long term is undetermined."
- **Ferguson 2022 (umbrella review of 39 SRs/MAs, 163,992 participants):** activity trackers gave SMD 0.3–0.6, "equating to approximately 1800 extra steps per day, 40 min per day more walking, and reductions of approximately 1 kg in bodyweight." Ferguson T, Olds T, Curtis R, et al. *Lancet Digit Health* 2022;4:e615–e626. DOI 10.1016/s2589-7500(22)00111-x. PMID 35868813.
- **Durability:** PACE-UP (age 45–75) at 3 years, accelerometer-measured: postal +627 steps/day (198–1056); nurse-supported +670 (237–1102). Harris T, et al. *PLoS Med* 2018;15:e1002526. DOI 10.1371/journal.pmed.1002526. PMID 29522529. Quote: "PACE-UP 3-year intervention versus control comparisons were as follows: additional steps/day postal +627 (95% CI: 198-1,056), p = 0.004, nurse +670 (95% CI: 237-1,102), p = 0.002". PACE-Lift (age 60–75) at 4 years: "+407 (95% CI: -177-992), p = 0.17 steps/day".
- **Recommendation:** about 2000–2500 steps/day in the short term, decaying to about 600 steps/day over 3–4 years.

---

## F7. Intentional weight loss and all-cause mortality (RCTs)

- **Value:** RR **0.85 (95% CI 0.73–1.00)**; average weight loss **5.5 ± 4.0 kg**.
- **Design:** 15 lifestyle RCTs of ≥18 months; 17,186 adults with obesity (BMI 30–46; mean age 52); mean follow-up 27 months; 264 vs 310 deaths; I² = 0.
- **Source:** Kritchevsky SB, Beavers KM, Miller ME, et al. *PLoS One* 2015;10:e0121993. DOI 10.1371/journal.pone.0121993. PMID 25794148. PMCID PMC4368053.
- **Quotes:** "average weight loss in reported trials was 5.5±4.0 kg." "The weight loss groups experienced a 15% lower all-cause mortality risk (RR = 0.85; 95% CI: 0.73-1.00)." "Results were similar in trials with a mean age at randomization ≥55 years (RR = 0.84; 95% CI 0.71-0.99)".
- **Corroboration:** Ma C, Avenell A, Bolland M, et al. *BMJ* 2017;359:j4849. DOI 10.1136/bmj.j4849. PMID 29138133. Quote: "weight loss interventions decrease all cause mortality (34 trials, 685 events; risk ratio 0.82, 95% confidence interval 0.71 to 0.95)".

---

## F8. Smoking cessation

- **Jha 2013 (US NHIS):** quitting at 25–34, 35–44, 45–54 and 55–64 years gained about **10, 9, 6 and 4 years** of life vs continuing to smoke. Jha P, Ramasundarahettige C, Landsman V, et al. *N Engl J Med* 2013;368:341–350. DOI 10.1056/NEJMsa1211128. PMID 23343063. Abstract via Europe PMC REST; full text from the DCP-3-hosted PDF https://www.dcp-3.org/sites/default/files/resources/NEJMsa1211128.pdf.
  - Abstract: "Adults who had quit smoking at 25 to 34, 35 to 44, or 45 to 54 years of age gained about 10, 9, and 6 years of life, respectively, as compared with those who continued to smoke."
  - Full text: "Smokers who stopped smoking at 45 to 54 years of age and those who stopped at 55 to 64 years of age (median, 49 and 59 years, respectively) gained about 6 and 4 years of life, respectively."
  - Full text: "smokers who had quit by about 39 years of age still had a 20% excess risk (hazard ratio, 1.2)".
- **Doll 2004 (British doctors, 50 years):** "Cessation at age 60, 50, 40, or 30 years gained, respectively, about 3, 6, 9, or 10 years of life expectancy." Doll R, Peto R, Boreham J, Sutherland I. *BMJ* 2004;328:1519. DOI 10.1136/bmj.38142.554479.ae. PMID 15213107. PMCID PMC437139.
- **China Kadoorie Biobank (men, by choice, all-cause mortality vs never-smokers):** RR 1.21 (1.07–1.37) <5 years after quitting; 1.00 (0.90–1.11) 5–14 years; 0.98 (0.87–1.11) ≥15 years; overall 1.02 (0.95–1.10). Chen Z, Peto R, Zhou M, et al. *Lancet* 2015;386:1447–1456. DOI 10.1016/s0140-6736(15)00340-2. PMID 26466050. PMCID PMC4691901.
  - Quote: "The second (China Kadoorie Biobank [CKB] study) recruited from June 25, 2004, to July 15, 2008".
  - Quote: "Among ex-smokers who had stopped by choice, the RR for all-cause mortality was 1·02 (0·95–1·10), and it attenuated with quitting duration. For men who had stopped by choice less than 5 years, 5–14 years, and 15 or more years before baseline, the RRs were 1·21 (1·07–1·37), 1·00 (0·90–1·11), and 0·98 (0·87–1·11) (trend p=0·01)."
  - Quote: "Ex-smokers who had stopped by choice (only 3% of ever-smokers in 1991, but 9% in 2006) had little smoking-attributed risk more than 10 years after stopping."
- **Caveats:** all of these are observational. CKB counts men who quit because of illness as smokers, to avoid reverse causation. Excess risk in Chinese smokers is lower than in Western cohorts: the CKB urban male smoker RR was 1.65.

---

## F9. Adherence

### F9a. Exercise programmes
- **Home exercise for falls prevention (older adults):** pooled **full adherence 21% (95% CI 15–29%; range 0–68%)** across 23 RCTs. Simek EM, McPhate L, Haines TP. *Prev Med* 2012;55:262–275. DOI 10.1016/j.ypmed.2012.07.007. PMID 22813920. Quote: "The pooled estimate of participants who were fully adherent was 21% (95% Confidence Interval: 15%-29%, range: 0%-68%)."
- **Aerobic programmes of ≥12 weeks in chronic disease (30 RCTs, 3721 participants):** 77% of the prescription completed (68–84%); home-based 80% (65–91%) vs clinic-based 74% (65–82%). Bullard T, Ji M, An R, et al. *BMC Public Health* 2019;19:636. DOI 10.1186/s12889-019-6877-z. PMID 31126260. Quote: "The pooled adherence rates for clinic-based and home-based programs did not differ (74% [95% CI, 0.65, 0.82] and 80% [95% CI, 0.65, 0.91], respectively)."
- **Five years, largely self-directed (Generation 100, Norway, age 70–77; sessions offered twice weekly, supervised only every sixth week):** adherence, defined as ≥50% of prescribed sessions, was 50%, 49% and 47% (HIIT) and 63%, 55% and 51% (MICT) at 1, 3 and 5 years. Stensvold D, et al. *BMJ* 2020;371:m3485. DOI 10.1136/bmj.m3485. PMID 33028588. PMCID PMC7539760. Quote: "Adherence to prescribed exercise after one, three, and five years was, respectively, 201 (50%), 196 (49%), and 187 (47%) of participants in the HIIT group and 244 (63%), 213 (55%), and 197 (51%) in the MICT group."
- **Recommendation:** trial participants complete about 75–80% over 3 months. Over years, about 50% reach at least half the prescribed dose. Unsupervised home programmes reach full adherence in only about 20%.

### F9b. Dietary sodium reduction: achieved vs targeted
- **TOHP II:** target 80 mmol/day; net achieved reduction 50 mmol/day at 6 months and 40 mmol/day at 36 months. Trials of Hypertension Prevention Collaborative Research Group. *Arch Intern Med* 1997;157:657–667. DOI 10.1001/archinte.157.6.657. PMID 9080920. Quote: "sodium intake of 80 mmol/d … Sodium excretion decreased 50 and 40 mmol/d at 6 and 36 months, respectively, in the sodium reduction group".
- **Long-term advice trials (Hooper 2002):** urinary sodium −35.5 mmol/24 h (23.9–47.2) at 13–60 months, with SBP −1.1 mmHg. Hooper L, Bartlett C, Davey Smith G, Ebrahim S. *BMJ* 2002;325:628. DOI 10.1136/bmj.325.7365.628. PMID 12242173. Quote: "Systolic and diastolic blood pressures were reduced (systolic by 1.1 mm Hg, 95% confidence interval 1.8 to 0.4 mm Hg …) at 13 to 60 months, as was urinary 24 hour sodium excretion (by 35.5 mmol/24 hours, 47.2 to 23.9)." It also notes: "Intensive interventions, unsuited to primary care or population prevention programmes".
- **China:**
  - **CRHI-SRS:** 120 villages, 18 months, salt substitute plus education. Urinary sodium −14 mmol/day (−26 to −1), i.e. −5.5%. Li N, et al. *PLoS One* 2016;11:e0166620. DOI 10.1371/journal.pone.0166620. PMID 27935977.
  - **School-EduSalt:** 3.5 months; adult family members −2.9 g/day salt (−3.7 to −2.2). He FJ, et al. *BMJ* 2015;350:h770. DOI 10.1136/bmj.h770. PMID 25788018.
  - **AppSalt:** 12 months; adults −0.82 g/day (−1.24 to −0.40). He FJ, et al. *BMJ* 2022;376:e066982. DOI 10.1136/bmj-2021-066982. PMID 35140061.
  - **DECIDE-Salt:** restricting salt supply had no effect (F2d).
- **Recommendation:** advice alone achieves about 35–50 mmol/day (≈2–3 g salt) sustained, roughly 40–50% of a typical target. Community and app programmes in China achieve about 1–3 g/day.

### F9c. Statin adherence in China
- **Claims data, Tianjin, 109,306 new users in 2012–13:** mean 12-month PDC **0.20 (SD 0.16)**; only **0.8%** had PDC ≥0.8 and about 5.4% PDC ≥0.5. Zhao B, He X, Wu J, Yan S. *BMC Cardiovasc Disord* 2020;20:282. DOI 10.1186/s12872-020-01566-2. PMID 32522146. PMCID PMC7288497. Quote: "For 109,306 identified new stain users, the mean (SD) PDC was 0.20 (0.16) during the initial 12-month follow-up period, and 0.8% patients had PDC ≥ 0.8".
- **ACS registry (CPACS-2, 75 hospitals, 10,337 patients):** 1-year statin discontinuation fell from **29.5% (2007–08) to 17.8% (2010)**. Xie G, et al. *BMJ Open* 2022;12:e056236. DOI 10.1136/bmjopen-2021-056236. PMID 36104136. Quote: "The 1-year statin discontinuation rate decreased from 29.5% in 2007-2008 to 17.8% in 2010 (adjusted OR=0.60; 95% CI: 0.51 to 0.70)." Companion 6-month figure: "Seventy two percent of patients adhered to statin therapy at 6 months." (Xie G, et al. *Lipids Health Dis* 2017;16:155. DOI 10.1186/s12944-017-0544-0. PMID 28810873.)
- **China PEACE prospective AMI study (4001 patients, 53 hospitals):** good adherence, defined as taking medication ≥90% of the time across five secondary-prevention drug classes, was **52.9%** at 1 year. Statins were the second most-used class at 80.5%. Shang P, et al. *J Am Heart Assoc* 2019;8:e011793. DOI 10.1161/jaha.118.011793. PMID 31057004. Quote: "The overall rate of good adherence was 52.9%." This is a composite and not statin-specific.
- **International anchor:** refill-based adherence was 57% (50–64) after a median of 24 months: primary prevention 50%, secondary 66%. Naderi SH, Bestwick JP, Wald DS. *Am J Med* 2012;125:882–887.e1. DOI 10.1016/j.amjmed.2011.12.013. PMID 22748400.
- **Caveat:** these definitions differ (PDC vs self-report vs "still taking"). Claims PDC in China may undercount purchases outside insurance. Report the range: about 50–80% still taking at 1 year after ACS, but far lower refill-based adherence in primary care.

---

## F10. Resistance training and strength; muscle-strengthening activity and mortality

- **Handgrip in sarcopenia (network meta-analysis of 42 RCTs, 3728 participants; 27 trials reported grip):** resistance exercise alone vs usual care **+2.69 kg (1.78–3.61)**, moderate certainty; resistance plus nutrition +3.93 kg (2.22–5.65). Median follow-up 12 weeks. Shen Y, Shi Q, Nong K, et al. *J Cachexia Sarcopenia Muscle* 2023;14:1199–1211. DOI 10.1002/jcsm.13225. PMID 37057640. PMCID PMC10235889. Quote: "Moderate certainty evidence showed that resistance exercise alone (MD: 2.69 kg, 95% CI: 1.78 to 3.61) and the combination of resistance and aerobic exercise with nutrition (MD: 3.02 kg, 95% CI: 1.64 to 4.4) are the most effective interventions for improving handgrip strength."
- **Healthy community-dwelling adults aged ≥60 (24 trials, 3018 participants; mixed training types):** handgrip SMD **0.28 (0.13–0.44)**. Labott BK, et al. *Gerontology* 2019;65:686–698. DOI 10.1159/000501203. PMID 31499496. Quote: "Small but significant effects (p < 0.001) on handgrip strength were observed (SMD 0.28, 95% CI 0.13-0.44)."
- **Trained-muscle strength:** progressive resistance training improved strength with SMD **0.84 (0.67–1.00)** (73 trials, 3059 participants); Liu CJ, Latham NK. *Cochrane Database Syst Rev* 2009;CD002759. DOI 10.1002/14651858.cd002759.pub2. PMID 19588334. Percentage gains were 24–33% across leg press, chest press, knee extension and lat pull; Peterson MD, Rhea MR, Sen A, Gordon PM. *Ageing Res Rev* 2010;9:226–237. DOI 10.1016/j.arr.2010.03.004. PMID 20385254. Quote: "percent changes were 29+/-2, 24+/-2, 33+/-3, and 25+/-2, respectively for leg press, chest press, knee extension, and lat pull."
- **Muscle-strengthening activity and mortality (Momma 2022, prospective cohorts):**
  - Any vs none: all-cause mortality RR **0.85 (0.79–0.93)**; I² = 83%; GRADE "very low".
  - Non-linear: lowest RR **0.83 (0.79–0.86) at 40 min/week**; RR stays <1.00 up to about 140 min/week.
  - Combined with aerobic activity vs neither: RR 0.60 (0.54–0.67).
  - Source: Momma H, Kawakami R, Honda T, Sawada SS. *Br J Sports Med* 2022;56:755–763. DOI 10.1136/bjsports-2021-105061. PMID 35228201. PMCID PMC9209691.
  - Quote: "Muscle-strengthening activities were associated with a 15% lower risk of all-cause mortality (RR 0.85; 95% CI 0.79 to 0.93; p<0.001)". "The lowest RR (RR 0.83; 95% CI 0.79 to 0.86) was observed at 40 min/week of muscle-strengthening activities, and the RR estimate for up to approximately 140 min/week was <1.00." "J-shaped associations with the maximum risk reduction (approximately 10–20%) at approximately 30–60 min/week".
- **Caveat:** grip is a poor transfer marker; whole-body strength gains are much larger than grip gains. The Momma estimates are observational and self-reported.

---

## F11. NMN in humans

| Trial | n / population | Dose, duration | Outcomes | Key result (verbatim) |
|---|---|---|---|---|
| Yoshino M, et al. *Science* 2021;372:1224–1229. DOI 10.1126/science.abe9985. PMID 33888596. PMCID PMC8550608 | 25 postmenopausal women with prediabetes and overweight/obesity (13 NMN, 12 placebo) | 250 mg/d, 10 weeks | Clamp insulin sensitivity, muscle insulin signalling, PBMC/muscle NAD+, body composition | "Muscle insulin sensitivity … was 25±7% greater after than before 10 weeks of NMN supplementation". "The absence of changes in steady-state levels of muscle NAD+ in our NMN-treated participants". Body composition, BP, glucose and lipids "did not change in either g[roup]". |
| Igarashi M, et al. *NPJ Aging* 2022;8:5. DOI 10.1038/s41514-022-00084-z. PMID 35927255. PMCID PMC9158788 | 42 healthy older men (21/21) | 250 mg/d, 6 or 12 weeks | Blood NAD+ metabolome, gait speed, grip, body composition | "There were nominally significant improvements in gait speed and performance in the left grip test, which should be validated in larger studies; however, NMN exerted no significant effect on body composition." |
| Yi L, et al. *GeroScience* 2023;45:29–43. DOI 10.1007/s11357-022-00705-1. PMID 36482258. PMCID PMC9735188 | 80 healthy middle-aged adults | Placebo vs 300, 600 or 900 mg/d, 60 days | Blood NAD, 6-minute walk, "blood biological age (Aging.Ai 3.0)", HOMA-IR, SF-36 | "Walking distance increase during the six-minute walking test was statistically significantly higher in the 300 mg, 600 mg, and 900 mg groups compared to placebo". "The HOMA-IR showed no statistically significant differences". |

- **Meta-analyses:**
  - Chen F, et al. *Curr Diab Rep* 2024. DOI 10.1007/s11892-024-01557-z. PMID 39531138. 8 RCTs, 342 adults, 14 days–12 weeks: "no significant benefit of NMN on fasting glucose, fasting insulin, glycated hemoglobin, homeostatic model assessment for insulin resistance and lipid profile."
  - Yang W, et al. *Nutrients* 2026;18:2251. DOI 10.3390/nu18142251. PMID 42514320. 15 RCTs, 14 days–24 weeks: safety and metabolic outcomes only; "Broad metabolic benefits were not evident".
- **Mortality and ageing outcomes:** none of the retrieved trials or meta-analyses reports mortality; the longest trial lasted 24 weeks. A Europe PMC search for NMN RCTs with mortality outcomes found none. The only "ageing" endpoint, Yi 2023's Aging.Ai 3.0 blood-age calculator, is not a validated surrogate for intervention effects. That trial was industry-affiliated: "LY is an employee of Abinopharm, Inc., RT and ZL are employees of Aba Chemicals, Co." Yoshino's authors disclose NMN patents and licensing fees.
- **Recommendation:** NMN should have no marker-to-mortality pathway in the model. At most, show it as "evidence limited to NAD+ levels and short-term surrogates".
