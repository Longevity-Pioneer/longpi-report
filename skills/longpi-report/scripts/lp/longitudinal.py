"""Generic state-space filter for any term's time series (PRD §4.4).

Local linear trend:  level_t = level_{t-1} + slope * dt + w_level,  slope_t = slope_{t-1} + w_slope,
observation y_t = level_t + e_t with e_t ~ N(0, r_t) (analytical error + within-person biological variation).
The 1.1.1 PhenoAge filter (lp.clock.kalman_gap) is the local-level special case; it is kept as is so the
1.1.1 numbers do not move. This module serves the new terms.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence


def _mm(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def _t(a):
    return [list(r) for r in zip(*a)]


def filter_series(times: Sequence[float], ys: Sequence[float], rs: Sequence[float], t_now: float,
                  prior_level: float, prior_level_sd: float, prior_slope_sd: float,
                  q_level: float, q_slope: float) -> Dict[str, float]:
    """Kalman filter + prediction to t_now. times in decimal years (sorted), rs = observation variances.

    Returns level, level_sd, slope, slope_sd at t_now, and the number of observations used."""
    x = [prior_level, 0.0]
    P = [[prior_level_sd ** 2, 0.0], [0.0, prior_slope_sd ** 2]]
    t_prev = times[0] if times else t_now
    for t, y, r in zip(times, ys, rs):
        dt = max(0.0, t - t_prev)
        F = [[1.0, dt], [0.0, 1.0]]
        x = [x[0] + dt * x[1], x[1]]
        P = _mm(_mm(F, P), _t(F))
        P[0][0] += q_level * dt
        P[1][1] += q_slope * dt
        s = max(P[0][0] + r, 1e-12)
        k0, k1 = P[0][0] / s, P[1][0] / s
        innov = y - x[0]
        x = [x[0] + k0 * innov, x[1] + k1 * innov]
        P = [[(1 - k0) * P[0][0], (1 - k0) * P[0][1]],
             [P[1][0] - k1 * P[0][0], P[1][1] - k1 * P[0][1]]]
        t_prev = t
    dt = max(0.0, t_now - t_prev)
    x = [x[0] + dt * x[1], x[1]]
    F = [[1.0, dt], [0.0, 1.0]]
    P = _mm(_mm(F, P), _t(F))
    P[0][0] += q_level * dt
    P[1][1] += q_slope * dt
    return {"level": x[0], "level_sd": math.sqrt(max(P[0][0], 0.0)), "slope": x[1],
            "slope_sd": math.sqrt(max(P[1][1], 0.0)), "n": len(times)}


def level_and_slope(rows: List[dict], meas_sd: List[float], t_now: float, ref_sd: float,
                    q_frac: float = 0.1, slope_frac: float = 0.1) -> Dict[str, Optional[float]]:
    """Rows: observations (value, decimal-year `t`). Single row: level = value, sd = measurement sd, no slope.

    Process noise and the slope prior scale with the population SD of the marker (defaults: level drifts
    0.1 SD per sqrt(year); slope prior 0.1 SD per year), so a slope is only reported when the data inform it."""
    if not rows:
        return {"level": None, "level_sd": None, "slope": None, "slope_sd": None, "n": 0, "slope_informed": False}
    floor = 1e-3 * max(ref_sd, 1e-9)                   # no zero-variance observation (avoids division by zero)
    meas_sd = [max(m, floor) for m in meas_sd]
    if len(rows) == 1:
        return {"level": float(rows[0]["value"]), "level_sd": meas_sd[0], "slope": None, "slope_sd": None, "n": 1,
                "slope_informed": False}
    s0 = slope_frac * ref_sd
    # diffuse prior on the level (10 population SDs) centred on the first value: the first observation is not
    # counted twice in any meaningful way
    out = filter_series([r["t"] for r in rows], [float(r["value"]) for r in rows], [s * s for s in meas_sd], t_now,
                        float(rows[0]["value"]), 10 * max(ref_sd, meas_sd[0]), s0, (q_frac * ref_sd) ** 2, (0.25 * s0) ** 2)
    out["slope_informed"] = out["slope_sd"] < 0.8 * s0
    return out
