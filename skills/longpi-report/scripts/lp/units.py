"""Unit normalisation for the measurements LongPi reads.

Every analyte is converted to one canonical unit before any model sees it.
Chinese reports mostly use SI units; US-style units are accepted too. Analytes not listed
in CANONICAL (for example Lp(a), whose mass and molar units cannot be converted) keep
their reported value and unit.
"""
from __future__ import annotations

from typing import Optional

# canonical unit per analyte
CANONICAL = {
    "albumin": "g/L",
    "creatinine": "umol/L",
    "glucose": "mmol/L",
    "crp": "mg/L",
    "lymph_pct": "%",
    "mcv": "fL",
    "rdw": "%",
    "alp": "U/L",
    "wbc": "10^9/L",
    "ldl": "mmol/L",
    "hdl": "mmol/L",
    "tc": "mmol/L",
    "tg": "mmol/L",
    "apob": "g/L",
    "hba1c": "%",
    "alt": "U/L",
    "ast": "U/L",
    "ggt": "U/L",
    "platelets": "10^9/L",
    "uric_acid": "umol/L",
    "vitd": "ng/mL",
    "cystatin_c": "mg/L",
    "uacr": "mg/g",
}

_ALIASES = {
    "umol/l": "umol/L", "μmol/l": "umol/L", "µmol/l": "umol/L",
    "mmol/l": "mmol/L", "mg/dl": "mg/dL", "mg/l": "mg/L", "g/l": "g/L", "g/dl": "g/dL",
    "fl": "fL", "%": "%", "u/l": "U/L", "iu/l": "U/L", "10^9/l": "10^9/L", "10*9/l": "10^9/L",
    "x10^9/l": "10^9/L", "×10^9/l": "10^9/L", "10⁹/l": "10^9/L", "×10⁹/l": "10^9/L", "x10⁹/l": "10^9/L",
    "10^3/ul": "10^9/L", "k/ul": "10^9/L", "10^3/μl": "10^9/L", "×10^3/μl": "10^9/L",
    "nmol/l": "nmol/L", "ng/ml": "ng/mL", "mg/g": "mg/g", "mg/mmol": "mg/mmol",
    "mmol/mol": "mmol/mol",
}

# multiply value in `from` unit by factor to get canonical unit
_FACTORS = {
    ("albumin", "g/dL"): 10.0,
    ("creatinine", "mg/dL"): 88.4,
    ("glucose", "mg/dL"): 1 / 18.016,
    ("crp", "mg/dL"): 10.0,
    ("ldl", "mg/dL"): 0.02586,
    ("hdl", "mg/dL"): 0.02586,
    ("tc", "mg/dL"): 0.02586,
    ("tg", "mg/dL"): 0.01129,
    ("apob", "mg/dL"): 0.01,
    ("uric_acid", "mg/dL"): 59.48,
    ("vitd", "nmol/L"): 1 / 2.496,
    ("uacr", "mg/mmol"): 8.84,
}


def norm_unit(unit: Optional[str]) -> str:
    if unit is None:
        return ""
    u = unit.strip().replace(" ", "")
    return _ALIASES.get(u.lower(), u)


def to_canonical(analyte: str, value: float, unit: Optional[str]) -> float:
    """Convert one value to the canonical unit of `analyte`. Raises on unknown units."""
    if analyte not in CANONICAL:
        return value
    u = norm_unit(unit) or CANONICAL[analyte]
    can = CANONICAL[analyte]
    if u == can:
        return value
    if analyte == "hba1c" and u == "mmol/mol":  # IFCC -> NGSP
        return value / 10.929 + 2.15
    f = _FACTORS.get((analyte, u))
    if f is None:
        raise ValueError(f"cannot convert {analyte} from {unit!r} to {can}")
    return value * f
