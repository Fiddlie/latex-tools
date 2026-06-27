"""Versioned latex-tools runtime install/ensure logic for fdoc.

Consuming repositories pin a latex-tools version in `.fdocrc`
(`latex_tools_version`) instead of vendoring the whole repo as a submodule.
The pinned version's *runtime* — just the LaTeX classes, packages, Lua
modules and shared assets needed to build — is downloaded once per machine
into a versioned cache directory and reused by every project that pins it.

This mirrors fonts.py (FontAwesome Pro install), but is version-aware so
multiple pinned versions can coexist side by side and each project selects
its own at build time via TEXINPUTS. Versions never collide because each
lives under its own directory and is added to TEXINPUTS explicitly, rather
than relying on kpse auto-discovery under TEXMFHOME.
"""
from __future__ import annotations

import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable, List, Optional

# The runtime subtrees a document needs in order to build. Everything else in
# the repo (cli/, docs/, examples/, scripts/) is build-irrelevant.
RUNTIME_SUBDIRS = ("classes", "packages", "lua", "assets")

# Files we expect after a successful install — a quick liveness check.
SENTINEL_FILES = (
    "packages/fiddlie-common.sty",
    "classes/datasheet.cls",
    "lua/fa-icons.lua",
)

# Release-artifact URL for a given version's runtime bundle. Override the whole
# URL/path per-environment with FDOC_LATEX_TOOLS_SOURCE, or per-call with
# `source`. Tags are vX.Y.Z; the bundle is attached to that GitHub release.
RUNTIME_URL_TEMPLATE = (
    "https://github.com/fiddlie/latex-tools/releases/download/"
    "v{version}/latex-tools-runtime-v{version}.zip"
)

# Where the authoring guides (docs/CLAUDE_*.md) live for a pinned version.
# Used in generated CLAUDE.md files, since consuming repos no longer vendor
# the docs/ tree via a submodule.
DOCS_URL_TEMPLATE = "https://github.com/fiddlie/latex-tools/blob/v{version}/docs"


def docs_base_url(version: str) -> str:
    return DOCS_URL_TEMPLATE.format(version=version)


ProgressFn = Callable[[str], None]


def cache_root() -> Path:
    """Base directory holding one subdirectory per installed version.

    Honours FDOC_LATEX_TOOLS_HOME, then XDG_CACHE_HOME, else ~/.cache.
    """
    override = os.environ.get("FDOC_LATEX_TOOLS_HOME")
    if override:
        return Path(override).expanduser()
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".cache"
    return base / "fdoc" / "latex-tools"


def install_dir(version: str) -> Path:
    """Directory where a given version's runtime is (or will be) installed."""
    return cache_root() / version


def is_installed(version: str) -> bool:
    d = install_dir(version)
    return all((d / rel).is_file() for rel in SENTINEL_FILES)


def texinputs(version: str) -> str:
    """TEXINPUTS prefix (with trailing colon) for a pinned, installed version."""
    return texinputs_for_dir(install_dir(version))


def texinputs_for_dir(root: Path) -> str:
    """TEXINPUTS prefix for a runtime tree rooted at `root` (dir per subtree).

    Uses the `//` recursive marker for each subtree and a trailing empty entry
    so the system default search path is still consulted.
    """
    root = Path(root)
    parts = [f"{root / sub}//" for sub in ("classes", "packages", "lua")]
    return ":".join(parts) + ":"


def resolved_source(version: str, source: Optional[str]) -> str:
    """Resolve the bundle source. Explicit `source` wins, then env, then URL."""
    return (
        source
        or os.environ.get("FDOC_LATEX_TOOLS_SOURCE")
        or RUNTIME_URL_TEMPLATE.format(version=version)
    )


def installed_versions() -> List[str]:
    root = cache_root()
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir() and is_installed(p.name))


def install(
    version: str,
    *,
    source: Optional[str] = None,
    force: bool = False,
    on_progress: Optional[ProgressFn] = None,
) -> Path:
    """Install a version's runtime into the cache and return its directory.

    `source` may be an http(s) URL, a path to a zip, or a path to an already
    extracted runtime directory (one containing classes/, packages/, ...).
    """
    target = install_dir(version)
    if is_installed(version) and not force:
        return target

    report = on_progress or (lambda _msg: None)
    src = resolved_source(version, source)
    report(f"Resolving latex-tools {version} from: {src}")

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        if src.startswith(("http://", "https://")):
            zip_path = td_path / "runtime.zip"
            report("Downloading runtime bundle…")
            urllib.request.urlretrieve(src, zip_path)
            bundle_root = _extract_zip(zip_path, td_path / "extracted")
        else:
            src_path = Path(src).expanduser().resolve()
            if src_path.is_dir():
                bundle_root = src_path
            elif src_path.is_file() and src_path.suffix == ".zip":
                bundle_root = _extract_zip(src_path, td_path / "extracted")
            else:
                raise FileNotFoundError(
                    f"latex-tools source not found or unsupported: {src}"
                )

        bundle_root = _locate_runtime_root(bundle_root)
        missing = [s for s in RUNTIME_SUBDIRS if not (bundle_root / s).is_dir()]
        # assets/ is optional in principle; classes/packages/lua are not.
        required_missing = [s for s in missing if s != "assets"]
        if required_missing:
            raise FileNotFoundError(
                f"Bundle is missing required subtrees {required_missing} in {bundle_root}"
            )

        # Install atomically-ish: build into a temp dir next to the target,
        # then swap, so a failed copy never leaves a half-populated version.
        staging = target.parent / f".{version}.partial"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=True)
        for sub in RUNTIME_SUBDIRS:
            srcsub = bundle_root / sub
            if srcsub.is_dir():
                shutil.copytree(srcsub, staging / sub)
        report(f"Installing runtime into {target}…")
        if target.exists():
            shutil.rmtree(target)
        staging.replace(target)

    return target


def ensure(
    version: str,
    *,
    source: Optional[str] = None,
    on_progress: Optional[ProgressFn] = None,
) -> bool:
    """Install a version's runtime if missing. Returns True iff installed now."""
    if is_installed(version):
        return False
    if on_progress is not None:
        on_progress(f"latex-tools {version} not installed — installing now.")
    install(version, source=source, on_progress=on_progress)
    return True


def make_bundle(repo_root: Path, out_dir: Path, version: str) -> Path:
    """Zip the runtime subtrees of a latex-tools checkout into a release bundle.

    Produces `latex-tools-runtime-v<version>.zip` with classes/, packages/,
    lua/ and assets/ at the top level. Used by the release workflow and for
    local testing of the install path.
    """
    repo_root = Path(repo_root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"latex-tools-runtime-v{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for sub in RUNTIME_SUBDIRS:
            base = repo_root / sub
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(repo_root).as_posix())
    return zip_path


def _extract_zip(zip_path: Path, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    return dest


def _locate_runtime_root(root: Path) -> Path:
    """Return the directory that directly contains the runtime subtrees.

    Handles bundles whose contents are nested one level inside a wrapper
    directory (e.g. a GitHub source zip "latex-tools-<sha>/...").
    """
    if any((root / s).is_dir() for s in RUNTIME_SUBDIRS):
        return root
    entries = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")]
    if len(entries) == 1 and any((entries[0] / s).is_dir() for s in RUNTIME_SUBDIRS):
        return entries[0]
    return root
