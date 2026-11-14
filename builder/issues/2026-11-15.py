"""PHNEWS Sunday, November 15, 2026 (Vol. 1, No. 18) -- issue content file (STYLE-RULES R71). Data only; all logic is in builder/core/.
Nov 15 DRAFT built Thu Nov 12 2026 from the Nov 8 file (Steven: "lets create this weeks newsletter"). Nothing approved yet. New week = copy the idea of this file, never a builder."""
ISSUE = "2026-11-15"
VOL_NO = 18
SHORT = "nov15"
DEFAULT_REPO = "/workspace/palmhillnews"
DEFAULT_WORK = "/workspace/phnews-consolidation/nov15"
# Community Stories section omitted (R45 / R104). Steven Nov 12 2026 (voice) approved Carolyn Story's
# "Serving on the Palm Hill Board of Directors" (Palm Hill Link, November 2026, p 36, verbatim) and asked
# that it be moved from Community Stories into Community Notices. The full page and Listen page stay published.
# Pages written by builder/nov15/stage_nov15_content.py (no photo printed).
STORY = None
STORY_OMIT_APPROVED = "Steven Leonowicz, Nov 12, 2026 (voice): move Carolyn Story's Board piece from Community Stories into Community Notices"
STORY_OMIT_DRYRUN_NOTE = None         # real omit is STORY_OMIT_APPROVED, not a dry-run
# Carry policy (set up Oct 24 2026 8:3x PM; Steven confirms Friday): keep notices still valid on/after Nov 1, drop Oct 25 one-offs.
NOTICES_DROPPED = ["Library Closed starting the week of October 26th", "Info from Linda", "North Clubhouse Ice Machine Moved",
                   "Help with maintaining Sanitation Field", "Please observe important stop sign rules",
                   # Nov 8 stale sweep (Nov 1 2026 11:55 AM task, Steven: "pull stale or out of date ... events"): dated before Sun Nov 8
                   "December Link Deadline",                     # deadline Thu Nov 5
                   "Senior Empowerment Lunch & Learn",           # Wed Nov 4
                   "Worship Service",                            # Sun Nov 1
                   "South Potable Water Shut off",               # Wed Nov 4 (R53). The Nov 11 reschedule is a separate notice.
                   "Palm Hill Men's Golf Association Meeting",  # Mon Nov 2
                   "Couples Golf League",                        # "Starts: November 5th" (flagged for Steven: league itself may continue)
                   # Nov 15 stale sweep (R53): dated before Sun Nov 15, or as instructed
                   "Missing Amazon Package",                     # ran Nov 1 and Nov 8 (Steven, Nov 12 task: drop it)
                   "Chair Yoga class canceled",                  # Mon Nov 9 (classes resumed Nov 16)
                   "South Potable Water Shut off (rescheduled)", # Wed Nov 11 (RPM: water restored Nov 11)
                   "Spaghetti Tickets - Still Available",        # dinner Sat Nov 14
                   "November Coffee and Pancake Volunteers",     # pancakes Sat Nov 14 (flagged for Steven)
                   "North Irrigation Down",                      # Steven Nov 12 2026 (voice): pull the undated RPM riser notice
                   "Taste of Golf"]                              # Steven Nov 12 2026 (voice): drop the Oct 14 sign-up promo; keep Taste of Golf Instructions + the event row
R60C_ICE_NOTICE = False               # the ice machine notice is dropped for Nov 1
DRYRUN_OK = True                      # PHNEWS_DRYRUN=1 lists content guards as TODOs (workspace only)
LOCKED = {
    "NOTICES_EXPECTED": [   # Nov 15 DRAFT (not yet approved by Steven): four new Nov 9-12 emails, then the Nov 8 list minus stale notices
        'Serving on the Palm Hill Board of Directors',
        'Singing Ensemble for Christmas Cantata',
        'Palm Hill Annual Golf Cart Parade',
        'Christmas Golf Cart Route',
        'Amazon Scam Email',
        'Exercise Class',
        'Taste of Golf Instructions',
        'Ladies Christmas Luncheon',
        'Cornhole Tournament',
        'How to access the Palm Hill Community Channel',
        'Social Shuffle',
        'A convenient way to send holiday cards for Palm Hill residents',
        '2027 South Rec Club Seeking Officers',
        'Swimming Pool Food and Beverage Rules',
        'Shuffleboard Season Reminders',
    ],
    # Nov 15: the Oct 12-14 chair reports are past the 30-day window (cutoff Oct 16) and no newer report came in
    # (R104b: heading stays with "No reports this week." unless a fresh report arrives before publish)
    "CHAIR_EXPECTED": {},
}

# =====================================================================================================================
# CARRIED FROM OCT 25 (Steven to review) -- coding batch 5 moved every per-issue item out of builder/core/ into the content
# files. Everything from here to the end of this file is the Oct 25 content, copied unchanged so the Nov 1 dry run stays
# byte-identical. Nothing below is approved Nov 1 content: replace or drop each section when Nov 1 content is decided.
# =====================================================================================================================
# ---------- Events (1): Upcoming/This Week event text, links and More → pages (R21/R23/R56) ----------
# Event detail rewritten from the calendar "info" (no personal phone numbers or home addresses).
EVENT_DETAIL = {
    "Mount Dora Trip": "Bus loads at 8:00 AM for the arts and crafts festival, with an optional boat ride on the lake. $35 per seat, payable at coffee; the calendar shows about 12 seats left.",
    "Halloween Golf Cart Parade": "Line up at the North Clubhouse at 6:30 PM for the 7:00 PM parade to the South Clubhouse; it takes about 1½ hours. Charge golf-cart batteries fully.",
    "Halloween Dance Party": "Doors open at 6:15 PM with no assigned seating. The tickets are sold out as of now. Bring a treat to share for table-to-table trick-or-treating.",  # Steven Oct 17 10:29 PM: sold-out wording restored (Linda, Oct 8)
    "Senior Empowerment Luncheon": "The luncheon runs 10:00 AM to 1:00 PM; the room is booked from 9:15 AM for set-up. Pre-registration is required.",
    "North Clubhouse Craft Fair": "Crafters can rent a table for $20, 9:00 AM to 1:00 PM. See the club calendar for who to contact to book.",
    "Veterans Day Program": "Program at the South Clubhouse; check the club calendar for later details.",
    "Pot Luck Supper": "Doors open at 5:00 PM; dinner is at 5:30 PM. Bring your own table setup and drink.",
    "MESCO Spaghetti Dinner Fundraiser": "Doors open at 4:30 PM; dinner is served at 5:00 PM. The $12 donation covers bread and butter, salad, spaghetti and meatballs, dessert and coffee; BYOB for other drinks. Tickets are sold at both coffees until Monday morning, Nov 9; none at the door.",
    "Fall Festival": "Music and food trucks on the South Lawn and Patio.",
    "Cantata rehearsal": "To accommodate those attending the Fall Festival, this weekend's rehearsal will take place at 7:00 p.m. in the North Clubhouse.",
    "Christmas Golf Cart Parade": "Line up 5:30 PM in front of the North Clubhouse. Ending at South Clubhouse. Batteries should be fully charged. Parade takes 1.5 hours to complete.",
    # Steven Oct 26 2026 11:49 AM: use the calendar's organizer (Mickey Bontrager) for now; detail = calendar listing, light edit (2:00 -> 2:00 PM)
    "Thanksgiving Dinner": "Dinner served at 2:00 PM.",
    "Bookclub:Foster by Claire Keegan": "Book club discussion of Foster by Claire Keegan.",
    "Bocce Party": "Sign up at either clubhouse or by calling Pat Foor or Joe Cothran. Join us for the fellowship and fun!",
    "Taste of Golf": "Free. New golfers and residents welcome; golf teachers on each hole, treats and a hot dog on the Pro Shop patio. Sign up at the Pro Shop, North or South Clubhouse.",
    "Bookclub Lunch at Irish Pub": "Members and those joining book club only.",
    "December Cruise Information Meeting": "Information meeting for everyone going on the December cruise. Questions: Tony Ciaramitaro.",
    "Bridge Club": "Moved due to Haunted House",
}
EVENT_EXTRA_SRC = {"Halloween Golf Cart Parade": BASE + "2026-09-18-halloween-golf-cart-parade-notice.html",
                   "Halloween Dance Party": BASE + "2026-10-08-info-from-linda-notice.html",
                   "Taste of Golf": BASE + "2026-11-10-taste-of-golf-instructions-notice.html",
                   "Cantata rehearsal": BASE + "2026-11-13-singing-ensemble-christmas-cantata-notice.html",
                   "Christmas Golf Cart Parade": BASE + "2026-11-13-palm-hill-annual-golf-cart-parade-notice.html",
                   # Sat Oct 31 6 PM sweep (staged pending Steven): R56 -- calendar row + Webmaster reminder notice (calendar facts only, More -> notice)
                   "Senior Empowerment Luncheon": BASE + "2026-10-31-senior-empowerment-lunch-and-learn-notice.html"}
EVENT_LINK = {"Halloween Dance Party": ("More →", BASE + "2026-10-31-halloween-dance.html"),
              "Mount Dora Trip": ("More →", BASE + "2026-10-24-mount-dora-trip.html"),
              "MESCO Spaghetti Dinner Fundraiser": ("More →", BASE + "2026-11-14-mesco-spaghetti-dinner-fundraiser.html"),
              "Thanksgiving Dinner": ("More →", BASE + "2026-11-26-thanksgiving-dinner.html"),
              "Thanksgiving/Friendsgiving Dance": ("More →", BASE + "2026-11-21-thanksgiving-friendsgiving-dance.html"),  # R114 (Steven Nov 4 2026 8:50 PM)
              "Bocce Party": ("More →", BASE + "2026-10-28-bocce-party.html"),
              "Taste of Golf": ("More →", BASE + "2026-11-10-taste-of-golf-instructions-notice.html"),
              "Senior Empowerment Luncheon": ("More →", BASE + "2026-10-31-senior-empowerment-lunch-and-learn-notice.html"),
              "Cantata rehearsal": ("More →", BASE + "2026-11-13-singing-ensemble-christmas-cantata-notice.html"),
              "Christmas Golf Cart Parade": ("More →", BASE + "2026-11-13-palm-hill-annual-golf-cart-parade-notice.html")}   # Sat Oct 31 6 PM sweep (staged, R56)      # existing Webmaster copy page (gotwicz 1a13d9d5ef6e178f)
# R21: full calendar listing text for the More → page. Personal phone numbers are not printed, EXCEPT on event pages Steven
# has explicitly OK'd (PHONE_OK_PAGES; Bocce Party approved Oct 16 11:37 PM). Issue summaries never carry them.
PHONE_OK_PAGES = {"Bocce Party", "Thanksgiving/Friendsgiving Dance"}  # Dance: Steven Nov 4 2026 8:50 PM (R114)
# R114: More → event pages whose OK'd phone numbers must be tap-to-call (tel:) links on the page.
EVENT_PAGE_TEL = [("Thanksgiving/Friendsgiving Dance", "269-317-6890", "2026-11-21-thanksgiving-friendsgiving-dance.html")]
EVENT_PAGE = {"Bocce Party": ("2026-10-28-bocce-party.html",
    ["Sign up at either clubhouse or by calling Pat Foor (727-631-3372) or Joe Cothran (727-512-1185). Join us for the fellowship and fun!",  # PHONE_OK_PAGES
     "Rescheduled from 4:00 PM to 6:00 PM (6:00 to 7:00 PM)."]),
    # R21 calendar re-pull Sat Oct 17 1:47 PM: start moved 4:00 PM -> 5:00 PM; the More → page date line now comes from the calendar
    "MESCO Spaghetti Dinner Fundraiser": ("2026-11-14-mesco-spaghetti-dinner-fundraiser.html",
    ["Doors open at 4:30 PM; dinner is served at 5:00 PM. The $12 donation covers bread and butter, salad, spaghetti and meatballs, dessert and coffee; BYOB for other drinks. Tickets are sold at both coffees until Monday morning, Nov 9; none at the door."]),
    # R21/R82 (Steven Oct 26 2026 11:49 AM): calendar listing text (booking 112626-1200-SMH), names exactly as the calendar gives them
    "Thanksgiving Dinner": ("2026-11-26-thanksgiving-dinner.html",
    ["Dinner served at 2:00 PM. Mickey Bontrager, Elroy Bontrager, Kate and Jeff Wesolowski."]),
    # R21/R114 (Steven Nov 4 2026 8:50 PM): calendar listing text exactly (booking 112126-1800-NCH); phone OK'd, tap-to-call
    "Thanksgiving/Friendsgiving Dance": ("2026-11-21-thanksgiving-friendsgiving-dance.html",
    ["Music by Zone II (60s, 70s & 80s). Tickets $8 per person at coffee hours or call Mollie Cardno 269-317-6890; assigned seating when purchased."])}

# ---------- Events (2): INFO_COVERED, TITLE + Oct 20/22 calendar re-pull additions (folded into data) ----------
INFO_COVERED = {"Halloween Golf Cart Parade", "Senior Empowerment Luncheon", "North Clubhouse Craft Fair", "Pot Luck Supper", "Fall Festival",
                "Veterans Day Program", "Bookclub:Foster by Claire Keegan",
                "Bookclub Lunch at Irish Pub", "December Cruise Information Meeting", "Bridge Club"}
TITLE = {"Bookclub:Foster by Claire Keegan": "Book Club: Foster by Claire Keegan", "Bookclub Lunch at Irish Pub": "Book Club Lunch at Irish Pub"}
# Oct 25: events new to the issue window (calendar re-pull Oct 20 2:40 PM). Detail = the calendar listing text (light edits only).
# Calendar re-pull Oct 22 7:55 PM: new one-off Bridge Club (Oct 26, Pool Room South); detail = its calendar listing text verbatim
# (batch 5: these additions were EVENT_DETAIL.update / EVENT_LINK[...] = ... statements; folded into the data above, same order)

