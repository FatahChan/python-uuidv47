# Python UUIDv47 Implementation Plan (Cython)

## Project Overview

Create `python-uuidv47` - a high-performance Python package using Cython to wrap the same C implementation used in the Node.js version.

### Goals
- **Same Performance**: Identical C core with native speed
- **Pythonic API**: Clean, intuitive Python interface
- **Type Safety**: Full type hints and mypy compatibility
- **Easy Installation**: Standard pip install with wheel distribution
- **Cross-Platform**: Windows, macOS, Linux support

## Project Structure

```
python-uuidv47/
├── src/
│   ├── uuidv47.h                    # Downloaded C implementation (same as Node.js)
│   ├── test_vectors_gen.c           # C compatibility test
│   └── download_header.py           # Header download script
├── python_uuidv47/
│   ├── __init__.py                  # Package entry point
│   ├── _uuidv47.pyx                 # Cython implementation
│   ├── _uuidv47.pxd                 # Cython declarations
│   └── py.typed                     # Type hint marker
├── tests/
│   ├── test_uuidv47.py             # pytest test suite
│   ├── test_performance.py         # Performance benchmarks
│   └── test_compatibility.py       # Cross-language compatibility
├── build_tools/
│   ├── setup.py                    # Build configuration
│   ├── build_ext.py                # Custom build commands
│   └── verify_compat.py            # C compatibility verification
├── pyproject.toml                  # Modern Python packaging
├── setup.cfg                       # setuptools configuration`
├── MANIFEST.in                     # Package manifest
├── requirements.txt                # Development dependencies
├── requirements-dev.txt            # Development tools
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI/CD pipeline
│       └── wheels.yml              # Wheel building
├── README.md                       # Documentation
├── CHANGELOG.md                    # Version history
└── LICENSE                         # MIT License
```

## Phase 1: Core Implementation (Week 1)

### 1.1 Cython Extension (`_uuidv47.pyx`)

```cython
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

from libc.stdint cimport uint8_t, uint64_t
from libc.string cimport memcpy
from libc.stdbool cimport bool

# C declarations from uuidv47.h
cdef extern from "uuidv47.h":
    ctypedef struct uuid128_t:
        uint8_t b[16]
    
    ctypedef struct uuidv47_key_t:
        uint64_t k0, k1
    
    # Core functions
    uuid128_t uuidv47_encode_v4facade(uuid128_t v7, uuidv47_key_t key) nogil
    uuid128_t uuidv47_decode_v4facade(uuid128_t facade, uuidv47_key_t key) nogil
    bool uuid_parse(const char* s, uuid128_t* out) nogil
    void uuid_format(const uuid128_t* u, char out[37]) nogil

# Global state (same pattern as Node.js)
cdef uuidv47_key_t _global_key = uuidv47_key_t(k0=0, k1=0)
cdef bool _key_set = False

# Public API functions
def set_keys(uint64_t k0, uint64_t k1) -> bool:
    """Set global encryption keys for encoding/decoding operations."""
    global _global_key, _key_set
    _global_key.k0 = k0
    _global_key.k1 = k1
    _key_set = True
    return True

def encode(str uuid_str) -> str:
    """Encode a UUIDv7 into a UUIDv4 facade using global keys."""
    if not _key_set:
        raise RuntimeError("Keys not set. Call set_keys() first.")
    
    cdef bytes uuid_bytes = uuid_str.encode('ascii')
    cdef const char* uuid_cstr = uuid_bytes
    cdef uuid128_t v7, facade
    cdef char facade_str[37]
    
    with nogil:
        if not uuid_parse(uuid_cstr, &v7):
            with gil:
                raise ValueError("Invalid UUIDv7 format")
        
        facade = uuidv47_encode_v4facade(v7, _global_key)
        uuid_format(&facade, facade_str)
    
    return facade_str[:36].decode('ascii')

def decode(str facade_str) -> str:
    """Decode a UUIDv4 facade back to original UUIDv7 using global keys."""
    if not _key_set:
        raise RuntimeError("Keys not set. Call set_keys() first.")
    
    cdef bytes facade_bytes = facade_str.encode('ascii')
    cdef const char* facade_cstr = facade_bytes
    cdef uuid128_t facade, v7
    cdef char v7_str[37]
    
    with nogil:
        if not uuid_parse(facade_cstr, &facade):
            with gil:
                raise ValueError("Invalid UUID format")
        
        v7 = uuidv47_decode_v4facade(facade, _global_key)
        uuid_format(&v7, v7_str)
    
    return v7_str[:36].decode('ascii')

