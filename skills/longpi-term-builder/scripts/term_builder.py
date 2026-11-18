#!/usr/bin/env python3
"""longpi-term-builder: verify, add and population-check registry terms (Python standard library only).

    python3 term_builder.py verify  spec.json [spec2.json ...] [--offline] [--refresh] [--json]
    python3 term_builder.py add     spec.json [...] [--qualitative] [--why "..."] [--replace]
    python3 term_builder.py check-population [--n 20000] [--json]
    python3 term_builder.py list [--qualitative]
    python3 term_builder.py show <id>

Contract: skills/longpi-report/references/registry_contract.md (term spec §3, sources §5, codes §1).

Privacy rule enforced in code: every network request goes through `http_get`, which only talks to an allow-listed
set of public hosts and only carries identifiers (standard codes, PMIDs, PMCIDs, DOIs, PGS ids). Specs never contain
personal data; `assert_public_identifier` rejects anything that does not look like one of those identifiers.

Normalisation (must agree with the engine, PRD §2.3):  l(x) = f(x) - ln E_ref[exp f(X)]
  loglinear     f = ln(hr)/per * x'         x' = clip(x) (then ln if transform.log_x; `per` is then in ln units)
  residualized  same as loglinear; reference gives mean/sd of the (already age-relative) input
  hinge         f = b_lo*max(0, knot_lo - x) + b_hi*max(0, x - knot_hi),  b = ln(hr_below|hr_above)/per
  categorical   f = ln(levels[level].hr), reference level hr = 1
  indicator     f = ln(hr) * x,  x in {0, 1}
"""
from __future__ import annotations

import argparse
import copy
import datetime as _dt
import hashlib
import json
import math
import os
import random
import re
import sys
import unicodedata
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
BUILDER_DIR = HERE.parent
SKILLS_DIR = BUILDER_DIR.parent
REPORT_DIR = SKILLS_DIR / "longpi-report"
sys.path.insert(0, str(REPORT_DIR / "scripts"))

from lp import registry as RG  # noqa: E402

VERSION = "0.1.0"
VERIFIER = f"longpi-term-builder {VERSION}"
DATA_DIR = REPORT_DIR / "data"

DISEASE_IDS = ("t2d", "chd", "stroke", "htn", "ckd", "masld", "crc", "lung_ca", "liver_ca", "gastric_ca",
               "breast_ca", "prostate_ca", "ad", "cervical_ca")
SEX_SPECIFIC = {"breast_ca": "F", "prostate_ca": "M", "cervical_ca": "F"}
ACCEPT_DESIGNS = ("meta-analysis", "pooled-cohort", "prospective-cohort", "mendelian-randomization", "rct",
                  "meta-analysis-rct", "pgs-catalog-evaluation")
EAST_ASIAN_RE = re.compile(r"east asian|chinese|china|japan|korea|taiwan|hong kong|singapore chinese|\bEAS\b", re.I)
NON_EAST_ASIAN_RE = re.compile(r"europe|\bUS\b|united states|americ|australia|multinational|international|mixed|"
                               r"white|\bUK\b|british|african|hispanic|global|worldwide|western", re.I)


def is_east_asian(ancestry: str) -> bool:
    return bool(EAST_ASIAN_RE.search(ancestry or "")) and not NON_EAST_ASIAN_RE.search(ancestry or "")
CORE_IDS = ("core.lipid", "core.bp", "core.adiposity", "core.glucose", "core.smoking", "core.alcohol", "core.crf",
            "core.muscle", "core.rhr", "core.sleep", "core.phenoage_clock", "core.methylation")
AGE_BANDS = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 99)]

# ----------------------------------------------------------------------------- network (privacy choke point)

ALLOWED_HOSTS = {
    "eutils.ncbi.nlm.nih.gov", "www.ebi.ac.uk", "clinicaltables.nlm.nih.gov", "rest.uniprot.org",
    "rest.genenames.org", "www.pgscatalog.org",
}
_ID_RE = re.compile(
    r"^(?:\d{1,9}"                        # PMID, taxonomy id, HGNC number
    r"|PMC\d{1,9}"                        # PMCID
    r"|10\.\d{4,9}/[^\s\"<>]{1,200}"      # DOI
    r"|PGS\d{6}|PPM\d{6}|PSS\d{6}"        # PGS Catalog ids
    r"|\d{1,7}-\d"                        # LOINC
    r"|[A-Z]\d{2}(?:\.[0-9A-Z]{1,4})?"    # ICD-10
    r"|[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}"  # UniProt accession
    r")$")
_FIXED_PARAMS = {"db", "retmode", "rettype", "format", "resultType", "df", "sf", "maxList", "terms_type", "fields",
                 "pageSize", "limit", "tool"}

FIXTURE_DIR = os.environ.get("LONGPI_TB_FIXTURES")      # replay recorded responses (tests); no network
RECORD_DIR = os.environ.get("LONGPI_TB_RECORD")         # record responses while running live
REQUEST_LOG: List[str] = []                              # every URL requested in this process (for tests)


class PrivacyError(RuntimeError):
    pass


def assert_public_identifier(value: str) -> str:
    if not _ID_RE.match(value or ""):
        raise PrivacyError(f"refusing to send a value that is not a public identifier: {value[:40]!r}")
    return value


def _fixture_name(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24] + ".txt"


def http_get(url: str, accept: str = "application/json", timeout: int = 40) -> str:
    """The only network function. Host allow-list + every query value must be a fixed keyword or an identifier."""
    u = urllib.parse.urlparse(url)
    if u.scheme != "https" or u.hostname not in ALLOWED_HOSTS:
        raise PrivacyError(f"host not allowed: {u.hostname}")
    for k, vals in urllib.parse.parse_qs(u.query, keep_blank_values=True).items():
        for v in vals:
            if k in _FIXED_PARAMS:
                if not re.match(r"^[A-Za-z0-9_,.\-]{0,40}$", v):
                    raise PrivacyError(f"unexpected value for {k}")
                continue
            if k in ("id", "terms"):
                assert_public_identifier(v)
            elif k == "query":
                inner = re.sub(r"^(?:EXT_ID:|DOI:|PMCID:)\"?|\"?(?: AND SRC:MED)?$", "", v)
                assert_public_identifier(inner)
            else:
                raise PrivacyError(f"query parameter not allowed: {k}")
    for seg in u.path.split("/"):
        if seg and re.search(r"\d", seg) and seg not in ("v3", "icd10cm"):
            assert_public_identifier(urllib.parse.unquote(seg).replace(".json", ""))
    REQUEST_LOG.append(url)
    if FIXTURE_DIR:
        p = Path(FIXTURE_DIR) / _fixture_name(url)
        if not p.exists():
            raise FileNotFoundError(f"no recorded fixture for {url}")
        return p.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "longpi-term-builder/0.1 (registry verifier)"})
    body, last = None, None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", errors="replace")
            break
        except urllib.error.HTTPError as e:   # NCBI allows 3 requests/s without a key: back off on 429/5xx
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(1.5 * (attempt + 1) + random.random())
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    if body is None:
        raise last
    if RECORD_DIR:
        Path(RECORD_DIR).mkdir(parents=True, exist_ok=True)
        (Path(RECORD_DIR) / _fixture_name(url)).write_text(body, encoding="utf-8")
    return body


