# fdoc installers

Self-contained, per-OS installers so non-technical users can set up `fdoc`
without Python, git, or private-repo access.

Each installer zip contains:

```
bin/fdoc[.exe]                          standalone fdoc (PyInstaller; no Python needed)
payload/fonts/*.otf                     FontAwesome Pro OTFs
payload/latex-tools-runtime-vX.Y.Z.zip  the pinned runtime bundle
install.sh | install.ps1                seeds everything offline via `fdoc setup`
```

The FontAwesome fonts ride **inside** the installer (an access-controlled
artifact), so the FA Pro license is respected and the user never needs a token
or a download — first run is fully offline.

## Building

CI builds these on each published release (`.github/workflows/installer.yml`)
and attaches them to the release. To build one locally for the current OS:

```bash
pip install ./cli pyinstaller
python installer/build.py --version 2.1.0 --fonts-kit /path/to/fa-kit.zip
# -> dist-installer/fdoc-installer-<os>-<arch>-v2.1.0.zip
```

`--fonts-kit` is the FontAwesome kit zip (or an extracted directory); it also
reads `$FDOC_FA_KIT_SOURCE`.

## Signing (TODO)

The macOS and Windows binaries are currently **unsigned**, so users get
Gatekeeper / SmartScreen warnings. Once an Apple Developer ID and a Windows
code-signing certificate are available, add the notarize/sign steps at the
marked `TODO(signing)` point in `installer.yml`.
