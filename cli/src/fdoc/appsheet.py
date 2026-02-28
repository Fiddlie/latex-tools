"""fdoc appsheet - AppSheet API client for document tracking."""

import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional

import click

from fdoc.config import get_appsheet_api_key, get_appsheet_app_id


def _api_request(
    table: str,
    action: str,
    rows: Optional[list] = None,
    selector: Optional[str] = None,
    config: Optional[dict] = None,
) -> list:
    """Make an AppSheet API request.

    Args:
        table: Table name (e.g., "Projects", "Documents")
        action: API action ("Add", "Find", "Edit", "Delete")
        rows: List of row dicts for Add/Edit actions
        selector: Filter expression for Find action
        config: Pre-loaded config dict (optional)

    Returns:
        List of result row dicts.
    """
    api_key = get_appsheet_api_key(config)
    if not api_key:
        raise click.ClickException(
            "AppSheet API key not configured. "
            "Set FDOC_APPSHEET_API_KEY environment variable or "
            "add appsheet_api_key to ~/.fdocrc"
        )

    app_id = get_appsheet_app_id(config)
    url = f"https://api.appsheet.com/api/v2/apps/{app_id}/tables/{table}/Action"

    body = {
        "Action": action,
        "Properties": {"Locale": "en-US"},
    }

    if rows is not None:
        body["Rows"] = rows

    if selector is not None:
        body["Properties"]["Selector"] = selector

    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "ApplicationAccessKey": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            if isinstance(result, list):
                return result
            # Add/Edit responses wrap rows in a {"Rows": [...]} dict
            if isinstance(result, dict) and "Rows" in result:
                return result["Rows"]
            return [result] if result else []
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise click.ClickException(
            f"AppSheet API error ({e.code}): {error_body}"
        )
    except urllib.error.URLError as e:
        raise click.ClickException(
            f"Failed to connect to AppSheet API: {e.reason}"
        )


def get_active_projects(config: Optional[dict] = None) -> list[dict]:
    """Fetch all active projects from AppSheet."""
    return _api_request(
        table="Projects",
        action="Find",
        selector='Filter(Projects, [Status] = "ACTIVE")',
        config=config,
    )


def create_document(
    title: str,
    project_id: str,
    revision: str,
    config: Optional[dict] = None,
) -> dict:
    """Create a new LTX document in AppSheet.

    Returns the created row dict (including auto-generated Document No).
    """
    rows = _api_request(
        table="Documents",
        action="Add",
        rows=[{
            "Row ID": "",
            "Title": title,
            "Type": "LTX",
            "Project Id": project_id,
            "Date Created": datetime.now().strftime("%m/%d/%Y"),
            "Revision": revision,
        }],
        config=config,
    )

    if not rows:
        raise click.ClickException("AppSheet returned no data after creating document.")

    created = rows[0]

    # The Add response may not include computed fields like Document No.
    # Re-fetch the row by its Row ID to get all fields.
    if created.get("Document No") is None:
        row_id = created.get("Row ID")
        if row_id:
            fetched = _api_request(
                table="Documents",
                action="Find",
                selector=f'Filter(Documents, [Row ID] = "{row_id}")',
                config=config,
            )
            if fetched:
                created = fetched[0]

    return created


def update_document_revision(
    document_no: int,
    revision: str,
    config: Optional[dict] = None,
):
    """Update the revision field of a document by its Document No."""
    # AppSheet Edit requires the row key field (Row ID).
    # First find the document to get its Row ID.
    doc = find_document_by_number(document_no, config)
    if doc is None:
        raise click.ClickException(
            f"Document No {document_no} not found in AppSheet."
        )

    row_id = doc.get("Row ID") or doc.get("Id")
    if not row_id:
        raise click.ClickException(
            f"Could not determine Row ID for Document No {document_no}."
        )

    _api_request(
        table="Documents",
        action="Edit",
        rows=[{
            "Row ID": row_id,
            "Revision": revision,
        }],
        config=config,
    )


def find_document_by_number(
    document_no: int,
    config: Optional[dict] = None,
) -> Optional[dict]:
    """Find a document by its Document No."""
    rows = _api_request(
        table="Documents",
        action="Find",
        selector=f'Filter(Documents, [Document No] = {document_no})',
        config=config,
    )
    return rows[0] if rows else None
