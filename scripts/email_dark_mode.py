"""STYLE-RULES R97 (Steven Oct 30 2026 10:11 PM) + R147 (Steven Nov 27 2026, voice).

Gmail iPhone dark mode turns a pure-white background black but keeps explicit dark text, which made
unreadable "black bands" on the white alternate rows. From DARK_FROM on, the SEND / email copy
(never the archived issues, never the on-site preview) gets:
  * every pure-white background (#FFF / #FFFFFF / white) on a tr / td / table in the body -> EMAIL_TINT
    (one constant), repeated on each cell of those rows (style background + bgcolor) and as bgcolor
    on the tr / table (R97);
  * <meta name="color-scheme" content="light only"> and
    <meta name="supported-color-schemes" content="light"> plus :root{color-scheme:light only;} in
    <head>, and the same :root/body color-scheme rule in a body-level <style> (head styles are often
    stripped when Gmail forwards a copy) (R97 + R147);
  * explicit light backgrounds (bgcolor attribute plus inline background-color) and an explicit text
    color on the body, wrapper tables / chrome cells, and section containers, so a forwarded copy
    keeps the light look even after Gmail strips the head (R147).

Text colours and the green rows are untouched. No script is added.
"""
import re

DARK_FROM = "2026-11-01"
EMAIL_TINT = "#FBFDF9"
PAGE_BG = "#f5f5f5"  # existing SEND page chrome (the grey around the card)
INK = "#333333"  # existing default body text colour in the SEND
_WHITE = r"(?:#fff(?:fff)?|white)\b"
HEAD_ADD = (
    '<meta name="color-scheme" content="light only">'
    '<meta name="supported-color-schemes" content="light">'
    "<style>:root{color-scheme:light only;}</style>"
)
BODY_SCHEME = "<style>:root,body{color-scheme:light only;}</style>"
# Tags that accept a bgcolor attribute (divs do not).
_BGCOLOR_TAGS = ("body", "table", "tr", "td", "th")


def applies(issue):
    return issue >= DARK_FROM


def _tint_tag(tag):
    tag = re.sub(r"(background(?:-color)?:\s*)" + _WHITE, r"\1" + EMAIL_TINT, tag, flags=re.I)
    if "bgcolor=" not in tag.lower():
        tag = re.sub(r"^<(\w+)", r'<\1 bgcolor="' + EMAIL_TINT + '"', tag)
    return tag


def _cell(tag):
    if re.search(r"background(?:-color)?:", tag, re.I) or "bgcolor=" in tag.lower():
        return tag
    if 'style="' in tag:
        tag = tag.replace('style="', f'style="background:{EMAIL_TINT};', 1)
    else:
        tag = tag[:-1] + f' style="background:{EMAIL_TINT};">'
    return re.sub(r"^<td", f'<td bgcolor="{EMAIL_TINT}"', tag)


def _style_dict(tag):
    m = re.search(r'\sstyle="([^"]*)"', tag, re.I)
    if not m:
        return {}
    out = {}
    for part in m.group(1).split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def _set_style(tag, **props):
    """Set or add style properties; existing properties not named here stay as they are."""
    styles = _style_dict(tag)
    for k, v in props.items():
        if v is None:
            continue
        key = k.strip().lower()
        if key not in styles or (key == "background-color" and not styles.get(key)):
            styles[key] = v
        elif key == "background-color" and key not in styles:
            styles[key] = v
        elif key not in styles:
            styles[key] = v
    # Always force background-color and color when provided (R147: explicit, even if shorthand exists).
    for k, v in props.items():
        if v is None:
            continue
        key = k.strip().lower()
        if key in ("background-color", "color"):
            if key == "color" and "color" in styles:
                continue  # never override an existing text colour (green-on-white, white-on-green)
            if key == "background-color":
                styles[key] = v
            elif key not in styles:
                styles[key] = v
    encoded = ";".join(f"{k}:{v}" for k, v in styles.items())
    if encoded and not encoded.endswith(";"):
        encoded += ";"
    if re.search(r'\sstyle="[^"]*"', tag, re.I):
        return re.sub(r'\sstyle="[^"]*"', f' style="{encoded}"', tag, count=1, flags=re.I)
    return tag[:-1] + f' style="{encoded}">'


def _tag_name(tag):
    m = re.match(r"</?([a-zA-Z0-9]+)", tag)
    return (m.group(1).lower() if m else "")


def _bgcolor_val(tag):
    m = re.search(r'\sbgcolor="([^"]*)"', tag, re.I)
    return m.group(1) if m else None


