"""R85/R85b: phone detection incl. stray space around last hyphen (Nov 1 spaghetti notice)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import tel_links as t
def test_stray_space():
    for s in ["608-312 -6958", "608-312- 6958", "608-312\u00a0-6958"]:
        out = t.linkify("call " + s + ".I was")
        assert 'href="tel:+16083126958"' in out and ">" + s + "</a>" in out, out
        assert t.find_bare(out) == ([], []) and t.tel_mismatches(out) == []
def test_existing():
    assert 'tel:+17275551234' in t.linkify("727-555-1234"); assert 'tel:+17275551234' in t.linkify("(727) 555-1234")
    assert t.find_bare(t.linkify("555-1234"))[1] == ["555-1234"]
if __name__ == "__main__": test_stray_space(); test_existing(); print("tel_links tests OK")
