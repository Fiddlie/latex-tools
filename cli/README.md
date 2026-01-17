# fdoc - Fiddlie Documentation CLI

A command-line tool for managing Fiddlie documentation repositories and creating LaTeX documents.

## Installation

```bash
pip install fdoc
```

Or for isolated installation:

```bash
pipx install fdoc
```

## Commands

### `fdoc init`

Initialize a new documentation repository with latex-tools as a submodule.

```bash
fdoc init my-project-docs
```

This creates:

- A new directory with git initialized
- latex-tools as a git submodule
- `.gitignore` for LaTeX artifacts
- `.latexmkrc` configured for the submodule
- `.vscode/settings.json` for LaTeX Workshop
- `README.md` with setup instructions

Options:

- `--submodule-url URL` - Custom git URL for latex-tools (default: git@github.com:fiddlie/latex-tools.git)
- `--no-commit` - Don't create an initial commit

### `fdoc create`

Create a new document in the current repository.

```bash
fdoc create datasheet --title "Power Supply Unit" --id "FD/DC/PSU/001"
fdoc create requirements --title "Project Requirements" --id "FD/REQ/001"
```

Document types:

- `datasheet` - Product data sheets
- `requirements` - Requirements specification documents

Options:

- `--title, -t TEXT` - Full document title (defaults to "New {Type} N")
- `--shorttitle, -s TEXT` - Short title for headers (defaults to title)
- `--author, -a TEXT` - Document author (defaults to git user.name)
- `--id TEXT` - Document ID (defaults to FD/DC/LTX/#####)
- `--no-manifest` - Use manual metadata instead of manifest.yaml
- `--template [default|empty]` - Template variant (default: default)
- `--output-dir, -o PATH` - Output directory (defaults to current directory)
- `--folder-name, -f TEXT` - Custom folder name (defaults to sanitized title)

## Examples

### Create a new documentation repository

```bash
fdoc init acme-docs
cd acme-docs
```

### Quick-start a new datasheet

```bash
fdoc create datasheet
# Creates "New Datasheet 1" with default ID
```

### Create a datasheet with custom title and ID

```bash
fdoc create datasheet \
  --title "ACME Power Module PM-500" \
  --id "FD/DC/PM/500"
```

### Create a requirements document without manifest

```bash
fdoc create requirements \
  --title "Project Alpha Requirements" \
  --id "FD/REQ/ALPHA/001" \
  --no-manifest \
  --template empty
```

## Requirements

- Python 3.9+
- Git
- LuaLaTeX (for building documents, we recommend TeXLive)
- latexmk (for building documents)

## Development

Install in development mode:

```bash
cd cli
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```
