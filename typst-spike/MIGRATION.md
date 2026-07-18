# Migration prototype: `latex2typ.py`

A working prototype of the hybrid **deterministic + LLM-fallback** migrator for
existing `.tex` documents. See `migrate/latex2typ.py`.

## Design

A **deterministic pass** handles the standard, well-understood constructs with
exact, idempotent, reviewable transforms. Anything it does *not* recognise with
high confidence is left in place, wrapped in a `// TODO[llm]:` block that
records the original LaTeX and a machine-readable reason. A second stage (a
per-block LLM call — not wired up here) resolves those. The deterministic layer
is cheap and exact; the LLM is paid for only the genuinely hard tail.

Deterministic coverage today:

- `\documentclass` + preamble metadata (`\title`, `\revision`, `\doctype`, …)
  → template `#show: cls.with(...)` args
- sectioning (`\section`/`\subsection`) → `=` / `==`
- inline markup (`\textbf`, `\emph`/`\textit`, `\texttt`, `\verb`) with a
  **balanced-brace scanner** so nested macros survive
- fiddlie commands: `\accentword`, `\card`, `\eyebrow`, `\closing`, `\faicon`
- `itemize`/`enumerate` → `-` / `+`
- `\clearpage`/`\tableofcontents` → `pagebreak()`/`outline()`
- LaTeX comment stripping (so commented-out macros aren't parsed)

Escalated to LLM (flagged, not guessed): `tabular`/`tabularx`/`longtable` and
the custom table environments (`requirementstable`, `glossarytable`), plus any
unrecognised environment (e.g. `tikzpicture`).

## Results on the repo's own examples

| source | deterministic | escalated to LLM |
|---|---|---|
| `prettydoc-example.tex` | **100%** | 0 blocks |
| `datasheet-example.tex` | body + metadata | 1 (`tabularx`) |
| `requirements-example.tex` | body + metadata | 2 (`requirementstable`, `glossarytable`) |

`prettydoc-example.tex` migrates **fully automatically** — the generated
`migrate/prettydoc.auto.typ` compiles and renders faithfully against the
original LaTeX (`compare-auto.png`), with no manual intervention.

## Lessons (all fixed here, all deterministic)

Building the prototype surfaced exactly the failure modes a real migrator must
handle — none of which needed an LLM:

1. **Nested braces** — `\title{Working \accentword{together}, simply.}` breaks a
   naive `\{(.*?)\}` regex (it stops at the first `}`). Fixed with a
   balanced-delimiter scanner (`grab()`).
2. **Silent corruption risk** — a mangled extraction can still *compile* as
   wrong content. The deterministic pass must be conservative and flag what it
   can't cleanly balance rather than emit plausible-but-wrong output.
3. **Comments** — a `%`-commented `\website{}` was being parsed. Fixed by
   stripping LaTeX line comments first.

## What a production version adds

- Table transforms as a real deterministic rule (column spec + cell walk)
  rather than an LLM escalation — the fiddlie table envs are regular enough.
- Math (`amsmath`) → Typst math via a dedicated sub-transpiler.
- The LLM stage: one call per `TODO[llm]` block, given the LaTeX + the target
  Typst template's API, returning a compilable snippet; then a compile-and-diff
  gate so a human reviews only blocks that fail to round-trip.