def _q(v: str) -> str:
    return urllib.parse.quote(assert_public_identifier(v), safe="")


# ----------------------------------------------------------------------------- code checks

def _lp_patterns() -> List[re.Pattern]:
    codes = json.loads((DATA_DIR / "observation_codes.json").read_text(encoding="utf-8"))["lp_codes"]
    pats = []
    for k in codes:
        rx = "^" + re.sub(r"<[^>]+>", "[A-Za-z0-9_:.\\-]+", re.escape(k).replace("\\<", "<").replace("\\>", ">")) + "$"
        pats.append(re.compile(rx))
    return pats


def check_code(code: str, offline: bool = False) -> Tuple[bool, str]:
    """Does this standard code exist in its public dictionary? Returns (ok, detail)."""
    if not code or ":" not in code:
        return False, "编码须为 命名空间:值"
    ns, val = code.split(":", 1)
    if ns == "LP":
        if not any(p.match(code) for p in _lp_patterns()):
            return False, f"{code} 不在 data/observation_codes.json 的 lp_codes 中"
        m = re.match(r"^LP:monogenic:(HGNC:\d+)$", code)
        if m:
            return check_code(m.group(1), offline)
        m = re.match(r"^LP:fh:(\w+)$", code)
        if m and m.group(1) not in DISEASE_IDS:
            return False, f"未知疾病 id {m.group(1)}"
        return True, "LP 编码已登记"
    if offline:
        return True, f"{ns} 未联网校验（--offline）"
    try:
        if ns == "LOINC":
            r = json.loads(http_get(f"https://clinicaltables.nlm.nih.gov/api/loinc_items/v3/search?terms={_q(val)}&df=LOINC_NUM,text"))
            hits = [row for row in (r[3] or []) if row and row[0] == val]
            return (bool(hits), hits[0][1] if hits else f"LOINC {val} 查无此码")
        if ns == "ICD10":
            r = json.loads(http_get(f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code&terms={_q(val)}&maxList=50"))
            codes = r[1] or []
            hit = [c for c in codes if c == val or c.startswith(val)]
            return (bool(hit), f"ICD-10-CM {val}: {len(hit)} 个编码" if hit else f"ICD-10 {val} 查无此码")
        if ns == "UNIPROT":
            r = json.loads(http_get(f"https://rest.uniprot.org/uniprotkb/{_q(val)}.json"))
            return (r.get("primaryAccession") == val, r.get("uniProtkbId", ""))
        if ns == "NCBITAXON":
            r = json.loads(http_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&id={_q(val)}&retmode=json"))
            res = r.get("result", {}).get(val, {})
            return ("scientificname" in res, res.get("scientificname", "taxonomy id 查无"))
        if ns == "HGNC":
            r = json.loads(http_get(f"https://rest.genenames.org/fetch/hgnc_id/{_q(val)}"))
            docs = r.get("response", {}).get("docs", [])
            return (bool(docs), docs[0].get("symbol", "") if docs else f"HGNC:{val} 查无")
        if ns == "PGS":
            r = json.loads(http_get(f"https://www.pgscatalog.org/rest/score/{_q(val)}"))
            return (r.get("id") == val, r.get("name", "") + " | license: " + (r.get("license") or "")[:200])
        if ns == "HMDB":
            return (bool(re.match(r"^HMDB\d{7}$", val)), "HMDB 只做格式校验（无公开 REST）")
    except PrivacyError:   # not a well-formed identifier: never sent, the code is simply invalid
        return False, f"{code} 不是格式正确的 {ns} 编码"
    except Exception as e:  # network or parse failure
        return False, f"{ns} 校验失败：{type(e).__name__}: {e}"
    return False, f"未知命名空间 {ns}"


def pgs_license(pgs_id: str) -> Tuple[Optional[bool], str]:
    r = json.loads(http_get(f"https://www.pgscatalog.org/rest/score/{_q(pgs_id)}"))
    lic = r.get("license") or ""
    nc = bool(re.search(r"non[- ]?commercial|\bCC[- ]BY[- ]NC|\bNC\b|academic use only|research use only", lic, re.I))
    return (False if nc else True), lic


# ----------------------------------------------------------------------------- sources

def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"(?<=\d)[·∙⋅](?=\d)", ".", s)      # Lancet mid-dot decimals
    s = re.sub(r"[−‐‑‒–—]", "-", s)   # minus and dashes
    s = s.replace(" ", " ").replace(" ", " ").replace(" ", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _strip_xml(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split())


def _pubmed_abstract(pmid: str) -> Tuple[str, str]:
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={_q(pmid)}&retmode=xml&rettype=abstract"
    body = http_get(url, accept="application/xml")
    root = ET.fromstring(body)
    art = root.find(".//Article")
    if art is None:
        raise LookupError(f"PubMed {pmid} 无记录")
    parts = []
    t = art.find("ArticleTitle")
    if t is not None:
        parts.append(_strip_xml(t))
    for a in art.findall(".//Abstract/AbstractText"):
        lab = a.get("Label")
        parts.append(((lab + ": ") if lab else "") + _strip_xml(a))
    j = art.find("Journal/Title")
    y = root.find(".//PubDate/Year")
    meta = (j.text if j is not None else "") + (" " + y.text if y is not None else "")
    return "\n".join(parts), meta


def _epmc_record(query: str) -> dict:
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
           + urllib.parse.quote(query, safe="") + "&format=json&resultType=core")
    r = json.loads(http_get(url))
    res = r.get("resultList", {}).get("result", [])
    return res[0] if res else {}


def _epmc_fulltext_paragraphs(pmcid: str) -> List[str]:
    body = http_get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{_q(pmcid)}/fullTextXML", accept="application/xml")
    root = ET.fromstring(body)
    out = []
    for tag in ("p", "tr", "caption", "title"):
        for el in root.iter(tag):
            if tag == "tr":   # keep cell boundaries, otherwise adjacent numbers fuse ("1.0751.114")
                txt = " | ".join(_strip_xml(c) for c in el if c.tag in ("td", "th"))
            else:
                txt = _strip_xml(el)
            if len(txt) > 20:
                out.append(txt)
    return out


def source_key(ev: dict) -> Optional[str]:
    if ev.get("source"):
        return ev["source"]
    if ev.get("pmid"):
        return f"pmid:{ev['pmid']}"
    if ev.get("pmcid"):
        return f"pmcid:{ev['pmcid']}"
    if ev.get("doi"):
        return f"doi:{ev['doi']}"
    return None


def _src_path(root: Path, key: str) -> Path:
    return root / "sources" / (RG.safe_key(key) + ".json")


def _cache_path(key: str) -> Path:
    """Fetched sources live in a cache until `add` copies them into the frozen registry (verify never touches it)."""
    base = Path(os.environ.get("LONGPI_TB_CACHE") or (BUILDER_DIR / ".cache"))
    return base / "sources" / (RG.safe_key(key) + ".json")


def fetch_source(key: str, root: Path, need: Iterable[str] = (), refresh: bool = False, offline: bool = False) -> dict:
    """Fetch (or reuse) a source record. `need` are normalised strings (quotes) the text should contain: when the
    abstract lacks one, open-access full-text paragraphs containing it are added."""
    p = _cache_path(key)
    rp = _src_path(root, key)
    rec = json.loads(p.read_text(encoding="utf-8")) if p.exists() else (
        json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else None)
    need = [n for n in need if n]
    if rec and not refresh and all(n.lower() in norm_text(rec["text"]).lower() for n in need):
        return rec
    if offline:
        if rec:
            return rec
        raise LookupError(f"离线模式且无缓存来源 {key}")
    kind, val = key.split(":", 1)
    texts, url, meta, raw_for_hash, extra = [], "", "", "", {}
    if kind == "pgs_perf":
        r = json.loads(http_get(f"https://www.pgscatalog.org/rest/performance/{_q(val)}"))
        texts.append(_render_pgs_perf(r))
        url = f"https://www.pgscatalog.org/rest/performance/{val}"
        raw_for_hash = json.dumps(r, sort_keys=True)
        extra = {"pgs_id": (r.get("associated_pgs_id") or "")}
    else:
        if kind == "pmid":
            abst, meta = _pubmed_abstract(val)
            texts.append(abst)
            url = f"https://pubmed.ncbi.nlm.nih.gov/{val}/"
            rec_e = _epmc_record(f"EXT_ID:{val} AND SRC:MED")
        elif kind == "doi":
            rec_e = _epmc_record(f'DOI:"{val}"')
            if rec_e.get("pmid"):
                abst, meta = _pubmed_abstract(rec_e["pmid"])
                texts.append(abst)
            elif rec_e.get("abstractText"):
                texts.append((rec_e.get("title") or "") + "\n" + re.sub(r"<[^>]+>", " ", rec_e["abstractText"]))
            url = f"https://doi.org/{val}"
        elif kind == "pmcid":
            rec_e = _epmc_record(f"PMCID:{val}")
            if rec_e.get("pmid"):
                abst, meta = _pubmed_abstract(rec_e["pmid"])
                texts.append(abst)
            url = f"https://europepmc.org/article/PMC/{val}"
        else:
            raise ValueError(f"未知来源类型 {key}")
        pmcid = rec_e.get("pmcid") if rec_e else None
        if kind == "pmcid":
            pmcid = val
        extra = {"pmcid": pmcid, "doi": rec_e.get("doi") if rec_e else None,
                 "open_access": (rec_e or {}).get("isOpenAccess"), "epmc_license": (rec_e or {}).get("license")}
        base = norm_text("\n".join(texts)).lower()
        missing = [n for n in need if n.lower() not in base]
        if missing and pmcid and (rec_e or {}).get("isOpenAccess", "N") == "Y" or (missing and kind == "pmcid"):
            try:
                paras = _epmc_fulltext_paragraphs(pmcid)
                keep = [pp for pp in paras if any(m.lower() in norm_text(pp).lower() for m in missing)]
                if keep:
                    texts.append("[full text, Europe PMC " + pmcid + "]")
                    texts.extend(keep)
            except Exception as e:  # full text is optional
                extra["fulltext_error"] = f"{type(e).__name__}"
        raw_for_hash = "\n".join(texts)
    if rec:   # keep previously stored paragraphs (other terms may quote them)
        old = rec["text"]
        new = "\n".join(texts)
        merged = new + "".join("\n" + line for line in old.split("\n") if line and line not in new)
        texts = [merged]
    text = "\n".join(texts)
    out = {"key": key, "url": url, "fetched_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "sha256": hashlib.sha256(raw_for_hash.encode("utf-8")).hexdigest(), "citation": meta, "text": text,
           **{k: v for k, v in extra.items() if v is not None},
           "checks": (rec or {}).get("checks", [])}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def _render_pgs_perf(r: dict) -> str:
    """Deterministic one-line-per-metric text of a PGS Catalog performance record (so a quote can be checked)."""
    ss = r.get("sampleset", {}) or {}
    samples = ss.get("samples", []) or []
    anc = "; ".join(sorted({(s.get("ancestry_broad") or "") for s in samples}))
    cohorts = "; ".join(sorted({c.get("name_short", "") for s in samples for c in (s.get("cohorts") or [])}))
    n = sum((s.get("sample_number") or 0) for s in samples)
    ncases = sum((s.get("sample_cases") or 0) for s in samples)
    pub = r.get("publication", {}) or {}
    lines = [f"{r.get('id')} | score {r.get('associated_pgs_id')} | trait {(r.get('phenotyping_reported') or '')}",
             f"ancestry: {anc} | cohorts: {cohorts} | n: {n} | cases: {ncases}",
             f"publication: {pub.get('firstauthor', '')} {pub.get('journal', '')} {pub.get('date_publication', '')} PMID {pub.get('PMID', '')}",
             f"covariates: {r.get('covariates') or ''}"]
    for m in (r.get("performance_metrics", {}) or {}).get("effect_sizes", []) or []:
        lines.append(f"{m.get('name_long')} ({m.get('name_short')}): {m.get('estimate')} [{m.get('ci_lower')}, {m.get('ci_upper')}]")
    for m in (r.get("performance_metrics", {}) or {}).get("class_acc", []) or []:
        lines.append(f"{m.get('name_long')} ({m.get('name_short')}): {m.get('estimate')} [{m.get('ci_lower')}, {m.get('ci_upper')}]")
    return "\n".join(lines)


# ----------------------------------------------------------------------------- number matching

def number_variants(x) -> List[str]:
    if x is None:
        return []
    x = float(x)
    out = set()
    if abs(x - round(x)) < 1e-12 and abs(x) < 1e9:
        i = int(round(x))
        out |= {str(i), f"{i}.0", f"{i}.00"}
    s = repr(x)
    if "e" not in s:
        out.add(s)
    for d in (1, 2, 3, 4):
        v = f"{x:.{d}f}"
        if abs(float(v) - x) < 1e-12:
            out.add(v)
    return sorted(out, key=len)


def _int_variants(n: int) -> List[str]:
    return [str(n), f"{n:,}", f"{n:,}".replace(",", " "), f"{n:,}".replace(",", " ")]


def find_number(x, text: str) -> Optional[str]:
    """First verbatim occurrence of x as a stand-alone number in (normalised) text; returns its context."""
    t = norm_text(text)
    for v in number_variants(x):
        m = re.search(r"(?<![\d.])" + re.escape(v) + r"(?!\d|\.\d)", t)
        if m:
            return t[max(0, m.start() - 60): m.end() + 60]
    return None


def _num_positions(x, t: str) -> List[Tuple[int, int]]:
    out = []
    for v in number_variants(x):
        out += [(m.start(), m.end()) for m in re.finditer(r"(?<![\d.])" + re.escape(v) + r"(?![\d]|\.\d)", t)]
    return sorted(out)


def find_triplet(hr, lo, hi, text: str, window: int = 90) -> bool:
    """hr followed (within `window` characters) by lo and then hi: the three numbers belong to one estimate."""
    t = norm_text(text)
    los, his = _num_positions(lo, t), _num_positions(hi, t)
    for s, e in _num_positions(hr, t):
        for ls, le in los:
            if e <= ls <= e + window:
                if any(le <= hs <= le + 25 for hs, _ in his):
                    return True
    return False


def _effect_numbers(term: dict, oc: str, e: dict) -> List[Tuple[str, float]]:
    """(label, number) pairs that must appear verbatim in the quote."""
    if e.get("derived"):
        d = e["derived"]["from"]
        return [(f"{oc}.derived.from.{k}", d[k]) for k in ("hr", "lo", "hi") if d.get(k) is not None]
    out = []
    shape = term["transform"]["shape"]
    if shape == "hinge":
        for side in ("hr_below", "hr_above"):
            s = e.get(side) or {}
            if s.get("derived"):
                out += [(f"{oc}.{side}.derived.{k}", s["derived"]["from"][k]) for k in ("hr", "lo", "hi")]
            elif s.get("hr", 1) != 1:
                out += [(f"{oc}.{side}.{k}", s[k]) for k in ("hr", "lo", "hi") if k in s]
        return out
    if shape == "categorical":
        for lvl, s in (e.get("levels") or {}).items():
            if s.get("hr", 1) == 1 and "lo" not in s:
                continue
            if s.get("derived"):
                out += [(f"{oc}.{lvl}.derived.{k}", s["derived"]["from"][k]) for k in ("hr", "lo", "hi")]
            else:
                out += [(f"{oc}.{lvl}.{k}", s[k]) for k in ("hr", "lo", "hi") if k in s]
        return out
    return [(f"{oc}.{k}", e[k]) for k in ("hr", "lo", "hi") if e.get(k) is not None]


def _check_derived(e: dict) -> Optional[str]:
    """Derived effect: hr = from.hr ** k (k from `pow`, -1 for invert). Returns a problem or None."""
    d = e.get("derived")
    if not d:
        return None
    k = float(d.get("pow", -1.0 if d.get("op") == "invert" else 1.0))
    f = d["from"]
    want = {"hr": f["hr"] ** k}
    if k >= 0:
        want["lo"], want["hi"] = f["lo"] ** k, f["hi"] ** k
    else:
        want["lo"], want["hi"] = f["hi"] ** k, f["lo"] ** k
    for key, w in want.items():
        if key in e and abs(math.log(e[key]) - math.log(w)) > 0.006 + 0.005 * abs(math.log(w)):
            return f"派生值 {key}={e[key]} 与 原值^{k} = {w:.4f} 不符"
    return None


# ----------------------------------------------------------------------------- normalisation (engine §2.3)

# probabilists' Gauss-Hermite, 20 points (same nodes as skills/longpi-report/scripts/lp/domains.py)
_GH_X = [-7.619048541679758, -6.510590157013654, -5.5787388058932015, -4.734581334046055, -3.9439673506573163,
         -3.1890148165533896, -2.458663611172368, -1.7452473208141268, -1.042945348802751, -0.346964157081356,
         0.346964157081356, 1.042945348802751, 1.7452473208141268, 2.458663611172368, 3.1890148165533896,
         3.9439673506573163, 4.734581334046055, 5.5787388058932015, 6.510590157013654, 7.619048541679758]
_GH_W = [1.2578006724379264e-13, 2.4820623623151797e-10, 6.127490259982928e-08, 4.4021210902308646e-06,
         0.00012882627996192942, 0.0018301031310804924, 0.013997837447100996, 0.06150637206397696,
         0.16173933398400003, 0.2607930634495548, 0.2607930634495548, 0.16173933398400003, 0.06150637206397696,
         0.013997837447100996, 0.0018301031310804924, 0.00012882627996192942, 4.4021210902308646e-06,
         6.127490259982928e-08, 2.4820623623151797e-10, 1.2578006724379264e-13]


def _ln(e: dict) -> float:
    return math.log(e.get("hr", 1.0))


def f_raw(term: dict, oc: str, x) -> float:
    """Un-normalised log HR of value x for outcome oc (point estimates)."""
    tr = term["transform"]
    shape = tr["shape"]
    e = term["effect"][oc]
    if shape == "categorical":
        lv = (e.get("levels") or {}).get(x)
        if lv is None:
            raise KeyError(f"{term['id']}: 未知水平 {x}")
        return _ln(lv)
    if shape == "indicator":
        return _ln(e) * (1.0 if x else 0.0)
    lo, hi = (tr.get("clip") or [None, None])
    if lo is not None:
        x = max(x, lo)
    if hi is not None:
        x = min(x, hi)
    if tr.get("log_x"):
        x = math.log(max(x, 1e-12))
    if shape in ("loglinear", "residualized"):
        return _ln(e) / e["per"] * x
    if shape == "hinge":
        b_lo = _ln(e["hr_below"]) / e["hr_below"]["per"] if e.get("hr_below") else 0.0
        b_hi = _ln(e["hr_above"]) / e["hr_above"]["per"] if e.get("hr_above") else 0.0
        k_lo, k_hi = tr.get("knot_lo", tr.get("knot")), tr.get("knot_hi", tr.get("knot"))
        if tr.get("log_x"):
            k_lo = math.log(k_lo) if k_lo else k_lo
            k_hi = math.log(k_hi) if k_hi else k_hi
        out = 0.0
        if b_lo:
            out += b_lo * max(0.0, k_lo - x)
        if b_hi:
            out += b_hi * max(0.0, x - k_hi)
        return out
    raise ValueError(shape)


def ref_band(term: dict, sex: str, age: float) -> Optional[dict]:
    """The reference row for sex/age, or None if the reference does not cover it."""
    ref = term.get("reference") or {}
    rows = ref.get("by_sex_age")
    if rows is None:   # one row for everybody
        keys = ("mean", "sd", "p", "prevalence", "meanlog", "sdlog")
        row = {k: ref[k] for k in keys if k in ref}
        return row or None
    for r in rows:
        if r.get("sex", "both") in (sex, "both") and r["age_lo"] <= age <= r["age_hi"]:
            return r
    return None


def ref_kind(term: dict) -> str:
    ref = term.get("reference") or {}
    k = ref.get("kind")
    if k:
        return k
    return {"categorical": "categorical", "indicator": "prevalence"}.get(term["transform"]["shape"], "normal")


_Z_N = 1200
_Z = [-8.0 + 16.0 * i / _Z_N for i in range(_Z_N + 1)]
_ZW = [(1 if i in (0, _Z_N) else (4 if i % 2 else 2)) * (16.0 / _Z_N) / 3 * math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
       for i, z in enumerate(_Z)]


def _expect_std_normal(g: Callable[[float], float]) -> float:
    """E[g(Z)], Z ~ N(0,1), Simpson on [-8, 8]. Clipping and hinges make g non-smooth, where 20-point Gauss-Hermite
    can be off by 1-3%; Simpson on this grid stays within about 1e-4."""
    return sum(w * g(z) for z, w in zip(_Z, _ZW))


def log_mean_exp_ref(term: dict, oc: str, sex: str, age: float, scale: float = 1.0) -> float:
    """ln E_ref[exp(scale * f(X))] for the reference population of this sex and age (the engine's normaliser;
    `scale` = overlap coefficient when the coefficient is applied before normalising)."""
    row = ref_band(term, sex, age)
    if row is None:
        raise LookupError(f"{term['id']}: 参考分布未覆盖 {sex} {age}")
    kind = ref_kind(term)
    F = lambda x: math.exp(scale * f_raw(term, oc, x))  # noqa: E731
    if kind == "categorical":
        return math.log(sum(p * F(lvl) for lvl, p in row["p"].items()))
    if kind == "categorical_mid":
        mids = term["reference"]["mids"]
        mids = mids.get(sex, mids) if isinstance(mids, dict) and sex in mids else mids
        return math.log(sum(p * F(mids[lvl]) for lvl, p in row["p"].items()))
    if kind == "prevalence":
        p = row["prevalence"]
        return math.log(1 - p + p * F(1))
    if kind == "lognormal":   # ln X ~ N(meanlog, sdlog)
        mu, sd = row["meanlog"], row["sdlog"]
        return math.log(_expect_std_normal(lambda z: F(math.exp(mu + sd * z))))
    mu, sd = row["mean"], row["sd"]   # normal / residualized
    if sd <= 0:
        return scale * f_raw(term, oc, mu)
    return math.log(_expect_std_normal(lambda z: F(mu + sd * z)))


def sample_ref(term: dict, sex: str, age: float, rng: random.Random):
    row = ref_band(term, sex, age)
    kind = ref_kind(term)
    if kind in ("categorical", "categorical_mid"):
        u, acc, last = rng.random(), 0.0, None
        for lvl, p in row["p"].items():
            acc += p
            last = lvl
            if u <= acc:
                break
        if kind == "categorical":
            return last
        mids = term["reference"]["mids"]
        mids = mids.get(sex, mids) if isinstance(mids, dict) and sex in mids else mids
        return mids[last]
    if kind == "prevalence":
        return 1 if rng.random() < row["prevalence"] else 0
    if kind == "lognormal":
        return math.exp(rng.gauss(row["meanlog"], row["sdlog"]))
    return rng.gauss(row["mean"], row["sd"])


def _engine_normaliser() -> Optional[Callable]:
    """If the engine exposes its normaliser, check against it as well (lp.terms.log_mean_exp_ref(term, oc, sex, age))."""
    spec = os.environ.get("LONGPI_ENGINE_NORMALISER", "lp.terms:log_mean_exp_ref")
    mod, _, fn = spec.partition(":")
    try:
        m = __import__(mod, fromlist=[fn])
        return getattr(m, fn, None)
    except Exception:
        return None


def stored_or_computed_norm(term: dict, oc: str, sex: str, age: float) -> float:
    """A spec may carry a precomputed normaliser table reference.log_norm = {oc: [{sex, age_lo, age_hi, value}]}."""
    tab = ((term.get("reference") or {}).get("log_norm") or {}).get(oc)
    if tab:
        for r in tab:
            if r.get("sex", "both") in (sex, "both") and r["age_lo"] <= age <= r["age_hi"]:
                return r["value"]
    return log_mean_exp_ref(term, oc, sex, age)


def _sexes(term: dict, oc: str) -> List[str]:
    s = SEX_SPECIFIC.get(oc) or (term.get("population") or {}).get("sex_scope")
    return [s] if s in ("M", "F") else ["M", "F"]


def check_population(terms: List[dict], n: int = 20000, tol: float = 0.02, seed: int = 20261118) -> dict:
    """Synthetic population drawn from each term's reference: mean exp(l) per term/outcome/sex/band must be 1 within
    tol (MC error allowed for), the reference must cover every band, directions must be coherent, and the combined
    all-cause ext contribution (with overlap coefficients) must also average 1 within tol."""
    rng = random.Random(seed)
    eng = _engine_normaliser()
    rows, fails = [], []
    combined = {}
    for t in terms:
        if t.get("core") or t.get("status", "active") != "active" or t.get("kind") is None:
            continue
        for oc, e in (t.get("effect") or {}).items():
            for prob in direction_problems(t, oc, e):
                fails.append(f"{t['id']} {oc}: {prob}")
            for sex in _sexes(t, oc):
                for lo, hi in AGE_BANDS:
                    age = (lo + hi) / 2
                    try:
                        L = stored_or_computed_norm(t, oc, sex, age)
                    except (LookupError, KeyError, ValueError, TypeError, ZeroDivisionError) as ex:
                        fails.append(f"{t['id']} {oc} {sex} {lo}-{hi}: {ex}")
                        continue
                    if eng is not None:
                        try:
                            Le = eng(t, oc, sex, age)
                            if abs(Le - log_mean_exp_ref(t, oc, sex, age)) > 1e-6:
                                fails.append(f"{t['id']} {oc} {sex} {lo}-{hi}: 引擎归一化 {Le:.6f} 与建项层不一致")
                        except Exception:
                            pass
                    vals = [math.exp(f_raw(t, oc, sample_ref(t, sex, age, rng)) - L) for _ in range(n)]
                    m = sum(vals) / n
                    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / max(1, n - 1))
                    se = sd / math.sqrt(n)
                    ok = abs(m - 1) <= tol + 3 * se and abs(m - 1) <= 2 * tol
                    rows.append({"term": t["id"], "outcome": oc, "sex": sex, "band": f"{lo}-{hi}", "mean_exp": round(m, 4),
                                 "mc_se": round(se, 4), "ok": ok})
                    if not ok:
                        fails.append(f"{t['id']} {oc} {sex} {lo}-{hi}: 人群平均风险倍数 {m:.4f}（应≈1，容差 {tol}）")
                    if oc == "all_cause" and t["kind"] in ("state", "exposure", "behavior"):
                        c = coef(t)
                        key = ("behavior" if t["kind"] == "behavior" else "state", sex, lo)
                        Lc = log_mean_exp_ref(t, oc, sex, age, scale=c) if c > 0 else 0.0
                        combined.setdefault(key, []).append((t, c, L, Lc))
    comb_rows = []
    for (part, sex, lo), lst in sorted(combined.items()):
        hi = dict(AGE_BANDS)[lo]
        age = (lo + hi) / 2
        acc_c, acc_prd, acc_sq = 0.0, 0.0, 0.0
        m_draws = max(1, n // 4)
        for _ in range(m_draws):
            s_c, s_prd = 0.0, 0.0
            for t, c, L, Lc in lst:
                f = f_raw(t, "all_cause", sample_ref(t, sex, age, rng))
                s_c += c * f - Lc            # coefficient applied, then normalised: population mean exactly 1
                s_prd += c * (f - L)         # PRD 2.3 as written (normalise, then coefficient): Jensen deficit
            acc_c += math.exp(s_c)
            acc_sq += math.exp(2 * s_c)
            acc_prd += math.exp(s_prd)
        m, m_prd = acc_c / m_draws, acc_prd / m_draws
        se = math.sqrt(max(0.0, acc_sq / m_draws - m * m) / m_draws)
        ok = abs(m - 1) <= tol + 3 * se and abs(m - 1) <= 2 * tol
        comb_rows.append({"part": part, "sex": sex, "band": f"{lo}-{hi}", "n_terms": len(lst), "mean_exp": round(m, 4),
                          "mean_exp_normalise_then_coef": round(m_prd, 4), "ok": ok})
        if not ok:
            fails.append(f"合计（{part} {sex} {lo}-{hi}，{len(lst)} 项）：人群平均风险倍数 {m:.4f}")
    return {"ok": not fails, "fails": fails, "rows": rows, "combined": comb_rows, "n": n, "tol": tol,
            "engine_normaliser": bool(eng)}


def coef(t: dict, oc: str = "all_cause") -> float:
    e = (t.get("effect") or {}).get(oc) or {}
    c = float(e.get("coef", (t.get("overlap") or {}).get("coef", 0.0)))
    return max(0.0, min(1.0, c))


def direction_problems(t: dict, oc: str, e: dict) -> List[str]:
    shape = t["transform"]["shape"]
    out = []
    if shape in ("loglinear", "residualized", "indicator"):
        d = e.get("direction")
        hr = e.get("hr")
        if hr is None:
            return ["缺 hr"]
        if d is None and shape != "indicator":
            out.append("缺 direction")
        elif d == "higher_worse" and hr < 1:
            out.append(f"direction=higher_worse 但 hr={hr}<1")
        elif d == "higher_better" and hr > 1:
            out.append(f"direction=higher_better 但 hr={hr}>1")
    elif shape == "hinge":
        for side in ("hr_below", "hr_above"):
            s = e.get(side)
            if s and s.get("hr", 1) < 1:
                out.append(f"{side}.hr<1：折线形状要求离开拐点风险上升")
    elif shape == "categorical":
        lv = e.get("levels") or {}
        if not any(abs(v.get("hr", 0) - 1) < 1e-12 for v in lv.values()):
            out.append("分类形状须有一个参考组 hr=1")
    return out


# ----------------------------------------------------------------------------- verify

def _adjusted_set(t: dict) -> set:
    return set(t.get("adjusted_for") or [])


def overlap_rule(t: dict) -> Optional[str]:
    """PRD §4.1 rules, checked in code: fully adjusted for the overlapping counted terms -> coef <= 1 (default 0.8);
    partially -> <= 0.6; only age/sex -> <= 0.3."""
    ov = t.get("overlap") or {}
    c = ov.get("coef")
    if c is None:
        return "overlap.coef 缺失"
    if not 0 <= c <= 1:
        return "overlap.coef 须在 0–1"
    if "all_cause" not in (t.get("effect") or {}) or t.get("kind") == "genetic":
        return None
    ow = list(ov.get("overlaps_with") or [])
    adj = _adjusted_set(t)
    if not ow:
        if not ov.get("rationale_zh"):
            return "overlap.overlaps_with 为空时须写 rationale_zh 说明为何与已计入项无重叠"
        return None
    covered = [o for o in ow if o in adj]
    non_demo = adj - {"age", "sex"}
    if len(covered) == len(ow):
        lim = 1.0
    elif covered or non_demo:
        lim = 0.6
    else:
        lim = 0.3
    if c > lim + 1e-9:
        return f"overlap.coef={c} 超过规则上限 {lim}（重叠项 {ow}，研究已校正 {covered}）"
    if not ov.get("rationale_zh"):
        return "overlap.rationale_zh 缺失"
    return None


def verify(spec: dict, root: Path = RG.REG_DIR, offline: bool = False, refresh: bool = False) -> dict:
    """Run every gate on a term spec. verdict: auto_accept | qualitative | invalid."""
    fail, warn, invalid, checks, info = [], [], [], [], []
    used: set = set()
    st = RG.validate_term(spec)
    if st:
        invalid += st
        return {"id": spec.get("id"), "verdict": "invalid", "invalid": invalid, "fail": fail, "warn": warn, "checks": checks}
    tid = spec["id"]
    code = spec["input"]["code"]
    ok, det = check_code(code, offline)
    (info if ok else invalid).append(f"编码 {code}: {det}")
    # dedupe by code (+platform)
    for sub in ("terms", "qualitative"):
        for p in sorted((root / sub).glob("*.json")) if (root / sub).is_dir() else []:
            o = json.loads(p.read_text(encoding="utf-8"))
            if o.get("id") == tid:
                continue
            if (o.get("input") or {}).get("code") == code and (o.get("input") or {}).get("platform") == spec["input"].get("platform"):
                invalid.append(f"编码 {code} 已有条目 {o['id']}（{sub}）：同一指标不建第二条，应合并到该条")
    # license
    lic = spec.get("license") or {}
    if lic.get("commercial_use") is False:
        invalid.append("许可不允许商业使用")
    elif lic.get("commercial_use") is None:
        fail.append("license.commercial_use 未写明")
    if code.startswith("PGS:") and not offline:
        try:
            cu, txt = pgs_license(code.split(":", 1)[1])
            info.append(f"PGS 许可：{txt[:160]}")
            if cu is False:
                invalid.append("PGS Catalog 许可含非商业限制")
        except Exception as e:
            fail.append(f"PGS 许可查询失败 {type(e).__name__}")
    # evidence per outcome
    ev0 = spec["evidence"]
    designs = ACCEPT_DESIGNS + (("case-control",) if spec["kind"] == "genetic" else ())   # germline exposure precedes disease
    blocks = []
    for oc, e in spec["effect"].items():
        if oc != "all_cause" and oc not in DISEASE_IDS:
            invalid.append(f"结局 {oc} 不是 all_cause 或已知疾病 id")
        ev = dict(ev0)
        ev.update(e.get("evidence") or {})
        blocks.append((oc, e, ev))
        if ev.get("grade") not in ("A", "B"):
            fail.append(f"{oc}: 证据等级 {ev.get('grade')} 低于 B")
        if (ev.get("design") or "").lower() not in designs:
            fail.append(f"{oc}: 研究设计 {ev.get('design') or '未写'} 不在入库范围 {designs}")
        dp = _check_derived(e)
        if dp:
            fail.append(f"{oc}: {dp}")
        for side in ("hr_below", "hr_above"):
            if isinstance(e.get(side), dict):
                dp = _check_derived(e[side])
                if dp:
                    fail.append(f"{oc}.{side}: {dp}")
        for prob in direction_problems(spec, oc, e):
            fail.append(f"{oc}: {prob}")
    scr = spec.get("screening")
    if scr:
        ev = dict(ev0)
        ev.update(scr.get("evidence") or {})
        blocks.append(("screening", {"_screening": True, **scr["mortality_rr"]}, ev))
        if (ev.get("design") or "").lower() not in designs:
            fail.append(f"screening: 研究设计 {ev.get('design') or '未写'} 不在入库范围")
        if ev.get("grade") not in ("A", "B"):
            fail.append(f"screening: 证据等级 {ev.get('grade')} 低于 B")
        if scr.get("disease_id") not in DISEASE_IDS:
            invalid.append(f"screening.disease_id {scr.get('disease_id')} 未知")
    if not spec["effect"] and not scr:
        fail.append("effect 为空且不是筛查项")
    for oc, e, ev in blocks:
        key = source_key(ev)
        quote = norm_text(ev.get("quote") or "")
        if not key:
            fail.append(f"{oc}: 缺来源（pmid/doi/pmcid/source）")
            continue
        if not quote:
            fail.append(f"{oc}: 缺 quote")
            continue
        try:
            src = fetch_source(key, root, need=[quote], refresh=refresh, offline=offline)
            used.add(key)
        except PrivacyError:
            raise
        except Exception as ex:
            fail.append(f"{oc}: 来源 {key} 抓取失败 {type(ex).__name__}: {ex}")
            continue
        text = norm_text(src["text"])
        if quote.lower() not in text.lower():
            fail.append(f"{oc}: quote 不是 {key} 原文的子串（空白归一化后）")
            continue
        nums = [(f"screening.{k}", e[k]) for k in ("hr", "lo", "hi")] if e.get("_screening") else _effect_numbers(spec, oc, e)
        for label, x in nums:
            ctx = find_number(x, quote)
            checks.append({"term": tid, "source": key, "number": label, "value": x, "found": bool(ctx),
                           "context": ctx or ""})
            if not ctx:
                fail.append(f"{oc}: {label}={x} 未在 quote 中逐字出现")
        groups3: Dict[str, dict] = {}
        for label, x in nums:
            pre, _, k = label.rpartition(".")
            groups3.setdefault(pre, {})[k] = x
        for pre, g in groups3.items():
            if all(k in g for k in ("hr", "lo", "hi")) and not find_triplet(g["hr"], g["lo"], g["hi"], quote):
                fail.append(f"{pre}: HR {g['hr']} 与 CI {g['lo']}–{g['hi']} 未在 quote 中成组出现（数值与原文结论未绑定）")
            if all(k in g for k in ("hr", "lo", "hi")) and g["lo"] <= 1.0 <= g["hi"]:
                msg = f"{pre}: 95% CI {g['lo']}–{g['hi']} 含 1（无统计学意义）"
                # a non-significant level inside a categorical term is acceptable; a main estimate is not
                (warn if spec["transform"]["shape"] == "categorical" and not e.get("_screening") else fail).append(msg)
        pop = dict(spec.get("population") or {})
        pop.update(e.get("population") or {})
        if pop.get("events") is not None and oc != "screening":
            ev_n = int(pop["events"])
            if ev_n < 100:
                fail.append(f"{oc}: 结局事件 {ev_n} < 100")
            elif not any(re.search(r"(?<![\d,.])" + re.escape(v) + r"(?![\d])", text) for v in _int_variants(ev_n)):
                warn.append(f"{oc}: 事件数 {ev_n} 未在来源文本中找到（可能在全文表格）")
        elif oc not in ("screening",):
            warn.append(f"{oc}: 未写结局事件数")
        anc = pop.get("ancestry") or ""
        tp = dict(spec.get("transport") or {})
        tp.update(e.get("transport") or {})
        if anc and not is_east_asian(anc):
            if tp.get("shrink", 1.0) > 0.8 + 1e-9 or tp.get("sd_inflate", 1.0) < 1.25 - 1e-9:
                fail.append(f"{oc}: 非东亚人群（{anc}）须 transport.shrink ≤0.8、sd_inflate ≥1.25")
        elif not anc:
            warn.append(f"{oc}: 未写人群族裔")
    # overlap rules, reference, groups
    r = overlap_rule(spec)
    if r:
        fail.append(r)
    if spec["kind"] in ("state", "exposure") and "all_cause" in spec["effect"]:
        grp = spec.get("group")
        groups = json.loads((root / "groups.json").read_text(encoding="utf-8")).get("groups", {}) if (root / "groups.json").exists() else {}
        if grp is not None and grp not in groups:
            fail.append(f"group {grp} 不在 groups.json")
    if spec["kind"] == "behavior" and not spec.get("behavior"):
        fail.append("行为项缺 behavior 块")
    try:
        expanded = expand_reference(spec)
        for oc in spec["effect"]:
            for sex in _sexes(expanded, oc):
                for lo, hi in AGE_BANDS:
                    log_mean_exp_ref(expanded, oc, sex, (lo + hi) / 2)
        rf = expanded.get("reference") or {}
        if not rf.get("source"):
            fail.append("reference.source 缺失")
        rkey = source_key({k: rf[k] for k in ("pmid", "doi", "pmcid") if rf.get(k)}) \
            if (rf.get("pmid") or rf.get("doi") or rf.get("pmcid")) else None
        if rkey and rf.get("quote"):
            rq = norm_text(rf["quote"])
            rsrc = fetch_source(rkey, root, need=[rq], refresh=refresh, offline=offline)
            used.add(rkey)
            if rq.lower() not in norm_text(rsrc["text"]).lower():
                fail.append(f"reference.quote 不是 {rkey} 原文的子串")
            else:
                info.append(f"参考分布原句已核对（{rkey}）")
        elif not rf.get("from_norms") and rf.get("kind") not in ("residualized",):
            warn.append("参考分布未给 pmid+quote，数值未经原文核对")
    except Exception as ex:
        fail.append(f"参考分布不可用：{ex}")
    for k in list(_adjusted_set(spec)) + list(((spec.get("overlap") or {}).get("mediated_by") or {}).keys()):
        if not (k in ("age", "sex") or k in CORE_IDS or k.startswith("ext.") or re.match(r"^[A-Z]+[0-9]*:", k)
                or re.match(r"^[a-z_]+$", k)):
            warn.append(f"adjusted_for/mediated_by 用词 {k} 不在约定词表")
    verdict = "invalid" if invalid else ("qualitative" if fail else "auto_accept")
    return {"id": tid, "verdict": verdict, "invalid": invalid, "fail": fail, "warn": warn, "info": info, "checks": checks,
            "sources": sorted(used)}


# ----------------------------------------------------------------------------- reference expansion

def _norms() -> dict:
    return json.loads((DATA_DIR / "population_norms_china.json").read_text(encoding="utf-8"))


def expand_reference(spec: dict) -> dict:
    """`reference.from_norms: <marker>` copies that marker's table from data/population_norms_china.json."""
    t = copy.deepcopy(spec)
    ref = t.get("reference") or {}
    m = ref.get("from_norms")
    if m:
        tab = _norms()["markers"][m]
        rows = []
        for sex in ("M", "F"):
            for r in tab[sex]:
                row = {"sex": sex, "age_lo": r["age_lo"], "age_hi": min(r["age_hi"], 99)}
                for k in ("mean", "sd", "p"):
                    if k in r:
                        row[k] = r[k]
                rows.append(row)
        ref = {k: v for k, v in ref.items() if k != "from_norms"}
        ref["by_sex_age"] = rows
        ref.setdefault("kind", "categorical" if "p" in rows[0] else "normal")
        ref["source"] = (ref.get("source", "") + "；" if ref.get("source") else "") + \
            f"data/population_norms_china.json markers.{m}（{_norms().get('note', '')}）"
        t["reference"] = ref
    return t


# ----------------------------------------------------------------------------- add / version

def bump_version(root: Path, today: Optional[_dt.date] = None) -> str:
    today = today or _dt.date.today()
    d = today.strftime("%Y.%m.%d")
    cur = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").exists() else ""
    n = 1
    if cur.startswith(d + "-"):
        n = int(cur.split("-")[1]) + 1
    return f"{d}-{n}"


def _all_terms(root: Path) -> List[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "terms").glob("*.json"))]