# ---------- Meetings: committee/board extras, notes and agenda/report overrides (R62/R62b/R62c) ----------
# Steven, Oct 16 (MEETING-SOURCES-COMPARE.md): Finance from agenda email (no Zoom link yet); Palm Hill dates for Nov conflicts, flagged TBC
# R86/R87 (Steven Oct 30 2026 11:21 AM "follow the Palm Hill calendar"): no MTG_EXTRA rows -- the calendar now shows the Nov 18
# Board of Directors meeting RESCHEDULED (moved to Fri Nov 20, 1:00 PM, which the calendar lists CONFIRMED). Was: Nov 18 TBC row.
MTG_EXTRA = []
# R87b (same message): the calendar's "Board Meeting" (Meetings category, e.g. Thu Nov 5 1:00 PM) is a board meeting too.
MEETINGS_NAME_RE_EXTRA = r"\bboard meeting\b"
# Steven Oct 30 2026 11:30 AM: B&G Nov 10 calendar date is firm -- "(date to be confirmed)" note removed.
MTG_NOTE = {}
# STYLE-RULES R86 (Steven Oct 27 2026 2:24 PM; Tony Oct 26 "Calendar dates only works for me"): from Nov 1 the Palm Hill calendar
# rules meeting dates/times. R62/R62b/R62c overrides released for Nov 1: no override keys (Finance = calendar Mon Nov 16, 10:00 AM;
# P&E = calendar Tue Nov 10, 12:30 PM). Agenda/report differences are listed by scripts/meeting_conflict_report.py.
MTG_OVERRIDE = {}
MTG_OVERRIDE_SOURCE = {}
# STYLE-RULES R87 (Steven Oct 27 2026 2:24 PM, Tony's option (c)): every meeting in the Meetings window, repeats and all.
MEETINGS_ALL_IN_WINDOW = True

# ---------- Community Notices (1): Tony's Facebook group notice (top row) ----------
# (title, text, source label, source href or None, listen href or None)
TONY_FB_PLACEHOLDER = False  # set False Saturday once Tony's wording (due Fri Oct 16, palmhillblast) is pasted below
TONY_FB = ("Join the Palm Hill Residents Group on Facebook", None)  # Tony's wording arrived Fri Oct 16 (palmhillblast); verbatim
FBURL = "https://www.facebook.com/groups/720846344400510"
# R60 (Steven Oct 21 8:34 PM): live published Oct 18 URLs (publish_oct18 MAP), never pages/previews/ or #listen-pending
FBQR = "https://palmhillnews.vercel.app/pages/assets/phnews/2026-10-18/fb-group-qr.png"
FBPAGE_NOTICE = "https://palmhillnews.vercel.app/pages/2026-10-18-facebook-group-notice.html"
FBPAGE_DYK = "https://palmhillnews.vercel.app/pages/2026-10-18-did-you-know-facebook-group.html"
FB_LISTEN = "https://palmhillnews.vercel.app/pages/2026-10-18-notice-join-the-palm-hill-residents-group-on-facebook.html?listen=1"  # as in the approved Oct 18 issue
TONY_FB_TXT = ('Palm Hill now has a private Facebook group just for residents, with park news, event reminders and photos posted by the admins (comments are turned off). '
    'Every request is checked against the member directory, so use the address and email the Office has for you, answer all 3 questions, or Facebook will turn the request down. '
    f'Search Facebook for &quot;Palm Hill Country Club - Residents Only Group&quot; or join here: <a href="{FBURL}" style="color:{G};">{FBURL}</a>'
    f'<br><a href="{FBPAGE_NOTICE}" style="color:{G};font-size:14px;">Full notice with QR code to scan →</a>')
TONY_FB_SOURCE = "Tony Ciaramitaro, Communications Chair"

# ---------- Community Notices (2): Webmaster source-email copy pages (L27/L29), verbatim ----------
WM_COPY_PANCAKES = "2026-10-15-november-pancakes-and-coffee-volunteers-notice.html"   # gotwicz 1a13ffdbd4141bdd
WM_COPY_SHUFFLE = "2026-10-12-shuffleboard-information-notice.html"                   # gotwicz 1a13200e1dcdde48
WM_COPY_GOLF = "2026-10-14-taste-of-golf-notice.html"                                  # gotwicz 1a13d9d5ef6e178f
WM_COPY_SANIT = "2026-10-22-sanitation-field-notice.html"                            # gotwicz 1a164e859613b210 (Steven Oct 23 5:09 AM, A)
WM_COPY_COUPLES = "2026-10-20-couples-golf-league-notice.html"                        # gotwicz 1a15c9dca2aac0fc (Steven Oct 23 5:09 AM, C)
WM_COPY_LIBRARY = "2026-10-22-library-closed-notice.html"                             # gotwicz 1a164ed6011d050d (Steven Oct 23 6:38 PM)
WM_COPY_STOP = "2026-10-21-stop-sign-rules-notice.html"                                # gotwicz 1a15eb6fba34f8ab (Steven Oct 23 6:38 PM; RPM duplicate ignored)
WM_COPY_SOUTHREC = "2026-10-21-south-rec-club-seeking-officers-notice.html"            # gotwicz 1a15eb2704b3f9a0 (Steven Oct 23 6:38 PM; image-only email)
# Steven Oct 30 2026 8:29 PM: five Oct 29 Palm Hill emails (gotwicz) added as Community Notices (R93 date lines, source wording)
WM_COPY_AMAZON = "2026-10-29-missing-amazon-package-notice.html"                       # gotwicz 1a188f3c35f60e0b
WM_COPY_WATER_S = "2026-10-29-south-potable-water-shut-off-notice.html"                # gotwicz 1a188c43d05d7df5 (RPM #XN9409838)
WM_COPY_SOCIAL_SHUFFLE = "2026-10-29-social-shuffle-begins-notice.html"                # gotwicz 1a188b1bcff509fa
WM_COPY_MENS_GOLF = "2026-10-29-mens-golf-association-meeting-notice.html"             # gotwicz 1a1882f2503385a3
WM_COPY_SPAGHETTI = "2026-10-29-spaghetti-tickets-still-available-notice.html"         # gotwicz 1a1880b577f20ce7
# Sat Oct 31 2026 morning sweep (STAGED in a draft PR, pending Steven's OK): two Fri Oct 30 evening Webmaster emails (leonowicz)
WM_COPY_LINK_DEC = "2026-10-30-december-link-deadline-notice.html"                     # leonowicz 1a18f12ee530aafa (Lisa Bria)
WM_COPY_CHANNEL = "2026-10-30-palm-hill-community-channel-xumo-notice.html"            # leonowicz 1a18f3dd208ede75 (Gail Stott)
# Sat Oct 31 2026 6 PM deadline sweep (STAGED in a draft PR, pending Steven's OK): three Sat Oct 31 Webmaster emails (leonowicz)
WM_COPY_CORNHOLE = "2026-10-31-cornhole-tournament-notice.html"                        # leonowicz 1a1928943f130516 (image-only flyer)
WM_COPY_SENIOR_LL = "2026-10-31-senior-empowerment-lunch-and-learn-notice.html"        # leonowicz 1a1923d6204ee46a (Bonnie Swanson)
WM_COPY_WORSHIP = "2026-10-31-worship-service-notice.html"                             # leonowicz 1a191d8809626222 (Claudia Hartz)
# Nov 15 sweep (Thu Nov 12 2026). Verbatim bodies; the per-recipient unsubscribe line is left out. gotwicz Gmail.
WM_COPY_IRRIGATION = "2026-11-12-north-irrigation-down-notice.html"           # gotwicz 1a1d0bfbee7da9ec Thu Nov 12 12:13 PM ET (RPM #XN9559224)
WM_COPY_EXERCISE = "2026-11-10-exercise-class-beginning-notice.html"          # gotwicz 1a1c8d83f9657711 Tue Nov 10 11:22 PM ET
WM_COPY_TOG_INSTR = "2026-11-10-taste-of-golf-instructions-notice.html"       # gotwicz 1a1c6a3df667d596 Tue Nov 10 12:20 PM ET
WM_COPY_LADIES_LUNCH = "2026-11-09-ladies-christmas-luncheon-notice.html"     # gotwicz 1a1c1e454ceb4faf Mon Nov 9 2:58 PM ET
IRRIGATION_TITLE = "North Irrigation Down"   # RPM subject "[#XN9559224] Message from Home Owners of Palm Hill, Inc - North Irrigation Down"
IRRIGATION_BODY = "The irrigation system in the North section has been temporarily shut down due to a damaged riser. Our maintenance team is assessing the damage and will make repairs as soon as possible."
EXERCISE_TITLE = "Exercise Class"            # R93: subject "Exercise Class Beginning Tuesday, November 17th" -- date words stay off the title
EXERCISE_BODY = "The winter session of the Exercise Class will begin on Tuesday, November 17, 2026 at 9am, North Clubhouse."
EXERCISE_DATE = "Begins: Tuesday, November 17, 2026 at 9am · North Clubhouse"
TOG_INSTR_TITLE = "Taste of Golf Instructions"
TOG_INSTR_BODY = "These are the initial instructions for all participants of Taste of Golf."
TOG_INSTR_BULLETS = ["Groups are posted at the Pro Shop, North and South Clubhouses.",
    "Each assigned group is identified by the name of the leader.",
    "Leaders will be identified with signs to welcome you.",
    "Meet at the parking lot behind The Pro Shop on November 18th at 10:00AM.",
    "Only you and your cart are allowed in the parking lot.",
    "Your Car must be Parked in Another Location.",
    "Bring your golf clubs and golf cart if you are using them.",
    "You will receive all further instructions when you arrive for your fun day."]
TOG_INSTR_DATE = "Meet: November 18th at 10:00AM · parking lot behind The Pro Shop"
LADIES_LUNCH_TITLE = "Ladies Christmas Luncheon"   # R93: subject "December 2, 2026 Ladies Christmas Luncheon" -- date stays off the title
LADIES_LUNCH_BODY = ("If you would like to purchase tickets for the 12/2/26 Ladies Christmas Luncheon at The Bayou Club, please contact me ASAP before they are sold out. "
    "This year we'll be enjoying a delicious Italian buffet.  Tickets are $32 each and are selling fast.  Contact Sandy Obi at (585)797-4299.")
