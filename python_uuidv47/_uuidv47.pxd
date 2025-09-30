# cython: language_level=3

from libc.stdint cimport uint8_t, uint64_t
from libcpp cimport bool

# C struct declarations from uuidv47.h
cdef extern from "uuidv47.h":
    ctypedef struct uuid128_t:
        uint8_t b[16]
    
    ctypedef struct uuidv47_key_t:
        uint64_t k0, k1
    
    # Core functions we need from the C implementation
    uuid128_t uuidv47_encode_v4facade(uuid128_t v7, uuidv47_key_t key) nogil
    uuid128_t uuidv47_decode_v4facade(uuid128_t facade, uuidv47_key_t key) nogil
    bool uuid_parse(const char* s, uuid128_t* out) nogil
    void uuid_format(const uuid128_t* u, char out[37]) nogil

# Public function declarations for other Cython modules
cpdef bool set_keys(uint64_t k0, uint64_t k1)
cpdef str encode(str uuid_str)
cpdef str decode(str facade_str)
cpdef bool has_keys()
cpdef bool uuid_parse_py(str uuid_str)