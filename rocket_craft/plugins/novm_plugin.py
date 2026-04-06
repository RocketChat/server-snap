from craft_parts.plugins.properties import PluginProperties
from craft_parts.plugins.base import Plugin

from typing import Literal, cast
from typing_extensions import override

from lib.contract.novm_release import (
    get_latest_novm_release,
    get_goarch,
    get_goos,
)
from lib.contract._craft_plugin import _CraftPluginRocketChatVersionValidator

class NovmPluginProperties(PluginProperties, frozen=True):
    plugin: Literal["novm"] = "novm"

    novm_node_version: str = ""


class NovmPlugin(Plugin):
    properties_class = NovmPluginProperties

    validator_class = _CraftPluginRocketChatVersionValidator
    novm_release = get_latest_novm_release()

    @override
    def get_build_snaps(self) -> set[str]:
        return set()

    @override
    def get_build_packages(self) -> set[str]:
        return {"curl"}

    @override
    def get_build_environment(self) -> dict[str, str]:
        options = cast(NovmPluginProperties, self._options)
        return {
            "NOVM_WORKDIR": self._part_info.part_build_dir,
            "NODE_VERSION": options.novm_node_version,
        }

    @override
    def get_build_commands(self) -> list[str]:
        options = cast(NovmPluginProperties, self._options)
        return [
            "./node --version",
            # MUST NOT USE --dereference
            f"cp -rp versions/v{options.novm_node_version}/linux/x64/* $CRAFT_PART_INSTALL"
        ]

    @override
    def get_pull_commands(self) -> list[str]:
        asset = self.novm_release.get_asset(get_goos(), get_goarch())
        print("novm release asset to pull", asset)
        return [
            f"curl -fsSL {asset.DownloadUrl} -o node",
            "chmod +x node",
        ]
