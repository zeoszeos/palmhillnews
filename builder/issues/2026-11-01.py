"""PHNEWS Sunday, November 1, 2026 (Vol. 1, No. 16) -- issue content file (STYLE-RULES R71). Data only; all logic is in builder/core/.
Workspace set up Oct 24 2026; Steven confirms content Friday. New week = copy the idea of this file, never a builder."""
ISSUE = "2026-11-01"
VOL_NO = 16
SHORT = "nov1"
DEFAULT_REPO = "/workspace/nov1-build"
DEFAULT_WORK = "/workspace/phnews-consolidation/nov1"
# Community Story (R45/R83, Steven Oct 26 2026 12:19 PM): Katra Peck, Palm Hill Link February 2026 pp 4-5, full length, credit line
# "First published in the Palm Hill Link, February 2026". Pages written by builder/nov1/stage_nov1_content.py.
STORY = dict(json="builder/nov1/data/community-story-katra-peck.json", listen="2026-02-listen-katra-peck-story.html", teaser_sentences=1)
STORY_OMIT_DRYRUN_NOTE = None         # Nov 1 has a story (Katra Peck); never omitted
# Carry policy (set up Oct 24 2026 8:3x PM; Steven confirms Friday): keep notices still valid on/after Nov 1, drop Oct 25 one-offs.
NOTICES_DROPPED = ["Library Closed starting the week of October 26th",   # closure ends Sun Nov 1
                   "Info from Linda",                                     # Halloween Dance Oct 31 / market Oct 24: past
                   "North Clubhouse Ice Machine Moved",                   # Oct 25 news item (R60c was Oct 25-only)
                   "Help with maintaining Sanitation Field", "Please observe important stop sign rules"]  # ran Oct 25; drop confirmed by Steven Oct 26 2026 11:22 AM
R60C_ICE_NOTICE = False               # the ice machine notice is dropped for Nov 1
DRYRUN_OK = True                      # PHNEWS_DRYRUN=1 lists content guards as TODOs (workspace only)
LOCKED = {  # TO REVIEW when Nov 1 content approved -- today's values, carried from Oct 25 (L11 FAIL expected until then)
    "NOTICES_EXPECTED": [
        'Join the Palm Hill Residents Group on Facebook',
        'A convenient way to send holiday cards for Palm Hill residents',
        'North Clubhouse Ice Machine Moved',
        'Library Closed starting the week of October 26th',
        'Help with maintaining Sanitation Field',
        'Please observe important stop sign rules',
        '2027 South Rec Club Seeking Officers',
        'Couples Golf League',
        'Swimming Pool Food and Beverage Rules',
        'November Coffee and Pancake Volunteers',
        'Shuffleboard Season Reminders',
        'Taste of Golf — November 18',
        'Info from Linda',
    ],
    "CHAIR_EXPECTED": {
        'Planning and Environmental Committee': 'Motion to the Board: pay $857.33 to WindowFilm LLC, to provide privacy coverings for wellness classes.',
        'Golf Advisory Committee': 'The amended Code of Conduct was unanimously approved by the Board of Directors on September 26, 2026.',
        'Communications Committee': 'Facebook: Henry Klain approved the two-month trial on October 9.',
    },
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
                   "Taste of Golf": BASE + "2026-10-14-taste-of-golf-notice.html"}
EVENT_LINK = {"Halloween Dance Party": ("More →", BASE + "2026-10-31-halloween-dance.html"),
              "Mount Dora Trip": ("More →", BASE + "2026-10-24-mount-dora-trip.html"),
              "MESCO Spaghetti Dinner Fundraiser": ("More →", BASE + "2026-11-14-mesco-spaghetti-dinner-fundraiser.html"),
              "Thanksgiving Dinner": ("More →", BASE + "2026-11-26-thanksgiving-dinner.html"),
              "Bocce Party": ("More →", BASE + "2026-10-28-bocce-party.html"),
              "Taste of Golf": ("More →", BASE + "2026-10-14-taste-of-golf-notice.html")}      # existing Webmaster copy page (gotwicz 1a13d9d5ef6e178f)
