# fdoc — VS Code extension

A friendly UI for the `fdoc` CLI. Lets team members create, build, and ship Fiddlie LaTeX docs without touching a terminal.

## What it does

- **Initialize a docs repo** — `fdoc: Initialize Documentation Repository` prompts for a name and parent folder, runs `fdoc init`, then offers to open the new project.
- **Create a document** — guided picker for type, template, title, and ID (with format validation). Opens the new `.tex` file when done.
- **Build documents** — context-menu actions on the **fdoc Documents** tree, or `fdoc: Build Document`. Streams `latexmk` output to the **fdoc** output channel; "Clean and Build" runs with `--clean`.
- **Build-on-save** — handled by [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop), which is listed as an extension dependency. `fdoc init` writes the right `.vscode/settings.json` to wire it up.
- **Revision management** — Lock, advance, and AppSheet-sync revisions from the document context menu.
- **Commit a document** — stages just that document folder, prompts for a message, optionally pushes with `--follow-tags`.
- **Push / update submodule** — one-click commands for `fdoc push` and `fdoc update`.

## Requirements

- **fdoc CLI** installed and on `PATH` (or set `fdoc.cliPath`):
  ```bash
  pipx install "git+ssh://git@github.com/Fiddlie/latex-tools.git#subdirectory=cli"
  ```
- **LaTeX Workshop** (installed automatically as an extension dependency).
- **TeX Live / MacTeX** with `latexmk` and LuaLaTeX.
- **git** on `PATH`.

## Settings

| Setting                    | Default     | Purpose                                            |
| -------------------------- | ----------- | -------------------------------------------------- |
| `fdoc.cliPath`             | `fdoc`      | Path to the `fdoc` executable.                     |
| `fdoc.python`              | `python3`   | Used in the install hint when fdoc is missing.     |
| `fdoc.confirmPush`         | `true`      | Confirm before `fdoc push`.                        |
| `fdoc.defaultPushOnLock`   | `false`     | Default to `--push` when locking a revision.       |

## AppSheet sync

The extension passes `--no-sync` for `create` and `rev lock` to avoid the CLI's interactive project picker. To use AppSheet:

1. Set `appsheet_api_key` in `~/.fdocrc`.
2. Set `project: "Your Project"` and `sync: true` in the repo's `.fdocrc`.
3. Use **fdoc: Sync Revision with AppSheet** to push revision state to the tracker.

(A future version may move the project picker into VS Code's QuickPick.)

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

## Limitations / known gaps

- Interactive AppSheet project selection isn't wired through VS Code yet — relies on `.fdocrc`.
- The "advance revision" command modifies the manifest only; commit it via **fdoc: Commit Document Changes**.
- Build-on-save uses LaTeX Workshop's recipe rather than `fdoc build`; the recipe is configured by `fdoc init`.
