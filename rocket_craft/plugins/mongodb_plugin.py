import os
from pathlib import Path
from craft_parts.plugins import PluginProperties, Plugin
from craft_parts.utils.os_utils import OsRelease

# extract deb command from v
#from craft_parts.utils.deb_utils import extract_deb

from typing import Literal, cast
from typing_extensions import override

from lib.contract.mongodb_release import (
    get_mongodb_release,
    NoMongoDBReleaseFoundError,
    MongoDBRelease,
)
from lib.contract._craft_plugin import _CraftPlugin, _CraftPluginRocketChatVersionValidator

import semver

from typing import cast

from lib._apt import _import_apt

class MongoDBPluginProperties(PluginProperties, frozen=True):
    plugin: Literal["mongodb"] = "mongodb"
    mongodb_version: str = ""
    mongodb_distro_override: str = ""

class MongoDBPlugin(_CraftPlugin):
    properties_class = MongoDBPluginProperties

    validator_class = _CraftPluginRocketChatVersionValidator

    @override
    def get_build_snaps(self) -> set[str]:
        return set()

    @override
    def get_build_packages(self) -> set[str]:
        return set()

    @override
    def get_build_environment(self) -> dict[str, str]:
        return {}

    @override
    def get_build_commands(self) -> list[str]:
        _import_apt()
        from apt.cache import Cache # pyright: ignore[reportMissingImports]

        cache = Cache()
        try:
            cache.update()
            cache.open()
        except Exception as e:
            print(f"error updating apt cache: {e}")
            if os.environ.get("CRAFT_PART_BUILD", None) is not None:
                raise e

        stage_packages = self.get_stage_packages()

        packages = stage_packages.copy()

        dependencies = set[str]()

        print("stage_packages calculated from mongodb deb", stage_packages)

        while len(packages) > 0:
            stage_package = packages.pop()
            package = cache.get(stage_package, None)
            if package is None:
                print(f"package {stage_package} has no source in apt cache, skipping, must be handled in a separate part")
                continue

            if package.essential:
                print(f"package {stage_package} is essential, skipping")
                continue

            if package.is_installed:
                print(f"package {stage_package} is already installed, skipping")
                continue

            if cache.is_virtual_package(stage_package):
                print(f"package {stage_package} is a virtual package, deciding the providing packages")

                packages.extend(list(package.shortname for package in cache.get_providing_packages(stage_package)))
                continue

            dependencies.add(package.shortname)

            # with_dependencies = f"$(apt-rdepends {package} 2>/dev/null | grep -v '^ ')"

            # commands.append(f"apt-get download {with_dependencies} -o Dir::Cache::archives=$CRAFT_PART_BUILD")
        commands = list[str]()

        dpkg_extract_command = "for deb in $CRAFT_PART_BUILD/*.deb; do dpkg-deb --extract $deb $CRAFT_PART_INSTALL; done"

        commands.append(dpkg_extract_command)

        if len(dependencies) > 0:
            download_deps_command = f"apt-get download {' '.join(dependencies)} -o Dir::Cache::archives=$CRAFT_PART_BUILD -o Debug::NoLocking=1"
            commands.append(download_deps_command)

        return commands

    @override
    def get_stage_packages(self) -> list[str]:
        _import_apt()
        from apt.debfile import DebPackage # pyright: ignore[reportMissingImports]

        build_dir = self._part_info.part_build_dir
        deb_file = Path(build_dir) / "mongodb.deb"
        return list(depends[0][0] for depends in DebPackage(filename=deb_file.as_posix()).depends)

    def get_required_target(self) -> str:
        options = cast(MongoDBPluginProperties, self._options)
        if options.mongodb_distro_override != "":
            return options.mongodb_distro_override
        os_release = OsRelease()
        return f"{os_release.id()}{os_release.version_id().replace('.', '')}"

    @override
    def get_pull_commands(self) -> list[str]:
        options = cast(MongoDBPluginProperties, self._options)
        current_version = options.mongodb_version
        if current_version == "":
            raise ValueError("mongodb-upgrader-current is required")

        release: MongoDBRelease

        try:
            release = get_mongodb_release(semver.parse_version_info(current_version))
        except NoMongoDBReleaseFoundError:
            raise NoMongoDBReleaseFoundError

        for asset in release.Assets:
            if not asset.is_community():
                continue
            if asset.Distro != self.get_required_target():
                continue
            if asset.Arch != "x86_64":
                continue

            return [
                f"curl -fsSL {asset.get_server_package_url()} -o mongodb.deb",
            ]


        raise ValueError(f"no community asset found for the release {release}, os id version string {self.get_required_target()}, arch x86_64")