LADIES_LUNCH_DATE = "Luncheon: 12/2/26 · The Bayou Club"
CAROLYN_BOARD_TITLE = "Serving on the Palm Hill Board of Directors"
CAROLYN_BOARD_BODY = "A board member is the guardian of your community, assets, and lifestyle."
CAROLYN_BOARD_DATE = "First published: November 2026"
CAROLYN_BOARD_PAGE = "2026-11-carolyn-story-serving-on-the-board.html"
# Fri Nov 13 2026 sweep (Steven approved adding these Webmaster emails). Verbatim bodies; unsubscribe left out. gotwicz Gmail.
# Parade + route emails are image-only flyers (club-site images); transcribed text is only what is clearly printed.
WM_COPY_CANTATA = "2026-11-13-singing-ensemble-christmas-cantata-notice.html"   # gotwicz 1a1d72de67a369a3 Fri Nov 13 12:30 PM ET (Mollie Cardno)
WM_COPY_PARADE = "2026-11-13-palm-hill-annual-golf-cart-parade-notice.html"     # gotwicz 1a1d63b9403c2f14 Fri Nov 13 10:36 AM ET (image-only flyer)
WM_COPY_ROUTE = "2026-11-13-christmas-golf-cart-route-notice.html"              # gotwicz 1a1d6405a331ef88 Fri Nov 13 10:38 AM ET (image-only map)
WM_COPY_SCAM = "2026-11-12-amazon-scam-email-notice.html"                       # gotwicz 1a1d214b00d8d6ce Thu Nov 12 1:29 PM ET (Bob Newport)
CANTATA_TITLE = "Singing Ensemble for Christmas Cantata"
CANTATA_BODY = "Share your singing talents with us as the Palm Hill Christmas Cantata Ensemble begins rehearsing this Sunday! To accommodate those attending the Fall Festival, this weekend's rehearsal will take place at 7:00 p.m. in the North Clubhouse. The Cantata will be presented on Sunday, December 6th at 4:00 p.m. in the North Clubhouse, celebrating the true meaning of Christmas through song and narration."
CANTATA_DATE = "Rehearsal: this weekend at 7:00 p.m. in the North Clubhouse · Cantata: Sunday, December 6th at 4:00 p.m. in the North Clubhouse"
SCAM_TITLE = "Amazon Scam Email"
SCAM_BODY = "You may have received an email from Bob Newport today requesting you to purchase an Amazon Gift Card for him. It is a SCAM. When ever getting an email like this please get in contact with the person you received the email from first before doing anything."
PARADE_TITLE = "Palm Hill Annual Golf Cart Parade"
PARADE_IMG = "https://www.palmhillcountryclub.net/editor_upload/Image/7112E469-713E-427C-A764-6C9A2CE4F4FA.png"
PARADE_ALT = "Palm Hill Annual Christmas Golf Cart Parade. December 12th, 2026. Line up 5:30 PM in front of the North Clubhouse. Ending at South Clubhouse. Batteries should be fully charged. Parade takes 1.5 hours to complete."
PARADE_TEASER = "December 12th, 2026. Line up 5:30 PM in front of the North Clubhouse. Ending at South Clubhouse. Batteries should be fully charged. Parade takes 1.5 hours to complete."
PARADE_DATE = "Parade: December 12th, 2026 · Line up: 5:30 PM in front of the North Clubhouse · Ending at South Clubhouse"
ROUTE_TITLE = "Christmas Golf Cart Route"
ROUTE_IMG = "https://www.palmhillcountryclub.net/editor_upload/Image/IMG_2330.png"
ROUTE_ALT = "Hand-drawn route on the Palm Hill Country Club map, with START and END labeled. Palm Hill Country Club, 1800 Seminole Boulevard, Largo, Florida 33770, Office: 554-6799."
ROUTE_TEASER = "START. END. Palm Hill Country Club, 1800 Seminole Boulevard, Largo, Florida 33770. Office: (727) 554-6799."
# Sat Nov 7 2026 morning sweep (draft, before Susan's proof). Verbatim bodies; unsubscribe already absent.
WM_COPY_CHAIR_YOGA = "2026-11-07-chair-yoga-class-canceled-notice.html"                 # gotwicz 1a1b5cc77232729c Sat Nov 7 6:37 AM ET
WM_COPY_WATER_1111 = "2026-11-06-south-potable-water-shut-off-rescheduled-notice.html"  # gotwicz 1a1b174eb713f7a4 Fri Nov 6 10:23 AM ET (supersedes the 10:00am wording)
CHAIR_YOGA_TITLE = "Chair Yoga class canceled"   # R93: subject "Chair Yoga class canceled Monday" — date word stays off the title
CHAIR_YOGA_BODY = "The chair yoga class for Monday, November 9, is cancelled. Classes will resume November 16 at 9:15 a.m., South Clubhouse."
CHAIR_YOGA_DATE = "Cancelled: Monday, November 9 · Resumes: November 16 at 9:15 a.m., South Clubhouse"
WATER_1111_TITLE = "South Potable Water Shut off (rescheduled)"
WATER_1111_BODY = "South Potable Water Shut off scheduled for Wednesday, November 11th @ 10:00am has been rescheduled to shut off at 2:30pm for approximately 2 hours."
WATER_1111_DATE = "Shut off: Wednesday, November 11th · Rescheduled: 2:30pm for approximately 2 hours"  # source words (November 11th, 2:30pm); R93 needs a label on each dated part
CORNHOLE_IMG = "https://www.palmhillcountryclub.net/editor_upload/Image/827E9BE2-A63E-4981-99FA-CFDD9C846292.png"
SOUTHREC_IMG = "https://www.palmhillcountryclub.net/editor_upload/Image/South_Recreation_Club_Election_Smaller.jpeg"
WM_COPIES = [
    # Fri Nov 13 2026 sweep (Steven approved): newest first; parade and route are image-only flyers (R60a)
    (WM_COPY_CANTATA, "Singing Ensemble for Christmas Cantata", "Friday, Nov 13, 2026, 12:30 PM ET", [
        ("p", "Share your singing talents with us as the Palm Hill Christmas Cantata Ensemble begins rehearsing this Sunday!"),
        ("p", "To accommodate those attending the Fall Festival, this weekend's rehearsal will take place at 7:00 p.m. in the North Clubhouse."),
        ("p", "The Cantata will be presented on Sunday, December 6th at 4:00 p.m. in the North Clubhouse, celebrating the true meaning of Christmas through song and narration."),
        ("p", "We hope you will join us!"),
        ("p", "Many thanks,"),
        ("p", "Mollie Cardno"),
        ("p", "Palm Hill Cantata Ensemble")],
        dict(title=CANTATA_TITLE)),
    (WM_COPY_ROUTE, "Christmas Golf Cart Route", "Friday, Nov 13, 2026, 10:38 AM ET", [
        ("img", (ROUTE_IMG, ROUTE_ALT)),
        ("p", "START"),
        ("p", "END"),
        ("p", "Palm Hill Country Club"),
        ("p", "1800 Seminole Boulevard"),
        ("p", "Largo, Florida 33770"),
        ("p", "Office: (727) 554-6799")],  # Steven Nov 13 8:54 PM ET: "yes, 727 for office number"
        dict(title=ROUTE_TITLE)),
    (WM_COPY_PARADE, "Palm Hill Annual Golf Cart Parade", "Friday, Nov 13, 2026, 10:36 AM ET", [
        ("img", (PARADE_IMG, PARADE_ALT)),
        ("p", "Palm Hill Annual Christmas Golf Cart Parade"),
        ("p", "December 12th, 2026"),
        ("p", "Line up 5:30 PM in front of the North Clubhouse"),
        ("p", "Ending at South Clubhouse"),
        ("p", "Batteries should be fully charged."),
        ("p", "Parade takes 1.5 hours to complete.")],
        dict(title=PARADE_TITLE)),
    (WM_COPY_SCAM, "Amazon Scam Email", "Thursday, Nov 12, 2026, 1:29 PM ET", [
        ("p", "Attention Residents:"),
        ("p", SCAM_BODY),
        ("p", "Thanks!"),
        ("p", "Bob Newport")],
        dict(title=SCAM_TITLE)),
    # Nov 15 sweep (Thu Nov 12 2026): newest first
    (WM_COPY_IRRIGATION, "[#XN9559224] Message from Home Owners of Palm Hill, Inc - North Irrigation Down", "Thursday, Nov 12, 2026, 12:13 PM ET", [
        ("p", "Dear Homeowners,"),
        ("p", IRRIGATION_BODY),
        ("p", "Until repairs are complete, the North section's irrigation system will remain off. We will update you when the system is back in service."),
        ("p", "Thank you for your patience. If you have questions, please contact the Association office at (727) 581-8729."),
        ("p", "Sincerely,"),
        ("p", "Resource Property Management, Inc. on behalf of Home Owners of Palm Hill, Inc"),
        ("p", "(727) 581-2662 | www.resourcepropertymgmt.com")],
        dict(source="Source: Resource Property Management message to residents, copied as sent.",
             sender="Resource Property Management", title=IRRIGATION_TITLE)),
    (WM_COPY_EXERCISE, "Exercise Class Beginning Tuesday, November 17th", "Tuesday, Nov 10, 2026, 11:22 PM ET", [
        ("p", EXERCISE_BODY),
        ("p", "Connie Paxhia"),
        ("p", "727-586-0313")],
        dict(title=EXERCISE_TITLE)),
    (WM_COPY_TOG_INSTR, "Taste of Golf Instructions", "Tuesday, Nov 10, 2026, 12:20 PM ET", [
        ("p", TOG_INSTR_BODY),
        ("ul", TOG_INSTR_BULLETS),
        ("p", "Carolyn Zimmerman")],
        dict(title=TOG_INSTR_TITLE)),
    (WM_COPY_LADIES_LUNCH, "December 2, 2026 Ladies Christmas Luncheon", "Monday, Nov 9, 2026, 2:58 PM ET", [
        ("p", LADIES_LUNCH_BODY),
        ("p", "Submitted by:"),
        ("p", "Sandy Obi"),
        ("p", "(585)797-4299")],
        dict(title=LADIES_LUNCH_TITLE)),
    # Sat Nov 7 morning sweep: newest first (Chair Yoga Sat 6:37 AM ET, then the Fri 10:23 AM ET water reschedule)
    (WM_COPY_CHAIR_YOGA, "Chair Yoga class canceled Monday", "Saturday, Nov 7, 2026, 6:37 AM ET", [
        ("p", CHAIR_YOGA_BODY),
        ("p", "Rebecca Baker"),
        ("p", "(509) 630-3403")],
        dict(title=CHAIR_YOGA_TITLE)),
    (WM_COPY_WATER_1111, WATER_1111_TITLE, "Friday, Nov 6, 2026, 10:23 AM ET", [
        ("p", WATER_1111_BODY),
        ("p", "Sincerely,"),
        ("p", "Resource Property Management, Inc. on behalf of Home Owners of Palm Hill, Inc"),
        ("p", "(727) 581-2662 | www.resourcepropertymgmt.com")],
        dict(source="Source: Resource Property Management message to residents, copied as sent.",
             sender="Resource Property Management", title=WATER_1111_TITLE)),
    # Sat Oct 31 6 PM sweep: Sat Oct 31 Webmaster emails, verbatim (staged pending Steven); flyer shown as sent, its words as text (R60a)
    (WM_COPY_CORNHOLE, "Cornhole Tournament", "Saturday, Oct 31, 2026, 11:11 AM ET", [
        ("img", (CORNHOLE_IMG, "Cornhole Tournament. Palm Hill Country Club. Saturday, November 28, 2026. Registration ends at 10:15AM. $5 per player, includes hot dog lunch. All levels welcome. Sign up in both clubhouses. Contact Earl & Sandy Sullivan 518-866-2079.")),
        # the email body is one flyer image (no text); shown as sent, its words as text (R60a; R101: flyer phone number included -- Steven Oct 31 7:33 PM)
        ("p", "Cornhole Tournament, Palm Hill Country Club"),
        ("p", "Saturday, November 28, 2026"), ("p", "Registration ends at 10:15AM"),
        ("p", "$5 per player, includes hot dog lunch"), ("p", "All levels welcome"),
        ("p", "Sign up in both clubhouses"), ("p", "Contact Earl & Sandy Sullivan 518-866-2079")]),
    (WM_COPY_SENIOR_LL, "REMINDER: Senior Empowerment Lunch & Learn", "Saturday, Oct 31, 2026, 9:53 AM ET", [
        ("h", "Senior Empowerment Lunch & Learn"),
        ("p", "When: Wednesday, November 4"), ("p", "Time: 10 a.m.\u20131 p.m."), ("p", "Where: South Clubhouse"),
        ("p", "A few friendly reminders:"),
        ("p", "Please arrive no earlier than 10 a.m."),
        ("p", "Lunch registration is now closed. Advance sign-up was required to receive lunch."),
        ("p", "You may still attend without signing up."),
        ("p", "Please plan to stay until 1 p.m. to hear from all healthcare providers and visit each table."),
        ("p", "Please sign in when you arrive."),
        ("p", "We look forward to seeing you there!"),
        ("p", "Your Palm Hill Wellness Team & Largo Police Senior Services"),
        ("p", "Respectfully submitted,"), ("p", "Bonnie Swanson")],
        dict(title="Senior Empowerment Lunch & Learn")),
    (WM_COPY_WORSHIP, "Reminder - Worship Service Tomorrow", "Saturday, Oct 31, 2026, 8:02 AM ET", [
        ("h", "Worship Service"),
        ("p", "Sunday, November 1"), ("p", "4:00 p.m.  (Doors open at 3:30)"),
        ("p", "Please join us at our Palm Hill Worship service on Sunday, November 1 at 4 o\u2019clock in the North Club House."),
        ("p", "Communion will be served and the Palm Hill Worship Choir, along with Barbara Brubaker on the piano, will fill the hall with music.   If you would like to sing with the choir or play an instrument,  please contact Mollie at 269-317-6890."),
        ("p", "This is a non-denominational service and all are welcome.   Our mission is to provide a place for all to connect with God. Our purpose is to Love God,  Love People, Reach Up,  Reach Out and Reach In."),
        ("p", "For information please contact our Worship Team: Claudia Hartz  (315) 368-8166, Steve or Maureen Livers (727) 481-8142, Mollie Cardno (269) 317-6890, Bernadette Witkiewicz (585) 749-2348, Bonnie Swanson (716) 870-3208."),
        ("p", "Submitted by:"), ("p", "Claudia  Hartz"), ("p", "Worship Team")],
        dict(title="Worship Service")),
    # Sat Oct 31 morning sweep: Fri Oct 30 evening Webmaster emails, verbatim (staged pending Steven)
    (WM_COPY_CHANNEL, "How to access the Palm Hill Community Channel", "Friday, Oct 30, 2026, 7:54 PM ET", [
        ("h", "How to Watch the Palm Hill Community Channel"), ("h", "Using Your XUMO Remote"),
        ("p", "Follow these simple steps to access Palm Hill Community News and Meetings on your television."),
        ("p", "Step 1: Turn on your television."),
        ("p", "Step 2: Select Spectrum and go to any TV channel."),
        ("p", "Step 3: Press the Back button on your XUMO remote twice."),
        ("p", "Step 4: At the top of your TV screen, you should see the following menu:"),
        ("p", "Home | Live TV | My Library | On Demand"),
        ("p", "Make sure Home is highlighted."),
        ("p", "Step 5: Using the large center navigation button on your XUMO remote, continue moving down through the Home screen until you reach the bottom."),
        ("p", "Step 6: Look for \u201cMy Community Channel.\u201d"),
        ("p", "Step 7: Highlight the bright blue \u201cView Now\u201d button and press the center OK/Select button on your remote."),
        ("p", "Step 8: Your Palm Hill Community Channel will open!"),
        ("p", "You\u2019re all set!"),
        ("p", "You can now enjoy Palm Hill Community News, meetings, and other important community information right from your television."),
        ("p", "Gail Stott"), ("p", "Webmaster"), ("p", "Palmhill.webmaster1@gmail.com")]),
    (WM_COPY_LINK_DEC, "December Link Deadline", "Friday, Oct 30, 2026, 6:44 PM ET", [
        ("p", "The next Link Deadline arrives this Thursday, November 5. Anything you need or want to appear in the December Link needs to be submitted by November 5."),
        ("p", "Submit your information to:"), ("p", "phcclink@gmail.com"),
        ("p", "Thank you,"), ("p", "Lisa Bria"), ("p", "727- 417-6742")]),
    # Oct 29 emails (Steven Oct 30 2026 8:29 PM), verbatim; the 5th element (optional) = notice_page.render keywords (R95)
    (WM_COPY_AMAZON, "Missing Amazon Package", "Thursday, Oct 29, 2026, 1:54 PM ET", [
        ("p", "We are search for an Amazon package that was delivered to the wrong address.  If you happen to see it please get in touch with Teddi McCune 727-481-1855 at 31 Thatch Palm W."),
        ("p", "Thank you!"), ("p", "Teddi McCune")]),
    (WM_COPY_WATER_S, "Message from Home Owners of Palm Hill, Inc - South Potable Water Shut off  Wednesday, November 4, 2026 from 10:00am for approximately 2 hours", "Thursday, Oct 29, 2026, 1:45 PM ET", [
        ("p", "Resident requested - South Potable Water Shut off  Wednesday, November 4, 2026 from 10:00am for approximately 2 hours"),
        ("p", "Sincerely,"), ("p", "Resource Property Management, Inc. on behalf of Home Owners of Palm Hill, Inc"),
        ("p", "(727) 581-2662 | www.resourcepropertymgmt.com")],
        dict(source="Source: Resource Property Management message to residents, copied as sent.", sender="Resource Property Management",
             title="South Potable Water Shut off")),
    (WM_COPY_SOCIAL_SHUFFLE, "Social Shuffle Begins Monday. November 2nd", "Thursday, Oct 29, 2026, 12:36 PM ET", [
        ("p", "Join us for Social Shuffle in the North Shuffleboard Courts on Monday\u2019s at 11:00am, beginning November 2nd, 2026."),
        ("p", "This is a weekly event which runs through March of 2027. Social Shuffle is a great way to learn more about the game of Shuffleboard. All skill levels are welcome."),
        ("p", "Please remember to wear closed toe shoes for your safety."),
        ("p", "If you have any questions, call Stewart."), ("p", "702-544-2649")]),
    (WM_COPY_MENS_GOLF, "Palm Hill Men's Golf Association Meeting", "Thursday, Oct 29, 2026, 10:43 AM ET", [
        ("h", "Palm Hill Men's Golf Association Meeting"),
        ("p", "When:   Monday, November 2, 2026"), ("p", "Time:   10:30 AM"), ("p", "Where:  North Clubhouse"),
        ("p", "If you have any questions please let one of us know."),
        ("p", "Jeff Wesolowski, President"), ("p", "Randy Mitchell, Vice President"), ("p", "Wayne Marshall, Secretary"), ("p", "Tom Locher, Treasurer")]),
    (WM_COPY_SPAGHETTI, "Spaghetti Tickets - Still Available", "Thursday, Oct 29, 2026, 10:13 AM ET", [
        ("p", "If anyone wants Spaghetti tickets for Sat November 14th please contact Mary Lou Shaw at 608-312 -6958.I was called back to Massachusetts on a family emergency. Sorry for any inconvenience."),
        ("p", "Joe Martin"), ("p", "Mesco")]),
    (WM_COPY_LIBRARY, "Library Closed starting the week of October 26th", "Thursday, Oct 22, 2026, 1:48 PM ET", [
        ("p", "We are very excited to offer our residents and their guests the experience of our Haunted Library again this year.  Our designer, Duane Smathers, along with Judy Flannigan, will be creating another Library that will definitely reflect the Halloween spirit."),
        ("p", "As additional animatronics will be featured, they will need the upcoming week to transform the room.   Therefore the Library will be closed beginning MONDAY, OCTOBER 26TH through SUNDAY, NOVEMBER 1ST."),
        ("p", "If you would like to pick up a book, please do so by Sunday the 25th.  To return books during that week,  Heidi Weeks has kindly placed a box in our main Recreation Hall near the curtain by the library for that purpose.   We so appreciate everyone's understanding and patience."),
        ("p", "Thank you,"),
        ("p", "Mollie Cardno"), ("p", "Inside Entertainment"), ("p", "North Recreation Hall")]),
    (WM_COPY_STOP, "Please observe important stop sign rules", "Wednesday, Oct 21, 2026, 9:42 AM ET", [
        ("p", "We hope this message finds you well. We are writing to remind all residents and their guests to please observe the posted speed limits and come to a complete stop at all stop signs throughout our community."),
        ("p", "As our northern friends join us for the season, there will be more vehicles on the road, making it even more important that we all follow these safety guidelines."),
        ("p", "The safety of our residents, their families, and guests is our top priority. Many of our neighbors enjoy walking, jogging, and cycling throughout Palm Hill, and we want to ensure everyone can do so safely."),
        ("p", "Please remember to:"),
        ("ul", ["Observe the posted speed limit at all times",
                "Come to a complete stop at all stop signs whether you are in a car, on a bike or in a golf cart",
                "Watch for pedestrians, cyclists, and golf carts",
                "Remind your guests and service providers of these safety rules"]),
        ("p", "Your cooperation in maintaining a safe environment for everyone is greatly appreciated. If you have any questions or concerns, please don't hesitate to contact the office at (727) 581-8729."),
        ("p", "Thank you for your attention to this important matter."),
        ("p", "Sincerely,"),
        ("p", "Resource Property Management, Inc. on behalf of Home Owners of Palm Hill, Inc")]),
    (WM_COPY_SOUTHREC, "2027 South Rec Club Seeking Officers", "Wednesday, Oct 21, 2026, 9:34 AM ET", [
        # the email body is one flyer image (no text); the flyer is shown as sent, alt text = its words (personal phone numbers left out)
        ("img", (SOUTHREC_IMG, "South Recreation Club. 2027 Election. Make a Difference! The South Recreation Club has the following positions available for the 2027 election: Inside Entertainment, Outside Entertainment, Bazaar Director. Deadline: December 2, 2026 at the close of the business meeting. If you're interested, please contact a search committee member: Joan Dougall, Martha Ladd, Tony Ciaramitaro. Get Involved... Help Keep Our Club Great! Thank you!")),
        ("p", "The South Recreation Club has the following positions available for the 2027 election: Inside Entertainment, Outside Entertainment, Bazaar Director."),
        ("p", "DEADLINE: December 2, 2026 at the close of the business meeting."),
        ("p", "If you're interested, please contact a search committee member: Joan Dougall, Martha Ladd, Tony Ciaramitaro.")]),
    (WM_COPY_SANIT, "Help with maintaining Sanitation Field", "Thursday, Oct 22, 2026, 1:42 PM ET", [
        ("p", "Dear Palm Hill Residents,"),
        ("p", "We need your help in maintaining our sanitation field and keeping disposal areas properly organized."),
        ("p", "Brush Dumpster - Brush Only: Please remember that the brush dumpster is designated for brush and yard waste ONLY. Do not place any trash, plastic bags, or other materials in this dumpster or on the brush pile near it. Only natural brush and plant material should be disposed of here."),
        ("p", "Broken Pavers: If you have broken pavers, please do not leave them in the sanitation field. All broken pavers and similar construction debris should be placed in the construction dumpster."),
        ("p", "Proper sorting helps us manage waste efficiently and keeps costs down for our community. Thank you for your cooperation in following these guidelines."),
        ("p", "If you have questions about where to dispose of specific items, please contact the office at (727) 581-8729."),
        ("p", "Thank you for helping keep Palm Hill clean and well-maintained."),
        ("p", "Sincerely,"),
        ("p", "Resource Property Management, Inc. on behalf of Home Owners of Palm Hill, Inc")]),
    (WM_COPY_COUPLES, "Couples Golf Leagur", "Tuesday, Oct 20, 2026, 11:59 PM ET", [   # subject as sent
        ("p", "Couples Golf League will be starting November 5th. A sign-up sheet for play and a Host Sign-up sheet, for the whole season, is posted at the Pro Shop. Couples League needs Hosting Volunteers."),
        ("p", "For Palm Hill Couples interested, please sign up and reach out to Mike McCarthy with any questions."),
        ("p", "Look forward to a fun Golf Season!"),
        ("p", "Julie Hughes")]),
    (WM_COPY_PANCAKES, "November Pancakes & Coffee Volunteers", "Thursday, Oct 15, 2026, 10:29 AM ET", [
        ("p", "An announcing chairperson is needed for the month of November for the North Club House coffees."),
        ("p", "8 volunteers are needed for November coffees in the North."),
        ("p", "14 volunteers are needed for pancakes on November 14th - arrival time is 7:30 AM"),
        ("p", "Please use the sign up sheets on the bulletin board at the north clubhouse."),
        ("p", "Thank you,"),
        ("p", "Mollie Cardon")]),
    (WM_COPY_SHUFFLE, "Shuffleboard Information", "Monday, Oct 12, 2026, 5:24 PM ET", [
        ("h", "With shuffleboard season approaching, just a few reminders:"),
        ("ul", ["For safety reasons, please do not walk on the courts.",
                "After use, return the disc to holders, and place under benches.",
                "After use, return cue sticks to wall hangers.",
                "When leaving the buildings, close the windows and turn off the lights and fans.",
                "All persons under 18 years old must be accompanied by an adult.",
                "No smoking.",
                "For safety, wear closed toe shoes"]),
        ("h", "Additional information for the north courts with embedded beads:"),
        ("ul", ["Do not drop the disc directly onto the beaded surface, as that can dislodge the beads. Place the disc outside of the playing area and push them forward into the kitchen to start play."]),
        ("p", "Thank you from the Shuffleboard Club.")]),
    (WM_COPY_GOLF, "Taste of Golf", "Wednesday, Oct 14, 2026, 11:31 PM ET", [
        ("h", "Palm Hill Country Club"),
        ("h", "\u201cTaste of Golf\u201d"),
        ("h", "November 18, 2026; 10 AM"),
        ("p", "Welcome New Golfers & Residents for a fun filled day to learn & play golf."),
        ("p", "Meet at Pro Shop.  Event is FREE."),
        ("p", "Golf teachers on each hole, teaching golf basics: Golf etiquette, Warm-up, Driving, Chipping, Putting, Reading the green."),
        ("p", "Not a golfer\u2026.Come walk & watch & enjoy the beauty of the course."),
        ("p", "Treats on each hole & enjoy a Hot Dog on the Pro Shop patio!"),
        ("p", "Join in on the fun and meet new friends!"),
        ("p", "Sign Up sheets:  Pro Shop, North Clubhouse, South Clubhouse"),
        ("p", "Questions contact:"),
        ("p", "Caroline Zimmerman")]),
]

