from dataclasses import dataclass
from functools import cache
import re
import requests
import semver

from typing import List, Literal, Optional

from lib.contract._dataclass import transform, Mapping

@dataclass
class MongoDBReleaseAsset:
	Arch: str
	Distro: str
	Edition: Literal["targeted", "enterprise", "base"] # don't know what "base" is
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
			if re.compile(r".+/(mongodb-org-(unstable-)?server.+)$").match(url) is not None:
				return url

		raise Exception(f"No server package found for {self} with packages {self.Packages}")

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
		return f"MongoDBRelease(Version={self.Version}, Development={self.Development}, Candidate={self.Candidate}, Continuous={self.Continuous}, Lts={self.Lts}, Production={self.Production})"

	@classmethod
	def from_dict(cls, data: dict):
		mapping: Mapping = {
			"version": lambda x: ("Version", semver.Version.parse(x)),
			"development_release": "Development",
			"release_candidate": "Candidate",
			"continuous_release": "Continuous",
			"lts_release": "Lts",
			"production_release": "Production",
			"downloads": lambda x: ("Assets", [MongoDBReleaseAsset.from_dict(asset) for asset in x]),
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
		return self.Current

@cache
def get_mongodb_releases() -> List[MongoDBRelease]:
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
def get_mongodb_release(version: semver.Version) -> MongoDBRelease:
	releases = get_mongodb_releases()
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

def get_next_latest_mongodb_release_within_major(version: semver.Version) -> MongoDBRelease:
	releases = get_mongodb_releases()
	for release in releases:
		if not release.is_stable():
			continue

		if version.is_compatible(release.Version) and release.Version > version:
			return release
	raise NoNextMongoDBReleaseFoundError(version)


def get_next_latest_major_mongodb_release(version: semver.Version) -> MongoDBRelease:
	releases = get_mongodb_releases()
	found: Optional[MongoDBRelease] = None
	for release in releases:
		if not release.is_stable():
			continue

		if release.Version.major <= version.major:
			break

		if release.Version.major > version.major:
			found = release

	if found is None:
		raise NoNextMongoDBReleaseFoundError(version)

	return get_next_latest_mongodb_release_within_major(found.Version)
