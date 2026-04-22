import click

import lib.contract.rocketchat_release as rc_rel

@click.group()
def node():
    pass

@click.command()
@click.option("--rocketchat-version", type=str, required=True)
def get_node_version(rocketchat_version: str):
    release = rc_rel.get_release_info(rocketchat_version)
    click.echo(release.NodeVersion)

node.add_command(get_node_version)