# ---------- Community Notices (3): resident flyer + ice machine notice pages ----------
# Steven Oct 24 11:38 AM: Bill Bender's flyer (gotwicz, bbenderfla@outlook.com, Fri Oct 23 11:38 PM ET, "Please add to your news
# letter....", attachment "Mari, Card.jpg"; the message is in Spam and stays there). Page = flyer image + its text as printed.
# Bill's email/phone are printed on the flyer as the program contact, so they are kept.
HOLIDAY_PAGE = "2026-10-23-holiday-greeting-distribution-plan.html"
HOLIDAY_IMG = "/pages/assets/notices/2026-10-23-holiday-greeting-distribution-plan.jpg"  # copy of /workspace/sweep/1024-0930/bill-bender-mari-card.jpg
HOLIDAY_BLOCKS = [
    ("img", (HOLIDAY_IMG, "Holiday Greeting Distribution Plan flyer")),
    ("h", "Holiday Greeting Distribution Plan"),
    ("p", "A simple way for Palm Hill residents to send holiday greetings to friends and neighbors within the community."),
    ("h", "Purpose"),
    ("p", "To offer shareholders a distribution plan for holiday greetings at Hanukkah and Christmas time. Limited to addresses within Palm Hill that do not require postage."),
    ("h", "How It Works"),
    ("ul", ["Send 1 or 1100 greetings — there is no minimum or limit.",
            "Save the cost of outside postage, currently about $.82 per item in the U.S.",
            "Any resident can participate, limited to greetings within Palm Hill.",
            "Address greetings as you would a normal letter: name and address.",
            "Greetings will be deposited in specially designated drop boxes in the clubhouses. Deposits can be made anytime the boxes are available.",
            "Boxes will be monitored and emptied as necessary. Contents will be stored until holiday week.",
            "If you are leaving, please drop off before you depart.  If you are not on site, please contact Bill for instructions."]),
    ("h", "Important Notes"),
    ("ul", ["Amazon and Wal-Mart have online offerings now!",
            "Sorting will take place as often as necessary by our committee.",
            "Please clearly mark on the envelope any cards for Hanukkah to ease sorting."]),
    ("h", "Distribution"),
    ("ul", ["Distribution will be made by residents approximately 1 week before Hanukkah or Christmas.",
            "In addition to our 1100 homes, cards will also be accepted for the administration offices and maintenance employees.",
            "Canadian and Northern friends: feel free to reach out for suggestions on getting your cards to us."]),
    ("h", "Volunteers Welcome"),
    ("p", "As the program develops, additional folks will be needed for various tasks. Please notify us if you would like to help."),
    ("h", "Contact"),
    ("p", "Comments or questions should be directed to:"),
    ("p", "Bill Bender"), ("p", "BBenderfla@outlook.com"), ("p", "315-520-0263"),
    ("h", "Friends Greeting Friends"),
    ("p", "This program is solely to encourage friends and neighbors to connect during the holiday season — friends greeting friends. Share your thoughts."),
    ("p", "Thank you... Let’s Succeed!!!!!"),
    ("p", "Bill Bender, Kate Wesoloowski, & Mike Okash")]
# Steven Oct 24 1:27 PM: North Clubhouse ice machine notice = Elaine Cole's sentence (Oct 14 P&E report, verbatim) + Steven's own
# confirmed details (he checked it in person), his words formed into sentences, no added facts. Title chosen (no source heading).
ICE_PAGE = "2026-10-24-north-clubhouse-ice-machine-moved-notice.html"
ICE_TITLE = "North Clubhouse Ice Machine Moved"   # chosen title (flagged: no source heading)
ICE_ELAINE = "The ice machine has been relocated so it no longer is a nuisance to the classes."   # Elaine Cole, P&E Oct 14, verbatim
ICE_STEVEN = ["The ice machine in the North Clubhouse was moved out of the North meeting room and into the pool table room.",
              "It's more convenient, and people getting ice won't disturb any meetings going on in the meeting room."]
