import click

from cli import part_lifecycle, mongodb_versions, node_version, rocketchat

@click.group()
def main():
    pass

main.add_command(part_lifecycle.parts)
main.add_command(mongodb_versions.mongodb)
main.add_command(node_version.node)
main.add_command(rocketchat.rocketchat)
