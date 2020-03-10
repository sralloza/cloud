class CloudError(Exception):
    """Base exception."""


class CloudWarning(Warning):
    """Base warning."""


class SudoersWarning(CloudWarning):
    """Sudoers warning."""


class IngoredWarning(CloudWarning):
    """Ignored warning."""
