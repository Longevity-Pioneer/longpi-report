#!/usr/bin/env python3
"""Build-time: flatten the organage (Oh et al. 2023 Nature, MIT licence) bootstrap Lasso models into JSON.

The organage package stores, per organ, 500 bootstrapped sklearn Lasso models, a StandardScaler for the
log10 RFU proteins, a StandardScaler for the age gap and a scipy interp1d (lowess of predicted vs
chronological age in the training cohort). Because every Lasso is linear, the bootstrap mean prediction
equals one linear model with averaged coefficients and intercept. We extract those numbers WITHOUT
executing pickled code: a restricted Unpickler that only maps a fixed whitelist of globals to inert stubs.

usage: build_organage_coefs.py <organage-main checkout> <out_dir>
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np

ORGANS = ["Adipose", "Artery", "Brain", "Heart", "Immune", "Intestine", "Kidney", "Liver", "Lung",
          "Muscle", "Pancreas", "Organismal", "Conventional"]
NORM = "Zprot_stableassayps_perf95"


class Stub:
    def __init__(self, *a, **k):
        self._args = a

    def __setstate__(self, state):
        if isinstance(state, tuple) and len(state) == 2 and all(isinstance(x, (dict, type(None))) for x in state):
            for part in state:  # (dict state, slot state)
                self.__dict__.update(part or {})
        elif isinstance(state, dict):
            self.__dict__.update(state)
        else:
            self.__dict__["_state"] = state


def _create_array(f, args, state, npdict=None):
    arr = f(*args)
    arr.__setstate__(state)
    if npdict is not None:
        arr.__dict__.update(npdict)
    return arr


ALLOWED = {
    ("numpy.core.multiarray", "_reconstruct"): np.core.multiarray._reconstruct,
    ("numpy._core.multiarray", "_reconstruct"): np.core.multiarray._reconstruct,
    ("numpy.core.multiarray", "scalar"): np.core.multiarray.scalar,
    ("numpy._core.multiarray", "scalar"): np.core.multiarray.scalar,
    ("numpy", "ndarray"): np.ndarray,
    ("numpy", "dtype"): np.dtype,
    ("numpy", "float64"): np.float64,
    ("numpy", "int64"): np.int64,
    ("dill._dill", "_create_array"): _create_array,
    ("sklearn.linear_model._coordinate_descent", "Lasso"): Stub,
    ("sklearn.preprocessing._data", "StandardScaler"): Stub,
    ("scipy.interpolate._interpolate", "interp1d"): Stub,
    ("scipy.interpolate.interpolate", "interp1d"): Stub,
}


class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        key = (module, name)
        if key in ALLOWED:
            return ALLOWED[key]
        if module.startswith("scipy.interpolate") and name.startswith("interp1d."):
            return None  # bound-method reference (_call_linear); not needed
        if module == "dill._dill" and name == "_load_type":
            return lambda n: {"float64": np.float64, "int64": np.int64}.get(n, object)
        raise pickle.UnpicklingError(f"global {module}.{name} not allowed")


def load(path: Path):
    with open(path, "rb") as fh:
        return SafeUnpickler(fh).load()


def dedupe_lowess(x, y):
    """interp1d(kind=linear) over the training ages; duplicate ages carry identical fitted values."""
    pts = {}
    for a, b in zip(np.asarray(x, dtype=float), np.asarray(y, dtype=float)):
        if a in pts:
            assert abs(pts[a] - b) < 1e-9, (a, pts[a], b)
        else:
            pts[a] = float(b)
    xs = sorted(pts)
    return {"x": [float(a) for a in xs], "y": [pts[a] for a in xs], "kind": "linear", "extrapolate": True}


def main(src: str, out: str):
    data = Path(src) / "src" / "organage" / "data"
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    plist = json.load(open(data / "tissue_pproteinlist_5k_dict_gtex_tissue_enriched_fc4_stable_assay_proteins_seqid.json"))
    seeds = json.load(open(data / "Bootstrap_and_permutation_500_seed_dict.json"))["BS_Seed"]
    v4 = json.load(open(data / "v4_to_v4.1_scale_dict.json"))
    v5 = json.load(open(data / "v5_to_v4.1_scale_dict.json"))
    models = {}
    for organ in ORGANS:
        d = data / "ml_models" / "KADRC" / NORM / organ
        prots = plist[organ]
        ps = load(d / f"KADRC_HC_based_{organ}_protein_zscore_scaler.pkl")
        gs = load(d / f"KADRC_HC_{NORM}_lasso_{organ}_agegap_zscore_scaler.pkl")
        lw = load(d / f"KADRC_HC_{NORM}_lasso_{organ}_age_prediction_lowess.dill")
        coefs, icpts = [], []
        for s in seeds:
            m = load(d / f"KADRC_HC_{NORM}_lasso_{organ}_seed{s}_aging_model.pkl")
            coefs.append(np.asarray(m.coef_, dtype=float))
            icpts.append(float(np.asarray(m.intercept_).ravel()[0]) if np.ndim(m.intercept_) else float(m.intercept_))
        C = np.vstack(coefs)
        assert C.shape[1] == len(prots) + 1, (organ, C.shape, len(prots))
        mc = C.mean(axis=0)
        keep = [i for i in range(len(prots)) if mc[i + 1] != 0.0]
        models[organ] = {
            "n_bootstrap": len(seeds),
            "intercept": float(np.mean(icpts)),
            "coef_sex_f": float(mc[0]),
            "proteins": [{"seqid": prots[i], "coef": float(mc[i + 1]), "mean": float(ps.mean_[i]),
                          "scale": float(ps.scale_[i])} for i in keep],
            "n_proteins_model": len(prots),
            "lowess": dedupe_lowess(lw.x, np.asarray(lw._y).ravel()),
            "agegap_scaler": {"mean": float(gs.mean_[0]), "scale": float(gs.scale_[0])},
        }
        print(organ, len(prots), "->", len(keep), "nonzero; lowess points", len(lw.x), "->", len(models[organ]["lowess"]["x"]))
    needed = sorted({p["seqid"] for m in models.values() for p in m["proteins"]})
    doc = {
        "source": "organage (Oh HS-H, Rutledge J et al. Nature 2023;624:164-172), MIT licence, Copyright (c) 2023 Hamilton Oh",
        "models": NORM + " (organ-enriched proteins, KADRC healthy-control training; bootstrap Lasso x500 averaged)",
        "input": "SomaScan ANML-normalised RFU; v4.1 native; v4 and v5 rescaled to v4.1 with the package's per-SeqId factors; log10; z-score",
        "scale_v4_to_v41": {k: v4[k] for k in needed if k in v4},
        "scale_v5_to_v41": {k: v5[k] for k in needed if k in v5},
        "organs": models,
    }
    (out / "organage_somascan.json").write_text(json.dumps(doc, separators=(",", ":"), sort_keys=True))
    print("wrote", out / "organage_somascan.json", (out / "organage_somascan.json").stat().st_size)


if __name__ == "__main__":
    main(*sys.argv[1:3])
