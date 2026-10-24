#!/usr/bin/env python3
"""Build data/population_norms_china.json: same-age, same-sex Chinese distributions of each marker.

Every number below is copied from a national survey table quoted in
evidence/literature/D_china_population_norms.md (section ids in comments).
"derived" marks values we computed from published margins; the rule is stated next to each.

Usage: build_norms.py <skill_data_dir>
"""
import json
import sys
from pathlib import Path

BANDS = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 110)]


def rows(means, sds, mean_se=None, note=""):
    out = []
    for i, (lo, hi) in enumerate(BANDS):
        r = {"age_lo": lo, "age_hi": hi, "mean": means[i], "sd": sds[i] if isinstance(sds, list) else sds}
        if mean_se is not None:
            r["mean_se"] = mean_se[i] if isinstance(mean_se, list) else mean_se
        out.append(r)
    return out


def cats(ps):
    return [{"age_lo": lo, "age_hi": hi, "p": p} for (lo, hi), p in zip(BANDS, ps)]


M = {}

# --- SBP, office/automated (CCDRFS 2018, Omron HBP1300, mean of readings 2-3) -----------------
# D1.2: means by sex x 10-y band 18-69. 70-79/80+ derived: 60-69 mean + CHARLS 2015 median increments (Appendix A).
# SD: CCDRFS 2013 by age band (D1.6): <40 15.93, 40-59 19.18, >=60 22.38 (not crossed with sex).
sbp_sd = [15.9, 15.9, 19.2, 19.2, 22.4, 22.4, 22.4]
M["sbp"] = {"M": rows([125.3, 127.1, 130.4, 135.8, 139.7, 139.7 + 3.6, 139.7 + 6.5], sbp_sd),
            "F": rows([113.2, 116.3, 124.6, 133.5, 139.4, 139.4 + 7.3, 139.4 + 13.5], sbp_sd),
            "source": "CCDRFS 2018 (Zhang M, BMJ 2023;380:e071952, Suppl Table 11); SD CCDRFS 2013 (Wang L, JAMA 2017); >=70 derived with CHARLS 2015 increments"}

# --- LDL-C (CANCDS 2015, Song PK, Biomed Environ Sci 2019; D2.2) -----------------------------
# Published by sex (M 2.90, F 2.83) and by age (18-44 2.71, 45-54 3.03, 55-64 3.13, 65-74 3.09, 75+ 3.04), not crossed.
# derived: age-band mean +/- half the sex difference (0.035). SD derived: CCDRFS 2013 TC SD 39 mg/dL (1.01 mmol/L) x 0.85.
ldl_age = [2.71, 2.71, 2.87, 3.08, 3.11, 3.07, 3.04]   # 40-49 = mean(2.71, 3.03); 50-59 = mean(3.03, 3.13); 60-69 = mean(3.13, 3.09)
M["ldl"] = {"M": rows([round(x + 0.035, 3) for x in ldl_age], 0.86), "F": rows([round(x - 0.035, 3) for x in ldl_age], 0.86),
            "source": "CANCDS 2015 margins (Song PK 2019); sex x age and SD derived"}

# --- glycaemic status, ADA criteria (CCDRFS 2018-19, Wang L, JAMA 2021; D3.1) -----------------
# By age (both sexes): diabetes 5.0, 6.5, 11.1, 19.3, 23.9, 27.3 (>=70); prediabetes 27.3, 34.2, 40.3, 45.8, 47.6, 48.9.
# By sex: diabetes M 13.3, F 11.5 (all 12.4); prediabetes M 41.2, F 34.9 (all 38.1).
# derived: age prevalence x sex ratio.
dm = [5.0, 6.5, 11.1, 19.3, 23.9, 27.3, 27.3]
pre = [27.3, 34.2, 40.3, 45.8, 47.6, 48.9, 48.9]


def glyc(rdm, rpre):
    out = []
    for a, b in zip(dm, pre):
        d, p = min(a * rdm, 60) / 100, min(b * rpre, 70) / 100
        out.append({"normal": round(1 - d - p, 4), "prediabetes": round(p, 4), "diabetes": round(d, 4)})
    return cats(out)


M["glycemic"] = {"M": glyc(13.3 / 12.4, 41.2 / 38.1), "F": glyc(11.5 / 12.4, 34.9 / 38.1),
                 "source": "CCDRFS 2018 (Wang L, JAMA 2021;326:2498), ADA criteria; sex x age derived"}

