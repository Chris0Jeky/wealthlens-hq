"""Tests for the registry directory resolver (in-repo + packaged-wheel strategies)."""

from __future__ import annotations

from pathlib import Path

import pytest

from wealthlens_sim._registry_path import find_registries_dir


class TestFindRegistriesDir:
    def test_walks_up_to_repo_root_registries(self, tmp_path: Path):
        """Strategy 1: a registries/ directory found by walking up is returned."""
        registries = tmp_path / "registries"
        registries.mkdir()
        nested = tmp_path / "pkg" / "wealthlens_sim"
        nested.mkdir(parents=True)
        assert find_registries_dir(start=nested) == registries

    def test_packaged_registries_fallback(self, tmp_path: Path):
        """Strategy 2: with no registries/ ancestor, the packaged _registries/ wins."""
        pkg = tmp_path / "wealthlens_sim"
        pkg.mkdir()
        packaged = pkg / "_registries"
        packaged.mkdir()
        assert find_registries_dir(start=pkg) == packaged

    def test_walk_up_preferred_over_packaged(self, tmp_path: Path):
        """When both exist, the canonical repo-root registries/ takes precedence."""
        registries = tmp_path / "registries"
        registries.mkdir()
        pkg = tmp_path / "wealthlens_sim"
        pkg.mkdir()
        (pkg / "_registries").mkdir()
        assert find_registries_dir(start=pkg) == registries

    def test_raises_when_neither_found(self, tmp_path: Path):
        """A clear FileNotFoundError when no registries can be located."""
        empty = tmp_path / "isolated"
        empty.mkdir()
        with pytest.raises(FileNotFoundError, match="registries"):
            find_registries_dir(start=empty)

    def test_default_resolves_in_repo(self):
        """With no argument, the in-repo checkout resolves to a real directory."""
        found = find_registries_dir()
        assert found.is_dir()
        assert (found / "assumptions.yml").is_file()
