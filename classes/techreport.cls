\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{techreport}[2026/05/11 Fiddlie Report Class]

% The class is based on the article class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[a4paper,11pt]{article}

% Load common Fiddlie styles
\RequirePackage{fiddlie-common}

% Put breaks after section titles
\RequirePackage{titlesec}
\newcommand{\sectionbreak}{\clearpage}

\renewcommand{\importantnotice}{%
  \section*{Important Notice}
  \begin{small}
    \MakeUppercase{The findings, measurements, and analysis presented in this report reflect the specific conditions, equipment, and methodology described herein and are provided for informational purposes only.}

    Results may not generalise to other configurations, environments, or use cases. Conclusions are based on data available at the time of writing and may be superseded by further investigation. Readers should independently verify any findings before relying on them for design, qualification, or production decisions.

    Fiddlie makes no warranty as to the accuracy, completeness, or applicability of the information in this report, and disclaims all liability for any loss, damage, or injury arising from its use, whether direct, indirect, incidental, or consequential.

    For questions about methodology or to request raw data, contact: \texttt{info@fiddlie.com}.
  \end{small}
}

\endinput
