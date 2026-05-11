## Create your first document

You're ready to go.

- **New repository** — run **fdoc: Initialize Documentation Repository** and pick a parent folder.
- **New document in an existing repo** — open the repo folder, then run **fdoc: Create Document**.

Both flows are also reachable from the **fdoc Documents** view in the Explorer.

Once the document is open:

- Save the `.tex` file to trigger a rebuild (LaTeX Workshop runs `latexmk` for you).
- The status bar shows the current document, revision, and a `DRAFT` flag.
- Use **fdoc: Lock Revision** when you're ready to ship — it sets `draft: false`, commits, and tags.
