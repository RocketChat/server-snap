from dataclasses import dataclass
from functools import cache
from typing import Callable, Dict, List, Set

import requests

import os

import semver


@dataclass
class ReleaseInfo:
    Tag: str
    Commit: str
    Key: str
    Etag: str
    Count: int
    NodeVersion: str
    DenoVersion: str
    CompatibleMongoVersions: list[str]
    Lts: bool

    @classmethod
    def from_dict(cls, data: dict):
        mapping = {
            "tag": "Tag",
            "commit": "Commit",
            "key": "Key",
            "etag": "Etag",
            "count": "Count",
            "nodeVersion": "NodeVersion",
            "denoVersion": "DenoVersion",
            "compatibleMongoVersions": "CompatibleMongoVersions",
            "lts": "Lts",
        }

        mapped_data = {str(mapping.get(k, k)): v for k, v in data.items()}
        return cls(**mapped_data)


@cache
def get_release_info(version: str) -> ReleaseInfo:
    response = requests.get(f"https://releases.rocket.chat/{version}/info")
    response.raise_for_status()
    return ReleaseInfo.from_dict(response.json())


@cache
def get_release_info_from_environment() -> ReleaseInfo:
    version = os.environ.get("ROCKETCHAT_VERSION", None)
    if version is None:
        raise Exception("ROCKETCHAT_VERSION environment variable is not set")
    return get_release_info(version)


def is_compatible_mongo_version_callable(
    release: ReleaseInfo,
) -> Callable[[semver.Version], bool]:
    compatible_versions: Dict[str, Set[str]] = {}

    for version in release.CompatibleMongoVersions:
        try:
            version.index(".")
        except ValueError:
            version = f"{version}.x"

        # intentional unpacking like this; should break if we at any point return patches as a compatibility gate
        [major, minor] = version.split(".")

        if major not in compatible_versions:
            compatible_versions[major] = set()
        compatible_versions[major].add(minor)

    major = lambda version: str(version.major)
    minor = lambda version: str(version.minor)

    return lambda version: major(version) in compatible_versions and (
        minor(version) in compatible_versions[major(version)]
        or compatible_versions[major(version)] == {"x"}
    )
