"""fdoc build command - Build a specific document."""

import os
import subprocess
from pathlib import Path
from typing import Optional

import click

from fdoc.commands.create import (
    find_legacy_submodule,
    find_repo_root,
    is_dev_checkout,
)
from fdoc.commands.list import find_documents
from fdoc.completion import complete_docname


def _build_env(repo_root: Path) -> dict:
    """Return an environment for latexmk with the latex-tools runtime on TEXINPUTS.

    Resolution order:
    - latex-tools source checkout -> build from the working tree;
    - pinned version in .fdocrc   -> lazy-install and use that version;
    - legacy `latex-tools/` submodule -> use it (back-compat, suggest migrating).
    """
    from fdoc import tools as tools_lib
    from fdoc.config import get_latex_tools_version

    env = os.environ.copy()
    prefix: Optional[str] = None

    if is_dev_checkout(repo_root):
        prefix = tools_lib.texinputs_for_dir(repo_root)
    else:
        version = get_latex_tools_version()
        legacy = find_legacy_submodule(repo_root)
        if version:
            tools_lib.ensure(version, on_progress=lambda m: click.echo(f"  {m}"))
            prefix = tools_lib.texinputs(version)
        elif legacy is not None:
            click.secho(
                "  Using legacy latex-tools submodule. Run 'fdoc update' to "
                "migrate to a pinned install.",
                fg="yellow",
            )
            prefix = tools_lib.texinputs_for_dir(legacy)
        else:
            raise click.ClickException(
                "No latex-tools runtime found. This repo has no "
                "'latex_tools_version' pin in .fdocrc and no latex-tools "
                "submodule. Run 'fdoc update' to set up a pinned install."
            )

    if prefix:
        env["TEXINPUTS"] = prefix + env.get("TEXINPUTS", "")
    return env


def find_current_document(repo_root: Path) -> Optional[dict]:
    """Check if the current directory is a document folder.

    Returns document info dict if cwd is a document folder, None otherwise.
    """
    cwd = Path.cwd()
    tex_file = cwd / f"{cwd.name}.tex"

    if tex_file.exists():
        # We're in a document folder
        from fdoc.commands.list import _detect_document_type
        return {
            "name": cwd.name,
            "path": cwd,
            "type": _detect_document_type(tex_file),
            "has_manifest": (cwd / "manifest.yaml").exists(),
        }
    return None


@click.command()
@click.argument("docname", shell_complete=complete_docname)
@click.option(
    "--clean", "-c",
    is_flag=True,
    help="Clean build artifacts before building",
)
@click.option(
    "--continuous", "-pvc",
    is_flag=True,
    help="Continuously watch for changes and rebuild",
)
def build(docname: str, clean: bool, continuous: bool):
    """Build a document by name.

    DOCNAME is the folder name of the document to build, or "." to build
    the current directory if it's a document folder.

    Uses latexmk with the repository's .latexmkrc configuration.

    Examples:

        fdoc build my-datasheet

        fdoc build .

        fdoc build my-datasheet --clean

        fdoc build my-datasheet --continuous
    """
    repo_root = find_repo_root()
    if repo_root is None:
        raise click.ClickException(
            "Not in a Fiddlie documentation repository. "
            "Run 'fdoc init' to create one."
        )

    # Handle "." to build current directory
    if docname == ".":
        doc = find_current_document(repo_root)
        if doc is None:
            raise click.ClickException(
                "Current directory is not a document folder. "
                "A document folder must contain a .tex file with the same name as the folder."
            )
    else:
        # Find the document by name
        documents = find_documents(repo_root)
        doc = next((d for d in documents if d["name"] == docname), None)

        if doc is None:
            # Try partial match
            matches = [d for d in documents if docname in d["name"]]
            if len(matches) == 1:
                doc = matches[0]
            elif len(matches) > 1:
                click.echo(f"Multiple documents match '{docname}':")
                for m in matches:
                    click.echo(f"  {m['name']}")
                raise click.ClickException("Please specify the full document name.")
            else:
                click.echo(f"Document '{docname}' not found.")
                click.echo()
                if documents:
                    click.echo("Available documents:")
                    for d in documents:
                        click.echo(f"  {d['name']}")
                else:
                    click.echo("No documents found in this repository.")
                raise click.ClickException("Document not found.")

    # Lazy-install FontAwesome fonts on first build of a machine. Silent
    # when already installed; downloads + extracts (~62MB) otherwise.
    from fdoc import fonts as fonts_lib
    fonts_lib.ensure(on_progress=lambda m: click.echo(f"  {m}"))

    # Resolve the latex-tools runtime and make it available to latexmk via
    # TEXINPUTS, so a build works regardless of what .latexmkrc does.
    build_env = _build_env(repo_root)

    doc_path = doc["path"]
    tex_file = f"{doc['name']}.tex"

    click.echo(f"Building {doc['name']}...")

    # Build latexmk command
    cmd = ["latexmk"]

    if clean:
        # Run clean first
        clean_cmd = ["latexmk", "-C", tex_file]
        click.echo("  Cleaning build artifacts...")
        subprocess.run(clean_cmd, cwd=doc_path, check=False, env=build_env)

    if continuous:
        cmd.append("-pvc")

    cmd.append(tex_file)

    # Run latexmk
    try:
        result = subprocess.run(
            cmd,
            cwd=doc_path,
            check=False,
            env=build_env,
        )
        if result.returncode == 0:
            pdf_file = doc_path / f"{doc['name']}.pdf"
            if pdf_file.exists():
                click.echo()
                click.secho(f"Successfully built {doc['name']}.pdf", fg="green", bold=True)
        else:
            raise click.ClickException(f"Build failed with exit code {result.returncode}")
    except FileNotFoundError:
        raise click.ClickException(
            "latexmk not found. Please install TeX Live or MacTeX."
        )
