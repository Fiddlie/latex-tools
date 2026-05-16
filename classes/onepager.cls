\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{onepager}[2026/05/16 Fiddlie One-pager Class]

% The class is based on the article class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[a4paper,11pt]{article}

% Load common Fiddlie styles
\RequirePackage{fiddlie-common}

% No per-section page breaks — one-pager layout.
\RequirePackage{titlesec}
\newcommand{\sectionbreak}{}

% Tighter geometry, vertical rhythm, and column gap for a one-page layout.
\geometry{left=1.5cm, top=1.8cm, right=1.5cm, bottom=2cm, headheight=22pt}
\setlength{\parskip}{0.7ex plus 0.2ex minus 0.1ex}
\renewcommand{\arraystretch}{1.15}
\setlength{\columnsep}{0.8cm}

% Discourage breaking paragraphs across columns: a widow (last line of a
% paragraph alone at the top of the next column) or an orphan (first line
% alone at the bottom) costs the maximum penalty, so TeX will reflow to
% keep paragraphs together unless there's no other option.
\widowpenalty=10000
\clubpenalty=10000

% \dotsection{colour}{Title}
% A coloured filled-circle bullet followed by a bold title, echoing the
% dots in the Fiddlie logo. Pass any xcolor name; brandpink/brandyellow/
% brandblue are predefined.
\newcommand{\dotsection}[2]{%
  \par\addvspace{6pt}\noindent
  \tikz[baseline=-0.5ex]\fill[#1] (0,0) circle (3pt);\hspace{4pt}\textbf{#2}%
  \par\nobreak\vspace{1pt}%
}

% Convenience shortcuts that cycle through the standard palette.
\newcommand{\pinksection}[1]{\dotsection{brandpink}{#1}}
\newcommand{\yellowsection}[1]{\dotsection{brandyellow}{#1}}
\newcommand{\bluesection}[1]{\dotsection{brandblue}{#1}}

% \iconsection[colour]{icon}{Title}
% Heading variant of \dotsection — a FontAwesome icon in place of the dot.
% Colour is optional (defaults to current text colour); pass any xcolor
% name including the brand palette. Icon is always solid; for other styles
% build a custom heading with \faicon directly.
\NewDocumentCommand{\iconsection}{o m m}{%
  \par\addvspace{6pt}\noindent
  \IfValueTF{#1}{\textcolor{#1}{\faicon{#2}}}{\faicon{#2}}%
  \hspace{4pt}\textbf{#3}%
  \par\nobreak\vspace{1pt}%
}

% \begin{twocol} ... \end{twocol} / \begin{threecol} ... \end{threecol}
% Thin wrappers around multicols (loaded by fiddlie-common) that drop to
% \small — the size most one-pagers want in their columned body.
\newenvironment{twocol}{\begin{multicols}{2}\small}{\end{multicols}}
\newenvironment{threecol}{\begin{multicols}{3}\small}{\end{multicols}}

% Compact masthead — logo (left) + revision/date/id (right), thin rule,
% then the document title in large bold. Replaces the full-page title
% layout from fiddlie-common.
\renewcommand{\maketitle}{%
  \pagestyle{firstpage}\thispagestyle{firstpage}%
  {\companylogo[height=1cm]}\hfill
  \begin{minipage}[b]{6cm}\raggedleft
    {\small Revision \@revision\ \textperiodcentered\ \@date}\\
    {\scriptsize\textit{\@documentId}}
  \end{minipage}\\[-2pt]
  \noindent\rule{\textwidth}{1pt}\\[2pt]
  {\LARGE\bfseries\@title}\\[4pt]
}

\endinput
