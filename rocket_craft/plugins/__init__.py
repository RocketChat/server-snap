from craft_parts.plugins import register

from plugins.mongodb_plugin import MongoDBPlugin
from plugins.novm_plugin import NovmPlugin

__ALL__ = {
    "mongodb": MongoDBPlugin,
    "novm": NovmPlugin,
}

def register_plugins():
    return register(__ALL__)
