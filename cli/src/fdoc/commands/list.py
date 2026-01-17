"""fdoc list command - List all documents in the repository."""

from pathlib import Path
from typing import Optional

import click

from fdoc.commands.create import DOCUMENT_TYPES, find_repo_root


def find_documents(repo_root: Path) -> list[dict]:
    """Find all document folders in the repository.

    A document folder is identified by containing a .tex file with the same
    name as the folder (e.g., my-doc/my-doc.tex).

    Returns:
        List of dicts with 'name', 'path', 'type', and 'has_manifest' keys.
    """
    documents = []

    # Search for document folders
    for item in repo_root.iterdir():
        if not item.is_dir():
            continue
        # Skip hidden folders and known non-document folders
        if item.name.startswith(".") or item.name in ("latex-tools", "output"):
            continue

        # Check if this looks like a document folder
        tex_file = item / f"{item.name}.tex"
        if tex_file.exists():
            doc_info = {
                "name": item.name,
                "path": item,
                "type": _detect_document_type(tex_file),
                "has_manifest": (item / "manifest.yaml").exists(),
            }
            documents.append(doc_info)

    return sorted(documents, key=lambda d: d["name"])


def _detect_document_type(tex_file: Path) -> Optional[str]:
    """Detect the document type from the .tex file content."""
    try:
        content = tex_file.read_text()
        for doctype in DOCUMENT_TYPES:
            # Look for documentclass usage
            if f"fiddlie-{doctype}" in content:
                return doctype
        return None
    except Exception:
        return None


@click.command("list")
def list_cmd():
    """List all documents in the current repository.

    Searches the repository for document folders and displays their names,
    types, and whether they use a manifest file.

    Example:

        fdoc list
    """
    repo_root = find_repo_root()
    if repo_root is None:
        raise click.ClickException(
            "Not in a Fiddlie documentation repository. "
            "Run 'fdoc init' to create one."
        )

    documents = find_documents(repo_root)

    if not documents:
        click.echo("No documents found in this repository.")
        click.echo()
        click.echo("Create a new document with:")
        click.echo("  fdoc create datasheet --title \"My Document\"")
        return

    click.echo(f"Found {len(documents)} document(s) in {repo_root.name}/")
    click.echo()

    # Calculate column widths
    name_width = max(len(d["name"]) for d in documents)
    name_width = max(name_width, 4)  # Minimum width for "NAME"

    # Header
    click.echo(f"  {'NAME':<{name_width}}  {'TYPE':<12}  MANIFEST")
    click.echo(f"  {'-' * name_width}  {'-' * 12}  --------")

    # Document rows
    for doc in documents:
        doc_type = doc["type"] or "unknown"
        manifest = "yes" if doc["has_manifest"] else "no"
        click.echo(f"  {doc['name']:<{name_width}}  {doc_type:<12}  {manifest}")
