#!/usr/bin/env python3
"""Flag abbreviated months in titles/headings/subtitle bands (STYLE-RULES.md rule 3). Exit 1 if any."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_rules import title_month_violations
bad = 0
for f in sys.argv[1:]:
    for ln, t in title_month_violations(open(f, encoding="utf-8", errors="ignore").read()):
        print(f"{f}:{ln}: {t}"); bad += 1
sys.exit(1 if bad else 0)
