class ReleaseNotFoundError(Exception):
    """Raised when a requested release does not exist."""


class ReleaseConflictError(Exception):
    """Raised when a release action conflicts with domain rules."""
