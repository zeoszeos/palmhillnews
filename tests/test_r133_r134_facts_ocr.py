"""R133 / R133b / R133c / R134 (Steven Nov 15 2026): Palm Hill ZIP/office phone, no handwritten map labels, source typo fixes,
OCR of handwritten content approved by Steven."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import style_rules as sr

BAD = "<p>START. END. Palm Hill Country Club, 1800 Seminole Boulevard, Largo, Florida 33770. Office: (727) 554-6799.</p>"
GOOD = "<p>Palm Hill Country Club, 1800 Seminole Boulevard, Largo, Florida 33778. Office: (727) 581-8729.</p>"


def test_r133_bad_and_good():
    p = sr.palm_hill_facts_problems(BAD)
    assert any("33770" in x for x in p) and any("554-6799" in x for x in p) and any(x.startswith("R133b") for x in p)
    assert sr.palm_hill_facts_problems(GOOD) == []


def test_r133_after_hours_and_reference_numbers_allowed():
    assert sr.palm_hill_facts_problems("<p>After Hours: (727) 269-8236. Office: (727) 269-8236</p>") == []
    assert sr.palm_hill_facts_problems("<p>Office: (727) 447-1952</p>", {"447-1952"}) == []
    assert sr.palm_hill_facts_problems("<p>Office: (727) 447-1952</p>")


def test_r133c_typo():
    assert sr.source_typo_problems("<p>in the Noeth Clubhouse</p>", [("Noeth", "North", "Steven")])
    assert sr.source_typo_problems("<p>in the North Clubhouse</p>", [("Noeth", "North", "Steven")]) == []


def test_r134_ocr_items():
    wm = [("route.html", "Route", "x", [("img", ("u", "a")), ("p", "text")], dict(title="Route"))]
    assert sr.ocr_items_problems(wm, [], ["Route"])  # unmarked
    item = dict(title="Route", page="route.html", ocr_source=True, handwritten=True, ocr_approved_by_steven=False)
    p = sr.ocr_items_problems(wm, [item], ["Route"])
    assert p and sr.OCR_FLAG_TEXT in p[0]
    item["ocr_approved_by_steven"] = True
    assert sr.ocr_items_problems(wm, [item], ["Route"]) == []
    assert sr.ocr_items_problems(wm, [dict(item, handwritten=False, ocr_approved_by_steven=None)], ["Route"]) == []
