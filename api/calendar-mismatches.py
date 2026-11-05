"""STYLE-RULES R106 (Steven, Nov 4 2026 4:30 PM): the "anytime button" for the Calendar Mismatches Report.
GET /api/calendar-mismatches re-pulls the Palm Hill calendar feed (public Apps Script feed, no credential) into /tmp and
renders the SAME Tony report via scripts/meeting_conflict_report.py (R105-R105f format, 60-day window, America/New_York).
What it cannot do yet: read RPM live (needs an RPM login + a headless browser) or search Gmail for notice emails (needs a
Gmail OAuth credential). Those columns use the last recorded read in builder/data/meeting-conflict-sources.json, and the
page says so in a banner above the report. Never sends mail, never writes the calendar.
Kill switch: REPORT_BUTTON_ENABLED must be "true" (Vercel env var); anything else returns 503. No secrets live in this file."""
import json, os, sys, tempfile, time, traceback
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler
from pathlib import Path
os.environ["TZ"] = "America/New_York"; time.tzset()   # R106: report run time is always Eastern
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts")); sys.path.insert(0, str(REPO / "builder/core"))
ENABLE_FLAG = "REPORT_BUTTON_ENABLED"
LIMITS_BANNER = ("Run on demand: the Palm Hill calendar was re-pulled live just now. The button cannot read RPM live yet, so the RPM "
                 "column uses the last recorded RPM read (date shown below); email notices are also from the last recorded check.")
def enabled(): return os.environ.get(ENABLE_FLAG, "").strip().lower() == "true"
os.environ.setdefault("PHNEWS_REPO", str(REPO))
def make_report(issue=None):
    import meeting_conflict_report as m, pull_calendar as pc
    issue = issue or os.environ.get("PHNEWS_ISSUE") or "2026-11-08"; os.environ["PHNEWS_ISSUE"] = issue
    work = Path(tempfile.mkdtemp(prefix="phcal-")); (work / "data").mkdir()
    pc.pull(str(work / "data"), date.today().isoformat(), (date.today() + timedelta(days=m.WINDOW_DAYS)).isoformat())
    R = m.build(issue, work); R["run"] = __import__("datetime").datetime.now().strftime("%a %b %-d, %Y, %-I:%M %p")
    h = m.render_tony_html(R)
    banner = f"<p data-r106='limits' style='margin:0 0 12px;padding:8px 10px;background:#eef3fb;color:#1f1f1f;border:1px solid #b6c8e6;font-size:13px;line-height:1.4;'>{LIMITS_BANNER}</p>"
    i = h.index(">", h.index("<body")) + 1   # banner goes first inside <body>; the report itself is untouched
    return h[:i] + banner + h[i:], R
class handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body.encode("utf-8"); self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store"); self.send_header("X-Robots-Tag", "noindex"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if not enabled(): return self._send(503, "<p>The Calendar Mismatches Report button is turned off.</p>")
        try: self._send(200, make_report()[0])
        except BaseException: traceback.print_exc(); self._send(502, "<p>The report could not be built right now (calendar feed or data problem). Nothing was sent.</p>")
