"""fdoc - CLI tool for managing Fiddlie documentation repositories."""

from __future__ import annotations


def _resolve_version() -> str:
    # Prefer the installed package metadata (set from the git tag at build time).
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            return version("fdoc")
        except PackageNotFoundError:
            pass
    except Exception:
        pass
    # Fall back to the file hatch-vcs writes into the source tree, then to a
    # sentinel so imports never fail in an unbuilt checkout.
    try:
        from fdoc._version import __version__ as _v  # type: ignore

        return _v
    except Exception:
        return "0+unknown"


__version__ = _resolve_version()
