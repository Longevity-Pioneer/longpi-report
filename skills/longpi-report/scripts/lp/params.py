"""The one place parameters are loaded: data/params.json (global settings) + the registry's core terms.

`load()` returns the parameter dict in the 1.1.1 shape (domains, calibration, methylation, clock_residual included),
so every model formula reads exactly what it read before the move to the registry.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import registry as RG

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@lru_cache(maxsize=1)
def raw() -> dict:
    return json.loads((DATA_DIR / "params.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load() -> dict:
    return RG.classic_params(raw(), RG.load())