# R21: full calendar listing text for the More → page. Personal phone numbers are not printed, EXCEPT on event pages Steven
# has explicitly OK'd (PHONE_OK_PAGES; Bocce Party approved Oct 16 11:37 PM). Issue summaries never carry them.
PHONE_OK_PAGES = {"Bocce Party"}
EVENT_PAGE = {"Bocce Party": ("2026-10-28-bocce-party.html",
    ["Sign up at either clubhouse or by calling Pat Foor (727-631-3372) or Joe Cothran (727-512-1185). Join us for the fellowship and fun!",  # PHONE_OK_PAGES
     "Rescheduled from 4:00 PM to 6:00 PM (6:00 to 7:00 PM)."]),
    # R21 calendar re-pull Sat Oct 17 1:47 PM: start moved 4:00 PM -> 5:00 PM; the More → page date line now comes from the calendar
    "MESCO Spaghetti Dinner Fundraiser": ("2026-11-14-mesco-spaghetti-dinner-fundraiser.html",
    ["Doors open at 4:30 PM; dinner is served at 5:00 PM. The $12 donation covers bread and butter, salad, spaghetti and meatballs, dessert and coffee; BYOB for other drinks. Tickets are sold at both coffees until Monday morning, Nov 9; none at the door."]),
    # R21/R82 (Steven Oct 26 2026 11:49 AM): calendar listing text (booking 112626-1200-SMH), names exactly as the calendar gives them
    "Thanksgiving Dinner": ("2026-11-26-thanksgiving-dinner.html",
    ["Dinner served at 2:00 PM. Mickey Bontrager, Elroy Bontrager, Kate and Jeff Wesolowski."])}

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
MTG_EXTRA = [dict(  # Oct 25: Finance Oct 22 (agenda email) is past -> dropped; no newer Finance agenda in palmhillblast as of Oct 20 2:4x PM
             date="2026-11-18", start="13:00", name="Board of Directors Meeting", venue="Board Room South", note="(date to be confirmed)")]
