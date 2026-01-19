"""fdoc create command - Create a new document in the repository."""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from jinja2 import Template

from fdoc.templates import get_template, list_templates

# Available document types and their display names
DOCUMENT_TYPES = ["datasheet", "requirements"]
DOCUMENT_TYPE_NAMES = {
    "datasheet": "Datasheet",
    "requirements": "Requirements",
}


def get_git_user_name() -> Optional[str]:
    """Get the user's name from git config."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def sanitize_folder_name(title: str) -> str:
    """Convert a title into a valid folder name."""
    # Convert to lowercase
    name = title.lower()
    # Replace spaces and special chars with hyphens
    name = re.sub(r'[^a-z0-9]+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Collapse multiple hyphens
    name = re.sub(r'-+', '-', name)
    return name


def get_next_document_number(output_dir: Path, doctype: str) -> int:
    """Find the next available document number for default naming."""
    pattern = re.compile(rf'^new-{doctype}-(\d+)$', re.IGNORECASE)

    max_num = 0
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir():
                match = pattern.match(item.name)
                if match:
                    max_num = max(max_num, int(match.group(1)))

    return max_num + 1


def find_repo_root() -> Optional[Path]:
    """Find the root of the documentation repository.

    Looks for a directory containing either:
    - A 'latex-tools' subdirectory (submodule)
    - A 'classes' subdirectory (we're inside latex-tools itself)
    """
    current = Path.cwd()

    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        # Check for latex-tools submodule
        if (parent / "latex-tools" / "classes").is_dir():
            return parent
        # Check if we're inside latex-tools itself (for development)
        if (parent / "classes").is_dir() and (parent / "packages").is_dir():
            return parent

    return None


@click.command()
@click.argument("doctype", type=click.Choice(DOCUMENT_TYPES, case_sensitive=False))
@click.option(
    "--title", "-t",
    default=None,
    help="Full document title (defaults to 'New {Type} N')",
)
@click.option(
    "--shorttitle", "-s",
    default=None,
    help="Short title for headers (defaults to title)",
)
@click.option(
    "--author", "-a",
    default=None,
    help="Document author (defaults to git user.name)",
)
@click.option(
    "--id", "document_id",
    default=None,
    help="Document ID (defaults to FD/DC/LTX/?????)",
)
@click.option(
    "--no-manifest",
    is_flag=True,
    help="Use manual metadata instead of manifest.yaml",
)
@click.option(
    "--template",
    "template_name",
    type=click.Choice(["default", "empty"], case_sensitive=False),
    default="default",
    help="Template variant to use",
    show_default=True,
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory (defaults to current directory)",
)
@click.option(
    "--folder-name", "-f",
    default=None,
    help="Custom folder name (defaults to sanitized title)",
)
def create(
    doctype: str,
    title: Optional[str],
    shorttitle: Optional[str],
    author: Optional[str],
    document_id: Optional[str],
    no_manifest: bool,
    template_name: str,
    output_dir: Optional[Path],
    folder_name: Optional[str],
):
    """Create a new document in the documentation repository.

    DOCTYPE is the type of document to create: datasheet or requirements

    Examples:

        fdoc create datasheet --title "Power Supply Unit" --id "FD/DC/LTX/00001"

        fdoc create requirements --title "Project Requirements" --id "FD/DC/LTX/00001" --no-manifest

        fdoc create datasheet  # Creates "New Datasheet 1" with default ID
    """
    # Determine output directory
    if output_dir is None:
        output_dir = Path.cwd()

    # Check if we're in a valid repo (optional warning)
    repo_root = find_repo_root()
    if repo_root is None:
        click.secho(
            "Warning: Not in a Fiddlie documentation repository. "
            "The document may not compile correctly.",
            fg="yellow",
        )

    # Generate default title if not provided
    if title is None:
        doc_num = get_next_document_number(output_dir, doctype)
        type_name = DOCUMENT_TYPE_NAMES[doctype]
        title = f"New {type_name} {doc_num}"

    # Generate default document ID if not provided
    if document_id is None:
        document_id = "FD/DC/LTX/#####"

    # Determine folder name
    if folder_name is None:
        folder_name = sanitize_folder_name(title)

    doc_folder = output_dir / folder_name

    # Check if folder exists
    if doc_folder.exists():
        raise click.ClickException(f"Directory '{folder_name}' already exists")

    # Get author from git if not provided
    if author is None:
        author = get_git_user_name()
        if author is None:
            raise click.ClickException(
                "Could not determine author. Please provide --author or configure git user.name"
            )

    # Default shorttitle to title
    if shorttitle is None:
        shorttitle = title

    # Prepare template context
    context = {
        "title": title,
        "shorttitle": shorttitle,
        "author": author,
        "date": datetime.now().strftime("%d %b %Y"),
        "document_id": document_id,
        "revision": "A-rc1",
        "doctype": doctype,
    }

    click.echo(f"Creating {doctype} document: {title}")

    try:
        # Create document folder
        doc_folder.mkdir(parents=True)
        click.echo(f"  Created directory: {folder_name}/")

        # Determine filename based on folder name
        tex_filename = f"{folder_name}.tex"

        # Write manifest.yaml if not --no-manifest
        if not no_manifest:
            manifest_content = _render_template(
                f"{doctype}/manifest.yaml.j2",
                context,
            )
            (doc_folder / "manifest.yaml").write_text(manifest_content)
            click.echo("  Created manifest.yaml")

        # Write .tex file
        if no_manifest:
            tex_template = f"{doctype}/{template_name}_no_manifest.tex.j2"
        else:
            tex_template = f"{doctype}/{template_name}.tex.j2"

        tex_content = _render_template(tex_template, {**context, "filename": tex_filename})
        (doc_folder / tex_filename).write_text(tex_content)
        click.echo(f"  Created {tex_filename}")

        click.echo()
        click.secho(f"Successfully created '{folder_name}'!", fg="green", bold=True)
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  cd {folder_name}")
        click.echo(f"  latexmk {tex_filename}")

    except Exception as e:
        # Clean up on failure
        if doc_folder.exists():
            import shutil
            shutil.rmtree(doc_folder)
        raise click.ClickException(f"Failed to create document: {e}")


def _render_template(template_path: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    template_content = get_template(template_path)
    template = Template(template_content)
    return template.render(**context)
