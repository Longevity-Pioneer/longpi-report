"""Term registry: every quantity that can enter LongPi Age, disease risk or the 120 Index (engine 1.1.2).

Layout (skills/longpi-report/registry/):

  VERSION                    e.g. 2026.11.18-1
  MANIFEST.json              sha256 of every file below; checked on load
  terms/<id>.json            terms counted in numbers
                               core.*      the 1.1.1 model (10 domains, PhenoAge clock calibration, methylation);
                                           read back into the classic parameter dict by `classic_params()`
                               ext.*       terms added through the term builder (state / exposure / behavior / genetic)
  qualitative/<id>.json      shown as supporting evidence only, never in numbers
  groups.json                overlap (mechanism) groups and their caps
  outcomes/<id>.json         disease definitions and Chinese baseline incidence
  sources/<key>.json         fetched source text and the verification record of each number

The runtime is offline: it only reads a frozen version. `freeze()` rewrites MANIFEST after a change; the
term builder calls it, nothing in the report path does.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

SKILL_DIR = Path(__file__).resolve().parents[2]
REG_DIR = Path(os.environ.get("LONGPI_REGISTRY_DIR", SKILL_DIR / "registry"))

KINDS = ("state", "exposure", "behavior", "genetic")
SHAPES = ("loglinear", "hinge", "categorical", "residualized", "indicator")
GRADES = ("A", "B", "C", "D")


class RegistryError(RuntimeError):
    pass


def _read(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


DATA_FILES = ("params.json", "observation_codes.json", "population_norms_china.json", "systems.json")
ID_RE = __import__("re").compile(r"^(core|ext)\.[a-z0-9_]{1,60}$")


def _files(root: Path) -> List[Path]:
    out = []
    data = root.parent / "data"      # the engine-wide data files are part of the frozen state too
    for name in DATA_FILES:
        if (data / name).exists():
            out.append(data / name)
    for sub in ("terms", "qualitative", "outcomes", "sources", "candidates"):
        d = root / sub
        if d.is_dir():
            out += sorted(x for x in d.glob("*.json"))
    for name in ("groups.json", "VERSION"):
        if (root / name).exists():
            out.append(root / name)
    return out


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return "../data/" + p.name


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def freeze(root: Path = REG_DIR, version: Optional[str] = None) -> dict:
    """Write VERSION (if given) and MANIFEST.json; returns the manifest."""
    if version:
        (root / "VERSION").write_text(version + "\n", encoding="utf-8")
    files = {_rel(p, root): _sha(p) for p in _files(root)}
    body = json.dumps(files, sort_keys=True, ensure_ascii=False)
    man = {"version": (root / "VERSION").read_text(encoding="utf-8").strip(), "files": files,
           "digest": hashlib.sha256(body.encode("utf-8")).hexdigest()}
    (root / "MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    load.cache_clear()
    return man


def verify_manifest(root: Path = REG_DIR) -> dict:
    mp = root / "MANIFEST.json"
    if not mp.exists():
        raise RegistryError(f"项目库缺少 MANIFEST.json：{root}")
    man = _read(mp)
    have = {_rel(p, root): _sha(p) for p in _files(root)}
    bad = sorted(k for k in set(have) | set(man["files"]) if have.get(k) != man["files"].get(k))
    if bad:
        raise RegistryError("项目库文件与 MANIFEST 不一致（未冻结的改动或被篡改）：" + "，".join(bad[:10]))
    return man


@lru_cache(maxsize=4)
def load(root: Optional[str] = None) -> dict:
    """The frozen registry as one dict: {version, digest, terms, qualitative, groups, outcomes}."""
    r = Path(root) if root else Path(REG_DIR)
    man = verify_manifest(r)
    terms = {}
    for p in sorted((r / "terms").glob("*.json")):
        t = _read(p)
        if t.get("status", "active") != "active":
            continue
        if not ID_RE.match(str(t.get("id", ""))) or p.stem != t["id"]:
            raise RegistryError(f"项目库条目 id 不合规或与文件名不符：{p.name}")
        if t["id"] in terms:
            raise RegistryError(f"项目库条目重复：{t['id']}")
        if not t.get("core"):
            prob = validate_term(t)
            if prob:
                raise RegistryError(f"项目库条目 {t['id']} 不合规：" + "；".join(prob[:3]))
        terms[t["id"]] = t
    qual = {(_read(p))["id"]: _read(p) for p in sorted((r / "qualitative").glob("*.json"))} if (r / "qualitative").is_dir() else {}
    outcomes = {(_read(p))["id"]: _read(p) for p in sorted((r / "outcomes").glob("*.json"))} if (r / "outcomes").is_dir() else {}
    groups = _read(r / "groups.json") if (r / "groups.json").exists() else {"groups": {}}
    return {"version": man["version"], "digest": man["digest"], "terms": terms, "qualitative": qual,
            "groups": groups, "outcomes": outcomes, "root": str(r)}


def overridden() -> bool:
    """True when the registry is not the one shipped with the skill (LONGPI_REGISTRY_DIR or registry.use)."""
    return Path(REG_DIR).resolve() != Path(SKILL_DIR / "registry").resolve()


def use(root) -> None:
    """Point the process at another registry directory (tests, staging); clears every cache that read the old one."""
    global REG_DIR
    REG_DIR = Path(root)
    load.cache_clear()
    from . import params as PR
    PR.load.cache_clear()


def source(key: str, root: Optional[str] = None) -> Optional[dict]:
    p = Path(root or REG_DIR) / "sources" / (safe_key(key) + ".json")
    if not p.exists():
        return None
    rec = _read(p)
    if rec.get("key") not in (None, key):
        raise RegistryError(f"来源文件名冲突：{key} 与 {rec.get('key')}")
    return rec


def safe_key(key: str) -> str:
    """File name of a source record. Kept readable (existing records use it); an empty key is refused, and the
    record stores its original key so two keys mapping to one name are detected (`source()` checks it)."""
    if not key:
        raise RegistryError("来源键为空")
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in key).strip(".") or "_"


# ----------------------------------------------------------------------------- the 1.1.1 model

def core_terms(reg: Optional[dict] = None) -> List[dict]:
    reg = reg or load()
    return sorted((t for t in reg["terms"].values() if t.get("core")), key=lambda t: t.get("order", 0))


def ext_terms(reg: Optional[dict] = None) -> List[dict]:
    reg = reg or load()
    return [t for t in sorted(reg["terms"].values(), key=lambda t: t["id"]) if not t.get("core")]


def classic_params(params: dict, reg: Optional[dict] = None) -> dict:
    """params.json + the core terms -> the parameter dict the 1.1.1 engine used (domains, calibration, methylation,
    clock_residual). Order of domains is the registry `order` field, which keeps the random-number sequence identical."""
    reg = reg or load()
    p = copy.deepcopy(params)
    doms, with_c, without_c = [], {}, {}
    cal_meta = {}
    for t in core_terms(reg):
        eng = t.get("engine")
        if eng == "domain":
            doms.append(copy.deepcopy(t["spec"]))
            with_c[t["spec"]["id"]] = copy.deepcopy(t["coef_sets"]["with_clock"])
            without_c[t["spec"]["id"]] = copy.deepcopy(t["coef_sets"]["without_clock"])
        elif eng == "phenoage_clock":
            cal_meta = {"source": t["calibration_source"], "gap": copy.deepcopy(t["gap"])}
            p["clock_residual"] = copy.deepcopy(t["clock_residual"])
        elif eng == "methylation":
            p["methylation"] = copy.deepcopy(t["spec"])
    if not doms or not cal_meta or "methylation" not in p:
        raise RegistryError("项目库缺少 1.1.1 核心项（core.*）")
    p["domains"] = doms
    p["calibration"] = {"source": cal_meta["source"], "gap": cal_meta["gap"], "with_clock": with_c, "without_clock": without_c}
    return p


def validate_term(t: dict) -> List[str]:
    """Structural checks for an ext.* term (the verifier adds source checks). Returns problems."""
    pr = []
    need = ("id", "name_zh", "kind", "input", "transform", "reference", "effect", "evidence", "overlap", "license")
    for k in need:
        if k not in t:
            pr.append(f"缺字段 {k}")
    if pr:
        return pr
    if not ID_RE.match(str(t["id"])) or not t["id"].startswith("ext."):
        pr.append("新项 id 必须是 ext. 加小写字母、数字或下划线")
    if t["kind"] not in KINDS:
        pr.append(f"kind 必须是 {KINDS}")
    if t["transform"].get("shape") not in SHAPES:
        pr.append(f"transform.shape 必须是 {SHAPES}")
    if not t["input"].get("code"):
        pr.append("input.code（标准编码）缺失")
    ev = t["evidence"]
    if ev.get("grade") not in GRADES:
        pr.append("evidence.grade 必须是 A/B/C/D")
    shape = t["transform"].get("shape")

    def _hr_block(e: dict, where: str, need_per: bool = True) -> None:
        for k in ("hr", "lo", "hi") + (("per",) if need_per else ()):
            if k not in e:
                pr.append(f"{where} 缺 {k}")
        if all(k in e for k in ("hr", "lo", "hi")) and not (0 < e["lo"] <= e["hr"] <= e["hi"]):
            pr.append(f"{where}：须 0 < lo ≤ hr ≤ hi")

    for oc, e in t["effect"].items():
        if shape == "hinge":
            if not (e.get("hr_below") or e.get("hr_above")):
                pr.append(f"effect.{oc} 折线形状须有 hr_below 或 hr_above")
            for side in ("hr_below", "hr_above"):
                if e.get(side):
                    _hr_block(e[side], f"effect.{oc}.{side}")
        elif shape == "categorical":
            lv = e.get("levels") or {}
            if not lv:
                pr.append(f"effect.{oc} 分类形状须有 levels")
            for name, s in lv.items():
                if s.get("hr") == 1 and "lo" not in s:
                    continue
                _hr_block(s, f"effect.{oc}.levels.{name}", need_per=False)
        else:
            _hr_block(e, f"effect.{oc}", need_per=shape != "indicator")
        if e.get("direction") not in ("higher_worse", "higher_better", None):
            pr.append(f"effect.{oc}.direction 取值不对")
    lic = t["license"]
    if lic.get("commercial_use") is False:
        pr.append("许可不允许商业使用，不能入库")
    return pr


def write_core(calibration: Optional[dict] = None, methylation: Optional[dict] = None,
               clock_residual: Optional[dict] = None, root: Path = REG_DIR) -> dict:
    """Write evidence-pipeline results into the core terms (used by evidence/scripts/apply_*.py), then re-freeze.

    calibration: {"source", "gap", "with_clock": {domain: coef}, "without_clock": {...}} as the 1.1.1 params block."""
    tdir = root / "terms"
    if calibration is not None:
        for p in sorted(tdir.glob("core.*.json")):
            t = _read(p)
            if t.get("engine") == "domain":
                did = t["spec"]["id"]
                t["coef_sets"] = {"with_clock": calibration["with_clock"][did], "without_clock": calibration["without_clock"][did]}
                p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        p = tdir / "core.phenoage_clock.json"
        t = _read(p)
        t["gap"], t["calibration_source"] = calibration["gap"], calibration["source"]
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if clock_residual is not None:
        p = tdir / "core.phenoage_clock.json"
        t = _read(p)
        t["clock_residual"] = clock_residual
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if methylation is not None:
        p = tdir / "core.methylation.json"
        t = _read(p)
        t["spec"] = methylation
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return freeze(root)
