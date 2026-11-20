"""R135: Reference Guide trash/recycling lines match the Fed Up Trash Valet source."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

def test_old_schedule_fails_and_apply_fixes_it():
    html = (
        'Trash, Recycling &amp; Sanitation</div>'
        '<div>• North Area:   Mon (trash) / Thu (recycling)</div>'
        '<div>• Palm Forest: Tue (trash) / Fri (recycling)</div>'
        '<div>• South Area:  Tue (trash) / Fri (recycling)</div>'
        '<div>• Debris/brush: call (727) 581-8729</div>'
        '<div>• Sanitation: Mon–Fri 9:00 AM – 3:00 PM / Sat 9:00 AM – 12:00 PM / Sun Closed</div>'
        '</td>'
    )
    hits = sr.reference_trash_problems(html)
    assert any("North Area:" in h for h in hits)
    assert any("missing source wording" in h for h in hits)
    fixed = sr.apply_reference_trash(html)
    assert sr.reference_trash_problems(fixed) == []
    assert sr.apply_reference_trash(fixed) == fixed
    assert "North Area:" not in fixed
    assert "Fed Up Trash Valet LLC" in fixed
    assert "Clear bags are still required for recycling." in fixed
    assert "•" in fixed
    assert "â€¢" not in fixed
    assert "Debris/brush" in fixed and "Sanitation:" in fixed
