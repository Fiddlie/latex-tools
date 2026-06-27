# Pretty Document Guidelines

Reference guide for writing Fiddlie `prettydoc` documents.

## Overview

`prettydoc` is a branded, presentation-grade class for public-facing material:
briefs, guides, proposals, client notes, and short marketing-style write-ups.
It captures the Fiddlie one-pager styling — a full-bleed tricolour top bar,
geometric Montserrat type, eyebrow kickers, two-tone display titles, numbered
cards and blue-dot lists — without imposing a fixed body layout. Write ordinary
sections, lists and paragraphs and they come out on-brand.

This is a *styling* class, not a rigid content template. Unlike `datasheet` or
`techreport`, there is no table of contents, no `\importantnotice` disclaimer,
and no rendered revision-history table. Use it when presentation matters more
than formal structure.

`fdoc create prettydoc` produces documents with `\documentclass{prettydoc}`.

## Document Structure

```latex
\documentclass{prettydoc}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

% Cover extras (not part of the manifest schema)
\doctype{Brief}
\kicker{A quick orientation}
\lead{One or two sentences introducing the document.}

\begin{document}
  \maketitle

  \eyebrow{What this covers}

  \card{First point}
  \begin{itemize}
    \item ...
  \end{itemize}

  \closing{A short closing line.}
\end{document}
```

## Key Features

- **Tricolour top bar** — full-bleed pink/yellow/blue bar on the cover
- **Two-tone display titles** — colour a word with `\accentword{}`
- **Eyebrow labels** — letterspaced blue caps via `\eyebrow{}` / `\kicker{}`
- **Numbered cards** — `\card{}` draws a pale-blue chip above a bold heading
- **Blue-dot lists** — ordinary `itemize` lists pick up the brand bullet
- **Quiet footer** — document reference and build ID bottom-left, a bold
  `01 / 02` page indicator squared into the bottom-right corner
- **Montserrat type** — falls back to the inherited font with a warning if
  Montserrat isn't installed

## Metadata

prettydoc reads the standard fiddlie-common metadata (works with or without a
manifest):

- `\title{}` — supports `\accentword{}` for the two-tone cover title
- `\author{}`, `\date{}` — the meta-block **year is pulled from `\date{}`**
  (e.g. `June 2026` → 2026); there is no separate year field
- `\revision{}` — the current revision, shown in the meta block and footer
- `\documentId{}` — document reference shown bottom-left in the footer
- `\shorttitle{}` — used by fiddlie-common headers

prettydoc-specific cover fields (set in the `.tex`, not the manifest):

- `\doctype{}` — small label in the top-right meta block (e.g. "Brief")
- `\kicker{}` — eyebrow line above the cover title
- `\lead{}` — intro paragraph under the title
- `\website{}` — last line of the meta block (defaults to `fiddlie.com`)

The build ID (from `fiddlie-common`, a `LOCAL - NOT FOR RELEASE` marker until a
release build sets it) always appears as a small line beneath the document
reference, so local builds are flagged.

## Revision history

With a manifest, revision history lives in `manifest.yaml` for the record but is
**not** rendered — prettydoc shows only the current `revision.current`. Do not
call `\makerevisionhistory` in a prettydoc; it is meant for the formal classes.

## Essential Commands

- `\maketitle` — branded cover (tricolour bar, wordmark, meta block, title, lead)
- `\eyebrow{Text}` — letterspaced blue caps label to introduce a section
- `\card{Heading}` — numbered card; `\card[A]{...}` sets a label, `\card*{...}`
  reuses the current number
- `\accentword{word}` — colour a word brand blue; `\accentword[brandpink]{word}`
  or `\accentword[brandyellow]{word}` for the other brand colours
- `\section{}` / `\subsection{}` — display heading / compact bold lead-in
- `\closing{Text}` — a closing sign-off block

## Important Notes

1. **Styling class, not a content template** — write ordinary LaTeX; it comes
   out on-brand.
2. **No `\tableofcontents` or `\importantnotice`** — these belong to the formal
   classes (`datasheet`, `techreport`).
3. **Use manifest for metadata** — see [CLAUDE_MANIFEST.md](CLAUDE_MANIFEST.md).
4. **Logo can be customised** — use `\setlogo{filename}` in the preamble.
5. **Year comes from `\date{}`** — there is no `\docyear` field.
