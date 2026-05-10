"""fdoc projects command - List AppSheet projects."""

import click


@click.group()
def projects():
    """Inspect AppSheet projects.

    Useful for scripts and tooling that need to populate project
    pickers without prompting interactively.
    """
    pass


@projects.command("list")
def list_cmd():
    """List active AppSheet project names, one per line.

    Designed for piping into selectors. Outputs nothing if no
    projects are available. Requires AppSheet credentials in
    ~/.fdocrc or FDOC_APPSHEET_API_KEY.
    """
    from fdoc.appsheet import get_active_projects
    from fdoc.config import load_config

    config = load_config()
    for project in get_active_projects(config):
        name = project.get("Name")
        if name:
            click.echo(name)
