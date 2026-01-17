"""Main CLI entry point for fdoc."""

import click

from fdoc import __version__
from fdoc.commands.init import init
from fdoc.commands.create import create


@click.group()
@click.version_option(version=__version__, prog_name="fdoc")
def cli():
    """fdoc - Fiddlie Documentation CLI

    A tool for managing Fiddlie documentation repositories and creating
    LaTeX documents using Fiddlie document classes.
    """
    pass


cli.add_command(init)
cli.add_command(create)


if __name__ == "__main__":
    cli()
