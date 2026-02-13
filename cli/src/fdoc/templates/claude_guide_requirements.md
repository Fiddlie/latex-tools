# Requirements Document Guidelines

Reference guide for writing Fiddlie requirements specification documents.

## Overview

Requirements documents are structured specifications with ID tracking, priority levels, and automatic duplicate detection. Use this document type for project requirements, specifications, and functional requirements documents.

## Document Structure

```latex
\documentclass{requirements}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  \tableofcontents

  \section{Introduction}
  \subsection{Project Background}
  Context and motivation for the project.

  \subsection{Business Context}
  Business objectives and constraints.

  \makedocumentconventions

  \section{Customer Requirements}
  \subsection{User Requirements}
  \begin{requirementstable}
    \req{CR-001}{User shall be able to log in using email}{\musthave}
    \req{CR-002}{System shall support 100 concurrent users}{\shouldhave}
    \req{CR-003}{UI shall support dark mode}{\couldhave}
  \end{requirementstable}

  \section{Technical Requirements}
  \begin{requirementstable}
    \req{TR-004}{System shall use HTTPS for all connections}{\musthave}
    \req{TR-005}{Database shall support transactions}{\musthave}
  \end{requirementstable}

  \section{Appendix A: Glossary}
  \begin{glossarytable}
    \term{API}{Application Programming Interface}
    \term{HTTPS}{Hypertext Transfer Protocol Secure}
  \end{glossarytable}

  \makerevisionhistory
  \importantnotice
\end{document}
```

## Requirement IDs

### Format

**Pattern:** `PREFIX-NNN`

- Prefix: Two-letter category code (see below)
- Number: Zero-padded to 3 digits (001, 002, ..., 999)

**Example:** `CR-001`, `TR-042`, `SR-123`

### Valid Prefixes

- `BR` - Business Requirement
- `CR` - Customer Requirement
- `TR` - Technical Requirement
- `ER` - Environmental Requirement
- `SR` - Safety Requirement

### Critical Rule: Global Uniqueness

**Requirement IDs are globally unique across ALL prefixes.**

❌ **WRONG:**

```latex
\req{CR-010}{Customer requirement}{\musthave}
\req{TR-010}{Technical requirement}{\musthave}  % ERROR: 010 already used!
```

✅ **CORRECT:**

```latex
\req{CR-010}{Customer requirement}{\musthave}
\req{TR-011}{Technical requirement}{\musthave}  % Different number
```

The numeric part (010, 011, etc.) can only appear once in the entire document, regardless of prefix.

### Duplicate Detection

LuaLaTeX automatically detects duplicate IDs at compile time:

```
! Duplicate requirement ID: TR-010 (conflicts with CR-010)
```

The build will fail if duplicates are found. Check the build log for the next available ID.

## Priority Levels

Use these commands for requirement priorities:

### \musthave

```latex
\req{CR-001}{User shall be able to authenticate}{\musthave}
```

- **Color:** Red background
- **Label:** "MUST"
- **Meaning:** Mandatory requirement, must be implemented
- **Use for:** Critical features, safety requirements, regulatory compliance

### \shouldhave

```latex
\req{CR-002}{System shall provide usage statistics}{\shouldhave}
```

- **Color:** Yellow background
- **Label:** "SHOULD"
- **Meaning:** Important requirement, needs strong justification if skipped
- **Use for:** Important features, expected functionality

### \couldhave

```latex
\req{CR-003}{UI shall support customizable themes}{\couldhave}
```

- **Color:** Light gray background
- **Label:** "COULD"
- **Meaning:** Desirable feature if resources permit
- **Use for:** Nice-to-have features, future enhancements

## Requirements Tables

### Basic Usage

```latex
\begin{requirementstable}
  \req{CR-001}{User shall be able to log in}{\musthave}
  \req{CR-002}{System shall log all access attempts}{\shouldhave}
  \req{CR-003}{UI shall support dark mode}{\couldhave}
\end{requirementstable}
```

### Column Layout

- **ID:** 3cm width, left-aligned
- **Description:** Variable width (fills remaining space)
- **Priority:** 3cm width, center-aligned with color coding

### Writing Good Requirements

**Use "shall" for requirements:**

```latex
\req{CR-001}{System shall authenticate users}{\musthave}  % Good
\req{CR-002}{System authenticates users}{\musthave}       % Avoid
```

**Be specific and measurable:**

