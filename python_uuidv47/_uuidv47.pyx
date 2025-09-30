# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

from libc.stdint cimport uint8_t, uint64_t
from libc.string cimport memcpy
from libcpp cimport bool


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

cpdef bool set_keys(uint64_t k0, uint64_t k1):
    """Set global encryption keys for encoding/decoding operations.
    
    Args:
        k0: First 64-bit encryption key
        k1: Second 64-bit encryption key
        
    Returns:
        True if keys were set successfully
        
    Raises:
        OverflowError: If keys don't fit in 64-bit integers
    """
    global _global_key, _key_set
    _global_key.k0 = k0
    _global_key.k1 = k1
    _key_set = True
    return True

cpdef bool has_keys():
    """Check if global encryption keys have been set.
    
    Returns:
        True if keys are set, False otherwise
    """
    return _key_set

cpdef str encode(str uuid_str):
    """Encode a UUIDv7 into a UUIDv4 facade using global keys.
    
    Args:
        uuid_str: A valid UUIDv7 string to encode
        
    Returns:
        Encoded UUIDv4 facade string
        
    Raises:
        RuntimeError: If keys are not set
        ValueError: If UUID format is invalid
    """
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

cpdef str decode(str facade_str):
    """Decode a UUIDv4 facade back to original UUIDv7 using global keys.
    
    Args:
        facade_str: A valid UUID facade string to decode
        
    Returns:
        Original UUIDv7 string
        
    Raises:
        RuntimeError: If keys are not set
        ValueError: If facade format is invalid
    """
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

cpdef bool uuid_parse_py(str uuid_str):
    """Validate if a string is a properly formatted UUID.
    
    Args:
        uuid_str: String to validate
        
    Returns:
        True if valid UUID format, False otherwise
    """
    if not uuid_str:
        return False
        
    cdef bytes uuid_bytes = uuid_str.encode('ascii')
    cdef const char* uuid_cstr = uuid_bytes
    cdef uuid128_t uuid
    cdef bool result
    
    with nogil:
        result = uuid_parse(uuid_cstr, &uuid)
    
    return result