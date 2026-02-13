# Fiddlie LaTeX Documentation Guidelines

This repository contains Fiddlie documentation written in LaTeX. When working with documents in this repository, refer to the appropriate guide below based on what you're working on.

<!-- MANAGED SECTION START -->
<!-- This section is automatically generated and updated by fdoc. Do not edit manually. -->
<!-- Last updated: {{ update_date }} -->

## Quick Reference

### Document Types

This repository supports two document types:

- **Datasheet** - Product datasheets with specifications and technical details
  - 📖 See [CLAUDE_DATASHEET.md](CLAUDE_DATASHEET.md) for complete guidelines

- **Requirements** - Requirements specifications with ID tracking and priority levels
  - 📖 See [CLAUDE_REQUIREMENTS.md](CLAUDE_REQUIREMENTS.md) for complete guidelines

### Common Resources

- **Manifest Files** - Document metadata in YAML format
  - 📖 See [CLAUDE_MANIFEST.md](CLAUDE_MANIFEST.md) for format specification

### When to Reference Which Guide

- Working on a datasheet? → Read [CLAUDE_DATASHEET.md](CLAUDE_DATASHEET.md)
- Working on requirements? → Read [CLAUDE_REQUIREMENTS.md](CLAUDE_REQUIREMENTS.md)
- Need manifest format? → Read [CLAUDE_MANIFEST.md](CLAUDE_MANIFEST.md)
- General LaTeX help? → Continue reading below

## Common Elements

These elements apply to all document types. They are defined in our templates,
and should not be modified. Key settings include:

### Build System

**Engine:** LuaLaTeX (required)

**Commands:**

```bash
latexmk document.tex      # Build
latexmk -c                # Clean build files
latexmk -g document.tex   # Force rebuild
```

### Page Layout

- Paper: A4
- Font: Arial, 11pt
- Margins: 2cm left/right, 3cm top/bottom
- Headers/Footers: Automatic with section names, dates, and page numbers

### Common LaTeX Packages

All documents include these packages: `siunitx`, `graphicx`, `tabularx`, `listings`, `tikz`, `hyperref`, `amsmath`

### Common Patterns

**Lists:**

```latex
\begin{itemize}
  \item Bullet point
\end{itemize}

\begin{enumerate}
  \item Numbered item
\end{enumerate}
```

**Tables:**

```latex
\begin{tabularx}{\textwidth}{|L{4cm}|X|}
  \hline
  \rowcolor{lightgray}
  \textbf{Parameter} & \textbf{Value} \\
  \hline
  Voltage & \SI{3.3}{\volt} \\
  \hline
\end{tabularx}
```

**References:**

```latex
\section{Introduction}
\label{sec:intro}

See Section~\ref{sec:intro} for details.
```

<!-- MANAGED SECTION END -->

<!-- CUSTOM SECTION START -->

## Repository-Specific Guidelines

Add your project-specific documentation guidelines, conventions, and notes here.

This section is preserved when running `fdoc update`.

<!-- CUSTOM SECTION END -->
