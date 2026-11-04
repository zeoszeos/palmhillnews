"""R107 (Steven Nov 4 2026 4:35 PM, voice): no white / near-white or low-contrast text on light or yellow backgrounds
in the calendar sections (email preview + SEND, Recurring and All Events pages). Static walk of the rendered HTML:
each text run gets its inherited text colour (-webkit-text-fill-color wins over color) and the nearest ancestor
background (style background/background-color or bgcolor). WCAG 2.x relative-luminance contrast; AA = 4.5:1."""
import colorsys, re
from html.parser import HTMLParser

AA = 4.5
VOID = {"br", "img", "hr", "meta", "link", "input", "source", "col", "area", "base", "wbr"}
_NAMED = {"white": "#ffffff", "black": "#000000", "yellow": "#ffff00", "lightyellow": "#ffffe0", "transparent": None}

def hexrgb(c):
    c = (c or "").strip().lower()
    c = _NAMED.get(c, c)
    if not c: return None
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c)
    if m:
        h = m.group(1); h = "".join(x * 2 for x in h) if len(h) == 3 else h
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)", c)
    if m and (m.group(4) is None or float(m.group(4)) > 0.5): return tuple(int(m.group(i)) for i in (1, 2, 3))
    return None

def lum(rgb):
    v = [x / 255 for x in rgb]; v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + 0.05) / (lb + 0.05)

def is_light(bg): return lum(bg) >= 0.6
def is_yellow(bg):
    h, l, s = colorsys.rgb_to_hls(*(x / 255 for x in bg)); return l >= 0.75 and s >= 0.3 and 35 / 360 <= h <= 70 / 360
def near_white(fg): return lum(fg) >= 0.85

def _decl(style, prop):
    m = None
    for m in re.finditer(r"(?:^|;)\s*" + prop + r"\s*:\s*([^;!]+)", style or "", re.I): pass
    return m.group(1).strip() if m else None

class _W(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.st = [((51, 51, 51), (255, 255, 255), "body")]; self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head", "title"): self.skip += 1
        if tag in VOID: return
        a = dict(attrs); s = a.get("style") or ""; fg, bg, _ = self.st[-1]
        bgs = _decl(s, "background-color") or _decl(s, "background") or a.get("bgcolor")
        if bgs: bg = hexrgb(bgs.split()[0]) or bg
        f = hexrgb(_decl(s, "-webkit-text-fill-color") or "") or hexrgb(_decl(s, "color") or a.get("color") or "")
        self.st.append((f or fg, bg, tag))
    def handle_endtag(self, tag):
        if tag in ("style", "script", "head", "title"): self.skip = max(0, self.skip - 1)
        if tag in VOID: return
        for i in range(len(self.st) - 1, 0, -1):
            if self.st[i][2] == tag: del self.st[i:]; break
    def handle_data(self, d):
        t = d.strip()
        if t and not self.skip and re.search(r"\w", t): fg, bg, _ = self.st[-1]; self.out.append((t[:60], fg, bg))

def runs(html): w = _W(); w.feed(html); return w.out

def violations(html):
    """(text, fg hex, bg hex, ratio) for every text run that is white/near-white on a light background, or below AA on yellow."""
    bad = []
    for t, fg, bg in runs(html):
        r = ratio(fg, bg)
        if (is_light(bg) and near_white(fg)) or (is_yellow(bg) and r < AA):
            bad.append((t, "#%02X%02X%02X" % fg, "#%02X%02X%02X" % bg, round(r, 2)))
    return bad
