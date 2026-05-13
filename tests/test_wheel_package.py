"""Assertions for installs that ship a precompiled extension (wheels / binary installs).

These tests pass for a normal editable or ``pip install -e .`` build as long as the
Cython extension is compiled to a native module. They fail loudly if the accelerator
is missing or only source artifacts are visible at import time.
"""

from __future__ import annotations

from pathlib import Path

import python_uuidv47._uuidv47 as _uuidv47

import python_uuidv47
from python_uuidv47 import decode, encode, has_keys, set_keys, uuid_parse


def _extension_file() -> str | None:
    return getattr(_uuidv47, "__file__", None)


def _is_native_extension_file(path: str) -> bool:
    """True if ``path`` looks like a loaded binary extension module."""
    if not path:
        return False
    p = Path(path)
    if p.suffix.lower() == ".pyd":
        return True
    # Linux/macOS: ``*.cpython-XY-…so`` or ``*.so``
    return p.suffix.lower() == ".so"


def test_native_extension_module_file_points_to_binary() -> None:
    path = _extension_file()
    assert path is not None, "_uuidv47 should define __file__"
    assert _is_native_extension_file(path), (
        "Expected compiled extension (.so / .pyd); "
        f"got __file__={path!r}. Is the Cython module built?"
    )
    assert not path.endswith(".pyx"), "Wheel/runtime should not import .pyx directly"


def test_package_version_matches_metadata() -> None:
    assert isinstance(python_uuidv47.__version__, str)
    assert len(python_uuidv47.__version__.split(".")) >= 2


def test_public_api_roundtrip_on_installed_package() -> None:
    set_keys(111, 222)
    assert has_keys() is True
    u = "550e8400-e29b-71d4-a716-446655440000"
    assert uuid_parse(u) is True
    facade = encode(u)
    assert uuid_parse(facade) is True
    assert decode(facade) == u
