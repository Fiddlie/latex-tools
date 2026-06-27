"""fdoc update command - bump the pinned latex-tools version (and migrate)."""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from fdoc.commands.create import find_legacy_submodule, find_repo_root
from fdoc.templates import get_template


@click.command()
@click.option(
    "--to",
    "to_version",
    default=None,
    help="latex-tools version to pin (default: this fdoc's version)",
)
def update(to_version: Optional[str]):
    """Update the pinned latex-tools version and sync generated files.

    If the repo still has a legacy `latex-tools/` submodule, this migrates it
    to the pinned-install model: the submodule is removed and the version is
    recorded in .fdocrc instead.

    Examples:

        fdoc update                 # pin this fdoc's version
        fdoc update --to 2.1.0      # pin a specific version
    """
    from fdoc import __version__
    from fdoc import tools as tools_lib
    from fdoc.config import get_latex_tools_version, set_latex_tools_version

    repo_root = find_repo_root()
    if repo_root is None:
        raise click.ClickException(
            "Not in a Fiddlie documentation repository. "
            "Run 'fdoc init' to create one."
        )

    legacy = find_legacy_submodule(repo_root)
    migrated = False

    if legacy is not None:
        # Prefer the version the submodule was actually at (if tagged), else
        # fall back to an explicit --to, else this fdoc's version.
        target = to_version or _submodule_version(legacy) or __version__
        click.echo("Migrating from the latex-tools submodule to a pinned install...")
        _remove_submodule(repo_root, legacy)
        click.echo("  Removed latex-tools submodule")
        migrated = True
    else:
        target = to_version or __version__
        current = get_latex_tools_version()
        if current:
            click.echo(f"Updating latex-tools pin: {current} -> {target}")
        else:
            click.echo(f"Pinning latex-tools {target}")

    # Record the pin.
    set_latex_tools_version(repo_root, target)
    click.echo(f"  Pinned latex-tools {target} in .fdocrc")

    # Sync generated files from templates.
    click.echo("  Syncing configuration files...")
    _sync_latexmkrc(repo_root)
    _sync_github_workflow(repo_root)
    _sync_claude_guide(repo_root, target)

    # Install the pinned runtime + fonts so the next build is ready.
    click.echo(f"  Installing latex-tools {target} runtime...")
    try:
        tools_lib.ensure(target, on_progress=lambda m: click.echo(f"    {m}"))
    except Exception as e:  # noqa: BLE001 - install is best-effort here
        click.secho(
            f"    Could not install runtime now ({e}). "
            "It will install on your next 'fdoc build'.",
            fg="yellow",
        )

    from fdoc import fonts as fonts_lib
    click.echo("  Checking FontAwesome icon fonts...")
    fonts_lib.ensure(on_progress=lambda m: click.echo(f"    {m}"))

    click.echo()
    click.secho("Successfully updated latex-tools!", fg="green", bold=True)
    click.echo()
    click.echo("Don't forget to commit the changes:")
    if migrated:
        click.echo("  git add -A")
        click.echo('  git commit -m "Migrate to pinned latex-tools install"')
    else:
        click.echo("  git add .fdocrc .latexmkrc .github/workflows/build.yml CLAUDE.md")
        click.echo(f'  git commit -m "Update latex-tools to {target}"')