def add(specs: List[dict], root: Path = RG.REG_DIR, qualitative: bool = False, why: Optional[str] = None,
        replace: bool = False, offline: bool = False, today: Optional[_dt.date] = None, n_pop: int = 20000) -> dict:
    """Verify, write, population-check and freeze. Nothing is written if any spec or the population check fails."""
    version = bump_version(root, today)
    plans, msgs = [], []
    for spec in specs:
        res = verify(spec, root, offline=offline)
        if res["verdict"] == "invalid":
            return {"ok": False, "error": f"{spec.get('id')}: 无效，不能入库：" + "；".join(res["invalid"])}
        sub = "qualitative" if (qualitative or res["verdict"] == "qualitative") else "terms"
        if sub == "qualitative" and not qualitative:
            return {"ok": False, "error": f"{spec['id']}: 未通过自动入库标准，须加 --qualitative：" + "；".join(res["fail"])}
        t = expand_reference(spec)
        t.pop("verdict_intended", None)       # drafting note, not part of the contract
        ev = t["evidence"]
        ev["verified_at"] = (today or _dt.date.today()).isoformat()
        ev["verifier"] = VERIFIER
        ev["numbers_verified"] = bool(res["checks"]) and all(c["found"] for c in res["checks"])
        t.setdefault("status", "active")
        t["added_by"] = "longpi-term-builder"
        t["registry_version_added"] = version
        if sub == "qualitative":
            reasons = res["fail"]
            t["why_qualitative_zh"] = why or t.get("why_qualitative_zh") or "；".join(reasons) or "未说明"
            t["verifier_reasons"] = reasons
        for other in ("terms", "qualitative"):
            q = root / other / f"{t['id']}.json"
            if q.exists() and not replace:
                return {"ok": False, "error": f"{t['id']} 已在 {other}/，替换须加 --replace"}
        plans.append((sub, t, res))
    # population check on the would-be registry
    cur = {x["id"]: x for x in _all_terms(root)}
    for sub, t, _ in plans:
        if sub == "terms":
            cur[t["id"]] = t
        else:
            cur.pop(t["id"], None)
    pc = check_population(list(cur.values()), n=n_pop)
    if not pc["ok"]:
        return {"ok": False, "error": "人群中性检查未通过，不冻结：" + "；".join(pc["fails"][:12])}
    for sub, t, res in plans:
        for other in ("terms", "qualitative"):
            q = root / other / f"{t['id']}.json"
            if q.exists():
                q.unlink()
        d = root / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{t['id']}.json").write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        by_src: Dict[str, list] = {k: [] for k in res.get("sources", [])}
        for c in res["checks"]:
            by_src.setdefault(c["source"], []).append({k: c[k] for k in ("term", "number", "value", "found", "context")})
        for key, cs in by_src.items():
            sp, cp = _src_path(root, key), _cache_path(key)
            s = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
            if cp.exists():   # newest fetched text; keep the registry's check history
                c_rec = json.loads(cp.read_text(encoding="utf-8"))
                s = {**c_rec, "checks": s.get("checks", [])}
            if not s:
                continue
            s["checks"] = [c for c in s.get("checks", []) if c["term"] != t["id"]] + cs
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        msgs.append(f"{t['id']} → {sub}/")
    man = RG.freeze(root, version)
    return {"ok": True, "version": version, "digest": man["digest"], "written": msgs}