def _parse_hex(color):
    if not color:
        return None
    c = color.strip().lower()
    if c == "white":
        c = "#ffffff"
    if c == "black":
        c = "#000000"
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c)
    if not m:
        return None
    h = m.group(1)
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _luma(rgb):
    r, g, b = rgb
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def _bg_color(tag):
    """Resolved background colour from bgcolor or style, if any."""
    styles = _style_dict(tag)
    for key in ("background-color", "background"):
        val = styles.get(key)
        if val:
            # background shorthand may start with the colour.
            tok = val.strip().split()[0]
            rgb = _parse_hex(tok)
            if rgb:
                return tok if tok.startswith("#") else val, rgb
    bc = _bgcolor_val(tag)
    rgb = _parse_hex(bc or "")
    if rgb:
        return bc, rgb
    return None, None


def _is_dark_bg(tag):
    _, rgb = _bg_color(tag)
    return rgb is not None and _luma(rgb) < 0.5


def _ensure_bgcolor(tag, color):
    if _tag_name(tag) not in _BGCOLOR_TAGS:
        return tag
    if _is_dark_bg(tag):
        return tag
    if "bgcolor=" not in tag.lower():
        return re.sub(r"^<(\w+)", r'<\1 bgcolor="' + color + '"', tag)
    return tag


def _paint_light(tag, color):
    """Add explicit light bgcolor + background-color, and ink if no text colour is set. Skip dark (green) cells."""
    if _is_dark_bg(tag):
        return tag
    existing, rgb = _bg_color(tag)
    # If the tag already has a light background, keep that colour (just make it explicit).
    use = existing if (rgb and _luma(rgb) >= 0.5) else color
    if use and not use.startswith("#"):
        use = color
    tag = _ensure_bgcolor(tag, use)
    styles = _style_dict(tag)
    props = {"background-color": use}
    if "color" not in styles:
        props["color"] = INK
    return _set_style(tag, **props)


def _apply_head(s):
    # Replace the previous R97 head block (supported-color-schemes "light only", optional semicolon)
    # so a rebuild is idempotent and head_ok sees exactly HEAD_ADD.
    old = (
        r'<meta name="color-scheme" content="light only">'
        r'<meta name="supported-color-schemes" content="light(?: only)?">'
        r"<style>:root\{color-scheme:light only;?\}</style>"
    )
    s = re.sub(old, HEAD_ADD, s, count=1, flags=re.I)
    if HEAD_ADD not in s:
        s = s.replace("</head>", HEAD_ADD + "</head>", 1)
    return s


def _apply_body_scheme(s):
    b = re.search(r"<body[^>]*>", s, re.I)
    if not b:
        return s
    insert_at = b.end()
    if BODY_SCHEME in s[insert_at : insert_at + 400] or ":root,body{color-scheme:light only;}" in s:
        return s
    return s[:insert_at] + BODY_SCHEME + s[insert_at:]


def _apply_body_tag(s):
    m = re.search(r"<body[^>]*>", s, re.I)
    if not m:
        return s
    tag = _paint_light(m.group(0), PAGE_BG)
    return s[: m.start()] + tag + s[m.end() :]


def _apply_wrappers_and_sections(s):
    b = s.find("<body")
    if b < 0:
        return s
    head, body = s[:b], s[b:]

    def repl_first_chrome_div(m):
        return _paint_light(m.group(0), PAGE_BG)

    # Outer chrome div (margin:0;padding:0;background:#f5f5f5;...).
    body = re.sub(
        r"<div\b[^>]*style=\"[^\"]*background:\s*#f5f5f5[^\"]*\"[^>]*>",
        repl_first_chrome_div,
        body,
        count=1,
        flags=re.I,
    )

    # Width=100% chrome table and the 660px card table, plus a bare <td align="center"> chrome cell.
    def repl_table(m):
        tag = m.group(0)
        # Card already uses EMAIL_TINT; chrome uses PAGE_BG.
        color = EMAIL_TINT if re.search(r'width="660"', tag, re.I) or EMAIL_TINT.lower() in tag.lower() or "fbdf9" in tag.lower() else PAGE_BG
        if EMAIL_TINT.lower() in tag.lower() or re.search(r'width="660"', tag, re.I):
            color = EMAIL_TINT
        return _paint_light(tag, color)

    # Only the first two opening tables after <body> are the page chrome + card wrappers.
    count = 0

    def repl_table_limited(m):
        nonlocal count
        count += 1
        if count <= 2:
            return repl_table(m)
        return m.group(0)

    body = re.sub(r"<table\b[^>]*>", repl_table_limited, body, flags=re.I)

    def repl_center_td(m):
        tag = m.group(0)
        if _style_dict(tag) or _bgcolor_val(tag) or _is_dark_bg(tag):
            # Still ensure bgcolor + background-color if it only has align="center"
            if "align=\"center\"" in tag.lower() and not _style_dict(tag) and not _bgcolor_val(tag):
                return _paint_light(tag, PAGE_BG)
            return tag
        return _paint_light(tag, PAGE_BG)

    # First bare centering cell after the chrome table.
    body = re.sub(r'<td align="center">', repl_center_td, body, count=1, flags=re.I)

    def repl_section(m):
        return _paint_light(m.group(0), EMAIL_TINT)

    body = re.sub(
        r'<div class="(?:canonical-section|section04)"[^>]*>',
        repl_section,
        body,
        flags=re.I,
    )
    return head + body


