# Pretty Document Class

A branded, presentation-grade class for **public-facing** Fiddlie documents —
briefs, guides, proposals and client notes. It captures the Fiddlie marketing
one-pager styling (tricolour top bar, geometric Montserrat type, eyebrow
kickers, two-tone display titles, numbered cards and blue-dot lists) without
imposing a particular body layout. Write ordinary sections, paragraphs and
lists and they come out on-brand.

This is a **styling** class, not a content template — drop your own copy in.

## Usage

```latex
\documentclass{prettydoc}

\title{Working \accentword{together}, simply.}  % \accentword colours a word
\kicker{A quick orientation}                 % eyebrow above the title
\lead{A one-line intro shown under the title.}

\doctype{Brief}        % top-right meta label
\revision{A}
\docyear{2026}
\website{fiddlie.com}  % defaults to fiddlie.com

\begin{document}
\maketitle

\eyebrow{Section label}

\section{A \accentword{two-tone} heading.}

\card{First point}
\begin{itemize}
  \item Lists pick up the brand bullet automatically
  \item \textbf{Inline emphasis} works as usual
\end{itemize}

\card{Second point}
% ...

\closing{A short, bold sign-off.}
\end{document}
```

See [`examples/prettydoc/prettydoc-example.tex`](../examples/prettydoc/prettydoc-example.tex)
for a complete worked document.

## Features

- A4 paper, 11pt **Montserrat** (Regular body, SemiBold display)
- Full-bleed tricolour top bar (pink / yellow / blue) on the cover
- 2cm margins; no running header, clean footer only
- Footer: website (left), zero-padded `01 / 02` page indicator in brand blue (right)
- Unnumbered, styled headings (`secnumdepth = 0`)
- Brand colours from `fiddlie-common`: `brandpink`, `brandyellow`, `brandblue`

## Commands

### Document metadata

- `\title{}` — document title; may contain `\accentword{}`
- `\kicker{}` — eyebrow label shown above the cover title
- `\lead{}` — intro paragraph shown under the cover title
- `\doctype{}` — small label in the top-right meta block (e.g. "Brief")
- `\revision{}` — revision string (e.g. A)
- `\docyear{}` — year shown beside the revision
- `\website{}` — meta/footer line (defaults to `fiddlie.com`)
- `\setlogo{filename}` — override the default logo (preamble)

### Structure & styling

- `\maketitle` — branded cover (top bar, logo, meta, kicker, title, lead)
- `\eyebrow{LABEL}` — letterspaced blue caps label with a leading rule
- `\section{...}` — large display heading (accepts `\accentword{}`)
- `\subsection{...}` — compact bold lead-in
- `\accentword{word}` — colour a word in brand blue;
  `\accentword[brandpink]{word}` for another colour
- `\card{Heading}` — numbered pale-blue chip above a bold heading
  (auto-numbers; `\card[A]{...}` sets a label, `\card*{...}` reuses the
  current number, `\cardreset` restarts at 01)
- `\closing{...}` — short coloured rule above a bold sign-off paragraph
- `\companylogo[height=...]` — insert the logo

## Requirements

Beyond the base toolset, `prettydoc` needs:

- **Montserrat** — the `montserrat` package (TeX Live) ships the fonts, or
  install the OTF family system-wide. If Montserrat is missing the class
  warns and falls back to the inherited font rather than failing.
- `eso-pic` — for the full-bleed top bar.

`microtype`, `enumitem` and `titlesec` are already part of the standard
build environment.

## Building

```bash
# from the document directory
fdoc build .
```
