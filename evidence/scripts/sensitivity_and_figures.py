#!/usr/bin/env python3
"""Sensitivity analyses and figures for the methods white paper.

Usage: sensitivity_and_figures.py <repo_root>
Writes evidence/results/sensitivity.json and docs/figures/*.png
"""
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from lifelines import CoxPHFitter  # noqa: E402

warnings.filterwarnings("ignore")
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "skills/longpi-report/scripts"))
from lp import clock, mortality as M  # noqa: E402

res_dir, fig_dir = root / "evidence/results", root / "docs/figures"
fig_dir.mkdir(parents=True, exist_ok=True)
for f in ("PingFang SC", "Hiragino Sans GB", "Heiti SC", "Arial Unicode MS"):
    if any(f in x.name for x in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = f
        break
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150, "axes.unicode_minus": False})
BLUE, GREY, RED = "#2a78d6", "#7c7b76", "#e34948"
out = {}

# ---------------------------------------------------------------- 1. 120 Index sensitivity
age0, year0 = 40.0, 2026.0
rows = []
Rs = [0.6, 0.8, 1.25, 1.6]
for plateau in (0.6, 0.7, 0.8):
    ref = M.Reference("M", plateau=plateau)
    for sk, sc in (("S1", {"kind": "period"}), ("S2", {"kind": "wpp"}),
                   ("S3", {"kind": "wpp_slowed", "start_year": 2045, "ramp_years": 20, "slope_reduction": 0.2, "pivot_age": 50})):
        s = M.survival_from(M.cohort_hazards(ref, age0, year0, sc), age0)
        ages = M.survival_ages(age0, len(s))
        p_ref = M.at_age(ages, s, 120)
        for s2 in (0.001, 0.10, 0.16, 0.22):
            idx = [100 + 10 * math.log10(max(M.at_age(ages, M.individual_survival(s, R, s2), 120), 1e-300) / p_ref) for R in Rs]
            rows.append({"plateau": plateau, "scenario": sk, "s2": s2, "p120_ref": p_ref, **{f"R={R}": round(v, 2) for R, v in zip(Rs, idx)}})
sens = pd.DataFrame(rows)
out["index_sensitivity"] = rows
# summary: spread of the index for R = 1.25 across frailty assumptions (excluding PH)
fr = sens[sens.s2 > 0.05]
out["index_R125_range_frailty"] = [float(fr["R=1.25"].min()), float(fr["R=1.25"].max())]
out["index_R125_range_PH"] = [float(sens[sens.s2 < 0.05]["R=1.25"].min()), float(sens[sens.s2 < 0.05]["R=1.25"].max())]

# ---------------------------------------------------------------- 2. LongPi Age approximation check
ref = M.Reference("M")
b = ref.gompertz_slope(2026)
errs = []
for a in range(30, 81, 5):
    for R in (0.7, 0.85, 1.2, 1.4):
        target = R * ref.mu_at(a, 2026)
        lo, hi = 18.0, 100.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if ref.mu_at(mid, 2026) < target:
                lo = mid
            else:
                hi = mid
        exact = (lo + hi) / 2
        approx = a + math.log(R) / b
        errs.append({"age": a, "R": R, "exact": round(exact, 2), "approx": round(approx, 2), "diff": round(approx - exact, 2)})
out["age_equivalence_check"] = {"b": b, "max_abs_diff": max(abs(e["diff"]) for e in errs), "rows": errs}

# ---------------------------------------------------------------- 3. Pace power
prior, noise = 0.29, 1.6
pw = []
for n in range(2, 11):
    t = np.arange(n, dtype=float)
    sxx = float(((t - t.mean()) ** 2).sum())
    for dup in (1, 2):
        post = (1 / prior ** 2 + sxx / (noise ** 2 / dup)) ** -0.5
        pw.append({"annual_tests": n, "draws_per_test": dup, "posterior_sd": round(post, 3), "reduction_vs_prior_pct": round(100 * (1 - post / prior), 1)})
