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
pip install "git+ssh://git@github.com/Fiddlie/latex-tools.git#subdirectory=cli"

# Create a new documentation repository
fdoc init my-docs
cd my-docs

# Create a new document
fdoc create datasheet --title "My Product" --id "FD/DC/LTX/10001"
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

### latexmk Parent Directory Support

By default, `latexmk` only loads `.latexmkrc` files from the current directory or your home directory. Since documents live in subdirectories (e.g. `my-datasheet/`), you need to configure `latexmk` to search parent directories for the project-level `.latexmkrc`.

Add the following to your `~/.latexmkrc`:

```perl
# Search parent directories for project-level .latexmkrc
use File::Spec;
use Cwd 'abs_path';

my $dir = Cwd::cwd();
my $home_rc = abs_path($ENV{HOME} . "/.latexmkrc");

while ($dir ne '/') {
    my $rc = "$dir/.latexmkrc";
    if (-f $rc && abs_path($rc) ne $home_rc) {
        do $rc;
        last;
    }
    $dir = abs_path(File::Spec->catdir($dir, '..'));
}
```

This walks up from the current directory until it finds a `.latexmkrc` (that isn't the home directory one) and loads it. This ensures that running `latexmk` from within a document subdirectory picks up the project root configuration.

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

## Claude Code Support

Repositories created with `fdoc init` include a generated `CLAUDE.md` file that provides Claude Code with instructions on how to use the LaTeX tools, build documents, and follow project conventions. This file is kept up to date automatically when running `fdoc init` or `fdoc update`.

A `reference/` directory is also gitignored in new repositories. This can be used to store reference documents (e.g. PDFs, specs, or notes) that you want Claude Code to be able to read during a session but that should not be committed to the repository.

## License

MIT
