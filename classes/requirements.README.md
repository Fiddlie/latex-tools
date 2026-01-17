# Requirements Document Class

Requirements specification documents for Fiddlie projects.

## Usage

```latex
\documentclass{requirements}

\title{Project Requirements}
\shorttitle{Requirements}
\author{Author Name}
\date{January 2026}
\documentId{FD/REQ/PRJ/001}
\revision{A-rc1}
\draft  % Optional: adds draft watermark

\begin{document}
  \maketitle
  \tableofcontents

  \section{Introduction}
  \makedocumentconventions

  \section{Customer Requirements}
  % Content...

  \importantnotice
\end{document}
```

## With Manifest

```latex
\documentclass{requirements}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  \tableofcontents

  \section{Introduction}
  \makedocumentconventions

  \section{Customer Requirements}
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
- Built-in support for requirements tables with priority highlighting
- TikZ libraries loaded for block diagrams

## Commands

### Document Metadata

- `\title{}` - Full document title
- `\shorttitle{}` - Abbreviated title for headers
- `\author{}` - Document author
- `\date{}` - Document date
- `\documentId{}` - Document ID (e.g., FD/REQ/PRJ/001)
- `\revision{}` - Revision string (e.g., A-rc1, B)
- `\draft` - Add draft watermark

### Document Structure

- `\maketitle` - Generate title page
- `\makedocumentconventions` - Insert standard conventions section explaining requirement prefixes and priority levels
- `\makerevisionhistory` - Generate revision history table (requires manifest)
- `\importantnotice` - Standard disclaimer section

### Requirements Formatting

- `\reqid{ID}` - Format a requirement ID (monospace)
- `\musthave` - Red-highlighted "MUST" priority cell
- `\shouldhave` - Yellow-highlighted "SHOULD" priority cell
- `\couldhave` - Gray-highlighted "COULD" priority cell
- `\req{ID}{Description}{Priority}` - Add a requirement row (use inside `requirementstable`)

### Table Column Types

- `L{width}` - Left-aligned paragraph column
- `C{width}` - Center-aligned paragraph column
- `R{width}` - Right-aligned paragraph column

## Requirements Table

Use the `requirementstable` environment with the `\req` command for easy table creation:

```latex
\begin{requirementstable}
  \req{CR-001}{System shall respond within 100ms}{\musthave}
  \req{CR-002}{System should support 1000 concurrent users}{\shouldhave}
  \req{CR-003}{System could provide dark mode}{\couldhave}
\end{requirementstable}
```

The optional argument sets the requirement column width (default 9cm):

```latex
\begin{requirementstable}[11cm]
  \req{CR-001}{A longer requirement description that needs more space}{\musthave}
\end{requirementstable}
```

### Manual Table (Advanced)

For more control, you can create tables manually:

```latex
\begin{longtable}{|c|L{9cm}|c|}
  \hline
  \rowcolor{lightgray}
  \textbf{ID} & \textbf{Requirement} & \textbf{Priority} \\
  \hline
  \endfirsthead
  \hline
  \rowcolor{lightgray}
  \textbf{ID} & \textbf{Requirement} & \textbf{Priority} \\
  \hline
  \endhead

  \reqid{CR-001} & System shall respond within 100ms & \musthave \\
  \hline
\end{longtable}
```

## Requirement ID Prefixes

The `\makedocumentconventions` command documents these standard prefixes:

| Prefix | Category |
|--------|----------|
| BR | Business Requirement |
| CR | Customer Requirement |
| TR | Technical Requirement |
| ER | Environmental Requirement |
| SR | Safety Requirement |

## Available Colors

- `headergray` - Dark gray for headers (RGB 80, 80, 80)
- `lightgray` - Light gray for table backgrounds (RGB 240, 240, 240)
- `tableborder` - Gray for table borders (RGB 200, 200, 200)
- `tabred` - Red for must-have highlighting (RGB 255, 51, 102)
- `tabyellow` - Yellow for should-have highlighting (RGB 255, 204, 0)