def has_keys() -> bool:
    """Check if global encryption keys have been set."""
    return _key_set

def uuid_parse(str uuid_str) -> bool:
    """Validate if a string is a properly formatted UUID."""
    cdef bytes uuid_bytes = uuid_str.encode('ascii')
    cdef const char* uuid_cstr = uuid_bytes
    cdef uuid128_t uuid
    
    with nogil:
        result = uuid_parse(uuid_cstr, &uuid)
    
    return result
```

### 1.2 Type Declarations (`_uuidv47.pxd`)

```cython
from libc.stdint cimport uint64_t
from libc.stdbool cimport bool

# Public function declarations for other Cython modules
cpdef bool set_keys(uint64_t k0, uint64_t k1)
cpdef str encode(str uuid_str)
cpdef str decode(str facade_str)
cpdef bool has_keys()
cpdef bool uuid_parse(str uuid_str)
```

### 1.3 Python Package (`__init__.py`)

```python
"""
python-uuidv47: High-performance UUIDv47 operations for Python

A Python extension for encoding UUIDv7 into UUIDv4 facades and decoding them back.
Uses the same C implementation as the Node.js version for maximum performance.
"""

from ._uuidv47 import (
    set_keys,
    encode, 
    decode,
    has_keys,
    uuid_parse
)

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
```

## Phase 2: Build System (Week 1-2)

### 2.1 Modern Build Configuration (`pyproject.toml`)

```toml
[build-system]
requires = [
    "setuptools>=64",
    "wheel",
    "Cython>=0.29.32",
    "requests"  # For downloading header
]
build-backend = "setuptools.build_meta"

[project]
name = "python-uuidv47"
version = "1.0.0"
description = "High-performance UUIDv47 operations - encoding UUIDv7 into UUIDv4 facades"
authors = [{name = "Your Name", email = "you@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
keywords = ["uuid", "uuidv7", "uuidv47", "cryptography", "performance"]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: C",
    "Topic :: Security :: Cryptography",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Operating System :: OS Independent",
]

dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-benchmark",
    "mypy>=1.0",
    "black",
    "isort",
    "flake8",
    "uuid7",  # For testing
]

[project.urls]
Homepage = "https://github.com/yourusername/python-uuidv47"
Repository = "https://github.com/yourusername/python-uuidv47.git"
Issues = "https://github.com/yourusername/python-uuidv47/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["python_uuidv47*"]

