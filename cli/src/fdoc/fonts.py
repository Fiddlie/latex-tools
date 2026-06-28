"""FontAwesome Pro install/ensure logic for fdoc.

Fonts live under TEXMFHOME so a single install on a machine serves every
documentation repo that uses fdoc. The LaTeX side (fiddlie-icons.sty)
finds them by filename through kpse/luaotfload — it doesn't need to know
the install path.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable, Optional

# Pin to a specific FA kit version. Bump when uploading a new release.
FA_KIT_VERSION = "2026.05.16"

# Default download URL. Override per-environment with FDOC_FA_KIT_SOURCE
# (URL or local path), or per-invocation with --source.
FA_KIT_URL = (
    "https://github.com/fiddlie/latex-tools/releases/download/"
    f"fa-kit-v{FA_KIT_VERSION}/fa-kit-v{FA_KIT_VERSION}.zip"
)

# Subpath under TEXMFHOME where the OTFs are placed. luaotfload reads from
# any opentype/ tree under TEXMFHOME automatically.
FONT_INSTALL_SUBPATH = Path("fonts/opentype/fiddlie")

# Files we expect after a successful install — used as a quick liveness
# check by is_installed().
SENTINEL_FONTS = (
    "Font Awesome 7 Pro-Solid-900.otf",
    "Font Awesome 7 Brands-Regular-400.otf",
)

ProgressFn = Callable[[str], None]


def texmfhome() -> Path:
    result = subprocess.run(
        ["kpsewhich", "-var-value", "TEXMFHOME"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip()).expanduser()


def font_install_dir() -> Path:
    return texmfhome() / FONT_INSTALL_SUBPATH


def is_installed() -> bool:
    d = font_install_dir()
    return all((d / name).is_file() for name in SENTINEL_FONTS)


def resolved_source(source: Optional[str]) -> str:
    """Resolve the kit source. Explicit --source wins, then env, then default."""
    return source or os.environ.get("FDOC_FA_KIT_SOURCE") or FA_KIT_URL


def install(
    source: Optional[str] = None,
    *,
    force: bool = False,
    on_progress: Optional[ProgressFn] = None,
) -> Path:
    """Install the FA kit into TEXMFHOME and return the install directory.

    `source` may be an http(s) URL, a path to a zip file, or a path to an
    already-extracted kit directory containing an otfs/ subfolder.
    """
    target = font_install_dir()
    if is_installed() and not force:
        return target

    report = on_progress or (lambda _msg: None)
    target.mkdir(parents=True, exist_ok=True)
    src = resolved_source(source)
    report(f"Resolving kit from: {src}")

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        if src.startswith(("http://", "https://")):
            zip_path = td_path / "kit.zip"
            report("Downloading kit zip…")
            urllib.request.urlretrieve(src, zip_path)
            kit_root = _extract_kit_zip(zip_path, td_path / "extracted")
        else:
            src_path = Path(src).expanduser().resolve()
            if src_path.is_dir():
                kit_root = src_path
            elif src_path.is_file() and src_path.suffix == ".zip":
                kit_root = _extract_kit_zip(src_path, td_path / "extracted")
            else:
                raise FileNotFoundError(
                    f"Kit source not found or unsupported: {src}"
                )

        otfs_dir = kit_root / "otfs" if (kit_root / "otfs").is_dir() else kit_root
        otfs = sorted(otfs_dir.glob("*.otf"))
        if not otfs:
            raise FileNotFoundError(f"No .otf files found in {otfs_dir}")

        report(f"Installing {len(otfs)} OTFs into {target}…")
        for otf in otfs:
            shutil.copy2(otf, target / otf.name)

    _add_spaceless_aliases(target)
    report("Refreshing luaotfload font database…")
    _refresh_font_cache()
    return target


def ensure(
    *,
    source: Optional[str] = None,
    on_progress: Optional[ProgressFn] = None,
) -> bool:
    """Install fonts if missing. Returns True iff an install was performed."""
    if is_installed():
        return False
    if on_progress is not None:
        on_progress("FontAwesome fonts not installed — installing now (one-off, ~62MB).")
    install(source=source, on_progress=on_progress)
    return True


def _extract_kit_zip(zip_path: Path, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    # FA kit zips contain a single top-level directory (e.g. kit-XXXX-desktop).
    entries = [p for p in dest.iterdir() if not p.name.startswith(".")]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return dest


def _add_spaceless_aliases(target: Path) -> None:
    """Add spaceless-named aliases next to OTFs whose filenames contain spaces.

    The FA Pro OTF filenames contain spaces (e.g. "Font Awesome 7 Pro-Solid-
    900.otf"). On older TeX Live (~2023), fontspec strips the spaces before the
    lookup and reports the font as not found. Providing a spaceless alias
    ("FontAwesome7Pro-Solid-900.otf") makes the lookup resolve there. Harmless
    on newer TeX Live, which resolves the spaced name directly.
    """
    for otf in list(target.glob("*.otf")):
        if " " not in otf.name:
            continue
        alias = target / otf.name.replace(" ", "")
        if alias.exists():
            continue
        try:
            alias.symlink_to(otf.name)  # relative symlink within the dir
        except (OSError, NotImplementedError):
            # Windows without symlink privilege, or other FS limitation.
            try:
                shutil.copy2(otf, alias)
            except OSError:
                pass


def _refresh_font_cache() -> None:
    # luaotfload rebuilds its database lazily on next compile anyway, so
    # a refresh failure here isn't fatal.
    try:
        subprocess.run(
            ["luaotfload-tool", "--update"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