_ICE_PE = "2026-10-14-planning-and-environmental-committee-report.html"
ICE_TEASER = ICE_STEVEN[0]
# Generated notice pages (scripts/notice_page.py render): one dict per page; the core writes each page and its Listen copy.
NOTICE_PAGES = [
    dict(page=HOLIDAY_PAGE, subject="Please add to your news letter....", sent="Friday, Oct 23, 2026, 11:38 PM ET", blocks=HOLIDAY_BLOCKS,
         kw=dict(source="Source: flyer from Bill Bender (Mari, Card.jpg), shown as sent with its text transcribed as printed.",
                 title="Holiday Greeting Distribution Plan", sender="Bill Bender")),
    dict(page=ICE_PAGE, subject=ICE_TITLE, sent="Saturday, Oct 24, 2026", blocks=[
        ("h", "From the Planning and Environmental Committee Report (Oct 14, Elaine Cole)"), ("p", ICE_ELAINE),
        ("h", "Details confirmed by Steven Leonowicz"), ("p", " ".join(ICE_STEVEN))],
         kw=dict(source="Source: Oct P&E Committee Report", source_href=BASE + _ICE_PE, title=ICE_TITLE,
                 sender="Oct P&E Committee Report (Elaine Cole); details confirmed by Steven Leonowicz")),
]
# Source-verbatim checks: (exact sentence, report page it must appear in, rule note)
SOURCE_VERBATIM = [(ICE_ELAINE, _ICE_PE, "R60c: Elaine's ice machine sentence must be verbatim from the P&E Oct 14 report")]

# ---------- Community Notices (4): teasers (R18) and the notice list, in order; earlier-issue drops ----------
LINDA_TEASER = "Halloween Dance tickets are sold out. Be respectful at clubhouses. Largo Evening Market: Sat. Oct. 24th, 5-9pm, Ulmer Park."  # R42/R18: Linda's own words, all 3 sections, 3 lines max
SANIT_TEASER = "The brush dumpster is designated for brush and yard waste ONLY. Broken pavers should be placed in the construction dumpster."  # R18: source sentences, light trims
COUPLES_TEASER = "Couples Golf League will be starting November 5th. Couples League needs Hosting Volunteers."  # R18: source sentences verbatim
LIBRARY_TEASER = "The Library will be closed beginning MONDAY, OCTOBER 26TH through SUNDAY, NOVEMBER 1ST. Pick up books by Sunday the 25th."  # R18: source sentences verbatim
STOP_TEASER = "Please observe the posted speed limits and come to a complete stop at all stop signs throughout our community."  # R18: source sentence, lead-in trimmed
SOUTHREC_TEASER = "The South Recreation Club has positions available for the 2027 election. DEADLINE: December 2, 2026."  # R18: flyer wording
HOLIDAY_TITLE = "A convenient way to send holiday cards for Palm Hill residents"  # Steven correction Oct 24 11:39 AM: exact main-page title (R60b guard)
HOLIDAY_TEASER = "A simple way for Palm Hill residents to send holiday greetings to friends and neighbors within the community."  # flyer's own words, verbatim
NOTICES = [
    # Steven Nov 12 2026 (voice): Carolyn Story's Board piece, moved from Community Stories into Community Notices.
    # Full verbatim page + Listen stay at CAROLYN_BOARD_PAGE (Link Nov 2026 p 36).
    (CAROLYN_BOARD_TITLE, CAROLYN_BOARD_BODY, "Carolyn Story", BASE + CAROLYN_BOARD_PAGE),
    # Fri Nov 13 2026 sweep (Steven approved). Carolyn stays first. Then newest Webmaster emails; parade then route
    # are kept as a pair (route was sent 2 minutes later) so the event sits above its map.
    (CANTATA_TITLE, CANTATA_BODY, "Webmaster", BASE + WM_COPY_CANTATA),
    (PARADE_TITLE, PARADE_TEASER, "Webmaster", BASE + WM_COPY_PARADE),
    (ROUTE_TITLE, ROUTE_TEASER, "Webmaster", BASE + WM_COPY_ROUTE),
    (SCAM_TITLE, SCAM_BODY, "Webmaster", BASE + WM_COPY_SCAM),
    # Nov 15 sweep (Thu Nov 12 2026): newest first. Teasers are source sentences; summary_trim SHORT cuts them to 3 lines and adds More →.
    (IRRIGATION_TITLE, IRRIGATION_BODY, "RPM", BASE + WM_COPY_IRRIGATION),
    (EXERCISE_TITLE, EXERCISE_BODY, "Webmaster", BASE + WM_COPY_EXERCISE),
    (TOG_INSTR_TITLE, TOG_INSTR_BODY, "Webmaster", BASE + WM_COPY_TOG_INSTR),
    (LADIES_LUNCH_TITLE, LADIES_LUNCH_BODY, "Webmaster", BASE + WM_COPY_LADIES_LUNCH),
    # Sat Nov 7 morning sweep: newest first. Teasers are source sentences; summary_trim SHORT cuts them to 3 lines and adds More →.
    (CHAIR_YOGA_TITLE, CHAIR_YOGA_BODY, "Webmaster", BASE + WM_COPY_CHAIR_YOGA),
    (WATER_1111_TITLE, WATER_1111_BODY, "RPM", BASE + WM_COPY_WATER_1111),
    # R103 (Steven Oct 31 2026, via Susan): Webmaster December Link Deadline notice first in Community Notices
    ("December Link Deadline",
     "The next Link Deadline arrives this Thursday, November 5. Anything you need or want to appear in the December Link needs to be submitted by November 5. Submit your information to: phcclink@gmail.com",
     "Webmaster", BASE + WM_COPY_LINK_DEC),
    # Sat Oct 31 6 PM sweep (STAGED pending Steven): Sat Oct 31 Webmaster emails, newest first (11:11, 9:53, 8:02 AM ET); teasers = source wording (R18)
    ("Cornhole Tournament",
     "Registration ends at 10:15AM. $5 per player, includes hot dog lunch. All levels welcome. Sign up in both clubhouses. Contact Earl & Sandy Sullivan 518-866-2079.",
     "Webmaster", BASE + WM_COPY_CORNHOLE),
    ("Senior Empowerment Lunch & Learn",
     "Lunch registration is now closed. Advance sign-up was required to receive lunch. You may still attend without signing up. Please sign in when you arrive.",
     "Webmaster", BASE + WM_COPY_SENIOR_LL),
    ("Worship Service",
     "Please join us at our Palm Hill Worship service on Sunday, November 1 at 4 o\u2019clock in the North Club House. This is a non-denominational service and all are welcome.",
     "Webmaster", BASE + WM_COPY_WORSHIP),
    # Sat Oct 31 morning sweep (STAGED pending Steven): Fri Oct 30 evening Webmaster emails, newest first (7:54, 6:44 PM ET); teasers = source sentences (R18)
    ("How to access the Palm Hill Community Channel",
     "Using Your XUMO Remote: Follow these simple steps to access Palm Hill Community News and Meetings on your television. Step 1: Turn on your television. Step 2: Select Spectrum and go to any TV channel.",
     "Webmaster", BASE + WM_COPY_CHANNEL),
    # Steven Oct 30 2026 8:29 PM: five Oct 29 emails, newest first (sent 1:54, 1:45, 12:36, 10:43, 10:13 AM ET); teasers = source sentences (R18)
    ("Missing Amazon Package",
     "We are search for an Amazon package that was delivered to the wrong address. If you happen to see it please get in touch with Teddi McCune 727-481-1855 at 31 Thatch Palm W.",
     "Webmaster", BASE + WM_COPY_AMAZON),
    ("South Potable Water Shut off",
     "Resident requested - South Potable Water Shut off Wednesday, November 4, 2026 from 10:00am for approximately 2 hours.",
     "RPM", BASE + WM_COPY_WATER_S),
    ("Social Shuffle",   # R93: subject "Social Shuffle Begins Monday. November 2nd" -> date moved to the date line
     "Join us for Social Shuffle in the North Shuffleboard Courts on Monday\u2019s at 11:00am, beginning November 2nd, 2026. This is a weekly event which runs through March of 2027. All skill levels are welcome.",
     "Webmaster", BASE + WM_COPY_SOCIAL_SHUFFLE),
    ("Palm Hill Men's Golf Association Meeting",
     "When: Monday, November 2, 2026. Time: 10:30 AM. Where: North Clubhouse. If you have any questions please let one of us know.",
     "Webmaster", BASE + WM_COPY_MENS_GOLF),
    ("Spaghetti Tickets - Still Available",
     "If anyone wants Spaghetti tickets for Sat November 14th please contact Mary Lou Shaw at 608-312 -6958. I was called back to Massachusetts on a family emergency. Sorry for any inconvenience.",
     "Webmaster", BASE + WM_COPY_SPAGHETTI),
    # Steven Oct 24 11:38 AM: Bill Bender's flyer (resident notice; Source = Bill Bender, linked to its page)
    (HOLIDAY_TITLE, HOLIDAY_TEASER, "Bill Bender email", BASE + HOLIDAY_PAGE),
    # Steven Oct 24 1:27 PM: position 3 (right after Bill Bender); Source links the Oct 14 P&E report page
    (ICE_TITLE, ICE_TEASER, "Oct P&E Committee Report", BASE + _ICE_PE),
    # Steven Oct 23 6:38 PM: three more Webmaster emails (gotwicz), newest first; RPM duplicate of the stop sign email ignored
    ("Library Closed starting the week of October 26th", LIBRARY_TEASER, "Webmaster", BASE + WM_COPY_LIBRARY),
    # Steven Oct 23 5:09 AM (A, C): two Webmaster emails (gotwicz); one email = one notice (R42); RPM duplicate of the sanitation email ignored
    ("Help with maintaining Sanitation Field", SANIT_TEASER, "Webmaster", BASE + WM_COPY_SANIT),
    ("Please observe important stop sign rules", STOP_TEASER, "Webmaster", BASE + WM_COPY_STOP),
    ("2027 South Rec Club Seeking Officers", SOUTHREC_TEASER, "Webmaster", BASE + WM_COPY_SOUTHREC),
    ("Couples Golf League", COUPLES_TEASER, "Webmaster", BASE + WM_COPY_COUPLES),
    ("Swimming Pool Food and Beverage Rules",  # Webmaster, Fri Oct 16 12:29 PM ET (gotwicz 1a1458d5b589bff6); newest notice after Tony's
     "All food and beverages must be kept at least 4 feet away from the edge of the pool (the \"wet deck\" area). No glass containers of any kind are permitted inside the fenced pool area; please use plastic or other non-breakable containers. Residents are responsible for ensuring that their guests comply with all pool rules and regulations.",
     "Webmaster", BASE + "2026-10-16-swimming-pool-food-and-beverage-rules-notice.html"),
    ("November Coffee and Pancake Volunteers",
     "An announcing chairperson is needed for November coffees at the North Clubhouse, along with 8 coffee volunteers. Pancakes on Saturday, Nov 14 need 14 volunteers, arriving at 7:30 AM. Sign-up sheets are on the North Clubhouse bulletin board.",
     "Webmaster", BASE + WM_COPY_PANCAKES),  # L27/L29: linked short Webmaster, no date/sender
    ("Shuffleboard Season Reminders",
     "Please don't walk on the courts; return discs to their holders under the benches and cue sticks to the wall hangers; close windows and turn off lights and fans when you leave. Anyone under 18 must be with an adult, no smoking, and wear closed-toe shoes. On the north courts with embedded beads, don't drop the disc onto the beaded surface — set it outside the playing area and push it forward into the kitchen.",
     "Webmaster", BASE + WM_COPY_SHUFFLE),  # L27/L29: "(Shuffleboard Club)" is a sender name -> dropped
    ("Taste of Golf",   # R93: was "Taste of Golf — November 18" (date moved to NOTICE_DATE_LINE)
     "New golfers and residents are welcome on Wednesday, Nov 18 at 10:00 AM. Meet at the Pro Shop; it's free. Golf teachers on each hole cover etiquette, warm-up, driving, chipping, putting and reading the green, with treats on each hole and a hot dog on the Pro Shop patio. Not a golfer? Walk, watch and enjoy the course. Sign-up sheets are at the Pro Shop and both clubhouses.",
     "Webmaster", BASE + WM_COPY_GOLF),  # L27/L29
    # STYLE-RULES R42 (Steven, Oct 17 10:29 PM): one source email = one notice. Linda Keehl's "Info from Linda" (Webmaster, Thu Oct 8
    # 5:25 PM ET) has three sections -- Halloween Dance, PLEASE-PLEASE-PLEASE (clubhouse courtesy), Largo Evening Market -- so it is ONE
    # notice titled with her subject, teaser in her words covering all three (scripts/source_sections.py SOURCES + guard). More → and
    # Listen open the existing copy of her email (use_existing_page: no generated notice page). The old 2026-10-18-notice-clubhouse-
    # courtesy-during-busy-season.html stays live (URL valid) but is no longer linked from the issue. Her email is not an event source of
    # truth: the Halloween Dance Party row's date/time/room come from the calendar.
    ("Info from Linda",
     LINDA_TEASER,
     "Webmaster", BASE + "2026-10-08-info-from-linda-notice.html"),
    ("Property Fraud Alert",
     f'The Palm Hill webmaster shared the sign-up link for <a href="https://www.propertyfraudalert.com/select" style="color:{G};">Property Fraud Alert</a>, a free service that notifies you when a document is recorded under your name.',
     "Webmaster", BASE + "2026-09-30-property-fraud-alert-notice.html"),
    ("October Mowing Date",
     "Reminder: BrightView's next tentative resident mowing date is Tuesday, Oct 27. The schedule may change.",
     "RPM", BASE + "2026-09-29-mowing-dates-notice.html"),
]
# R93 (Steven Oct 30 2026 11:58 AM; approved 12:13 PM "yes to all"): every notice shows a brief date line directly under its title,
# "<What>: <date>" in source wording only (two dates split with " · "), or an approved "No date". Titles carry no dates.
NOTICE_DATES = True
NOTICE_DATE_LINE = {
    CAROLYN_BOARD_TITLE: CAROLYN_BOARD_DATE,
    CANTATA_TITLE: CANTATA_DATE,
    PARADE_TITLE: PARADE_DATE,
    EXERCISE_TITLE: EXERCISE_DATE,
    TOG_INSTR_TITLE: TOG_INSTR_DATE,
    LADIES_LUNCH_TITLE: LADIES_LUNCH_DATE,
    CHAIR_YOGA_TITLE: CHAIR_YOGA_DATE,
    WATER_1111_TITLE: WATER_1111_DATE,
    "Cornhole Tournament": "Tournament: Saturday, November 28, 2026 · Registration ends: 10:15AM",               # Webmaster Oct 31 flyer (staged)
    "Senior Empowerment Lunch & Learn": "When: Wednesday, November 4, 10 a.m.\u20131 p.m. · South Clubhouse",       # Webmaster Oct 31 (staged)
    "Worship Service": "Service: Sunday, November 1, 4:00 p.m. (Doors open at 3:30) · North Club House",                    # Webmaster Oct 31 (staged)
    "December Link Deadline": "Deadline: Thursday, November 5",                                                     # Webmaster Oct 30 (staged)
    "South Potable Water Shut off": "Shut off: Wednesday, November 4, 2026 from 10:00am for approximately 2 hours",   # RPM Oct 29
    "Social Shuffle": "Begins: November 2nd, 2026 at 11:00am · Runs: weekly through March of 2027",                # Webmaster Oct 29
    "Palm Hill Men's Golf Association Meeting": "Meeting: Monday, November 2, 2026, 10:30 AM · North Clubhouse",     # Webmaster Oct 29 (calendar: 10:00-11:30 AM North Main Hall -- flagged)
    "Spaghetti Tickets - Still Available": "Dinner: Sat November 14th",                                             # Webmaster Oct 29
    "A convenient way to send holiday cards for Palm Hill residents":
        "Distribution: approximately 1 week before Hanukkah or Christmas · If you are leaving: please drop off before you depart",  # Bill Bender flyer
    "2027 South Rec Club Seeking Officers": "Deadline: December 2, 2026 at the close of the business meeting",   # Webmaster Oct 21
    "Couples Golf League": "Starts: November 5th",                                                               # Webmaster Oct 20
    "November Coffee and Pancake Volunteers":
        "Coffees: month of November (North Clubhouse) · Pancakes: November 14th, arrival time 7:30 AM",         # Webmaster Oct 15
    "Taste of Golf": "Event: November 18, 2026; 10 AM · Meet at Pro Shop",                                       # Webmaster Oct 14
}
NOTICE_NO_DATE = {  # source gives no date; Steven Oct 30 2026 12:13 PM "yes to all": leave undated
    SCAM_TITLE: "Nov 15 draft: the Webmaster email (Thu Nov 12) warns about a scam received that day; no event date (flagged for Steven)",
    ROUTE_TITLE: "Nov 15 draft: the route email is an image-only map with START and END labels and no printed date (flagged for Steven)",
    IRRIGATION_TITLE: "Nov 15 draft: the RPM email (Thu Nov 12) gives no date or end date (flagged for Steven)",
    "How to access the Palm Hill Community Channel": "Sat Oct 31 morning sweep (staged); its email gives no date (flagged for Steven)",
    "Missing Amazon Package": "Steven Oct 30 2026 8:29 PM added it; its email gives no date (flagged for Steven)",
    "Join the Palm Hill Residents Group on Facebook": "Steven Oct 30 2026 12:13 PM",
    "Swimming Pool Food and Beverage Rules": "Steven Oct 30 2026 12:13 PM",
    "Shuffleboard Season Reminders": "Steven Oct 30 2026 12:13 PM",
}
# Steven Oct 20 3:03 PM: drop stale carried-over notices (Linda's Oct 24 market email, Oct 27 mowing date, Taste of Golf notice --
# Taste of Golf stays as an event row). Guard: none of these titles may appear in Community Notices.
NOTICES_DROPPED_OCT25 = {"October Mowing Date", "Property Fraud Alert"}  # Steven Oct 21 8:43 PM: Property Fraud Alert dropped (its Vercel page stays live)  # Steven Oct 21 11:20 AM: Info from Linda + Taste of Golf notice restored (R56 event cards link them)

