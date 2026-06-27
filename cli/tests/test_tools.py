"""Tests for the versioned latex-tools runtime install (fdoc.tools)."""

import zipfile

import pytest

from fdoc import tools


def _make_fake_runtime(root):
    """Create a minimal runtime tree (the sentinel files) under `root`."""
    (root / "classes").mkdir(parents=True)
    (root / "packages").mkdir(parents=True)
    (root / "lua").mkdir(parents=True)
    (root / "assets").mkdir(parents=True)
    (root / "classes" / "datasheet.cls").write_text("% fake cls\n")
    (root / "packages" / "fiddlie-common.sty").write_text("% fake sty\n")
    (root / "lua" / "fa-icons.lua").write_text("return {}\n")
    (root / "assets" / "logo.txt").write_text("logo\n")
    return root


@pytest.fixture(autouse=True)
def _isolate_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("FDOC_LATEX_TOOLS_HOME", str(tmp_path / "cache"))
    # Make sure no real download is ever attempted by these tests.
    monkeypatch.delenv("FDOC_LATEX_TOOLS_SOURCE", raising=False)


def test_cache_root_honours_env(tmp_path, monkeypatch):
    monkeypatch.setenv("FDOC_LATEX_TOOLS_HOME", str(tmp_path / "x"))
    assert tools.cache_root() == tmp_path / "x"


def test_install_from_directory(tmp_path):
    src = _make_fake_runtime(tmp_path / "src")
    assert not tools.is_installed("1.2.3")
    tools.install("1.2.3", source=str(src))
    assert tools.is_installed("1.2.3")
    assert "1.2.3" in tools.installed_versions()


def test_texinputs_points_at_version_dir(tmp_path):
    src = _make_fake_runtime(tmp_path / "src")
    tools.install("2.0.0", source=str(src))
    ti = tools.texinputs("2.0.0")
    assert ti.endswith(":")
    assert str(tools.install_dir("2.0.0") / "classes") + "//" in ti
    # Each runtime subtree appears.
    for sub in ("classes", "packages", "lua"):
        assert f"{sub}//" in ti


def test_bundle_roundtrips_into_install(tmp_path):
    repo = _make_fake_runtime(tmp_path / "repo")
    out = tmp_path / "dist"
    zip_path = tools.make_bundle(repo, out, "9.9.9")
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    assert "classes/datasheet.cls" in names
    # No build tooling leaks into the runtime bundle.
    assert not any(n.startswith("cli/") for n in names)

    tools.install("9.9.9", source=str(zip_path))
    assert tools.is_installed("9.9.9")


def test_install_rejects_bundle_missing_required_subtrees(tmp_path):
    bad = tmp_path / "bad"
    (bad / "classes").mkdir(parents=True)  # packages/ and lua/ missing
    with pytest.raises(FileNotFoundError):
        tools.install("0.0.1", source=str(bad))


def test_ensure_is_idempotent(tmp_path):
    src = _make_fake_runtime(tmp_path / "src")
    assert tools.ensure("3.1.4", source=str(src)) is True
    assert tools.ensure("3.1.4", source=str(src)) is False


def test_docs_base_url():
    assert tools.docs_base_url("2.1.0").endswith("/blob/v2.1.0/docs")
