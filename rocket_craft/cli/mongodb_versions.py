import click

import semver

import lib.contract.mongodb_release as mdb
from lib.contract.rocketchat_release import (
    get_release_info,
    is_compatible_mongo_version_callable,
)


@click.group()
def mongodb():
    pass


def _get_next_upgradable_version(rocketchat_version: str, current_version: str) -> str:
    release = get_release_info(rocketchat_version)

    is_compatible_mongo_version = is_compatible_mongo_version_callable(release)

    v = semver.Version.parse(current_version)
    current = mdb.get_mongodb_release_or_throw(v)
    if current.is_latest_stable():
        return current_version

    # sucks but yeah a valid version might not have assets returned in their api;
    # can return NoMongoDBReleaseFoundError if we run out of versions; can't help
    def __return_with_assets(release: mdb.MongoDBRelease) -> str:
        while len(release.Assets) == 0:
            if release.Version.patch == 0:
                raise mdb.NoMongoDBReleaseFoundError(release.Version)

            v = release.Version.replace(patch=release.Version.patch - 1)

            release = mdb.get_mongodb_release_or_throw(v)
        return str(release.Version)

    next_upgradable = mdb.get_next_upgradable_version_or_throw(v)
    # we ignore NoNextMongoDBReleaseFoundError here because v
    # not finding an upgradable version means the current version is the latest stable
    # but that should have been caught by L-8 already; something is wrong to indicate
    # current version is not the latest stable but also being unable to find the
    # next upgradable version

    if is_compatible_mongo_version(next_upgradable.Version):
        return __return_with_assets(next_upgradable)

    if not is_compatible_mongo_version(current.Version):
        # current not supported, next either; we can not upgrade
        raise Exception(
            f"Current MongoDB version {current_version} is not supported by Rocket.Chat version {rocketchat_version}, nor is the next upgradable version {next_upgradable.Version}, can not proceed"
        )

    # default calculation is not within compatible range;
    # next_upgradable will have at most major+1
    # we need a versiion that is in the middle of current and next_upgradable
    all_mongo_releases = mdb.get_mongodb_releases_or_throw()
    in_range = [
        r
        for r in all_mongo_releases
        if r.Version >= current.Version and r.Version < next_upgradable.Version
    ]
    candidates_descending = sorted(in_range, key=lambda r: r.Version, reverse=True)
    for candidate in candidates_descending:
        if is_compatible_mongo_version(candidate.Version):
            return __return_with_assets(candidate)
    raise Exception(
        f"No compatible MongoDB version found between {current.Version} and {next_upgradable.Version}"
    )


@click.command()
@click.option("--rocketchat-version", type=str, required=True)
@click.option("--current-version", type=str, required=True)
def get_next_upgradable_version(rocketchat_version: str, current_version: str):
    click.echo(_get_next_upgradable_version(rocketchat_version, current_version))


@click.command()
@click.argument("version", type=str)
def info(version: str):
    v = semver.Version.parse(version)
    release = mdb.get_mongodb_release_or_throw(v)
    click.echo(release)


@click.command()
@click.argument("version", type=str)
@click.option("--distro", type=str, required=True)
def assets(version: str, distro: str):
    v = semver.Version.parse(version)
    release = mdb.get_mongodb_release_or_throw(v)
    for asset in release.Assets:
        if distro != "" and asset.Distro == distro:
            click.echo(asset)


mongodb.add_command(get_next_upgradable_version)
mongodb.add_command(info)
mongodb.add_command(assets)
