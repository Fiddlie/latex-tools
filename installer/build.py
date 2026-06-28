#!/usr/bin/env python3
"""Build a self-contained fdoc installer for the current OS.

Produces a single zip that contains:

    bin/fdoc[.exe]                          a standalone fdoc (no Python needed)
    payload/fonts/*.otf                     the FontAwesome Pro OTFs
    payload/latex-tools-runtime-vX.Y.Z.zip  the pinned runtime bundle
    install.sh | install.ps1                seeds everything offline via `fdoc setup`

The end user unzips it and runs the install script — no Python, no git, no
private-repo access, no network. The FontAwesome fonts travel inside the
installer (an access-controlled artifact), respecting the FA Pro license.

Usage:
    python installer/build.py --version 2.1.0 --fonts-kit /path/to/fa-kit.zip
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI_SRC = REPO / "cli" / "src"
HERE = Path(__file__).resolve().parent


def os_slug() -> str:
    return {"darwin": "macos", "windows": "windows", "linux": "linux"}.get(
        platform.system().lower(), platform.system().lower()
    )


def arch_slug() -> str:
    m = platform.machine().lower()
    return {"amd64": "x86_64", "x64": "x86_64", "aarch64": "arm64"}.get(m, m or "unknown")


def _extract_otfs(fonts_kit: Path, dest: Path) -> int:
    """Copy every .otf from a FA kit (zip or directory) into `dest`."""
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    if fonts_kit.is_dir():
        for otf in fonts_kit.rglob("*.otf"):
            shutil.copy2(otf, dest / otf.name)
            count += 1
    elif fonts_kit.suffix == ".zip":
        with zipfile.ZipFile(fonts_kit) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".otf"):
                    target = dest / Path(name).name
                    with zf.open(name) as src, open(target, "wb") as out:
                        shutil.copyfileobj(src, out)
                    count += 1
    else:
        raise SystemExit(f"--fonts-kit must be a .zip or directory: {fonts_kit}")
    if count == 0:
        raise SystemExit(f"No .otf files found in {fonts_kit}")
    return count


def _build_binary(workdir: Path) -> Path:
    """Build a one-file fdoc binary with PyInstaller. Returns its path."""
    sep = ";" if os.name == "nt" else ":"
    add_data = f"{CLI_SRC / 'fdoc' / 'templates'}{sep}fdoc/templates"
    dist = workdir / "dist"
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--onefile", "--name", "fdoc",
            "--add-data", add_data,
            "--clean", "--noconfirm", "--log-level", "WARN",
            "--distpath", str(dist),
            "--workpath", str(workdir / "build"),
            "--specpath", str(workdir),
            str(HERE / "fdoc_entry.py"),
        ],
        check=True,
    )
    exe = dist / ("fdoc.exe" if os.name == "nt" else "fdoc")
    if not exe.is_file():
        raise SystemExit(f"PyInstaller did not produce {exe}")
    return exe


def _render_install_script(staging: Path, version: str) -> None:
    if os.name == "nt":
        tmpl = (HERE / "install.ps1.in").read_text()
        (staging / "install.ps1").write_text(tmpl.replace("@VERSION@", version))
    else:
        tmpl = (HERE / "install.sh.in").read_text()
        script = staging / "install.sh"
        script.write_text(tmpl.replace("@VERSION@", version))
        script.chmod(0o755)


def _zip_dir(src: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src.rglob("*")):
            if path.is_file():
                arc = path.relative_to(src)
                zi = zipfile.ZipInfo(arc.as_posix())
                zi.compress_type = zipfile.ZIP_DEFLATED
                # Preserve the exec bit for binaries / scripts.
                mode = path.stat().st_mode
                zi.external_attr = (mode & 0o7777) << 16
                zf.writestr(zi, path.read_bytes())


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a self-contained fdoc installer.")
    ap.add_argument("--version", required=True, help="Runtime/installer version (e.g. 2.1.0).")
    ap.add_argument(
        "--fonts-kit",
        default=os.environ.get("FDOC_FA_KIT_SOURCE"),
        help="FontAwesome kit (.zip or dir). Defaults to $FDOC_FA_KIT_SOURCE.",
    )
    ap.add_argument("--output", default=str(REPO / "dist-installer"), help="Output directory.")
    args = ap.parse_args()

    if not args.fonts_kit:
        raise SystemExit("--fonts-kit (or $FDOC_FA_KIT_SOURCE) is required.")
    fonts_kit = Path(args.fonts_kit).expanduser().resolve()
    version = args.version
    output = Path(args.output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(CLI_SRC))
    from fdoc import tools  # noqa: E402 - after sys.path tweak

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        staging = work / "staging"
        (staging / "bin").mkdir(parents=True)
        payload = staging / "payload"
        payload.mkdir()

        print(f"[1/4] Runtime bundle for {version}...")
        tools.make_bundle(REPO, payload, version)

        print("[2/4] FontAwesome OTFs...")
        n = _extract_otfs(fonts_kit, payload / "fonts")
        print(f"      {n} OTFs")

        print("[3/4] fdoc binary (PyInstaller)...")
        exe = _build_binary(work)
        shutil.copy2(exe, staging / "bin" / exe.name)

        print("[4/4] Assembling installer...")
        _render_install_script(staging, version)
        zip_path = output / f"fdoc-installer-{os_slug()}-{arch_slug()}-v{version}.zip"
        if zip_path.exists():
            zip_path.unlink()
        _zip_dir(staging, zip_path)

    size_mb = zip_path.stat().st_size / 1e6
    print(f"\nWrote {zip_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
