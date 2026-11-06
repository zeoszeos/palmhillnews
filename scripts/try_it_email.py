#!/usr/bin/env python3
"""'Calendar Mismatches Report - try it' email to Tony, built from a template (R112, Steven Nov 4 2026 6:11 PM).
Light-only head tags, white background, every p/a carries an explicit inline colour. Writes <out>/try-it-email.html and .txt."""
import argparse, html, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from email_dark_mode import HEAD_ADD
TEXT, LINK, BG, PX = "#000000", "#0f3a08", "#ffffff", 16   # R113: pure black on white, >= 15px, gradient-backed white wrapper table
GR = f"background:{BG};background-image:linear-gradient({BG},{BG});"
LINK_PLACEHOLDER = ("[SHARE LINK NOT CREATED YET - Steven must approve Vercel team access first; "
                    "replace this line with the no-login share link before sending]")
REFRESH_STATUS_NOTE = ("[STEVEN - REMOVE BEFORE SENDING: the RPM login and the email search are not working from the "
                       "server yet (RPM needs an email-address login; Gmail IMAP is blocked from the build box). Until they are, "
                       "the report shows each source's last successful check in its Refresh note, so do not promise "
                       "fully current data.]")
PARAS = [
    "Hey Tony,",
    "I came up with a way you can run this report anytime you want. Try it now:",
    None,  # link line
    "Here's what happens when you click it. It first pulls the latest Palm Hill calendar, then the RPM calendar. Then it searches email for any messages that may have committee or board meeting dates. It puts all of that together into the report for you. All of that happens before it looks for mismatches, so what you see is current.",
    REFRESH_STATUS_NOTE,
    "You don't need to log in to anything; just click the link.",
    "A few notes about the link:",
]
NOTES = ["You can run the report whenever you want.",
         "The link is just for you, so please don't forward it.",
         "If I'm ever worried about security, I can shut that link off and give you a new one, or turn the button off from my end. Either way, the old link stops working."]
TAIL = ["Every report also shows a Refresh date near the top, with a short note under it for each source: the Palm Hill calendar, the RPM calendar, and the committee and board emails that may mention a meeting date. Each note shows when that source was last checked, so you can see how current the data is.",
        "Steven"]

def build(link=None):
    P = f'<p style="margin:0 0 14px 0;color:{TEXT};font-size:{PX}px;line-height:1.5;font-weight:400;{GR}">'
    def linkp():
        if link: return P + f'<a href="{html.escape(link)}" style="color:{LINK};font-weight:700;text-decoration:underline">Run the Calendar Mismatches Report</a></p>'
        return P + html.escape(LINK_PLACEHOLDER) + "</p>"
    h = [f'<!DOCTYPE html><html><head><meta charset="utf-8">{HEAD_ADD}</head>',
         f'<body bgcolor="{BG}" style="margin:0;padding:0;{GR}color:{TEXT};font-family:Arial,Helvetica,sans-serif;font-size:{PX}px;line-height:1.5">',
         f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="width:100%;border-collapse:collapse;{GR}color:{TEXT};font-size:{PX}px"><tr bgcolor="{BG}" style="{GR}">'
         f'<td bgcolor="{BG}" style="padding:16px;{GR}color:{TEXT};font-family:Arial,Helvetica,sans-serif;font-size:{PX}px;line-height:1.5">',
         f'<div style="max-width:640px;color:{TEXT};{GR}">']
    t = []
    for p in PARAS:
        h.append(linkp() if p is None else P + html.escape(p) + "</p>"); t.append((link or LINK_PLACEHOLDER) if p is None else p)
    h.append(f'<ul style="margin:0 0 14px 0;padding-left:22px;color:{TEXT};font-size:{PX}px;{GR}">' + "".join(
        f'<li style="margin:0 0 8px 0;color:{TEXT};font-size:{PX}px;line-height:1.5;{GR}">{html.escape(n)}</li>' for n in NOTES) + "</ul>")
    t.append("\n".join("- " + n for n in NOTES))
    for p in TAIL: h.append(P + html.escape(p) + "</p>"); t.append(p)
    h.append("</div></td></tr></table></body></html>")
    return "".join(h), "\n\n".join(t) + "\n"

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--out", required=True); a.add_argument("--link"); o = a.parse_args()
    H, T = build(o.link); d = Path(o.out); d.mkdir(parents=True, exist_ok=True)
    (d / "try-it-email.html").write_text(H, encoding="utf-8"); (d / "try-it-email.txt").write_text(T, encoding="utf-8")
    print(d / "try-it-email.html")
