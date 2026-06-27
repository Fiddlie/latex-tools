# Fiddlie LaTeX Documentation Guidelines

This repository contains Fiddlie documentation written in LaTeX. When working with documents in this repository, refer to the appropriate guide below based on what you're working on.

<!-- MANAGED SECTION START -->
<!-- This section is automatically generated and updated by fdoc. Do not edit manually. -->
<!-- Last updated: {{ update_date }} -->

## Quick Reference

### Document Types

This repository supports the following document types:

- **Datasheet** - Product datasheets with specifications and technical details
  - 📖 See [latex-tools/docs/CLAUDE_DATASHEET.md](latex-tools/docs/CLAUDE_DATASHEET.md) for complete guidelines

- **Requirements** - Requirements specifications with ID tracking and priority levels
  - 📖 See [latex-tools/docs/CLAUDE_REQUIREMENTS.md](latex-tools/docs/CLAUDE_REQUIREMENTS.md) for complete guidelines

- **Policy** - Internal policy documents
  - 📖 See [latex-tools/docs/CLAUDE_POLICY.md](latex-tools/docs/CLAUDE_POLICY.md) for complete guidelines

- **Report** - Engineering and research reports (`techreport` class)
  - 📖 See [latex-tools/docs/CLAUDE_REPORT.md](latex-tools/docs/CLAUDE_REPORT.md) for complete guidelines

- **One-pager** - Single-page, brand-styled summaries and fact sheets
  - 📖 See [latex-tools/docs/CLAUDE_ONEPAGER.md](latex-tools/docs/CLAUDE_ONEPAGER.md) for complete guidelines

- **Pretty document** - Branded, public-facing briefs, guides and proposals
  - 📖 See [latex-tools/docs/CLAUDE_PRETTYDOC.md](latex-tools/docs/CLAUDE_PRETTYDOC.md) for complete guidelines

### Common Resources

- **Manifest Files** - Document metadata in YAML format
  - 📖 See [latex-tools/docs/CLAUDE_MANIFEST.md](latex-tools/docs/CLAUDE_MANIFEST.md) for format specification

### When to Reference Which Guide

- Working on a datasheet? → Read [latex-tools/docs/CLAUDE_DATASHEET.md](latex-tools/docs/CLAUDE_DATASHEET.md)
- Working on requirements? → Read [latex-tools/docs/CLAUDE_REQUIREMENTS.md](latex-tools/docs/CLAUDE_REQUIREMENTS.md)
- Working on a policy? → Read [latex-tools/docs/CLAUDE_POLICY.md](latex-tools/docs/CLAUDE_POLICY.md)
- Working on a report? → Read [latex-tools/docs/CLAUDE_REPORT.md](latex-tools/docs/CLAUDE_REPORT.md)
- Working on a one-pager? → Read [latex-tools/docs/CLAUDE_ONEPAGER.md](latex-tools/docs/CLAUDE_ONEPAGER.md)
- Working on a branded brief/guide? → Read [latex-tools/docs/CLAUDE_PRETTYDOC.md](latex-tools/docs/CLAUDE_PRETTYDOC.md)
- Need manifest format? → Read [latex-tools/docs/CLAUDE_MANIFEST.md](latex-tools/docs/CLAUDE_MANIFEST.md)
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
