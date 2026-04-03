# {{ project_name }}

Fiddlie documentation repository.

## Setup

This repository uses [latex-tools](latex-tools/) as a git submodule for LaTeX document classes and packages.

After cloning, initialize the submodule:

```bash
git submodule update --init --recursive
```

## Building Documents

Each document is in its own directory. To build a document:

```bash
cd <document-folder>
latexmk <document>.tex
```

Or use the LaTeX Workshop extension in VSCode for automatic builds on save.

## Creating New Documents

Use the `fdoc` CLI tool:

```bash
fdoc create datasheet --title "Document Title" --id "FD-DC-LTX-00001"
```

## Requirements

- LuaLaTeX (via TeX Live or MacTeX)
- latexmk
- lyaml (optional, for YAML manifests): `luarocks install lyaml`
