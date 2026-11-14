#!/usr/bin/env python3
"""R129: keep original 50%/1%/50% palm centering; paint gaps green with border-spacing:0."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

BAD = '''<style>
@media (max-width:700px) {
  .header-palm-cell { width:50% !important; }
  .header-title { font-size:20px !important; line-height:25px !important; }
}
</style>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;background:#2D5016;"><tr>
      <td class="header-palm-cell" width="50%" align="center" valign="middle" bgcolor="#2D5016" style="width:50%;height:105px;background:#2D5016;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;"></td>
      <td width="1%" align="center" valign="middle" bgcolor="#2D5016" style="width:1%;white-space:nowrap;height:105px;background:#2D5016;color:#ffffff;text-align:center;"><span class="header-title" style="font:700 29px/34px Arial,sans-serif;color:#ffffff;white-space:nowrap;">Palm Hill Country Club</span><br><span style="font:700 15px/22px Arial,sans-serif;color:#e5f1d1;">Sunday, November 15, 2026</span></td>
      <td class="header-palm-cell" width="50%" align="center" valign="middle" bgcolor="#2D5016" style="width:50%;height:105px;background:#2D5016;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;transform:scaleX(-1);"></td>
    </tr></table>'''

# The rejected first fix: fixed 100px / 60px palm cells (palms moved to the edges).
OLDFIX = '''<style>
@media (max-width:700px) {
  .header-palm-cell { width:60px !important; }
  .header-title { font-size:20px !important; line-height:25px !important; }
}
</style>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;border-spacing:0;background:#2D5016;"><tr>
      <td class="header-palm-cell" width="100" align="center" valign="middle" bgcolor="#2D5016" style="width:100px;height:105px;background:#2D5016;padding:0;border:0;font-size:0;line-height:0;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;"></td>
      <td align="center" valign="middle" bgcolor="#2D5016" style="white-space:nowrap;height:105px;background:#2D5016;color:#ffffff;text-align:center;padding:0 8px;"><span class="header-title" style="font:700 29px/34px Arial,sans-serif;color:#ffffff;white-space:nowrap;">Palm Hill Country Club</span><br><span style="font:700 15px/22px Arial,sans-serif;color:#e5f1d1;">Sunday, November 15, 2026</span></td>
      <td class="header-palm-cell" width="100" align="center" valign="middle" bgcolor="#2D5016" style="width:100px;height:105px;background:#2D5016;padding:0;border:0;font-size:0;line-height:0;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;transform:scaleX(-1);"></td>
    </tr></table>'''

# Short-lived attempt that dropped the 1% title width (also shifted the palms).
DROPPED_1PCT = '''<style>
@media (max-width:700px) {
  .header-palm-cell { width:50% !important; }
  .header-title { font-size:20px !important; line-height:25px !important; }
}
</style>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;border-spacing:0;background:#2D5016;"><tr>
      <td class="header-palm-cell" width="50%" align="center" valign="middle" bgcolor="#2D5016" style="width:50%;height:105px;background:#2D5016;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;"></td>
      <td align="center" valign="middle" bgcolor="#2D5016" style="white-space:nowrap;height:105px;background:#2D5016;color:#ffffff;text-align:center;"><span class="header-title" style="font:700 29px/34px Arial,sans-serif;color:#ffffff;white-space:nowrap;">Palm Hill Country Club</span><br><span style="font:700 15px/22px Arial,sans-serif;color:#e5f1d1;">Sunday, November 15, 2026</span></td>
      <td class="header-palm-cell" width="50%" align="center" valign="middle" bgcolor="#2D5016" style="width:50%;height:105px;background:#2D5016;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;transform:scaleX(-1);"></td>
    </tr></table>'''


def _masthead_ok(fixed):
    assert sr.masthead_seam_problems(fixed) == []
    assert fixed.count('width="50%"') == 2
    assert "width:50% !important" in fixed
    assert "width:50%;height:105px" in fixed
    assert 'width="1%"' in fixed
    assert "width:1%" in fixed
    assert "border-spacing:0" in fixed
    assert "background:#2D5016" in fixed
    assert "width:100px" not in fixed
    assert 'width="100"' not in fixed
    assert "width:60px" not in fixed
    assert "padding:0 8px" not in fixed
    assert "Palm Hill Country Club" in fixed
    assert "transform:scaleX(-1)" in fixed
    assert sr.fix_masthead_seams(fixed) == fixed


def test_original_without_border_spacing_is_caught():
    hits = sr.masthead_seam_problems(BAD)
    assert hits, "the original masthead must fail until border-spacing:0 is added"
    assert any("border-spacing" in h for h in hits)


def test_rejected_100px_placement_is_caught():
    hits = sr.masthead_seam_problems(OLDFIX)
    assert hits, "the rejected 100px palm placement must fail"
    assert any("100px" in h or "60px" in h for h in hits)


def test_dropped_title_width_is_caught():
    hits = sr.masthead_seam_problems(DROPPED_1PCT)
    assert hits, "dropping the 1% title width must fail (it shifts the palms)"
    assert any("1%" in h for h in hits)


def test_fixer_keeps_original_palm_placement_and_paints_gaps_green():
    fixed = sr.fix_masthead_seams(BAD)
    _masthead_ok(fixed)
    # The only structural change to the original is border-spacing:0.
    assert BAD.replace(
        'style="width:100%;border-collapse:collapse;background:#2D5016;"',
        'style="width:100%;border-collapse:collapse;border-spacing:0;background:#2D5016;"',
        1,
    ) == fixed


def test_fixer_restores_original_placement_from_100px_version():
    _masthead_ok(sr.fix_masthead_seams(OLDFIX))


def test_fixer_restores_title_width_from_dropped_1pct_version():
    _masthead_ok(sr.fix_masthead_seams(DROPPED_1PCT))


def test_pages_without_a_masthead_are_skipped():
    html = "<html><body><p>No banner here</p></body></html>"
    assert sr.fix_masthead_seams(html) == html
    assert sr.masthead_seam_problems(html) == []
