#!/usr/bin/env python3
"""Regenerate lua/fa-icons.lua from the Font Awesome metadata bundle.

Reads assets/fonts/icons.json (shipped with the FA Pro download) and emits
a Lua module mapping each icon name to its hex codepoint, plus the set of
brand-only icons. Run after dropping a new icons.json into assets/fonts/.
"""
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
META = REPO_ROOT / "assets" / "fonts" / "icons.json"
OUT = REPO_ROOT / "lua" / "fa-icons.lua"


def main() -> None:
    icons = json.loads(META.read_text())

    codepoints: list[tuple[str, str]] = []
    brand_only: list[str] = []
    for name in sorted(icons):
        entry = icons[name]
        cp = entry.get("unicode")
        if not cp:
            continue
        codepoints.append((name, cp))
        if entry.get("styles") == ["brands"]:
            brand_only.append(name)

    lines: list[str] = []
    lines.append("-- fa-icons.lua - Font Awesome icon name -> codepoint lookup")
    lines.append(f"-- Auto-generated from assets/fonts/icons.json ({len(codepoints)} icons)")
    lines.append("-- Regenerate with: python3 scripts/regenerate-fa-icons.py")
    lines.append("local M = {}")
    lines.append("")
    lines.append("M.codepoints = {")
    for name, cp in codepoints:
        lines.append(f'  ["{name}"] = "{cp}",')
    lines.append("}")
    lines.append("")
    lines.append("M.brand_only = {")
    for name in brand_only:
        lines.append(f'  ["{name}"] = true,')
    lines.append("}")
    lines.append("")
    lines.append("return M")
    lines.append("")

    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT.relative_to(REPO_ROOT)}: {len(codepoints)} icons "
          f"({len(brand_only)} brand-only)")


if __name__ == "__main__":
    main()
