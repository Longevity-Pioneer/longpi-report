#!/usr/bin/env python3
"""Fetch the published sources behind registry/outcomes/*.json and store them as registry/sources/<key>.json.

For each source the script downloads the article page, records sha256 of the downloaded bytes, and keeps as `text`
the title plus the cells of the tables the outcome definitions use (one row per line, cells joined by " | ").
Numbers in registry/outcomes/*.json are checked against this text by build_outcomes.py.

One publisher (JACC) refuses scripted downloads; for it the text is the excerpt file in
evidence/outcomes/excerpts/ (taken from the article PDF's text layer by a web reader) and sha256 is that of the
excerpt bytes. The record says so in `retrieval`.

Usage:  python3 evidence/scripts/fetch_outcome_sources.py [--only KEY ...]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "skills/longpi-report/registry/sources"
EXCERPTS = ROOT / "evidence/outcomes/excerpts"
UA = "Mozilla/5.0 (compatible; longpi-registry-fetch/1.0)"
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

# key -> where to fetch, which tables (0-based order of table blocks on the PMC page), licence of the article.
# For PMC pages the citation is read from the page's citation_* meta tags.
SOURCES = {
    "pmcid:PMC11256708": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11256708/", tables=[0, 1],
        licence="CC BY-NC-ND 4.0 (article); figures used are published registry statistics", year=2022),
    "pmcid:PMC4329182": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC4329182/", tables=[1, 2, 3, 4],
        licence="CC BY-NC-SA (article)", year=2011),
    "pmcid:PMC4718125": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC4718125/", tables=[1, 2, 3, 4],
        licence="CC BY-NC (article)", year=2011),
    "pmcid:PMC3845572": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3845572/", tables=[1, 2, 3, 4],
        licence="CC BY-NC-SA 3.0 (article)", year=2009),
    "pmcid:PMC6037587": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC6037587/", tables=[1, 2, 3, 4],
        licence="CC BY-NC-SA (article)", year=2014),
    "pmcid:PMC5415464": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC5415464/", tables=[1, 2, 3, 4],
        licence="CC BY-NC (article)", year=2013),
    "pmcid:PMC11431764": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11431764/", tables=[2, 3],
        licence="CC BY 4.0", year=2019),
    "pmcid:PMC6169758": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC6169758/", tables=[1],
        licence="CC BY-NC 4.0 (article)", year=2016),
    "pmcid:PMC12226831": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC12226831/", tables=[2],
        licence="CC BY 4.0", year=2020),
    "pmcid:PMC6443580": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC6443580/", tables=[1],
        licence="NIH author manuscript (publisher copyright); figures used are published cohort statistics", year=2011),
    "doi:10.1016/j.jacc.2025.08.060": dict(
        url="https://www.jacc.org/doi/pdf/10.1016/j.jacc.2025.08.060", excerpt=True,
        citation="Zheng C, Wang X, Gu R, et al. The Burden of Cardiovascular Disease in China: Incidence Estimates From "
                 "National Surveillance (2023). JACC. 2026;87(12):1453-1465. doi:10.1016/j.jacc.2025.08.060.",
        licence="CC BY-NC-ND 4.0 (article)", year=2023),
    "pmcid:PMC13156572": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC13156572/", tables=[2],
        licence="CC BY-NC-ND 4.0 (article)", year=2018),
    "pmcid:PMC11882351": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11882351/", tables=[2],
        licence="CC BY 4.0", year=2023),
    "pmcid:PMC8021353": dict(
        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC8021353/", tables=[1],
        licence="CC BY-NC 4.0 (article)", year=2016),
}


def _cells(row_html: str):
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, re.S)]


def pmc_tables(page: str):
    """[(caption, [row cells])] in page order; PMC renders each table in <section class="tw ...">."""
    out = []
    for m in re.finditer(r'<section[^>]*class="tw[^"]*"[^>]*>(.*?)</section>', page, re.S):
        blk = m.group(0)
        cap = re.search(r'class="caption[^"]*"[^>]*>(.*?)</div>', blk, re.S) or re.search(r"<h[34][^>]*>(.*?)</h[34]>", blk, re.S)
        capt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", cap.group(1)))).strip() if cap else ""
        rows = [_cells(r) for r in re.findall(r"<tr[^>]*>(.*?)</tr>", blk, re.S)]
        out.append((capt, rows))
    return out


def citation_from_meta(page: str) -> str:
    meta = lambda n: [html.unescape(x) for x in re.findall(r'<meta name="citation_%s" content="([^"]*)"' % n, page)]
    au = meta("author")
    who = ", ".join(au[:3]) + (", et al." if len(au) > 3 else "")
    first = lambda n: (meta(n) or [""])[0]
    return (f"{who.rstrip('.')}. {first('title')}. {first('journal_title')}. {first('publication_date')};{first('volume')}"
            f"({first('issue')}):{first('firstpage')}. doi:{first('doi')}. PMID {first('pmid')}.")


def licence_from_page(page: str) -> str:
    """Licence as stated on the article page (Creative Commons link or phrase); otherwise say it is not stated."""
    m = re.search(r"creativecommons\.org/licenses/([a-z-]+)/([0-9.]+)", page)
    if m:
        return f"CC {m.group(1).upper()} {m.group(2)} (stated on article page)"
    m = re.search(r"Creative Commons (Attribution[A-Za-z\- ]*?\d\.\d)", page)
    if m:
        return f"Creative Commons {m.group(1)} (stated on article page)"
    if re.search(r"author manuscript", page, re.I):
        return "NIH author manuscript; no open licence stated (publisher copyright)"
    return "no licence stated on the PMC page (publisher copyright)"


def fetch(url: str) -> bytes:
    last = None
    for ua in (UA, BROWSER_UA):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,application/xhtml+xml"})
            b = urllib.request.urlopen(req, timeout=90).read()
            if len(b) > 20000:
                return b
            last = RuntimeError(f"short response ({len(b)} bytes)")
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(1)
    raise RuntimeError(f"fetch failed: {url}: {last}")


def safe_key(key: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in key)


def build_record(key: str, spec: dict) -> dict:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    if spec.get("excerpt"):
        p = EXCERPTS / (safe_key(key) + ".txt")
        raw = p.read_bytes()
        text = raw.decode("utf-8")
        retrieval = ("publisher blocks scripted download; text = excerpt of the article PDF text layer taken with a web reader, "
                     "stored at evidence/outcomes/excerpts/" + p.name + "; sha256 is of the excerpt bytes")
    else:
        for attempt in range(4):  # PMC occasionally serves a page without the article body; retry
            raw = fetch(spec["url"])
            page = raw.decode("utf-8", errors="replace")
            tabs = pmc_tables(page)
            if len(tabs) > max(spec["tables"]):
                break
            time.sleep(3 * (attempt + 1))
        title = re.search(r"<title>(.*?)</title>", page, re.S)
        parts = [html.unescape(title.group(1)).strip() if title else key]
        for i in spec["tables"]:
            if i >= len(tabs):
                raise RuntimeError(f"{key}: table index {i} not on page (found {len(tabs)})")
            cap, rows = tabs[i]
            parts.append(f"[Table block {i}] {cap}")
            parts += [" | ".join(r) for r in rows if any(r)]
        text = "\n".join(parts)
        retrieval = ("HTTP GET of the PMC article page; text = title + cells of the listed table blocks. PMC pages embed "
                     "per-request tokens, so sha256 of the page differs between fetches while the extracted text does not")
        spec = dict(spec, citation=citation_from_meta(page), licence=licence_from_page(page))
    return {"key": key, "url": spec["url"], "fetched_at": now, "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), "retrieval": retrieval, "citation": spec["citation"], "licence": spec["licence"],
            "data_year": spec.get("year"), "text": text, "checks": []}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    keys = a.only or list(SOURCES)
    for k in keys:
        rec = build_record(k, SOURCES[k])
        p = SRC_DIR / (safe_key(k) + ".json")
        old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
        if old and old.get("text") == rec["text"]:
            rec["checks"] = old.get("checks", [])  # unchanged content: keep the verification record
        p.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{k:34s} {rec['bytes']:>8d} bytes  sha256 {rec['sha256'][:12]}  text {len(rec['text'])} chars")


if __name__ == "__main__":
    sys.exit(main())
