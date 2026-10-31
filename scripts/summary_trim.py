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
 # Steven Oct 30 2026 8:29 PM: five Oct 29 emails (gotwicz) as Nov 1 notices; cut, never reworded; More → = the copied email (R47)
 ("We are search for an Amazon package that was delivered", "We are search for an Amazon package that was delivered to the wrong address. If you happen to see it please get in touch.", B + "2026-10-29-missing-amazon-package-notice.html"),
 ("Resident requested - South Potable Water Shut off", "Resident requested - South Potable Water Shut off Wednesday, November 4, 2026 from 10:00am for approximately 2 hours.", B + "2026-10-29-south-potable-water-shut-off-notice.html"),
 ("Join us for Social Shuffle in the North Shuffleboard Courts", "Join us for Social Shuffle in the North Shuffleboard Courts on Monday\u2019s at 11:00am, beginning November 2nd, 2026.", B + "2026-10-29-social-shuffle-begins-notice.html"),
 ("When: Monday, November 2, 2026. Time: 10:30 AM.", "When: Monday, November 2, 2026. Time: 10:30 AM. Where: North Clubhouse.", B + "2026-10-29-mens-golf-association-meeting-notice.html"),
 ("If anyone wants Spaghetti tickets for Sat November 14th", "If anyone wants Spaghetti tickets for Sat November 14th please contact Mary Lou Shaw at 608-312 -6958.", B + "2026-10-29-spaghetti-tickets-still-available-notice.html"),
 ("Bus loads at 8:00 AM for the arts and crafts festival", "Bus loads at 8:00 AM for the arts and crafts festival. $35 per seat, payable at coffee.", B + "2026-10-24-mount-dora-trip.html"),
 ("Palm Hill now has a private Facebook group just for residents,", "Palm Hill now has a private Facebook group just for residents.", None),
 # Steven Oct 23 5:09 AM: new Webmaster notices (gotwicz); teaser already short, trim adds the inline More → (R23/R47)
 ("The brush dumpster is designated for brush and yard waste ONLY.", "The brush dumpster is designated for brush and yard waste ONLY. Broken pavers should be placed in the construction dumpster.", B + "2026-10-22-sanitation-field-notice.html"),
 # Steven Oct 24 11:38 AM: Bill Bender's Holiday Greeting flyer (resident notice)
 ("A simple way for Palm Hill residents to send holiday greetings", "A simple way for Palm Hill residents to send holiday greetings to friends and neighbors within the community.", B + "2026-10-23-holiday-greeting-distribution-plan.html"),
 # Steven Oct 24 1:27 PM: North Clubhouse ice machine notice (Steven's confirmed sentence; More -> its own page holding Elaine's sentence + his details)
 ("The ice machine in the North Clubhouse was moved out of", "The ice machine in the North Clubhouse was moved out of the North meeting room and into the pool table room.", B + "2026-10-24-north-clubhouse-ice-machine-moved-notice.html"),
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
def unmatched(s, base=B):
    """R18b (Steven, Oct 24 2026 9:05 PM, coding batch 1): SHORT entries whose saved full-text prefix is not in s.
    Returns [(prefix, url, current)]; current=True when the entry's More page is linked in s (the item is in this issue
    but its text no longer starts with the saved prefix, so it would go out untrimmed). The builder reports all and fails on current."""
    out = []
    for pre, short, url in SHORT:
        if s.find(OPEN + pre) >= 0: continue
        cur = bool(url) and (url.replace(B, base) in s) and short not in s
        out.append((pre, url, cur))
    return out
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
