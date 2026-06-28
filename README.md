# Fiddlie LaTeX Tools

LaTeX document classes and packages for Fiddlie documentation.

## Document Classes

- **[datasheet](classes/datasheet.README.md)** - Professional product data sheets
- **[requirements](classes/requirements.README.md)** - Structured requirements specification documents
- **[policy](classes/policy.README.md)** - Internal policy documents
- **[techreport](classes/techreport.README.md)** - Technical reports
- **[onepager](classes/onepager.README.md)** - Single-page, brand-styled summaries and fact sheets
- **[prettydoc](classes/prettydoc.README.md)** - Branded, presentation-grade documents for public-facing briefs, guides and proposals

## Install (no technical setup)

For non-developers, the easiest path is the **self-contained installer** — no
Python, git, or command-line setup required:

1. Download the installer for your OS from the latest
   [Release](https://github.com/fiddlie/latex-tools/releases)
   (`fdoc-installer-<os>-<arch>-vX.Y.Z.zip`).
2. Unzip it and run the install script: `install.sh` (macOS/Linux — open a
   terminal and run `bash install.sh`) or `install.ps1` (Windows — right-click →
   *Run with PowerShell*).

That's it. The installer places `fdoc` on your PATH and silently sets up the
FontAwesome fonts and the latex-tools runtime from inside the bundle (offline).
You still need a TeX distribution (TeX Live / MacTeX) and Arial installed.

Developers can instead install the CLI directly — see below.

## Usage

Consuming repositories use the [`fdoc` CLI](cli/README.md) and **pin a
latex-tools version** in `.fdocrc` (`latex_tools_version`). `fdoc` installs that
version's runtime (classes, packages, Lua modules and assets) on demand, cached
per machine — no git submodule to vendor or keep in sync.

### Quick Start with fdoc CLI

```bash
# Install the CLI
pip install "git+https://github.com/Fiddlie/latex-tools.git#subdirectory=cli"

# Create a new documentation repository (pins a version, installs the runtime)
fdoc init my-docs
cd my-docs

# Create and build a document
fdoc create datasheet --title "My Product" --id "FD-DC-LTX-10001"
fdoc build .
```

`fdoc build` lazy-installs the pinned runtime and the FontAwesome fonts on first
use. Plain `latexmk` and LaTeX Workshop also work: the generated `.latexmkrc`
asks `fdoc tools texinputs` for the pinned runtime's location.

### Migrating an existing submodule-based repo

Older repos vendored latex-tools as a `latex-tools/` submodule. To move to the
pinned model, run `fdoc update` in the repo — it removes the submodule, records
the version in `.fdocrc`, and rewrites `.latexmkrc`. Commit the result.

### Pinning, updating and the runtime cache

- The pin lives in `.fdocrc`: `latex_tools_version: "2.1.0"`.
- Bump it with `fdoc update --to <version>` (a one-line, reviewable diff), then
  commit — this keeps released documents reproducible.
- Versions are cached under `~/.cache/fdoc/latex-tools/<version>/` (override with
  `FDOC_LATEX_TOOLS_HOME`); many versions coexist.
- Manage the cache directly with `fdoc tools {install,ensure,status}`.

## Requirements

- LuaLaTeX (via TeX Live or MacTeX)
- latexmk
- lyaml (optional, for YAML manifests): `luarocks install lyaml`

## Structure

```
latex-tools/
├── classes/          # Document classes (.cls files)
├── packages/         # LaTeX packages (.sty files)
├── lua/              # Lua modules for LuaLaTeX
├── assets/           # Shared assets (logos, etc.)
├── examples/         # Example documents
└── cli/              # fdoc CLI tool
```

## Claude Code Support

Repositories created with `fdoc init` include a generated `CLAUDE.md` file that provides Claude Code with instructions on how to use the LaTeX tools, build documents, and follow project conventions. This file is kept up to date automatically when running `fdoc init` or `fdoc update`.

A `reference/` directory is also gitignored in new repositories. This can be used to store reference documents (e.g. PDFs, specs, or notes) that you want Claude Code to be able to read during a session but that should not be committed to the repository.

## License

MIT
