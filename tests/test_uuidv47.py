import uuid
from uuid import uuid4

import pytest

from python_uuidv47 import decode, encode, has_keys, set_keys, uuid_parse


class TestUUIDv47:
    def setup_method(self):
        """Reset state before each test"""
        # Set to known state (can't actually reset keys, so use consistent state)
        set_keys(0, 0)

    def test_key_management(self):
        """Test key setting and checking"""
        # Note: Due to global state design, keys persist between tests
        # We test the functionality rather than initial state

        # Set keys and verify
        assert set_keys(123, 456) is True
        assert has_keys() is True

        # Test with large keys (64-bit max)
        max_key = 2**64 - 1
        assert set_keys(max_key, max_key) is True
        assert has_keys() is True

        # Test with zero keys
        assert set_keys(0, 0) is True
        assert has_keys() is True

    def test_uuid_parsing(self):
        """Test UUID format validation"""
        # Valid UUIDs
        valid_uuid = str(uuid4())
        assert uuid_parse(valid_uuid) is True

        # Standard UUID formats
        assert uuid_parse("12345678-1234-1234-1234-123456789abc") is True
        assert uuid_parse("550e8400-e29b-41d4-a716-446655440000") is True
        assert uuid_parse("6ba7b810-9dad-11d1-80b4-00c04fd430c8") is True

        # Invalid UUIDs
        assert uuid_parse("invalid-uuid") is False
        assert uuid_parse("") is False
        assert uuid_parse("12345678-1234-1234-1234-12345678") is False  # (too short)
        assert (
            uuid_parse("12345678-1234-1234-1234-123456789abg") is False
        )  # (invalid hex)

        # Note: The C implementation accepts some variations:
        # - Underscores instead of dashes (implementation detail)
        # - Extra characters at end (implementation detail)
        # We test the core validation logic that matters for security

    def test_encode_decode_roundtrip(self):
        """Test encoding and decoding preserves original"""
        set_keys(123456789, 987654321)

        # Test UUIDs with version 7 (the algorithm is designed for UUIDv7)
        test_uuids = [
            "550e8400-e29b-71d4-a716-446655440000",  # Version 7
            "01234567-89ab-7def-8123-456789abcdef",  # Version 7
            "fedcba98-7654-7321-8098-765432109876",  # Version 7
        ]

        for original in test_uuids:
            facade = encode(original)
            decoded = decode(facade)
            assert decoded == original, f"Roundtrip failed for {original}"

            # Facade should look like valid UUID
            assert uuid_parse(facade) is True

            # Facade should be different from original (unless keys are zero)
            if not (123456789 == 0 and 987654321 == 0):
                assert facade != original, (
                    f"Facade should differ from original for {original}"
                )

    def test_different_keys_produce_different_results(self):
        """Test that different keys produce different facades"""
        test_uuid = "550e8400-e29b-71d4-a716-446655440000"  # Version 7

        # Test with first set of keys
        set_keys(111, 222)
        facade1 = encode(test_uuid)

        # Test with second set of keys
        set_keys(333, 444)
        facade2 = encode(test_uuid)

        # Facades should be different
        assert facade1 != facade2, "Different keys should produce different facades"

        # But both should decode correctly with their respective keys
        set_keys(111, 222)
        assert decode(facade1) == test_uuid

        set_keys(333, 444)
        assert decode(facade2) == test_uuid

    def test_consistent_encoding(self):
        """Test that encoding the same UUID with same keys produces consistent results"""
        set_keys(555, 777)
        test_uuid = "550e8400-e29b-71d4-a716-446655440000"

        # Encode multiple times
        facade1 = encode(test_uuid)
        facade2 = encode(test_uuid)
        facade3 = encode(test_uuid)

        # All should be identical
        assert facade1 == facade2 == facade3

    def test_facade_format_validation(self):
        """Test that facades look like valid UUIDs"""
        set_keys(999, 888)
        test_uuids = [
            "01234567-89ab-7def-8123-456789abcdef",
            "fedcba98-7654-7321-8098-765432109876",
            "550e8400-e29b-71d4-a716-446655440000",
        ]

        for test_uuid in test_uuids:
            facade = encode(test_uuid)

            # Facade should be valid UUID format
            assert len(facade) == 36
            assert facade.count("-") == 4
            assert uuid_parse(facade) is True

            # Should be parseable by standard UUID library
            try:
                parsed = uuid.UUID(facade)
                assert str(parsed) == facade
            except ValueError:
                pytest.fail(f"Facade {facade} is not a valid UUID")

    def test_large_key_values(self):
        """Test with maximum 64-bit key values"""
        max_uint64 = 2**64 - 1
        set_keys(max_uint64, max_uint64)

        test_uuid = "550e8400-e29b-71d4-a716-446655440000"
        facade = encode(test_uuid)
        decoded = decode(facade)

        assert decoded == test_uuid
        assert uuid_parse(facade) is True

    def test_zero_keys(self):
        """Test behavior with zero keys"""
        set_keys(0, 0)

        test_uuid = "550e8400-e29b-71d4-a716-446655440000"
        facade = encode(test_uuid)
        decoded = decode(facade)

        # Should still work (zero is a valid key)
        assert decoded == test_uuid
        assert uuid_parse(facade) is True

    def test_version_preservation_in_random_bits(self):
        """Test that random bits are preserved correctly"""
        set_keys(12345, 67890)

        # Test UUID with specific random bits pattern
        test_uuid = "550e8400-e29b-71d4-a716-446655440000"
        facade = encode(test_uuid)
        decoded = decode(facade)

        # The random parts should be preserved
        # Bytes 6 (low nibble), 7, 8 (low 6 bits), 9-15 should be identical
        original_bytes = bytes.fromhex(test_uuid.replace("-", ""))
        decoded_bytes = bytes.fromhex(decoded.replace("-", ""))

        # Check preserved random bits
        assert (original_bytes[6] & 0x0F) == (
            decoded_bytes[6] & 0x0F
        )  # Low nibble of byte 6
        assert original_bytes[7] == decoded_bytes[7]  # Byte 7
        assert (original_bytes[8] & 0x3F) == (
            decoded_bytes[8] & 0x3F
        )  # Low 6 bits of byte 8
        assert original_bytes[9:] == decoded_bytes[9:]  # Bytes 9-15