# ---------- Community Notices (5): Listen overrides ----------
NOTICE_LISTEN_OVERRIDE = {
    ICE_TITLE: BASE + ICE_PAGE,  # R60c: Listen reads the notice's own page (Source is the P&E report)
    CAROLYN_BOARD_TITLE: BASE + "2026-11-listen-carolyn-story-serving-on-the-board.html",  # dedicated Listen page (same as when this was the Community Story)
}

# ---------- Committee Chair Reports: cards, full report pages, archive-only reports, archive rows ----------
# ---------- Chair reports: stacked cards (to-do #12) ----------
CHAIR = [  # newest first; no Source line; no word "Report" in titles; 17px summary; action row at bottom
    ("Communications Committee", "2026-09-21", "Tony Ciaramitaro chaired his first meeting: booking system, Facebook trial, Zoom training.",
     BASE + "2026-09-21-communications-committee-report.html", BASE + "2026-10-04-listen-communications-committee-report.html"),
    ("Planning and Environmental Committee", "2026-09-09", "The committee found buying the land HOPH rents feasible; its report is with the Board.",
     BASE + "2026-09-16-planning-and-environmental-committee-report.html", BASE + "2026-10-04-listen-planning-environmental-committee-report.html"),
    ("Golf Advisory Committee", "2026-09-08", "Sprinkler work continues and hole #1 has a new sand trap. Golf clinic proposed for Nov 18.",
     BASE + "2026-09-08-golf-advisory-committee-report.html", BASE + "2026-10-04-listen-golf-advisory-committee-report.html"),
]
# Steven, Oct 17 1:40 PM (post-proof addition): Golf Advisory Committee summary from Carolyn Story (nystory11@gmail.com),
# palmhillblast "Golf Advisory Committee", Sat Oct 17 1:20 PM ET. Meeting date: not stated in the email; Tuesday Oct 13, 2026
# per the calendar-confirmed Golf Committee meeting (agenda: Board liaison Carolyn Story, Communications request, next meeting
# Nov 10) and "Finances (as of 10/13)". Full text = Carolyn's wording, block by block (scripts/chair_report_page.py).
GOLF_1013_PAGE = "2026-10-13-golf-advisory-committee-report.html"
GOLF_1013_LISTEN = "2026-10-18-listen-golf-advisory-committee-report.html"
GOLF_1013 = [
    ("p", "Please find the summary of our recent meeting notes below:"),
    ("h2", "Finances (as of 10/13) – Megan Leftwich"),
    ("ul", ["Budget: $2,534.31 over budget for the month; $5,519.89 over YTD.",
            "Activity: 76 paid memberships, 46 paid cart fees, and 8 ten-packs sold."]),
    ("h2", "Golf Course Update – Joe Clay, Superintendent"),
    ("ul", ["Course Conditions: Weather is currently affecting growth, but normal conditions are expected in about a week.",
            "Projects: Pro Shop plantings are complete, sod green work is ongoing, and new sand traps were added."]),
    ("h2", "Board Liaison Update – Carolyn Story"),
    ("ul", ["The amended Code of Conduct was unanimously approved by the Board of Directors on September 26, 2026.",
            "Commended the team on the upcoming Golf Clinic."]),
    ("h2", "Code of Conduct & Accountability – Caroline Zimmerman, Chair"),
    ("ul", ["Posting: The approved Code of Conduct will be posted in the Link, Pro Shop, and sign-up area, and included in membership packets.",
            "Accountability: Members must pay before play each season. The membership list is available to the Pro Shop."]),
    ("h2", "Fiscal Year"),
    ("ul", ["The Golf Committee is currently processing a request to move the fiscal year start from July to April."]),
    ("h2", "Associations & Leagues"),
    ("ul", ["Women's League (Sue Waldecker): Friday morning slot is reserved; league starts Nov 6, with the first meeting on Nov 13. Volunteer/chair sign-ups are in the Pro Shop. First year using an online handicap system managed by K. Kummer and D. Southward.",
            "Couples League (Mike McCarthy): Hosting sign-up is available at the Pro Shop. Thanksgiving, Christmas Eve, and New Year's Eve will be open play.",
            "Bandits (Chuck Silcox): Members are slowly returning."]),
    ("h2", "Pro Shop & Events"),
    ("ul", ["Deep cleaning is complete, and two large artificial ferns are on order for the patio.",
            "Golf Clinic: 15 people signed up so far. Sign-up sheets are in the Pro Shop and North/South Clubhouses."]),
    ("h2", "Communication Committee"),
    ("ul", ["Approved minutes will be sent after each meeting for posting on the PHCC website."]),
    ("h2", "Next Meeting"),
    ("ul", ["Date & Time: November 10, 2026, at 2:00 PM EST", "Location: SCH"]),
]
# Oct 23 Friday build: Planning and Environmental Committee report from Elaine Cole (elainezcole@gmail.com), palmhillblast
# "Blast report of P&E 10/14", Fri Oct 23 2:43 PM ET (Google Docs attachment "On-line report of P&E 10/14"). Meeting date
# confirmed (R30) by the Webmaster agenda "Notice is given of a Planning and Environmental Meeting" (gotwicz, Oct 9) and the
# "Reminder: Planning and Environmental Committee Meeting Today" notice (Oct 14): Wed Oct 14, 2026, 1:00 PM, South Board Room.
# Full text = Elaine's wording, block by block. Her "12:30 a.m." for Nov 10 is kept as written (flagged for Steven).
PE_1014_PAGE = "2026-10-14-planning-and-environmental-committee-report.html"
PE_1014_LISTEN = "2026-10-25-listen-planning-environmental-committee-report.html"
PE_1014 = [
    ("p", "There were 3 items on the P&E agenda: update on progress in the north clubhouse for wellness classes, decision on laundry service lease, and master plan update."),
    ("p", "The committee approved a motion to the Board to pay $857.33 to WindowFilm LLC, to provide privacy coverings for wellness classes. The ice machine has been relocated so it no longer is a nuisance to the classes. A hydration station has been installed. This station will accommodate filling water bottles."),
    ("p", "The committee also approved a motion to the Board that it contract with Laundry Leasing LLC to provide and maintain 2 washers and 2 dryers. Committee members who researched the issue of Largo's Business Receipt Tax determined that this operation will not subject Palm Hill to the tax."),
    ("p", "The Master Plan sub-committee will meet in late-October. It is working on evaluating HOPH's assets."),
    ("p", "The next meeting will be on Tuesday, Nov. 10, at 12:30 a.m."),
]
# R79 (Steven, Oct 26 2026 11:25 AM): "a link named See the All Events List and a note on the all events page that says These are
# all events that are not on the Recurring Events Page" -- his wording, verbatim (no arrow, no trailing period).
ALL_EVENTS_PAGE = True
# R81 (Steven approved Oct 24; "go" Oct 26 2026 11:49 AM): Helpful Webpages 9 -> 7 links (docs/NOV1-START.md carry-over a)
LINKS_SEVEN = True
# R82 (Steven Oct 26 2026 11:49 AM): More → pages built from the calendar listing only; run_checks checks this calendar wording is on the page
R82_CAL_PAGES = {"Thanksgiving Dinner": "Mickey Bontrager, Elroy Bontrager, Kate and Jeff Wesolowski"}
ALL_EVENTS_LINK_TEXT = "See the All Events List"
ALL_EVENTS_NOTE = "These are all events that are not on the Recurring Events Page"
# R78 (Steven, Oct 26 2026 11:15 AM, option (a) of his reply to Tony): no date range in the Committee & Board Meeting Schedules
# header; one row per committee/board (R54) and agenda-wins (R62/R62b/R62c) unchanged.
MEETINGS_SHOW_RANGE = False
# R77 (Nov 1): Communications Committee Report, meeting of Monday Oct 12, 2026 -- Tony Ciaramitaro (tonysee99@outlook.com) to
# Chuck Silcox, cc palmhillblast, "Communications Committee Report - October 12, 2026 Meeting", Mon Oct 26 2026 10:01 AM ET
# (thread 1a17884503342ec9). Tony's wording verbatim, bullet by bullet; his email has a stray line break after the bullet
# marker before "Committee-run Zoom" -- joined into one bullet (no words changed). Title drops "- Meeting of October 12, 2026"
# (date goes on the date line, R77). Replaces the Sep 21 Communications card (latest per committee, 30-day retention).
COMMS_1012_PAGE = "2026-10-12-communications-committee-report.html"
COMMS_1012_LISTEN = "2026-11-01-listen-communications-committee-report.html"
COMMS_1012 = [
    ("ul", ["Six of nine members attended, and the September 21 minutes were approved.",
            "Webmaster: 66 email blasts have gone out to 1,362 addresses since the last meeting.",
            "Website: more than 78,000 page views and about 4,500 visitors in the last 90 days, almost half of the views on Homes for Sale and Rent. The site is getting a facelift ahead of its February renewal.",
            "Calendar: the new calendar and booking system went live September 30. RPM has its own Board Room page, and a public Events Calendar is under About.",
            "e-Newsletter: a weekly \"Did You Know\" rule is coming, at David Bates' suggestion.",
            "Facebook: Henry Klain approved the two-month trial on October 9. The committee agreed, with no objection, to include the private Palm Hill Country Club - Residents Only Group. Both are one-way with comments off, only Jean Stjernstrom and Tony Ciaramitaro post, and group members are checked against the member directory.",
            "Committee-run Zoom: the chair proposed automating meeting setup and recordings, and Megan offered RPM's help at meetings. Chuck, Gail and Megan will review and if necessary, will revise the process to reduce volunteer steps to setup and manage meetings.",
            "Candidates Night: Wednesday, January 6, at 6:30 p.m. 14 of 34 past candidates have answered the survey.",
            "Next meeting: Monday, November 9, 2026 at 10:00 a.m., South Clubhouse Boardroom and Zoom."]),
    ("p", "Thank you!"),
    ("p", "Tony Ciaramitaro"),
    ("p", "Communications Committee Chair"),
]
COMMS_1012_TEASER = "Facebook: Henry Klain approved the two-month trial on October 9."  # Tony's wording (R18, fits 3 lines)
# Chair reports with a generated full page (scripts/chair_report_page.py); the core writes the page (never overwriting a published
# one), seeds its listen-* page and puts the card at the top of CHAIR, in this order (so the last one listed ends up first).
CHAIR_REPORTS = [
    dict(page=GOLF_1013_PAGE, listen=GOLF_1013_LISTEN, title="Golf Advisory Committee Report", blocks=GOLF_1013,
         source="Source: Golf Advisory Committee Report (Carolyn Story)",
         card=("Golf Advisory Committee", "2026-10-13",
        "The amended Code of Conduct was unanimously approved by the Board of Directors on September 26, 2026.",  # Carolyn's wording
        BASE + GOLF_1013_PAGE, BASE + GOLF_1013_LISTEN)),
    dict(page=PE_1014_PAGE, listen=PE_1014_LISTEN, title="Planning and Environmental Committee Report", blocks=PE_1014,
         source="Source: Planning and Environmental Committee Report (Elaine Cole)",
         card=("Planning and Environmental Committee", "2026-10-14",
        "Motion to the Board: pay $857.33 to WindowFilm LLC, to provide privacy coverings for wellness classes.",  # Elaine's wording, trimmed to 3 lines (R18)
        BASE + PE_1014_PAGE, BASE + PE_1014_LISTEN)),
    dict(page=COMMS_1012_PAGE, listen=COMMS_1012_LISTEN, title="Communications Committee Report", blocks=COMMS_1012,
         source="Source: Communications Committee Report (Tony Ciaramitaro)",
         card=("Communications Committee", "2026-10-12", COMMS_1012_TEASER,
        BASE + COMMS_1012_PAGE, BASE + COMMS_1012_LISTEN)),
]
# Archive rows this issue adds (R59; archive/archive-items.json, idempotent on the row's page): (section, row)
ARCHIVE_ROWS = [
    ("committee-reports", {"date": "2026-10-14", "title": "Planning and Environmental Committee Report", "page": PE_1014_PAGE,
                                    "listen": PE_1014_LISTEN, "issues": ["2026-10-25"]}),
    ("committee-reports", {"date": "2026-10-12", "title": "Communications Committee Report", "page": COMMS_1012_PAGE,
                                    "listen": COMMS_1012_LISTEN, "issues": ["2026-11-01"]}),
]
# Rules and Regulations (Bob Newport, palmhillblast "Re: Committee Chair Reports Archive", Sat Oct 17 12:05 PM ET): the three
# attached reports are Mar 23, May 11 and Aug 10, 2026 -- all older than the 30-day retention cutoff (Sep 18), and Aug 10 is
# already published -- so none is added to the Oct 18 Chair Reports section without Steven's decision.
# Steven, Oct 17 (answer t839s3231): "Add March and May to the Chair Reports archive only". Full report + listen-* seed pages
# from Bob's own wording (Word files "Rules Mtg. March 23 26.docx", "Rules Meeting May 2026.docx"; R30), block by block, typos kept.
# ARCHIVE ONLY: not added to CHAIR (the Oct 18 issue / SEND are unchanged); archive rows live in archive/archive-items.json
# (committee-reports, issues: []) and build_archive.js adds the date line + R28 bottom-right speaker Listen. Aug 10 stays as published.
RULES_ARCHIVE_ONLY = [
    ("2026-03-23-rules-and-regulations-committee-report.html", "2026-03-23-listen-rules-regulations-committee-report.html", [
        ("p", "Rules and Regulation Committee"),
        ("p", "March 23, 2026 11 am"),
        ("p", "Boardroom, Zoom, and Ch.732"),
        ("p", "The Rules and Regulation Committee held a meeting on 23 March. 2026 at 11 am. Since this was the first meeting of the committee, the agenda was just topics for future actions, and discussions on Park issues. Also to allow the committee to meet each other."),
        ("p", "Topics for future actions and discussion are, Replacement of trees that are removed, ESA animals and the responsibility of them trespassing on others property, (especially where they toilet), Guns and Weapons Policy, Possible Speed Bump Locations, and Increasing the Application fee."),
        ("p", "There was Discussion of Rule Enforcement in the park, and this will be a subject for future discussion. The meeting was adjourned at 11:40 am.")]),
    ("2026-05-11-rules-and-regulations-committee-report.html", "2026-05-11-listen-rules-regulations-committee-report.html", [
        ("p", "Rules and Regulation Committee"),
        ("p", "May 11, 2026 1 pm"),
        ("p", "Boardroom, Zoom, and Ch.732"),
        ("p", "The Rules and Regulations Meeting was called to order at 1pm, and adjourned at 2:30pm. Although the length of the meeting was fairly long the number of Topics was limited. Discussion of a Firearms rule was briefly discussed but was tabled until further input could be accessed. There was also a brief discussion on Speed bumps but was tabled for future discussion. There was a lot of discussion on ESA dogs, but it is to be further reviewed in a Future meeting. The Committee reviewed the proposed Violations Policy, and made adjustments to it. It was then approved to be sent to the Board for adoption. The next meeting was set for August 10, 2026, at 1pm. Then the meeting was adjourned"),
        ("p", "Submitted by Bob Newport, Committee Laison")]),
]
RULES_ARCHIVE_TITLE = "Rules and Regulations Committee Report"
RULES_ARCHIVE_SOURCE = "Source: Rules and Regulations Committee Report (Bob Newport)"

