#!/usr/bin/env python3
"""R131: small 48px Listen icon; R132: only the wrapping masthead cell paints the green (Gmail iOS)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

OLD_ICON = "https://palmhillnews.vercel.app/assets/images/phnews/2026-10-04/speaker-read-aloud-green-gold-512-v3.png"


def _listen(src):
    return (f'<a href="x.html?listen=1" style="color:#3A6B1A;"><img src="{src}" width="24" height="24" alt="" '
            'style="display:inline-block;width:24px;height:24px;vertical-align:middle;border:0;margin:-3px 4px -3px 0;">Listen</a>')


def test_old_512_icon_is_caught():
    hits = sr.listen_icon_problems(_listen(OLD_ICON) * 3, ROOT)
    assert hits and "48px" in hits[0]


def test_new_icon_passes_and_file_is_small():
    assert sr.listen_icon_problems(_listen(sr.LISTEN_ICON_URL) * 11, ROOT) == []
    f = ROOT / sr.LISTEN_ICON_REL
    assert f.exists() and f.stat().st_size <= sr.LISTEN_ICON_MAX_BYTES


def test_missing_icon_file_is_caught():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        hits = sr.listen_icon_problems(_listen(sr.LISTEN_ICON_URL), d)
    assert any("missing" in h for h in hits)


def test_no_listen_icons_is_fine():
    assert sr.listen_icon_problems("<p>no icons</p>", ROOT) == []


WRAP = '<td bgcolor="#2D5016" height="105" style="height:105px;background:#2D5016;padding:0;color:#ffffff;text-align:center;">\n'
INNER_R129 = '''    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;border-spacing:0;background:#2D5016;"><tr>
      <td class="header-palm-cell" width="50%" align="center" valign="middle" bgcolor="#2D5016" style="width:50%;height:105px;background:#2D5016;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;"></td>
      <td width="1%" align="center" valign="middle" bgcolor="#2D5016" style="width:1%;white-space:nowrap;height:105px;background:#2D5016;color:#ffffff;text-align:center;"><span class="header-title">Palm Hill Country Club</span></td>
      <td class="header-palm-cell" width="50%" align="center" valign="middle" bgcolor="#2D5016" style="width:50%;height:105px;background:#2D5016;"><img class="header-palm" alt="" src="palm.png" width="80" height="84" style="display:block;width:80px;height:84px;border:0;margin:auto;transform:scaleX(-1);"></td>
    </tr></table>
  </td></tr>'''
R129_HTML = '<table><tr>' + WRAP + INNER_R129


def test_r129_painted_cells_are_caught():
    hits = sr.masthead_single_paint_problems(R129_HTML)
    assert hits and "paints its own background" in hits[0]


def test_fixer_paints_only_the_wrapping_cell_and_keeps_widths():
    fixed = sr.fix_masthead_single_paint(R129_HTML)
    assert sr.masthead_single_paint_problems(fixed) == []
    assert sr.masthead_seam_problems(fixed) == []  # R129 widths / border-spacing still hold
    assert fixed.count('bgcolor="#2D5016"') == 1 and fixed.count("background:#2D5016") == 1
    assert fixed.startswith('<table><tr>' + WRAP)
    assert fixed.count('width="50%"') == 2 and 'width="1%"' in fixed
    assert "transform:scaleX(-1)" in fixed
    assert sr.fix_masthead_single_paint(fixed) == fixed


def test_r129_then_r132_pipeline_on_current_send():
    send = ROOT / "pages/previews/2026-11-15/PHNEWS-2026-11-15-SEND.html"
    html = send.read_text(encoding="utf-8")
    assert sr.masthead_single_paint_problems(html) == []
    assert sr.masthead_seam_problems(html) == []
    assert sr.listen_icon_problems(html, ROOT) == []
    assert sr.fix_masthead_single_paint(sr.fix_masthead_seams(html)) == html


def test_pages_without_a_masthead_are_skipped():
    html = "<html><body><p>No banner here</p></body></html>"
    assert sr.fix_masthead_single_paint(html) == html
    assert sr.masthead_single_paint_problems(html) == []


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:
                failed += 1
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
