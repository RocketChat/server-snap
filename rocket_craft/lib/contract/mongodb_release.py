from dataclasses import dataclass
from functools import cache
import re
from typing_extensions import override
import requests
import semver

from typing import Dict, List, Literal, Optional, Callable

from lib.contract._dataclass import transform, Mapping


@dataclass
class MongoDBReleaseAsset:
    Arch: str
    Distro: str
    Edition: Literal["targeted", "enterprise", "base"]  # don't know what "base" is
    Packages: Optional[List[str]] = None

    def __str__(self) -> str:
        return f"MongoDBReleaseAsset(Arch={self.Arch}, Distro={self.Distro}, Edition={self.Edition})"

    def is_community(self) -> bool:
        return self.Edition == "targeted"

    def is_enterprise(self) -> bool:
        return self.Edition == "enterprise"

    def get_server_package_url(self) -> str:
        if self.Packages is None:
            raise Exception(f"No packages found for {self}")

        for url in self.Packages:
            if (
                re.compile(r".+/(mongodb-org-(unstable-)?server.+)$").match(url)
                is not None
            ):
                return url

        raise Exception(
            f"No server package found for {self} with packages {self.Packages}"
        )

    @classmethod
    def from_dict(cls, data: dict):
        mapping: Mapping = {
            "arch": "Arch",
            "target": "Distro",
            "edition": "Edition",
            "packages": "Packages",
        }

        try:
            mapped_data = transform(data, mapping)
            return cls(**mapped_data)
        except Exception:
            return None


@dataclass
class MongoDBRelease:
    Version: semver.Version
    Development: bool
    Candidate: bool
    Continuous: bool
    Lts: bool
    Production: bool
    Current: bool
    Assets: List[MongoDBReleaseAsset]

    def __str__(self) -> str:
        return f"MongoDBRelease(Version={self.Version}, Development={self.Development}, Candidate={self.Candidate}, Continuous={self.Continuous}, Lts={self.Lts}, Production={self.Production} Current={self.Current})"

    @classmethod
    def from_dict(cls, data: dict):
        mapping: Mapping = {
            "version": lambda x: ("Version", semver.Version.parse(x)),
            "development_release": "Development",
            "release_candidate": "Candidate",
            "continuous_release": "Continuous",
            "lts_release": "Lts",
            "production_release": "Production",
            "downloads": lambda x: (
                "Assets",
                [MongoDBReleaseAsset.from_dict(asset) for asset in x],
            ),
            "current": "Current",
        }

        try:
            mapped_data = transform(data, mapping)
            return cls(**mapped_data)
        except Exception:
            return None

    def is_stable(self) -> bool:
        return not self.Candidate and self.Version.prerelease is None

    def is_latest_stable(self) -> bool:
        return False
        # TODO: uncomment this when we have a way to get the latest stable version, seems Current is not reliable or I don't understand the meaning of it
        # return self.Current


@cache
def get_mongodb_releases_or_throw() -> List[MongoDBRelease]:
    response = requests.get("https://downloads.mongodb.org/full.json")
    response.raise_for_status()

    data = response.json()

    assert "versions" in data

    releases: List[MongoDBRelease] = []
    for release in data["versions"]:
        r = MongoDBRelease.from_dict(release)
        if r is not None:
            releases.append(r)

    releases.sort(key=lambda x: x.Version, reverse=True)

    return releases


@cache
def get_mongodb_release_or_throw(version: semver.Version) -> MongoDBRelease:
    releases = get_mongodb_releases_or_throw()
    for release in releases:
        if release.Version == version:
            return release
    raise NoMongoDBReleaseFoundError(version)


class NoMongoDBReleaseFoundError(Exception):
    def __init__(self, version: semver.Version):
        super().__init__(f"No MongoDB release found for version {version}")


class NoNextMongoDBReleaseFoundError(Exception):
    def __init__(self, version: semver.Version):
        super().__init__(f"No next MongoDB release found for version {version}")


# function name keywords
# next_{semver_type} | max_{semver_type}
# max_{semver_type} | min_{semver_type} | same_{semver_type}_line {1,2}
# or_throw


def _get_candidates(
    is_candidate: Callable[[MongoDBRelease], bool],
) -> List[MongoDBRelease]:
    releases = get_mongodb_releases_or_throw()
    is_stable = lambda r: r.is_stable()
    filters = [is_stable, is_candidate]
    predicate = lambda r: all(f(r) for f in filters)
    candidates: List[MongoDBRelease] = []
    for release in releases:
        if predicate(release):
            candidates.append(release)
    return candidates


def get_next_major_min_minor_max_patch_or_throw(
    version: semver.Version,
) -> MongoDBRelease:
    candidates = _get_candidates(lambda r: r.Version.major == version.major + 1)
    if not candidates:
        raise NoNextMongoDBReleaseFoundError(version)
    min_minor = min(r.Version.minor for r in candidates)
    min_minor_line = [r for r in candidates if r.Version.minor == min_minor]
    return max(min_minor_line, key=lambda r: r.Version)


def get_max_minor_max_patch_same_major_line_or_throw(
    version: semver.Version,
) -> MongoDBRelease:
    candidates = _get_candidates(lambda r: r.Version.major == version.major)
    if not candidates:
        raise NoNextMongoDBReleaseFoundError(version)
    return max(candidates, key=lambda r: r.Version)


def get_next_minor_max_patch_same_major_line_or_throw(
    version: semver.Version,
) -> MongoDBRelease:
    candidates = _get_candidates(
        lambda r: r.Version.major == version.major
        and r.Version.minor == version.minor + 1
    )
    if not candidates:
        raise NoNextMongoDBReleaseFoundError(version)
    return max(candidates, key=lambda r: r.Version)


def get_next_upgradable_version_or_throw(version: semver.Version) -> MongoDBRelease:
    release = get_mongodb_release_or_throw(version)
    if release.is_latest_stable():
        return release
    try:
        next_major = get_next_major_min_minor_max_patch_or_throw(release.Version)
        assert next_major.is_stable()
        return next_major
    except NoNextMongoDBReleaseFoundError:
        # try the same major line, max version
        # throw if must
        max_same_major_line = get_max_minor_max_patch_same_major_line_or_throw(
            release.Version
        )
        assert max_same_major_line.is_stable()
        return max_same_major_line
