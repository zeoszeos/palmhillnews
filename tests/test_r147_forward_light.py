"""R147: forwarded SEND copies keep a light look in Gmail (explicit body/wrapper/section backgrounds)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import email_dark_mode as dm

BARE = """<!doctype html><html><head><meta charset="utf-8"><title>t</title></head>
<body style="margin:0">
<div style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f5f5f5;padding:20px 0;">
<tr><td align="center">
<table width="660" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:660px;background:#ffffff;">
<tr><td style="background:#ffffff;color:#333333;">hello</td></tr>
</table>
</td></tr></table>
<div class="canonical-section"><p style="color:#333333;">one</p></div>
<div class="section04"><p>two</p></div>
</div>
</body></html>"""

GREEN = """<!doctype html><html><head></head><body>
<table width="100%" style="background:#f5f5f5;"><tr><td align="center">
<table width="660" bgcolor="#FBFDF9" style="background:#FBFDF9;">
<tr><td bgcolor="#2D5016" style="background:#2D5016;color:#ffffff;">masthead</td></tr>
</table></td></tr></table>
<div class="canonical-section">x</div>
</body></html>"""


def test_apply_adds_metas_and_explicit_light():
    out = dm.apply(BARE)
    assert dm.head_ok(out), out[:400]
    assert not dm.find_white(out), dm.find_white(out)
    probs = dm.forward_light_problems(out)
    assert not probs, probs
    # idempotent
    out2 = dm.apply(out)
    assert dm.head_ok(out2)
    assert not dm.forward_light_problems(out2)


def test_green_masthead_untouched():
    out = dm.apply(GREEN)
    assert 'bgcolor="#2D5016"' in out
    assert "background:#2D5016" in out or "background-color:#2D5016" in out
    assert "color:#ffffff" in out
    # do not paint the green cell light
    assert 'bgcolor="#2D5016" style="background:#2D5016;color:#ffffff;"' in out or (
        'bgcolor="#2D5016"' in out and "color:#ffffff" in out
    )


def test_guard_fails_on_bare_body():
    probs = dm.forward_light_problems(BARE)
    assert any("body" in p for p in probs), probs


def test_publish_guard_is_systemexit_pattern():
    # R146: the publish path raises SystemExit, not assert. Confirm the helper returns a list
    # the caller raises SystemExit on, and that a failing document is non-empty.
    assert dm.forward_light_problems(BARE)
    assert not dm.forward_light_problems(dm.apply(BARE))
