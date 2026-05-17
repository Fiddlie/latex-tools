"""fdoc rev command - Manage document revisions."""

import re
import subprocess
from datetime import datetime
from pathlib import Path

import click
import yaml

from fdoc.commands.build import find_current_document
from fdoc.commands.create import find_repo_root, get_git_user_name
from fdoc.commands.list import find_documents
from fdoc.commands.name import load_manifest
from fdoc.completion import complete_docname


def resolve_document(repo_root: Path, docname: str) -> dict:
    """Resolve a document by name, supporting '.' and partial matches."""
    if docname == ".":
        doc = find_current_document(repo_root)
        if doc is None:
            raise click.ClickException(
                "Current directory is not a document folder. "
                "A document folder must contain a .tex file with the same name as the folder."
            )
        return doc

    documents = find_documents(repo_root)
    doc = next((d for d in documents if d["name"] == docname), None)

    if doc is None:
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

    return doc


class _IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def save_manifest(doc_path: Path, manifest: dict):
    """Write manifest data back to manifest.yaml."""
    manifest_file = doc_path / "manifest.yaml"
    with open(manifest_file, "w") as f:
        yaml.dump(
            manifest,
            f,
            Dumper=_IndentedDumper,
            default_flow_style=False,
            sort_keys=False,
        )


