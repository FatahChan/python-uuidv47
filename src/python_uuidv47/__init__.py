"""
python-uuidv47: High-performance UUIDv47 operations for Python

A Python extension for encoding UUIDv7 into UUIDv4 facades and decoding them back.
Uses the same C implementation as the Node.js version for maximum performance.
"""

from ._uuidv47 import decode, encode, has_keys, set_keys
from ._uuidv47 import uuid_parse_py as uuid_parse

__version__ = "1.0.8"
__all__ = ["set_keys", "encode", "decode", "has_keys", "uuid_parse"]