# --- BMI (CNHS 2015-17, Yu D, AJPM Focus 2024; D4.1) ---------------------------------------------
# M 20-39 24.1, 40-59 24.7, >=60 23.8; F 23.1, 24.7, 24.2. >=80 derived from CHARLS medians (M 80: 21.5 vs 70: 22.4).
# SD: CCDRFS 2013 M 3.65, F 3.79 (D4.2).
M["bmi"] = {"M": rows([24.1, 24.1, 24.7, 24.7, 23.8, 23.8, 22.9], 3.65),
            "F": rows([23.1, 23.1, 24.7, 24.7, 24.2, 24.2, 23.0], 3.79),
            "source": "CNHS 2015-17 (Yu D 2024); SD CCDRFS 2013; >=80 derived (CHARLS 2015 decline)"}

# --- waist (CNHS 2015, Nan J, Biomed Environ Sci 2025; D4.4) — used by risk cards, not the model --
M["waist"] = {"M": rows([81.48, 85.48, 86.58, 85.75, 84.95, 84.26, 84.26], 10.4),
              "F": rows([75.33, 78.29, 80.87, 83.22, 83.65, 82.11, 82.11], 10.1),
              "source": "CNHS 2015 (Nan J 2025); SD Wang Z 2026"}

# --- resting pulse, clinic (2014 National Physical Fitness Surveillance, healthy volunteers; D7-A) --
# 5-y means averaged into 10-y bands (derived); 70+ from CHARLS 2015 medians (D7-E); SD CKB baseline M 12, F 11 (D7-B).
M["rhr"] = {"M": rows([78.3, 78.4, 78.2, 77.8, 77.0, 72.0 + 4.0, 72.2 + 4.0], 12.0),
            "F": rows([79.2, 78.2, 77.4, 76.8, 76.6, 74.1 + 3.0, 75.6 + 3.0], 11.0),
            "source": "2014 国民体质监测公报 安静脉搏; >=70 derived (CHARLS medians + mean-median offset); SD CKB"}

# --- grip, stronger hand best of 2 (6th National Physical Fitness Monitoring 2025; D8.1) -----------
# 5-y means averaged into 10-y bands (derived); 80+ from CHARLS median at 80 (D8.5/Appendix A). SD CNHS decades (D8.4).
M["grip"] = {"M": rows([42.75, 43.6, 42.2, 40.0, 35.0, 31.15, 27.3], [7.6, 7.6, 7.6, 7.7, 7.3, 7.2, 7.2]),
             "F": rows([26.55, 26.75, 26.5, 25.3, 23.1, 21.6, 19.5], [5.0, 5.2, 5.3, 4.9, 4.8, 4.8, 4.8]),
             "source": "第六次全国国民体质监测公报 (2025) 附表2-2/3-2; SD CNHS 2012-17 (He H 2023)"}

# --- self-reported sleep, total h/day (CCDRFS 2018, Chen Y, Biomed Environ Sci 2026; D9-A) ---------
# By age (both sexes; sex difference 0.03 h): 7.91 (1.27), 7.69 (1.20), 7.49 (1.32), 7.29 (1.53), 7.28 (1.75), >=70 7.34 (2.04).
sl = rows([7.91, 7.69, 7.49, 7.29, 7.28, 7.34, 7.34], [1.27, 1.20, 1.32, 1.53, 1.75, 2.04, 2.04])
M["sleep"] = {"M": sl, "F": sl, "source": "CCDRFS 2018 (Chen Y 2026), self-reported total sleep"}

# --- VO2max, treadmill scale (the scale smartwatch estimates are calibrated to) ------------------
# Chinese treadmill CPET VO2peak means (Huang J, J Cardiopulm Rehabil Prev 2024;44:212, n=4,199; B2b):
#   men 20s 42.6, 30s 41.2, 40s 38.7, 50s 35.9; women 37.1, 34.7, 32.0, 30.3.
# 60+ derived: continue with the FRIEND 2015 treadmill decade decline (men 50s->60s -4.4, 60s->70s -3.8; women -3.4, -1.7; B2c).
# SD not retrievable for Huang 2024: FRIEND 2015 decade SDs used (derived, ~7.5 men / 6.5 women).
# mean_se 2.5 carries residual scale uncertainty (FRIEND 2022: treadmill norms 1.5-4.6 lower than 2015).
M["vo2max"] = {"M": rows([42.6, 41.2, 38.7, 35.9, 31.5, 27.7, 24.5], [8.0, 7.6, 7.3, 7.0, 6.6, 6.2, 6.0], 2.5),
               "F": rows([37.1, 34.7, 32.0, 30.3, 26.9, 25.2, 23.0], [7.2, 6.8, 6.3, 5.9, 5.4, 5.0, 5.0], 2.5),
               "source": "Chinese treadmill VO2peak (Huang J 2024) 20-59; 60+ and SDs derived from FRIEND 2015 (Kaminsky 2015)"}