MTG_NOTE = {("2026-11-10", "Buildings and Grounds Committee Meeting"): "(date to be confirmed)",
            }
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
SOUTHREC_IMG = "https://www.palmhillcountryclub.net/editor_upload/Image/South_Recreation_Club_Election_Smaller.jpeg"
WM_COPIES = [
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
    ("Taste of Golf — November 18",
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
# Steven Oct 20 3:03 PM: drop stale carried-over notices (Linda's Oct 24 market email, Oct 27 mowing date, Taste of Golf notice --
# Taste of Golf stays as an event row). Guard: none of these titles may appear in Community Notices.
NOTICES_DROPPED_OCT25 = {"October Mowing Date", "Property Fraud Alert"}  # Steven Oct 21 8:43 PM: Property Fraud Alert dropped (its Vercel page stays live)  # Steven Oct 21 11:20 AM: Info from Linda + Taste of Golf notice restored (R56 event cards link them)

# ---------- Community Notices (5): Listen overrides ----------
NOTICE_LISTEN_OVERRIDE = {ICE_TITLE: BASE + ICE_PAGE}  # R60c: Listen reads the notice's own page (Source is the P&E report)

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
STORY_DATE_LABEL = "Feb 2026"   # archive "date_label" for this issue's story row (used only when STORY is set)

# ---------- Weekly Manager Update (page items, PDF attachment, main-page card) ----------
# Weekly Manager Update Oct 23 (Megan Leftwich, "Fw: Weekly Update 2026.10.23", palmhillblast Fri Oct 23 4:07 PM ET; her
# original went to the Board at 4:03 PM) replaces Oct 16 (retention rule). The page is built here from the Oct 16 page's
# card template with Megan's wording item by item (never hand-edited); decorative emoji in the insurance scenarios dropped.
WMU_1023_PAGE = "2026-10-23-weekly-manager-update.html"
WMU_1023 = [
    "We had a complaint regarding the temperature of the water in the north pool. Staff have checked over the heaters, and they are working properly and maintaining the correct temperatures. We will not be changing the temperature, as it has been established and is maintained year-round.",
    "At the Finance committee meeting, I confirmed the placement of the requested CDs. You now have 4 in your reserve account and 3 in your savings. All are $100,000 and have staggered due dates.",
    "The City of Largo picked up the trash compactor to empty on Friday, and their truck broke down with the unit on it. They dropped off an open-top container temporarily but were able to get the compactor back to us just now.",
    "The election equipment will be dropped off on Thursday morning next week, with the election on Tuesday the following week.",
    "Toni has begun preparing the First Notice for the annual meeting. It is scheduled to go out on or before November 20th.",
    "We received the second grease trap permit from the City of Largo this week. They are posted in the south clubhouse.",
    "We had a motorcycle in the community on Needle today. I spoke to them, and we sent them a letter regarding it.",
    ("David had asked if the insurance coverage was necessary and Lauren responded with the following:", [
        "The coverage is not mandatory, but a recommendation considering the prior policy included the coverage.",
        "Below are examples of claim scenarios that would preclude coverage without implementing such a policy:",
        "<strong>Scenario 1 – Neighbor Dispute Turns Physical</strong><br>Two residents get into a heated argument over a parking space in a common lot. The dispute escalates and one resident strikes the other. The injured party sues the park, alleging negligent security and failure to address prior complaints about the aggressive neighbor.",
        "<strong>Scenario 2 – Pool / Common Area Altercation</strong><br>A fight breaks out between teenagers at the community pool. A bystander resident is injured trying to break it up. The park is named in the lawsuit for failing to provide adequate supervision or security.",
        "<strong>Scenario 3 – On-Site Manager Involvement</strong><br>A park manager physically confronts a resident who is violating community rules. The resident alleges excessive force and files a claim against both the manager and the park ownership entity."]),
    "Lynntina with Duke confirmed receipt of the payment for the transformer. She has requested the signed waiver before they will schedule the work.",
    "Manhole inspections were conducted today. I have reached out to them to confirm they have completed them. We will submit the required paperwork by the November 6th deadline.",
    "Attached is a paper from RPM regarding minutes and some guidelines as to what to include. Please let me know if you have any questions, and I will share them with the committees.",
]
WMU_TEMPLATE = "2026-10-16-weekly-manager-update.html"   # previous update page = card template
WMU_GREETING = "Good Afternoon Everyone,"
WMU_TEMPLATE_DATE = "2026-10-16"                         # must not survive in the new page (above the Listen block)
WMU_REPLACE = [("October 16, 2026", "October 23, 2026"), ("Oct 16, 2026", "Oct 23, 2026"),
               ("2026-10-16-weekly-manager-update", "2026-10-23-weekly-manager-update"), ("2026.10.16", "2026.10.23")]
# STYLE-RULES R65 (Steven-approved Oct 24 2:26 PM): Megan's attached RPM paper ("Recording Minutes at Meetings", 2 pages, from her
# "Weekly Update 2026.10.23" email) is hosted as a PDF and linked in an Attachments card on her Oct 23 page (Oct 9 page layout).
# Applied by the builder to the existing page (idempotent); a copy, the source PDF is never moved.
WMU_1023_PDF_SRC = "source/megan-1023/minutes-M100.pdf"   # R72: source PDF, relative to PHNEWS_WORK (copied, never moved)
WMU_1023_PDF = "assets/manager/2026-10-23-rpm-recording-minutes-at-meetings.pdf"
WMU_1023_PDF_TITLE = "Recording Minutes at Meetings"
WMU_1023_PDF_DESC = "Paper from RPM on what to include in minutes · PDF, 2 pages"
ARCHIVE_ROWS_LATE = [   # archive rows added after the weekly update page is built (R59)
    ("weekly-manager-updates", {"date": "2026-10-23", "title": "Weekly Manager Update", "byline": "Megan Leftwich",
                                         "page": WMU_1023_PAGE, "issues": ["2026-10-25"]}),
]
# Main-page Weekly Manager Update card: the seed card to replace (title + a phrase proving it is the old one) and the new date line/teaser
WMU_CARD_OLD = '<div style="font-size:15px;font-weight:bold;color:#333333;">Weekly Manager Update — October 9</div>'
WMU_CARD_OLD_MARK = "Duke Energy Waiver"
WMU_CARD_DATE = "Friday, Oct 23, 2026"
WMU_CARD_TEASER = "The election equipment will be dropped off on Thursday morning next week, with the election on Tuesday the following week."

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
DYK_NEW_JSON = "builder/nov1/data/dyk-spectrum-unplugging.json"
# R66c (Steven Oct 24 3:34 PM): Oct 18 Traffic Rules archive row teaser in R66 style (archive row only)
R66C_SOURCE_JSON = "builder/oct18/data/dyk-traffic-rules-source.json"; R66C_ROW_DATE = "2026-10-18"; R66C_ROW_ID = "traffic-rules"
R66C_PHRASES = ["the speed limit", "stop signs", "lights after dark", "operators under 16", "motorcycles", "golf cart registration"]

# ---------- Community Notices (6): archive rows added by this issue (R59) ----------
NOTICE_ARCHIVE_ROWS = [dict(date="2026-10-25", id="2026-10-25-sanitation-field", title="Help with maintaining Sanitation Field", text=SANIT_TEASER,
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
    dict(rule="R87", start=">Finance Committee<", span=1200,   # R86/R87 (Oct 27): calendar date, Mon Nov 16 (agenda said Nov 18)
         need=["Monday, Nov 16, 2026", "10:00 AM", "South Clubhouse Boardroom"], never=["to be confirmed", "Nov 18"]),
    dict(rule="R87", start="Planning and Environmental Committee Meeting", span=1500,
         need=["Tuesday, Nov 10, 2026", "12:30 PM"], never=["to be confirmed"]),
]
HOLIDAY_SOURCE_LABEL = "Bill Bender email"            # R60b linked Source wording
ICE_SOURCE_LABEL = "Oct P&E Committee Report"         # R60c linked Source wording
UPCOMING_LABEL_EXPECTED = "November 1 through November 22"   # L08 Upcoming header label
CHAIR_DATES_EXPECTED = ["Wednesday, Oct 14, 2026", "Tuesday, Oct 13, 2026", "Monday, Oct 12, 2026"]   # L14 chair report dates
CHAIR_DATES_LABEL = "chair dates P&E Oct 14, Golf Oct 13, Communications Oct 12 (3-letter months)"
RECURRING_CHECK_LABEL = "Recurring: Oct 25 window, By Date/Name/Location pages"
