"""Dual independent build rule (2026-11-20): a term counts only where two independent builds agree."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import consensus as CN  # noqa: E402


def spec(hr, lo, hi, per=1.0, events=500, shape="loglinear", pmid="1"):
    return {"id": "ext.x", "input": {"code": "LOINC:1-1"}, "transform": {"shape": shape},
            "effect": {"all_cause": {"hr": hr, "lo": lo, "hi": hi, "per": per}},
            "population": {"events": events}, "evidence": {"pmid": pmid}}


class Consensus(unittest.TestCase):
    def test_agree_on_rescaled_units(self):
        a = spec(1.10, 1.05, 1.15, per=10)            # per 10 units
        b = spec(1.0096, 1.0049, 1.0141, per=1)       # same effect per 1 unit
        c = CN.compare(a, b)
        self.assertTrue(c["outcomes"]["all_cause"]["agree"], c)
        m, dropped = CN.merge(a, b, c)
        self.assertIsNotNone(m)
        self.assertEqual(m["evidence"]["replication"]["pmid"], "1")

    def test_disagree(self):
        c = CN.compare(spec(1.07, 1.05, 1.10, per=100), spec(1.18, 1.15, 1.20, per=100))
        self.assertFalse(c["outcomes"]["all_cause"]["agree"])
        self.assertIn("每 100 单位", c["outcomes"]["all_cause"]["why"][0])
        self.assertIsNone(CN.merge(spec(1.07, 1.05, 1.10), spec(1.18, 1.15, 1.20), c)[0])

    def test_more_events_wins_and_missing_outcome_dropped(self):
        a = spec(1.10, 1.02, 1.20, events=200, pmid="A")
        b = spec(1.12, 1.05, 1.19, events=9000, pmid="B")
        b["effect"]["chd"] = {"hr": 1.3, "lo": 1.1, "hi": 1.5, "per": 1}
        c = CN.compare(a, b)
        m, dropped = CN.merge(a, b, c)
        self.assertEqual(m["evidence"]["pmid"], "B")
        self.assertNotIn("chd", m["effect"])
        self.assertTrue(any(d.startswith("chd") for d in dropped))

    def test_hinge_knots_must_match(self):
        a = spec(1.2, 1.1, 1.3, shape="hinge")
        a["transform"]["knot_lo"] = 20
        a["effect"]["all_cause"] = {"hr_below": {"hr": 1.2, "lo": 1.1, "hi": 1.3, "per": 1}}
        b = {**a, "transform": {"shape": "hinge", "knot_lo": 25}}
        self.assertFalse(CN.compare(a, b)["agree_any"])


if __name__ == "__main__":
    unittest.main()
