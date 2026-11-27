"""R145: a Steven-picked single photo from a cover collage goes on the main-page story card."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import style_rules as sr

SRC = "https://palmhillnews.vercel.app/assets/images/phnews/2026-11/smiling-ladies-luncheon-main-november-2026.jpg"
COVER = "https://palmhillnews.vercel.app/assets/images/phnews/2026-11/smiling-ladies-luncheon-cover-november-2026.jpg"
REC = dict(
    src=SRC, w=297, h=261, alt="Ladies at lunch",
    tile="middle-center",
    by="Steven Leonowicz, Nov 23 2026, t1864u",
)
CARD = f'<div>Community Stories</div><img src="{SRC}" width="297" height="261" alt="Ladies at lunch"><div>More</div>Residents Reference Guide'
STORY_PAGE = f'<main><figure><img src="{COVER}" width="927" height="743" alt="cover"></figure><article><p>body</p></article></main>'


def test_recorded_photo_on_card_passes():
    assert sr.story_main_photo_problems(CARD, REC, story_page_html=STORY_PAGE, cover_src=COVER, label="preview") == []


def test_missing_photo_fails():
    html = '<div>Community Stories</div><div>Volunteering for the first time</div>Residents Reference Guide'
    hits = sr.story_main_photo_problems(html, REC, story_page_html=STORY_PAGE, cover_src=COVER, label="SEND")
    assert hits and "missing from the Community Stories card" in hits[0]


def test_incomplete_record_fails():
    hits = sr.story_main_photo_problems(CARD, dict(src=SRC), label="preview")
    assert hits and "must record" in hits[0]


def test_full_collage_on_card_fails():
    html = f'<div>Community Stories</div><img src="{COVER}" alt="cover"><div>More</div>Residents Reference Guide'
    hits = sr.story_main_photo_problems(html, REC, story_page_html=STORY_PAGE, cover_src=COVER, label="preview")
    assert hits and any("full cover collage" in h for h in hits)


def test_story_page_must_keep_cover():
    hits = sr.story_main_photo_problems(CARD, REC, story_page_html="<main><article><p>no photo</p></article></main>", cover_src=COVER)
    assert hits and any("full cover collage at the top" in h for h in hits)


def test_no_record_is_ok():
    assert sr.story_main_photo_problems(CARD, None) == []
    assert sr.story_main_photo_problems(CARD, {}) == []
