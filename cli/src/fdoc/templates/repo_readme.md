# {{ project_name }}

Fiddlie documentation repository.

## Setup

This repository uses the [`fdoc`](https://github.com/fiddlie/latex-tools) CLI
for LaTeX document classes and packages. latex-tools is **not** vendored as a
submodule — instead the version is pinned in `.fdocrc` (`latex_tools_version`),
and `fdoc` installs that version's runtime on demand (cached per machine).

After cloning, install the CLI and the pinned runtime:

```bash
pip install "git+https://github.com/fiddlie/latex-tools.git#subdirectory=cli"
fdoc tools install   # installs the runtime pinned in .fdocrc
```

`fdoc build` also installs the pinned runtime (and fonts) automatically on
first use, so this step is optional if you build via `fdoc`.

## Building Documents

Each document is in its own directory. The recommended way to build:

```bash
cd <document-folder>
fdoc build .
```

Plain `latexmk <document>.tex` and the LaTeX Workshop extension also work —
the generated `.latexmkrc` asks `fdoc` for the pinned runtime's location.

## Creating New Documents

Use the `fdoc` CLI tool:

```bash
fdoc create datasheet --title "Document Title" --id "FD-DC-LTX-00001"
```

## Updating latex-tools

```bash
fdoc update --to <version>   # bump the pin in .fdocrc, then commit it
```

## Requirements

- The `fdoc` CLI (`pip install …#subdirectory=cli`)
- LuaLaTeX (via TeX Live or MacTeX)
- latexmk
- lyaml (optional, for YAML manifests): `luarocks install lyaml`
