# python-uuidv47

[![CI](https://github.com/FatahChan/python-uuidv47/workflows/CI/badge.svg)](https://github.com/FatahChan/python-uuidv47/actions)
[![PyPI version](https://img.shields.io/pypi/v/python-uuidv47.svg)](https://pypi.org/project/python-uuidv47/)
[![Python versions](https://img.shields.io/pypi/pyversions/python-uuidv47.svg)](https://pypi.org/project/python-uuidv47/)

High-performance Python library for UUIDv47 operations - encoding UUIDv7 into UUIDv4 facades and decoding them back. Uses the same C implementation.

## What is UUIDv47?

UUIDv47 is a technique for encoding UUIDv7 (time-ordered UUIDs) into UUIDv4 facades (random-looking UUIDs) using cryptographic keys. This allows you to:

- **Hide temporal information** in UUIDs while maintaining format compatibility
- **Preserve randomness** in the facade for security
- **Maintain reversibility** with the correct keys
- **Ensure cross-language compatibility** between implementations

## Quick Start

```python
import python_uuidv47 as uuidv47

# Set encryption keys once (use your own secure keys!)
uuidv47.set_keys(0x123456789ABCDEF0, 0xFEDCBA9876543210)

# Example with a UUIDv7 (time-ordered UUID)
original_uuid = "550e8400-e29b-71d4-a716-446655440000"  # Version 7

# Encode to facade (looks like UUIDv4)
facade = uuidv47.encode(original_uuid)
print(f"Facade: {facade}")  # e.g., "3ebd5dfc-1b0d-41d4-a716-446655440000"

# Decode back to original
decoded = uuidv47.decode(facade)
print(f"Decoded: {decoded}")  # "550e8400-e29b-71d4-a716-446655440000"

assert original_uuid == decoded  # Perfect roundtrip!
```

## Installation

### From PyPI (Recommended)

```bash
uv add python-uuidv47
```

Or with pip:
```bash
pip install python-uuidv47
```

### From Source

```bash
git clone https://github.com/FatahChan/python-uuidv47.git
cd python-uuidv47
uv sync
```

## API Reference

### `set_keys(k0: int, k1: int) -> bool`

Set the global encryption keys used for encoding and decoding operations.

**Parameters:**
- `k0`: First 64-bit encryption key (0 to 2^64-1)
- `k1`: Second 64-bit encryption key (0 to 2^64-1)

**Returns:** `True` if keys were set successfully

**Example:**
```python
uuidv47.set_keys(0x123456789ABCDEF0, 0xFEDCBA9876543210)
```

### `encode(uuid_str: str) -> str`

Encode a UUIDv7 into a UUIDv4 facade using the global keys.

**Parameters:**
- `uuid_str`: A valid UUIDv7 string to encode

**Returns:** Encoded UUIDv4 facade string

**Raises:**
- `RuntimeError`: If keys are not set
- `ValueError`: If UUID format is invalid

### `decode(facade_str: str) -> str`

Decode a UUIDv4 facade back to the original UUIDv7 using the global keys.

**Parameters:**
- `facade_str`: A valid UUID facade string to decode

**Returns:** Original UUIDv7 string

**Raises:**
- `RuntimeError`: If keys are not set
- `ValueError`: If facade format is invalid

### `has_keys() -> bool`

Check if global encryption keys have been set.

**Returns:** `True` if keys are set, `False` otherwise

### `uuid_parse(uuid_str: str) -> bool`

Validate if a string is a properly formatted UUID.

**Parameters:**
- `uuid_str`: String to validate

**Returns:** `True` if valid UUID format, `False` otherwise

## Performance

This library is built for high-performance applications:

- **Native C implementation** using Cython for maximum speed
- **Same algorithm** as the Node.js node-uuidv47 package
- **100,000+ operations per second** on modern hardware
- **Minimal memory allocation** and efficient string handling
- **Thread-safe operations** with nogil Cython blocks

### Benchmarks

```python
import python_uuidv47 as uuidv47
import time

uuidv47.set_keys(0x123456789ABCDEF0, 0xFEDCBA9876543210)
test_uuid = "550e8400-e29b-71d4-a716-446655440000"

# Benchmark encoding
start = time.perf_counter()
for _ in range(100000):
    facade = uuidv47.encode(test_uuid)
encode_time = time.perf_counter() - start

print(f"Encode: {100000/encode_time:.0f} ops/sec")
# Typical output: Encode: 150000+ ops/sec
```

## Cross-Language Compatibility

This Python implementation produces identical results to the Node.js version:

```python
# Python
uuidv47.set_keys(0x123456789ABCDEF0, 0xFEDCBA9876543210)
facade = uuidv47.encode("550e8400-e29b-71d4-a716-446655440000")
# Result: "3ebd5dfc-1b0d-41d4-a716-446655440000"
```

```javascript
// Node.js (node-uuidv47)
const uuidv47 = require('node-uuidv47');
uuidv47.setKeys(0x123456789ABCDEF0n, 0xFEDCBA9876543210n);
const facade = uuidv47.encode("550e8400-e29b-71d4-a716-446655440000");
// Result: "3ebd5dfc-1b0d-41d4-a716-446655440000" (identical!)
```

## Security Considerations

- **Use strong, random keys**: Generate your encryption keys securely
- **Keep keys secret**: Never expose keys in logs, code, or public repositories
- **Key rotation**: Consider rotating keys periodically for enhanced security
- **Constant-time operations**: The implementation uses constant-time operations where possible

```python
import secrets

# Generate secure random keys
k0 = secrets.randbits(64)
k1 = secrets.randbits(64)
uuidv47.set_keys(k0, k1)
```

## Error Handling

The library provides clear error messages for common issues:

```python
import python_uuidv47 as uuidv47

# Attempting operations without setting keys
try:
    uuidv47.encode("550e8400-e29b-71d4-a716-446655440000")
except RuntimeError as e:
    print(e)  # "Keys not set. Call set_keys() first."

# Invalid UUID format
uuidv47.set_keys(123, 456)
try:
    uuidv47.encode("invalid-uuid")
except ValueError as e:
    print(e)  # "Invalid UUIDv7 format"
```

## Development

### Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Cython 3.0+
- C11 compatible compiler

### Building from Source

```bash
git clone https://github.com/FatahChan/python-uuidv47.git
cd python-uuidv47

# Install development dependencies and build the package
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Run benchmarks
uv run pytest tests/test_performance.py --benchmark-only

# Build source distribution
uv run python -m build --sdist
```

### Code Quality

This project uses modern Python tooling:

- **uv** for fast Python package management
- **Ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing with benchmarks
- **pre-commit** hooks for code quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy python_uuidv47/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [uuidv47](https://github.com/stateless-me/uuidv47) - Original uuid47 in C
- [node-uuid47](https://github.com/sh1kxrv/node_uuidv47) uuid47 in Node.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.