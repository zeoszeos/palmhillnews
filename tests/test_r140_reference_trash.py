"""R140: Reference Guide trash/recycling entry is the minimal Starting December 1st list."""
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
    assert any("Starting December 1st" in h for h in hits)
    fixed = sr.apply_reference_trash(html)
    assert sr.reference_trash_problems(fixed) == []
    assert sr.apply_reference_trash(fixed) == fixed
    assert "North Area:" not in fixed
    assert "Fed Up Trash Valet" not in fixed
    assert "Effective December 1, 2026" not in fixed
    assert "Starting December 1st: Trash Mondays and Thursdays, entire community" in fixed
    assert "Recycling Wednesdays, entire community (clear bags required)" in fixed
    assert "Bags out by 8:00 a.m. on collection days" in fixed
    assert "•" in fixed
    assert "â€¢" not in fixed
    assert "Debris/brush" in fixed and "Sanitation:" in fixed

def test_long_form_valet_prose_in_reference_fails():
    html = (
        'Trash, Recycling &amp; Sanitation</div>'
        '<div>• Effective December 1, 2026, Palm Hill will begin a new valet trash and recycling service with Fed Up Trash Valet LLC. The first collection will be the recycling on December 2nd.</div>'
        '<div>• Debris/brush: call (727) 581-8729</div>'
        '<div>• Sanitation: Mon–Fri 9:00 AM – 3:00 PM / Sat 9:00 AM – 12:00 PM / Sun Closed</div>'
        '</td>'
    )
    hits = sr.reference_trash_problems(html)
    assert any("Fed Up Trash Valet" in h or "Effective December 1, 2026" in h for h in hits)
    fixed = sr.apply_reference_trash(html)
    assert sr.reference_trash_problems(fixed) == []
    assert "Fed Up Trash Valet" not in fixed
