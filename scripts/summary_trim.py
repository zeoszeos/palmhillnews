#!/usr/bin/env python3
"""STYLE-RULES.md R18 (Steven Oct 16 2026): every main-newsletter item summary is 3 lines max at 390px (phone) and 660px;
the full text lives on its Vercel page. Short texts use only the source's own wording. Idempotent; applied by the builder
(make_live_preview + publish) and safe to run on the live issue / FINAL. Edit SHORT when a new long item appears."""
import re, sys
B = "https://palmhillnews.vercel.app/pages/"
MORE = '<a href="{u}" style="color:#3A6B1A;white-space:nowrap;">More →</a>'
# full-text prefix -> (short text in source wording, full-text page or None when the row already links to it)
SHORT = [
 ("Bus loads at 8:00 AM for the arts and crafts festival", "Bus loads at 8:00 AM for the arts and crafts festival. $35 per seat, payable at coffee.", B + "2026-10-24-mount-dora-trip.html"),
 ("Palm Hill now has a private Facebook group just for residents,", "Palm Hill now has a private Facebook group just for residents.", None),
 ("All food and beverages must be kept at least 4 feet away", "All food and beverages must be kept at least 4 feet away from the edge of the pool. No glass containers.", B + "2026-10-18-notice-swimming-pool-food-and-beverage-rules.html"),
 ("An announcing chairperson is needed for November coffees", "Volunteers are needed for November coffees and for Pancakes on Saturday, Nov 14.", B + "2026-10-18-notice-november-coffee-and-pancake-volunteers.html"),
 ("Please don&#x27;t walk on the courts;", "Please don&#x27;t walk on the courts; return discs and cue sticks; turn off lights and fans when you leave.", B + "2026-10-18-notice-shuffleboard-season-reminders.html"),
 ("New golfers and residents are welcome on Wednesday, Nov 18", "New golfers and residents are welcome on Wednesday, Nov 18 at 10:00 AM. Meet at the Pro Shop; it&#x27;s free.", B + "2026-10-18-notice-taste-of-golf-november-18.html"),
 # R42 (Steven, Oct 17 10:29 PM): Linda's whole "Info from Linda" email is ONE notice; More → opens the existing copy of her email
 ("Halloween Dance tickets are sold out.", "Halloween Dance tickets are sold out. Be respectful at clubhouses. Largo Evening Market: Sat. Oct. 24th, 5-9pm, Ulmer Park.", B + "2026-10-08-info-from-linda-notice.html"),
 ("The Palm Hill webmaster shared the sign-up link for", '<a href="https://www.propertyfraudalert.com/select" style="color:#3A6B1A;">Property Fraud Alert</a> is a free service that notifies you when a document is recorded under your name.', B + "2026-10-18-notice-property-fraud-alert.html"),
 ("58 work orders in Aug (72% done);", "58 work orders in Aug (72% done); new north clubhouse A/C; Fern St. still closed for storm-sewer repair.", None),
 ("The invoice for the transformer was paid;", "The invoice for the transformer was paid; installation will take approximately 6 weeks. Fern sewer liner expected the week of 10/26.", None),
 ("Doors open at 4:30 PM; dinner is served at 5:00 PM.", "Doors open at 4:30 PM; dinner is served at 5:00 PM. $12 donation; tickets at both coffees until Nov 9, none at the door.", B + "2026-11-14-mesco-spaghetti-dinner-fundraiser.html"),
 ("Henry Klain on the land purchase initiative:", "Henry Klain: on Sep 30 the Board formed a Land Advisory Team to study buying the land Palm Hill leases.", None),
 ("Did you know Palm Hill has a private, residents-only Facebook group?", "Did you know Palm Hill has a private, residents-only Facebook group? Park news, events and photos.", None),
]
OPEN = 'margin-top:3px;">'
def trim(s, base=B):
    for pre, short, url in SHORT:
        i = s.find(OPEN + pre)
        if i < 0: continue
        a = i + len(OPEN); b = s.index("</div>", a); inner = s[a:b]
        tail = inner[inner.index("<br><a"):] if "<br><a" in inner else ""
        new = short + ((" " + MORE.format(u=url.replace(B, base))) if url else "") + tail
        s = s[:a] + new + s[b:]
        if url:  # inline More → replaces the row's own More → div (one More → per item; STYLE-RULES R25)
            dup = f'<div style="font-size:14px;margin-top:4px;"><a href="{url.replace(B, base)}" style="color:#3A6B1A;">More →</a></div>'
            e = a + len(new) + len("</div>")
            if s.startswith(dup, e): s = s[:e] + s[e + len(dup):]
    return s
if __name__ == "__main__":
    for f in sys.argv[1:]:
        t = open(f, encoding="utf-8").read(); n = trim(t); open(f, "w", encoding="utf-8").write(n); print(("trimmed " if n != t else "unchanged ") + f)
