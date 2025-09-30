#!/usr/bin/env python3
"""
Header download script for python-uuidv47

Downloads the uuidv47.h header file from the upstream repository
to ensure we use the same C implementation as the Node.js version.
"""

import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def download_header():
    """Download uuidv47.h from upstream repository"""
    header_path = Path(__file__).parent / "uuidv47.h"

    if header_path.exists():
        print(f"Header {header_path} already exists")
        return True

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


if __name__ == "__main__":
    success = download_header()
    sys.exit(0 if success else 1)
