"""fdoc tools ... commands - manage the versioned latex-tools runtime install."""
import sys

import click

from fdoc import tools as tools_lib
from fdoc.commands.create import find_repo_root, is_dev_checkout
from fdoc.config import get_latex_tools_version


@click.group(name="tools")
def tools():
    """Manage the pinned latex-tools runtime (classes/packages/lua/assets)."""


def _progress(msg: str) -> None:
    click.echo(f"  {msg}")


def _resolve_pinned_version() -> str:
    """Return the version pinned by the current repo, or error with guidance."""
    version = get_latex_tools_version()
    if not version:
        raise click.ClickException(
            "No latex-tools version is pinned. Run this inside a repo whose "
            ".fdocrc sets 'latex_tools_version', or pass an explicit version."
        )
    return version


@tools.command(name="install")
@click.argument("version", required=False)
@click.option(
    "--source",
    default=None,
    help="Override the bundle source (https URL, zip path, or extracted dir).",
)
@click.option("--force", is_flag=True, help="Reinstall even if already present.")
def install_cmd(version, source, force):
    """Download and install a latex-tools runtime version into the cache.

    VERSION defaults to the version pinned in the current repo's .fdocrc.
    """
    version = version or _resolve_pinned_version()
    if tools_lib.is_installed(version) and not force:
        click.echo(f"latex-tools {version} already installed. Use --force to reinstall.")
        return
    target = tools_lib.install(version, source=source, force=force, on_progress=_progress)
    click.echo()
    click.secho(f"Installed latex-tools {version} into {target}", fg="green", bold=True)


@tools.command(name="ensure")
@click.argument("version", required=False)
@click.option("--source", default=None, hidden=True)
def ensure_cmd(version, source):
    """Install a runtime version only if missing (silent when present)."""
    version = version or _resolve_pinned_version()
    did_install = tools_lib.ensure(version, source=source, on_progress=_progress)
    if not did_install:
        click.echo(f"latex-tools {version} already installed.")


@tools.command(name="status")
def status_cmd():
    """Show installed runtime versions and the version pinned here."""
    installed = tools_lib.installed_versions()
    pinned = get_latex_tools_version()
    repo_root = find_repo_root()

    if repo_root and is_dev_checkout(repo_root):
        click.secho(f"In a latex-tools checkout — builds use the working tree ({repo_root}).", fg="cyan")

    click.echo(f"Cache: {tools_lib.cache_root()}")
    if installed:
        click.echo("Installed versions:")
        for v in installed:
            mark = "  *" if v == pinned else "   "
            click.echo(f"{mark} {v}")
    else:
        click.echo("Installed versions: (none)")

    if pinned:
        state = "installed" if pinned in installed else "NOT installed"
        click.echo(f"Pinned here: {pinned} ({state})")
        if pinned not in installed:
            click.echo("Run: fdoc tools install")
    else:
        click.echo("Pinned here: (none)")


@tools.command(name="texinputs")
@click.argument("version", required=False)
def texinputs_cmd(version):
    """Print the TEXINPUTS prefix for the pinned runtime (lazy-installs it).

    Used by the generated .latexmkrc so plain `latexmk`/LaTeX Workshop builds
    resolve the pinned version. Only the prefix is written to stdout; progress
    goes to stderr so it can be captured cleanly in shell substitution.
    """
    repo_root = find_repo_root()
    # In a latex-tools checkout, build straight from the working tree.
    if repo_root is not None and is_dev_checkout(repo_root):
        click.echo(tools_lib.texinputs_for_dir(repo_root), nl=True)
        return

    version = version or get_latex_tools_version()
    if not version:
        # No pin: print nothing so .latexmkrc leaves TEXINPUTS untouched.
        return
    tools_lib.ensure(version, on_progress=lambda m: print(f"  {m}", file=sys.stderr))
    click.echo(tools_lib.texinputs(version))


@tools.command(name="bundle")
@click.option("--version", "version", default=None, help="Version label for the bundle (default: fdoc version).")
@click.option(
    "--output", "-o", "output_dir", default=".", help="Directory to write the zip into.",
)
def bundle_cmd(version, output_dir):
    """Build a runtime bundle zip from a latex-tools checkout (maintainer tool)."""
    from pathlib import Path
    from fdoc import __version__

    repo_root = find_repo_root()
    if repo_root is None or not is_dev_checkout(repo_root):
        raise click.ClickException(
            "Run this from inside a latex-tools source checkout."
        )
    version = version or __version__
    zip_path = tools_lib.make_bundle(repo_root, Path(output_dir), version)
    click.secho(f"Wrote {zip_path}", fg="green", bold=True)
