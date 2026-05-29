"""Smoke test: package imports and version string is set."""

from wealthlens_sim import __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)


def test_version_is_dev() -> None:
    assert "dev" in __version__
