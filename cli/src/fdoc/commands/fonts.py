"""fdoc fonts ... commands - manage FontAwesome Pro install."""
import click

from fdoc import fonts as fonts_lib


@click.group(name="fonts")
def fonts():
    """Manage the FontAwesome Pro font install."""


def _progress(msg: str) -> None:
    click.echo(f"  {msg}")


@fonts.command(name="install")
@click.option(
    "--source",
    default=None,
    help="Override default kit source (https URL, zip path, or extracted kit dir).",
)
@click.option(
    "--force",
    is_flag=True,
    help="Reinstall even if fonts are already present.",
)
def install_cmd(source, force):
    """Download and install FontAwesome Pro into TEXMFHOME."""
    if fonts_lib.is_installed() and not force:
        click.echo("FontAwesome fonts already installed. Use --force to reinstall.")
        return
    target = fonts_lib.install(source=source, force=force, on_progress=_progress)
    click.echo()
    click.secho(f"Installed into {target}", fg="green", bold=True)


@fonts.command(name="ensure")
@click.option("--source", default=None, hidden=True)
def ensure_cmd(source):
    """Install fonts only if missing (silent when already installed)."""
    did_install = fonts_lib.ensure(source=source, on_progress=_progress)
    if not did_install:
        click.echo("FontAwesome fonts already installed.")


@fonts.command(name="status")
def status_cmd():
    """Print install status and target directory."""
    target = fonts_lib.font_install_dir()
    if fonts_lib.is_installed():
        click.secho(f"Installed at {target}", fg="green")
    else:
        click.secho(f"Not installed (expected at {target})", fg="yellow")
        click.echo("Run: fdoc fonts install")