```latex
% Good - specific and measurable
\req{TR-001}{System shall respond to requests within 500ms}{\musthave}

% Poor - vague and unmeasurable
\req{TR-002}{System shall be fast}{\musthave}
```

**One requirement per entry:**

```latex
% Good - single requirement
\req{CR-001}{User shall be able to reset password}{\musthave}

% Poor - multiple requirements in one
\req{CR-002}{User shall be able to reset password and change email}{\musthave}
```

## Glossary Tables

### Basic Usage

```latex
\begin{glossarytable}
  \term{API}{Application Programming Interface}
  \term{HTTPS}{Hypertext Transfer Protocol Secure}
  \term{JWT}{JSON Web Token used for authentication}
\end{glossarytable}
```

### Column Widths

**Default:** 4cm (term) | 12cm (definition)

**Custom widths:**

```latex
% Wider terms column
\begin{glossarytable}[5cm]
  \term{Long Term Name}{Definition}
\end{glossarytable}

% Specify both columns
\begin{glossarytable}[3cm][13cm]
  \term{Term}{Longer definition text}
\end{glossarytable}
```

### Organizing Glossary

Organize alphabetically:

```latex
\section{Appendix A: Glossary}

\begin{glossarytable}
  \term{API}{Application Programming Interface}
  \term{CI/CD}{Continuous Integration/Continuous Deployment}
  \term{HTTPS}{Hypertext Transfer Protocol Secure}
  \term{JWT}{JSON Web Token}
  \term{REST}{Representational State Transfer}
\end{glossarytable}
```

## Document Conventions Section

The `\makedocumentconventions` command automatically generates a section explaining:

- Priority levels and their meanings
- Requirement ID format
- How the document should be read

Place this after the Introduction section:

```latex
\section{Introduction}
\subsection{Project Background}
% ... content ...

\makedocumentconventions

\section{Requirements}
% ... requirements tables ...
```

## Essential Commands

### Document Structure

- `\maketitle` - Generate title page
- `\tableofcontents` - Generate table of contents
- `\makedocumentconventions` - Auto-generate conventions section
- `\makerevisionhistory` - Auto-generate revision history
- `\importantnotice` - Add standard disclaimer (at end)

### Requirements

- `\req{ID}{Description}{Priority}` - Add a requirement (use inside `requirementstable`)
- `\musthave` - Mandatory priority (red)
- `\shouldhave` - Important priority (yellow)
- `\couldhave` - Optional priority (gray)

### Glossary

- `\term{Term}{Definition}` - Add glossary entry (use inside `glossarytable`)

## Common Patterns

### Organizing Requirements by Category

```latex
\section{Functional Requirements}

\subsection{Authentication}
\begin{requirementstable}
  \req{CR-001}{User shall be able to log in with email}{\musthave}
  \req{CR-002}{User shall be able to reset password}{\musthave}
\end{requirementstable}

\subsection{Data Management}
\begin{requirementstable}
  \req{CR-003}{User shall be able to export data}{\shouldhave}
  \req{CR-004}{System shall backup data daily}{\musthave}
\end{requirementstable}
```

### Requirements with Technical Details

```latex
\section{Performance Requirements}

\begin{requirementstable}
  \req{TR-001}{API shall respond within \SI{500}{\milli\second}}{\musthave}
  \req{TR-002}{System shall support 1000 concurrent users}{\musthave}
  \req{TR-003}{Database queries shall complete within \SI{100}{\milli\second}}{\shouldhave}
\end{requirementstable}
```

### Cross-Referencing

```latex
\section{Security Requirements}
\label{sec:security}

\begin{requirementstable}
  \req{SR-001}{System shall use TLS 1.3 or higher}{\musthave}
\end{requirementstable}

% Later in the document:
\section{Implementation Notes}
Security requirements are defined in Section~\ref{sec:security}.
```

## Important Notes

1. **IDs are globally unique** - You cannot reuse a numeric ID with different prefixes
2. **Duplicate detection is automatic** - Build will fail on duplicates
3. **Use "shall" language** - Standard for requirements documentation
4. **One requirement per entry** - Don't combine multiple requirements
5. **Be specific and measurable** - Requirements should be testable
6. **Organize logically** - Group related requirements in subsections
7. **Use glossary liberally** - Define all technical terms and acronyms
8. **Check build log for next ID** - The system tracks the next available ID
