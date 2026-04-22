import os
from typing_extensions import override
from craft_parts.plugins import Plugin, PluginEnvironmentValidator

from abc import ABC

class _CraftPlugin(Plugin, ABC):
    def get_stage_packages(self) -> list[str]:
        return []


class _CraftPluginRocketChatVersionValidator(PluginEnvironmentValidator):
    @override
    def validate_environment(self, *, part_dependencies: list[str] | None = None) -> None:
        # if os.environ.get("ROCKETCHAT_VERSION", None) is None:
        # 	raise ValueError("ROCKETCHAT_VERSION environment variable is not set")
        pass
