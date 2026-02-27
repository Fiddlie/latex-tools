# Datasheet Document Class

Professional product data sheets for Fiddlie products.

## Usage

```latex
\documentclass{datasheet}

\title{Product Name}
\shorttitle{Short Name}
\author{Author Name}
\date{January 2026}
\documentId{FD/DC/LTX/12345}
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
\documentclass{datasheet}

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

## Commands

### Document Metadata

- `\title{}` - Full document title
- `\shorttitle{}` - Abbreviated title for headers
- `\author{}` - Document author
- `\date{}` - Document date
- `\documentId{}` - Document ID (e.g., FD/DC/LTX/12345)
- `\revision{}` - Revision string (e.g., A-rc1, B)
- `\draft` - Add draft watermark
- `\setlogo{filename}` - Override the default logo (use in preamble)

### Document Structure

- `\maketitle` - Generate title page
- `\makerevisionhistory` - Generate revision history table (requires manifest)
- `\importantnotice` - Standard disclaimer section
- `\companylogo` - Insert company logo (default height 0.6cm)
- `\companylogo[height=1.2cm]` - Insert company logo with custom height
- `\revisionnumber` - Output current revision inline

## Creating a New Datasheet

Use the `fdoc` CLI to create a new datasheet:

```bash
# With full options
fdoc create datasheet --title "Power Supply Unit" --id "FD/DC/LTX/10001"

# Quick start with defaults
fdoc create datasheet

# Without manifest (manual metadata)
fdoc create datasheet --title "My Product" --no-manifest
```

## Building

From the document directory:

```bash
fdoc build .
```

Or from the repository root:

```bash
fdoc build power-supply-unit
```
