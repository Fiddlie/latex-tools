"""fdoc update command - Update latex-tools in the repository."""

import subprocess
from pathlib import Path

import click

from fdoc.commands.create import find_repo_root


@click.command()
@click.option(
    "--ref",
    default=None,
    help="Specific git ref (branch, tag, or commit) to checkout",
)
def update(ref: str):
    """Update the latex-tools submodule to the latest version.

    Pulls the latest changes from the latex-tools remote repository
    and updates the submodule reference.

    Examples:

        fdoc update

        fdoc update --ref v1.2.0

        fdoc update --ref main
    """
    repo_root = find_repo_root()
    if repo_root is None:
        raise click.ClickException(
            "Not in a Fiddlie documentation repository. "
            "Run 'fdoc init' to create one."
        )

    latex_tools_path = repo_root / "latex-tools"
    if not latex_tools_path.is_dir():
        raise click.ClickException(
            "latex-tools submodule not found. "
            "This repository may not be properly initialized."
        )

    click.echo("Updating latex-tools...")

    try:
        # Fetch latest from remote
        click.echo("  Fetching from remote...")
        _run_git(["fetch", "origin"], cwd=latex_tools_path)

        if ref:
            # Checkout specific ref
            click.echo(f"  Checking out {ref}...")
            _run_git(["checkout", ref], cwd=latex_tools_path)
        else:
            # Get the current branch or default to main
            current_branch = _get_current_branch(latex_tools_path)
            if current_branch:
                click.echo(f"  Pulling latest {current_branch}...")
                _run_git(["pull", "origin", current_branch], cwd=latex_tools_path)
            else:
                # Detached HEAD - checkout main and pull
                click.echo("  Checking out main branch...")
                _run_git(["checkout", "main"], cwd=latex_tools_path)
                _run_git(["pull", "origin", "main"], cwd=latex_tools_path)

        # Get the new commit info
        commit_info = _get_commit_info(latex_tools_path)

        click.echo()
        click.secho("Successfully updated latex-tools!", fg="green", bold=True)
        if commit_info:
            click.echo(f"  Now at: {commit_info}")
        click.echo()
        click.echo("Don't forget to commit the submodule update:")
        click.echo("  git add latex-tools")
        click.echo('  git commit -m "Update latex-tools"')

    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Git command failed: {e.stderr or e}")


def _run_git(args: list, cwd: Path) -> subprocess.CompletedProcess:
    """Run a git command in the specified directory."""
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _get_current_branch(repo_path: Path) -> str | None:
    """Get the current branch name, or None if in detached HEAD state."""
    try:
        result = _run_git(["symbolic-ref", "--short", "HEAD"], cwd=repo_path)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def _get_commit_info(repo_path: Path) -> str | None:
    """Get a short description of the current commit."""
    try:
        result = _run_git(
            ["log", "-1", "--format=%h %s"],
            cwd=repo_path,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
