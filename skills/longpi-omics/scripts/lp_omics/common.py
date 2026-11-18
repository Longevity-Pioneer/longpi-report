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


def offline_guard(url: str) -> None:
    if os.environ.get("LONGPI_OMICS_OFFLINE"):
        raise PrivacyError(f"offline mode: {url} is not cached")


def download(url: str, dest: Path, *, force: bool = False) -> Path:
    """GET a public resource into the cache (atomic). Never sends a body."""
    check_public_url(url)
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0 and not force and cached_ok(dest):
        return dest
    offline_guard(url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "longpi-omics/" + OMICS_VERSION})
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as fh:
        expected = getattr(r, "headers", {}).get("Content-Length") if hasattr(getattr(r, "headers", None), "get") else None
        shutil.copyfileobj(r, fh)
    got = tmp.stat().st_size
    if expected is not None and got != int(expected):
        tmp.unlink(missing_ok=True)
        raise OSError(f"download truncated: {got} of {expected} bytes from {url}")
    if not _integrity_ok(tmp):
        tmp.unlink(missing_ok=True)
        raise OSError(f"downloaded file is corrupt (gzip test failed): {url}")
    os.replace(tmp, dest)
    return dest


def _integrity_ok(path: Path) -> bool:
    """A .gz file must decompress to its end (a cut-off download fails here, before it reaches the cache)."""
    if not str(path).endswith(".gz"):
        return True
    import gzip
    try:
        with gzip.open(path, "rb") as fh:
            while fh.read(1 << 20):
                pass
        return True
    except (OSError, EOFError):
        return False


def cached_ok(dest: Path) -> bool:
    """A cached file is reused only if it passes the integrity test once (marker file next to it)."""
    dest = Path(dest)
    mark = dest.with_name(dest.name + ".ok")
    if mark.exists() and mark.stat().st_mtime >= dest.stat().st_mtime:
        return True
    if _integrity_ok(dest):
        mark.write_text("ok\n")
        return True
    dest.unlink()
    return False


def download_ranged(url: str, dest: Path, *, connections: int = 8, force: bool = False) -> Path:
    """Parallel HTTP range download with resume (for large public files on throttled links)."""
    import concurrent.futures as cf
    check_public_url(url)
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return dest
    offline_guard(url)
    head = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "longpi-omics/" + OMICS_VERSION})
    size = int(urllib.request.urlopen(head, timeout=120).headers["Content-Length"])
    chunk = 1 << 20
    parts = [(a, min(a + chunk, size) - 1) for a in range(0, size, chunk)]
    pdir = Path(str(dest) + ".parts")
    pdir.mkdir(parents=True, exist_ok=True)

    def get(rg):
        a, b = rg
        p = pdir / f"{a:012d}"
        if p.exists() and p.stat().st_size == b - a + 1:
            return
        last = None
        for _ in range(6):
            try:
                req = urllib.request.Request(url, headers={"Range": f"bytes={a}-{b}",
                                                           "User-Agent": "longpi-omics/" + OMICS_VERSION})
                data = urllib.request.urlopen(req, timeout=600).read()
                if len(data) == b - a + 1:
                    tmp = p.with_suffix(".tmp")
                    tmp.write_bytes(data)
                    os.replace(tmp, p)
                    return
            except Exception as e:  # retry on network errors
                last = e
        raise RuntimeError(f"range {a}-{b} of {url} failed: {last}")

    with cf.ThreadPoolExecutor(connections) as ex:
        list(ex.map(get, parts))
    tmp = Path(str(dest) + ".tmp")
    with open(tmp, "wb") as out:
        for a, _ in parts:
            out.write((pdir / f"{a:012d}").read_bytes())
    os.replace(tmp, dest)
    shutil.rmtree(pdir, ignore_errors=True)
    return dest


def drop_bad_index(directory: Path, url: str) -> None:
    """htslib caches remote indexes in the working directory; remove a cached .tbi that is not BGZF
    (e.g. an HTML error page saved by an earlier failed download)."""
    p = Path(directory) / (url.rsplit("/", 1)[-1] + ".tbi")
    if p.exists():
        with open(p, "rb") as fh:
            if fh.read(4) != b"\x1f\x8b\x08\x04":
                p.unlink()


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
    sources = {o.get("source_file") for o in observations} | {p.get("source_file") for p in provenance}
    sources.discard(None)

    def replaced(x: dict) -> bool:
        # a re-run replaces only what the same tools wrote from the same input file; another file's results stay
        tid = (x.get("tool") or {}).get("id") if isinstance(x.get("tool"), dict) else x.get("tool")
        return tid in tool_ids and (not sources or x.get("source_file") in sources or x.get("source_file") is None)
    keep = [o for o in doc["observations"] if not replaced(o)]
    doc["observations"] = keep + observations
    doc["provenance"] = [p for p in doc["provenance"] if not replaced(p)] + provenance
    if genetics is not None:
        g = doc.get("genetics") or {}
        old_mono = g.get("monogenic") or []
        supplement = genetics.pop("_monogenic_supplement", False)
        old_src, new_src = g.get("source_file"), genetics.get("source_file")
        if not supplement and g and old_src and new_src and old_src != new_src:
            # a second genotype file: the one with more called variants stays primary; the other is kept as a
            # supplement (its monogenic findings are added; its PRS/APOE/PGx do not overwrite the primary's)
            n_old = ((g.get("qc") or {}).get("n_variants") or 0)
            n_new = ((genetics.get("qc") or {}).get("n_variants") or 0)
            if n_new <= n_old:
                genetics = {"monogenic": [dict(m, supplement=True, source_file=new_src) for m in genetics.get("monogenic", [])],
                            "supplements": (g.get("supplements") or []) + [{k: genetics.get(k) for k in ("source_file", "build", "source_type", "qc")}]}
                supplement = True
            else:
                genetics["supplements"] = (g.get("supplements") or []) + [{k: g.get(k) for k in ("source_file", "build", "source_type", "qc")}]
                old_mono = [dict(m, supplement=True) for m in old_mono]
        if supplement:
            # a clinical WGS/WES file adds monogenic findings without replacing the main genotype run
            g["monogenic"] = [m for m in old_mono if not (m.get("supplement") and m.get("source_file") in
                                                          {x.get("source_file") for x in genetics.get("monogenic", [])})] + genetics.get("monogenic", [])
            if genetics.get("supplements"):
                g["supplements"] = genetics["supplements"]
        else:
            g.update(genetics)
            g["monogenic"] = genetics.get("monogenic", []) + [m for m in old_mono if m.get("supplement")]
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