[tool.setuptools.package-data]
python_uuidv47 = ["py.typed", "*.pyi"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### 2.2 Custom Setup Script (`setup.py`)

```python
import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from Cython.Build import cythonize
import requests

def download_header():
    """Download uuidv47.h from upstream repository"""
    header_path = Path("src/uuidv47.h")
    
    if header_path.exists():
        print(f"Header {header_path} already exists")
        return
    
    header_path.parent.mkdir(exist_ok=True)
    
    url = "https://raw.githubusercontent.com/stateless-me/uuidv47/main/uuidv47.h"
    print(f"Downloading {url}...")
    
    response = requests.get(url)
    response.raise_for_status()
    
    with open(header_path, 'w') as f:
        f.write(response.text)
    
    print(f"Downloaded to {header_path}")

def verify_c_compatibility():
    """Compile and run C compatibility test"""
    test_gen_path = Path("src/test_vectors_gen")
    test_source = Path("src/test_vectors_gen.c")
    
    if not test_source.exists():
        print("Warning: C compatibility test not found, skipping verification")
        return
    
    print("Compiling C test vector generator...")
    try:
        subprocess.run([
            "gcc", "-std=c11", "-O2", 
            "-o", str(test_gen_path), 
            str(test_source)
        ], check=True, capture_output=True)
        
        print("Running C compatibility test...")
        result = subprocess.run([str(test_gen_path)], 
                              check=True, capture_output=True, text=True)
        print("C compatibility verified!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"C compatibility test failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    finally:
        # Clean up
        if test_gen_path.exists():
            test_gen_path.unlink()

def build_extension():
    """Build the Cython extension"""
    
    # Pre-build setup
    download_header()
    verify_c_compatibility()
    
    # Compiler flags for performance
    extra_compile_args = [
        "-std=c11",
        "-O3", 
        "-march=native",
        "-ffast-math",
        "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"
    ]
    
    # Platform-specific optimizations
    if sys.platform == "win32":
        extra_compile_args = ["/O2", "/std:c11"]
    
    extensions = [
        Extension(
            "python_uuidv47._uuidv47",
            sources=["python_uuidv47/_uuidv47.pyx"],
            include_dirs=["src"],
            extra_compile_args=extra_compile_args,
            language="c"
        )
    ]
    
    return cythonize(
        extensions,
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
            "embedsignature": True,
        }
    )

if __name__ == "__main__":
    setup(ext_modules=build_extension())
```

## Phase 3: Testing & Quality (Week 2)

### 3.1 Comprehensive Test Suite (`tests/test_uuidv47.py`)

```python
import pytest
import uuid
from uuid import uuid4
from python_uuidv47 import set_keys, encode, decode, has_keys, uuid_parse

class TestUUIDv47:
    
    def setup_method(self):
        """Reset state before each test"""
        # Can't actually reset keys, so set to known state
        set_keys(0, 0)
    
    def test_key_management(self):
        """Test key setting and checking"""
        assert set_keys(123, 456) is True
        assert has_keys() is True
        
        # Test with large keys
        max_key = 2**64 - 1
        assert set_keys(max_key, max_key) is True
    
    def test_uuid_parsing(self):
        """Test UUID format validation"""
        valid_uuid = str(uuid4())
        assert uuid_parse(valid_uuid) is True
        
        assert uuid_parse("invalid-uuid") is False
        assert uuid_parse("") is False
        assert uuid_parse("12345678-1234-1234-1234-123456789abc") is True
    
    def test_encode_decode_roundtrip(self):
        """Test encoding and decoding preserves original"""
        set_keys(123456789, 987654321)
        
        # Generate test UUIDs (using uuid4 as proxy for UUIDv7)
        test_uuids = [str(uuid4()) for _ in range(10)]
        
        for original in test_uuids:
            facade = encode(original)
            decoded = decode(facade)
            assert decoded == original
            
            # Facade should look like valid UUID
            assert uuid_parse(facade) is True
    
    def test_error_conditions(self):
        """Test error handling"""
        # Reset keys
        set_keys(0, 0)
        
        with pytest.raises(RuntimeError, match="Keys not set"):
            encode("12345678-1234-7234-8234-123456789abc")
        
        with pytest.raises(RuntimeError, match="Keys not set"):
            decode("12345678-1234-4234-8234-123456789abc")
        
        # Set keys and test invalid UUIDs
        set_keys(123, 456)
        
        with pytest.raises(ValueError, match="Invalid UUIDv7"):
            encode("invalid-uuid")
        
        with pytest.raises(ValueError, match="Invalid UUID"):
            decode("invalid-uuid")
    
    def test_different_keys_produce_different_results(self):
        """Test that different keys produce different facades"""
        test_uuid = str(uuid4())
        
        set_keys(111, 222)
        facade1 = encode(test_uuid)
        
        set_keys(333, 444)
        facade2 = encode(test_uuid)
        
        assert facade1 != facade2
        
        # But both should decode correctly with their respective keys
        set_keys(111, 222)
        assert decode(facade1) == test_uuid
        
        set_keys(333, 444)
        assert decode(facade2) == test_uuid
```

### 3.2 Performance Benchmarks (`tests/test_performance.py`)

```python
import pytest
import uuid
from python_uuidv47 import set_keys, encode, decode

class TestPerformance:
    
    def setup_method(self):
        set_keys(123456789, 987654321)
        self.test_uuid = str(uuid.uuid4())
    
    def test_encode_performance(self, benchmark):
        """Benchmark encoding performance"""
        result = benchmark(encode, self.test_uuid)
        assert len(result) == 36
    
    def test_decode_performance(self, benchmark):
        """Benchmark decoding performance"""
        facade = encode(self.test_uuid)
        result = benchmark(decode, facade)
        assert result == self.test_uuid
    
    def test_batch_operations(self, benchmark):
        """Benchmark batch encode/decode operations"""
        test_uuids = [str(uuid.uuid4()) for _ in range(1000)]
        
        def batch_encode_decode():
            for uuid_str in test_uuids:
                facade = encode(uuid_str)
                decoded = decode(facade)
                assert decoded == uuid_str
        
        benchmark(batch_encode_decode)
```

## Phase 4: Distribution & CI/CD (Week 3)

### 4.1 GitHub Actions CI (`/.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build wheel Cython requests
    
    - name: Build extension
      run: python -m build
    
    - name: Install package
      run: pip install dist/*.whl
    
    - name: Install test dependencies
      run: pip install pytest pytest-benchmark
    
    - name: Run tests
      run: pytest tests/ -v
    
    - name: Run benchmarks
      run: pytest tests/test_performance.py --benchmark-only

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install linting tools
      run: |
        pip install black isort flake8 mypy
    
    - name: Check formatting
      run: |
        black --check .
        isort --check-only .
        flake8 .
    
    - name: Type checking
      run: mypy python_uuidv47/
```

### 4.2 Wheel Building (`/.github/workflows/wheels.yml`)

```yaml
name: Build Wheels

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-20.04, windows-2019, macos-11]

    steps:
    - uses: actions/checkout@v4

    - name: Build wheels
      uses: pypa/cibuildwheel@v2.16.2
      env:
        CIBW_BUILD: cp38-* cp39-* cp310-* cp311-* cp312-*
        CIBW_SKIP: "*-win32 *-manylinux_i686"
        CIBW_BEFORE_BUILD: pip install Cython requests
        CIBW_TEST_REQUIRES: pytest
        CIBW_TEST_COMMAND: pytest {project}/tests/

    - uses: actions/upload-artifact@v3
      with:
        path: ./wheelhouse/*.whl

  build_sdist:
    name: Build source distribution
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Build sdist
      run: pipx run build --sdist

    - uses: actions/upload-artifact@v3
      with:
        path: dist/*.tar.gz

  upload_pypi:
    needs: [build_wheels, build_sdist]
    runs-on: ubuntu-latest
    if: github.event_name == 'release' && github.event.action == 'published'
    steps:
    - uses: actions/download-artifact@v3
      with:
        name: artifact
        path: dist

    - uses: pypa/gh-action-pypi-publish@v1.8.10
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Phase 5: Documentation & Examples (Week 3-4)

### 5.1 README.md Structure

```markdown
# python-uuidv47

High-performance Python library for UUIDv47 operations - encoding UUIDv7 into UUIDv4 facades.

## Quick Start

```python
import python_uuidv47 as uuidv47
from uuid import uuid7  # Python 3.12+ or uuid7 package

# Set encryption keys once
uuidv47.set_keys(1234567890123456789, 9876543210987654321)

# Generate a UUIDv7
original = str(uuid7())

# Encode to facade
facade = uuidv47.encode(original)

# Decode back to original  
decoded = uuidv47.decode(facade)

assert original == decoded
```

## Installation

```bash
pip install python-uuidv47
```

## Performance

- Native C implementation using Cython
- Same algorithm as node-uuidv47
- Optimized for high-throughput operations
```

### 5.2 Type Stubs (`python_uuidv47/__init__.pyi`)

```python
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
```

## Timeline Summary

### Week 1: Core Implementation
- [ ] Set up project structure
- [ ] Implement Cython extension (`_uuidv47.pyx`)
- [ ] Create Python package interface
- [ ] Basic build system (`setup.py`, `pyproject.toml`)

### Week 2: Testing & Quality
- [ ] Comprehensive test suite
- [ ] Performance benchmarks  
- [ ] Error handling validation
- [ ] Code quality tools (black, mypy, etc.)

### Week 3: Distribution
- [ ] GitHub Actions CI/CD
- [ ] Multi-platform wheel building
- [ ] PyPI publishing setup
- [ ] Cross-language compatibility tests

### Week 4: Documentation & Polish
- [ ] Complete README with examples
- [ ] API documentation
- [ ] Type stubs and mypy compatibility
- [ ] Performance comparison with Node.js version

## Success Criteria

1. **Performance**: Match or exceed Node.js version speed
2. **Compatibility**: Identical results for same inputs/keys
3. **Distribution**: Wheels available for all major platforms
4. **Quality**: 100% test coverage, type safety, linting
5. **Usability**: Simple pip install, clear documentation

This plan leverages Cython's strengths while maintaining the same architectural patterns that made the Node.js version successful. The result will be a high-performance Python package that's easy to install and use.