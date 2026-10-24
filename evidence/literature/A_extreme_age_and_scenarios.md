# Topic A: extreme-age mortality, frailty models, mortality improvement and scenarios

Verification log for the LongPi methods paper. Retrieved 2026-10-24.

## How to read this file

- **Verbatim quotes** were copied from text extracted from the full text (PMC/Europe PMC XML, publisher HTML or PDF). For abstracts, the text came from PubMed or Europe PMC. Only two kinds of edits were made:
  - PDF line-break hyphenation was removed.
  - For Oeppen & Vaupel 2002, margin line numbers that the PDF layout interleaves were removed.
- **"Derived"** marks an interval or rate I computed from numbers the source reports, such as a Wald 95% CI = estimate ± 1.96·SE. These intervals are not printed in the source.
- **Identifiers.** PMIDs and DOIs were all checked against PubMed efetch or Crossref records retrieved in this session. "No PMID" means PubMed returned no record for that work.
- **Hazard vs probability.**
  - A hazard (force of mortality) μ is a rate per year.
  - The annual probability of death is q = 1 − exp(−μ) when the hazard is constant within the year.
  - Remaining life expectancy under a constant hazard is 1/μ.

## Summary table

| id | claim | value (95% CI) | source | verified |
|---|---|---|---|---|
| A1a | Hazard plateau after 105, Italy | a = 0.645/yr (derived CI 0.614–0.676); q = 0.475 | Barbi 2018 Science | yes |
| A1b | Hazard after 110, IDL 2010 | λ ≈ 0.7/yr, q = 0.5, e110 ≈ 1.4 y; no numeric CI | Gampe 2010 | yes |
| A1c | Hazard after 110, updated IDL | US 0.7238 (SE 0.0343); Europe 0.7953 (SE 0.0365); Japan 0.5891 (SE 0.0481) | Gampe 2021 | yes |
| A1d | Pooled IDL exponential λ | 0.733 (derived 0.685–0.781) | Pearce & Raftery 2021 | yes |
| A1e | Country-specific hazards at 105+ | France women at 105: 0.64 (0.62–0.67), rising to ≈0.8 at 110 | Alvarez 2021 PLOS ONE | yes |
| A1f | Controversy | Plateaus attributed to data errors (Newman 2018); deaths accelerating after 113 (Gavrilova 2020); rebuttals | see A1 | yes |
| A2a | Gamma frailty origin | Demography 16(3):439–454 | Vaupel, Manton, Stallard 1979 | yes |
| A2b | Gamma-Gompertz hazard and plateau b/γ | eq. (40); μ̄* = b/γ | Vaupel & Missov 2014 | yes |
| A3a | Old-age improvement, 27 countries | ages 80–99: 1–2%/yr (F), 0.5–1.5%/yr (M) since the 1960s; 2.5% (F80s), 1.7% (M80s) 1982-86→1987-91 | Kannisto 1994 PDR | yes |
| A3b | Continued improvement | 80→90 survival: 12%→26% (M), 16%→38% (F), 1950–2002; US stagnation since 1980 | Rau 2008 PDR | yes (abstract) |
| A3c | Improvement rates by decade, 19 countries | 1980s→1990s: F80–89 2.45%/yr, M80–89 1.88%/yr, F90–99 1.28%/yr, M90–99 0.71%/yr | Rau et al. MPIDR WP 2006-033, precursor of Rau 2008 | yes (working paper) |
| A3d | Record life expectancy trend | +0.243 y/y for women (r² = 0.992); +0.222 y/y for men (r² = 0.980), 1840–2000 | Oeppen & Vaupel 2002 Science | yes |
| A3e | Best-practice life expectancy | ≈2.5 y per decade; Swedish women q85 17%→7%, 1950–2018 | Vaupel 2021 PNAS | yes |
| A4a | Delayed-aging scenario | intrinsic-mortality slope −20% by 2050; LE at 51 +2.2 y (35.8→38.0); $7.1T | Goldman 2013 Health Aff | yes |
| A4b | Slowing aging, the "Peter Pan" case | age multiplied by δ < 1; Gompertz baseline β = 0.0966; +1 y LE = US$38T, +10 y = US$367T | Scott 2021 Nat Aging | yes |
| A5 | Probability of record ages by 2100 | P(>122) > 99%; P(126) = 89%; P(128) = 44%; P(130) = 13%; P(135) ≈ 0.4% | Pearce & Raftery 2021 | yes |
| A6a | Life expectancy declines 2014–15 | 12/18 countries (F), 11/18 (M); mean −0.21 y (F), −0.18 y (M); UK and US stagnating | Ho & Hendi 2018 BMJ | yes |
| A6b | England & Wales slowdown | mean annual LE gain 2011–16: 0.07 (M), 0.02 (F), vs 0.33/0.25 in 2006–11; 22-country median 0.18/0.13 | Leon 2019 **Lancet Public Health** (not BMJ) | yes |
| A6c | Deceleration since 1990 | survival to 100 unlikely to exceed 15% (F), 5% (M) | Olshansky 2024 Nat Aging | yes (abstract) |
| A7 | Gompertz slope / doubling time | MRDT ≈ 8 y (b ≈ 0.087); 3100 d (b ≈ 0.082); b = 0.103 (ages 65–80, Italy); β = 0.0966 (US 2018 calibration) | Kirkwood 2015; Barbi 2018; Scott 2021 | yes |
| A8a | RAP definition | "time periods by which the risk or rate of disease is advanced among exposed subjects…" | Brenner 1993 (abstract) | yes |
| A8b | RAP formula | RAP = log HR_exposure / log HR_age (per year) | Ordóñez-Mena 2016; Mons 2015 (Brenner senior author); Lees 2021 | yes (secondary sources); formula in Brenner/Discacciati full text **not verified** (paywalled) |
| A9 | PhenoAge age conversion | "the age within the general population that corresponds with that person's mortality risk" | Liu 2018 PLoS Med; Levine 2018 Suppl. 1 | yes |

---

## A1. Hazard of death at ages 105+ and 110+ (the "mortality plateau")

### A1a. Barbi et al. 2018, Science: Italy, ages 105+

- **Value.** The plateau hazard for the baseline cohort (born 1904, women; the male indicator is 0 at baseline) is **a = 0.645 per year (SE 0.016)**.
  - 95% CI **0.614–0.676** (derived: Wald, a ± 1.96·SE).
  - Annual probability of death **0.475** (derived CI 0.459–0.492).
  - Expectation of further life **1.55 y**.
- **Other parameters.** All are from Table 2 of the constant-hazard model.
  - **Slope above 105:** b = 0.013 (SE 0.017) in the alternative Gompertz model, derived 95% CI −0.020 to 0.046. This is not significant, and the likelihood-ratio test p = 0.44.
  - **Cohort effect:** β1 = −0.020 (SE 0.008) per birth year, about 2% lower hazard per later cohort.
  - **Male effect:** β2 = 0.033 (SE 0.058), i.e. HR 1.034 (derived 95% CI 0.922–1.158). Not significant.
