"""Reference mortality for China and individual survival under three scenarios.

Reference hazards are the UN World Population Prospects 2024 single-age central
death rates for China (estimates to 2023, medium-variant projections 2024-2100).
From age 96 the WPP rates are replaced by a gamma-Gompertz curve fitted to WPP ages
60-94 whose asymptote is the hazard plateau seen in validated supercentenarian data
(ages 92-95 blend the two on the log scale).

Individual survival uses the gamma-frailty identity. If frailty Z is gamma with
mean 1 and variance s2 among people alive at the start age, and a person's
observed risk multiplies their frailty by R, then with S_ref the reference
cohort survival from the start age

    S_R(x) = (1 + R * (S_ref(x) ** -s2 - 1)) ** (-1 / s2)

which equals S_ref when R = 1, gives hazard ratio R at the start age, and makes
the hazard ratio drift toward 1 at extreme ages, where only the most robust are
left. The identity needs no parametric baseline: any reference cohort path
(frozen period rates or projected improvement) can be used.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MAX_AGE = 130


@lru_cache(maxsize=1)
def _table() -> dict:
    return json.loads((DATA_DIR / "lifetable_china_wpp2024.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def model_params() -> dict:
    return json.loads((DATA_DIR / "params.json").read_text(encoding="utf-8"))


def _sex(sex: str) -> str:
    s = sex.strip().upper()[:1]
    if s not in ("M", "F"):
        raise ValueError(f"sex must be M or F, got {sex!r}")
    return s


class Reference:
    """Reference (population) hazards mu(age, year) for one sex."""

    def __init__(self, sex: str, plateau: Optional[float] = None):
        self.sex = _sex(sex)
        t = _table()
        self.years: List[int] = [int(y) for y in t["years"]]
        self.y0, self.y1 = min(self.years), max(self.years)
        self._mx: Dict[int, List[float]] = {int(y): v for y, v in t["mx"][self.sex].items()}
        p = model_params()["old_age"]
        self.plateau = plateau if plateau is not None else p["plateau_hazard"]["value"]
        self.fit_ages = tuple(p["fit_ages"])
        self.blend = tuple(p.get("blend_ages", [91, 96]))
        self._old: Dict[int, tuple] = {}
        # Long-run improvement used after 2100: mean annual log change 2090-2100, by age.
        a, b = self._mx[2090], self._mx[2100]
        self._r_after = [math.log(b[x] / a[x]) / 10.0 if a[x] > 0 and b[x] > 0 else 0.0 for x in range(101)]

    # -- old-age extension -------------------------------------------------
    def _old_fit(self, year: int) -> tuple:
        """Gamma-Gompertz fit mu(x) = a e^{b(x-80)} / (1 + (a s2 / b)(e^{b(x-80)} - 1)), s2 = b/plateau.

        Fitted by least squares on log mu over fit_ages of the given year's WPP rates.
        Returns (a, b, s2).
        """
        if year in self._old:
            return self._old[year]
        mx = self._mx[year]
        ages = range(self.fit_ages[0], self.fit_ages[1] + 1)
        L = self.plateau

        def sse(a: float, b: float) -> float:
            s2 = b / L
            tot = 0.0
            for x in ages:
                e = math.exp(b * (x - 80))
                m = a * e / (1 + (a * s2 / b) * (e - 1))
                tot += (math.log(m) - math.log(mx[x])) ** 2
            return tot

        # coarse grid over (a, b), then coordinate descent with halving steps
        best = (float("inf"), 0.05, 0.1)
        for bi in range(40, 181, 4):
            b = bi / 1000.0
            for ai in range(1, 400):
                a = mx[80] * ai / 100.0
                v = sse(a, b)
                if v < best[0]:
                    best = (v, a, b)
        _, a, b = best
        step_a, step_b = a * 0.05, 0.002
        for _ in range(60):
            improved = False
            for da, db in ((step_a, 0), (-step_a, 0), (0, step_b), (0, -step_b)):
                na, nb = a + da, b + db
                if na <= 0 or nb <= 0.01:
                    continue
                v = sse(na, nb)
                if v < best[0]:
                    best, a, b, improved = (v, na, nb), na, nb, True
            if not improved:
                step_a *= 0.5
                step_b *= 0.5
        res = (a, b, b / L)
        self._old[year] = res
        return res

    def old_age_s2(self, year: Optional[int] = None) -> float:
        """Frailty variance implied by the old-age fit (b / plateau)."""
        return self._old_fit(self._clamp(year or 2026))[2]

    def _clamp(self, year: int) -> int:
        return min(max(int(year), self.y0), self.y1)

    # -- hazards -------------------------------------------------------------
    def _old_mu(self, age: float, yr: int) -> float:
        a, b, s2 = self._old_fit(yr)
        e = math.exp(b * (age - 80))
        return a * e / (1 + (a * s2 / b) * (e - 1))

    def mu_period(self, age: int, year: int) -> float:
        """Hazard at integer age in a calendar year.

        Ages <= 91: WPP 2024. Ages >= 96: gamma-Gompertz curve fitted to WPP ages
        60-94 with its asymptote fixed at the supercentenarian plateau. Ages 92-95
        blend the two on the log scale. After 2100 the 2090-2100 pace continues.
        """
        yr = self._clamp(year)
        lo, hi = self.blend
        if age <= lo:
            m = self._mx[yr][age]
        elif age >= hi:
            m = self._old_mu(age, yr)
        else:
            w = (age - lo) / (hi - lo)
            m = math.exp((1 - w) * math.log(self._mx[yr][age]) + w * math.log(self._old_mu(age, yr)))
        if year > self.y1:
            m *= math.exp(self._r_after[min(age, 100)] * (year - self.y1))
        return m

    def mu_at(self, age: float, year: int) -> float:
        """Hazard at a fractional age (log-linear between single ages)."""
        a0 = int(math.floor(age))
        w = age - a0
        if w == 0:
            return self.mu_period(a0, year)
        return math.exp((1 - w) * math.log(self.mu_period(a0, year)) + w * math.log(self.mu_period(min(a0 + 1, MAX_AGE), year)))

    def gompertz_slope(self, year: int, ages: Sequence[int] = (35, 90)) -> float:
        """Least-squares slope of log mu on age (the rate of ageing b) for one period."""
        xs = list(range(ages[0], ages[1] + 1))
        ys = [math.log(self.mu_period(x, year)) for x in xs]
        mx_, my = sum(xs) / len(xs), sum(ys) / len(ys)
        return sum((x - mx_) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx_) ** 2 for x in xs)


# -- scenarios ---------------------------------------------------------------

def cohort_hazards(ref: Reference, age0: float, year0: float, scenario: dict) -> List[float]:
    """Annual hazards for single years of age floor(age0)..MAX_AGE along the cohort path.

    scenario kinds:
      period      rates frozen at year0 (current medicine)
      wpp         WPP 2024 medium projection, continued after 2100 at the 2090-2100 pace
      wpp_slowed  wpp, with the age slope above `pivot_age` reduced by `slope_reduction`,
                  phased in over `ramp_years` from `start_year` (delayed ageing)
      wpp_plus    wpp until `start_year`, then an extra annual decline `extra_rate` at ages >= `min_age`
    """
    kind = scenario["kind"]
    a0 = int(math.floor(age0))
    out = []
    for x in range(a0, MAX_AGE + 1):
        yr = int(round(year0 + (x - age0)))
        if kind == "period":
            m = ref.mu_period(x, int(year0))
        elif kind == "wpp":
            m = ref.mu_period(x, yr)
        elif kind == "wpp_plus":
            m = ref.mu_period(x, yr)
            if yr > scenario["start_year"] and x >= scenario.get("min_age", 0):
                m *= (1 - scenario["extra_rate"]) ** (yr - scenario["start_year"])
        elif kind == "wpp_slowed":
            # delayed ageing (Goldman et al. 2013): the slope of mortality with age above
            # `pivot_age` falls by `slope_reduction`, phased in over `ramp_years` from `start_year`
            pv = scenario["pivot_age"]
            frac = min(1.0, max(0.0, (yr - scenario["start_year"]) / scenario["ramp_years"]))
            d = scenario["slope_reduction"] * frac
            xe = x if x <= pv else pv + (x - pv) * (1 - d)
            m = ref.mu_at(xe, yr)
        else:
            raise ValueError(f"unknown scenario kind {kind}")
        out.append(m)
    return out


def survival_from(hazards: Sequence[float], age0: float) -> List[float]:
    """Survival at age0, floor(age0)+1, ..., MAX_AGE given annual hazards from floor(age0); S(age0) = 1."""
    frac = age0 - math.floor(age0)
    cur = math.exp(-hazards[0] * (1 - frac))
    out = [1.0, cur]
    for h in hazards[1:-1]:
        cur *= math.exp(-h)
        out.append(cur)
    return out


def individual_survival(s_ref: Sequence[float], R: float, s2: float) -> List[float]:
    """Gamma-frailty survival of a person whose hazard is R x the reference at the start age."""
    out = []
    for s in s_ref:
        if s <= 0:
            out.append(0.0)
            continue
        q = s ** (-s2)
        out.append((1 + R * (q - 1)) ** (-1 / s2))
    return out


def survival_ages(age0: float, n: int) -> List[float]:
    a0 = int(math.floor(age0))
    return [age0] + [float(a0 + 1 + i) for i in range(n - 1)]


def at_age(ages: Sequence[float], surv: Sequence[float], target: float) -> float:
    """Survival probability to exact age `target` (log-linear interpolation)."""
    if target <= ages[0]:
        return 1.0
    for i in range(1, len(ages)):
        if ages[i] >= target:
            a, b = ages[i - 1], ages[i]
            sa, sb = surv[i - 1], surv[i]
            if sa <= 0 or sb <= 0:
                return max(sb, 0.0)
            w = (target - a) / (b - a)
            return math.exp(math.log(sa) * (1 - w) + math.log(sb) * w)
    return surv[-1]


def life_expectancy(ages: Sequence[float], surv: Sequence[float]) -> float:
    """Expected age at death: age0 + area under the survival curve (trapezoid)."""
    area = 0.0
    for i in range(1, len(ages)):
        area += (ages[i] - ages[i - 1]) * (surv[i] + surv[i - 1]) / 2
    return ages[0] + area
