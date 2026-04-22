import os
from pathlib import Path
from craft_parts.plugins import PluginProperties, Plugin
from craft_parts.utils.os_utils import OsRelease

# extract deb command from v
#from craft_parts.utils.deb_utils import extract_deb

from typing import Literal, cast
from typing_extensions import override

from lib.contract.mongodb_release import (
    get_mongodb_release_or_throw,
    NoMongoDBReleaseFoundError,
    MongoDBRelease,
)
from lib.contract._craft_plugin import _CraftPlugin, _CraftPluginRocketChatVersionValidator

import semver

from typing import cast

from lib._apt import _import_apt

def get_all_dependencies(filename: Path, *, include_installed=True) -> set[str]:
    """
    returns all dependencies this package has;
    has a problem, includes all preinstalled packages too;
    however since snapcraft may install other packages on top of base, not possible easily to know what base will have preinstalled at runtime;
    FIXME: ^
    """
    _import_apt()

    from apt.cache import Cache
    from apt.debfile import DebPackage
    from apt.package import Package

    cache = Cache()
    try:
        cache.update()
        cache.open()
    except Exception as e:
        print(e)

    final_dependencies = set[str]()

    initial_dependencies = set(dep[0][0] for dep in DebPackage(filename=filename.as_posix()).depends)

    while len(initial_dependencies) > 0:
        dependency = initial_dependencies.pop()
        if dependency in final_dependencies:
            continue

        package = cache.get(dependency, None)
        if package is None:
            print(f"Package {dependency} not found in cache")
            continue
            # raise Exception(f"Package {dependency} not found in cache")

        package = cast(Package, package)
        if package.essential:
            print(f"Package {dependency} is essential, skipping")
            continue

        if not include_installed and package.is_installed:
            print(f"Package {dependency} is already installed, skipping")
            continue

        # check if virutal package, if yes get the providing packages
        if cache.is_virtual_package(dependency):
            providing_packages = cache.get_providing_packages(dependency)
            for package in providing_packages:
                if package.shortname not in final_dependencies:
                    initial_dependencies.add(package.shortname)
            continue

        final_dependencies.add(package.shortname)

        for dependencies in package.candidate.dependencies:
            for dep in dependencies:
                if dep.name not in final_dependencies:
                    initial_dependencies.add(dep.name)

    return final_dependencies


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
        dependencies = get_all_dependencies(Path(self._part_info.part_build_dir) / "mongodb.deb", include_installed=True)

        print("runtime dependencies for mongodb", dependencies)

            # with_dependencies = f"$(apt-rdepends {package} 2>/dev/null | grep -v '^ ')"

            # commands.append(f"apt-get download {with_dependencies} -o Dir::Cache::archives=$CRAFT_PART_BUILD")
        commands = list[str]()

        dpkg_extract_command = "for deb in $CRAFT_PART_BUILD/*.deb; do dpkg-deb --extract $deb $CRAFT_PART_INSTALL; done"

        commands.append(dpkg_extract_command)

        if len(dependencies) > 0:
            download_deps_command = f"apt-get download {' '.join(dependencies)} -o Dir::Cache::archives=$CRAFT_PART_BUILD -o Debug::NoLocking=1"
            commands.insert(0, download_deps_command)

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
            release = get_mongodb_release_or_throw(semver.parse_version_info(current_version))
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
