"""
Pytest configuration file for async tests.
"""

import pytest

# Configure pytest to use asyncio
pytest_plugins = ("pytest_asyncio",)

# Set default timeout for async tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    ) 