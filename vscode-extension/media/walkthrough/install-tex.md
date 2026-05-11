## Install a LaTeX distribution

fdoc builds documents with `lualatex` + `latexmk`, which come bundled with the standard distributions:

- **macOS** — install [MacTeX](https://www.tug.org/mactex/) (full) or [BasicTeX](https://www.tug.org/mactex/morepackages.html) + manual extras. Easiest via Homebrew:
  ```sh
  brew install --cask mactex
  ```
- **Linux** — install [TeX Live](https://tug.org/texlive/) from your distro (`apt install texlive-full`, `dnf install texlive-scheme-full`, …) or [tlmgr](https://www.tug.org/texlive/quickinstall.html) for the latest packages.
- **Windows** — install [TeX Live](https://tug.org/texlive/) or [MiKTeX](https://miktex.org/).

After installing, verify in a terminal:

```sh
lualatex --version
latexmk --version
```

If either command isn't found, restart VS Code so it picks up the updated PATH.
