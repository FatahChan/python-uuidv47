"""
python-uuidv47: High-performance UUIDv47 operations for Python

A Python extension for encoding UUIDv7 into UUIDv4 facades and decoding them back.
Uses the same C implementation as the Node.js version for maximum performance.
"""

from ._uuidv47 import decode, encode, has_keys, set_keys
from ._uuidv47 import uuid_parse_py as uuid_parse

__version__ = "1.0.0"
__all__ = ["set_keys", "encode", "decode", "has_keys", "uuid_parse"]

# Type hints for better IDE support
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    def set_keys(k0: int, k1: int) -> bool: ...
    def encode(uuid_str: str) -> str: ...
    def decode(facade_str: str) -> str: ...
    def has_keys() -> bool: ...
    def uuid_parse(uuid_str: str) -> bool: ...
