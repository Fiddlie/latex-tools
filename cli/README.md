# fdoc - Fiddlie Documentation CLI

A command-line tool for managing Fiddlie documentation repositories and creating LaTeX documents.

## Installation

```bash
pip install git+ssh://git@github.com/Fiddlie/latex-tools.git
```

Or for isolated installation:

```bash
pipx install git+ssh://git@github.com/Fiddlie/latex-tools.git
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

### `fdoc list`

List all documents in the current repository.

```bash
fdoc list
```

Outputs document folder names, one per line. Outputs nothing if no documents are found. Designed for use in CI pipelines.

### `fdoc build`

Build a document using latexmk.

```bash
fdoc build my-datasheet
fdoc build .                    # Build current directory
fdoc build my-datasheet --clean # Clean before building
fdoc build my-datasheet -pvc    # Watch and rebuild on changes
```

Options:

- `--clean, -c` - Clean build artifacts before building
- `--continuous, -pvc` - Continuously watch for changes and rebuild

The `DOCNAME` argument can be:

- A full document folder name (e.g., `my-datasheet`)
- A partial name if unambiguous (e.g., `datasheet` if only one matches)
- `.` to build the document in the current directory

### `fdoc update`

Update the latex-tools submodule to the latest version.

```bash
fdoc update
fdoc update --ref v1.2.0  # Update to specific tag
fdoc update --ref main    # Update to specific branch
```

Options:

- `--ref TEXT` - Specific git ref (branch, tag, or commit) to checkout

### `fdoc name`

Generate a pretty name for a document based on its manifest metadata.

```bash
fdoc name my-datasheet
fdoc name .                          # Use current directory
fdoc name my-datasheet --safe        # Filename-safe output
fdoc name my-datasheet --no-spaces   # Replace spaces with underscores
```

The generated name format depends on whether the document is a draft:

- Non-draft: `{id}-{revision} - {title}`
- Draft: `{id}-{revision}-{commit_hash} - {title}`

Examples:

- `FD/DC/LTX/10010-A - Datasheet Doc` (non-draft)
- `FD/DC/LTX/10010-B-rc2-1a2b3c - My Document` (draft)

Options:

- `--safe, -s` - Replace filename-unsafe characters (`/`, `\`, `:`, etc.) with hyphens
- `--no-spaces` - Replace all spaces with underscores

The `DOCNAME` argument can be:

- A full document folder name (e.g., `my-datasheet`)
- A partial name if unambiguous (e.g., `datasheet` if only one matches)
- `.` to use the document in the current directory

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
  --id "FD/DC/LTX/00542"
```

### Create a requirements document without manifest

```bash
fdoc create requirements \
  --title "Project Alpha Requirements" \
  --id "FD/DC/LTX/01234" \
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
