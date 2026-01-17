"""Template loading utilities for fdoc."""

from pathlib import Path
from typing import List


def get_template(name: str) -> str:
    """Load a template file by name.

    Args:
        name: Template filename relative to the templates directory.
              Can include subdirectories (e.g., "datasheet/default.tex.j2")

    Returns:
        The template content as a string.

    Raises:
        FileNotFoundError: If the template doesn't exist.
    """
    template_dir = Path(__file__).parent
    template_path = template_dir / name

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {name}")

    return template_path.read_text()


def list_templates(doctype: str) -> List[str]:
    """List available templates for a document type.

    Args:
        doctype: Document type (e.g., "datasheet", "requirements")

    Returns:
        List of template names (without .tex.j2 extension)
    """
    template_dir = Path(__file__).parent / doctype
    if not template_dir.is_dir():
        return []

    templates = []
    for path in template_dir.glob("*.tex.j2"):
        name = path.stem.replace(".tex", "")
        # Skip no_manifest variants from the list
        if not name.endswith("_no_manifest"):
            templates.append(name)

    return sorted(templates)
