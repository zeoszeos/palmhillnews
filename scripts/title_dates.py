#!/usr/bin/env python3
"""STYLE-RULES.md R19 (Steven Oct 16 2026): no dates in item titles when a date line sits beneath; the date goes on its
own line under the title (Weekly Manager Update style). Idempotent; applied by the builder and safe on live/FINAL."""
import re, sys
DATELINE = '<div style="font-size:14px;color:#666666;margin-top:2px;">{d}</div>'
# (old title, new title, date line to insert if the row has none yet or None)
FIX = [("President&#x27;s Message — October 2026", "President&#x27;s Message", "Saturday, Oct 10, 2026"),
       ("Weekly Manager Update — October 16", "Weekly Manager Update", None),
       ("Shareholders Report — September 30 Board Meeting", "Shareholders Report", None)]
def fix(s):
    for old, new, d in FIX:
        i = s.find(">" + old + "<")
        if i < 0: continue
        s = s[:i + 1] + new + s[i + 1 + len(old):]
        if d:
            j = s.index("</table>", i) + len("</table>")
            if not s[j:j + 200].startswith(DATELINE.format(d=d)):
                s = s[:j] + DATELINE.format(d=d) + s[j:]
    return s
if __name__ == "__main__":
    for f in sys.argv[1:]:
        t = open(f, encoding="utf-8").read(); n = fix(t); open(f, "w", encoding="utf-8").write(n); print(("fixed " if n != t else "unchanged ") + f)
