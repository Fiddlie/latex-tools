"""fdoc push command - Push commits and revision tags to the remote."""

import subprocess

import click


@click.command()
def push():
    """Push commits and revision tags to the remote.

    Runs 'git push --follow-tags' to push commits along with any
    annotated or revision tags.

    Examples:

        fdoc push
    """
    click.echo("Pushing commits and tags...")
    try:
        subprocess.run(
            ["git", "push", "--follow-tags"],
            check=True,
        )
        click.secho("Pushed successfully", fg="green", bold=True)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Push failed with exit code {e.returncode}")
