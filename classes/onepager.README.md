# One-pager Document Class

Single-page, brand-styled summaries for Fiddlie — overviews, fact sheets,
quick-reference cards and similar dense, scannable documents.

## Usage

```latex
\documentclass{onepager}

\title{Document Title}
\shorttitle{Short Title}
\author{Author Name}
\date{June 2026}
\documentId{FD-DC-LTX-12345}
\revision{A}
\draft  % Optional: adds draft watermark

\begin{document}
  \maketitle

  \begin{small}
    % Optional preamble paragraph
  \end{small}

  \begin{twocol}
    \pinksection{First topic}
    % Content...

    \yellowsection{Second topic}
    % Content...
  \end{twocol}
\end{document}
```

## With Manifest

```latex
\documentclass{onepager}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle

  \begin{twocol}
    \pinksection{First topic}
    % Content...
  \end{twocol}
\end{document}
```

## Features

- A4 paper, 11pt Arial font (from `fiddlie-common`)
- Tight geometry (1.5cm sides, 1.8cm/2cm top/bottom) for a dense single page
- **Sections never force a page break** — the layout stays on one page
- Compact masthead: logo (left) + revision/date/ID (right), thin rule, title
- Coloured dot headings echoing the Fiddlie logo dots
- Two- and three-column body environments
- Widow/orphan protection so paragraphs avoid splitting across columns
- **No legal disclaimer or table of contents** — one-pagers are summaries

## Commands

### Document Metadata

- `\title{}` - Full document title (shown in the masthead)
- `\shorttitle{}` - Abbreviated title (used by headers)
- `\author{}` - Document author
- `\date{}` - Document date
- `\documentId{}` - Document ID (e.g., FD-DC-LTX-12345)
- `\revision{}` - Revision string (e.g., A, A-rc1)
- `\draft` - Add draft watermark
- `\setlogo{filename}` - Override the default logo (use in preamble)

### Document Structure

- `\maketitle` - Generate the compact masthead
- `\companylogo[height=1cm]` - Insert the company logo at a given height

### Headings

- `\dotsection{colour}{Title}` - A filled-circle bullet in any xcolor name
  followed by a bold title
- `\pinksection{Title}` / `\yellowsection{Title}` / `\bluesection{Title}` -
  Shortcuts for the standard brand palette
- `\iconsection[colour]{icon}{Title}` - Heading variant with a FontAwesome
  icon in place of the dot (colour optional; icon is always solid)

### Columns

- `\begin{twocol} ... \end{twocol}` - Two-column body at `\small`
- `\begin{threecol} ... \end{threecol}` - Three-column body at `\small`

## Creating a New One-pager

Use the `fdoc` CLI:

```bash
# With full options
fdoc create onepager --title "Product Overview" --id "FD-DC-LTX-10001"

# Quick start with defaults
fdoc create onepager

# Without manifest (manual metadata)
fdoc create onepager --title "My Summary" --no-manifest
```

## Building

From the document directory:

```bash
fdoc build .
```

Or from the repository root:

```bash
fdoc build product-overview
```

See [`examples/onepager/onepager-example.tex`](../examples/onepager/onepager-example.tex)
for a worked document.