# ----------------------------------------------------------------------------- CLI

def _load_spec(p: str) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _print_verify(res: dict) -> None:
    print(f"== {res['id']}: {res['verdict']}")
    for k, lab in (("invalid", "无效"), ("fail", "未达标"), ("warn", "提示"), ("info", "信息")):
        for m in res.get(k, []):
            print(f"  [{lab}] {m}")
    for c in res.get("checks", []):
        print(f"  [核对] {c['number']}={c['value']} {'找到' if c['found'] else '未找到'}  {c['context'][:100]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="term_builder")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("specs", nargs="+")
    v.add_argument("--offline", action="store_true")
    v.add_argument("--refresh", action="store_true")
    v.add_argument("--json", action="store_true")
    a = sub.add_parser("add")
    a.add_argument("specs", nargs="+")
    a.add_argument("--qualitative", action="store_true")
    a.add_argument("--why")
    a.add_argument("--replace", action="store_true")
    a.add_argument("--offline", action="store_true")
    c = sub.add_parser("check-population")
    c.add_argument("--n", type=int, default=20000)
    c.add_argument("--json", action="store_true")
    li = sub.add_parser("list")
    li.add_argument("--qualitative", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("id")
    ap.add_argument("--root", default=str(RG.REG_DIR))
    args = ap.parse_args(argv)
    root = Path(args.root)
    if args.cmd == "verify":
        rc = 0
        out = []
        for p in args.specs:
            res = verify(_load_spec(p), root, offline=args.offline, refresh=args.refresh)
            out.append(res)
            if not args.json:
                _print_verify(res)
            rc |= 0 if res["verdict"] == "auto_accept" else (2 if res["verdict"] == "invalid" else 1)
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=1))
        return rc
    if args.cmd == "add":
        res = add([_load_spec(p) for p in args.specs], root, qualitative=args.qualitative, why=args.why,
                  replace=args.replace, offline=args.offline)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0 if res["ok"] else 1
    if args.cmd == "check-population":
        res = check_population(_all_terms(root), n=args.n)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        else:
            print(f"人群中性检查：{'通过' if res['ok'] else '未通过'}（n={res['n']}，容差 {res['tol']}，"
                  f"引擎归一化对照：{'有' if res['engine_normaliser'] else '无（引擎未提供 lp.terms.log_mean_exp_ref）'}）")
            worst = sorted(res["rows"], key=lambda r: -abs(r["mean_exp"] - 1))[:5]
            for r in worst:
                print(f"  偏差最大：{r['term']} {r['outcome']} {r['sex']} {r['band']} 平均 {r['mean_exp']}")
            for r in res["combined"]:
                print(f"  合计 {r['part']} {r['sex']} {r['band']}（{r['n_terms']} 项）平均 {r['mean_exp']}")
            for f in res["fails"]:
                print("  [未通过] " + f)
        return 0 if res["ok"] else 1
    if args.cmd == "list":
        d = root / ("qualitative" if args.qualitative else "terms")
        for p in sorted(d.glob("*.json")):
            t = json.loads(p.read_text(encoding="utf-8"))
            if t.get("core"):
                print(f"{t['id']:34s} core   {t.get('name_zh', '')}")
                continue
            ocs = ",".join(t.get("effect", {}).keys()) or ("screening:" + t.get("screening", {}).get("disease_id", "") if t.get("screening") else "")
            print(f"{t['id']:34s} {t.get('kind', ''):9s} {t.get('input', {}).get('code', ''):28s} {ocs:30s} {t.get('name_zh', '')}")
        return 0
    if args.cmd == "show":
        for sd in ("terms", "qualitative"):
            p = root / sd / f"{args.id}.json"
            if p.exists():
                print(p.read_text(encoding="utf-8"))
                return 0
        print(f"未找到 {args.id}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
