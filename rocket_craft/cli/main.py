import click

from cli import part_lifecycle, mongodb_versions, node_version, rocketchat


@click.group()
def rocketcraft():
    pass


rocketcraft.add_command(part_lifecycle.parts)
rocketcraft.add_command(mongodb_versions.mongodb)
rocketcraft.add_command(node_version.node)
rocketcraft.add_command(rocketchat.rocketchat)
