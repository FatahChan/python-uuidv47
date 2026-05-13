#!/usr/bin/env bash
# Build one manylinux wheel (selector via CIBW_BUILD) and run tests against a clean venv.
# Used on PR CI and in the release workflow before PyPI upload.
set -euxo pipefail

: "${CIBW_BUILD:=cp311-manylinux_x86_64}"

python -m pip install --upgrade pip
pip install cibuildwheel
cibuildwheel --platform linux --output-dir wheelhouse .

WHEEL="$(ls wheelhouse/python_uuidv47-*.whl | head -n1)"
test -n "${WHEEL}"

python -m venv .venv-wheeltest
.venv-wheeltest/bin/pip install --upgrade pip
.venv-wheeltest/bin/pip install pytest "${WHEEL}"
.venv-wheeltest/bin/python -m pytest \
  tests/test_wheel_package.py \
  tests/test_uuidv47.py \
  tests/test_error_handling.py \
  -v --tb=short
