from typing import Any
import click
import semver
import yaml

import lib.contract.rocketchat_release as rc_rel
from lib.contract._epoch import _Epoch
import jinja2

from .mongodb_versions import _get_next_upgradable_version

@click.group()
def rocketchat():
    pass

@click.command()
@click.option("--version", type=str, required=True)
@click.option("--current-mongodb-version", type=str, required=True)
@click.option("--work-dir", type=click.Path(), default="/tmp/work")
@click.option("--cache-dir", type=click.Path(), default="/tmp/cache")
@click.option("--craft-file", type=click.Path(exists=True))
def prepare(version: str, current_mongodb_version: str, work_dir: str, cache_dir: str, craft_file: str):
    from pathlib import Path

    parts_file_template = Path(__file__).resolve().parent.parent / "parts.yaml.jinja"

    release = rc_rel.get_release_info(version)
    next_mongodb_version = _get_next_upgradable_version(version, current_mongodb_version)
    template = jinja2.Template(open(parts_file_template).read())
    rendered = template.render(mongodb_version=next_mongodb_version, novm_node_version=release.NodeVersion)
    parts_file_rendered = parts_file_template.parent / f"parts-{version}.yaml"
    with open(parts_file_rendered, "w") as f:
        f.write(rendered)


    from .part_lifecycle import _run

    # checks before passing to snapcraft
    _run("prime", parts_file_rendered, work_dir, cache_dir)


    craft_file_data: dict[str, Any]

    with open(craft_file, "r") as f:
        craft_file_data = yaml.safe_load(f)

    if not semver.parse_version_info(next_mongodb_version).is_compatible(semver.parse_version_info(current_mongodb_version)):
        click.echo("next_mongodb_version is not compatible with current_mongodb_version, incrementing epoch")
        current_epoch = _Epoch(craft_file_data["epoch"])
        craft_file_data["epoch"] = str(current_epoch + 1)
        migration_path = Path(craft_file).parent.parent / "migrations" / "pre_refresh" / "feature_compatibility" / "00-adopt_version.sh"
        if not migration_path.exists():
            raise click.ClickException(f"{migration_path.as_posix()} does not exist, please enable it")
        click.echo("ensuring mongodb upgrade migration is enabled " + migration_path.as_posix())
        migration_path.chmod(0o755)

    craft_file_data["version"] = version

    with open(craft_file, "w") as f:
        yaml.dump(craft_file_data, f, default_flow_style=False)
    click.echo("craft file updated")


rocketchat.add_command(prepare)
