#!/usr/bin/env python3
"""STYLE-RULES.md R18 (Steven Oct 16 2026): every main-newsletter item summary is 3 lines max at 390px (phone) and 660px;
the full text lives on its Vercel page. Short texts use only the source's own wording. Idempotent; applied by the builder
(make_live_preview + publish) and safe to run on the live issue / FINAL. Edit SHORT when a new long item appears."""
import re, sys
B = "https://palmhillnews.vercel.app/pages/"
MORE = '<a href="{u}" style="color:#3A6B1A;white-space:nowrap;">More →</a>'
# R47 (Steven, Oct 18 12:23 AM): a Webmaster-sourced notice's More → is the SAME full-email page as its 'Webmaster' Source link
# (never the short 2026-10-18-notice-*.html page); style_rules.assert_webmaster_more checks every build.
# full-text prefix -> (short text in source wording, full-text page or None when the row already links to it)
SHORT = [
 ("Bus loads at 8:00 AM for the arts and crafts festival", "Bus loads at 8:00 AM for the arts and crafts festival. $35 per seat, payable at coffee.", B + "2026-10-24-mount-dora-trip.html"),
 ("Palm Hill now has a private Facebook group just for residents,", "Palm Hill now has a private Facebook group just for residents.", None),
 # Steven Oct 23 5:09 AM: new Webmaster notices (gotwicz); teaser already short, trim adds the inline More → (R23/R47)
 ("The brush dumpster is designated for brush and yard waste ONLY.", "The brush dumpster is designated for brush and yard waste ONLY. Broken pavers should be placed in the construction dumpster.", B + "2026-10-22-sanitation-field-notice.html"),
 # Steven Oct 23 6:38 PM: Library / stop sign / South Rec Webmaster notices
 ("The Library will be closed beginning MONDAY, OCTOBER 26TH", "The Library will be closed beginning MONDAY, OCTOBER 26TH through SUNDAY, NOVEMBER 1ST. Pick up books by Sunday the 25th.", B + "2026-10-22-library-closed-notice.html"),
 ("Please observe the posted speed limits and come to a complete stop", "Please observe the posted speed limits and come to a complete stop at all stop signs throughout our community.", B + "2026-10-21-stop-sign-rules-notice.html"),
 ("The South Recreation Club has positions available", "The South Recreation Club has positions available for the 2027 election. DEADLINE: December 2, 2026.", B + "2026-10-21-south-rec-club-seeking-officers-notice.html"),
 ("Couples Golf League will be starting November 5th.", "Couples Golf League will be starting November 5th. Couples League needs Hosting Volunteers.", B + "2026-10-20-couples-golf-league-notice.html"),
 ("All food and beverages must be kept at least 4 feet away", "All food and beverages must be kept at least 4 feet away from the edge of the pool. No glass containers.", B + "2026-10-16-swimming-pool-food-and-beverage-rules-notice.html"),
 ("An announcing chairperson is needed for November coffees", "Volunteers are needed for November coffees and for Pancakes on Saturday, Nov 14.", B + "2026-10-15-november-pancakes-and-coffee-volunteers-notice.html"),
 ("Please don&#x27;t walk on the courts;", "Please don&#x27;t walk on the courts; return discs and cue sticks; turn off lights and fans when you leave.", B + "2026-10-12-shuffleboard-information-notice.html"),
 ("New golfers and residents are welcome on Wednesday, Nov 18", "New golfers and residents are welcome on Wednesday, Nov 18 at 10:00 AM. Meet at the Pro Shop; it&#x27;s free.", B + "2026-10-14-taste-of-golf-notice.html"),
 # R42 (Steven, Oct 17 10:29 PM): Linda's whole "Info from Linda" email is ONE notice; More → opens the existing copy of her email
 ("Halloween Dance tickets are sold out.", "Halloween Dance tickets are sold out. Be respectful at clubhouses. Largo Evening Market: Sat. Oct. 24th, 5-9pm, Ulmer Park.", B + "2026-10-08-info-from-linda-notice.html"),
 ("The Palm Hill webmaster shared the sign-up link for", '<a href="https://www.propertyfraudalert.com/select" style="color:#3A6B1A;">Property Fraud Alert</a> is a free service that notifies you when a document is recorded under your name.', B + "2026-09-30-property-fraud-alert-notice.html"),
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
