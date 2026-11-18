"""Shared helpers for the LongPi omics layer.

- observations.json load / merge / deterministic write (schema longpi.observations/1)
- reference cache (env LONGPI_OMICS_REF, default ~/longpi/omics-ref)
- public-resource downloads with a privacy guard: only URLs on an allow-list of
  public reference hosts may be fetched, and no request ever carries a body.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "longpi.observations/1"
PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"
OMICS_VERSION = "0.1.0"

# Hosts that serve public reference resources only. Personal data is never sent:
# every request is a GET (or a range GET by htslib) of a fixed public URL.
PUBLIC_HOSTS = {
    "ftp.ebi.ac.uk",            # PGS Catalog scoring files
    "www.pgscatalog.org",
    "ftp.ncbi.nlm.nih.gov",     # ClinVar
    "ftp.1000genomes.ebi.ac.uk",  # 1000 Genomes genotypes / panels
    "hgdownload.soe.ucsc.edu",  # liftover chain files
    "faculty.washington.edu",   # Beagle jar / maps
    "bochet.gcc.biostat.washington.edu",
}


class PrivacyError(RuntimeError):
    pass


def ref_dir(*parts: str) -> Path:
    base = Path(os.environ.get("LONGPI_OMICS_REF", str(Path.home() / "longpi" / "omics-ref")))
    p = base.joinpath(*parts)
    p.mkdir(parents=True, exist_ok=True)
    return p


def check_public_url(url: str) -> None:
    u = urllib.parse.urlparse(url)
    if u.scheme not in ("https", "http"):
        raise PrivacyError(f"refusing non-http(s) url: {url}")
    if u.hostname not in PUBLIC_HOSTS:
        raise PrivacyError(f"refusing download from non-allow-listed host: {u.hostname}")
    if u.query:
        # Public resources are fixed paths; a query string could smuggle data.
        raise PrivacyError(f"refusing url with query string: {url}")


def download(url: str, dest: Path, *, force: bool = False) -> Path:
    """GET a public resource into the cache (atomic). Never sends a body."""
    check_public_url(url)
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "longpi-omics/" + OMICS_VERSION})
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as fh:
        shutil.copyfileobj(r, fh)
    os.replace(tmp, dest)
    return dest


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def open_text(path: Path | str):
    path = str(path)
    if path.endswith(".gz") or path.endswith(".bgz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "rt", encoding="utf-8", errors="replace")


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def data_file(name: str) -> Path:
    return DATA_DIR / name


# ---------------------------------------------------------------- observations

PRIORITY = {"lab": 0, "tool": 1, "vendor": 2, "device": 3, "self_report": 4}


def new_doc(person_code: str | None) -> dict:
    return {"schema": SCHEMA, "person_code": person_code, "observations": [], "provenance": []}


def load_doc(path: Path, person_code: str | None) -> dict:
    path = Path(path)
    if path.exists():
        doc = load_json(path)
        if doc.get("schema") != SCHEMA:
            raise ValueError(f"{path}: schema is {doc.get('schema')!r}, expected {SCHEMA}")
        if person_code and doc.get("person_code") and doc["person_code"] != person_code:
            raise ValueError(f"{path}: person_code {doc['person_code']!r} != {person_code!r}")
        if person_code:
            doc["person_code"] = person_code
        doc.setdefault("observations", [])
        doc.setdefault("provenance", [])
        return doc
    return new_doc(person_code)


def make_obs(code: str, value: Any, *, unit: str | None, method: str = "tool", tool: str,
             platform: str | None = None, specimen: str | None = None, source_file: str | None = None,
             source_locator: str | None = None, datetime: str | None = None, sd: float | None = None,
             flags: Iterable[str] = (), vendor_derived: bool = False, **extra) -> dict:
    o = {"obs_id": None, "code": code, "value": value, "unit": unit, "datetime": datetime,
         "method": method, "platform": platform, "specimen": specimen,
         "source_file": source_file, "source_locator": source_locator,
         "sd": sd, "flags": list(flags), "tool": tool, "vendor_derived": vendor_derived,
         "sustained_weeks": None}
    o.update(extra)
    return o


def merge(doc: dict, *, tool_ids: Iterable[str], observations: list[dict], provenance: list[dict],
          genetics: dict | None = None, extra_blocks: dict | None = None) -> dict:
    """Replace everything previously written by `tool_ids`, then append the new results.

    Re-running a subcommand is idempotent: its old observations and provenance are dropped.
    """
    tool_ids = set(tool_ids)
    keep = [o for o in doc["observations"] if o.get("tool") not in tool_ids]
    doc["observations"] = keep + observations
    doc["provenance"] = [p for p in doc["provenance"] if p.get("tool") not in tool_ids] + provenance
    if genetics is not None:
        g = doc.get("genetics") or {}
        g.update(genetics)
        doc["genetics"] = g
    for k, v in (extra_blocks or {}).items():
        doc[k] = v
    # deterministic ids: order of codes within the document
    for i, o in enumerate(doc["observations"], 1):
        o["obs_id"] = f"o{i}"
    return doc


def write_doc(doc: dict, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False, allow_nan=False) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def r(x: float | None, nd: int = 4):
    """Round for output so floating noise never breaks byte-identical reruns."""
    if x is None:
        return None
    return float(round(float(x), nd))