- **Population and design.**
  - All Italian residents aged ≥105 between 1 Jan 2009 and 31 Dec 2015, born 1896–1910: n = 3836 (463 men), 2883 deaths.
  - Data were validated by ISTAT (birth and death certificates).
  - Analysis: maximum likelihood for left-truncated and right-censored individual trajectories. The hazard is a·exp(bx)·exp(β1C + β2M).
- **Source.** Barbi E, Lagona F, Marsili M, Vaupel JW, Wachter KW.
  - "The plateau of human mortality: Demography of longevity pioneers." *Science* 2018;360(6396):1459–1461.
  - DOI 10.1126/science.aat3119; PMID 29954979; PMCID PMC6457902 (NIH author manuscript).
- **Retrieved.**
  - Full text (author manuscript): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=6457902&rettype=xml (canonical: https://pmc.ncbi.nlm.nih.gov/articles/PMC6457902/).
  - Abstract: Europe PMC record MED/29954979.
- **Quotes.**
  - "For the baseline cohort born in 1904, the estimated level of the plateau is a = 0.645. It corresponds to an annual probability of dying of 1 — exp(−0.645) = 0.475, and an expectation of further life of 1/0.645 = 1.55 years."
  - "A likelihood ratio test fails to reject the constant-hazard null model at a level as generous as 0.44. Under the alternative hypothesis, the Gompertz slope parameter estimate b = 0.013 with standard error 0.017, is not statistically significant at the 5% level and is practically indistinguishable from zero."
  - "The estimated cohort effect β1 = −0.020 with standard error 0.008, though small, is in line with expectations, statistically significant, and important (13). The 463 male survivors beyond 105 are too few for the gender effect to come out statistically significant, though the estimate β2 = 0.033 is plausible."
  - Table 2, constant-hazard model: "a 0.645 (0.016) … β1 −0.020 (0.008) … β2 0.033 (0.058)". Gompertz model: "a 0.629 (0.026) … b 0.013 (0.017)".
- **Caveats.**
  - The numbers come from the NIH author manuscript. I could not open the Science publisher page (Cloudflare human-verification) to check the typeset version.
  - The paper reports SEs, not CIs.
  - "90% of person-years at risk coming before age 108" (same paper), so precision falls quickly above about 108.

### A1b. Gampe 2010: supercentenarians (110+), International Database on Longevity (IDL)

- **Value.**
  - **Hazard λ ≈ 0.7 per year**, i.e. q = 0.5.
  - Life expectancy at 110 ≈ **1.4 y**.
  - **No numeric CI is reported.** Uncertainty is shown only graphically: hazard over quarter-year intervals, Figs. 2–4.
  - No sex difference and no cohort trend were detected.
- **Population and design.**
  - 637 validated cases (573 women, 64 men) from 11 countries/regions in the IDL as of 31 Oct 2008, validation level A only. USA n = 341.
  - Flexible piecewise-constant model fitted by EM, with country-specific truncation and censoring.
- **Source.** Gampe J. "Human mortality beyond age 110."
  - In: Maier H, Gampe J, Jeune B, Robine J-M, Vaupel JW (eds). *Supercentenarians*. Demographic Research Monographs 7. Springer, Berlin/Heidelberg, 2010, pp. 219–230.
  - DOI 10.1007/978-3-642-11520-2_13 (printed on the chapter). No PMID.
- **Retrieved.** https://www.demogr.mpg.de/books/drm/007/3-1.pdf (MPIDR-hosted chapter PDF, 12 pp.).
- **Quotes.**
  - Abstract: "The analysis confirms that human mortality after age 110 is flat at a level corresponding to an annual probability of death of 50%. No sex-specific differences in mortality could be found, and no time trend in supercentenarian mortality between earlier and later cohorts could be detected."
  - Conclusions: "Human mortality after age 110 is flat at a constant level of λ ≈ 0.7. This implies an annual probability of death of qx = 0.5. This result confirms the previous analysis by Robine et al. (2005). Correspondingly, life expectancy after age 110 is about 1.4 years. Beyond the age of 114, data become too sparse to allow us to make reliable statements."
  - "No sex-specific differences can be detected. However, we have to be aware that only a small portion, about 10%, of supercentenarians are males, making the sample size for comparisons highly unbalanced."
- **Caveats.**
  - "λ ≈ 0.7" is −ln 0.5 = 0.693, the reference level from Robine et al. 2005, against which the flexible estimates are compared. It is not a separately fitted MLE with an SE.

### A1c. Gampe 2021: updated IDL, 110+

- **Values.** These are exponential (constant-hazard) MLEs from Table 3.2. Wald CIs and q values are derived from the reported SEs.

| Sample | λ̂ (SE) | derived 95% CI | q (reported or derived) |
|---|---|---|---|
| USA (n = 486) | 0.7238 (0.0343) | 0.657–0.791 | 0.5151 (reported) |
| Europe (n = 573) | 0.7953 (0.0365) | 0.724–0.867 | 0.5486 (reported) |
| Japan (n = 160) | 0.5891 (0.0481) | 0.495–0.683 | 0.4452 (reported) |
| Europe men | 0.8617 (0.1387) | 0.590–1.134 | 0.578 (derived) |
| Europe women | 0.7898 (0.0379) | 0.716–0.864 | 0.546 (derived) |
| US men | 0.6537 (0.1049) | 0.448–0.859 | 0.480 (derived) |
| US women | 0.7313 (0.0362) | 0.660–0.802 | 0.519 (derived) |
| Europe early / late cohorts | 0.7629 (0.0448) / 0.8520 (0.0619) | — | — |
| US early / late cohorts | 0.7609 (0.0480) / 0.6805 (0.0495) | — | — |

- **Population and design.**
  - N = 1219 validated supercentenarians: USA 486 (442 women, 44 men), Europe 573 (531 women, 42 men), Japan 160 (139 women, 21 men).
  - Methods: an EM-fitted flexible model, plus an exponential model fitted by maximum likelihood. Truncation and censoring are handled. Standard errors come from the observed information matrix; the delta method is used for derived quantities.
- **Source.** Gampe J. "Mortality of Supercentenarians: Estimates from the Updated IDL."
  - In: Maier H, Jeune B, Vaupel JW (eds). *Exceptional Lifespans*. Demographic Research Monographs. Springer, Cham, 2021 (first online 10 Dec 2020), pp. 29–35.
  - DOI 10.1007/978-3-030-49970-9_3. Open access. No PMID.
- **Retrieved.**
  - https://link.springer.com/chapter/10.1007/978-3-030-49970-9_3, via browser.
  - Tables: …/tables/1 and …/tables/2.
- **Quotes.**
  - Abstract: "Mortality after age 110 has been estimated to be flat at a level corresponding to an annual probability of death of 50% (Gampe, Supercentenarians. Springer, Berlin, 2010). Since the publication of these results, the IDL has been substantially updated, and the number of supercentenarians in the database has roughly doubled. Here we report the results obtained from the updated database (N = 1219 supercentenarians). The broad conclusions regarding human mortality at the highest ages still hold."
  - "The estimated value λˆ = 0.7238 (s.e. 0.0343) corresponds to an annual probability of death qˆ = 0.5151."
  - "…the estimated hazard parameter is λˆ = 0.7953 (s.e. 0.0365). The estimated parameter is slightly higher, but is comparable to the estimate from the U.S. The corresponding estimated annual probability of death is qˆ = 0.5486."
  - "…if we estimate an exponential distribution, the estimated hazard is λˆ = 0.5891 (s.e. 0.0481), which implies an annual probability of death qˆ = 0.4452."
  - "Although the point estimates are different, the uncertainty in the estimates (due to low numbers of male supercentenarians) does not allow us to reject the hypothesis that men and women have the same level of mortality"
- **Caveats.**
  - The US data stop at a maximum observed age of 119.
  - For Europe, "The largest observation in the European data is for Jeanne Calment (at age 122)". Right-truncation inflates uncertainty at 113+.
  - Japan "do[es] not align as closely" with the exponential model.

### A1d. Pooled IDL estimate used for forecasting (Pearce & Raftery 2021)

- **Value.** λ̂ ~ Normal(μ = 0.733, σ² = 0.0006): SD 0.0245, derived 95% interval **0.685–0.781**, derived q ≈ 0.52.
  - The Bayesian posterior is "nearly identical".
  - Data: 13 IDL countries; the exponential model of Rootzén & Zholud (2017).
- **Quote.** "We note that the distribution of λˆ from a frequentist analysis (as described in Section 2.2) would be λˆ~Normal(μ=0.733,σ2=0.0006). This distribution is also plotted in Figure A-2 and is nearly identical to the estimated posterior from our Bayesian analysis." The inline formula was re-typed from MathML.
- The full source record is under A5.

### A1e. Alvarez et al. 2021, PLOS ONE: country-specific hazards above 105

- **Value.**
  - **France, women, age 105: hazard 0.64 (95% empirical CI 0.62–0.67)**, slowly increasing toward about **0.8 at age 110**.
  - Other female populations: 0.6–0.7 at 105, approaching about 0.8.
  - US 110+: 0.6–0.8.
- **Population and design.**
  - IDL, more than 13,000 validated records of people aged 105+ from 8 populations: France, Germany, Belgium, USA (110+ only), Denmark, Quebec, Austria, Norway. France n = 9853 (8990 women).
  - Non-parametric central death rates in 6-month intervals. CIs from 10,000 simulations.
- **Source.** Alvarez JA, Villavicencio F, Strozza C, Camarda CG.
  - "Regularities in human mortality after age 105." *PLoS One* 2021;16(7):e0253940.
  - DOI 10.1371/journal.pone.0253940; PMID 34260647; PMCID PMC8279393.
- **Retrieved.** https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8279393/fullTextXML
- **Quotes.**
  - "In France, the risk of dying is 0.64 (95% CI 0.62–0.67) at age 105, and slowly increases toward values of about 0.8 at age 110."
  - "A similar pattern to that found in France is replicated for the other female populations: the risk of death ranges between 0.6 and 0.7 at age 105 and goes up slightly, approaching values of around 0.8."
  - Abstract: "We show that, in all of them, similar mortality trajectories arise, suggesting that the risk of dying levels off after age 105."
  - Methods: "Then we computed δMx = δEx/δNx, i.e. the corresponding central death rate within each interval. By taking a small δ, δMx provides a quasi-continuous estimate of the risk of dying μ(x)." In this paper, "risk of dying" therefore means the hazard.
- **Caveats.**
  - Males could be estimated only for France.
  - Above 113 there are too few people for reliable estimates.
  - The slight upward drift from about 0.64 to 0.8 between 105 and 110 means the hazard is "levelling off", not strictly flat.

### A1f. The controversy (state it explicitly in the paper)

- **Newman SJ. "Errors as a primary cause of late-life mortality deceleration and plateaus."**
  - *PLoS Biol* 2018;16(12):e2006776. DOI 10.1371/journal.pbio.2006776; PMID 30571676; PMCID PMC6301557.
  - Abstract: "Age estimation and cohort blending errors introduced at rates below 1 in 10,000 are sufficient to cause LLMD and plateaus. … Correction for these sources of demographic error using a mixed linear model eliminates LLMD and late-life mortality plateaus (LLMPs) without recourse to biological or evolutionary models. These results suggest models developed to explain LLMD have been fitted to an error distribution, that ageing does not slow or stop during old age in humans, and that there is a finite limit to human longevity."
- **Newman SJ. "Plane inclinations: A critique of hypothesis and model choice in Barbi et al."**
  - *PLoS Biol* 2018;16(12):e3000048. DOI 10.1371/journal.pbio.3000048; PMID 30571678.
  - Abstract: "This study highlights how the mortality plateau in Barbi and colleagues can be generated by low-frequency, randomly distributed age-misreporting errors."
- **Wachter KW. "Hypothetical errors and plateaus: A response to Newman."**
  - *PLoS Biol* 2018;16(12):e3000076. DOI 10.1371/journal.pbio.3000076; PMID 30571682.
  - Abstract: "His model implies implausibly high error rates for extreme ages. For individuals over 110, for whom birth certificates have been collected, the form in which Italian births were registered precludes the kinds of clerical errors in year of birth that Newman assumes."
- **Beltrán-Sánchez H, Austad SN, Finch CE. Comment.**
  - *Science* 2018;361(6409):eaav1200. DOI 10.1126/science.aav1200; PMID 30262471.
  - Abstract: "We show, using their data, that potential lifespans cannot increase much beyond the current 122 years unless future biomedical advances alter the intrinsic rate of human aging."
  - **Response:** Barbi E et al., *Science* 2018;362(6412):eaav3229, DOI 10.1126/science.aav3229, PMID 30337380: "With realistic numbers of people attaining age 105 and the estimated plateau, the Jeanne Calment record is indeed plausible."
- **Gavrilova NS, Gavrilov LA. "Are We Approaching a Biological Limit to Human Longevity?"**
  - *J Gerontol A Biol Sci Med Sci* 2020;75(6):1061–1067. DOI 10.1093/gerona/glz164; PMID 31276575.
  - Abstract: "We also found an exponential acceleration of age-specific death rates for persons older than 113 years in more recent data."
- Retrieved: Europe PMC REST records (abstracts) for all of the above.

---

## A2. The gamma-Gompertz frailty model

### A2a. Vaupel, Manton & Stallard 1979

- **Source.** Vaupel JW, Manton KG, Stallard E.
  - "The impact of heterogeneity in individual frailty on the dynamics of mortality." *Demography* 1979;16(3):439–454.
  - DOI 10.2307/2061224 (Crossref); PMID 510638.
- **Retrieved.**
  - https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=510638
  - https://api.crossref.org/works?query.bibliographic=… (returned DOI 10.2307/2061224, vol 16, issue 3, pp. 439–454, Aug 1979)
- **Quote (abstract).** "Life table methods are developed for populations whose members differ in their endowment for longevity. … The results imply that standard methods overestimate current life expectancy and potential gains in life expectancy from health and safety interventions, while underestimating rates of individual aging, past progress in reducing mortality, and mortality differentials between pairs of populations."
- **Caveat.** Full text not opened (JSTOR). The gamma-Gompertz formulas are attributed to this paper by Vaupel & Missov 2014 (A2b).

### A2b. Vaupel & Missov 2014: formal statement of the gamma-Gompertz (ΓG) hazard and its plateau

- **Statement.** Relative-risk model with fixed frailty Z ~ Γ(k, λ), mean 1, so k = λ = 1/γ, where γ is the squared coefficient of variation, i.e. the variance of frailty, the user's "s2". The baseline is Gompertz, μ(x) = a·e^{bx}.
  - Population hazard, eq. (40): **μ̄(x) = a e^{bx} / [1 + (aγ/b)(e^{bx} − 1)]**.
  - Plateau: **μ̄\* = lim_{x→∞} μ̄(x) = b/γ**.
  - μ̄(0) = a.
  - This matches the LongPi form exactly, with s2 ≡ γ.
- **Source.** Vaupel JW, Missov TI.
  - "Unobserved population heterogeneity: A review of formal relationships." *Demographic Research* 2014;31(22):659–686 (Crossref; the re-generated PDF prints 659–688).
  - DOI 10.4054/DemRes.2014.31.22 (journal landing page and Crossref). No PMID.
  - Note: the PDF header misprints the DOI as "10.4054/DemRes.2018.31.22". Cite the 2014 form.
- **Retrieved.**
  - https://www.demographic-research.org/volumes/vol31/22/31-22.pdf
  - https://www.demographic-research.org/articles/volume/31/22
- **Quotes.**
  - "A mean of one implies k = λ = 1/γ, where γ can be interpreted as the squared coefficient of variation of Z at any age x."
  - "In a ΓG model with k = λ = 1/γ the following relationships hold: 6A. The population hazard can be represented in several equivalent forms: 1. in terms of the ΓG parameters only (Vaupel, Manton, and Stallard 1979; Missov et al. 2014) µ̄(x) = ae^{bx} / (1 + (aγ/b)(e^{bx} − 1)) = be^{b(x−M)} / (1 + γe^{−bM}(e^{bx} − 1)). (40)" The fractions were re-linearised from the typeset equation.
  - "…where µ̄\* = lim_{x→∞} µ̄(x) = b/γ denotes the plateau and µ̄0 = µ̄(0) = a is the mortality level at the starting age."
  - "In both the gamma-Gompertz (ΓG) and the gamma-Gompertz-Makeham (ΓGM) model settings, the force of mortality for the population eventually levels off."
  - Survivorship, eq. (47): s̄(x) = [1 + (aγ/b)(e^{bx} − 1)]^{−1/γ}.
- **Derived arithmetic, not a literature value.** If b = 0.09–0.10/yr and the plateau is 0.70–0.72/yr (A1), then γ = b/μ̄\* ≈ 0.125–0.14.

---

## A3. Rates of mortality improvement at older ages in high-income countries

### A3a. Kannisto et al. 1994

- **Values.**
  - Ages 80–99, most developed countries outside Eastern Europe, since the 1960s: **1–2% per year for women, 0.5–1.5% per year for men**.
  - Nine-country aggregate, 1982-86 → 1987-91: **2.5%/yr for female octogenarians, 1.7%/yr for male octogenarians**.
- **Source.** Kannisto V, Lauritsen J, Thatcher AR, Vaupel JW.
  - "Reductions in Mortality at Advanced Ages: Several Decades of Evidence from 27 Countries." *Population and Development Review* 1994;20(4):793–810.
  - DOI 10.2307/2137662. No PMID (PubMed returned no record).
- **Retrieved.** https://www.jstor.org/stable/2137662 (abstract, via browser).
- **Quote (abstract).** "In most developed countries outside Eastern Europe, average death rates at ages 80-99 have declined at a rate of 1 to 2 percent per year for females and 0.5 to 1.5 percent per year for males since the 1960s. For an aggregate of nine countries with reliable data through 1991, the annual average rate of improvement between 1982-86 and 1987-91 was 1.7 percent for male octogenarians and 2.5 percent for female octogenarians."

### A3b. Rau et al. 2008 (published article)

- **Values.**
  - Probability of surviving from 80 to 90: men 12% (1950) → 26% (2002); women 16% → 38%.
  - US old-age mortality "stagnated since 1980".
  - Japan and France show no deceleration in decline.
- **Source.** Rau R, Soroko E, Jasilionis D, Vaupel JW.
  - "Continued Reductions in Mortality at Advanced Ages." *Population and Development Review* 2008;34(4):747–768.
  - DOI 10.1111/j.1728-4457.2008.00249.x. No PMID.
- **Retrieved.** https://onlinelibrary.wiley.com/doi/10.1111/j.1728-4457.2008.00249.x (abstract, via browser).
- **Quote (abstract).** "For men, the probability of surviving from age 80 to age 90 has risen from 12 percent in 1950 to 26 percent in 2002; for women, the increase has been from 16 percent to 38 percent. … For selected countries, average annual percent declines in age-specific death rates over the preceding ten years are calculated for single-year age groups 80 to 99 and the years 1970 to 2004. … The trends are not favorable in all countries: for example, old-age mortality in the United States has stagnated since 1980. But countries with exceptionally low mortality, like Japan and France, do not show a deceleration in death rate declines. It is argued that life expectancy at advanced ages may continue to increase at the same pace as in the past."
- **Caveat.** Full text paywalled. The abstract gives no single %/yr figure.

### A3c. Rau et al. MPIDR Working Paper WP-2006-033 (precursor of A3b): rates by decade

- **Values.** Table 2, average annual improvement in mortality (%), 19 countries, Kannisto-Thatcher Database:

| Period | M 80–89 | M 90–99 | F 80–89 | F 90–99 |
|---|---|---|---|---|
| 1950s–1960s | 0.81 | 0.32 | 0.91 | 0.27 |
| 1960s–1970s | 0.89 | 0.94 | 1.35 | 0.85 |
| 1970s–1980s | 1.20 | 1.13 | 2.00 | 1.31 |
| 1980s–1990s | 1.88 | 0.71 | 2.45 | 1.28 |

- **Source.** Rau R, Soroko E, Jasilionis D, Vaupel JW.
  - "10 years after Kannisto: further evidence for mortality decline at advanced ages in developed countries." MPIDR Working Paper WP 2006-033, October 2006.
  - DOI 10.4054/MPIDR-WP-2006-033 (Crossref).
- **Retrieved.** https://www.demogr.mpg.de/papers/working/wp-2006-033.pdf
- **Quote.** "While there was an annual survival improvement of 0.81 percent for men in their 80s when comparing the 1960s with the 1950s, survival improved much faster during the 1990s in comparison the 1980s. This trend is even more pronounced for women where the average annual improvement was 2.45% for octogenarians during the most recent period."
- **Caveat.** This is a working paper with "limited review". The published PDR table may differ. Cite A3b as the peer-reviewed source and the working paper for the decade-specific figures.

### A3d. Oeppen & Vaupel 2002

- **Values.**
  - Record female life expectancy rose linearly 1840–2000: **slope 0.243 years per year** (≈2.9 months/yr), **r² = 0.992**.
  - Men: **slope 0.222** (≈2.7 months/yr), r² = 0.980.
  - 1840 record a little over 45 y (Swedish women); "almost 85 years" (Japanese women) when the paper was written in 2002.
- **Source.** Oeppen J, Vaupel JW.
  - "Broken limits to life expectancy." *Science* 2002;296(5570):1029–1031.
  - DOI 10.1126/science.1069675; PMID 12004104.
- **Retrieved.**
  - https://pdf.stafforini.com/oeppen-2002-broken-limits-life.pdf, a mirror of the 2-page Science PDF. The PDF metadata title is "Broken limits to life expectancy".
  - The publisher page (science.org) was behind a human-verification wall that I did not bypass.
- **Quotes** (margin line numbers removed).
  - "Female life expectancy in the record-holding country has risen for 160 years at a steady pace of almost 3 months per year [Fig. 1 and suppl. table 1 (1)]. In 1840 the record was held by Swedish women, who lived on average a little more than 45 years. Among nations today, the longest expectation of life—almost 85 years—is enjoyed by Japanese women. The four-decade increase in life expectancy in 16 decades is so extraordinarily linear [r2 = 0.992; also see suppl. figs. 1 to 5 (1)] that it may be the most remarkable regularity of mass endeavor ever observed. Record life expectancy has also risen linearly for men (r2 = 0.980), albeit more slowly (slope = 0.222)…"
  - Fig. 1 caption: "Record female life expectancy from 1840 to the present [suppl. table 2 (1)]. The linear-regression trend is depicted by a bold black line (slope = 0.243)…"
  - "For 160 years, best-performance life expectancy has steadily increased by a quarter of a year per year, an extraordinary constancy of human achievement."
- **Caveat.** This trend is in period life expectancy at birth, not old-age hazard. Vallin & Meslé (2009) found a segmented trend, see A3e.

### A3e. Vaupel, Villavicencio & Bergeron-Boucher 2021

- **Values.**
  - Best-practice life expectancy rises by **almost 2.5 y per decade (3 months/yr)**.
  - Vallin–Meslé segmented slopes: 0.32 (1885–1960), **0.23 (since 1960)**.
  - Swedish women: q85 fell from 17% (1950) to 7% (2018), **≈1.3%/yr** (derived: ln(17/7)/68).
  - US women: q85 14% → 7% (1950–2017), ≈1.0%/yr (derived); q95 31% → 22%, ≈0.5%/yr (derived).
  - Maximum observed lifespan rises about 0.12 y per year.
- **Source.** Vaupel JW, Villavicencio F, Bergeron-Boucher M-P.
  - "Demographic perspectives on the rise of longevity." *PNAS* 2021;118(9):e2019536118.
  - DOI 10.1073/pnas.2019536118; PMID 33571137; PMCID PMC7936303.
- **Retrieved.** https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7936303/fullTextXML
- **Quotes.**
  - Abstract: "In the countries doing best each year, life expectancy started to increase around 1840 at a pace of almost 2.5 y per decade. This trend has continued until the present."
  - "…from 46 in 1840 to 87 today, best-practice life expectancy has almost doubled—rising at a remarkably steady pace of almost two and a half years per decade, 3 mo per year, 6 h per day."
  - "Vallin and Meslé (35) … found that the maximum life expectancy followed a segmented trend, with a slope of 0.32 between 1885 and 1960 and 0.23 since 1960."
  - "For Swedish women, the risk of death at age 85 has been cut from about 17% in 1950 to 7% in 2018 (26, 27)."
  - "For US females, the risk of death at age 85 decreased from 14% in 1950 to 7% in 2017. Similar progress was also observed at older ages (e.g., from 31 to 22% at age 95)."
  - "On average, for the countries and ages shown in Table 1, over the past 50 y mortality has been postponed by about a decade."
  - Three views of the future, a natural basis for three scenarios: "1) Some argue that life expectancy will rise more slowly than in the past, perhaps approaching a limit that is not much greater than the current best-practice level, with some chance that life expectancy will fall (14); 2) others think that life expectancy will continue to rise and mortality to decline at the historical pace for the next several decades, and perhaps longer (59, 60); 3) finally, some futurologists predict that life expectancy will rise substantially faster than this because of major biomedical breakthroughs (61)."
  - "This claim is also inconsistent with observed plateaus at a level of about 50% per year of the annual probability of death after age 105 in Italy (54) and after age 110 in a group of countries (55, 56)…"

---

## A4. Delayed-aging scenarios

### A4a. Goldman et al. 2013, Health Affairs

- **How the scenario was parameterised.**
  1. The slope of the intrinsic mortality curve, as observed in 2000 at ages 15–50, **declines by 20% by 2050**.
  2. Mortality, onset of six chronic conditions, and disability are reduced "by **1.25 percent for each year of life lived above age fifty**". This is phased in linearly from 0% in 2010 to the full effect in 2030.
- **Model.** Future Elderly Model microsimulation, US. Progress is assumed to stop after 2030. Baseline mortality: SSA intermediate projections.
- **Gain.** Life expectancy at age 51 in 2030: **35.8 y (status quo) → 38.0 y, i.e. +2.2 y**.
  - Compare delayed cancer: 36.9 y; delayed heart disease: 36.6 y.
  - Social value about **$7.1 trillion** over 50 years: discounted additional quality-adjusted life-years "valued using a conservative metric such as $100,000 per life-year". Costs were discounted at 3% per year.
- **Source.** Goldman DP, Cutler D, Rowe JW, Michaud P-C, Sullivan J, Peneva D, Olshansky SJ.
  - "Substantial health and economic returns from delayed aging may warrant a new focus for medical research." *Health Aff (Millwood)* 2013;32(10):1698–1705.
  - DOI 10.1377/hlthaff.2013.0052; PMID 24101058; PMCID PMC3938188.
- **Retrieved.** https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=3938188&rettype=xml (NIH author manuscript).
- **Quotes.**
  - "We assumed that the slope of the intrinsic mortality curve—that is, mortality from factors such as age, as opposed to exposure to external risks such as trauma or smoking—observed in 2000 for both men and women ages 15–50 would decline by 20 percent by 2050."
  - "The scenario reduced mortality and the probability of onset of both chronic conditions (heart disease, cancer, stroke or transient ischemic attack, diabetes, chronic bronchitis and emphysema, and hypertension), and disability by 1.25 percent for each year of life lived above age fifty (the period in life when most of these diseases emerge). This reduction was phased in over twenty years, starting with a 0 percent reduction in 2010 and increasing linearly until the full 1.25 percent reduction was achieved in 2030."
  - "Life expectancy at age fifty-one in 2030 was 35.8 years in the status quo scenario … In the delayed aging scenario, however, it increased to 38.0 years, an improvement of 2.2 years"
  - Abstract: "Delayed aging could increase life expectancy by an additional 2.2 years, most of which would be spent in good health. The economic value of delayed aging is estimated to be $7.1 trillion over fifty years."
- **Caveat.** "1.25 percent for each year of life lived above age fifty" is ambiguous: it could mean a cumulative or a per-year-of-age multiplier. Quote it verbatim rather than paraphrasing it as a hazard-ratio schedule.

### A4b. Scott, Ellison & Sinclair 2021, Nature Aging

- **How slowing aging was modelled.**
  - The "Peter Pan" case multiplies chronological age by a constant δ (δ = 1 is the current rate; δ = 0 is "forever young").
  - In the Methods, a frailty index F(a) = F\*·e^{δ(a−T)} drives both mortality μ(a) = M\*·F(a)^λ and disability. δ, μ and T are varied to stretch the health and survival functions together.
  - Gompertz baseline: μ(a) = M·e^{β(a−T)} with **T = 97.6, M = 0.3319, β = 0.0966**, calibrated to US life expectancy at birth of 78.9 y (2018).
  - "Struldbrugg" case (contrast): the rate at which mortality rises with age is slowed while health decline is held unchanged.
- **Values.** Willingness to pay (US, VSL framework):
  - **US$37.6 trillion** for a slowdown that raises life expectancy by 1 year (rounded to US$38T in the abstract).
  - **US$366.8 trillion** for +10 years (US$367T).
- **Source.** Scott AJ, Ellison M, Sinclair DA.
  - "The economic value of targeting aging." *Nat Aging* 2021;1(7):616–623.
  - DOI 10.1038/s43587-021-00080-0; PMID 37117804; PMCID PMC10154220.
- **Retrieved.** https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=10154220&rettype=xml
- **Quotes.**
  - "To allow for a slowdown in aging we multiply chronological age a by a constant δ. For δ = 1, biological damage accumulates at its current rate but the lower δ is, the more slowly aging occurs and the greater the gap between biological and chronological age. The 'forever young' case is given by δ = 0."
  - Methods: "We use a Gompertz equation for mortality, in which imposing a compensating effect of mortality gives the restricted expression μ(a) = Me^{β(a − T)}. We set T = 97.6 and M = 0.3319 based on cross-country evidence39, and then calibrate β = 0.0966 so that LE at birth matches that in the US for 2018 (78.9 years)."
  - "For Peter Pan we assume that aging is captured by a frailty index F(a) = θe^{δa} and impose a compensating effect such that θ = F\*e^{δT} so that F(a) = F\*e^{δ(a−T)}. … mortality by μ(a) = M\*F(a)^λ … For our Peter Pan simulations we vary δ, µ and T in order to simultaneously elongate both the health and survival functions."
  - "In our simulations, we achieve this by reducing the rate at which mortality increases with age while holding unchanged the rate at which health declines." (Struldbrugg case)
  - In the two Methods quotes above, the equations were re-typed from MathML. The surrounding text matches the source exactly.
  - "…the total WTP for a 2017 slowdown in aging leading to a 1-year increase in LE is US$37.6 trillion … The corresponding number for a 10-year increase in LE is US$366.8 trillion"
  - On Goldman 2013: "…ref. 29, which calculates a slowdown in aging producing a 2.2-year increase in LE as worth US$7.1 trillion to those aged over 51."
- **Caveat.** The main-text description (age × δ) and the Methods description (δ as the exponent rate of the frailty index) are both quoted above. They are equivalent in effect: δ scales the exponential rate of damage accumulation.

---

## A5. Forecasts of extreme longevity: Pearce & Raftery 2021

- **Values.** Probabilities that someone (from the 13 IDL countries) reaches a given age, at last birthday, during 2020–2100 (Table 2 / Table A-4):

| Age reached | Probability |
|---|---|
| >122 (record broken) | >99% |
| 124 | 0.99938 |
| 125 | 0.98324 |
| **126** | **0.88777** |
| 127 | 0.68112 |
| **128** | **0.43703** |
| 129 | 0.24813 |
| **130** | **0.13223** |
| 135 | 0.00408 |
| 140 | 0.00012 |

- **Design.**
  - Exponential survival above 110 (Rootzén & Zholud 2017), λ posterior from the IDL (A1d).
  - Bayesian projections of the population aged 110–114 to 2080, based on UN WPP 2019 data.
  - Monte Carlo over both sources of uncertainty.
- **Source.** Pearce M, Raftery AE.
  - "Probabilistic forecasting of maximum human lifespan by 2100 using Bayesian population projections." *Demographic Research* 2021;44(52):1271–1294.
  - DOI 10.4054/DemRes.2021.44.52; PMID 39363909; PMCID PMC11448547.
- **Retrieved.** https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=11448547&rettype=xml
- **Quotes.**
  - Abstract: "Based on the Bayesian analysis, there is a greater than 99% probability that the current MRAD of 122 will be broken by 2100. We estimate the probabilities that a person lives to at least age 126,128, or 130 this century, as 89%, 44%, and 13%, respectively."
  - "Although possible under the model, it is extremely unlikely that a person will attain age 135 or 140 this century."
- **Caveats.**
  - Only individuals from the 13 IDL countries are counted, so the results are conservative.
  - The model assumes λ is constant over age and time above 110, i.e. no future improvement at 110+.

---

## A6. Evidence of stagnating mortality improvement in the 2010s (for a "no improvement" scenario)

### A6a. Ho & Hendi 2018, BMJ

- **Values.**
  - In 2014–15, 12 of 18 countries had declines in life expectancy (women) and 11 of 18 (men). Average declines: −0.21 y (women), −0.18 y (men). These were driven mainly by mortality at ages ≥65.
  - 2010–16 gains: other countries +0.88 y (F) and +1.38 y (M); US +0.19 (F) and +0.04 (M); British women +0.37, British men +0.68.
  - US rate: 0.32 (F) and 0.06 (M) y per decade, vs 1.7/2.1 y per decade in the 2000s.
- **Source.** Ho JY, Hendi AS.
  - "Recent trends in life expectancy across high income countries: retrospective observational study." *BMJ* 2018;362:k2562.
  - DOI 10.1136/bmj.k2562; PMID 30111634; PMCID PMC6092679.
  - **Erratum:** BMJ 2018;362:k3622, PMID 30135175. It corrects the US male 2010 value to 76.36 (not 73.36).
- **Retrieved.**
  - PMC6092679 and PMC6103465 via https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=…
- **Quotes.**
  - Abstract: "The majority of high income countries in the study experienced declines in life expectancy during 2014-15; of the 18 countries, 12 experienced declines in life expectancy among women and 11 experienced declines in life expectancy among men. The average decline was 0.21 years for women and 0.18 years for men. In most countries experiencing declines in life expectancy, these declines were predominantly driven by trends in older age (≥65 years) mortality…"
  - Abstract: "Most of the countries that experienced declines in life expectancy during 2014-15 experienced robust gains in life expectancy during 2015-16 that more than compensated for the declines. However, the United Kingdom and the United States appear to be experiencing stagnating or continued declines in life expectancy, raising questions about future trends in these countries."
- **Caveat.** Most 2014–15 declines rebounded in 2015–16, attributed partly to the severe H3N2 season. This is evidence of a transient shock, not universal stagnation, except for the UK and US.

### A6b. Leon, Jdanov & Shkolnikov 2019 (correction: Lancet Public Health, not BMJ)

- **Values.** Table 1, mean annual change in life expectancy at birth (years):

| Period | E&W men | 22-country median men | E&W women | 22-country median women |
|---|---|---|---|---|
| 2006–11 | 0.33 | 0.31 | 0.25 | 0.14 |
| 2011–16 | **0.07** | **0.18** | **0.02** | **0.13** |

- **Source.** Leon DA, Jdanov DA, Shkolnikov VM.
  - "Trends in life expectancy and age-specific mortality in England and Wales, 1970–2016, in comparison with a set of 22 high-income countries: an analysis of vital statistics data." *Lancet Public Health* 2019;4(11):e575–e582.
  - DOI 10.1016/S2468-2667(19)30177-X; PMID 31677776. Open access.
- **Retrieved.** https://www.thelancet.com/journals/lanpub/article/PIIS2468-2667(19)30177-X/fulltext (via browser).
- **Quotes.**
  - "In 2011–16, the rate of improvement in life expectancy slowed sharply for both sexes in England and Wales, and slowed more moderately in the comparator group because of negative trends in all adult age groups."
  - "Although many countries have seen slower increases in life expectancy since 2011, trends in England and Wales are among the worst."
  - "Life expectancy trends in 2011–16 have not slowed down in Italy, Japan, New Zealand, Norway, and Switzerland."

### A6c. Olshansky et al. 2024, Nature Aging (supplementary: the deceleration argument)

- **Source.** Olshansky SJ, Willcox BJ, Demetrius L, Beltrán-Sánchez H.
  - "Implausibility of radical life extension in humans in the twenty-first century." *Nat Aging* 2024;4(11):1635–1642.
  - DOI 10.1038/s43587-024-00702-3; PMID 39375565; PMCID PMC11564081.
- **Retrieved.** Europe PMC record MED/39375565 (abstract).
- **Quote.** "We found that, since 1990, improvements overall in life expectancy have decelerated. … Our analysis suggests that survival to age 100 years is unlikely to exceed 15% for females and 5% for males, altogether suggesting that, unless the processes of biological aging can be markedly slowed, radical human life extension is implausible in this century."
- Also relevant: Rau 2008 abstract, "old-age mortality in the United States has stagnated since 1980" (A3b).

---

## A7. The human Gompertz slope ("rate of ageing") and mortality-rate doubling time (MRDT)

- **Values.** MRDT = ln 2 / b.

| Source | Reported | Implied b (/yr) | Implied MRDT (yr) |
|---|---|---|---|
| Kirkwood 2015, citing Jones | MRDT "consistently around 8 years" | 0.087 (derived) | 8 |
| Kirkwood 2015, citing Sacher | MRDT 3100 days (US white females, 1969) | 0.082 (derived) | 8.5 |
| Barbi 2018 | slope 0.103 at ages 65–80 (Italian women, 1904 cohort) | 0.103 | 6.7 (derived) |
| Scott 2021 | β = 0.0966 (US 2018 calibration) | 0.0966 | 7.2 (derived) |
| Liu 2018 / Levine 2018 Suppl. | divisor 0.09165 (Liu) or 0.090165 (Levine Suppl.); see A9 | ≈0.090–0.092 | ≈7.6–7.7 (derived) |

- **Source 1.** Kirkwood TBL.
  - "Deciphering death: a commentary on Gompertz (1825) 'On the nature of the function expressive of the law of human mortality, and on a new mode of determining the value of life contingencies'." *Phil Trans R Soc B* 2015;370(1666):20140379.
  - DOI 10.1098/rstb.2014.0379; PMID 25750242; PMCID PMC4360127.
  - Retrieved: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=4360127&rettype=xml
  - Quotes:
    - "Sacher [10] termed the quantity ln[2]/β the mortality rate 'doubling time, i.e. the time required for the death rate to increase by a factor of two'."
    - "Sacher [10] reported that the mortality doubling time was 220 days for the house mouse (Mus musculus) but 3100 days for humans (US white females, 1969)."
    - "Jones [23] compared mortality patterns from India in 1900, Mexico in 1940, Sweden in 1949, and the USA in 1900, 1940 and 1950. Despite large differences between these populations in the levels of mortality in earlier life, the slopes in a graph of log mortality rate against age showed a close approximation to parallelism after mid-life (40 years), with a mortality doubling time consistently around 8 years."
    - "Vaupel [25] provided evidence that the slope parameter β in equation (2.1) is the same for all human populations today and in the past, whereas it is α that varies."
- **Source 2.** Barbi 2018 (A1a). Quote: "This near- negligible slope stands in striking contrast to the slope as large as 0.103 at younger ages (65–80) in Fig. 1b, which is paired with a log hazard at 65 of log(0.015)."
- **Source 3.** Scott 2021 (A4b). Quote: "…calibrate β = 0.0966 so that LE at birth matches that in the US for 2018 (78.9 years)."
- **Caveats.**
  - b depends on the age range fitted and on whether a Makeham term is included. Kirkwood also notes "Gompertzian mortality doubling times appear to become shorter when levels of absolute mortality fall".
  - Report 0.08–0.10/yr (MRDT about 7–8.5 y) as the typical range for adult human populations, with the age range stated.

---

## A8. Risk and rate advancement periods (RAP)

### A8a. Definition: Brenner, Gefeller & Greenland 1993

- **Source.** Brenner H, Gefeller O, Greenland S.
  - "Risk and rate advancement periods as measures of exposure impact on the occurrence of chronic diseases." *Epidemiology* 1993;4(3):229–236.
  - DOI 10.1097/00001648-199305000-00006; PMID 8512987.
- **Retrieved.**
  - https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=8512987&rettype=abstract
  - Ovid/LWW abstract page. Full text is subscriber-only.
- **Quote (abstract).** "In this paper, we examine two alternative measures, the risk and rate advancement periods, which are the time periods by which the risk or rate of disease is advanced among exposed subjects conditional on disease-free survival to some baseline age. These measures are applicable for risk factors that promote progression of chronic diseases whose rates increase with age. Point and interval estimates of these measures are easily derived from the output of standard modeling analyses."

### A8b. Interpretation and cautions: Discacciati, Bellavia, Orsini & Greenland 2016

- **Source.** Discacciati A, Bellavia A, Orsini N, Greenland S.
  - "On the interpretation of risk and rate advancement periods." *Int J Epidemiol* 2016;45(1):278–284.
  - DOI 10.1093/ije/dyv320; PMID 26675753.
- **Retrieved.**
  - PubMed abstract.
  - OUP article page, where full text is paywalled ("Get access"; the Unpaywall "free" PDF link returned an HTML wall).
- **Quote (abstract).** "Specifically, they quantify the time by which the risk or rate of a disease is advanced among exposed subjects conditional on disease-free survival to a certain baseline age. … In particular, RAP is often misinterpreted as the difference in mean survival time, when in fact it is a distinct concept and a profoundly different quantity. Other misinterpretations include interpreting RAP as the time by which a survival curve is shifted between exposed and unexposed, and equating RAP to a simple function of relative risks. … We also show how RAP is profoundly sensitive to the specification of disease dependence on age."

### A8c. Formula RAP = ln(HR_exposure) / ln(HR_age per year)

The formula is verified in open-access papers co-authored by Brenner. It is not verified in the Brenner 1993 or Discacciati 2016 full text, which are paywalled.

- **Ordóñez-Mena JM, …, Orsini N, …, Brenner H.** "Quantification of the smoking-associated cancer risk with rate advancement periods: meta-analysis of individual participant data from cohorts of the CHANCES consortium."
  - *BMC Med* 2016;14:62. DOI 10.1186/s12916-016-0607-5; PMID 27044418; PMCID PMC4820956.
  - Quotes:
    - "RAPs for a given smoking exposure variable ("smok_expo") were calculated from the HRs for that given smoking exposure variable and the HR for age obtained in the Cox models by applying the following formula: RAPsmok_expo = (log HRsmok_expo)/(log HRage)."
    - "This calculation of the RAPs assumes that the risk of the disease exponentially increases with age, which is a fair assumption for cancer and is commonly made in Cox regression models including age as a linear term."
    - "…if the age at which a given level of cancer risk is reached is 65 years for never smokers and 55 years for current smokers, the RAP for current smoking would be 10 years…"
- **Mons U, …, Brenner H.** *BMJ* 2015;350:h1551. DOI 10.1136/bmj.h1551; PMID 25896935; PMCID PMC4413837.
  - Quote: "Risk advancement periods are calculated as the ratio of the regression coefficients of the respective predictor variable and age (see appendix for further details and formulas) and quantify by how many years cardiovascular mortality is advanced in exposed participants compared with the unexposed reference group (for example, current smokers in comparison with never smokers)."
- **Lees JS et al.** *EClinicalMedicine* 2021;38:101030. DOI 10.1016/j.eclinm.2021.101030; PMID 34505030; PMCID PMC8413238. It cites Brenner 1993 as ref. 25.
  - Quote: "RAP = βE/βA, where βE represents the adjusted coefficient of the exposure variable, and βA represents the regression coefficient for age."
- **Retrieved.** PMC XML via https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={4820956,4413837,8413238}&rettype=xml
- **Relevance to LongPi.**
  - LongPi's "mortality-equivalent age" offset is mathematically a rate advancement period: Δage = ln HR / b under log-linear age dependence.
  - Per Discacciati 2016, it must not be presented as a difference in life expectancy or as a horizontal shift of the survival curve.
  - It is model-dependent: it requires an exponential dependence on age and no exposure × age interaction.

---

## A9. Converting a Gompertz mortality score to an "age" (PhenoAge)

- **Source 1.** Liu Z, Kuo P-L, Horvath S, Crimmins E, Ferrucci L, Levine M.
  - "A new aging measure captures morbidity and mortality risk across diverse subpopulations from NHANES IV: A cohort study." *PLoS Med* 2018;15(12):e1002718.
  - DOI 10.1371/journal.pmed.1002718; PMID 30596641; PMCID PMC6312200.
  - **Correction:** *PLoS Med* 2019;16(2):e1002760, PMID 30802240, PMCID PMC6388911. The published equation was "missing a step".
- **Retrieved.** https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=6312200 and id=6388911.
- **Quotes.**
  - "In general, a person's Phenotypic Age signifies the age within the general population that corresponds with that person's mortality risk. For example, 2 individuals may be 50 years old chronologically, but one may have a Phenotypic Age of 55 years, indicating that he/she has the average mortality risk of someone who is 55 years old chronologically, whereas the other may have a Phenotypic Age of 45 years, indicating that he/she has the average mortality risk of someone who is 45 years old chronologically."
  - "The algorithm for calculating Phenotypic Age is based on parametrization of 2 Gompertz proportional hazard models—one fit using all 10 selected variables, and the other fit using only chronological age."
  - Correction, the corrected equation: "PhenotypicAge=141.50+ln[−0.00553×ln(1−M)]/0.09165 Where: M=1−exp(−1.51714×exp(xb)/0.0076927) and: xb=−19.907−0.0336×Albumin+0.0095×Creatinine+0.1953×Glucose+0.0954×ln(CRP)−0.0120×LymphocytePercent+0.0268×MeanCellVolume+0.3306×RedCellDistributionWidth+0.00188×AlkalinePhosphatase+0.0554×WhiteBloodCellCount+0.0804×ChronologicalAge". The fraction bars were linearised.
- **Source 2.** Levine ME, Lu AT, Quach A, et al.
  - "An epigenetic biomarker of aging for lifespan and healthspan." *Aging (Albany NY)* 2018;10(4):573–591.
  - DOI 10.18632/aging.101414; PMID 29676998; PMCID PMC5940111.
- **Retrieved.**
  - Full text: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=5940111&rettype=xml
  - Supplement 1 (aging-10-101414-s001.pdf): https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5940111/supplementaryFiles
- **Quotes.**
  - Main text: "These nine biomarkers and chronological age were then included in a parametric proportional hazards model based on the Gompertz distribution. Based on this model, we estimated the 10-year (120 months) mortality risk of the j-the individual. Next, the mortality score was converted into units of years (Supplement 1)."
  - Supplement 1: "In step 3, carried out another parametric proportional hazards model analysis with Gompertz distribution, but only including chronological age as a IV. We will refer to this analysis as the univariate Gompertz regression model since it only involved one covariate (age). … In step 4, we solved the equation CDF(120,xj)=CDF.univariate(120,agej) for the variable agej. The resulting solution for the j-th individual, referred to as PhenotypicAge, is given by PhenotypicAgej = 141.50225 + ln(−0.00553 ∗ ln(1 − CDF(120, xj)))/0.090165"
  - Supplement 1: "CDF(t,x)=1-exp(-exp(xb) (exp(γt)-1)/γ) where t denotes time (here in units of months) … and γ =0.0076927."
- **Caveat: discrepancy in the constants.**
  - Levine 2018 Supplement 1 prints the divisor as **0.090165** (twice), with intercept 141.50225.
  - Liu 2018 and its 2019 correction print **0.09165**, with intercept 141.50.
  - Both cannot be correct. Cite the formula as published and state which constant LongPi uses.
  - The divisor is the per-year age coefficient of the age-only Gompertz model, implied by the inversion. This is consistent with b ≈ 0.09 (A7).

---

## Not verified / limits of this check

1. **RAP formula in the primary methods papers** (Brenner 1993; Discacciati 2016). Full texts are paywalled. The definitions are verified from the abstracts, and the formula from Brenner-coauthored open-access papers (A8c).
   - Lead: the Discacciati 2016 full text, via institutional access to academic.oup.com/ije/article/45/1/278.
2. **Science-published versions** of Barbi 2018 and Oeppen & Vaupel 2002. Numbers were taken from the NIH author manuscript and from a mirror of the publisher PDF, because science.org required human verification.
3. **Rau 2008 published tables.** The decade-specific %/yr figures come from the 2006 MPIDR working-paper precursor. The published PDR article was not accessible beyond its abstract.
4. **Numeric CIs for Gampe 2010.** None are reported; uncertainty is graphical only. Use Gampe 2021's SEs.
