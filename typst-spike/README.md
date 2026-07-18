# Typst port — de-risking spike

A proof-of-concept port of latex-tools to [Typst](https://typst.app), built to
validate the LaTeX→Typst assessment. It ports the hardest layout (`prettydoc`)
and the simplest (`datasheet`), the FontAwesome icon path, and the YAML manifest
path, and diffs the rendered output against the committed example PDFs.

**Read the docs in this order:**

1. [`FINDINGS.md`](FINDINGS.md) — what was built, fidelity result, and the
   LaTeX→Typst mapping table. Start here.
2. [`MIGRATION.md`](MIGRATION.md) — the `latex2typ.py` migration prototype
   (deterministic + LLM-fallback) and results on the repo's own examples.
3. [`WEB-TOOL-ASSESSMENT.md`](WEB-TOOL-ASSESSMENT.md) — architecture for the
   hosted web product (authoring, AppSheet-replacement doc management,
   revisions, Google-Docs-style collaboration).

The `compare-*.png` files are side-by-side render diffs (LaTeX reference vs the
Typst port, and vs the fully auto-migrated output).

## Reproducing

The spike compiles with the `typst` compiler. In this sandbox it was installed
from PyPI (`pip install typst`) because the GitHub release wasn't reachable;
a normal `typst` binary works identically.

Fonts used (open stand-ins — see FINDINGS.md): Montserrat, Liberation Sans
(Arial-compatible), and FontAwesome 6 Free. Put them in a `fonts/` dir.

```bash
# with the typst binary:
typst compile --root . --font-path fonts build/prettydoc-example.typ

# or via the PyPI package wrapper used here:
python tc.py build/prettydoc-example.typ out/prettydoc.pdf

# run the migrator on any .tex:
python migrate/latex2typ.py ../examples/requirements/*.tex out.typ
```

> This is exploratory scaffolding, not production code — it lives outside the
> shipped `classes/`, `packages/`, `lua/` and `cli/` trees on purpose.
