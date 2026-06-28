"""Tests for FontAwesome install helpers (fdoc.fonts)."""

from fdoc import fonts


def test_spaceless_aliases_created(tmp_path):
    spaced = tmp_path / "Font Awesome 7 Pro-Solid-900.otf"
    spaced.write_text("otf")
    plain = tmp_path / "already-spaceless.otf"
    plain.write_text("otf")

    fonts._add_spaceless_aliases(tmp_path)

    alias = tmp_path / "FontAwesome7Pro-Solid-900.otf"
    assert alias.exists()
    # The alias resolves to the spaced original.
    assert alias.read_text() == "otf"
    # Files without spaces get no extra alias.
    assert not (tmp_path / "already-spaceless.otf.alias").exists()


def test_spaceless_aliases_idempotent(tmp_path):
    (tmp_path / "Font Awesome 7 Pro-Regular-400.otf").write_text("x")
    fonts._add_spaceless_aliases(tmp_path)
    # Second run must not raise even though the alias already exists.
    fonts._add_spaceless_aliases(tmp_path)
    assert (tmp_path / "FontAwesome7Pro-Regular-400.otf").exists()
