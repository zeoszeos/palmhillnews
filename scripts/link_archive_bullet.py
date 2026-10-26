"""STYLE-RULES.md R14: Helpful Webpages carries 'Palm Hill Link Archives' right after 'Palm Hill Link Monthly'. Idempotent."""
import re
URL = "https://palmhillnews.vercel.app/pages/archive/palm-hill-link.html"
BUL = f'<div>• <a href="{URL}" style="color:#3A6B1A;">Palm Hill Link Archives</a></div>'
def add(s, web_copy=False):
    if web_copy:  # archive web copy: Link Monthly (download stripped) -> Link Archives page
        s = s.replace("<span>Palm Hill Link Monthly</span>", f'<a href="{URL}" style="color:#3A6B1A;">Palm Hill Link Monthly</a>')
    if "Palm Hill Link Archives</a>" in s or f'href="{URL}" style="color:#3A6B1A;">Palm Hill Link</a>' in s: return s  # R81 single "Palm Hill Link" bullet
    n = re.subn(r'(<div>• <(?:a|span)\b[^>]*>Palm Hill Link Monthly</(?:a|span)></div>)', r'\1\n          ' + BUL, s, count=1)
    assert n[1] == 1, "Palm Hill Link Monthly bullet not found"
    return n[0]
if __name__ == "__main__":
    import sys
    web = "--web" in sys.argv
    for f in [a for a in sys.argv[1:] if a != "--web"]:
        t = open(f, encoding="utf-8").read(); open(f, "w", encoding="utf-8").write(add(t, web)); print("ok", f)
