import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from Cython.Build import cythonize
from setuptools import Extension, setup


def download_header():
    """Download uuidv47.h from upstream repository"""
    header_path = Path("src/uuidv47.h")

    if header_path.exists():
        print(f"Header {header_path} already exists")
        return True

    header_path.parent.mkdir(exist_ok=True)

    url = "https://raw.githubusercontent.com/stateless-me/uuidv47/main/uuidv47.h"
    print(f"Downloading {url}...")

    try:
        with urlopen(url) as response:
            if response.status != 200:
                print(f"Failed to download header: HTTP {response.status}")
                return False

            content = response.read().decode("utf-8")

        with open(header_path, "w") as f:
            f.write(content)

        print(f"Downloaded to {header_path}")
        return True

    except URLError as e:
        print(f"Failed to download header: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error downloading header: {e}")
        return False


def verify_c_compatibility():
    """Compile and run C compatibility test"""
    test_gen_path = Path("src/test_vectors_gen")
    test_source = Path("src/test_vectors_gen.c")

    if not test_source.exists():
        print("Warning: C compatibility test not found, skipping verification")
        return True

    print("Compiling C test vector generator...")
    try:
        subprocess.run(
            ["gcc", "-std=c11", "-O2", "-o", str(test_gen_path), str(test_source)],
            check=True,
            capture_output=True,
        )

        print("Running C compatibility test...")
        result = subprocess.run(
            [str(test_gen_path)], check=True, capture_output=True, text=True
        )
        print("C compatibility verified!")
        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"C compatibility test failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Warning: gcc not found, skipping C compatibility test")
        return True
    finally:
        # Clean up
        if test_gen_path.exists():
            test_gen_path.unlink()


def build_extension():
    """Build the Cython extension"""

    # Pre-build setup
    if not download_header():
        print("Warning: Failed to download header, build may fail")

    if not verify_c_compatibility():
        print("Warning: C compatibility verification failed")

    # Compiler flags for performance
    extra_compile_args = [
        "-std=c11",
        "-O3",
        "-ffast-math",
    ]

    # Platform-specific optimizations
    if sys.platform == "win32":
        extra_compile_args = ["/O2", "/std:c11"]
    elif sys.platform == "darwin":
        # macOS specific flags
        extra_compile_args.extend(["-mmacosx-version-min=10.9"])
    else:
        # Linux and other Unix-like systems
        extra_compile_args.extend(["-march=native"])

    extensions = [
        Extension(
            "python_uuidv47._uuidv47",
            sources=["python_uuidv47/_uuidv47.pyx"],
            include_dirs=["src"],
            extra_compile_args=extra_compile_args,
            language="c",
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
        },
    )


if __name__ == "__main__":
    setup(ext_modules=build_extension())
