# fdoc — VS Code extension

A friendly UI for the `fdoc` CLI. Lets team members create, build, and ship Fiddlie LaTeX docs without touching a terminal.

## What it does

### Repository & document management
- **fdoc: Initialize Documentation Repository** — prompts for a name and parent folder, runs `fdoc init`, then offers to open the new project.
- **fdoc: Create Document** — guided picker for type, template, title, and ID. **Auto-assign from AppSheet** fetches the project list via `fdoc projects list` and passes `--project` so there are no terminal prompts.
- **fdoc: Build Document** / **Build All Documents** / **Clean and Build** / **Open Built PDF** — streams `latexmk` output to the **fdoc** output channel.
- **fdoc: Open Manifest** / **Reveal Document Folder** — jump straight to `manifest.yaml` or open the folder in Finder/Explorer.
- **Build-on-save** — handled by LaTeX Workshop (installed as an extension dependency). `fdoc init` writes the right `.vscode/settings.json` to wire it up.

### Editor integration
- **Editor title bar** — Build and Open PDF buttons appear on any `.tex` file inside an fdoc document folder.
- **Status bar** — shows the current document, revision, and a `DRAFT` flag when active. Click it to build.
- **`manifest.yaml` schema** — autocomplete and validation for the manifest format (requires the Red Hat YAML extension, which most teams already use).

### Revision management
- **Lock Revision**, **Advance to Next Revision**, **Sync Revision with AppSheet** — all from the **fdoc Documents** tree's context menu or the Command Palette.

### Git
- **Commit Document Changes** — stages just one document's folder, prompts for a message, optionally pushes with `--follow-tags`.
- **Push / Pull** — one-click commands that include submodule sync.
- Document folders in the tree get **M** (modified) and **D** (draft) badges.

### AppSheet
- **fdoc: Configure AppSheet Credentials** — paste your API key once. The extension writes `~/.fdocrc` for you (chmod 600).

### Submodule freshness
- Once per day per repo, the extension fetches the `latex-tools` submodule's remote and offers to run `fdoc update` if you're behind. Disable with `fdoc.checkSubmoduleUpdates`.

## Walkthrough

A built-in setup walkthrough covers: installing TeX Live/MacTeX/MiKTeX, installing Python 3.9+ with pipx, installing the fdoc CLI, the bundled LaTeX Workshop extension, and connecting to AppSheet. Open it via **fdoc: Open Setup Walkthrough** or VS Code's **Get Started** page.

## Requirements

- **fdoc CLI** installed and on `PATH` (or set `fdoc.cliPath`):
  ```bash
  pipx install "git+ssh://git@github.com/Fiddlie/latex-tools.git#subdirectory=cli"
  ```
- **LaTeX Workshop** (installed automatically as an extension dependency).
- **TeX Live / MacTeX / MiKTeX** with `latexmk` and LuaLaTeX.
- **git** on `PATH`.
- **Python 3.9+** (for the CLI).

## Settings

| Setting                          | Default     | Purpose                                                       |
| -------------------------------- | ----------- | ------------------------------------------------------------- |
| `fdoc.cliPath`                   | `fdoc`      | Path to the `fdoc` executable.                                |
| `fdoc.python`                    | `python3`   | Used in the install hint when fdoc is missing.                |
| `fdoc.confirmPush`               | `true`      | Confirm before `fdoc push`.                                   |
| `fdoc.defaultPushOnLock`         | `false`     | Default to `--push` when locking a revision.                  |
| `fdoc.checkSubmoduleUpdates`     | `true`      | Daily check that the latex-tools submodule is up to date.     |

## Develop

```bash
cd vscode-extension
npm install
npm run compile
# F5 in VS Code to launch an Extension Development Host
```

## Package a private VSIX

```bash
npm run package
# produces fdoc.vsix; share with the team or host on a private feed
```

Install with: `code --install-extension fdoc.vsix`.
