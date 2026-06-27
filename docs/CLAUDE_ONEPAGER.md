# One-pager Guidelines

Reference guide for writing Fiddlie `onepager` documents.

## Overview

The `onepager` class produces dense, brand-styled documents that fit on a
single A4 page: product overviews, fact sheets, quick-reference cards, summaries
and similar scannable material. It is deliberately compact — tight geometry,
coloured dot headings, and two- or three-column bodies.

Unlike `datasheet` or `techreport`, sections **never** force a page break, there
is no table of contents, and there is no `\importantnotice` disclaimer. Keep the
content short enough to land on one page.

`fdoc create onepager` produces documents with `\documentclass{onepager}`.

## Document Structure

```latex
\documentclass{onepager}

\usepackage{fiddlie-manifest}
\loadmanifest{manifest.yaml}
\applymanifest

\begin{document}
  \maketitle

  \begin{small}
    Optional preamble — a paragraph of context before the columned body.
  \end{small}

  \begin{twocol}
    \pinksection{First topic}
    Content for the first topic.

    \yellowsection{Second topic}
    Content for the second topic.

    \bluesection{Third topic}
    Content for the third topic.
  \end{twocol}
\end{document}
```

## Key Features

- **Single page** - Sections do not force page breaks; keep content brief
- **Compact masthead** - Logo (left) + revision/date/ID (right), rule, title
- **Coloured dot headings** - Filled-circle bullets echoing the logo dots
- **Icon headings** - Swap the dot for a FontAwesome icon
- **Multi-column body** - `twocol` and `threecol` environments at `\small`
- **Widow/orphan protection** - Paragraphs avoid splitting across columns

## Essential Commands

### Document Structure

- `\maketitle` - Generate the compact masthead from the metadata
- `\companylogo[height=1cm]` - Insert the company logo at a given height

### Headings

- `\dotsection{colour}{Title}` - Coloured dot + bold title (any xcolor name)
- `\pinksection{Title}` / `\yellowsection{Title}` / `\bluesection{Title}` -
  Brand-palette shortcuts
- `\iconsection[colour]{icon}{Title}` - Icon heading; colour optional. The icon
  name is a FontAwesome solid icon (e.g. `lightbulb`, `bolt`, `palette`)

### Columns

- `\begin{twocol} ... \end{twocol}` - Two columns at `\small`
- `\begin{threecol} ... \end{threecol}` - Three columns at `\small`

## Common Patterns

### A scannable three-column strip

```latex
\begin{threecol}
  \iconsection[brandpink]{bolt}{Fast}
  Single-page output builds quickly.

  \iconsection[brandyellow]{ruler-combined}{Tight}
  Compact geometry fits more on the page.

  \iconsection[brandblue]{palette}{On-brand}
  Brand colours and type are inherited.
\end{threecol}
```

### Units with siunitx

```latex
\SI{3.3}{\volt}
\SIrange{-40}{85}{\celsius}
```

## Important Notes

1. **Keep it to one page** - There are no automatic page breaks; trim content
   that overflows, or move to a `datasheet`/`techreport`.
2. **Use manifest for metadata** - See [CLAUDE_MANIFEST.md](CLAUDE_MANIFEST.md).
3. **No `\tableofcontents` or `\importantnotice`** - These belong to the formal
   classes.
4. **Icons need the FontAwesome fonts** - `fdoc build` installs them on first
   use; icon names come from the FontAwesome solid set.
5. **Logo can be customised** - Use `\setlogo{filename}` in the preamble.
