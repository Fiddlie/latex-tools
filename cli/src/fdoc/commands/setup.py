"""fdoc setup command - one-step environment setup for building documents.

Installs everything a machine needs to build Fiddlie documents — the
FontAwesome Pro fonts, the pinned latex-tools runtime, and (best-effort)
shell completion — in a single, idempotent, mostly-silent step.

This is what the bundled installer runs on first use: pointed at the
fonts/runtime payloads shipped inside the installer (via --fonts-source /
--runtime-source), it seeds everything offline with no downloads and no
private-repo access.
"""
import click

from fdoc.commands.create import find_repo_root, is_dev_checkout
from fdoc.config import get_latex_tools_version


@click.command()
@click.option(
    "--version",
    default=None,
    help="latex-tools runtime version (default: the repo pin, else this fdoc's version).",
)
@click.option(
    "--fonts-source",
    default=None,
    help="Local path/URL for the FontAwesome kit (default: download, or $FDOC_FA_KIT_SOURCE).",
)
@click.option(
    "--runtime-source",
    default=None,
    help="Local path/URL for the runtime bundle (default: download, or $FDOC_LATEX_TOOLS_SOURCE).",
)
@click.option("--no-completion", is_flag=True, help="Skip installing shell completion.")
@click.option("--force", is_flag=True, help="Reinstall fonts/runtime even if present.")
@click.option("-q", "--quiet", is_flag=True, help="Only print warnings and the final status.")
def setup(version, fonts_source, runtime_source, no_completion, force, quiet):
    """Set up this machine to build Fiddlie documents (fonts + runtime + completion).

    Safe to re-run: each piece is skipped when already present (unless --force).

    Examples:

        fdoc setup
        fdoc setup --fonts-source ./payload/fa-kit.zip --runtime-source ./payload/runtime.zip
    """
    from fdoc import __version__
    from fdoc import fonts as fonts_lib
    from fdoc import tools as tools_lib

    def say(msg: str):
        if not quiet:
            click.echo(msg)

    repo_root = find_repo_root()
    if version is None:
        version = get_latex_tools_version() or __version__

    say("Setting up fdoc...")

    # 1. FontAwesome Pro fonts (required by every document).
    say("  FontAwesome fonts...")
    if force and fonts_lib.is_installed():
        fonts_lib.install(source=fonts_source, force=True, on_progress=lambda m: say(f"    {m}"))
    else:
        if not fonts_lib.ensure(source=fonts_source, on_progress=lambda m: say(f"    {m}")):
            say("    already installed")

    # 2. latex-tools runtime. In a source checkout the working tree is used,
    #    so there is nothing to install.
    if repo_root is not None and is_dev_checkout(repo_root):
        say("  latex-tools runtime: using working tree (source checkout)")
    else:
        say(f"  latex-tools runtime {version}...")
        if force and tools_lib.is_installed(version):
            tools_lib.install(version, source=runtime_source, force=True,
                              on_progress=lambda m: say(f"    {m}"))
        else:
            if not tools_lib.ensure(version, source=runtime_source,
                                    on_progress=lambda m: say(f"    {m}")):
                say("    already installed")

    # 3. Shell completion (best-effort — never fail setup over this).
    if not no_completion:
        say("  Shell completion...")
        try:
            from fdoc.commands.completion import install as completion_install

            completion_install.callback(shell=None, print_only=False)
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001 - completion is a nicety
            say(f"    skipped ({e})")

    click.secho("fdoc is ready. Build a document with: fdoc build .", fg="green", bold=True)
