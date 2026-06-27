\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{prettydoc}[2026/06/07 Fiddlie Pretty Document Class]

% prettydoc — a branded, presentation-grade class for public-facing
% documents: briefs, guides, proposals, client notes. It captures the
% Fiddlie "marketing one-pager" styling (tricolour top bar, geometric
% Montserrat type, eyebrow kickers, two-tone display titles, numbered
% cards and blue-dot lists) without imposing any particular body layout —
% write ordinary sections, lists and paragraphs and they come out on-brand.
%
% This is a styling class, not a content template. See
% examples/prettydoc/prettydoc-example.tex for a worked document.

% Based on the article class; unknown options are passed straight through.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[a4paper,10pt]{article}

% Shared Fiddlie styles: brand colours, logo, fancyhdr scaffolding,
% FontAwesome icons, hyperref, etc.
\RequirePackage{fiddlie-common}

% Full-bleed page furniture (tricolour top bar), per-section heading control,
% list customisation and letterspacing for the brand labels.
\RequirePackage{eso-pic}
\RequirePackage{titlesec}
\RequirePackage{enumitem}
\RequirePackage{microtype}
% Expandable page-reference lookup that returns 0 for an as-yet-undefined
% label (e.g. LastPage on the first pass), so zero-padding never sees "??".
\RequirePackage{refcount}

% ---------------------------------------------------------------------------
% Typography — Montserrat
% ---------------------------------------------------------------------------
% The source brand documents are set in Montserrat (Regular body, SemiBold
% display). fiddlie-common sets Arial as the main font; here we override
% with Montserrat for on-brand output. If Montserrat isn't installed we keep
% the inherited font and warn rather than failing the build.
\IfFontExistsTF{Montserrat}{%
  \setmainfont{Montserrat}[
    UprightFont    = *-Regular,
    BoldFont       = *-SemiBold,
    ItalicFont     = *-Italic,
    BoldItalicFont = *-SemiBoldItalic,
  ]%
}{%
  \ClassWarning{prettydoc}{Montserrat not found — falling back to the
    inherited main font. Install the 'montserrat' package (TeX Live) or the
    Montserrat OTF family for on-brand output}%
}

% ---------------------------------------------------------------------------
% Colours
% ---------------------------------------------------------------------------
% brandpink/brandyellow/brandblue come from fiddlie-common (the logo dots).
% Ink/body/fade are the neutral text tones lifted from the source document.
\definecolor{pdink}{HTML}{1A1A1A}   % near-black — display titles, headings
\definecolor{pdbody}{HTML}{444A52}  % dark slate — running body text
\definecolor{pdfade}{HTML}{8A9099}  % muted grey — secondary footer text

% ---------------------------------------------------------------------------
% Page geometry
% ---------------------------------------------------------------------------
% Compact margins. The logo/meta masthead and the footer sit close to the
% paper edges, so the running text has no header or footer reserved inside
% the body — the footer is stamped in the margin (see below).
\geometry{left=1.6cm, right=1.6cm, top=1.2cm, bottom=2.2cm,
  headheight=0pt, headsep=0pt, footskip=0pt}

% No section numbering — headings are styled, not enumerated.
\setcounter{secnumdepth}{0}

% Body text is set in the slate ink; headings restate their own colour.
\AtBeginDocument{\color{pdbody}}

% ---------------------------------------------------------------------------
% Font-size helpers for the brand type scale
% ---------------------------------------------------------------------------
\newcommand{\pd@titlefont}{\fontsize{30}{34}\bfseries}
\newcommand{\pd@sectionfont}{\fontsize{22}{26}\bfseries}
\newcommand{\pd@subsectionfont}{\fontsize{13}{17}\bfseries}
\newcommand{\pd@cardfont}{\fontsize{14}{18}\bfseries}
\newcommand{\pd@closingfont}{\fontsize{13}{18}\bfseries}
\newcommand{\pd@eyebrowfont}{\footnotesize\bfseries\color{brandblue}}
% Meta block: small, light (regular weight), neutral — not the brand blue.
\newcommand{\pd@metafont}{\scriptsize\mdseries}

