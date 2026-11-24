"""Check the CSV against two implementations other than the one it was exported from (python-holidays).

    npm install date-holidays@3.39.2
    pip install holidays==0.109 workalendar==17.0.0
    python -m unittest discover -s tests -v

For each region and year, the holiday dates that fall on working days (Mon-Fri here) must equal
the same set from date-holidays (npm) or from workalendar, as listed in regions.csv checked_by_<year>.
"""
import csv
import json
import os
import subprocess
import unittest
import warnings
from collections import defaultdict
from datetime import date, timedelta

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
YEARS = (2026, 2027, 2028)


def load(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


ROWS, REGS = load("public_holidays_2026_2028.csv"), load("regions.csv")


def ours(observed):
    got = defaultdict(set)
    for r in ROWS:
        if r["is_weekend"] == "0" and (observed or r["is_observed_shift"] == "0"):
            got[(r["region"], int(r["date"][:4]))].add(date.fromisoformat(r["date"]))
    return got


class Data(unittest.TestCase):
    def test_flags(self):
        for r in ROWS:
            d = date.fromisoformat(r["date"])
            self.assertEqual(r["weekday"], d.strftime("%a"), r)
            self.assertEqual(r["is_weekend"], "1" if d.weekday() >= 5 else "0", r)
            self.assertIn(int(r["date"][:4]), YEARS)
        self.assertEqual({r["region"] for r in ROWS}, {r["region"] for r in REGS})

    def test_matches_independent_sources(self):
        dump = json.loads(subprocess.check_output(["node", os.path.join(HERE, "dump.js")] + [r["region"] for r in REGS], cwd=os.path.join(HERE, "..")))
        from workalendar.registry import registry
        W = registry.get_calendars(include_subregions=True)
        raw, allx = ours(False), ours(True)
        for reg in REGS:
            g = reg["region"]
            for y in YEARS:
                by = reg[f"checked_by_{y}"].split(";")
                self.assertTrue(by and by[0], (g, y))
                ok = []
                if "date-holidays" in by:
                    dr, da = set(), set()
                    for d, n, sub in dump[g][str(y)]:
                        for i in range(n):
                            x = date.fromisoformat(d) + timedelta(i)
                            if x.weekday() < 5:
                                da.add(x)
                                if not sub:
                                    dr.add(x)
                    ok.append(dr == raw[(g, y)] or da == allx[(g, y)])
                if "workalendar" in by:
                    wd = {d for d, _n in W[g]().holidays(y) if d.weekday() < 5}
                    ok.append(wd in (raw[(g, y)], allx[(g, y)]))
                self.assertTrue(all(ok), (g, y, by, ok))


if __name__ == "__main__":
    unittest.main()
