# tests/test_tests.py

import sys

def test_basic_math():
    """
    A trivial test to verify pytest is running.
    """
    assert 1 + 1 == 2, "Basic math failed, so something is off!"

def test_python_version():
    """
    This test checks if the Python version is at least 3.8.
    Adjust the version requirement as needed.
    """
    major, minor = sys.version_info[:2]
    assert (major == 3 and minor >= 8), (
        f"Expected Python 3.8+ but found Python {major}.{minor}."
    )

def test_pytest_is_installed():
    """
    A quick sanity check to ensure 'pytest' is recognized.
    The fact that we're running this test at all typically
    confirms pytest is installed, but let's be explicit.
    """
    try:
        import pytest  # noqa: F401  # just to check import
    except ImportError as e:
        assert False, f"pytest not installed or not found: {e}"
