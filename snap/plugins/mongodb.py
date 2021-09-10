from snapcraft.plugins.v1 import PluginV1
from snapcraft.internal.repo.apt_key_manager import AptKeyManager
from snapcraft.internal.sources import Tar
from snapcraft.internal import errors

from typing import Dict, Any, List, Set
import os
import re


REPO_URL: str = (
    " deb [ arch=amd64,arm64 ] "
    " https://repo.mongodb.org/apt/ubuntu "
    " {ubuntu_codename}/mongodb-org/{version_major_minor} "
    " multiverse "
)
KEY_URL: str = "https://www.mongodb.org/static/pgp/server-{version_major_minor}.asc"
REPO_FILE: str = "/etc/apt/sources.list.d/mongodb-{version_major_minor}.list"
TOOLS: Set[str] = {
    "install_compass",
    "mongodump",
    "mongorestore",
    "bsondump",
    "mongoexport",
    "mongofiles",
    "mongoimport",
    "mongoperf",
    "mongostat",
    "mongotop"
}
COMPONENTS: Set[str] = {
    "shell",
    "server",
    "tools"
}

PACKAGES: Dict[str, str] = {
    "shell": "mongodb-org-shell",
    "server": "mongodb-org-server",
    "tools": "mongodb-org-tools"
}


def get_ubuntu_codename() -> str:
    with open("/etc/os-release", 'r') as file_handler:
        for line in file_handler:
            match = re.match(r'^UBUNTU_CODENAME=(.+)$', line)
            if match != None:
                return match.group(1)


class MongoRepoWriteError(errors.SnapcraftError):
    # TODO: error string
    pass


class InvalidToolSelection(errors.SnapcraftError):
    fmt: str = (
        "Invalid list of tools.\n"
        "Please select one of the following\n"
        "\tinstall_compass\n"
        "\tmongodump\n"
        "\tmongorestore\n"
        "\tbsondump\n"
        "\tmongoexport\n"
        "\tmongofiles\n"
        "\tmongoimport\n"
        "\tmongoperf\n"
        "\tmongostat\n"
        "\tmongotop"
    )


class InvalidComponentSelection(errors.SnapcraftError):
    fmt: str = (
        "Invalid list of components.\n"
        "Please select one of the following\n"
        "\tshell\n"
        "\tdaemon\n"
        "\ttools"
    )


class PluginImpl(PluginV1):

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "version": {
                    "type": "string"
                },
                "components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 3,
                    "uniqueItems": True
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 10,
                    "uniqueItems": True
                }
            },
            "required": ["version"]
        }

    @classmethod
    def get_pull_properties(cls) -> List[str]:
        return ["version"]

    @classmethod
    def get_build_properties(cls) -> List[str]:
        return ["tools"]

    def __init__(self, name, options, project=None) -> "PluginImpl":
        super().__init__(name, options, project)

        self.init_variables()
        self.validate_schema()

    @property
    def stage_packages(self) -> List[str]:
        self._install_key()
        self._install_repository()

        self._stage_packages.extend([PACKAGES[selection]
                                    for selection in self.options.components])

        return self._stage_packages

    def _install_repository(self) -> None:
        try:
            with open(self.repo_file, 'w') as file_handler:
                file_handler.write(self.repo_url)
        except Exception as e:
            print(e)

    def _install_key(self) -> None:
        # It isn't a tar file
        # but FileBase isn't accessible :p

        key_file_handler: Tar = Tar(self.key_url, self.sourcedir)
        key_file_handler.download()

        apt_key = AptKeyManager(key_assets="")
        try:
            with open(self.key_file) as file_handler:
                apt_key.install_key(key=file_handler.read())
        except Exception as e:
            print(f"error occured: {e}")

    def init_variables(self):
        self.mongodb_version: str = self.options.version
        version_major_minor: str = '.'.join(
            self.mongodb_version.split('.')[0:2])
        self.repo_url: str = REPO_URL.format(
            version_major_minor=version_major_minor, ubuntu_codename=get_ubuntu_codename())
        self.repo_file: str = REPO_FILE.format(
            version_major_minor=version_major_minor)
        self.key_url: str = KEY_URL.format(
            version_major_minor=version_major_minor)
        self.key_file: str = os.path.join(
            self.sourcedir, f"server-{version_major_minor}.asc")

    def validate_schema(self):
        # I wish I could pass a list and snapcraft would validate it
        # for me :p
        if not set(self.options.components).issubset(COMPONENTS):
            raise InvalidComponentSelection
        if "tools" in self.options.components:
            if not set(self.options.tools).issubset(TOOLS):
                raise InvalidToolSelection

    def snap_fileset(self):
        fileset: List[str] = super().snap_fileset()
        fileset.extend(
            [f"-usr/bin/{tool}" for tool in TOOLS.difference(set(self.options.tools))])
        return fileset