out["pace_power"] = pw

# ---------------------------------------------------------------- 4. PhenoAge noise by analyte (typical values)
typ = dict(albumin=45, creatinine=80, glucose=5.2, crp=1.0, lymph_pct=31, mcv=90, rdw=13.0, alp=70, wbc=6.2)
sd, shares = clock.noise_sd(typ)
out["phenoage_noise"] = {"sd_years": round(sd, 2), "rcv95_two_tests": round(1.96 * math.sqrt(2) * sd, 2),
                         "shares": {k: round(v, 3) for k, v in sorted(shares.items(), key=lambda kv: -kv[1])}}
(res_dir / "sensitivity.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

# ================================================================ figures
cal = json.loads((res_dir / "nhanes_calibration.json").read_text())

# Fig 1: decile calibration (with clock)
dec = cal["validation"]["with_clock"]["deciles"]
fig, ax = plt.subplots(figsize=(5.2, 4.4))
pred = [d["pred"] for d in dec]
obs = [d["obs"] for d in dec]
lo = [d["obs"] - d["lo"] for d in dec]
hi = [d["hi"] - d["obs"] for d in dec]
ax.errorbar(pred, obs, yerr=[lo, hi], fmt="o", color=BLUE, ecolor="#9cc0ec", capsize=3, label="观察值（95% CI）")
lim = [min(pred + obs) - 0.2, max(pred + obs) + 0.2]
ax.plot(lim, lim, "--", color=GREY, lw=1, label="完全校准")
ax.set_xlabel("预测的对数风险比（LongPi 差值 × 年龄系数）")
ax.set_ylabel("观察到的对数风险比（Cox，相对第 5 十分位）")
ax.set_title("图 1  NHANES 2009–2018 时间外推验证：十分位校准", fontsize=10)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(fig_dir / "fig1_calibration.png")
plt.close(fig)

# Fig 2: PhenoAge gap, binned log HR vs piecewise fit
ph = pd.read_parquet(root / "evidence/derived/nhanes_phenoage.parquet")
ph["male"] = (ph.sex == 1).astype(int)
edges = [-1000, -10, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10, 15, 1000]
ph["bin"] = pd.cut(ph.gap, edges, labels=False).astype(int)
refbin = int(ph.loc[ph.gap.between(-2.5, 0), "bin"].iloc[0])
dm = pd.get_dummies(ph["bin"], prefix="b").astype(float).drop(columns=f"b_{refbin}")
cph = CoxPHFitter().fit(pd.concat([ph[["years", "died", "age", "male"]], dm], axis=1), "years", "died")
s = cph.summary
mids = ph.groupby("bin").gap.mean()
xs, ys, es = [], [], []
for k in sorted(mids.index):
    xs.append(mids[k])
    if k == refbin:
        ys.append(0.0); es.append(0.0)
    else:
        ys.append(s.loc[f"b_{k}", "coef"]); es.append(1.96 * s.loc[f"b_{k}", "se(coef)"])
g = cal["calibration"]["gap"]
def pw_fn(x):
    k0, k1 = g["knots"]; a, m, c = g["slopes"]
    return m * k0 + a * (x - k0) if x < k0 else (m * k1 + c * (x - k1) if x > k1 else m * x)
base = pw_fn(mids[refbin])
xx = np.linspace(min(xs), max(xs), 200)
fig, ax = plt.subplots(figsize=(5.4, 4.2))
ax.errorbar(xs, ys, yerr=es, fmt="o", color=BLUE, ecolor="#9cc0ec", capsize=3, label="分组 Cox 估计（95% CI）")
ax.plot(xx, [pw_fn(x) - base for x in xx], color=RED, lw=1.6, label="分段线性校准（拐点 −5、+5）")
ax.plot(xx, [0.0975 * (x - mids[refbin]) for x in xx], ":", color=GREY, lw=1.2, label="若 1 个 PhenoAge 年 = 1 年真实年龄")
ax.set_xlabel("PhenoAge 差值（岁）")
ax.set_ylabel("对数风险比（调整年龄、性别）")
ax.set_title("图 2  PhenoAge 差值与全因死亡（NHANES，6,527 例死亡）", fontsize=10)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(fig_dir / "fig2_phenoage_gap.png")
plt.close(fig)

# Fig 3: China hazards with old-age extension; scenario survival for a 38-year-old man
fig, axs = plt.subplots(1, 2, figsize=(10, 4))
t = json.loads((root / "skills/longpi-report/data/lifetable_china_wpp2024.json").read_text())
for sex, col in (("M", BLUE), ("F", RED)):
    r = M.Reference(sex)
    xs_ = list(range(30, 121))
    axs[0].semilogy(xs_, [r.mu_period(x, 2026) for x in xs_], color=col, lw=1.6, label=("男" if sex == "M" else "女") + "（模型）")
    axs[0].semilogy(list(range(30, 100)), t["mx"][sex]["2026"][30:100], "o", ms=2.2, color=col, alpha=.5, label=("男" if sex == "M" else "女") + "（WPP 2024 原值）")
axs[0].axhline(0.7, color=GREY, ls="--", lw=1)
axs[0].text(31, 0.75, "超百岁老人死亡率平台 0.70/年", fontsize=8, color=GREY)
axs[0].set_xlabel("年龄"); axs[0].set_ylabel("年死亡率（对数）"); axs[0].legend(frameon=False, fontsize=7)
axs[0].set_title("图 3a  2026 年中国死亡率与 96 岁以上外推", fontsize=10)
r = M.Reference("M")
for sk, sc, col in (("S1 当前医学", {"kind": "period"}, GREY), ("S2 趋势延续", {"kind": "wpp"}, BLUE),
                    ("S3 衰老干预突破", {"kind": "wpp_slowed", "start_year": 2045, "ramp_years": 20, "slope_reduction": 0.2, "pivot_age": 50}, RED)):
    s_ = M.survival_from(M.cohort_hazards(r, 38.0, 2026, sc), 38.0)
    a_ = M.survival_ages(38.0, len(s_))
    axs[1].plot(a_, [v * 100 for v in s_], color=col, lw=1.6, label=f"{sk}（期望寿命 {M.life_expectancy(a_, s_):.1f}）")
axs[1].set_xlim(38, 120); axs[1].set_xlabel("年龄"); axs[1].set_ylabel("从 38 岁起活到该年龄的概率（%）")
axs[1].legend(frameon=False, fontsize=8); axs[1].set_title("图 3b  38 岁中国男性在三种情景下的生存曲线", fontsize=10)
fig.tight_layout(); fig.savefig(fig_dir / "fig3_mortality.png"); plt.close(fig)

# Fig 4: history of mortality improvement
h = pd.read_csv(res_dir / "scenario_history_windows.csv")
hist = json.loads((res_dir / "scenario_history.json").read_text())
fig, ax = plt.subplots(figsize=(5.6, 3.8))
ax.hist(h.r60_89 * 100, bins=40, color="#9cc0ec", edgecolor="white")
for v, lab, col in ((0.0, "S1：不再下降", GREY), (hist["china"]["M"]["2026_2050_r60_89"] * 100, "S2：WPP 中国男性 2026–2050", BLUE)):
    ax.axvline(v, color=col, lw=1.6)
    ax.text(v + 0.05, ax.get_ylim()[1] * 0.9, lab, fontsize=8, color=col)
ax.set_xlabel("60–89 岁死亡率年均下降速度（%/年，20 年窗口）")
ax.set_ylabel("窗口数")
ax.set_title("图 4  1970–2019 年 28 个死亡登记完整国家/地区", fontsize=10)
fig.tight_layout(); fig.savefig(fig_dir / "fig4_history.png"); plt.close(fig)

# Fig 5: index vs R, frailty vs proportional hazards (S2, plateau 0.7)
fig, ax = plt.subplots(figsize=(5.4, 4.0))
ref = M.Reference("M")
s_ = M.survival_from(M.cohort_hazards(ref, 40.0, 2026, {"kind": "wpp"}), 40.0)
a_ = M.survival_ages(40.0, len(s_))
pr = M.at_age(a_, s_, 120)
RR = np.linspace(0.5, 2.0, 60)
for s2, col, lab in ((0.10, "#9cc0ec", "脆弱性 s²=0.10"), (0.16, BLUE, "脆弱性 s²=0.16（采用）"), (0.22, "#1a4f8f", "脆弱性 s²=0.22"), (0.001, RED, "比例风险（风险比一直不变）")):
    ax.plot(RR, [100 + 10 * math.log10(max(M.at_age(a_, M.individual_survival(s_, R, s2), 120), 1e-300) / pr) for R in RR], color=col, lw=1.6, label=lab)
ax.axhline(100, color=GREY, lw=.8, ls=":"); ax.axvline(1, color=GREY, lw=.8, ls=":")
ax.set_xscale("log"); ax.set_xticks([0.5, 0.75, 1, 1.5, 2]); ax.set_xticklabels(["0.5", "0.75", "1", "1.5", "2"])
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_xlabel("相对同龄人的死亡风险倍数 R（40 岁男性）"); ax.set_ylabel("120 指数（趋势延续情景）")
ax.set_title("图 5  120 指数对极高龄假设的敏感性", fontsize=10)
ax.legend(frameon=False, fontsize=8); fig.tight_layout(); fig.savefig(fig_dir / "fig5_index_sensitivity.png"); plt.close(fig)

# Fig 6: transport slopes per domain
q1 = cal["q1_transport"]
names = {"crf": "心肺适能", "muscle": "握力", "rhr": "静息心率", "sleep": "睡眠", "bp": "血压", "lipid": "LDL-C", "glucose": "血糖", "adiposity": "BMI", "smoking": "吸烟"}
keys = [k for k in names if k in q1]
fig, ax = plt.subplots(figsize=(6.2, 4.2))
for i, k in enumerate(keys):
    v = q1[k]
    ax.errorbar(v["slope"], i + 0.12, xerr=[[v["slope"] - v["lo"]], [v["hi"] - v["slope"]]], fmt="o", color=GREY, capsize=2, ms=4)
    if "slope_adj_phenoage" in v:
        ax.errorbar(v["slope_adj_phenoage"], i - 0.12, xerr=[[v["slope_adj_phenoage"] - v["lo_adj"]], [v["hi_adj"] - v["slope_adj_phenoage"]]],
                    fmt="s", color=BLUE, capsize=2, ms=4)
ax.axvline(1, color=RED, lw=1, ls="--"); ax.axvline(0, color=GREY, lw=.8)
ax.set_yticks(range(len(keys))); ax.set_yticklabels([names[k] for k in keys])
ax.set_xlabel("文献剂量反应在 NHANES 中的斜率（1 = 完全成立）")
ax.plot([], [], "o", color=GREY, label="调整年龄、性别"); ax.plot([], [], "s", color=BLUE, label="再调整 PhenoAge")
ax.legend(frameon=False, fontsize=8, loc="lower right"); ax.set_title("图 6  各领域文献效应在独立人群中的可迁移性", fontsize=10)
fig.tight_layout(); fig.savefig(fig_dir / "fig6_transport.png"); plt.close(fig)

print(json.dumps({k: v for k, v in out.items() if k not in ("index_sensitivity", "age_equivalence_check")}, indent=1, ensure_ascii=False))
print("age equivalence max diff", out["age_equivalence_check"]["max_abs_diff"])
print("index R=1.25 range under frailty", out["index_R125_range_frailty"], "under PH", out["index_R125_range_PH"])
print(sorted(p.name for p in fig_dir.glob("*.png")))
