"""Tests for repo detection and the .fdocrc version pin."""

from fdoc.commands.create import (
    find_legacy_submodule,
    is_dev_checkout,
)
from fdoc.config import (
    LATEX_TOOLS_VERSION_KEY,
    get_latex_tools_version,
    set_latex_tools_version,
)
from fdoc.config import _load_yaml_file


def test_is_dev_checkout(tmp_path):
    assert not is_dev_checkout(tmp_path)
    for sub in ("classes", "packages", "lua"):
        (tmp_path / sub).mkdir()
    assert is_dev_checkout(tmp_path)


def test_find_legacy_submodule(tmp_path):
    assert find_legacy_submodule(tmp_path) is None
    (tmp_path / "latex-tools" / "classes").mkdir(parents=True)
    assert find_legacy_submodule(tmp_path) == tmp_path / "latex-tools"


def test_pin_roundtrip_preserves_other_keys(tmp_path):
    # Seed an .fdocrc with an unrelated key.
    (tmp_path / ".fdocrc").write_text("project: My Project\nsync: true\n")
    set_latex_tools_version(tmp_path, "2.1.0")

    data = _load_yaml_file(tmp_path / ".fdocrc")
    assert data[LATEX_TOOLS_VERSION_KEY] == "2.1.0"
    # Existing keys survive the rewrite.
    assert data["project"] == "My Project"
    assert data["sync"] is True

    assert get_latex_tools_version(data) == "2.1.0"


def test_pin_overwrites_existing(tmp_path):
    set_latex_tools_version(tmp_path, "1.0.0")
    set_latex_tools_version(tmp_path, "1.1.0")
    data = _load_yaml_file(tmp_path / ".fdocrc")
    assert data[LATEX_TOOLS_VERSION_KEY] == "1.1.0"


def test_get_version_none_when_absent():
    assert get_latex_tools_version({}) is None
