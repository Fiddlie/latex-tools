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

    Outputs document folder names, one per line. Outputs nothing if no
    documents are found. Designed for use in CI pipelines.

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

    for doc in documents:
        click.echo(doc["name"])
