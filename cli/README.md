# fdoc - Fiddlie Documentation CLI

A command-line tool for managing Fiddlie documentation repositories and creating LaTeX documents.

## Installation

```bash
pip install "git+ssh://git@github.com/Fiddlie/latex-tools.git#subdirectory=cli"
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
- `.github/workflows/build.yml` for CI builds
- `README.md` with setup instructions

Options:

- `--submodule-url URL` - Custom git URL for latex-tools (default: git@github.com:fiddlie/latex-tools.git)
- `--no-commit` - Don't create an initial commit

### `fdoc create`

Create a new document in the current repository.

```bash
fdoc create datasheet --title "Power Supply Unit" --id "FD-DC-LTX-00001"
fdoc create requirements --title "Project Requirements" --id "FD-DC-LTX-00002"
```

Document types:

- `datasheet` - Product data sheets
- `requirements` - Requirements specification documents
- `policy` - Internal policy documents
- `report` - Engineering/research reports (`techreport` class)
- `onepager` - Single-page summaries
- `prettydoc` - Branded, public-facing briefs, guides and proposals

Options:

- `--title, -t TEXT` - Full document title (defaults to "New {Type} N")
- `--shorttitle, -s TEXT` - Short title for headers (defaults to title)
- `--author, -a TEXT` - Document author (defaults to git user.name)
- `--id TEXT` - Document ID (defaults to FD-DC-LTX-#####)
- `--no-manifest` - Use manual metadata instead of manifest.yaml
- `--template [default|empty]` - Template variant (default: default)
- `--output-dir, -o PATH` - Output directory (defaults to current directory)
- `--folder-name, -f TEXT` - Custom folder name (defaults to sanitized title)
- `--sync / --no-sync` - Enable or disable AppSheet sync (default: from `.fdocrc`)

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

This also syncs configuration files from latex-tools templates, including the GitHub Actions workflow (`.github/workflows/build.yml`).

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

- `FD-DC-LTX-10010-A - Datasheet Doc` (non-draft)
- `FD-DC-LTX-10010-B-rc2-1a2b3c - My Document` (draft)

Options:

- `--safe, -s` - Replace filename-unsafe characters (`/`, `\`, `:`, etc.) with hyphens
- `--no-spaces` - Replace all spaces with underscores

The `DOCNAME` argument can be:

- A full document folder name (e.g., `my-datasheet`)
- A partial name if unambiguous (e.g., `datasheet` if only one matches)
- `.` to use the document in the current directory

### `fdoc rev lock`

Lock a document revision for release. Sets draft to false, commits the change, and creates a git tag.

```bash
fdoc rev lock my-datasheet          # Lock current revision
fdoc rev lock my-datasheet -p       # Lock and push
fdoc rev lock my-datasheet -p -n    # Lock, push, and advance to next revision
```

This command will:

1. Verify the working tree is clean (error if uncommitted changes exist)
2. Set `revision.draft` to `false` in the manifest
3. Commit the manifest change
4. Create a git tag `{docname}-{revision}` (e.g., `my-datasheet-A`)

Options:

- `-p, --push` - Push commit and tags after locking (`git push --follow-tags`)
- `-n, --next` - Advance to the next revision after locking (and after pushing if `-p`)
- `--sync / --no-sync` - Enable or disable AppSheet sync (default: from `.fdocrc`)

### `fdoc rev next`

Advance a document to its next revision. Modifies the manifest only — does not commit.

```bash
fdoc rev next my-datasheet
fdoc rev next .
```

This command will:

1. Increment the revision number intelligently:
   - Single letter: `A` → `B`, `B` → `C`
   - Ends in number: `A-rc1` → `A-rc2`, `B-rc10` → `B-rc11`
2. Set `revision.draft` to `true`
3. Add a new entry to the revision history with the current author, date, and a placeholder changes field

### `fdoc push`

Push commits and revision tags to the remote.

```bash
fdoc push
```

Runs `git push --follow-tags` to push commits along with any revision tags.

## Shell completion

`fdoc` exposes shell completion for the `DOCNAME` argument used by `fdoc build`, `fdoc name`, `fdoc rev lock`, and `fdoc rev next`. When you press <kbd>Tab</kbd>, the completer lists document folder names found in the current repository.

Install it once with:

```bash
fdoc completion install
```

This auto-detects your shell from `$SHELL` and writes the completion script to a stable location. Per-shell behaviour:

- **fish** → installed to `~/.config/fish/completions/fdoc.fish` and auto-loaded by fish. No further setup needed; just open a new shell.
- **bash** → installed to `~/.local/share/bash-completion/completions/fdoc`. Auto-loaded by `bash-completion` ≥ 2.1. Requires bash ≥ 4.4 (macOS users: `brew install bash bash-completion@2`).
- **zsh** → installed to `~/.local/share/fdoc/fdoc.zsh`. Add `source ~/.local/share/fdoc/fdoc.zsh` to your `~/.zshrc` (the install command prints the exact line).

To target a specific shell or print the script without writing it:

```bash
fdoc completion install --shell zsh
fdoc completion install --shell bash --print > /etc/bash_completion.d/fdoc
```

Completion only returns results when you run `fdoc` from inside a Fiddlie documentation repository.

## AppSheet Integration

fdoc can sync with the Fiddlie AppSheet document tracker to auto-assign document IDs and update revision status.

### Setup

1. Get your AppSheet API key from the app's Settings > Integrations > API
2. Add it to your `~/.fdocrc`:

   ```yaml
   appsheet_api_key: "your-api-key-here"
   ```

   Or set the `FDOC_APPSHEET_API_KEY` environment variable.

3. Optionally, enable sync by default and set a project in your repo's `.fdocrc`:
   ```yaml
   sync: true
   project: "My Project Name"
   ```

### Configuration (`.fdocrc`)

fdoc searches for `.fdocrc` files in order: current directory, parent directories, then `~/.fdocrc`. Settings from nearer files take priority. Environment variables (`FDOC_APPSHEET_API_KEY`, `FDOC_APPSHEET_APP_ID`) override file config.

| Setting            | Description                                      |
| ------------------ | ------------------------------------------------ |
| `sync`             | Enable AppSheet sync by default (`true`/`false`) |
| `project`          | Default project name for this repo               |
| `appsheet_api_key` | AppSheet API access key                          |
| `appsheet_app_id`  | AppSheet app ID (has default)                    |

### Usage

Use `--sync` on supported commands, or set `sync: true` in `.fdocrc`:

```bash
# Create a document with auto-assigned ID from AppSheet
fdoc create datasheet --title "My Widget" --sync

# Lock a revision and update AppSheet
fdoc rev lock my-widget --sync
```

When creating a document with sync enabled, fdoc will prompt you to choose a project (if not set in `.fdocrc`) and offer to save it. Saving the project also enables `sync: true` in `.fdocrc` by default, so future commands sync automatically.

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
  --id "FD-DC-LTX-00542"
```

### Create a requirements document without manifest

```bash
fdoc create requirements \
  --title "Project Alpha Requirements" \
  --id "FD-DC-LTX-01234" \
  --no-manifest \
  --template empty
```

### Create a branded brief with prettydoc

```bash
fdoc create prettydoc \
  --title "Working Together, Simply" \
  --id "FD-DC-LTX-10001"
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
