"""Type stubs for python-uuidv47"""

def set_keys(k0: int, k1: int) -> bool:
    """Set global encryption keys for encoding/decoding operations.

    Args:
        k0: First 64-bit encryption key
        k1: Second 64-bit encryption key

    Returns:
        True if keys were set successfully

    Raises:
        OverflowError: If keys don't fit in 64-bit integers
    """

def encode(uuid_str: str) -> str:
    """Encode a UUIDv7 into a UUIDv4 facade using global keys.

    Args:
        uuid_str: A valid UUIDv7 string to encode

    Returns:
        Encoded UUIDv4 facade string

    Raises:
        RuntimeError: If keys are not set
        ValueError: If UUID format is invalid
    """

def decode(facade_str: str) -> str:
    """Decode a UUIDv4 facade back to original UUIDv7 using global keys.

    Args:
        facade_str: A valid UUID facade string to decode

    Returns:
        Original UUIDv7 string

    Raises:
        RuntimeError: If keys are not set
        ValueError: If facade format is invalid
    """

def has_keys() -> bool:
    """Check if global encryption keys have been set.

    Returns:
        True if keys are set, False otherwise
    """

def uuid_parse(uuid_str: str) -> bool:
    """Validate if a string is a properly formatted UUID.

    Args:
        uuid_str: String to validate

    Returns:
        True if valid UUID format, False otherwise
    """

__version__: str
