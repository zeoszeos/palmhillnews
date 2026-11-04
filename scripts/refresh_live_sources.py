"""STYLE-RULES R110 (Steven, Nov 4 2026 5:02 PM): refresh every source right before the Calendar Mismatches Report runs.
  (a) Palm Hill calendar  -> scripts/pull_calendar.py (public feed, no credential)
  (b) RPM calendar        -> headless Chromium (Playwright) login to home.resourcepropertymgmt.com with env RPM_USERNAME / RPM_PASSWORD
  (c) palmhillblast Gmail -> IMAP imap.gmail.com, mailboxes selected READ-ONLY, env GMAIL_APP_PASSWORD
Credentials come ONLY from environment variables (box env / vault / Vercel sensitive env vars). They are never printed, logged,
written to a file or committed. Output: <work>/data/cal-*.json and <work>/data/live-sources.json (meeting data + real stamps
only: rpm, rpm_fetched, emails_searched, agenda entries with verbatim excerpts under <work>/data/emails/). Nothing is written to
the repo. A step that fails is reported with its exact reason and is NOT retried; its source keeps its last recorded stamp, which
R109 then shows as 'not refreshed at this run'.
Run:  TZ=America/New_York python3 scripts/refresh_live_sources.py --work DIR   (then meeting_conflict_report.py --work DIR)"""
import argparse, email, email.header, email.utils, imaplib, json, os, re, sys, time
from datetime import date, datetime, timedelta
from pathlib import Path
os.environ.setdefault("TZ", "America/New_York"); time.tzset()
REPO = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(REPO / "scripts"))
WINDOW_DAYS = 60
RPM_LOGIN_URL = "https://home.resourcepropertymgmt.com/public?modal=login"
RPM_CAL_URL = "https://home.resourcepropertymgmt.com/community/calendar"
GMAIL_USER = "palmhillblast@gmail.com"
ENV_NAMES = ("RPM_USERNAME", "RPM_PASSWORD", "GMAIL_APP_PASSWORD")
def stamp(): return datetime.now().strftime("%a %b %-d, %Y, %-I:%M %p") + " ET"
class StepFailed(Exception): pass
def need(name):
    v = os.environ.get(name)
    if not v: raise StepFailed(f"environment variable {name} is not set")
    return v
def step_calendar(data):
    import pull_calendar as pc
    return pc.pull(str(data), date.today().isoformat(), (date.today() + timedelta(days=WINDOW_DAYS)).isoformat())
def step_rpm(data):
    user, pw = need("RPM_USERNAME"), need("RPM_PASSWORD")
    from playwright.sync_api import sync_playwright
    raw = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH", "/usr/bin/google-chrome"), args=["--no-sandbox"])
        pg = b.new_page()
        pg.on("response", lambda r: raw.append(r) if r.request.resource_type in ("xhr", "fetch") and re.search(r"calendar|event", r.url, re.I) else None)
        pg.goto(RPM_LOGIN_URL, wait_until="networkidle", timeout=60000)
        pg.type("input[name=email]", user, delay=15); pg.type("input[name=password]", pw, delay=15)
        bt = pg.get_by_role("dialog").get_by_role("button", name="Log In", exact=True)
        if not bt.is_enabled():
            b.close(); raise StepFailed("RPM login form kept 'Log In' disabled after filling the fields" + ("" if "@" in user else " (RPM_USERNAME is not an email address; the portal asks for an Email)"))
        bt.click(); pg.wait_for_timeout(8000)
        body = pg.inner_text("body")
        if "modal=login" in pg.url or re.search(r"(?i)invalid|incorrect|verification code|captcha", body):
            b.close(); raise StepFailed("RPM login did not complete (still on the login form; page mentions: " + "; ".join(l.strip() for l in body.split("\n") if re.search(r"(?i)invalid|incorrect|code|captcha", l))[:200] + ")")
        pg.goto(RPM_CAL_URL, wait_until="networkidle", timeout=60000); pg.wait_for_timeout(3000)
        if "/community/calendar" not in pg.url: b.close(); raise StepFailed(f"RPM calendar page redirected to {pg.url.split('?')[0]}")
        got = [r.text() for r in raw if r.ok]; fetched = stamp(); b.close()
    # The logged-in calendar data format has not been seen by an automated run yet; parse it once a login succeeds (R110).
    raise StepFailed(f"RPM logged in and the calendar loaded ({len(got)} calendar responses at {fetched}), but the RPM calendar parser is not written yet")
