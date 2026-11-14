"""Pytest fixtures shared across the test suite."""

import pytest


@pytest.fixture
def db_path(tmp_path) -> str:
    """A throwaway SQLite database path unique to each test."""

    return str(tmp_path / "test_elt.db")
