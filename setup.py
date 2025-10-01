from Cython.Build import cythonize
from setuptools import Extension, setup


def build_extension():
    """Build the Cython extension"""

    extensions = [
        Extension(
            "python_uuidv47._uuidv47",
            sources=["src/python_uuidv47/_uuidv47.pyx"],
        )
    ]

    return cythonize(
        extensions,
        compiler_directives={},
    )


setup(name="python_uuidv47", ext_modules=build_extension())
