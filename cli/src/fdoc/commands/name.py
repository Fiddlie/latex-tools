"""fdoc name command - Generate a pretty name for a document."""

import subprocess
from pathlib import Path
from typing import Optional

import click
import yaml

from fdoc.commands.create import find_repo_root
from fdoc.commands.list import find_documents
from fdoc.commands.build import find_current_document
from fdoc.completion import complete_docname


def load_manifest(doc_path: Path) -> Optional[dict]:
    """Load and parse the manifest.yaml file from a document folder."""
    manifest_file = doc_path / "manifest.yaml"
    if not manifest_file.exists():
        return None
    try:
        with open(manifest_file) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def get_git_short_hash(doc_path: Path) -> Optional[str]:
    """Get the abbreviated git commit hash for the document directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=doc_path,
        )
        return result.stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def generate_document_name(
    doc_id: str,
    revision: str,
    is_draft: bool,
    title: str,
    commit_hash: Optional[str],
) -> str:
    """Generate the pretty document name.

    Format:
    - Non-draft: "{id}-{revision} - {title}"
    - Draft: "{id}-{revision}-{commit_hash} - {title}"
    """
    if is_draft and commit_hash:
        return f"{doc_id}-{revision}-{commit_hash} - {title}"
    else:
        return f"{doc_id}-{revision} - {title}"


def make_filename_safe(name: str) -> str:
    """Replace characters that can't be used in filenames with hyphens."""
    # Characters not allowed in filenames on various OS
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    result = name
    for char in unsafe_chars:
        result = result.replace(char, '-')
    return result


def replace_spaces(name: str) -> str:
    """Replace all spaces with underscores."""
    return name.replace(' ', '_')


@click.command()
@click.argument("docname", shell_complete=complete_docname)
@click.option(
    "--safe", "-s",
    is_flag=True,
    help="Replace characters that can't be used in filenames with hyphens",
)
@click.option(
    "--no-spaces",
    is_flag=True,
    help="Replace all spaces with underscores",
)
def name(docname: str, safe: bool, no_spaces: bool):
    """Generate a pretty name for a document.

    DOCNAME is the folder name of the document, or "." for the current directory.

    The generated name format is:
    - Non-draft: "{id}-{revision} - {title}"
    - Draft: "{id}-{revision}-{commit_hash} - {title}"

    Examples:

        fdoc name my-datasheet

        fdoc name .

        fdoc name my-datasheet --safe

        fdoc name my-datasheet --no-spaces

        fdoc name my-datasheet --safe --no-spaces
    """
    repo_root = find_repo_root()
    if repo_root is None:
        raise click.ClickException(
            "Not in a Fiddlie documentation repository. "
            "Run 'fdoc init' to create one."
        )

    # Handle "." to use current directory
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

    doc_path = doc["path"]

    # Load manifest
    if not doc["has_manifest"]:
        raise click.ClickException(
            f"Document '{doc['name']}' does not have a manifest.yaml file. "
            "The name command requires a manifest to read document metadata."
        )

    manifest = load_manifest(doc_path)
    if manifest is None:
        raise click.ClickException(
            f"Failed to load manifest.yaml for '{doc['name']}'."
        )

    # Extract required fields
    try:
        doc_id = manifest["document"]["id"]
        title = manifest["document"]["title"]
        revision = manifest["revision"]["current"]
        is_draft = manifest["revision"].get("draft", False)
    except KeyError as e:
        raise click.ClickException(
            f"Missing required field in manifest.yaml: {e}"
        )

    # Get commit hash for drafts
    commit_hash = None
    if is_draft:
        commit_hash = get_git_short_hash(doc_path)

    # Generate the name
    result = generate_document_name(doc_id, revision, is_draft, title, commit_hash)

    # Apply transformations
    if safe:
        result = make_filename_safe(result)
    if no_spaces:
        result = replace_spaces(result)

    click.echo(result)
