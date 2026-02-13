"""fdoc update command - Update latex-tools in the repository."""

import subprocess
from datetime import datetime
from pathlib import Path

import click

from fdoc.commands.create import find_repo_root
from fdoc.templates import get_template


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

        # Sync configuration files from templates
        click.echo("  Syncing configuration files...")
        _sync_github_workflow(repo_root)
        _sync_claude_guide(repo_root)

        click.echo()
        click.secho("Successfully updated latex-tools!", fg="green", bold=True)
        if commit_info:
            click.echo(f"  Now at: {commit_info}")
        click.echo()
        click.echo("Don't forget to commit the changes:")
        click.echo("  git add latex-tools .github/workflows/build.yml CLAUDE*.md")
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


def _sync_github_workflow(repo_root: Path):
    """Sync the GitHub Actions workflow from the latex-tools templates."""
    workflows_dir = repo_root / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    content = get_template("github_workflow.yml")
    (workflows_dir / "build.yml").write_text(content)


def _sync_claude_guide(repo_root: Path):
    """Sync the CLAUDE.md files while preserving custom content in main file."""
    from jinja2 import Template

    # Sync main CLAUDE.md with custom content preservation
    claude_md_path = repo_root / "CLAUDE.md"

    # Extract custom section if file exists
    custom_content = None
    if claude_md_path.exists():
        existing_content = claude_md_path.read_text()

        # Try to extract content between custom section markers
        custom_start = "<!-- CUSTOM SECTION START -->"
        custom_end = "<!-- CUSTOM SECTION END -->"

        if custom_start in existing_content and custom_end in existing_content:
            # Extract custom section
            start_idx = existing_content.find(custom_start)
            end_idx = existing_content.find(custom_end) + len(custom_end)
            custom_content = existing_content[start_idx:end_idx]
        else:
            # No markers found - preserve entire file as legacy custom content
            managed_end = "<!-- MANAGED SECTION END -->"
            if managed_end in existing_content:
                # Has managed section marker but missing custom markers
                # Extract everything after managed section
                end_idx = existing_content.find(managed_end) + len(managed_end)
                legacy_content = existing_content[end_idx:].strip()
                if legacy_content:
                    custom_content = f"""\n\n{custom_start}

## Repository-Specific Guidelines

<!-- Legacy content preserved from previous CLAUDE.md -->

{legacy_content}

{custom_end}
"""

    # Generate new managed section
    template_content = get_template("claude_guide.md")
    template = Template(template_content)
    update_date = datetime.now().strftime("%Y-%m-%d")
    new_content = template.render(update_date=update_date)

    # If we have custom content, replace the default custom section
    if custom_content:
        # Remove the default custom section from the template
        custom_start = "<!-- CUSTOM SECTION START -->"
        custom_end = "<!-- CUSTOM SECTION END -->"

        start_idx = new_content.find(custom_start)
        end_idx = new_content.find(custom_end) + len(custom_end)

        if start_idx != -1 and end_idx != -1:
            # Replace default custom section with preserved content
            new_content = new_content[:start_idx] + custom_content + new_content[end_idx:]

    # Write the main CLAUDE.md file
    claude_md_path.write_text(new_content)

    # Sync reference guides (these are always overwritten)
    datasheet_content = get_template("claude_guide_datasheet.md")
    (repo_root / "CLAUDE_DATASHEET.md").write_text(datasheet_content)

    requirements_content = get_template("claude_guide_requirements.md")
    (repo_root / "CLAUDE_REQUIREMENTS.md").write_text(requirements_content)

    manifest_content = get_template("claude_guide_manifest.md")
    (repo_root / "CLAUDE_MANIFEST.md").write_text(manifest_content)
