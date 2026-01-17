"""fdoc init command - Initialize a new documentation repository."""

import re
import subprocess
from pathlib import Path

import click

from fdoc.templates import get_template

LATEX_TOOLS_REPO = "git@github.com:fiddlie/latex-tools.git"


def validate_folder_name(ctx, param, value):
    """Validate folder name doesn't contain problematic characters."""
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise click.BadParameter(
            "Folder name must contain only letters, numbers, hyphens, and underscores"
        )
    return value


@click.command()
@click.argument("folder_name", callback=validate_folder_name)
@click.option(
    "--submodule-url",
    default=LATEX_TOOLS_REPO,
    help="Git URL for the latex-tools submodule",
    show_default=True,
)
@click.option(
    "--no-commit",
    is_flag=True,
    help="Don't create an initial commit",
)
def init(folder_name: str, submodule_url: str, no_commit: bool):
    """Initialize a new Fiddlie documentation repository.

    Creates a new directory with git initialized, latex-tools as a submodule,
    and all necessary configuration files for building LaTeX documents.

    Example:

        fdoc init my-project-docs
    """
    folder_path = Path.cwd() / folder_name

    # Check if folder already exists
    if folder_path.exists():
        raise click.ClickException(f"Directory '{folder_name}' already exists")

    click.echo(f"Creating documentation repository: {folder_name}")

    try:
        # Create directory
        folder_path.mkdir(parents=True)
        click.echo(f"  Created directory: {folder_path}")

        # Initialize git
        _run_git(["init"], cwd=folder_path)
        click.echo("  Initialized git repository")

        # Add latex-tools submodule
        click.echo("  Adding latex-tools submodule...")
        _run_git(
            ["submodule", "add", submodule_url, "latex-tools"],
            cwd=folder_path,
        )
        click.echo("  Added latex-tools submodule")

        # Write configuration files
        _write_gitignore(folder_path)
        click.echo("  Created .gitignore")

        _write_latexmkrc(folder_path)
        click.echo("  Created .latexmkrc")

        _write_vscode_settings(folder_path)
        click.echo("  Created .vscode/settings.json")

        _write_readme(folder_path, folder_name)
        click.echo("  Created README.md")

        # Create initial commit
        if not no_commit:
            _run_git(["add", "."], cwd=folder_path)
            _run_git(
                ["commit", "-m", "Initial commit: Set up documentation repository"],
                cwd=folder_path,
            )
            click.echo("  Created initial commit")

        click.echo()
        click.secho(f"Successfully created '{folder_name}'!", fg="green", bold=True)
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  cd {folder_name}")
        click.echo("  fdoc create datasheet --title \"My Document\" --id \"FD/DOC/001\"")

    except subprocess.CalledProcessError as e:
        # Clean up on failure
        if folder_path.exists():
            import shutil
            shutil.rmtree(folder_path)
        raise click.ClickException(f"Git command failed: {e}")
    except Exception as e:
        # Clean up on failure
        if folder_path.exists():
            import shutil
            shutil.rmtree(folder_path)
        raise click.ClickException(f"Failed to create repository: {e}")


def _run_git(args: list, cwd: Path) -> subprocess.CompletedProcess:
    """Run a git command in the specified directory."""
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _write_gitignore(folder_path: Path):
    """Write the .gitignore file for LaTeX projects."""
    content = get_template("gitignore.txt")
    (folder_path / ".gitignore").write_text(content)


def _write_latexmkrc(folder_path: Path):
    """Write the .latexmkrc file."""
    content = get_template("latexmkrc.txt")
    (folder_path / ".latexmkrc").write_text(content)


def _write_vscode_settings(folder_path: Path):
    """Write VSCode settings for LaTeX Workshop."""
    vscode_dir = folder_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    content = get_template("vscode_settings.json")
    (vscode_dir / "settings.json").write_text(content)


def _write_readme(folder_path: Path, project_name: str):
    """Write a basic README.md file."""
    from jinja2 import Template
    template_content = get_template("repo_readme.md")
    template = Template(template_content)
    content = template.render(project_name=project_name)
    (folder_path / "README.md").write_text(content)
