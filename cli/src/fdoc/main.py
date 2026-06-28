"""Main CLI entry point for fdoc."""

import click

from fdoc import __version__
from fdoc.commands.init import init
from fdoc.commands.create import create
from fdoc.commands.list import list_cmd
from fdoc.commands.build import build
from fdoc.commands.update import update
from fdoc.commands.name import name
from fdoc.commands.rev import rev
from fdoc.commands.push import push
from fdoc.commands.completion import completion
from fdoc.commands.fonts import fonts
from fdoc.commands.tools import tools
from fdoc.commands.setup import setup


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
cli.add_command(list_cmd, name="list")
cli.add_command(build)
cli.add_command(update)
cli.add_command(name)
cli.add_command(rev)
cli.add_command(push)
cli.add_command(completion)
cli.add_command(fonts)
cli.add_command(tools)
cli.add_command(setup)


if __name__ == "__main__":
    cli()