# ---------- Community Story archive row label (story itself: STORY above) ----------
STORY_DATE_LABEL = "Nov 2026"   # archive "date_label" for this issue's story row (Link month, same form as Feb 2026 / Oct 2026)

# ---------- Weekly Manager Update (page items, PDF attachment, main-page card) ----------
# Weekly Manager Update Nov 6 (Megan Leftwich, weekly update email dated Friday, November 6, 2026) replaces Oct 30
# on this issue (retention rule). Built from the Oct 30 page's card template with her wording item by item (never
# hand-edited). No document was attached, so nothing is hosted (R65b). Oct 30 page and archive row stay as published.
# The Inliner day list and the Manager's Corner paragraphs sit under their bullets the way an earlier update nests
# follow-on paragraphs. The page sign-off stays the weekly-update shell.
WMU_1023_PAGE = "2026-11-06-weekly-manager-update.html"
WMU_1023 = [
    "The signed laundry lease has been sent over to Laundry Leasing Co. for them to countersign and then get the laundry room set up.",
    "The signed waiver for the transformer installation was sent to Duke yesterday. We can now expect approximately 6 weeks for the installation to be completed.",
    ("Inliner has been sent both signed change orders and has confirmed scheduling starting next Monday. The schedule is as follows:", [
        "Monday - shore up floor of basin",
        "Tuesday - install 48\" CIPP",
        "Wednesday - Wrap up any lining issues and roadway begins",
        "Thursday - Roadway work",
        "Friday - Roadway completion"]),
    "I already forwarded the information from Spectrum that they will begin removal of all coaxial infrastructure on 12/8. We will send out a notice to the residents regarding this. There is a lot going on, and with the Inliner work and meeting notices going out today, I don't want this to get lost in the shuffle. I have it calendared to send out next Thursday the 12th.",
    "With the Valet Trash being approved, we will be sending out weekly reminders that the trash and recycling pickup days will be changing. We will also be letting everyone know to have their bags out to the curb by 8am.",
    "The documents to bind the Assault & Battery coverage have been signed and returned to the insurance broker. We are now waiting on an invoice.",
    "The North pool lights were repaired this week. They brought the wrong lights with them on Monday and had to return on Wednesday.",
    "I am getting a quote to re-strap 18 lounge chairs and 3 regular chairs for the pool area.",
    "I met with Tony C from Communications this week. He has been working to update the website and the calendar, as you are all aware. We will be utilizing the calendar on the website for booking the Board Room and Small Conference Room in order to keep everything in one place. He is keeping the momentum from Victoria going!",
    ("We have started to get the meeting notice setup in GetQuorum for the First Notice and will be starting to make copies next week. I have submitted a Manager's Corner to the Link about the voting certificates and voting overall:", [
        "The Palm Hill election will be here soon, and we want everyone to be ready! The Annual Meeting is held at 1:00 p.m. in the North Clubhouse on the third Wednesday in January, which this coming year falls on January 20, 2027. Here are a few things to know before it is time to vote.",
        "Know Your Voting Certificate: Every home has a voting certificate on file. For most owners, it was completed when you purchased your home. It names the designated voter for your unit. If your household plans have changed, you can update the certificate at any time by completing a new form signed by ALL owners of the home. Not sure who your designated voter is? Just call or stop by the office. We're happy to help!",
        "Sign Your Ballot: Please ensure the designated voter signs your ballot. If the designated voter on the voting certificate hasn't signed it, the election inspectors will have to mark the ballot invalid on the morning of the meeting. We'd hate for your vote not to count!",
        "Watch for Emails from GetQuorum. Palm Hill uses GetQuorum to send electronic notices for the association. If you've consented to receive notices electronically, look for emails from GetQuorum. They contain your meeting notice and the link to vote when the time comes. Don't see them? Check your spam or junk folder and add GetQuorum to your safe senders list.",
        "A Note About Online Voting: Online voting is handled entirely by GetQuorum, so the office isn't involved in the process. When voting closes, we simply receive a report with the vote counts. If you have a technical question about your online ballot, the instructions in your GetQuorum email are the best place to start.",
        "Why Your Vote Matters: Every ballot helps Palm Hill reach quorum and keeps your community running smoothly. Please take a moment to vote, whether online or by paper ballot."]),
]
WMU_TEMPLATE = "2026-10-30-weekly-manager-update.html"   # previous update page = card template
WMU_GREETING = "Hello Everyone, Happy Friday!"
WMU_TEMPLATE_DATE = "2026-10-30"                         # must not survive in the new page (above the Listen block)
WMU_REPLACE = [("October 30, 2026", "November 6, 2026"), ("Oct 30, 2026", "Nov 6, 2026"),
               ("2026-10-30-weekly-manager-update", "2026-11-06-weekly-manager-update"), ("2026.10.30", "2026.11.6")]
# No document attachment on this update (signature images only, not newsletter copy). R65b: no PDF, no Attachments card.
WMU_1023_PDF_SRC = None
WMU_PDF_INLINE = {}
WMU_PDF_MISSING = []
ARCHIVE_ROWS_LATE = [   # archive rows added after the weekly update page is built (R59)
    ("weekly-manager-updates", {"date": "2026-10-23", "title": "Weekly Manager Update", "byline": "Megan Leftwich",
                                         "page": "2026-10-23-weekly-manager-update.html", "issues": ["2026-10-25"]}),
    ("weekly-manager-updates", {"date": "2026-10-30", "title": "Weekly Manager Update", "byline": "Megan Leftwich",
                                         "page": "2026-10-30-weekly-manager-update.html", "issues": ["2026-11-01"]}),
    ("weekly-manager-updates", {"date": "2026-11-06", "title": "Weekly Manager Update", "byline": "Megan Leftwich",
                                         "page": WMU_1023_PAGE, "issues": ["2026-11-08"]}),
]
# Main-page Weekly Manager Update card: the seed card to replace (title + a phrase proving it is the old one) and the new date line/teaser
WMU_CARD_OLD = '<div style="font-size:15px;font-weight:bold;color:#333333;">Weekly Manager Update — October 9</div>'
WMU_CARD_OLD_MARK = "Duke Energy Waiver"
WMU_CARD_DATE = "Friday, Nov 6, 2026"
WMU_CARD_TEASER = "The signed laundry lease has been sent over to Laundry Leasing Co. for them to countersign and then get the laundry room set up."

# ---------- Manager reports with a Listen on the title line ----------
MANAGER_LISTEN = [("Shareholders Report — September 30 Board Meeting", BASE + "2026-09-30-shareholders-report.html"),
                 ("Weekly Manager Update", BASE + WMU_1023_PAGE)]

# ---------- Did You Know (1): Tony's Facebook item text (HTML-escaped as printed) ----------
DYK_FB_TEXT = 'Did you know Palm Hill has a private, residents-only Facebook group? Park news, events and photos. Search &quot;Palm Hill Country Club - Residents Only Group&quot; on Facebook and answer all 3 questions.'

# ---------- Did You Know (2): Rules item text (R39) -- main-page framing teaser + archive summary ----------
DYK_RULES_SUMMARY = ("The speed limit in the park is 15 mph. It's okay to go 15 mph and make a full stop at a stop sign. "
    "Golf Carts and all motor vehicles shall not be operated after dark without tail lights and headlights.")  # Steven 6:28 PM: 3 sentences max
DYK_RULES_PV = "https://palmhillnews.vercel.app/pages/previews/2026-10-18/did-you-know-traffic-rules.html"
# R39 (Steven, Oct 17 6:32 PM): teaser mode per item -- "framing" (topic/source description, no author name, no rule quotes) or
# "distilled" (<= 3 verbatim source sentences). Traffic Rules = framing on the main page; the archive row keeps the distilled summary.
DYK_RULES_TEASER_MODE = "framing"
DYK_RULES_TEASER = "A look at traffic rules from the park's official Rules and Regulations."   # Steven's wording, 6:32 PM
DYK_CONTRIBUTOR_NAMES = ["Dave", "David", "Bates", "Board VP"]
DYK_RULES_ARCHIVE_KEY = {"id": "traffic-rules", "title": "Traffic Rules"}   # its archive row (archive-items.json)
DYK_RULES_SOURCE_FILE = "data/dyk-traffic-rules-source.json"   # in the work tree

# ---------- Did You Know (3): this issue's items, teasers (R39/R18c/R66) and archive rows ----------
DYK_ITEMS_JSON = "builder/oct25/data/dyk-link-oct2026-spectrum.json"     # source-verbatim DYK items (stage script output)
DYK_RULES_ITEM_JSON = "builder/oct25/data/dyk-dave-assessments.json"     # the Rules DYK item (shown first, R31)
_PV25 = "https://palmhillnews.vercel.app/pages/previews/2026-10-25/"
# R39 distilled teasers: at most 3 verbatim sentences from each item (ALL CAPS kept, RD9)
_TEASE = {"2026-10-25-spectrum-information": "SPECTRUM SUPPORT PHONE NUMBER: 877-647-7732 is the Community Solutions Line for Bulk Owners Customer Support.",  # R18c cut (Steven Oct 24 12:18 PM)
          "2026-10-25-spectrum-music-channels": "Did you know with our new Spectrum set up we have access to several music channels? Simply turn on your TV then select the Spectrum app."}
