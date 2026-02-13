# Datasheet Document Guidelines

Reference guide for writing Fiddlie datasheet documents.

## Overview

Datasheets are professional product documentation with specifications, features, and technical details. Use this document type for product specifications, hardware datasheets, and technical reference documents.

## Document Structure

```latex
\documentclass{datasheet}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle
  \tableofcontents

  \section{Introduction}
  Brief overview of the product.

  \section{Features}
  \begin{itemize}
    \item Feature 1
    \item Feature 2
  \end{itemize}

  \section{Specifications}
  \subsection{Electrical Specifications}
  % Specification tables here

  \subsection{Mechanical Specifications}
  % Mechanical details here

  \makerevisionhistory
  \importantnotice
\end{document}
```

## Key Features

- **Automatic page breaks** - Each `\section{}` starts on a new page
- **Company logo** - Appears in header on all pages except first
- **Revision tracking** - Automatically displayed in footers
- **Build IDs** - Shows build identifier from `.buildid` file

## Essential Commands

### Document Structure

- `\maketitle` - Generate title page with metadata from manifest
- `\tableofcontents` - Generate table of contents
- `\section{Title}` - Top-level section (starts new page)
- `\subsection{Title}` - Subsection (continues on same page)

### Document Metadata

- `\makerevisionhistory` - Auto-generate revision history table from manifest
- `\importantnotice` - Add standard disclaimer section (place at end)

## Common Patterns

### Specification Tables

Use `tabularx` with custom column types for specification tables:

```latex
\section{Electrical Specifications}

\begin{table}[h]
  \centering
  \caption{Power Supply Specifications}
  \begin{tabularx}{\textwidth}{|L{4cm}|C{2.5cm}|C{2.5cm}|C{2.5cm}|X|}
    \hline
    \rowcolor{lightgray}
    \textbf{Parameter} & \textbf{Min} & \textbf{Typ} & \textbf{Max} & \textbf{Unit} \\
    \hline
    Input Voltage & 3.0 & 3.3 & 3.6 & V \\
    \hline
    Output Current & - & 500 & 1000 & mA \\
    \hline
    Efficiency & 85 & 90 & - & \% \\
    \hline
  \end{tabularx}
</table>
```

**Column types:**
- `L{width}` - Left-aligned, fixed width
- `C{width}` - Center-aligned, fixed width
- `R{width}` - Right-aligned, fixed width
- `X` - Flexible width (fills remaining space)

### Units with siunitx

Always use `siunitx` for units and numbers:

```latex
\SI{5}{\volt}                    % 5 V
\SI{100}{\milli\ampere}          % 100 mA
\SI{3.3}{\kilo\ohm}              % 3.3 kΩ
\SI{25}{\celsius}                % 25 °C
\num{1.5e6}                      % 1.5 × 10⁶
\SIrange{-40}{85}{\celsius}      % -40 °C to 85 °C
```

### Feature Lists

```latex
\section{Features}

\begin{itemize}
  \item Low power consumption: \SI{50}{\micro\watt} typical
  \item Wide input voltage range: \SIrange{2.7}{5.5}{\volt}
  \item Small form factor: $5 \times 5$ mm package
  \item Temperature range: \SIrange{-40}{125}{\celsius}
\end{itemize}
```

### Block Diagrams

Use TikZ for block diagrams:

```latex
\section{Functional Block Diagram}

\begin{figure}[h]
  \centering
  \begin{tikzpicture}[node distance=2.5cm, auto,
      block/.style={rectangle, draw, fill=blue!20, text width=5em, text centered, minimum height=3em}]

    \node [block] (input) {Input Stage};
    \node [block, right of=input] (process) {Processor};
    \node [block, right of=process] (output) {Output Stage};

    \draw [->] (input) -- (process);
    \draw [->] (process) -- (output);
  \end{tikzpicture}
  \caption{System Block Diagram}
\end{figure}
```

### Pin Descriptions

```latex
\section{Pin Descriptions}

\begin{table}[h]
  \centering
  \caption{Pin Functions}
  \begin{tabularx}{\textwidth}{|C{2cm}|L{3cm}|X|}
    \hline
    \rowcolor{lightgray}
    \textbf{Pin} & \textbf{Name} & \textbf{Description} \\
    \hline
    1 & VDD & Power supply input \\
    \hline
    2 & GND & Ground \\
    \hline
    3 & IN & Signal input \\
    \hline
    4 & OUT & Signal output \\
    \hline
  \end{tabularx}
</table>
```

### Images and Diagrams

```latex
\section{Mechanical Specifications}

\begin{figure}[h]
  \centering
  \includegraphics[width=0.6\textwidth]{images/package-dimensions.pdf}
  \caption{Package Dimensions (mm)}
  \label{fig:package}
\end{figure}

% Reference in text:
See Figure~\ref{fig:package} for detailed dimensions.
```

**Image formats:**
- PDF - Best for vector graphics (schematics, diagrams)
- PNG - For screenshots and raster images
- JPG - For photos

## Headers and Footers

Automatic headers and footers are configured:

**First page (title page):**
- No header
- Footer: Revision | Date | Page X of Y

**Subsequent pages:**
- Header: Section Name | Short Title | Logo
- Footer: Revision | Date | Page X of Y

The short title comes from `manifest.yaml` (`shorttitle` field, max ~30 characters).

## Important Notes

1. **Each section starts a new page** - This is automatic for top-level `\section{}` commands
2. **Use manifest for metadata** - See [CLAUDE_MANIFEST.md](CLAUDE_MANIFEST.md) for format
3. **Always use siunitx for units** - This ensures consistent formatting
4. **End with standard sections** - Always include `\makerevisionhistory` and `\importantnotice`
5. **Logo can be customized** - Use `\setlogo{filename}` in preamble if needed
