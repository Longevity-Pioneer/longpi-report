"""Strict input validation (engine 1.1.2): types, finite numbers, full-match dates, plausible ranges, codes.

`check` and `compute` both call `validate(person, base)`; any error stops `compute` before the model runs, so a
plausible-but-wrong input gives a one-line message instead of a traceback or a silently wrong number.
"""
from __future__ import annotations

import json
import math
import re
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?)?)?$")
ICD_RE = re.compile(r"^[A-Z]\d{2}(\.[0-9A-Z]{1,4})?$")
CODE_RE = re.compile(r"^[A-Z0-9]{2,12}:[^\s]{1,80}$")
MED_CLASSES = {"antihypertensive", "statin", "lipid_lowering", "antidiabetic", "urate_lowering", "anticoagulant", "antiplatelet",
               "other", ""}
SMOKING = {"never", "former", "current"}
VITAL_RANGES = {"sbp": (60, 260), "dbp": (30, 160), "pulse": (25, 200)}
ANTH_RANGES = {"height_cm": (100, 230), "weight_kg": (20, 300), "waist_cm": (40, 200), "bmi": (10, 80)}
FIT_RANGES = {"vo2max": (8, 90), "grip_kg": (2, 100)}


def finite(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def norm_icd10(v) -> Optional[str]:
    """'e11.9 ' / 'ICD10:E11' -> 'E11.9' / 'E11'; None if it is not an ICD-10 code."""
    if not isinstance(v, str):
        return None
    s = v.strip().upper()
    if s.startswith("ICD10:"):
        s = s[6:].strip()
    return s if ICD_RE.match(s) else None


def _date_ok(s, today: Optional[date] = None, allow_future_days: int = 0) -> Tuple[bool, str]:
    if not isinstance(s, str) or not DATE_RE.match(s.strip()):
        return False, "日期格式应为 YYYY、YYYY-MM、YYYY-MM-DD 或 YYYY-MM-DD HH:MM"
    try:
        from .engine import parse_date
        d = parse_date(s.strip())
    except ValueError:
        return False, "日期不存在"
    if d.year < 1900:
        return False, "日期早于 1900 年"
    if today and (d - today).days > allow_future_days:
        return False, "日期晚于数据截至日期"
    return True, ""


def _list_of_dicts(person: dict, key: str, errors: List[str]) -> list:
    if key not in person:
        return []
    v = person.get(key)
    if v is None:
        errors.append(f"{key} 不能是 null（没有就删去这个字段或写 []）")
        return []
    if not isinstance(v, list) or not all(isinstance(x, dict) for x in v):
        errors.append(f"{key} 必须是对象列表")
        return []
    return v


def _ranges() -> dict:
    from .observations import codes
    return codes().get("ranges", {})


def validate(person, base: Optional[Path] = None) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warn: List[str] = []
    if not isinstance(person, dict):
        return ["person.json 的最外层必须是对象"], []
    p = person.get("person")
    if not isinstance(p, dict):
        return ["缺少 person 对象"], []
    if not isinstance(p.get("sex"), str) or p["sex"].strip().upper()[:1] not in ("M", "F"):
        errors.append("person.sex 必须是 M 或 F")
    as_of = None
    ok, why = _date_ok(person.get("as_of"))
    if not ok:
        errors.append(f"as_of：{why}")
    else:
        from .engine import parse_date
        as_of = parse_date(person["as_of"])
        if as_of > date.today().replace(year=date.today().year + 1) or as_of.year < 2000:
            errors.append(f"as_of {person['as_of']} 不合理（应在 2000 年到明年之间）")
    if "age" in p:
        if not finite(p["age"]) or not (18 <= p["age"] <= 100):
            errors.append("person.age 必须是 18–100 之间的数字")
    elif "birth" in p:
        ok, why = _date_ok(p["birth"])
        if not ok:
            errors.append(f"person.birth：{why}")
        elif as_of:
            from .engine import parse_date
            age = (as_of - parse_date(p["birth"])).days / 365.25
            if not (18 <= age <= 100):
                errors.append(f"按出生年月算得年龄 {age:.0f} 岁，不在 18–100 岁")
    else:
        errors.append("person.age 或 person.birth（YYYY-MM）至少给一个")

    seen_lab_dates = set()
    for i, l in enumerate(_list_of_dicts(person, "labs", errors)):
        ok, why = _date_ok(l.get("date"), as_of)
        if not ok:
            errors.append(f"labs[{i}].date：{why}")
        elif l["date"] in seen_lab_dates:
            warn.append(f"labs[{i}]：{l['date']} 有两次化验，同一天应合并为一条")
        seen_lab_dates.add(l.get("date"))
        items = l.get("items")
        if not isinstance(items, dict):
            errors.append(f"labs[{i}].items 必须是对象")
            continue
        for k, v in items.items():
            val = v[0] if isinstance(v, list) and v else (v.get("value") if isinstance(v, dict) else v)
            if not finite(val):
                errors.append(f"labs[{i}].{k} 的数值不是有限数字：{v!r}")
            elif val <= 0 and k not in ("lymph_pct",):
                errors.append(f"labs[{i}].{k} 必须为正数：{val}")
            else:
                from .schema import RANGES
                from . import units as UU
                lo_hi = RANGES.get(k)
                unit = v[1] if isinstance(v, list) and len(v) > 1 else (v.get("unit") if isinstance(v, dict) else None)
                try:
                    cv = UU.to_canonical("glucose" if k == "glucose_fasting" else k, float(val), unit)
                except (TypeError, ValueError):
                    cv = None
                if lo_hi and cv is not None and not (lo_hi[0] / 5 <= cv <= lo_hi[1] * 5):
                    errors.append(f"labs[{i}].{k}={val} {unit or ''} 远超可能范围（{lo_hi[0]}–{lo_hi[1]}），多半是单位或录入错误")
        fl = l.get("flags")
        if fl is not None and (not isinstance(fl, list) or not all(isinstance(x, str) for x in fl)):
            errors.append(f"labs[{i}].flags 必须是字符串列表")
    for sec, rng in (("vitals", VITAL_RANGES), ("anthropometrics", ANTH_RANGES), ("fitness", FIT_RANGES)):
        for i, v in enumerate(_list_of_dicts(person, sec, errors)):
            ok, why = _date_ok(v.get("date"), as_of)
            if not ok:
                errors.append(f"{sec}[{i}].date：{why}")
            for k, (lo, hi) in rng.items():
                if k in v and v[k] is not None and (not finite(v[k]) or not (lo <= v[k] <= hi)):
                    errors.append(f"{sec}[{i}].{k}={v[k]!r} 不在 {lo}–{hi}")
    ls = person.get("lifestyle")
    if ls is not None:
        if not isinstance(ls, dict):
            errors.append("lifestyle 必须是对象")
        else:
            sm = ls.get("smoking")
            if sm is not None and (not isinstance(sm, dict) or sm.get("status") not in SMOKING):
                errors.append("lifestyle.smoking.status 必须是 never / former / current")
            al = ls.get("alcohol")
            if isinstance(al, dict):
                for k in ("grams_per_week", "grams_per_day"):
                    if k in al and (not finite(al[k]) or al[k] < 0 or al[k] > (3000 if k == "grams_per_week" else 500)):
                        errors.append(f"lifestyle.alcohol.{k}={al[k]!r} 不合理")
            if "sleep_h" in ls and (not finite(ls["sleep_h"]) or not (2 <= ls["sleep_h"] <= 16)):
                errors.append(f"lifestyle.sleep_h={ls['sleep_h']!r} 不在 2–16 小时")
            for k, hi in (("mvpa_min_week", 3000), ("resistance_sessions_week", 21)):
                v = ls.get(k)
                if v is None:
                    continue
                if not isinstance(v, dict) or not finite(v.get("value")) or not (0 <= v["value"] <= hi):
                    errors.append(f"lifestyle.{k} 须写成 {{\"value\": 数字, \"since\": \"YYYY-MM\"}}，数值 0–{hi}")
                elif v.get("since") is not None and not _date_ok(v["since"], as_of)[0]:
                    errors.append(f"lifestyle.{k}.since 日期无效")
    for i, c in enumerate(_list_of_dicts(person, "conditions", errors)):
        if norm_icd10(c.get("icd10")) is None:
            errors.append(f"conditions[{i}]「{c.get('name', '')}」缺少有效的 icd10（如 E11、I10）：没有编码的诊断无法判断“已确诊”，"
                          "会被当成未发生而给出发病风险")
        if c.get("diagnosed") is not None and not _date_ok(str(c["diagnosed"]), as_of)[0]:
            errors.append(f"conditions[{i}].diagnosed 日期无效")
    for i, m in enumerate(_list_of_dicts(person, "medications", errors)):
        if m.get("class") is not None and (not isinstance(m.get("class"), str) or m["class"] not in MED_CLASSES):
            errors.append(f"medications[{i}].class 必须是 {sorted(x for x in MED_CLASSES if x)} 之一")
        for k in ("since", "until"):
            if m.get(k) is not None and not _date_ok(str(m[k]), as_of, 3660 if k == "until" else 0)[0]:
                errors.append(f"medications[{i}].{k} 日期无效")
        if m.get("class") and not m.get("since"):
            warn.append(f"medications[{i}]「{m.get('name', '')}」没有 since：无法判断哪些化验在用药期间")
    try:
        from . import registry as RG
        outcome_ids = set(RG.load()["outcomes"])
        screen_tests = {t["input"]["code"][10:] for t in RG.load()["terms"].values() if t["input"]["code"].startswith("LP:screen.")}
    except Exception:  # noqa: BLE001 - registry problems are reported by compute
        outcome_ids, screen_tests = set(), set()
    for i, f in enumerate(_list_of_dicts(person, "family_history", errors)):
        did = f.get("disease_id")
        if did is None:
            warn.append(f"family_history[{i}]「{f.get('condition', '')}」没有 disease_id：家族史不进入疾病风险")
        elif not isinstance(did, str) or (outcome_ids and did not in outcome_ids):
            errors.append(f"family_history[{i}].disease_id「{did}」不在疾病清单 {sorted(outcome_ids)}")
    for i, s in enumerate(_list_of_dicts(person, "screenings", errors)):
        if not isinstance(s.get("test"), str) or (screen_tests and s["test"] not in screen_tests):
            errors.append(f"screenings[{i}].test 必须是 {sorted(screen_tests)} 之一")
        if not _date_ok(str(s.get("date")), as_of)[0]:
            errors.append(f"screenings[{i}].date 日期无效或晚于数据截至日期")
    for i, im in enumerate(_list_of_dicts(person, "imaging", errors)):
        ms = im.get("measures")
        if ms is not None:
            if not isinstance(ms, dict):
                errors.append(f"imaging[{i}].measures 必须是对象")
            else:
                rng = _ranges()
                for k, v in ms.items():
                    if not finite(v):
                        errors.append(f"imaging[{i}].measures.{k} 不是有限数字")
                    elif ("LP:" + k) in rng and not (rng["LP:" + k][0] <= v <= rng["LP:" + k][1]):
                        errors.append(f"imaging[{i}].measures.{k}={v} 不在合理范围 {rng['LP:' + k]}")
    for i, r in enumerate(_list_of_dicts(person, "methylation", errors)):
        for k, (lo, hi) in (("bio_age", (5, 130)), ("chrono_age", (10, 110))):
            if r.get(k) is not None and (not finite(r[k]) or not (lo <= r[k] <= hi)):
                errors.append(f"methylation[{i}].{k}={r[k]!r} 不在 {lo}–{hi}")
    gp = person.get("genetic_preferences")
    if gp is not None:
        if not isinstance(gp, dict):
            errors.append("genetic_preferences 必须是对象")
        else:
            for k, v in gp.items():
                if not isinstance(v, bool):
                    errors.append(f"genetic_preferences.{k} 必须是 true 或 false（JSON 布尔值），现在是 {v!r}")
    for key in ("observations_file",):
        f = person.get(key)
        if f is not None and (not isinstance(f, str) or Path(f).is_absolute() or ".." in Path(f).parts):
            warn.append(f"{key} 建议写成工作文件夹内的相对路径")
    w = person.get("wearables")
    if isinstance(w, dict):
        for k, v in w.items():
            if k != "device" and isinstance(v, str) and (Path(v).is_absolute() or ".." in Path(v).parts):
                warn.append(f"wearables.{k} 建议写成工作文件夹内的相对路径")
    if person.get("observations_file") and base is not None and isinstance(person["observations_file"], str):
        errors += validate_observations_file(Path(base) / person["observations_file"] if not Path(person["observations_file"]).is_absolute()
                                             else Path(person["observations_file"]), as_of)
    return errors, warn


def validate_observations_file(f: Path, as_of: Optional[date]) -> List[str]:
    errs: List[str] = []
    if not f.exists():
        return [f"observations_file 不存在：{f.name}"]
    try:
        doc = json.loads(f.read_text(encoding="utf-8"), parse_constant=lambda c: math.nan)
    except ValueError as e:
        return [f"observations_file 不是合法 JSON：{e}"]
    if not isinstance(doc, dict) or doc.get("schema") != "longpi.observations/1":
        return ["observations_file 的最外层必须是对象，且 schema 为 longpi.observations/1"]
    obs = doc.get("observations", [])
    if not isinstance(obs, list):
        return ["observations 必须是列表"]
    rng = _ranges()
    for j, o in enumerate(obs[:200000]):
        if not isinstance(o, dict):
            errs.append(f"observations[{j}] 必须是对象")
            continue
        code = o.get("code")
        if not isinstance(code, str) or not CODE_RE.match(code):
            errs.append(f"observations[{j}].code 必须是“命名空间:值”的标准编码")
            continue
        v = o.get("value")
        if isinstance(v, str):
            if len(v) > 40:
                errs.append(f"observations[{j}]（{code}）的分类值过长")
        elif not finite(v):
            errs.append(f"observations[{j}]（{code}）的 value 必须是有限数字或分类名")
        elif code in rng and not (rng[code][0] <= v <= rng[code][1]):
            errs.append(f"observations[{j}]（{code}）= {v} 不在合理范围 {rng[code][0]}–{rng[code][1]}（多半是单位错误）")
        if o.get("datetime") is not None and not _date_ok(str(o["datetime"]), as_of, 1)[0]:
            errs.append(f"observations[{j}]（{code}）的 datetime 无效或晚于数据截至日期")
        if o.get("sd") is not None and (not finite(o["sd"]) or o["sd"] < 0):
            errs.append(f"observations[{j}]（{code}）的 sd 必须是非负数字")
        fl = o.get("flags")
        if fl is not None and (not isinstance(fl, list) or not all(isinstance(x, str) for x in fl)):
            errs.append(f"observations[{j}]（{code}）的 flags 必须是字符串列表")
        if o.get("sustained_weeks") is not None and (not finite(o["sustained_weeks"]) or o["sustained_weeks"] < 0):
            errs.append(f"observations[{j}]（{code}）的 sustained_weeks 必须是非负数字")
        if len(errs) > 50:
            errs.append("……错误过多，只列前 50 条")
            break
    g = doc.get("genetics")
    if g is not None:
        if not isinstance(g, dict):
            errs.append("genetics 必须是对象")
        else:
            for k in ("prs", "monogenic", "pgx"):
                if g.get(k) is not None and (not isinstance(g[k], list) or not all(isinstance(x, dict) for x in g[k])):
                    errs.append(f"genetics.{k} 必须是对象列表")
    return errs
