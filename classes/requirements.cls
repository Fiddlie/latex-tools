\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{requirements}[2025/09/01 Fiddlie Requirements Class]

% The class is based on the article class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[a4paper,11pt]{article}

% Load common Fiddlie styles
\RequirePackage{fiddlie-common}

% Put breaks after section titles
\RequirePackage{titlesec}
\newcommand{\sectionbreak}{\clearpage}

% Additional packages for requirements documents
\RequirePackage{longtable}
\RequirePackage{booktabs}
\RequirePackage{enumitem}
\RequirePackage{array}
\RequirePackage{colortbl}
% Note: TikZ is loaded by fiddlie-common

% xparse for advanced command definitions
\RequirePackage{xparse}

% Additional colour definitions for requirements
\definecolor{headergray}{RGB}{80, 80, 80}
\definecolor{lightgray}{RGB}{240, 240, 240}
\definecolor{tableborder}{RGB}{200, 200, 200}
\definecolor{tabred}{RGB}{255, 51, 102}
\definecolor{tabyellow}{RGB}{255, 204, 0}

% Custom commands for requirements
\newcommand{\reqid}[1]{\texttt{#1}}
\newcommand{\priority}[1]{\uppercase{#1}}
\newcommand{\musthave}{\cellcolor{tabred!20}\priority{Must}}
\newcommand{\shouldhave}{\cellcolor{tabyellow!30}\priority{Should}}
\newcommand{\couldhave}{\cellcolor{lightgray}\priority{Could}}

% Table column types
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}

% Document conventions command
\newcommand{\makedocumentconventions}{%
  \subsection{Document Conventions}

  Requirements are identified using the following prefixes:

  \begin{tabularx}
    {\textwidth}{|c|X|} \hline \rowcolor{lightgray} \textbf{Prefix} & \textbf{Requirement Category} \\
    \hline BR & Business Requirement \\
    \hline CR & Customer Requirement \\
    \hline TR & Technical Requirement \\
    \hline ER & Environmental Requirement \\
    \hline SR & Safety Requirement \\
    \hline
  \end{tabularx}

  \vspace{0.5cm}

  Priority levels are defined as:

  \begin{itemize}
    \item \textbf{Must} --- Mandatory requirement; system cannot ship without compliance
    \item \textbf{Should} --- Important requirement; non-compliance requires justification
    \item \textbf{Could} --- Desirable requirement; included if resources permit
  \end{itemize}
}

% Requirements table environment
% Usage:
%   \begin{requirementstable}
%     \req{CR-001}{System shall do something}{\musthave}
%     \req{CR-002}{System should do something else}{\shouldhave}
%   \end{requirementstable}
%
% Optional argument sets the requirement column width (default 9cm):
%   \begin{requirementstable}[11cm]
%     ...
%   \end{requirementstable}

\NewDocumentEnvironment{requirementstable}{O{9cm}}{%
  \begin{longtable}{|c|L{#1}|c|}
    \hline
    \rowcolor{lightgray}
    \textbf{ID} & \textbf{Requirement} & \textbf{Priority} \\
    \hline
    \endfirsthead
    \hline
    \rowcolor{lightgray}
    \textbf{ID} & \textbf{Requirement} & \textbf{Priority} \\
    \hline
    \endhead
}{%
  \end{longtable}
}

% Requirement row command for use inside requirementstable
% Usage: \req{ID}{Description}{Priority}
% Example: \req{CR-001}{The system shall respond within 100ms}{\musthave}
\newcommand{\req}[3]{%
  \reqid{#1} & #2 & #3 \\
  \hline
}

\endinput
