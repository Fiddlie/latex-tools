\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{policy}[2026/05/11 Fiddlie Policy Class]

% The class is based on the article class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[a4paper,11pt]{article}

% Load common Fiddlie styles
\RequirePackage{fiddlie-common}

% Put breaks after section titles
\RequirePackage{titlesec}
\newcommand{\sectionbreak}{\clearpage}

\endinput
