"""Shim: Listen fix now lives in the repo's shared scripts/style_rules.py (STYLE-RULES.md)."""
import sys; sys.path.insert(0, "/workspace/oct18-batch/scripts")
from style_rules import listen_fix as fix
if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read(); n = fix(s); open(f, "w", encoding="utf-8").write(n); print(f, n != s)
