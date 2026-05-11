# Policy Document Class

Internal policy documentation for Fiddlie.

## Usage

```latex
\documentclass{policy}

\title{Policy Name}
\shorttitle{Short Name}
\author{Author Name}
\date{January 2026}
\documentId{FD-DC-LTX-12345}
\revision{A-rc1}
\draft  % Optional: adds draft watermark

\begin{document}
  \maketitle
  \tableofcontents

  \section{Purpose}
  % Content...
\end{document}
```

## With Manifest

```latex
\documentclass{policy}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  \tableofcontents

  \section{Purpose}
  % Content...

  \makerevisionhistory
\end{document}
```

## Features

- A4 paper, 11pt Arial font
- 2cm left/right margins, 3cm top/bottom
- Each section starts on a new page
- Headers: Section name (left), Short title (center), Company logo (right)
- Footers: Revision (left), Date (center), Page X of Y (right)
- First page has no header, footer only
- **No legal disclaimer** — policy documents are internal and do not include the `\importantnotice` section used by datasheets

## Commands

### Document Metadata

- `\title{}` - Full document title
- `\shorttitle{}` - Abbreviated title for headers
- `\author{}` - Document author
- `\date{}` - Document date
- `\documentId{}` - Document ID (e.g., FD-DC-LTX-12345)
- `\revision{}` - Revision string (e.g., A-rc1, B)
- `\draft` - Add draft watermark
- `\setlogo{filename}` - Override the default logo (use in preamble)

### Document Structure

- `\maketitle` - Generate title page
- `\makerevisionhistory` - Generate revision history table (requires manifest)
- `\companylogo` - Insert company logo (default height 0.6cm)
- `\companylogo[height=1.2cm]` - Insert company logo with custom height
- `\revisionnumber` - Output current revision inline

## Creating a New Policy

Use the `fdoc` CLI to create a new policy:

```bash
# With full options
fdoc create policy --title "Code Review Policy" --id "FD-DC-LTX-10001"

# Quick start with defaults
fdoc create policy

# Without manifest (manual metadata)
fdoc create policy --title "My Policy" --no-manifest
```

## Building

From the document directory:

```bash
fdoc build .
```

Or from the repository root:

```bash
fdoc build code-review-policy
```
