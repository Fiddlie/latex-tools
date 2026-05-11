## LaTeX Workshop

[LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop) handles build-on-save, the integrated PDF viewer, syntax highlighting, and snippets.

It's listed as a dependency of this extension, so VS Code installs it automatically when you install fdoc. If it didn't install for some reason, you can install it manually from the marketplace.

`fdoc init` writes a `.vscode/settings.json` to each new repo that configures LaTeX Workshop to:

- run `latexmk` (which picks up the repo's `.latexmkrc`)
- rebuild on save
- show the PDF in a side tab

You shouldn't need to touch its settings — just open a `.tex` file and start typing.
