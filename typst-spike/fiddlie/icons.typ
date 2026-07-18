// fiddlie icons — Typst port of packages/fiddlie-icons.sty
// The name->codepoint table is generated from lua/fa-icons.lua (see fa-icons.typ).
#import "fa-icons.typ": codepoints, brand-only

// Style -> font family name. In production these are the FA7 Pro family names;
// for this spike we map onto the FA6 Free families that are actually installed.
// (The mapping is the only thing that changes when the Pro kit is present.)
#let _style-to-font = (
  "solid":   "Font Awesome 6 Free Solid",
  "regular": "Font Awesome 6 Free Regular",
  "brands":  "Font Awesome 6 Brands Regular",
)

// \faicon[style]{name}  ->  faicon("name", style: "solid")
#let faicon(name, style: "solid") = {
  let cp = codepoints.at(name, default: none)
  if cp == none {
    panic("fiddlie-icons: unknown icon name '" + name + "'")
  }
  let fam = if brand-only.at(name, default: false) {
    _style-to-font.at("brands")
  } else {
    _style-to-font.at(style, default: none)
  }
  if fam == none { panic("fiddlie-icons: unknown style '" + style + "'") }
  text(font: fam)[#str.from-unicode(int(cp, base: 16))]
}

// \bigicon[style]{size}{name}
#let bigicon(name, size: 3cm, style: "solid") = {
  text(size: size)[#faicon(name, style: style)]
}
