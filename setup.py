# setup.py
from Cython.Build import cythonize
from setuptools import Extension, setup

extensions = [
    Extension(
        "python_uuidv47._uuidv47",  # Module name (matches import path)
        ["src/python_uuidv47/_uuidv47.pyx"],
        extra_compile_args=["-O3"],  # Optional: compiler optimizations
    )
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
)
