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

% ============================================================================
% Requirement ID Tracking and Duplicate Detection
% ============================================================================
% This system tracks all requirement IDs used in the document to:
%   1. Detect duplicate IDs (same number used twice, even with different prefixes)
%   2. Report the next available ID in the compilation log (highest number + 1)
%
% IDs are extracted from the format PREFIX-NNN (e.g., CR-001, TR-042).
% The numeric portion is tracked globally - you cannot have CR-010 and TR-010.
%
% Usage remains unchanged:
%   \req{CR-001}{Description}{\musthave}
%
% At the end of compilation, the log will show:
%   "Requirements: Next available ID is XXX (highest used: YYY)"
% ============================================================================

% Load the requirement tracking Lua module
% Note: Use \luaescapestring and avoid bare % in patterns (TeX interprets as comment)
\directlua{
  local function load_reqtracker_module()
    local loader_path = kpse.find_file("req-tracker.lua", "lua")
    if loader_path then
      return dofile(loader_path)
    end
    local cls_path = kpse.find_file("requirements.cls", "tex")
    if cls_path then
      local dir = cls_path:match("(.-)[^/]*$")
      loader_path = dir .. "../lua/req-tracker.lua"
      local f = io.open(loader_path, "r")
      if f then
        f:close()
        return dofile(loader_path)
      end
    end
    texio.write_nl("term and log", "WARNING: req-tracker.lua not found")
    return {
      register = function() return true, nil end,
      getMaxId = function() return 0 end,
      getCount = function() return 0 end,
      getNextId = function() return "001" end,
      printSummary = function() end,
    }
  end
  reqtracker = load_reqtracker_module()
}

% Internal command to check and register a requirement ID
% Issues an error if duplicate
\newcommand{\@registerReqId}[1]{%
  \directlua{
    local id = "\luaescapestring{#1}"
    local ok, existing = reqtracker.register(id)
    if not ok then
      tex.error("Duplicate requirement ID: " .. id .. " (conflicts with " .. existing .. ")")
    end
  }%
}

% Hook to print summary at end of document
\AtEndDocument{\directlua{reqtracker.printSummary()}}

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
% The ID is registered for duplicate detection and next-ID tracking.
\newcommand{\req}[3]{%
  \@registerReqId{#1}%
  \reqid{#1} & #2 & #3 \\
  \hline
}

% Glossary table environment
% Usage:
%   \begin{glossarytable}
%     \term{ABC}{The first three letters of the alphabet}
%     \term{API}{Application Programming Interface}
%   \end{glossarytable}
%
% Optional argument sets the term column width (default 3cm):
%   \begin{glossarytable}[4cm]
%     ...
%   \end{glossarytable}

% Glossary table environment using longtable
% Usage:
%   \begin{glossarytable}
%     \term{ABC}{The first three letters of the alphabet}
%   \end{glossarytable}
%
% Optional arguments: [term width][definition width] (defaults: 3cm, 12cm)
%   \begin{glossarytable}[4cm]           % 4cm term, 12cm definition
%   \begin{glossarytable}[4cm][10cm]     % 4cm term, 10cm definition

\NewDocumentEnvironment{glossarytable}{O{3cm}O{12cm}}{%
  \begin{longtable}{|L{#1}|L{#2}|}
    \hline
    \rowcolor{lightgray}
    \textbf{Term} & \textbf{Definition} \\
    \hline
    \endfirsthead
    \hline
    \rowcolor{lightgray}
    \textbf{Term} & \textbf{Definition} \\
    \hline
    \endhead
}{%
  \end{longtable}
}

% Glossary term command for use inside glossarytable
% Usage: \term{Term}{Definition}
% Example: \term{API}{Application Programming Interface}
\newcommand{\term}[2]{%
  \textbf{#1} & #2 \\
  \hline
}

\endinput
