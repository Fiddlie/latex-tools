#!/usr/bin/env python3
"""tc.py <input.typ> <output.pdf> — compile with scratchpad as root + font dir."""
import sys, typst, pathlib
root = pathlib.Path(__file__).parent.resolve()
inp, out = sys.argv[1], sys.argv[2]
pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
try:
    typst.compile(inp, output=out, root=str(root), font_paths=[str(root/"fonts")])
    print(f"OK -> {out}")
except Exception as e:
    print("TYPST ERROR:\n", e); sys.exit(1)
