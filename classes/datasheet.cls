\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{datasheet}[2025/09/01 Fiddlie Datasheet Class]

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
