# Datasheet Document Class

Professional product data sheets for Fiddlie products.

## Usage

```latex
\documentclass{datasheet}

\title{Product Name}
\shorttitle{Short Name}
\author{Author Name}
\date{September 2025}
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

- `\title{}` - Full document title
- `\shorttitle{}` - Abbreviated title for headers
- `\author{}` - Document author
- `\date{}` - Document date
- `\documentId{}` - Document ID (e.g., FD/DC/LTX/12345)
- `\revision{}` - Revision string (e.g., A-rc1, B)
- `\draft` - Add draft watermark
- `\maketitle` - Generate title page
- `\companylogo[height]` - Insert company logo
- `\revisionnumber` - Output current revision inline
- `\importantnotice` - Standard disclaimer section
