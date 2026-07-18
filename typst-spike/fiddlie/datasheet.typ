// fiddlie/datasheet.typ — Typst port of classes/datasheet.cls + the
// fiddlie-common furniture it relies on (fancyhdr header/footer, maketitle,
// importantnotice, section-per-page).
#import "common.typ": company-logo

#let important-notice = [
  #heading(level: 1, numbering: none, outlined: false)[Important Notice]
  #set text(size: 9pt)
  #upper[The information contained in this datasheet is provided for general
  guidance only. While Fiddlie has exercised reasonable care in its
  preparation, no warranty is given as to the accuracy, completeness, or
  fitness for any particular purpose of this information.]

  Users are responsible for determining the suitability of products and
  components for their specific applications. All specifications are subject
  to change without notice.

  For technical support or clarification of specifications, contact:
  #raw("info@fiddlie.com").
]

#let datasheet(
  title: none, shorttitle: none, author: none, date: none,
  documentId: none, revision: none, draft: false,
  buildid: "LOCAL - NOT FOR RELEASE",
  body,
) = {
  set text(font: "Liberation Sans", size: 11pt)
  set par(spacing: 1.4em, leading: 0.7em)

  let footer = context {
    let total = counter(page).final().first()
    grid(columns: (1fr, 1fr, 1fr),
      align: (left, center, right),
      text(size: 9pt)[#revision\ #text(size: 6pt)[#buildid]],
      text(size: 9pt)[#date],
      text(size: 9pt)[Page #counter(page).get().first() of #total],
    )
  }
  let header = context {
    if counter(page).get().first() > 1 {
      grid(columns: (1fr, auto),
        align: (left + horizon, right + horizon),
        emph(shorttitle), company-logo(height: 0.6cm))
      line(length: 100%, stroke: 0.5pt)
    }
  }

  set page(paper: "a4", margin: (left: 2cm, right: 2cm, top: 3cm, bottom: 3cm),
    header: header, footer: footer,
    background: if draft {
      rotate(-55deg, text(size: 130pt, fill: luma(210))[*DRAFT*])
    })

  set heading(numbering: "1.")
  // \sectionbreak -> \clearpage : each top-level section starts a page.
  show heading.where(level: 1): it => { pagebreak(weak: true); it }

  // --- maketitle ---
  company-logo(height: 1.2cm)
  v(2cm)
  text(size: 24pt, weight: "bold")[#title]
  v(2pt)
  line(length: 100%, stroke: 1pt)
  v(0.5cm)
  text(size: 14pt)[Revision #revision, #date]
  v(0.2cm)
  emph(documentId)
  v(0.5cm)

  body
}
