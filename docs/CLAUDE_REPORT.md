# Report Document Guidelines

Reference guide for writing Fiddlie engineering and research report documents.

## Overview

Report documents capture engineering investigations, test results, and research findings. Use this document type for test reports, characterisation studies, design reviews, and similar technical writing.

The class file is named `techreport` to avoid colliding with LaTeX's built-in `report` class. The `fdoc create report` command produces documents with `\documentclass{techreport}`.

## Document Structure

```latex
\documentclass{techreport}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  \tableofcontents

  \section{Introduction}
  Background and report objective.

  \section{Methodology}
  Equipment, setup, and procedure.

  \section{Results}
  Measurements, observations, and analysis.

  \section{Conclusions}
  Summary of findings.

  \makerevisionhistory
  \importantnotice
\end{document}
```

## Key Features

- **Automatic page breaks** - Each `\section{}` starts on a new page
- **Company logo** - Appears in header on all pages except first
- **Revision tracking** - Automatically displayed in footers
- **Build IDs** - Shows build identifier from `.buildid` file
- **Report-specific disclaimer** - `\importantnotice` produces wording about the validity of findings (rather than the product fitness-for-purpose wording used by datasheets)

## Essential Commands

### Document Structure

- `\maketitle` - Generate title page with metadata from manifest
- `\tableofcontents` - Generate table of contents
- `\section{Title}` - Top-level section (starts new page)
- `\subsection{Title}` - Subsection (continues on same page)

### Document Metadata

- `\makerevisionhistory` - Auto-generate revision history table from manifest
- `\importantnotice` - Report-specific disclaimer section (place at end)

## Common Patterns

### Result Tables

Use `tabularx` with custom column types from the report class:

```latex
\section{Results}

\begin{table}[h]
  \centering
  \caption{Measured efficiency vs.\ load}
  \begin{tabularx}{\textwidth}{|C{3cm}|C{3cm}|X|}
    \hline
    \textbf{Load (A)} & \textbf{Efficiency (\%)} & \textbf{Notes} \\
    \hline
    0.5 & 88 & Light load \\
    \hline
    1.0 & 92 & Rated load \\
    \hline
    2.0 & 89 & Overload \\
    \hline
  \end{tabularx}
\end{table}
```

### Units with siunitx

Always use `siunitx` for units and numbers:

```latex
\SI{5}{\volt}
\SI{100}{\milli\ampere}
\SIrange{-40}{85}{\celsius}
```

### Figures

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{images/efficiency-curve.pdf}
  \caption{Efficiency vs.\ load current}
  \label{fig:efficiency}
\end{figure}
```

## Important Notes

1. **Each section starts a new page** - This is automatic for top-level `\section{}` commands
2. **Use manifest for metadata** - See [CLAUDE_MANIFEST.md](CLAUDE_MANIFEST.md) for format
3. **End with `\importantnotice`** - The report class provides a methodology-focused version of the disclaimer
4. **Logo can be customized** - Use `\setlogo{filename}` in preamble if needed
