// fiddlie/common.typ — Typst port of packages/fiddlie-common.sty (shared core)
#import "icons.typ": faicon, bigicon

// Brand colours — the dots in the Fiddlie logo (from fiddlie-common.sty).
#let brand-pink   = rgb("#FF006E")
#let brand-yellow = rgb("#FFBE0B")
#let brand-blue   = rgb("#3A86FF")

// Path to the shared logo asset (SVG loads natively — no graphicspath/kpse).
#let logo-path = "assets/fiddlie-logo.svg"
#let company-logo(height: 0.6cm) = image(logo-path, height: height)

// --- Manifest ---------------------------------------------------------------
// Replaces manifest-loader.lua (189 lines) + fiddlie-manifest.sty entirely.
// `yaml()` is native; dependency tracking is automatic.
#let load-manifest(path) = yaml(path)

// Revision-history table straight from a manifest's `history` list.
#let revision-history(manifest) = {
  let rows = ()
  for h in manifest.at("history", default: ()) {
    rows += (h.at("revision", default: ""), h.at("date", default: ""),
             h.at("author", default: ""), h.at("changes", default: ""))
  }
  table(
    columns: (auto, auto, auto, 1fr),
    stroke: 0.5pt + luma(180),
    table.header([*Revision*], [*Date*], [*Author*], [*Changes*]),
    ..rows,
  )
}
