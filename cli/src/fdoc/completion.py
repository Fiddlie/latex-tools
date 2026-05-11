"""Shell completion helpers for fdoc commands."""

from fdoc.commands.create import find_repo_root
from fdoc.commands.list import find_documents


def complete_docname(ctx, param, incomplete: str) -> list[str]:
    # Stay silent (return []) when outside a docs repo so completion doesn't error.
    repo_root = find_repo_root()
    if repo_root is None:
        return []
    return [d["name"] for d in find_documents(repo_root) if d["name"].startswith(incomplete)]