_DATE = re.compile(r"(?i)\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? (\d{1,2}),? (20\d\d)\b(?:[^.\n]{0,40}?\b(\d{1,2}(?::\d{2})?\s?[AP]\.?M\.?))?")
def step_gmail(data, comm, since):
    pw = need("GMAIL_APP_PASSWORD")
    try: M = imaplib.IMAP4_SSL("imap.gmail.com", timeout=30)
    except Exception as e: raise StepFailed(f"could not open a TLS connection to imap.gmail.com:993 from this machine ({type(e).__name__}); the password was not tried")
    try: M.login(GMAIL_USER, pw)
    except imaplib.IMAP4.error as e: raise StepFailed("Gmail rejected the IMAP login (" + re.sub(r"\S+@\S+", "", str(e))[:120] + ")")
    out, edir = [], data / "emails"; edir.mkdir(exist_ok=True)
    for box in ('"[Gmail]/All Mail"', "INBOX"):
        if M.select(box, readonly=True)[0] == "OK": break
    _, ids = M.search(None, "SINCE", since.strftime("%d-%b-%Y"))
    until = (date.today() + timedelta(days=WINDOW_DAYS)).isoformat()
    for i in ids[0].split():
        _, d = M.fetch(i, "(BODY.PEEK[])"); msg = email.message_from_bytes(d[0][1])
        subj = str(email.header.make_header(email.header.decode_header(msg.get("Subject", ""))))
        c = next((k for k, pat in comm.items() if re.search(pat, subj) or re.search(pat, subj.replace(" Committee", ""))), None)
        if not c: continue
        part = next((p for p in msg.walk() if p.get_content_type() == "text/plain"), None)
        text = re.sub(r"\s+", " ", (part.get_payload(decode=True) or b"").decode(part.get_content_charset() or "utf-8", "replace")) if part else ""
        for m in _DATE.finditer(text):
            dt = datetime.strptime(f"{m.group(1)[:3]} {m.group(2)} {m.group(3)}", "%b %d %Y").date().isoformat()
            if not (date.today().isoformat() <= dt <= until): continue
            tm = None
            if m.group(4):
                t = m.group(4).upper().replace(".", "").replace(" ", ""); t = t if ":" in t else t[:-2] + ":00" + t[-2:]
                tm = datetime.strptime(t, "%I:%M%p").strftime("%H:%M")
            f = edir / f"{i.decode()}.txt"; f.write_text(f"{subj}\n{text}", encoding="utf-8")
            sent = email.utils.parsedate_to_datetime(msg["Date"]).astimezone()
            out.append(dict(committee=c, date=dt, time=tm, page="work:data/emails/" + f.name, quote=m.group(0),
                            kind="email (palmhillblast IMAP)", email_date=sent.strftime("%a %b %-d, %Y, %-I:%M %p") + f" ET ({subj[:80]}, palmhillblast)"))
    M.logout(); return out
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--work", required=True); a = ap.parse_args(argv)
    data = Path(a.work) / "data"; data.mkdir(parents=True, exist_ok=True)
    src = json.load(open(REPO / "builder/data/meeting-conflict-sources.json", encoding="utf-8"))
    live, fails = {}, {}
    try: print("Palm Hill calendar:", os.path.basename(step_calendar(data)))
    except BaseException as e: fails["Palm Hill calendar"] = str(e)
    try: live.update(step_rpm(data))
    except StepFailed as e: fails["RPM"] = str(e)
    try:
        ag = step_gmail(data, src["committees"], date.today() - timedelta(days=14)); live["agenda"] = ag; live["emails_searched"] = stamp() + ", palmhillblast IMAP"
        print(f"Gmail: {len(ag)} meeting-date mention(s)")
    except StepFailed as e: fails["Gmail"] = str(e)
    (data / "live-sources.json").write_text(json.dumps(live, indent=1), encoding="utf-8")
    for k, v in fails.items(): print(f"FAILED {k}: {v}")
    return 1 if fails else 0
if __name__ == "__main__": sys.exit(main())
