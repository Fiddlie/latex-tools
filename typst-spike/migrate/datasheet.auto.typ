#import "../fiddlie/datasheet.typ": *
#import "../fiddlie/common.typ": brand-pink, brand-yellow, brand-blue

#show: datasheet.with(
  title: "Fiddlie Template",
  shorttitle: "Template",
  author: "Ed Hill",
  date: "September 2025",
  documentId: "FD-DC-LTX-?????",
  revision: "A-rc1",
  draft: true,
)

#outline()
= Introduction
Place your document content here...
= Revision History
// TODO[llm]: tabular-family: needs column-spec + cell mapping
// \begin{tabularx}
//   {\textwidth}{XXXX} \hline \textbf{Revision} & \textbf{Date} & \textbf{Author}
//   & \textbf{Changes} \\
//   \hline
//   \revisionnumber & - & - & Initial version \\
//   & & & \\
//   & & & \\
//   \hline
// \end{tabularx}

\importantnotice
