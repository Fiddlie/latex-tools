# Typst port — de-risking spike findings

Goal: validate the LaTeX→Typst port assessment by actually porting the hardest
layout (`prettydoc`) and the icon/manifest path, and diffing the output against
the committed example PDFs. Verdict up front: **the port is viable and mostly
simplifying; the hardest LaTeX layout reproduces faithfully in Typst.**

## What was built

```
typst-spike/
  fiddlie/            the ported library
    fa-icons.typ      4,319-icon codepoint dict, transpiled from lua/fa-icons.lua
    icons.typ         faicon()/bigicon() — port of fiddlie-icons.sty
    common.typ        brand colours, logo, native yaml() manifest path
    prettydoc.typ     the flagship class — full port
    datasheet.typ     the simplest class + shared furniture
    assets/           logo (SVG loads natively)
  build/              the two example docs, hand-ported to Typst
  migrate/            latex2typ.py — the migration prototype (see below)
  compare-*.png       side-by-side render diffs vs the LaTeX reference PDFs
```

Everything compiles with the `typst` compiler (tested via the `typst` PyPI
package) using open fonts: Montserrat (Google Fonts), Liberation Sans (metric-
compatible Arial stand-in — and exactly the graceful fallback `prettydoc`
itself takes when Montserrat is absent), and **FontAwesome 6 Free** in place of
FA7 Pro (only the family-name mapping differs).

## Fidelity result

`prettydoc-example` and `datasheet-example` were rendered from both toolchains
and rasterised for comparison (`compare-*.png`).

- **prettydoc** (the hard one) reproduces faithfully: full-bleed tricolour bar,
  logo, letterspaced meta block, eyebrow kickers, two-tone accent title,
  auto-numbered card chips, blue-dot lists, section/subsection display
  headings, the closing sign-off, and the margin-stamped footer with the
  computed `01 / 02` page indicator. Same 2-page flow.
- **datasheet** reproduces faithfully: logo, title, rule, revision line, italic
  doc-ID, diagonal DRAFT watermark, and the three-part footer. **Same 5-page
  output**, confirming `\pageref{LastPage}` → `counter(page).final()` and
  section-per-page (`\clearpage` → `pagebreak`).

The only residual differences are spacing rhythm (LaTeX `\parskip` is a touch
more generous) — pure tuning, not structural gaps.

## How the hard LaTeX machinery mapped

| LaTeX (prettydoc / common) | Typst | Verdict |
|---|---|---|
| `eso-pic` full-bleed bar (`\AddToShipoutPictureBG`) | `page(background:)` + `place`/`rect` | simpler |
| `eso-pic` margin footer (`\AddToShipoutPictureFG`) | `page(footer:)` grid | simpler |
| `fancyhdr` + `lastpage` + `refcount` `01/02` | `counter(page).get()/.final()` | simpler |
| `titlesec` heading formatting | `show heading.where(...)` | direct |
| `enumitem` custom bullets | `set list(marker: ...)` | direct |
| TikZ card chip / bar / dots | `box`/`rect`/`circle` | direct |
| `microtype` `\textls` letterspacing | `text(tracking: ...)` | direct |
| `directlua` year-from-`\date` | native `str.matches(regex)` | simpler |
| `fontspec` + Montserrat fallback | `text(font: ("Montserrat", "Liberation Sans"))` | native fallback |
| `manifest-loader.lua` (189-line YAML parser) + `lyaml` | native `yaml()` | **deleted** |
| `req-tracker.lua` dedup | `state`/`counter` + `query` | portable |
| `fa-icons.lua` 4,877-line table | transpiled to a Typst dict (script, `migrate/`) | mechanical |
| `.buildid` `\openin`/`\read` dep-tracking hack | native `read()` + automatic deps | **deleted** |
| `kpse`/`graphicspath` asset resolution | package system / relative paths | **deleted** |

## Two toolchain notes

- The `typst` compiler is not reachable from this sandbox's GitHub scope; it
  installs cleanly from **PyPI** (`pip install typst`) which exposes
  `typst.compile(..., root=..., font_paths=[...])`. See `tc.py`.
- FA7 Pro OTFs weren't available here; FA6 Free proves the mechanism. In
  production only `_style-to-font` in `icons.typ` changes (Pro family names).
