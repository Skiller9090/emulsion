import pprint

import click
from .manager import Manager
from .sources import GithubSource
from .apply import apply_fn

manager = Manager.get()


@click.group()
def cli():
    pass


@cli.group()
def apply():
    pass


@apply.command()
@click.argument("project")
def github(project):
    manager.login()
    source = GithubSource(manager, project)
    apply_fn(source)


@cli.group()
def auth():
    pass


@auth.command()
@click.argument("token")
def github(token):
    manager.config.save_token(token)
    print("Github token saved")


if __name__ == "__main__":
    cli()