def _run_git(args: list, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in the specified directory."""
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def _submodule_version(submodule_path: Path) -> Optional[str]:
    """Return the submodule's checked-out version from its git tag, if any.

    Looks for a tag like vX.Y.Z; returns the bare X.Y.Z. None if untagged.
    """
    try:
        result = _run_git(
            ["describe", "--tags", "--exact-match"], cwd=submodule_path, check=False
        )
        tag = result.stdout.strip()
    except Exception:
        return None
    if not tag:
        return None
    return tag[1:] if tag.startswith("v") else tag


def _remove_submodule(repo_root: Path, submodule_path: Path) -> None:
    """Remove a `latex-tools` submodule (or plain vendored dir) from the repo."""
    rel = submodule_path.name  # "latex-tools"

    # Best-effort submodule deinit; ignore failure (may be a plain directory).
    _run_git(["submodule", "deinit", "-f", "--", rel], cwd=repo_root, check=False)

    # Remove from the index + working tree. Fall back to cached-only + rmtree.
    rm = _run_git(["rm", "-rf", rel], cwd=repo_root, check=False)
    if rm.returncode != 0:
        _run_git(["rm", "-r", "--cached", rel], cwd=repo_root, check=False)
        if submodule_path.exists():
            shutil.rmtree(submodule_path, ignore_errors=True)

    # Drop the stored submodule git dir.
    modules_dir = repo_root / ".git" / "modules" / rel
    if modules_dir.exists():
        shutil.rmtree(modules_dir, ignore_errors=True)

    # Remove the .gitmodules entry; delete the file if it's now empty.
    gitmodules = repo_root / ".gitmodules"
    if gitmodules.is_file():
        _run_git(
            ["config", "-f", ".gitmodules", "--remove-section", f"submodule.{rel}"],
            cwd=repo_root,
            check=False,
        )
        remaining = gitmodules.read_text().strip()
        if remaining:
            _run_git(["add", ".gitmodules"], cwd=repo_root, check=False)
        else:
            _run_git(["rm", "-f", ".gitmodules"], cwd=repo_root, check=False)
            if gitmodules.exists():
                gitmodules.unlink()


def _sync_latexmkrc(repo_root: Path):
    """Rewrite .latexmkrc from the current template (pinned-runtime resolver)."""
    (repo_root / ".latexmkrc").write_text(get_template("latexmkrc.txt"))


def _sync_github_workflow(repo_root: Path):
    """Sync the GitHub Actions workflow from the latex-tools templates."""
    workflows_dir = repo_root / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    content = get_template("github_workflow.yml")
    (workflows_dir / "build.yml").write_text(content)


def _sync_claude_guide(repo_root: Path, version: str):
    """Sync the CLAUDE.md file while preserving custom content."""
    from jinja2 import Template
    from fdoc.tools import docs_base_url

    claude_md_path = repo_root / "CLAUDE.md"

    # Extract custom section if file exists
    custom_content = None
    if claude_md_path.exists():
        existing_content = claude_md_path.read_text()

        custom_start = "<!-- CUSTOM SECTION START -->"
        custom_end = "<!-- CUSTOM SECTION END -->"

        if custom_start in existing_content and custom_end in existing_content:
            start_idx = existing_content.find(custom_start)
            end_idx = existing_content.find(custom_end) + len(custom_end)
            custom_content = existing_content[start_idx:end_idx]
        else:
            managed_end = "<!-- MANAGED SECTION END -->"
            if managed_end in existing_content:
                end_idx = existing_content.find(managed_end) + len(managed_end)
                legacy_content = existing_content[end_idx:].strip()
                if legacy_content:
                    custom_content = f"""\n\n{custom_start}

## Repository-Specific Guidelines

<!-- Legacy content preserved from previous CLAUDE.md -->

{legacy_content}

{custom_end}
"""

    template_content = get_template("claude_guide.md")
    template = Template(template_content)
    update_date = datetime.now().strftime("%Y-%m-%d")
    new_content = template.render(
        update_date=update_date, docs_base=docs_base_url(version)
    )

    if custom_content:
        custom_start = "<!-- CUSTOM SECTION START -->"
        custom_end = "<!-- CUSTOM SECTION END -->"
        start_idx = new_content.find(custom_start)
        end_idx = new_content.find(custom_end) + len(custom_end)
        if start_idx != -1 and end_idx != -1:
            new_content = new_content[:start_idx] + custom_content + new_content[end_idx:]

    claude_md_path.write_text(new_content)