# --- smoking (CCDRFS 2018, Zhang M, PLoS Med 2022, S3 tables; D5.1) -----------------------------
# Men current: 18-19 31.6, 20-24 45.2, 25-29 50.6, 30-39 50.8, 40-49 53.5, 50-59 56.0, 60-69 50.1; former 3.1, 2.8, 2.7, 5.2, 7.8, 12.7, 19.5.
# Women current: 4.3, 1.2, 1.1, 1.3, 2.0, 2.6, 3.2; former 0.9, 0.4, 0.3, 0.3, 0.3, 0.5, 1.0.
# 18-29 derived as the mean of the three sub-bands; >=70: men current 40.6 (2024 CATS, D5.4), former 25 (derived from trend); women current 2.5, former 1.5.
def sm(cur, form):
    return {"never": round(1 - cur - form, 4), "former": round(form, 4), "current": round(cur, 4)}


M["smoking"] = {"M": cats([sm(0.425, 0.029), sm(0.508, 0.052), sm(0.535, 0.078), sm(0.560, 0.127), sm(0.501, 0.195), sm(0.406, 0.25), sm(0.35, 0.28)]),
                "F": cats([sm(0.022, 0.005), sm(0.013, 0.003), sm(0.020, 0.003), sm(0.026, 0.005), sm(0.032, 0.010), sm(0.025, 0.015), sm(0.025, 0.015)]),
                "source": "CCDRFS 2018 (Zhang M, PLoS Med 2022;19:e1004064); >=70 from 2024 CATS + derived"}

# --- alcohol (CCDRFS 2018 via Song S, EClinicalMedicine 2023, Table S3; D6.6) --------------------
# Categories by average ethanol g/day; men: moderate 1-40, hazardous 41-60, harmful 61+; women 1-20 / 21-40 / 41+.
# urban + rural averaged with equal weight (derived). Bands 18-44 / 45-59 / 60+ mapped onto 10-y bands.
def alc(non, mod, haz, harm):
    t = non + mod + haz + harm
    return {"none": round(non / t, 4), "moderate": round(mod / t, 4), "hazardous": round(haz / t, 4), "harmful": round(harm / t, 4)}


aM = [alc((38.5 + 37.4) / 2, (55.0 + 54.6) / 2, (2.6 + 3.2) / 2, (3.8 + 4.8) / 2),
      alc((35.1 + 38.4) / 2, (50.6 + 43.6) / 2, (5.8 + 6.7) / 2, (8.5 + 11.3) / 2),
      alc((48.7 + 51.3) / 2, (38.8 + 32.9) / 2, (4.9 + 5.7) / 2, (7.6 + 10.1) / 2)]
aF = [alc((76.2 + 82.3) / 2, (23.2 + 17.3) / 2, (0.4 + 0.3) / 2, (0.2 + 0.1) / 2),
      alc((78.0 + 84.3) / 2, (21.2 + 14.8) / 2, (0.4 + 0.4) / 2, (0.4 + 0.5) / 2),
      alc((85.4 + 88.0) / 2, (13.8 + 10.5) / 2, (0.3 + 0.7) / 2, (0.4 + 0.8) / 2)]
M["alcohol"] = {"M": cats([aM[0], aM[0], aM[0], aM[1], aM[2], aM[2], aM[2]]),
                "F": cats([aF[0], aF[0], aF[0], aF[1], aF[2], aF[2], aF[2]]),
                "source": "CCDRFS 2018 (Song S, EClinicalMedicine 2023, Table S3), WHO g/day categories"}

out = {"version": "2026-10-24", "bands": BANDS, "markers": M,
       "note": "see evidence/literature/D_china_population_norms.md for tables and quotes"}
Path(sys.argv[1], "population_norms_china.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("markers:", list(M))
