# CLAUDE.md — Fiddlie latex-tools

Guidance for working on the **latex-tools** repo itself (the document classes,
packages, Lua modules and the `fdoc` CLI). Repos that *consume* latex-tools get
their own generated `CLAUDE.md` from `fdoc init`; this file is for developing
latex-tools.

## Repository layout

- `classes/` — document classes (`.cls`) and their per-class `*.README.md`
- `packages/` — shared LaTeX packages (`.sty`): `fiddlie-common`, `fiddlie-icons`, `fiddlie-manifest`
- `lua/` — Lua modules loaded by the packages (icon table, manifest loader, requirement tracker)
- `assets/` — shared logo files
- `cli/` — the `fdoc` Python CLI (document scaffolding, build, revisions, fonts)
- `docs/` — `CLAUDE_*.md` authoring guides, one per document type (referenced by consuming repos)
- `examples/` — one worked example per class, each with a committed PDF
- `scripts/` — maintenance scripts (e.g. regenerating the FA icon table)

## Building documents (IMPORTANT: fonts required)

**FontAwesome Pro fonts must be installed before any document will build.**
`fiddlie-common` loads `fiddlie-icons`, which binds the FA7 Pro OTF families at
package-load time via `fontspec`. This happens for **every** document — even
ones that use no icons — so a missing font is a hard failure
(`Package fontspec Error: The font "..." cannot be found`), not a warning.

Install the fonts once per machine (they go to `TEXMFHOME`, shared across repos):

```bash
fdoc fonts install      # downloads the FA kit (~150MB) from the GitHub release
fdoc fonts status       # check install state
```

Other build prerequisites:

- **LuaLaTeX** (the classes are LuaLaTeX-only) and **latexmk**.
- **Arial** — `fiddlie-common`'s main font.
- **Montserrat** — used by `prettydoc` only; ships with TeX Live as the
  `montserrat` package. If absent, prettydoc falls back to the inherited font
  with a class warning (it still builds).
- **TEXINPUTS** must include `classes/`, `packages/` and `lua/`. Consuming repos
  get this from the `.latexmkrc` that `fdoc init` writes; when building the
  examples here directly, set it yourself, e.g.:

  ```bash
  export TEXINPUTS="$PWD/classes//:$PWD/packages//:$PWD/lua//:"
  ```

The reliable way to build is `fdoc build <doc>` (or `fdoc build .` inside a
document folder), which also lazy-installs the fonts on first use.

### Toolchain caveat: spaces in font filenames

The FA Pro OTF filenames contain spaces (e.g. `Font Awesome 7 Pro-Solid-900.otf`).
On older TeX Live (≈2023), `fontspec` strips the spaces before the lookup and the
font is reported as not found. Fixes, cheapest first:

- Use a recent TeX Live (2024+), where this resolves correctly; **or**
- Add spaceless symlinks next to the installed OTFs
  (`FontAwesome7Pro-Solid-900.otf` → the spaced file) and refresh
  (`mktexlsr` + `luaotfload-tool --update`); **or**
- Ensure `luaotfload`'s cache is writable (`TEXMFCACHE`/`TEXMFVAR`) so the font
  database persists and isn't rebuilt mid-run.

The packages themselves are correct as shipped — this is purely a local
toolchain quirk, so do not "fix" it by editing `fiddlie-icons.sty`.

## Conventions when adding a document type

A new document type should be wired through every surface (see the prettydoc and
onepager commits for a worked example):

1. `classes/<type>.cls` and `classes/<type>.README.md`
2. CLI registration in `cli/src/fdoc/commands/create.py`
   (`DOCUMENT_TYPES`, `DOCUMENT_TYPE_NAMES`, `DOCUMENT_TYPE_CLASSES`)
3. CLI templates under `cli/src/fdoc/templates/<type>/`
   (`default`/`empty`, each with and without manifest, plus `manifest.yaml.j2`)
4. `docs/CLAUDE_<TYPE>.md` authoring guide
5. An `examples/<type>/` worked example (with a built PDF)
6. Listings in the top-level `README.md`, `cli/README.md`, and the generated
   `cli/src/fdoc/templates/claude_guide.md`

## CLI development

```bash
cd cli
pip install -e ".[dev]"
pytest
```
