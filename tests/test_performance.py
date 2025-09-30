import time

from python_uuidv47 import decode, encode, set_keys, uuid_parse


class TestPerformance:
    def setup_method(self):
        """Set up test environment"""
        set_keys(123456789, 987654321)
        self.test_uuid = "550e8400-e29b-71d4-a716-446655440000"  # Version 7
        self.test_facade = encode(self.test_uuid)

    def test_encode_performance(self, benchmark):
        """Benchmark encoding performance"""
        result = benchmark(encode, self.test_uuid)

        # Verify result is correct
        assert len(result) == 36
        assert uuid_parse(result) is True

        # Verify it's a valid facade
        decoded = decode(result)
        assert decoded == self.test_uuid

    def test_decode_performance(self, benchmark):
        """Benchmark decoding performance"""
        result = benchmark(decode, self.test_facade)

        # Verify result is correct
        assert result == self.test_uuid
        assert len(result) == 36
        assert uuid_parse(result) is True

    def test_uuid_parse_performance(self, benchmark):
        """Benchmark UUID parsing performance"""
        result = benchmark(uuid_parse, self.test_uuid)

        # Verify result is correct
        assert result is True

    def test_batch_encode_operations(self, benchmark):
        """Benchmark batch encoding operations"""
        # Generate test UUIDs (version 7 format)
        test_uuids = [
            f"550e840{i % 16:01x}-e29b-71d4-a716-44665544000{i % 16:01x}"
            for i in range(100)
        ]

        def batch_encode():
            results = []
            for uuid_str in test_uuids:
                results.append(encode(uuid_str))
            return results

        results = benchmark(batch_encode)

        # Verify all results are valid
        assert len(results) == 100
        for result in results:
            assert len(result) == 36
            assert uuid_parse(result) is True

    def test_batch_decode_operations(self, benchmark):
        """Benchmark batch decoding operations"""
        # Generate test facades
        test_uuids = [
            f"550e840{i % 16:01x}-e29b-71d4-a716-44665544000{i % 16:01x}"
            for i in range(100)
        ]
        test_facades = [encode(uuid_str) for uuid_str in test_uuids]

        def batch_decode():
            results = []
            for facade in test_facades:
                results.append(decode(facade))
            return results

        results = benchmark(batch_decode)

        # Verify all results are correct
        assert len(results) == 100
        for i, result in enumerate(results):
            assert result == test_uuids[i]

    def test_batch_encode_decode_roundtrip(self, benchmark):
        """Benchmark batch encode/decode roundtrip operations"""
        # Generate test UUIDs
        test_uuids = [
            f"550e840{i % 16:01x}-e29b-71d4-a716-44665544000{i % 16:01x}"
            for i in range(1000)
        ]

        def batch_encode_decode():
            for uuid_str in test_uuids:
                facade = encode(uuid_str)
                decoded = decode(facade)
                assert decoded == uuid_str

        benchmark(batch_encode_decode)

    def test_performance_with_different_key_sizes(self, benchmark):
        """Test performance with different key values"""
        # Test with maximum key values
        max_key = 2**64 - 1
        set_keys(max_key, max_key)

        result = benchmark(encode, self.test_uuid)

        # Verify result is correct
        assert len(result) == 36
        assert uuid_parse(result) is True

        # Restore original keys
        set_keys(123456789, 987654321)

    def test_performance_with_various_uuid_patterns(self, benchmark):
        """Test performance with various UUID patterns"""
        # Different UUID patterns that might affect performance
        uuid_patterns = [
            "00000000-0000-7000-8000-000000000000",  # Mostly zeros
            "ffffffff-ffff-7fff-8fff-ffffffffffff",  # Mostly ones
            "12345678-9abc-7def-8123-456789abcdef",  # Sequential pattern
            "fedcba98-7654-7321-8098-765432109876",  # Reverse pattern
            "a1b2c3d4-e5f6-7890-8abc-def123456789",  # Mixed pattern
        ]

        def encode_various_patterns():
            results = []
            for pattern in uuid_patterns:
                results.append(encode(pattern))
            return results

        results = benchmark(encode_various_patterns)

        # Verify all results are valid
        assert len(results) == len(uuid_patterns)
        for result in results:
            assert len(result) == 36
            assert uuid_parse(result) is True

    def test_memory_efficiency(self):
        """Test memory efficiency of operations"""
        import gc

        # Force garbage collection
        gc.collect()

        # Measure memory before operations
        initial_objects = len(gc.get_objects())

        # Perform many operations
        for i in range(1000):
            test_uuid = f"550e840{i % 16:01x}-e29b-71d4-a716-44665544000{i % 16:01x}"
            facade = encode(test_uuid)
            decoded = decode(facade)
            assert decoded == test_uuid

        # Force garbage collection
        gc.collect()

        # Measure memory after operations
        final_objects = len(gc.get_objects())

        # Memory growth should be minimal (allow some tolerance for test framework)
        memory_growth = final_objects - initial_objects
        assert memory_growth < 100, f"Excessive memory growth: {memory_growth} objects"

    def test_concurrent_performance(self):
        """Test performance under concurrent access"""
        import threading

        results = []
        errors = []

        def worker():
            try:
                for i in range(100):
                    test_uuid = (
                        f"550e840{i % 16:01x}-e29b-71d4-a716-44665544000{i % 16:01x}"
                    )
                    facade = encode(test_uuid)
                    decoded = decode(facade)
                    assert decoded == test_uuid
                    results.append((test_uuid, facade, decoded))
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        start_time = time.time()

        for _ in range(4):  # 4 concurrent threads
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors in concurrent execution: {errors}"

        # Verify all operations completed
        assert len(results) == 400  # 4 threads * 100 operations each

        # Performance should be reasonable (less than 5 seconds for 400 operations)
        total_time = end_time - start_time
        assert total_time < 5.0, (
            f"Concurrent operations took too long: {total_time:.2f}s"
        )

    def test_performance_regression_detection(self, benchmark):
        """Detect performance regressions"""
        # This test establishes baseline performance expectations

        # Single operation should be very fast (sub-millisecond)
        result = benchmark.pedantic(
            encode, args=(self.test_uuid,), rounds=1000, iterations=1
        )

        # The benchmark framework will track this automatically
        # We can add assertions for minimum performance requirements

        # Verify the operation still works correctly
        assert len(result) == 36
        assert uuid_parse(result) is True

    def test_performance_comparison_baseline(self):
        """Establish performance baseline for comparison"""

        # Measure encode performance
        start_time = time.perf_counter()
        for _ in range(10000):
            encode(self.test_uuid)
        encode_time = time.perf_counter() - start_time

        # Measure decode performance
        start_time = time.perf_counter()
        for _ in range(10000):
            decode(self.test_facade)
        decode_time = time.perf_counter() - start_time

        # Performance expectations (adjust based on actual performance)
        # These are rough targets - actual performance may vary by system
        encode_ops_per_sec = 10000 / encode_time
        decode_ops_per_sec = 10000 / decode_time

        print(f"Encode performance: {encode_ops_per_sec:.0f} ops/sec")
        print(f"Decode performance: {decode_ops_per_sec:.0f} ops/sec")

        # Minimum performance requirements (conservative targets)
        assert encode_ops_per_sec > 50000, (
            f"Encode too slow: {encode_ops_per_sec:.0f} ops/sec"
        )
        assert decode_ops_per_sec > 50000, (
            f"Decode too slow: {decode_ops_per_sec:.0f} ops/sec"
        )