DYK_PAGE_PREFIX = "2026-10-25-"   # final page URL = pages/<prefix><preview_page> (Oct 18 pattern)
_DYK_TITLE = {"2026-10-25-spectrum-information": "Spectrum Support Phone Number"}   # Steven Oct 21: short block title (source wording)
_DYK3_TEASER_FULL = ("$100.00 total ($50.00 transfer + $50.00 administrative) is required when a home/unit is transferred; "
                "maintenance fees are due on the first day of the month, delinquent if not received by the tenth.")
_R66_PHRASES = {"2026-10-25-assessments-due": ["home transfer fees", ["monthly maintenance fee due dates", "late fees"]]}  # A, B
DYK_RULES_ITEM_TEASER_APPROVED = "Information on home transfer fees, monthly maintenance fee due dates, and late fees."  # Steven's chosen option 2 (R66)
DYK_ROW_DATE = "2026-10-25"; DYK_ROW_ISSUES = ["2026-10-25"]   # archive rows for these DYK items (R59/R66b)
# R88 (Steven Oct 29 2026 11:11 AM "add the spectrum warning"): new Nov 1 DYK item, top of the section. WORDING PENDING Steven.
# PARKED (Steven Oct 29 2026 7:32 PM, via Mail Scan): Spectrum unplugging item pulled until a proper answer is agreed in the
# palmhillblast thread (no official Spectrum source). Data kept: builder/nov1/data/dyk-spectrum-unplugging.json; full item
# (page, preview, guards) at branch nov1-dyk-spectrum-parked (a2b4659). RESTORE: set DYK_NEW_JSON back to that path, set
# DYK_REPRISE = None, rerun builder/nov1/stage_nov1_content.py + the build (page + archive row are regenerated).
# R88 (Steven Nov 6, 2026): Sunshine Directors box from the November 2026 Link, page 10. The Facebook reprise was Nov 1's
# stand-in (R91). R89 keeps last week's Did You Know off this main page, so Nov 8 shows this issue's new item only.
# The Facebook page and its Oct 18 archive row stay. Spectrum unplugging stays parked.
# R118 (Steven Nov 7, 2026): that item's main-card teaser includes the printed email line. Do not cut it back to the semicolon.
# Nov 15 (Steven Nov 12 2026 2:06 PM): one of Dave Bates's Rules & Regs emails not used before, his exact wording, linked to the
# rule. DRAFT PICK (pending Steven): 'Rule VI' (Nov 9) = Rules and Regulations VI.G, homesite care and maintenance. Main teaser =
# the rule's first sentence, verbatim (R39 distilled). R89 keeps Sunshine Directors (Nov 8) off this main page.
DYK_NEW_JSON = "builder/nov15/data/dyk-dave-rule-vi-homesites.json"
DYK_PARKED_PAGES = ["2026-11-01-did-you-know-spectrum-unplugging.html"]   # must not be linked or archived while parked
DYK_REPRISE = None
# R89 (Steven Oct 29 2026 11:33 AM "Remove last week's dyk items from the main nl page"): Oct 25 items stay in the archive only
DYK_CARRY_PREVIOUS = False
# R66c (Steven Oct 24 3:34 PM): Oct 18 Traffic Rules archive row teaser in R66 style (archive row only)
R66C_SOURCE_JSON = "builder/oct18/data/dyk-traffic-rules-source.json"; R66C_ROW_DATE = "2026-10-18"; R66C_ROW_ID = "traffic-rules"
R66C_PHRASES = ["the speed limit", "stop signs", "lights after dark", "operators under 16", "motorcycles", "golf cart registration"]

# ---------- Community Notices (6): archive rows added by this issue (R59) ----------
NOTICE_ARCHIVE_ROWS = [dict(date="2026-11-15", id="2026-11-15-singing-ensemble-christmas-cantata", title=CANTATA_TITLE,
                     text="Share your singing talents with us as the Palm Hill Christmas Cantata Ensemble begins rehearsing this Sunday!",
                     page=WM_COPY_CANTATA, source="Palm Hill Webmaster notice, Nov 13", issues=["2026-11-15"]),
                dict(date="2026-11-15", id="2026-11-15-palm-hill-annual-golf-cart-parade", title=PARADE_TITLE,
                     text=PARADE_TEASER, page=WM_COPY_PARADE, source="Palm Hill Webmaster notice, Nov 13", issues=["2026-11-15"]),
                dict(date="2026-11-15", id="2026-11-15-christmas-golf-cart-route", title=ROUTE_TITLE,
                     text=ROUTE_TEASER, page=WM_COPY_ROUTE, source="Palm Hill Webmaster notice, Nov 13", issues=["2026-11-15"]),
                dict(date="2026-11-15", id="2026-11-15-amazon-scam-email", title=SCAM_TITLE,
                     text="You may have received an email from Bob Newport today requesting you to purchase an Amazon Gift Card for him. It is a SCAM.",
                     page=WM_COPY_SCAM, source="Palm Hill Webmaster notice, Nov 12", issues=["2026-11-15"]),
                dict(date="2026-11-15", id="2026-11-15-north-irrigation-down", title=IRRIGATION_TITLE,
                     text=IRRIGATION_BODY, page=WM_COPY_IRRIGATION, source="Resource Property Management message, Nov 12", issues=["2026-11-15"]),
                dict(date="2026-11-15", id="2026-11-15-exercise-class", title=EXERCISE_TITLE,
                     text=EXERCISE_BODY, page=WM_COPY_EXERCISE, source="Palm Hill Webmaster notice, Nov 10", issues=["2026-11-15"]),
                dict(date="2026-11-15", id="2026-11-15-taste-of-golf-instructions", title=TOG_INSTR_TITLE,
                     text=TOG_INSTR_BODY, page=WM_COPY_TOG_INSTR, source="Palm Hill Webmaster notice, Nov 10", issues=["2026-11-15"]),
                dict(date="2026-11-15", id="2026-11-15-ladies-christmas-luncheon", title=LADIES_LUNCH_TITLE,
                     text="If you would like to purchase tickets for the 12/2/26 Ladies Christmas Luncheon at The Bayou Club, please contact me ASAP before they are sold out.",
                     page=WM_COPY_LADIES_LUNCH, source="Palm Hill Webmaster notice, Nov 9", issues=["2026-11-15"]),
                dict(date="2026-11-08", id="2026-11-08-chair-yoga-class-canceled", title=CHAIR_YOGA_TITLE,
                     text="The chair yoga class for Monday, November 9, is cancelled.",
                     page=WM_COPY_CHAIR_YOGA, source="Palm Hill Webmaster notice, Nov 7", issues=["2026-11-08"]),
                dict(date="2026-11-08", id="2026-11-08-south-potable-water-shut-off-rescheduled", title=WATER_1111_TITLE,
                     text="South Potable Water Shut off scheduled for Wednesday, November 11th @ 10:00am has been rescheduled",
                     page=WM_COPY_WATER_1111, source="Resource Property Management message, Nov 6", issues=["2026-11-08"]),
                dict(date="2026-10-25", id="2026-10-25-sanitation-field", title="Help with maintaining Sanitation Field", text=SANIT_TEASER,
                     page=WM_COPY_SANIT, source="Palm Hill Webmaster notice, Oct 22", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-couples-golf-league", title="Couples Golf League", text=COUPLES_TEASER,
                     page=WM_COPY_COUPLES, source="Palm Hill Webmaster notice, Oct 20", issues=["2026-10-25"]),
                # Steven Oct 23 6:38 PM
                dict(date="2026-10-25", id="2026-10-25-library-closed", title="Library Closed starting the week of October 26th", text=LIBRARY_TEASER,
                     page=WM_COPY_LIBRARY, source="Palm Hill Webmaster notice, Oct 22", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-stop-sign-rules", title="Please observe important stop sign rules", text=STOP_TEASER,
                     page=WM_COPY_STOP, source="Palm Hill Webmaster notice, Oct 21", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-south-rec-club-seeking-officers", title="2027 South Rec Club Seeking Officers", text=SOUTHREC_TEASER,
                     page=WM_COPY_SOUTHREC, source="Palm Hill Webmaster notice, Oct 21", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-holiday-greeting-distribution-plan", title=HOLIDAY_TITLE, text=HOLIDAY_TEASER,
                     page=HOLIDAY_PAGE, source="Flyer from Bill Bender, Oct 23", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-north-clubhouse-ice-machine-moved", title=ICE_TITLE, text=ICE_TEASER,
                     page=ICE_PAGE, source="Oct P&E Committee Report (Elaine Cole); details confirmed by Steven Leonowicz", issues=["2026-10-25"])]

# CARRIED FROM OCT 25 (Steven to review): the footer row checks below are the Oct 25 values, unchanged.
# ---------- footer row checks (R62 / R62b / R60b / R60c / L08 / L14) ----------
MEETING_ROW_CHECKS = [   # R62/R62b: a meetings row must show (need) and must not show (never) these, text before its Source line
    # Nov 15: Finance keeps its calendar date, time and place (R86/R87) and gains Agenda and Zoom pages from the Nov 8 Webmaster notice (R4)
    dict(rule="R4", start=">Finance Committee<", span=1500,
         need=["Monday, Nov 16, 2026", "10:00 AM", "South Clubhouse Boardroom", "Agenda", "Zoom"], never=["to be confirmed", "Nov 18"]),
    # Calendar pull cal-20261112-1346: Board of Directors Wed Nov 18 and Wed Nov 25 are RESCHEDULED; Fri Nov 20 1:00 PM is CONFIRMED
    dict(rule="R87", start=">Board of Directors Meeting<", span=1200,
         need=["Friday, Nov 20, 2026", "1:00 PM"], never=["Nov 18", "Nov 25"]),
    # R122: club calendar (Fri Dec 4, 9:00 AM) supersedes the RPM Oct 27 copy (Mon Dec 14, 10:00 AM)
    dict(rule="R122", start=">Communications Committee Meeting<", span=1200,
         need=["Friday, Dec 4, 2026", "9:00 AM"], never=["Dec 14"]),
]
HOLIDAY_SOURCE_LABEL = "Bill Bender email"            # R60b linked Source wording
ICE_SOURCE_LABEL = "Oct P&E Committee Report"         # R60c linked Source wording
# R92 (Steven Oct 30 2026 11:40 AM): Events - Next Week (Nov 8-14) directly under This Week; label derived from ISSUE (L08).
NEXT_WEEK_SECTION = True
UPCOMING_LABEL_EXPECTED = None   # unused with NEXT_WEEK_SECTION (was stale Oct 25 carry-over "November 1 through November 22")
CHAIR_DATES_EXPECTED = []   # Nov 15: no report inside 30 days (R104b placeholder)
CHAIR_DATES_LABEL = "chair section shows No reports this week. (no report inside 30 days)"
RECURRING_CHECK_LABEL = "Recurring: Oct 25 window, By Date/Name/Location pages"

# R100 (Steven Oct 31 2026 6:07 PM "Drop community notice"): Tony's Facebook group notice off the main page; Did You Know item kept.
TONY_FB_NOTICE = False
# R99 (Steven Oct 31 2026, "Put it in its own banner, and add some tasteful clock icons"): DST banner, wording verbatim.
# R102 (Steven Oct 31 2026 7:33 PM, voice): flyer phone numbers Steven OKs are printed verbatim and must be tap-to-call
# in the NL row (preview + SEND) and on the copy page. (label, number as printed, page file)
REQUIRED_TEL = [("Cornhole Tournament", "518-866-2079", WM_COPY_CORNHOLE),
                 ("Christmas Golf Cart Route", "(727) 554-6799", WM_COPY_ROUTE)]  # Steven Nov 13 8:54 PM ET
_NOV1_TOP_BANNER = dict(heading="\u23f0 Did you set your clocks back one hour?",
                  body="Daylight Saving Time ended at 2 a.m. on Sunday, November 1. Enjoy the extra hour!")
# R101 (Steven Oct 31 2026 7:34 PM, voice: "don't forget to vote on Tuesday" / "you can vote here in the park"): second small
# banner under the DST one; his wording, light polish. The in-park location is Steven's word (not from a source). No hours/links.
VOTE_BANNER = dict(heading="\u2605 Don't forget to vote on Tuesday, November 3!"  # R101f (Steven Nov 1 12:32 AM)
                  , body="")  # R101e (Steven Oct 31 10:18 PM): body line removed
TOP_BANNERS = []   # Nov 8: DST (Nov 1) and vote (Nov 3) banners are past

# R103 (Steven Oct 31 2026, via Susan's proof note): the Webmaster December Link Deadline notice is the first Community Notice
FIRST_NOTICE = None   # Nov 8: December Link Deadline (Nov 5) dropped as stale

# R104 (Steven Nov 1 2026 11:55 AM: "if there are no current items in a section, we won't even show the section header"):
# sections (by key: president, story, chair, manager, dyk, ...) with no current item are left out entirely (header and all). Archive pages and URLs stay live.
HIDE_SECTIONS = {"president": "Henry Klain's October message ran Oct 25 and Nov 1; no new message (Steven Nov 1 11:55 AM)",
                 # R120 (Steven Nov 7 2026): no newer monthly report, so the September 30 card leaves this main page.
                 # The report page and the Shareholders Report archive stay.
                 "shareholders": "September 30 monthly report; no newer monthly report (Steven Nov 7 2026)",
                 # Steven Nov 12 2026 (voice): Carolyn's Board piece moved to Community Notices; the Stories section is omitted (R45).
                 "story": "Steven Nov 12 2026 (voice): move Carolyn Story's Board piece from Community Stories into Community Notices"}
