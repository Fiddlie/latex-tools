"""fdoc completion command - Install shell completion scripts."""

import os
from pathlib import Path

import click
from click.shell_completion import BashComplete, FishComplete, ZshComplete

SHELLS = {"bash": BashComplete, "zsh": ZshComplete, "fish": FishComplete}


@click.group()
def completion():
    """Manage shell completion for fdoc."""


@completion.command("install")
@click.option(
    "--shell",
    type=click.Choice(sorted(SHELLS)),
    default=None,
    help="Target shell (auto-detected from $SHELL if not given).",
)
@click.option(
    "--print",
    "print_only",
    is_flag=True,
    help="Print the completion script to stdout instead of writing a file.",
)
def install(shell, print_only):
    """Install the shell completion script.

    Auto-detects the current shell from $SHELL. Writes the completion script
    to a well-known location and prints any extra setup needed.

    Examples:

        fdoc completion install

        fdoc completion install --shell zsh

        fdoc completion install --print --shell bash > /etc/bash_completion.d/fdoc
    """
    if shell is None:
        shell = Path(os.environ.get("SHELL", "")).name
        if shell not in SHELLS:
            raise click.ClickException(
                "Could not detect shell from $SHELL. Pass --shell explicitly "
                f"(one of: {', '.join(sorted(SHELLS))})."
            )

    from fdoc.main import cli
    script = SHELLS[shell](cli, {}, "fdoc", "_FDOC_COMPLETE").source()

    if print_only:
        click.echo(script)
        return

    home = Path.home()
    if shell == "fish":
        path = home / ".config/fish/completions/fdoc.fish"
        hint = None
    elif shell == "bash":
        # XDG location auto-loaded by bash-completion >= 2.1 on Linux.
        # On macOS, the user typically needs Homebrew bash + bash-completion@2.
        path = home / ".local/share/bash-completion/completions/fdoc"
        hint = (
            "If completion doesn't work in a new shell, ensure bash >= 4.4 and the\n"
            "bash-completion package are installed (on macOS: brew install bash bash-completion@2)."
        )
    else:  # zsh — no XDG auto-load for sourced scripts, so user must source it.
        path = home / ".local/share/fdoc/fdoc.zsh"
        hint = f"Add the following line to your ~/.zshrc:\n\n    source {path}"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script)

    click.secho(f"Installed {shell} completion to {path}", fg="green", bold=True)
    if hint is None:
        click.echo("Restart your shell (or open a new terminal) to activate it.")
    else:
        click.echo()
        click.echo(hint)
