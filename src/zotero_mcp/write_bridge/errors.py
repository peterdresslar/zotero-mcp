class WriteBridgeError(Exception):
    pass


class WriteBridgeUnavailable(WriteBridgeError):
    """Bridge not reachable or not installed/running."""
    pass


class WriteBridgeAuthError(WriteBridgeError):
    """Token missing or invalid."""
    pass
