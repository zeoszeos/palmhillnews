"""STYLE-RULES R97 (Steven Oct 30 2026 10:11 PM): Gmail iPhone dark mode turns a pure-white background black but keeps the
explicit dark text colour -> unreadable "black bands" on the white alternate rows. From DARK_FROM on, the SEND / email copy
(never the archived issues, never the on-site preview) gets:
  * every pure-white background (#FFF / #FFFFFF / white) on a tr / td / table in the body -> EMAIL_TINT (one constant),
  * the tint repeated on each cell of those rows (style background + bgcolor attribute) and as bgcolor on the tr / table,
  * <meta name="color-scheme" / "supported-color-schemes" content="light only"> + :root{color-scheme:light only} in <head>.
Text colours and the green rows are untouched. No script is added."""
import re
DARK_FROM = "2026-11-01"
EMAIL_TINT = "#FBFDF9"
_WHITE = r"(?:#fff(?:fff)?|white)\b"
HEAD_ADD = ('<meta name="color-scheme" content="light only"><meta name="supported-color-schemes" content="light only">'
            '<style>:root{color-scheme:light only}</style>')
def applies(issue): return issue >= DARK_FROM
def _tint_tag(tag):
    tag = re.sub(r"(background(?:-color)?:\s*)" + _WHITE, r"\1" + EMAIL_TINT, tag, flags=re.I)
    if "bgcolor=" not in tag.lower(): tag = re.sub(r"^<(\w+)", r'<\1 bgcolor="' + EMAIL_TINT + '"', tag)
    return tag
def _cell(tag):
    if re.search(r"background(?:-color)?:", tag, re.I) or "bgcolor=" in tag.lower(): return tag
    if 'style="' in tag: tag = tag.replace('style="', f'style="background:{EMAIL_TINT};', 1)
    else: tag = tag[:-1] + f' style="background:{EMAIL_TINT};">'
    return re.sub(r"^<td", f'<td bgcolor="{EMAIL_TINT}"', tag)
def apply(s):
    if HEAD_ADD not in s: s = s.replace("</head>", HEAD_ADD + "</head>", 1)
    b = s.index("<body")
    head, body = s[:b], s[b:]
    out, i, white_tr_depth, depth = [], 0, [], 0   # depth = table nesting; white_tr_depth = depths of open white rows
    for m in re.finditer(r"<(/?)(table|tr|td)\b[^>]*>", body, re.I):
        out.append(body[i:m.start()]); tag = m.group(0); close, name = m.group(1), m.group(2).lower(); i = m.end()
        white = bool(re.search(r"background(?:-color)?:\s*" + _WHITE, tag, re.I))
        if not close and name == "table":
            depth += 1
            if white: tag = _tint_tag(tag)
        elif close and name == "table": depth -= 1
        elif not close and name == "tr":
            if white: tag = _tint_tag(tag); white_tr_depth.append(depth)
        elif close and name == "tr":
            if white_tr_depth and white_tr_depth[-1] == depth: white_tr_depth.pop()
        elif not close and name == "td":
            if white: tag = _tint_tag(tag)
            elif white_tr_depth and white_tr_depth[-1] == depth: tag = _cell(tag)
        out.append(tag)
    out.append(body[i:])
    return head + "".join(out)
def find_white(s):
    """Guard: pure-white backgrounds left on table/tr/td in the body (style or bgcolor)."""
    body = s[s.find("<body"):]
    return [t[:90] for t in re.findall(r"<(?:table|tr|td)\b[^>]*>", body, re.I)
            if re.search(r"background(?:-color)?:\s*" + _WHITE + r"|bgcolor=\"" + _WHITE, t, re.I)]
def head_ok(s): return HEAD_ADD in s[:s.find("<body")]
