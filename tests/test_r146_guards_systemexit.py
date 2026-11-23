"""R146: live build/send guards raise SystemExit, not assert (survives python -O)."""
import subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr


def test_no_bare_assert_in_guard_code():
    hits = sr.bare_assert_problems(ROOT)
    assert hits == [], "R146: bare assert in guard code (stripped by python -O):\n" + "\n".join(hits)


def test_scanner_finds_assert_and_ignores_comments():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "builder" / "core").mkdir(parents=True)
        (t / "scripts").mkdir()
        (t / "builder" / "core" / "example.py").write_text("x = 1\nassert x == 1, 'nope'\n")
        (t / "scripts" / "check_demo.py").write_text("# this comment mentions assert\nx = 1\n")
        (t / "scripts" / "style_rules.py").write_text("ok = True\n")
        hits = sr.bare_assert_problems(t)
        assert any("example.py:2:" in h and "assert x == 1" in h for h in hits), hits
        assert not any("check_demo.py" in h for h in hits), hits


def test_assert_dyk_items_raises_systemexit():
    try:
        sr.assert_dyk_items([])
    except SystemExit as e:
        assert "R50" in str(e)
    else:
        raise AssertionError("expected SystemExit")




def _load_r18_cut():
    """Load _R18_CUT from build_core.py without running the builder."""
    import ast
    src = (ROOT / "builder/core/build_core.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_R18_CUT")
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "build_core.py", "exec"), ns)
    return ns["_R18_CUT"]


def test_r18_cut_returns_prefix():
    """Claude's patch had `if not ...: raise ...; return cut` on one line, so a valid cut returned None."""
    cut = _load_r18_cut()
    text = "First sentence. Second sentence. Third."
    assert cut(text, 1) == "First sentence."
    assert cut(text, 2) == "First sentence. Second sentence."
    try:
        cut("", 1)
    except SystemExit:
        pass
    else:
        raise AssertionError("empty source should SystemExit")

def test_guard_stops_under_optimize():
    """A deliberately failing guard must still stop under python -O (assert would be stripped)."""
    code = (
        "import sys; sys.path.insert(0, %r); import style_rules as s; s.assert_dyk_items([])"
        % str(ROOT / "scripts")
    )
    r = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True)
    assert r.returncode != 0, r.stdout + r.stderr
    assert "R50" in (r.stderr or "") + (r.stdout or ""), r.stdout + r.stderr


if __name__ == "__main__":
    test_no_bare_assert_in_guard_code()
    test_scanner_finds_assert_and_ignores_comments()
    test_assert_dyk_items_raises_systemexit()
    test_r18_cut_returns_prefix()
    test_guard_stops_under_optimize()
    print("PASS test_r146_guards_systemexit")
