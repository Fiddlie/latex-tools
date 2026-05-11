# Report Document Class

Engineering and research reports for Fiddlie. Implemented by the `techreport` class to avoid colliding with LaTeX's built-in `report` class.

## Usage

```latex
\documentclass{techreport}

\title{Report Title}
\shorttitle{Short Name}
\author{Author Name}
\date{January 2026}
\documentId{FD-DC-LTX-12345}
\revision{A-rc1}
\draft  % Optional: adds draft watermark

\begin{document}
  \maketitle
  \tableofcontents

  \section{Introduction}
  % Content...

  \importantnotice
\end{document}
```

## With Manifest

```latex
\documentclass{techreport}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  \tableofcontents

  \section{Introduction}
  % Content...

  \makerevisionhistory
  \importantnotice
\end{document}
```

## Features

- A4 paper, 11pt Arial font
- 2cm left/right margins, 3cm top/bottom
- Each section starts on a new page
- Headers: Section name (left), Short title (center), Company logo (right)
- Footers: Revision (left), Date (center), Page X of Y (right)
- First page has no header, footer only
- **Report-specific disclaimer** — `\importantnotice` produces wording focused on the validity of findings and methodology rather than product fitness for purpose

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
- `\importantnotice` - Report-specific disclaimer section (place at end)
- `\companylogo` - Insert company logo (default height 0.6cm)
- `\companylogo[height=1.2cm]` - Insert company logo with custom height
- `\revisionnumber` - Output current revision inline

## Creating a New Report

Use the `fdoc` CLI to create a new report:

```bash
# With full options
fdoc create report --title "Thermal Test Results" --id "FD-DC-LTX-10001"

# Quick start with defaults
fdoc create report

# Without manifest (manual metadata)
fdoc create report --title "My Report" --no-manifest
```

## Building

From the document directory:

```bash
fdoc build .
```

Or from the repository root:

```bash
fdoc build thermal-test-results
```
