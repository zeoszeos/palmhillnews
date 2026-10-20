"""Run the Oct 11 locked checks on the Oct 18 draft with Oct 18 expectations (content lists only; rules unchanged)."""
import json, sys, importlib.util
from pathlib import Path
H=Path(__file__).parent
spec=importlib.util.spec_from_file_location("lc",H/"locked_checks_oct25.py");lc=importlib.util.module_from_spec(spec);spec.loader.exec_module(lc)
a=json.load(open(H.parent/"build-audit-oct25.json"))
lc.MEETINGS_EXPECTED=[n for d,n in a["meetings"]]
lc.THIS_WEEK_EXPECTED=[n for d,n in a["this_week"]]
lc.UPCOMING_EXPECTED=[n for d,n in a["upcoming"]]
page=(H.parent/"PHNEWS-2026-10-25-preview.html").read_text()
import re
lc.NOTICES_EXPECTED=re.findall(r'font-weight:bold;color:#333333;text-align:left;padding-right:8px;">([^<]+)</td>', lc._section(page,"Community Notices"))
L=lc.check_email(page)
L2=lc.Locks()
lc.check_title_months(L2,{"newsletter":page})
try: lc.check_webmaster_sources(L2,page)
except Exception as e: print("ERR webmaster",e)
for r in L.results+L2.results: print(r)
