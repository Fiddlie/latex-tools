#import "../fiddlie/prettydoc.typ": *
#import "../fiddlie/common.typ": brand-pink, brand-yellow, brand-blue

#show: prettydoc.with(
  title: [Working #accent[together], simply.],
  author: "Fiddlie",
  date: "June 2026",
  documentId: "FD-DC-LTX-10001",
  revision: "A",
  doctype: "Brief",
  kicker: "A quick orientation",
  lead: "A short, brand-styled template you can drop any public-facing content
into — briefs, guides, proposals or client notes. Replace the copy; the
styling looks after itself.",
)

#eyebrow[What this template gives you]
The building blocks below are the same ones used across Fiddlie's
public-facing documents. Each is a single command, so a document stays
readable in source and consistent in print.
#card[A branded cover]
- A full-bleed *tricolour bar* along the top edge
- The #raw("fiddlie.") wordmark with a right-aligned metadata block
- A two-tone display title and an optional lead paragraph

#card[Eyebrow labels]
- Use #raw("\\eyebrow{...}") to introduce a section in letterspaced blue caps
- The same treatment appears above the cover title via #raw("\\kicker{}")

#card[Numbered cards]
- #raw("\\card{Heading}") draws the chip and heading you see here
- Numbering is automatic; pass #raw("\\card[A]{...}") to set a label, or

#card[Blue-dot lists]
- Ordinary #raw("itemize") lists pick up the brand bullet automatically
- *Inline emphasis* works exactly as usual

#pagebreak()
#eyebrow[Putting it to use]
= Write #accent(color: brand-pink)[ordinary] LaTeX.
There is no special body layout to learn. Headings, paragraphs and lists all
inherit the brand styling, so you can focus on the content.
== Section headings
Use #raw("\\section{...}") for big display headings — they accept #raw("#accent[]")
for a two-tone effect. Use #raw("\\subsection{...}") for the compact bold lead-ins
that sit above a short run of bullets, like this one.
== Two-tone accents
- #raw("#accent[word]") colours a word in brand #accent[blue]
- #raw("#accent(color: brand-pink)[word]") uses #accent(color: brand-pink)[pink]
- #raw("#accent(color: brand-yellow)[word]") uses #accent(color: brand-yellow)[yellow]

== Footer and metadata
Every page carries the document reference — #raw("\\documentId{}") with the
revision — bottom-left, with the build ID on a line beneath it (a LOCAL
marker until a release build sets it). A small bold #accent[01 / 02]
page indicator sits squared into the bottom-right corner. The cover's meta
block is driven by #raw("\\doctype{}"), #raw("\\revision{}") and #raw("\\website{}");
the year is pulled from #raw("\\date{}").
\closing{Swap in your own content and the document stays on-brand —
predictable structure, so the writing has room to breathe.}
