# Policy Document Guidelines

Reference guide for writing Fiddlie policy documents.

## Overview

Policy documents capture internal company policies and procedures. Use this document type for internal policy statements, governance documents, and procedural reference material.

Policy documents do **not** include the legal disclaimer (`\importantnotice`) used by datasheets, since they are internal documents not intended for external distribution.

## Document Structure

```latex
\documentclass{policy}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  \tableofcontents

  \section{Purpose}
  Why this policy exists and what it covers.

  \section{Scope}
  Who and what the policy applies to.

  \section{Policy}
  The policy statement itself.

  \section{Responsibilities}
  Roles and accountabilities.

  \makerevisionhistory
\end{document}
```

## Key Features

- **Automatic page breaks** - Each `\section{}` starts on a new page
- **Company logo** - Appears in header on all pages except first
- **Revision tracking** - Automatically displayed in footers
- **Build IDs** - Shows build identifier from `.buildid` file
- **No legal disclaimer** - `\importantnotice` is omitted from policy templates

## Essential Commands

### Document Structure

- `\maketitle` - Generate title page with metadata from manifest
- `\tableofcontents` - Generate table of contents
- `\section{Title}` - Top-level section (starts new page)
- `\subsection{Title}` - Subsection (continues on same page)

### Document Metadata

- `\makerevisionhistory` - Auto-generate revision history table from manifest

## Important Notes

1. **Each section starts a new page** - This is automatic for top-level `\section{}` commands
2. **Use manifest for metadata** - See [CLAUDE_MANIFEST.md](CLAUDE_MANIFEST.md) for format
3. **Do not add `\importantnotice`** - Policy documents are internal and do not carry the external-facing disclaimer
4. **End with `\makerevisionhistory`** - Always include the revision history table
5. **Logo can be customized** - Use `\setlogo{filename}` in preamble if needed
