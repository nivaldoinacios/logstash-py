class EventforgeError(Exception):
    """Base error."""


class ConfigError(EventforgeError):
    """Configuration error."""


class PluginError(EventforgeError):
    """Plugin execution error."""
