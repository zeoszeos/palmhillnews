#!/usr/bin/env python3
"""R129: the 50%+50%+1% masthead widths are rewritten; the guard fails if they return."""
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

def test_bad_layout_is_caught():
    hits = sr.masthead_seam_problems(BAD)
    assert hits, "the original 50%+50%+1% masthead must fail"

def test_fixer_removes_the_seams():
    fixed = sr.fix_masthead_seams(BAD)
    assert sr.masthead_seam_problems(fixed) == []
    assert 'width="50%"' not in fixed
    assert "width:50%" not in fixed
    assert "width:1%" not in fixed
    assert f"width:{sr.MASTHEAD_PALM_PX}px" in fixed
    assert f"width:{sr.MASTHEAD_PALM_MOBILE_PX}px !important" in fixed
    assert "Palm Hill Country Club" in fixed
    assert "transform:scaleX(-1)" in fixed
    # Idempotent.
    assert sr.fix_masthead_seams(fixed) == fixed

def test_pages_without_a_masthead_are_skipped():
    html = "<html><body><p>No banner here</p></body></html>"
    assert sr.fix_masthead_seams(html) == html
    assert sr.masthead_seam_problems(html) == []
