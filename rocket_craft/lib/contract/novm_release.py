from dataclasses import dataclass
from functools import cache
import platform
from typing import List

import requests
import semver

_MACHINE_TO_GOARCH = {
	"x86_64": "amd64",
	"aarch64": "arm64",
	"armv7l": "arm",
	"i686": "386",
	"riscv64": "riscv64",
	"s390x": "s390x",
}

def get_goos() -> str:
    return "linux"

def get_goarch() -> str:
	machine = platform.machine().lower()
	return _MACHINE_TO_GOARCH.get(machine, machine)

@dataclass(frozen=True)
class NovmReleaseAsset:
    Os: str
    Arch: str
    DownloadUrl: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(Os=data["os"], Arch=data["arch"], DownloadUrl=data["download_url"])


@dataclass(frozen=True)
class NovmRelease:
    Version: semver.Version
    Assets: List[NovmReleaseAsset]

    @classmethod
    def from_dict(cls, data: dict):
        version = data["tag"]
        if version.startswith("v"):
            version = version[1:]
        return cls(
            Version=semver.Version.parse(version),
            Assets=[NovmReleaseAsset.from_dict(asset) for asset in data["assets"]],
        )

    def get_asset(self, platform: str, arch: str) -> NovmReleaseAsset:
        for asset in self.Assets:
            if asset.Os == platform and asset.Arch == arch:
                return asset
        raise Exception(f"No asset found for {self.Version}")


@cache
def get_latest_novm_release() -> NovmRelease:
    response = requests.get("https://debdutdeb.github.io/novm/releases.json")
    response.raise_for_status()

    data = response.json()
    assert data["releases"] is not None
    assert len(data["releases"]) > 0

    releases: List[NovmRelease] = []
    for release in data["releases"]:
        releases.append(NovmRelease.from_dict(release))

    releases.sort(key=lambda x: x.Version, reverse=True)

    return releases[0]
