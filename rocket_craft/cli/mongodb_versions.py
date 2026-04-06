import click

import semver

import lib.contract.mongodb_release as mdb_rel
from lib.contract.rocketchat_release import get_release_info

@click.group()
def mongodb():
    pass

def _get_next_upgradable_version(rocketchat_version: str, current_version: str) -> str:
    release = get_release_info(rocketchat_version)

    def _is_within_compatible_range(version: semver.Version) -> bool:
        return any(version.major == int(v.split(".")[0]) for v in release.CompatibleMongoVersions)

    current_mongodb_release = mdb_rel.get_mongodb_release(semver.parse_version_info(current_version))

    if current_mongodb_release.is_latest_stable():
        return current_version

    mdb_release: mdb_rel.MongoDBRelease

    # try the next major upgrade first
    try:
        mdb_release = mdb_rel.get_next_latest_major_mongodb_release(current_mongodb_release.Version)
        # found
        if _is_within_compatible_range(mdb_release.Version):
            return str(mdb_release.Version)
    except mdb_rel.NoNextMongoDBReleaseFoundError:
        pass

    # now try within current major
    try:
        mdb_release = mdb_rel.get_next_latest_mongodb_release_within_major(current_mongodb_release.Version)
        return str(mdb_release.Version)
    except mdb_rel.NoNextMongoDBReleaseFoundError:
        pass

    return current_version

@click.command()
@click.option("--rocketchat-version", type=str, required=True)
@click.option("--current-version", type=str, required=True)
def get_next_upgradable_version(rocketchat_version: str, current_version: str):
    click.echo(_get_next_upgradable_version(rocketchat_version, current_version))

mongodb.add_command(get_next_upgradable_version)