def run_git(args: list[str], cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a git command and return the result."""
    try:
        return subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        )
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Git command failed: git {' '.join(args)}\n{e.stderr.strip()}")


def increment_revision(current: str) -> str:
    """Increment a revision string intelligently.

    - Ending in a number: "A-rc1" → "A-rc2", "B-rc10" → "B-rc11"
    - Single letter: "A" → "B", "B" → "C"
    - "Z" → error
    """
    # Check if ends with a number: "A-rc1" → "A-rc2"
    match = re.match(r"^(.*?)(\d+)$", current)
    if match:
        prefix, num = match.groups()
        return f"{prefix}{int(num) + 1}"
    # Single letter: "A" → "B"
    if len(current) == 1 and current.isalpha() and current.upper() != "Z":
        return chr(ord(current) + 1)
    raise click.ClickException(
        f"Cannot automatically increment revision '{current}'. "
        "Please update the manifest manually."
    )


def _do_next_revision(repo_root: Path, doc: dict):
    """Advance a document to its next revision (shared logic for lock -n and rev next)."""
    doc_path = doc["path"]

    manifest = load_manifest(doc_path)
    if manifest is None:
        raise click.ClickException(
            f"Failed to load manifest.yaml for '{doc['name']}'."
        )

    current_revision = manifest["revision"]["current"]
    new_revision = increment_revision(current_revision)

    # Update revision
    manifest["revision"]["current"] = new_revision
    manifest["revision"]["draft"] = True

    # Get author from git config
    author = get_git_user_name()
    if author is None:
        author = "Unknown"

    # Append new history entry
    new_entry = {
        "revision": new_revision,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "author": author,
        "changes": "TODO",
    }
    if "history" not in manifest:
        manifest["history"] = []
    manifest["history"].append(new_entry)

    save_manifest(doc_path, manifest)

    click.secho(
        f"Advanced to revision {new_revision} for {doc['name']}",
        fg="green",
        bold=True,
    )


def _sync_revision_to_appsheet(manifest: dict, revision: str, config: dict):
    """Update the revision in AppSheet (non-fatal on failure)."""
    try:
        doc_id = manifest.get("document", {}).get("id", "")
        # Extract trailing number from ID like "FD-DC-LTX-00042"
        match = re.search(r"(\d+)$", doc_id)
        if not match:
            click.secho(
                f"  Warning: Could not extract document number from '{doc_id}', skipping AppSheet sync.",
                fg="yellow",
            )
            return

        doc_no = int(match.group(1))
        from fdoc.appsheet import update_document_revision
        update_document_revision(doc_no, revision, config)
        click.echo("  Updated revision in AppSheet")
    except Exception as e:
        click.secho(f"  Warning: Failed to update AppSheet: {e}", fg="yellow")


@click.group()
def rev():
    """Manage document revisions.

    Lock revisions for release or advance to the next revision.
    """
    pass


@rev.command()
@click.argument("docname", shell_complete=complete_docname)
@click.option("-p", "--push", "do_push", is_flag=True, help="Push commit and tags after locking")
@click.option("-n", "--next", "do_next", is_flag=True, help="Advance to next revision after locking")
@click.option("--sync/--no-sync", "do_sync", default=None, help="Sync with AppSheet document tracker (default: from .fdocrc)")
def lock(docname: str, do_push: bool, do_next: bool, do_sync: bool):
    """Lock a document revision for release.

    Sets draft to false, commits the change, and creates a git tag.

    DOCNAME is the folder name of the document, or "." for the current directory.

    Examples:

        fdoc rev lock my-datasheet

        fdoc rev lock my-datasheet -p

        fdoc rev lock my-datasheet -p -n
    """
    repo_root = find_repo_root()
    if repo_root is None:
        raise click.ClickException(
            "Not in a Fiddlie documentation repository. "
            "Run 'fdoc init' to create one."
        )

    # Verify working tree is clean
    result = run_git(["status", "--porcelain"], cwd=repo_root)
    if result.stdout.strip():
        raise click.ClickException(
            "Working tree has uncommitted changes. "
            "Please commit or stash your changes before locking a revision."
        )

    # Resolve document
    doc = resolve_document(repo_root, docname)
    doc_path = doc["path"]

    # Load manifest
    if not doc["has_manifest"]:
        raise click.ClickException(
            f"Document '{doc['name']}' does not have a manifest.yaml file. "
            "A manifest is required to lock a revision."
        )

    manifest = load_manifest(doc_path)
    if manifest is None:
        raise click.ClickException(
            f"Failed to load manifest.yaml for '{doc['name']}'."
        )

    revision = manifest["revision"]["current"]
    tag_name = f"{doc['name']}-{revision}"

    # Check if the current revision's changes field is still "TODO"
    history = manifest.get("history", [])
    for entry in history:
        if entry.get("revision") == revision and entry.get("changes") == "TODO":
            click.secho(
                f"Warning: The changes field for revision {revision} is still 'TODO'.",
                fg="yellow",
            )
            if not click.confirm("Continue with locking?"):
                raise click.ClickException("Aborted.")
            break

    click.echo(f"Locking revision {revision} for {doc['name']}...")

    # Set draft to false
    manifest["revision"]["draft"] = False
    save_manifest(doc_path, manifest)
    click.echo("  Set draft to false")

    # Stage and commit
    manifest_path = doc_path / "manifest.yaml"
    run_git(["add", str(manifest_path)], cwd=repo_root)
    run_git(["commit", "-m", f"Lock revision {revision} for {doc['name']}"], cwd=repo_root)
    click.echo("  Committed manifest change")

    # Create tag
    run_git(["tag", tag_name], cwd=repo_root)
    click.echo(f"  Created tag: {tag_name}")

    click.secho(f"\nRevision {revision} locked for {doc['name']}", fg="green", bold=True)

    # Sync to AppSheet if enabled
    from fdoc.config import load_config, is_sync_enabled
    config = load_config()
    if is_sync_enabled(do_sync, config):
        _sync_revision_to_appsheet(manifest, revision, config)

    # Push if requested
    if do_push:
        click.echo("\nPushing...")
        run_git(["push", "--follow-tags"], cwd=repo_root)
        click.secho("Pushed successfully", fg="green", bold=True)

    # Advance to next revision if requested
    if do_next:
        click.echo()
        _do_next_revision(repo_root, doc)


@rev.command("next")
@click.argument("docname", shell_complete=complete_docname)
def next_rev(docname: str):
    """Advance a document to its next revision.

    Increments the revision number, sets draft to true, and adds a new
    history entry. Does not commit — you commit when ready.

    Revision increment rules:
    - Single letter: A → B, B → C, ...
    - Ends in number: A-rc1 → A-rc2, B-rc10 → B-rc11

    DOCNAME is the folder name of the document, or "." for the current directory.

    Examples:

        fdoc rev next my-datasheet

        fdoc rev next .
    """
    repo_root = find_repo_root()
    if repo_root is None:
        raise click.ClickException(
            "Not in a Fiddlie documentation repository. "
            "Run 'fdoc init' to create one."
        )

    # Resolve document
    doc = resolve_document(repo_root, docname)

    # Require manifest
    if not doc["has_manifest"]:
        raise click.ClickException(
            f"Document '{doc['name']}' does not have a manifest.yaml file. "
            "A manifest is required to advance the revision."
        )

    _do_next_revision(repo_root, doc)
