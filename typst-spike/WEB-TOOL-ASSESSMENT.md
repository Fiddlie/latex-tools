# Web-tool architecture assessment

Turning latex-tools into a hosted web product — authoring, document management
(currently AppSheet), revision control, and Google-Docs-style collaboration —
and how the Typst port changes what's possible.

## Why Typst is the enabler here (not an incidental choice)

The web-tool ambition is the strongest single argument for the port. The
compile engine has to run **server-side on every keystroke-ish edit** (for live
preview) and ideally **in the browser** too. Typst is built for this; LaTeX is
not.

- **Typst compiles in milliseconds and has an official WASM build**
  (`typst.ts`). You can run the compiler *in the browser* for instant preview,
  or on a tiny server sandbox. A full document recompiles faster than LaTeX
  finishes its first of several passes.
- **In-browser LaTeX** means shipping a ~100–300 MB TeX Live WASM blob and
  still waiting seconds per build. It's the reason Overleaf compiles
  server-side in heavyweight containers.
- Typst is a **single sandboxed binary with no shell-escape, no `\write18`, no
  arbitrary file/network I/O** — far easier to run safely as a multi-tenant
  hosted service than `lualatex --shell-escape`.

So: the document-tooling and the web-tooling decisions are really one decision.
Port to Typst → the web product becomes tractable.

## Target architecture

```
┌─────────────── Browser ───────────────┐        ┌─────────── Backend ──────────────┐
│  Editor (CodeMirror/Monaco)            │        │  Compile service (typst crate)   │
│   + Yjs CRDT (real-time collab)        │◀──ws──▶│   fonts provisioned once          │
│  Live preview (typst.ts WASM  OR       │        │   (FA Pro, Montserrat, Arial)     │
│    server SVG stream)                  │        │  Document store (Postgres)        │
│  Comment threads on source ranges      │        │   docs, revisions, status, tags   │
└────────────────────────────────────────┘        │  Asset store (S3/object)          │
                                                   │  Template registry (Typst pkg,    │
                                                   │   pinned & versioned)             │
                                                   └───────────────────────────────────┘
```

### 1. Documents as data
A document is just **Typst source + a manifest (YAML/JSON) + assets**. That's
already how the repo works. In the web tool the source/manifest live in
Postgres rows (or a git blob store) and assets in object storage. Because the
content is concise plain text, everything downstream — diffing, versioning,
CRDT collaboration, search — is natural. (This is *much* nicer than diffing
LaTeX, and impossible to do well with binary formats.)

### 2. Templates as a versioned package
The ported `fiddlie` templates (see `../typst-spike/fiddlie/`) publish as a
**Typst package** with a semver. Each document pins a version
(`#import "@fiddlie/templates:1.4.0"`). Upgrading a brand style becomes a
version bump + recompile, not a submodule dance. This replaces the git-submodule
consumption model entirely.

### 3. Compilation service
Server-side `typst` (the Rust crate, called in-process — no subprocess) in a
sandbox. **Fonts are provisioned once on the server** — this permanently kills
the per-machine FontAwesome-Pro install pain (`fdoc fonts install`), the
TEXMFHOME juggling, and the "spaces in font filenames" TeX Live quirk. FA Pro
licensing still applies, but it's one server-side install instead of one per
user per machine.

### 4. Document management (replacing AppSheet)
`cli/src/fdoc/appsheet.py` already pushes revision metadata to AppSheet's REST
API — so the data model is understood. Bring it in-house as a first-class
`documents` table (id, title, type, owner, current revision, draft/locked
status, tags, timestamps) with search, filtering and dashboards. The generic
half of the `fdoc` CLI (`rev`, `name`, manifest I/O, `appsheet` sync) is
engine-agnostic and becomes the **backend domain layer** more or less as-is.
Postgres (e.g. Neon) is a fine home; the existing YAML manifest maps directly
to columns/JSONB.

### 5. Revision control
Today: `fdoc rev lock` bumps the manifest, commits, and creates a git tag.
In the web tool this becomes **DB-backed immutable revisions** with the same
semantics (draft → locked, build IDs, "A" → "B" bumps). You can keep git under
the hood (each doc a repo, revisions = tags) or model revisions as rows. Either
way the current logic transfers; the state machine is already written.

### 6. Google-Docs-style collaboration — the hard part
Two layers, both feasible:

- **Real-time co-editing of source:** a **CRDT (Yjs or Automerge)** over the
  Typst source text gives multi-cursor, offline-tolerant, conflict-free
  editing. This is mature, off-the-shelf tech (Yjs + `y-websocket`). Because
  Typst source is *just text*, it drops straight in — the same reason Google
  Docs can't operate on a `.docx` blob but can on structured text.
- **Comments & suggestions:** anchor comment threads to **source ranges
  expressed as CRDT-relative positions** so they survive concurrent edits
  (Yjs `RelativePosition`). Rendering comments *next to the preview* rather than
  the source needs a **source↔output map**: Typst exposes element locations via
  its `query`/introspection system (analogous to SyncTeX), so a click in the
  SVG preview can map back to a source span. This mapping is the one genuinely
  novel piece of engineering.

### 7. Live preview
Two options, not mutually exclusive:
- **Client-side** via `typst.ts` WASM — zero server round-trip, instant.
- **Server-side** streaming SVG/PDF — needed anyway for the canonical PDF
  export and for very large documents. SVG preview keeps text selectable and
  supports the click-to-source mapping above.

## Build vs. buy

- **`typst.app`** is the official *collaborative web editor* for Typst
  (real-time co-editing, teams) — essentially "Overleaf for Typst," and it
  already exists. If plain collaborative authoring is enough, adopting or
  self-hosting-adjacent to it could skip most of layer 6. It is **not** a
  document-management / revision-governance / AppSheet-replacement system,
  though — that part you build regardless.
- **Overleaf** is the LaTeX analog. Staying on LaTeX effectively means adopting
  Overleaf's weight (server containers, slow compiles) and still not getting the
  in-browser preview or clean collaboration story.
- **Recommendation:** build the document-management + revision + brand-template
  layers as a bespoke app (that's your differentiator and where AppSheet is
  today), and embed Typst compilation (`typst.ts` client + server crate). Decide
  separately whether to build real-time collab in-house (Yjs) or lean on
  `typst.app` for the authoring surface early on.

## Suggested phasing

1. **Port the library to Typst** and publish as a versioned package. *(This
   spike proves feasibility.)*
2. **Server compile service + fonts provisioned once.** Immediately removes the
   biggest operational pain (font installs) even before any UI.
3. **Web editor + live preview + document DB** replacing AppSheet: authoring,
   revisions, status, search. Single-user-at-a-time editing is fine here.
4. **Real-time collaboration + comments** (Yjs CRDT, source-range-anchored
   threads, preview↔source mapping). The largest build; do it last.

## Principal risks

- **Real-time collab** is a real engineering project (CRDT infra, presence,
  comment anchoring). Mitigate by shipping phases 1–3 first — they're valuable
  standalone and de-risk the rest.
- **Preview↔source comment mapping** relies on Typst introspection; prototype it
  early to confirm the ergonomics.
- **FA Pro font licensing** in a hosted/multi-tenant context — check the license
  permits server-side embedding for your user base.
- **Access control / multi-tenancy** — net-new vs the current file-based model;
  standard web-app work, but real.
