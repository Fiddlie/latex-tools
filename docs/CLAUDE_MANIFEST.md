# Manifest File Format

Reference guide for `manifest.yaml` files used in Fiddlie documents.

## Overview

The manifest file contains document metadata in YAML format. It's loaded automatically by the `fiddlie-manifest` package and provides values for title, author, revision, and history.

## Basic Usage

In your LaTeX document:

```latex
\documentclass{datasheet}  % or {requirements}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  % ... document content ...
\end{document}
```

## Complete Format

```yaml
document:
  title: "Full Document Title"
  shorttitle: "Short Title"
  author: "Author Name"
  date: "DD MMM YYYY"
  id: "FD-SEGMENT-TYPE-NUMBER"

revision:
  current: "A-rc1"
  draft: true

history:
  - revision: "A-rc1"
    date: "2025-01-17"
    author: "Author Name"
    changes: "Initial draft"
  - revision: "A-rc2"
    date: "2025-01-20"
    author: "Author Name"
    changes: "Updated specifications"
  - revision: "B"
    date: "2025-02-01"
    author: "Author Name"
    changes: "First release version"
```

## Field Descriptions

### document section

**title** (required)

- Full document title displayed on the title page
- Can be long and descriptive
- Example: `"ABC-123 Power Supply Unit Datasheet"`

**shorttitle** (required)

- Abbreviated title for headers
- Keep under 30 characters for good formatting
- Example: `"ABC-123 PSU"`

**author** (required)

- Document author name
- Can be a person or team
- Example: `"John Smith"` or `"Hardware Team"`

**date** (required)

- Document date in `DD MMM YYYY` format
- Example: `"15 Jan 2026"`, `"03 Feb 2026"`
- Use three-letter month abbreviations: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec

**id** (required)

- Document identifier in format `FD-SEGMENT-TYPE-NUMBER`
- Example: `"FD-DC-LTX-00001"` - Default format
- Should be unique within your organization

### revision section

**current** (required)

- Current revision identifier
- Common formats:
  - `"A-rc1"`, `"A-rc2"` - Release candidate versions
  - `"A"`, `"B"`, `"C"` - Released versions
  - `"1.0"`, `"1.1"`, `"2.0"` - Numeric versions
- Displayed in footer on every page

**draft** (required)

- Boolean: `true` or `false`
- When `true`: Shows "DRAFT" watermark diagonally across all pages
- When `false`: No watermark

### history section

Array of revision entries, each with:

**revision** (required)

- Revision identifier matching the format used in `revision.current`
- Example: `"A-rc1"`

**date** (required)

- Date of this revision in `DD MMM YYYY` format
- Example: `"15 Jan 2026"`

**author** (required)

- Who made this revision
- Example: `"John Smith"`

**changes** (required)

- Brief description of what changed
- Examples:
  - `"Initial draft"`
  - `"Updated electrical specifications"`
  - `"Added pin descriptions"`
  - `"Corrected typos in section 3"`

## Examples

### New Datasheet (Draft)

```yaml
document:
  title: "XYZ-500 Voltage Regulator Datasheet"
  shorttitle: "XYZ-500 Regulator"
  author: "Hardware Engineering"
  date: "13 Feb 2026"
  id: "FD-DC-LTX-001"

revision:
  current: "A-rc1"
  draft: true

history:
  - revision: "A-rc1"
    date: "13 Feb 2026"
    author: "Hardware Engineering"
    changes: "Initial draft"
```

### Released Requirements Document

```yaml
document:
  title: "Mobile App Requirements Specification"
  shorttitle: "Mobile App Reqs"
  author: "Product Team"
  date: "01 Feb 2026"
  id: "FD-DC-LTX-00002"

revision:
  current: "B"
  draft: false

history:
  - revision: "A-rc1"
    date: "15 Jan 2026"
    author: "Product Team"
    changes: "Initial draft"
  - revision: "A"
    date: "22 Jan 2026"
    author: "Product Team"
    changes: "First release"
  - revision: "B"
    date: "01 Feb 2026"
    author: "Product Team"
    changes: "Added performance requirements"
```

### Document with Multiple Revisions

```yaml
document:
  title: "ABC-100 System Specification"
  shorttitle: "ABC-100 Spec"
  author: "Systems Team"
  date: "10 Feb 2026"
  id: "FD-DC-LTX-100"

revision:
  current: "1.2"
  draft: false

history:
  - revision: "1.0"
    date: "15 Jan 2026"
    author: "Systems Team"
    changes: "Initial release"
  - revision: "1.1"
    date: "25 Jan 2026"
    author: "Systems Team"
    changes: "Updated power specifications, added thermal data"
  - revision: "1.2"
    date: "10 Feb 2026"
    author: "Systems Team"
    changes: "Corrected pin assignments in Section 4"
```

## Revision History Table

The `\makerevisionhistory` command in LaTeX automatically generates a table from the `history` section:

| Revision | Date        | Author     | Changes       |
| -------- | ----------- | ---------- | ------------- |
| A-rc1    | 15 Jan 2026 | John Smith | Initial draft |
| A-rc2    | 20 Jan 2026 | John Smith | Updated specs |
| B        | 01 Feb 2026 | John Smith | First release |

Always include `\makerevisionhistory` before `\importantnotice` at the end of your document.

## Best Practices

1. **Keep shorttitle concise** - Maximum ~30 characters to fit in headers
2. **Use consistent date format** - Always `DD MMM YYYY`
3. **Use semantic revision IDs** - Choose a scheme and stick to it
4. **Update history for every change** - Add new entry at the bottom
5. **Mark drafts clearly** - Set `draft: true` until officially released
6. **Increment revision properly** - Use `-rc1`, `-rc2` for candidates, then release without suffix
7. **Document ID should be unique** - Coordinate with your team on numbering

## Alternative: Manual Metadata

If you don't want to use a manifest, you can specify metadata manually:

```latex
\documentclass{datasheet}

\title{Full Document Title}
\shorttitle{Short Title}
\author{Author Name}
\date{February 2026}
\revision{A-rc1}
\documentId{FD-DC-LTX-00001}
\draft  % Optional: adds draft watermark

\begin{document}
  \maketitle
  % ... content ...
\end{document}
```

However, **manifest is recommended** because:

- Metadata is separate from LaTeX code
- Revision history is automatic
- Easier to maintain and update
- Better for version control