% Letterspaced uppercase — the look of every label and kicker in the brand.
\newcommand{\pd@caps}[1]{\textls[140]{\MakeUppercase{#1}}}

% ---------------------------------------------------------------------------
% Document metadata fields (in addition to \title, \revision, \date,
% \documentId etc. provided by fiddlie-common)
% ---------------------------------------------------------------------------
% \doctype{...}  — the small label in the top-right meta block (e.g. "Brief")
% \website{...}  — final line of the top-right meta block; defaults to fiddlie.com
% \kicker{...}   — the eyebrow line shown above the title on the cover
% \lead{...}     — the intro paragraph shown under the title on the cover
% The meta-block year is not a field: it is pulled from \date (see below).
\gdef\pd@doctype{}
\newcommand{\doctype}[1]{\gdef\pd@doctype{#1}}
\gdef\pd@website{fiddlie.com}
\newcommand{\website}[1]{\gdef\pd@website{#1}}
\gdef\pd@kicker{}
\newcommand{\kicker}[1]{\gdef\pd@kicker{#1}}
\gdef\pd@lead{}
\newcommand{\lead}[1]{\gdef\pd@lead{#1}}

% Pull a four-digit year out of \@date (e.g. "June 2026" -> "2026"); leaves
% \pd@yearstr empty if the date carries no year. luacode is already loaded
% (via fiddlie-icons), so \directlua is available.
\gdef\pd@yearstr{}
% (The year pattern uses [0-9] rather than %d: a literal % would start a TeX
% comment inside the \directlua argument.)
\newcommand{\pd@setyear}{%
  \directlua{
    local d = "\luaescapestring{\@date}"
    token.set_macro("pd@yearstr", d:match("[0-9][0-9][0-9][0-9]") or "")
  }%
}

% ---------------------------------------------------------------------------
% Tricolour top bar (pink / yellow / blue), full-bleed on the first page
% ---------------------------------------------------------------------------
% Proportions and height mirror the source artwork. Drawn as a background
% picture so it sits flush with the paper edge, independent of margins.
\newlength{\pd@barheight}\setlength{\pd@barheight}{5pt}
\newlength{\pd@bary}
\newcommand{\pd@topbar}{%
  \AddToShipoutPictureBG*{%
    \setlength{\pd@bary}{\dimexpr\paperheight-\pd@barheight\relax}%
    \put(0,0){%
      \begin{tikzpicture}
        \useasboundingbox (0,0) rectangle (\paperwidth,\paperheight);
        \fill[brandpink]   (0,\pd@bary)              rectangle (0.25\paperwidth,\paperheight);
        \fill[brandyellow] (0.25\paperwidth,\pd@bary) rectangle (0.50\paperwidth,\paperheight);
        \fill[brandblue]   (0.50\paperwidth,\pd@bary) rectangle (\paperwidth,\paperheight);
      \end{tikzpicture}%
    }%
  }%
}

% ---------------------------------------------------------------------------
% Footer — stamped into the page margin on every page
% ---------------------------------------------------------------------------
% The footer is drawn as a foreground overlay rather than via fancyhdr so the
% page indicator can sit square in the bottom-right corner: inset equally
% from the right and bottom edges (= the side margin). The document
% reference sits bottom-left on the same baseline. No running header.
\pagestyle{empty}

% Zero-padded "01 / 02" page indicator — small, bold, gently letterspaced.
\newcommand{\pd@two}[1]{\ifnum#1<10 0\fi\number#1}
\newcommand{\pd@pagenum}{\textls[120]{\pd@two{\thepage}\,/\,\pd@two{\getpagerefnumber{LastPage}}}}

% Bottom-left footer: the document reference (document ID with revision) on
% top, and the build ID beneath it — the latter always shown so local builds
% are flagged (it defaults to a LOCAL marker in fiddlie-common). With no
% document ID, only the build ID line remains.
\newcommand{\pd@footleft}{%
  \pd@footfont\color{pdfade}%
  \ifx\@documentId\@empty
    {\tiny\@buildid}%
  \else
    \shortstack[l]{\@documentId\,\textperiodcentered\,Rev~\@revision\\[1pt]{\tiny\@buildid}}%
  \fi
}

% Footer insets. The page number is squared into the corner (equal inset
% from the right and bottom edges); the bottom inset is a touch smaller than
% the side inset so the whole footer sits a little closer to the page edge.
\newlength{\pd@footside}\setlength{\pd@footside}{1.6cm}
\newlength{\pd@footbottom}\setlength{\pd@footbottom}{1.45cm}
\newcommand{\pd@footfont}{\scriptsize}
\AddToShipoutPictureFG{%
  % Bottom-right: page number.
  \put(\LenToUnit{\dimexpr\paperwidth-\pd@footside\relax},\LenToUnit{\pd@footbottom}){%
    \makebox(0,0)[rb]{\pd@footfont\bfseries\color{pdink}\pd@pagenum}%
  }%
  % Bottom-left: document reference + build ID.
  \put(\LenToUnit{\pd@footside},\LenToUnit{\pd@footbottom}){%
    \makebox(0,0)[lb]{\pd@footleft}%
  }%
}

% ---------------------------------------------------------------------------
% Eyebrow / kicker label — short blue rule + letterspaced uppercase blue text
% ---------------------------------------------------------------------------
% Use it on the cover (via \kicker) or inline before any section to introduce
% it, echoing "— A NOTE BEFORE WE BEGIN" in the source.
\newcommand{\eyebrow}[1]{%
  \par\addvspace{2pt}%
  {\color{brandblue}\rule[0.25ex]{1.2em}{1.5pt}}\hspace{0.6em}%
  {\pd@eyebrowfont\pd@caps{#1}}\par
}

% ---------------------------------------------------------------------------
% Accent — colour a single word/phrase inside a title or run of text
% ---------------------------------------------------------------------------
% \accentword{work}            -> brand blue (default)
% \accentword[brandpink]{...}  -> any xcolor name (brandpink/brandyellow/...)
% Declared expandable so hyperref reaches the \texorpdfstring when the
% command appears inside a title or heading: it then emits just the plain
% word into PDF metadata/bookmarks (where colour has no meaning), while
% typesetting the coloured word everywhere else.
\DeclareExpandableDocumentCommand{\accentword}{O{brandblue} m}{%
  \texorpdfstring{\textcolor{#1}{#2}}{#2}%
}

% ---------------------------------------------------------------------------
% Cover masthead
% ---------------------------------------------------------------------------
% Logo (left) + meta block (right), then the eyebrow, the two-tone display
% title, and an optional lead paragraph. Replaces fiddlie-common's full-page
% title layout.
% Doctype line in near-black, the revision and website lines in muted grey,
% echoing the source artwork.
\newcommand{\pd@metablock}{%
  \pd@setyear
  \ifx\pd@doctype\@empty\else{\color{pdink}\pd@caps{\pd@doctype}}\\[2pt]\fi
  {\color{pdfade}\pd@caps{Document Rev \@revision\ifx\pd@yearstr\@empty\else\ /\ \pd@yearstr\fi}}\\[2pt]
  {\color{pdfade}\pd@caps{\pd@website}}%
}
\renewcommand{\maketitle}{%
  \pd@topbar
  \thispagestyle{empty}%
  \vspace*{0pt}%
  \noindent
  {\companylogo[height=1.05cm]}\hfill
  \begin{minipage}[b]{0.5\textwidth}\raggedleft\pd@metafont
    \pd@metablock
  \end{minipage}\par
  \vspace{1.3cm}%
  \ifx\pd@kicker\@empty\else\eyebrow{\pd@kicker}\vspace{0.5cm}\fi
  {\pd@titlefont\color{pdink}\@title\par}%
  \ifx\pd@lead\@empty\else
    \vspace{0.45cm}{\large\color{pdbody}\pd@lead\par}%
  \fi
  \vspace{0.6cm}%
}

% ---------------------------------------------------------------------------
% Headings — \section is a big two-tone-capable display heading, \subsection
% a compact bold lead-in (the kind that sits above a short run of bullets).
% ---------------------------------------------------------------------------
\titleformat{\section}{\pd@sectionfont\color{pdink}}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.4\baselineskip}{0.6\baselineskip}
\titleformat{\subsection}{\pd@subsectionfont\color{pdink}}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{0.9\baselineskip}{0.3\baselineskip}

% ---------------------------------------------------------------------------
% Numbered cards — a rounded pale-blue chip ("01") above a bold heading
% ---------------------------------------------------------------------------
% \card{Heading}        -> auto-incrementing "01", "02", ...
% \card[A]{Heading}     -> explicit chip label "A"
% \card*{Heading}       -> reuse the current number (no increment)
% \cardreset            -> restart numbering from 01
\newcounter{pdcard}
\newcommand{\cardreset}{\setcounter{pdcard}{0}}
\newcommand{\pd@chip}[1]{%
  \tikz[baseline=(c.base)]{%
    \node[fill=brandblue!12, rounded corners=2.5pt,
          inner xsep=5pt, inner ysep=2.5pt,
          text=brandblue, font=\footnotesize\bfseries] (c) {\textls[80]{#1}};%
  }%
}
\NewDocumentCommand{\card}{s o m}{%
  \par\addvspace{0.9\baselineskip}%
  \IfValueTF{#2}{\def\pd@clabel{#2}}{%
    \IfBooleanF{#1}{\stepcounter{pdcard}}%
    \edef\pd@clabel{\pd@two{\value{pdcard}}}%
  }%
  \noindent\pd@chip{\pd@clabel}\par\nobreak\vspace{4pt}%
  {\pd@cardfont\color{pdink}#3}\par\nobreak\vspace{2pt}%
}

% ---------------------------------------------------------------------------
% Blue-dot bullet lists
% ---------------------------------------------------------------------------
% A solid round blue dot, a touch larger than the text, vertically centred.
\newcommand{\pd@bullet}{\tikz[baseline=-0.55ex]{\fill[brandblue] (0,0) circle (1.4pt);}}
\setlist[itemize]{label=\pd@bullet, leftmargin=1.6em,
  itemsep=0.5ex, parsep=0pt, topsep=0.4ex}

% ---------------------------------------------------------------------------
% Closing statement — a short coloured rule above a bold sign-off paragraph
% ---------------------------------------------------------------------------
\newcommand{\closing}[1]{%
  \par\addvspace{1.2\baselineskip}%
  \noindent{\color{brandblue}\rule{2.2em}{2pt}}\par\vspace{6pt}%
  {\pd@closingfont\color{pdink}#1\par}%
}

\endinput
