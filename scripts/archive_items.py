#!/usr/bin/env python3
"""STYLE-RULES R68 (Steven, Oct 24 2026 9:05 PM, coding batch 2): the ONE way code edits archive/archive-items.json.
Every edit is made on the parsed data first; the file keeps its hand-curated one-row-per-line layout (only the edited
rows' text changes), and the new text is written only after it parses back to exactly the intended data. The write is
atomic (temp file + rename), so a failed edit never leaves a half-written file."""
import json, os, tempfile
from pathlib import Path

def path(repo): return Path(repo) / "archive" / "archive-items.json"
def load(repo):
    t = path(repo).read_text(encoding="utf-8"); return t, json.loads(t)
def _items_open(t, section):
    k = t.find(f'"{section}": {{'); i = t.find('"items": [', k)
    if k < 0 or i < 0: raise SystemExit(f"R68: archive-items.json has no {section!r} items list")
    return i + len('"items": [')
def _check(t, want):
    got = json.loads(t)
    if got != want: raise SystemExit("R68: archive-items.json edit did not produce the intended data; nothing written")
    return t
def save_text(repo, t, want):
    _check(t, want); f = path(repo)
    if f.read_text(encoding="utf-8") == t: return False
    fd, tmp = tempfile.mkstemp(dir=f.parent, prefix=".archive-items.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as h: h.write(t)
    os.replace(tmp, f); return True

def add_rows_text(t, section, rows, key="page"):
    """Insert rows (in order) at the top of a section's items, skipping any whose `key` is already listed. Returns text."""
    d = json.loads(t); items = d["sections"][section]["items"]
    have = {it.get(key) for it in items}; new = [r for r in rows if r.get(key) not in have]
    if not new: return t
    d["sections"][section]["items"] = new + items
    i = _items_open(t, section)
    out = t[:i] + "".join("\n      " + json.dumps(r, ensure_ascii=False) + "," for r in new) + t[i:]
    return _check(out, d)
def add_rows(repo, section, rows, key="page"):
    t, _ = load(repo); out = add_rows_text(t, section, rows, key); return save_text(repo, out, json.loads(out))

def set_field_text(t, section, match, field, value):
    """Set `field` on the ONE item of `section` whose keys equal `match` (dict). Only that value's text changes."""
    d = json.loads(t); items = d["sections"][section]["items"]
    hit = [n for n, it in enumerate(items) if all(it.get(k) == v for k, v in match.items())]
    if len(hit) != 1: raise SystemExit(f"R68: expected one {section} row matching {match}, found {len(hit)}")
    it = items[hit[0]]
    if it.get(field) == value: return t
    if field not in it: raise SystemExit(f"R68: {section} row {match} has no {field!r} field")
    old_s = f'"{field}": ' + json.dumps(it[field], ensure_ascii=False); new_s = f'"{field}": ' + json.dumps(value, ensure_ascii=False)
    it[field] = value
    cands, p = [], t.find(old_s)
    while p >= 0:
        c = t[:p] + new_s + t[p + len(old_s):]
        try:
            if json.loads(c) == d: cands.append(c)
        except ValueError: pass
        p = t.find(old_s, p + 1)
    if len(cands) != 1: raise SystemExit(f"R68: could not place {section} {match} {field} edit uniquely ({len(cands)} candidates)")
    return cands[0]
def set_field(repo, section, match, field, value):
    t, _ = load(repo); out = set_field_text(t, section, match, field, value); return save_text(repo, out, json.loads(out))

def set_items_text(t, section, items):
    """Replace a section's whole items list, one row per line (used by the Latest videos sync)."""
    d = json.loads(t); d["sections"][section]["items"] = list(items)
    a = _items_open(t, section); b = t.index("\n    ]}", a)
    out = t[:a] + "\n" + ",\n".join("      " + json.dumps(v, ensure_ascii=False) for v in items) + t[b:]
    return _check(out, d)
def set_items(repo, section, items):
    t, _ = load(repo); out = set_items_text(t, section, items); return save_text(repo, out, json.loads(out))
