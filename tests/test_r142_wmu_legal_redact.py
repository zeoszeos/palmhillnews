"""R142: cut legal/safety phrases must not appear in Nov 13 weekly manager update outputs."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

CLEAN = (
    "<p>Hello Everyone,</p>"
    "<p>It was a bit of a crazy week with the Microsoft Outage affecting our email for most of the day on Thursday.</p>"
    "<li>The quote to re-strap the chairs and lounge chairs for the pool areas was approved by Henry.</li>"
    "<li>Brightview sent their monthly site assessment, which is attached.</li>"
    "<li>The attachment for the tractor arrived today.</li>"
    "<li>Picture attached.</li>"
)

def test_clean_page_passes():
    assert sr.wmu_legal_redact_problems(CLEAN, "page") == []

def test_shooting_sentence_fails():
    bad = CLEAN + "<p>an Association manager was shot and killed in DC yesterday</p>"
    hits = sr.wmu_legal_redact_problems(bad, "page")
    assert any("shot and killed" in h for h in hits)

def test_assault_bullet_fails():
    bad = CLEAN + "<li>The Assault and Battery Policy came back with the same premium.</li>"
    hits = sr.wmu_legal_redact_problems(bad, "page")
    assert any("Assault and Battery" in h for h in hits)

def test_cai_mention_fails_and_mosaic_does_not():
    hits = sr.wmu_legal_redact_problems("I've attached the email from CAI's CEO.", "page")
    assert any("CAI" in h for h in hits)
    assert sr.wmu_legal_redact_problems("MOSAIC meeting", "page") == []