def apply(s):
    s = _apply_head(s)
    b = s.index("<body")
    head, body = s[:b], s[b:]
    out, i, white_tr_depth, depth = [], 0, [], 0  # depth = table nesting; white_tr_depth = depths of open white rows
    for m in re.finditer(r"<(/?)(table|tr|td)\b[^>]*>", body, re.I):
        out.append(body[i : m.start()])
        tag = m.group(0)
        close, name = m.group(1), m.group(2).lower()
        i = m.end()
        white = bool(re.search(r"background(?:-color)?:\s*" + _WHITE, tag, re.I))
        if not close and name == "table":
            depth += 1
            if white:
                tag = _tint_tag(tag)
        elif close and name == "table":
            depth -= 1
        elif not close and name == "tr":
            if white:
                tag = _tint_tag(tag)
                white_tr_depth.append(depth)
        elif close and name == "tr":
            if white_tr_depth and white_tr_depth[-1] == depth:
                white_tr_depth.pop()
        elif not close and name == "td":
            if white:
                tag = _tint_tag(tag)
            elif white_tr_depth and white_tr_depth[-1] == depth:
                tag = _cell(tag)
        out.append(tag)
    out.append(body[i:])
    s = head + "".join(out)
    s = _apply_body_tag(s)
    s = _apply_body_scheme(s)
    s = _apply_wrappers_and_sections(s)
    return s


def find_white(s):
    """Guard: pure-white backgrounds left on table/tr/td in the body (style or bgcolor)."""
    body = s[s.find("<body") :]
    return [
        t[:90]
        for t in re.findall(r"<(?:table|tr|td)\b[^>]*>", body, re.I)
        if re.search(r"background(?:-color)?:\s*" + _WHITE + r"|bgcolor=\"" + _WHITE, t, re.I)
    ]


def head_ok(s):
    return HEAD_ADD in s[: s.find("<body")]


def _has_light_bgcolor(tag):
    val, rgb = _bg_color(tag)
    return rgb is not None and _luma(rgb) >= 0.5


def _has_bgcolor_attr(tag):
    val = _bgcolor_val(tag)
    rgb = _parse_hex(val or "")
    return rgb is not None and _luma(rgb) >= 0.5


def _has_bgcolor_style(tag):
    styles = _style_dict(tag)
    raw = styles.get("background-color") or (styles.get("background", "").split() or [""])[0]
    rgb = _parse_hex(raw)
    return rgb is not None and _luma(rgb) >= 0.5


def _has_text_color(tag):
    styles = _style_dict(tag)
    # 'color' not 'background-color'
    rgb = _parse_hex(styles.get("color") or "")
    return rgb is not None and _luma(rgb) < 0.5  # dark text on the light ground


def forward_light_problems(s):
    """R147 guard: SEND has the metas and explicit light backgrounds + text colour on body, wrappers, sections."""
    problems = []
    if "<body" not in s:
        return ["no <body>"]
    head = s[: s.find("<body")]
    if not re.search(r'<meta\s+name="color-scheme"\s+content="light only"', head, re.I):
        problems.append("head missing <meta name=\"color-scheme\" content=\"light only\">")
    if not re.search(r'<meta\s+name="supported-color-schemes"\s+content="light"', head, re.I):
        problems.append("head missing <meta name=\"supported-color-schemes\" content=\"light\">")
    if not re.search(r":root\{color-scheme:light only;?\}", head):
        problems.append("head missing :root{color-scheme:light only;}")
    bm = re.search(r"<body[^>]*>", s, re.I)
    if not bm:
        problems.append("no body tag")
        return problems
    body_tag = bm.group(0)
    if not _has_bgcolor_attr(body_tag):
        problems.append("body missing light bgcolor attribute")
    if not _has_bgcolor_style(body_tag):
        problems.append("body missing inline background-color")
    if not _has_text_color(body_tag):
        problems.append("body missing explicit text color")
    body = s[s.find("<body") :]
    tables = re.findall(r"<table\b[^>]*>", body, re.I)
    if not tables:
        problems.append("no wrapper table")
    else:
        for i, tag in enumerate(tables[:2], 1):
            if not _has_bgcolor_attr(tag):
                problems.append(f"wrapper table {i} missing light bgcolor attribute")
            if not _has_bgcolor_style(tag):
                problems.append(f"wrapper table {i} missing inline background-color")
    sections = re.findall(r'<div class="(?:canonical-section|section04)"[^>]*>', body, re.I)
    if not sections:
        problems.append("no section containers")
    for i, tag in enumerate(sections, 1):
        if not _has_bgcolor_style(tag):
            problems.append(f"section container {i} missing inline background-color")
        if not _has_text_color(tag):
            problems.append(f"section container {i} missing explicit text color")
    return problems
