// fiddlie/prettydoc.typ — Typst port of classes/prettydoc.cls
#import "common.typ": brand-pink, brand-yellow, brand-blue, company-logo, faicon

// Neutral text tones from the source artwork.
#let pd-ink  = rgb("#1A1A1A")
#let pd-body = rgb("#444A52")
#let pd-fade = rgb("#8A9099")

// Letterspaced uppercase — the brand label look (\pd@caps -> \textls[140]).
#let caps(body) = text(tracking: 0.14em)[#upper(body)]

// \accentword — colour a word inside a title/run (blue by default).
#let accent(body, color: brand-blue) = text(fill: color, body)

// Zero-padded two-digit page number (\pd@two).
#let _two(n) = if n < 10 { "0" + str(n) } else { str(n) }

// \eyebrow — short blue rule + letterspaced blue caps kicker.
#let eyebrow(body) = block(above: 1.2em, below: 0.7em)[
  #box(baseline: -0.15em, line(length: 1.2em, stroke: 1.5pt + brand-blue))
  #h(0.6em)
  #text(size: 9pt, weight: 600, fill: brand-blue)[#caps(body)]
]

// Auto-incrementing numbered card: a pale-blue rounded chip above a heading.
#let _card-ctr = counter("pdcard")
#let card(body, label: none) = {
  block(above: 1.2em, below: 0.3em)[
    #context {
      let lbl = if label != none { label } else {
        _card-ctr.step()
        _two(_card-ctr.get().first() + 1)
      }
      box(
        fill: brand-blue.lighten(88%), inset: (x: 5pt, y: 2.5pt),
        radius: 2.5pt,
      )[#text(size: 9pt, weight: 600, fill: brand-blue, tracking: 0.08em)[#lbl]]
    }
    #v(4pt, weak: true)
    #text(size: 14pt, weight: 600, fill: pd-ink)[#body]
    #v(2pt, weak: true)
  ]
}

// \closing — coloured rule above a bold sign-off paragraph.
#let closing(body) = block(above: 1.4em)[
  #line(length: 2.2em, stroke: 2pt + brand-blue)
  #v(6pt, weak: true)
  #text(size: 13pt, weight: 600, fill: pd-ink)[#body]
]

// The template.
#let prettydoc(
  title: none, kicker: none, lead: none,
  doctype: none, revision: none, documentId: none,
  author: none, date: none, website: "fiddlie.com",
  buildid: "LOCAL - NOT FOR RELEASE",
  body,
) = {
  // Year pulled out of the date string (\pd@setyear, but native regex).
  let year = if type(date) == str {
    let m = date.matches(regex("[0-9]{4}"))
    if m.len() > 0 { m.first().text } else { none }
  } else { none }

  set text(font: ("Montserrat", "Liberation Sans"), size: 10pt, fill: pd-body)
  set par(justify: false, leading: 0.7em, spacing: 1.35em)

  set page(
    paper: "a4",
    margin: (left: 1.6cm, right: 1.6cm, top: 1.2cm, bottom: 2.2cm),
    // Full-bleed tricolour bar — first page only (eso-pic BG -> native bg).
    background: context {
      if here().page() == 1 {
        place(top, dx: 0pt, dy: 0pt, block(width: 100%, height: 5pt)[
          #place(left, rect(width: 25%, height: 5pt, fill: brand-pink))
          #place(left, dx: 25%, rect(width: 25%, height: 5pt, fill: brand-yellow))
          #place(left, dx: 50%, rect(width: 50%, height: 5pt, fill: brand-blue))
        ])
      }
    },
    // Margin-stamped footer (eso-pic FG -> native footer grid).
    footer: context {
      let ref = if documentId != none {
        [#documentId #sym.dot.c Rev #revision]
      } else { none }
      let total = counter(page).final().first()
      grid(columns: (1fr, auto),
        align: (left + bottom, right + bottom),
        text(size: 8pt, fill: pd-fade)[
          #if ref != none [#ref\ ]
          #text(size: 6pt)[#buildid]
        ],
        text(size: 8pt, weight: 600, fill: pd-ink, tracking: 0.12em)[
          #_two(counter(page).get().first())#sym.space.thin\/#sym.space.thin#_two(total)
        ],
      )
    },
  )

  set heading(numbering: none)
  show heading.where(level: 1): it => block(above: 1.6em, below: 0.7em,
    text(size: 22pt, weight: 600, fill: pd-ink)[#it.body])
  show heading.where(level: 2): it => block(above: 1.1em, below: 0.55em,
    text(size: 13pt, weight: 600, fill: pd-ink)[#it.body])

  // Blue-dot bullet lists (\pd@bullet -> native list marker).
  set list(marker: text(fill: brand-blue)[#sym.bullet], indent: 0.6em,
    spacing: 0.9em, body-indent: 0.5em)
  show list: it => block(above: 0.7em, below: 0.7em, it)

  // --- Cover masthead ---
  grid(columns: (1fr, auto), align: (left + bottom, right + bottom),
    company-logo(height: 1.05cm),
    text(size: 8pt, fill: pd-fade)[
      #set par(leading: 0.8em)
      #if doctype != none [#text(fill: pd-ink)[#caps(doctype)]\ ]
      #caps[Document Rev #revision#if year != none [ \/ #year]]\
      #caps(website)
    ],
  )
  v(1.3cm)
  if kicker != none { eyebrow(kicker); v(0.5cm) }
  text(size: 30pt, weight: 600, fill: pd-ink)[#title]
  if lead != none { v(0.45cm); text(size: 13pt, fill: pd-body)[#lead] }
  v(0.6cm)

  body
}
