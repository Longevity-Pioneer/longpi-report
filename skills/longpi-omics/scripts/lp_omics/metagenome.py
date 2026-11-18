"""Gut species abundance table -> GMHI (Gupta 2020) and species-level Shannon diversity.

Accepts MetaPhlAn-style tables (merged `clade_name` x samples, a single-sample MetaPhlAn output, or
GMHI-style `s__` rows). 16S / amplicon tables (SILVA `D_0__`, `d__...;`, Greengenes `k__Bacteria; p__`,
ASV/OTU ids, genus-level resolution) are recognised and NOT scored: GMHI is defined on shotgun
species-level MetaPhlAn2 profiles.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from . import common, tables

VERSION = "0.1.0"
MIN_READS = 1_000_000  # refuse scoring when the user-supplied read depth is below this
ASV = re.compile(r"^[0-9a-f]{32}$")


def add_arguments(p):
    p.add_argument("table", help="species abundance table (MetaPhlAn style)")
    p.add_argument("--sample", default=None, help="sample column when several are present")
    p.add_argument("--reads", type=int, default=None, help="sequencing depth (reads) from the lab report, if known")
    p.add_argument("--antibiotics-3m", action="store_true", help="antibiotics within the last 3 months (flag)")
    p.add_argument("--specimen", default="stool")


def load_gmhi() -> dict:
    return common.load_json(common.DATA_DIR / "metagenome" / "gmhi_gupta2020.json")


def detect_kind(names: list[str]) -> dict:
    n = len(names) or 1
    joined = names[:2000]
    amplicon_markers = sum(1 for x in joined if x.startswith("D_0__") or re.match(r"^d__\w+;", x)
                           or "; p__" in x or "; g__" in x or ASV.match(x) or x.lower().startswith(("otu", "asv")))
    pipe = sum(1 for x in joined if "|" in x and x.startswith("k__"))
    species = sum(1 for x in joined if re.search(r"(^|\|)s__[^|;]+$", x))
    genus_only = sum(1 for x in joined if re.search(r"(^|[|;] ?)g__[^|;]+$", x))
    if amplicon_markers > 0.2 * n:
        return {"kind": "16S/amplicon", "reason": "SILVA/Greengenes/ASV identifiers"}
    if species == 0 and genus_only > 0:
        return {"kind": "16S/amplicon", "reason": "genus-level resolution only"}
    if species == 0:
        return {"kind": "unknown", "reason": "no species-level (s__) rows"}
    return {"kind": "shotgun", "reason": "MetaPhlAn lineage" if pipe else "species (s__) rows"}


def read_profile(path: str, sample: str | None) -> tuple[dict, dict]:
    header, rows = tables.read_table(path)
    low = [h.lower() for h in header]
    if "relative_abundance" in low:
        col = low.index("relative_abundance")
    else:
        skip = 2 if len(low) > 2 and low[1] in ("ncbi_tax_id", "clade_taxid", "taxid") else 1
        col = tables.pick_column(header, sample, skip=skip)
    names = [r[0] for r in rows]
    kind = detect_kind(names)
    species = {}
    for r in rows:
        name = r[0]
        if "|t__" in name:
            continue
        m = re.search(r"(?:^|\|)(s__[^|]+)$", name)
        if not m:
            continue
        v = tables.num(r[col])
        if v is None:
            continue
        if v < 0:
            raise ValueError(f"negative abundance for {m.group(1)}")
        species[m.group(1)] = species.get(m.group(1), 0.0) + v
    return species, kind


def clr(values: dict, pseudocount: float | None = None) -> dict:
    """Centred log-ratio. Pseudocount defaults to half the smallest non-zero value (documented choice)."""
    nz = [v for v in values.values() if v > 0]
    if not nz:
        raise ValueError("all abundances are zero")
    pc = pseudocount if pseudocount is not None else min(nz) / 2
    logs = {k: math.log(v + pc) for k, v in values.items()}
    g = sum(logs.values()) / len(logs)
    return {k: x - g for k, x in logs.items()}


def gmhi(species: dict, ref: dict) -> dict:
    keep = {k: v for k, v in species.items() if not any(s in k for s in ref["exclude_substrings"])}
    total = sum(keep.values())
    if total <= 0:
        raise ValueError("no classified species abundance")
    p = {k: v / total for k, v in keep.items()}
    p = {k: (0.0 if v < ref["abundance_floor"] else v) for k, v in p.items()}
    mh = [p.get(s, 0.0) for s in ref["health_prevalent_MH"]]
    mn = [p.get(s, 0.0) for s in ref["health_scarce_MN"]]

    def sh(xs):
        return -sum(x * math.log(x) for x in xs if x > 0)

    r_mh, r_mn = sum(1 for x in mh if x > 0), sum(1 for x in mn if x > 0)
    psi_mh = (r_mh / ref["MH_prime"]) * sh(mh)
    psi_mn = (r_mn / ref["MN_prime"]) * sh(mn)
    val = math.log10((psi_mh + ref["pseudocount"]) / (psi_mn + ref["pseudocount"]))
    return {"gmhi": val, "R_MH": r_mh, "R_MN": r_mn, "psi_MH": psi_mh, "psi_MN": psi_mn}


def shannon(species: dict) -> float:
    keep = {k: v for k, v in species.items() if "unclassified" not in k and v > 0}
    tot = sum(keep.values())
    return -sum((v / tot) * math.log(v / tot) for v in (keep[k] for k in sorted(keep)))


def run(args) -> dict:
    species, kind = read_profile(args.table, args.sample)
    src = Path(args.table).name
    ref = load_gmhi()
    qc = {"input_kind": kind, "n_species": len(species), "reads": args.reads,
          "abundance_sum": common.r(sum(species.values()), 4)}
    obs, summary = [], [f"metagenome: {kind['kind']} ({kind['reason']}), {len(species)} species"]
    flags = ["antibiotics_3m"] if args.antibiotics_3m else []
    skipped = None
    if kind["kind"] != "shotgun":
        skipped = f"not scored: input recognised as {kind['kind']} ({kind['reason']}); GMHI needs shotgun species profiles"
    elif args.reads is not None and args.reads < MIN_READS:
        skipped = f"not scored: read depth {args.reads} < {MIN_READS}"
    elif not species:
        skipped = "not scored: no species rows"
    if args.reads is None:
        qc["depth_note"] = "read depth unknown (relative abundances only); depth check not possible"
    prov = []
    if skipped:
        summary.append("  " + skipped)
        prov.append({"step": "metagenome", "tool": "micro_gmhi2020", "version": VERSION, "skipped": skipped, "qc": qc})
    else:
        g = gmhi(species, ref)
        h = shannon(species)
        kw = dict(tool="micro_gmhi2020", platform="shotgun metagenome (MetaPhlAn species profile)",
                  specimen=args.specimen, source_file=src, datetime=args.date, flags=flags)
        o = common.make_obs("LP:micro.gmhi", common.r(g["gmhi"], 4), unit="index", **kw)
        o["detail"] = {"R_MH": g["R_MH"], "R_MN": g["R_MN"]}
        obs.append(o)
        kw["tool"] = "micro_shannon"
        obs.append(common.make_obs("LP:micro.shannon", common.r(h, 4), unit="nats", **kw))
        prov.append({"step": "metagenome.gmhi", "tool": "micro_gmhi2020", "version": VERSION,
                     "ref_data": {"species_lists": ref["source"]}, "qc": qc,
                     "params": {"abundance_floor": ref["abundance_floor"], "MH_prime": ref["MH_prime"],
                                "MN_prime": ref["MN_prime"]}})
        prov.append({"step": "metagenome.shannon", "tool": "micro_shannon", "version": VERSION,
                     "params": {"log": "natural", "level": "species", "excluded": "unclassified"}})
        summary.append(f"  GMHI {g['gmhi']:+.3f} (MH {g['R_MH']}/7, MN {g['R_MN']}/43); Shannon {h:.3f}")
    return {"tool_ids": ["micro_gmhi2020", "micro_shannon"], "observations": obs, "provenance": prov,
            "summary": summary}
