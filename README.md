# Fiddlie LaTeX Tools

LaTeX document classes and packages for Fiddlie documentation.

## Document Classes

- **[datasheet](classes/datasheet.README.md)** - Professional product data sheets
- **[requirements](classes/requirements.README.md)** - Structured requirements specification documents

## Usage

This repository is designed to be used as a git submodule in documentation repositories.

### Quick Start with fdoc CLI

The easiest way to get started is with the [`fdoc` CLI tool](cli/README.md):

```bash
# Install the CLI
pip install git+ssh://git@github.com/Fiddlie/latex-tools.git

# Create a new documentation repository
fdoc init my-docs
cd my-docs

# Create a new document
fdoc create datasheet --title "My Product" --id "FD/DC/001"
```

### Manual Setup

1. Add this repository as a submodule:

   ```bash
   git submodule add git@github.com:fiddlie/latex-tools.git latex-tools
   ```

2. Create a `.latexmkrc` in your project root:

   ```perl
   use File::Basename;
   use File::Spec;

   my $root_dir = dirname(File::Spec->rel2abs(__FILE__));
   my $latex_tools = "$root_dir/latex-tools";
   $ENV{'TEXINPUTS'} = "$latex_tools/classes//:$latex_tools/packages//:$latex_tools/lua//:" . ($ENV{'TEXINPUTS'} // '');

   $pdf_mode = 4;  # Use LuaLaTeX
   $lualatex = 'lualatex -interaction=nonstopmode -synctex=1 -shell-escape %O %S';
   ```

3. Create your document using the document class:
   ```latex
   \documentclass{datasheet}
   % ... your content
   ```

## Requirements

- LuaLaTeX (via TeX Live or MacTeX)
- latexmk
- lyaml (optional, for YAML manifests): `luarocks install lyaml`

## Structure

```
latex-tools/
├── classes/          # Document classes (.cls files)
├── packages/         # LaTeX packages (.sty files)
├── lua/              # Lua modules for LuaLaTeX
├── assets/           # Shared assets (logos, etc.)
├── examples/         # Example documents
└── cli/              # fdoc CLI tool
```

## License

MIT
