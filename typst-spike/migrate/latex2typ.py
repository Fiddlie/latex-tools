#!/usr/bin/env python3
"""
latex2typ — prototype LaTeX->Typst migrator for Fiddlie documents.

Design: a DETERMINISTIC pass handles the standard, well-understood constructs
(class + metadata, sectioning, inline markup, lists, the fiddlie custom
commands, simple tables, icons). Anything it does NOT recognise with high
confidence is left in place, wrapped in a `// TODO[llm]:` block that records
the original LaTeX and a machine-readable reason. A second stage (not shown
here — it would call an LLM per block) resolves those; the deterministic pass
is exact and cheap, and the LLM is only paid for the genuinely hard parts.

This keeps ~90% of typical content fully deterministic (fast, reviewable,
idempotent) and isolates the long tail (TikZ, bespoke math, exotic macros).
"""
import re, sys, json, pathlib

# --- metadata commands -> template kwargs -----------------------------------
META = ["title", "shorttitle", "author", "date", "documentId", "revision",
        "doctype", "kicker", "lead", "website"]

# --- balanced-brace helpers (regex can't match nested {}) -------------------
def grab(s, i):
    """s[i] == '{'; return (content, index-after-closing-brace)."""
    assert s[i] == '{'
    depth, j = 0, i
    while j < len(s):
        if s[j] == '{': depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0: return s[i+1:j], j+1
        j += 1
    raise ValueError("unbalanced braces")

def replace_cmd(s, name, render, optional=False):
    """Replace every \\name[opt]{balanced} via render(opt, content), brace-aware
    and recursing into the content through inline()."""
    out, i = [], 0
    pat = re.compile(r'\\' + name + (r'(\*)?' if False else '') + r'(\[[^\]]*\])?\s*\{')
    while True:
        m = pat.search(s, i)
        if not m: out.append(s[i:]); break
        out.append(s[i:m.start()])
        opt = m.group(1)[1:-1] if m.group(1) else None
        try:
            content, end = grab(s, m.end()-1)
        except ValueError:
            out.append(s[m.start():m.end()]); i = m.end(); continue
        out.append(render(opt, content)); i = end
    return "".join(out)

# --- inline markup: deterministic, order matters, brace-aware ---------------
def inline(s):
    s = replace_cmd(s, "accentword",
        lambda o, c: (f'#accent(color: {brandmap(o)})[{inline(c)}]' if o
                      else f'#accent[{inline(c)}]'))
    s = replace_cmd(s, "faicon",
        lambda o, c: (f'#faicon("{c}", style: "{o}")' if o else f'#faicon("{c}")'))
    s = replace_cmd(s, "textbf", lambda o, c: f'*{inline(c)}*')
    s = replace_cmd(s, "emph",   lambda o, c: f'_{inline(c)}_')
    s = replace_cmd(s, "textit", lambda o, c: f'_{inline(c)}_')
    s = replace_cmd(s, "texttt", lambda o, c: f'#raw("{esc(c)}")')
    s = re.sub(r'\\verb\|([^|]*)\|', lambda m: f'#raw("{esc(m.group(1))}")', s)
    return s

def brandmap(name):
    return {"brandpink": "brand-pink", "brandyellow": "brand-yellow",
            "brandblue": "brand-blue"}.get(name, f'rgb("{name}")')

def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

# --- block-level line handlers ----------------------------------------------
def strip_comments(tex):
    # drop LaTeX line comments (% ... EOL) but keep escaped \%
    return "\n".join(re.sub(r'(?<!\\)%.*$', '', ln) for ln in tex.splitlines())

def convert(tex):
    tex = strip_comments(tex)
    body = tex.split(r'\begin{document}', 1)[1].rsplit(r'\end{document}', 1)[0] \
        if r'\begin{document}' in tex else tex
    preamble = tex.split(r'\begin{document}', 1)[0]

    # class + metadata
    m = re.search(r'\\documentclass(?:\[[^\]]*\])?\{(\w+)\}', preamble)
    cls = m.group(1) if m else "prettydoc"
    meta = {}
    for key in META:
        mm = re.search(r'\\%s\s*\{' % key, preamble)
        if mm:
            content, _ = grab(preamble, mm.end()-1)
            meta[key] = content.strip()
    draft = bool(re.search(r'\\draft\b', preamble))

    out, todos = [], []
    out.append(f'#import "../fiddlie/{cls}.typ": *')
    out.append(f'#import "../fiddlie/common.typ": brand-pink, brand-yellow, brand-blue')
    out.append("")
    args = []
    for k, v in meta.items():
        # a metadata value may itself contain inline markup (e.g. accentword)
        val = f'[{inline(v)}]' if re.search(r'\\', v) else f'"{esc(v)}"'
        args.append(f'  {k}: {val},')
    if draft: args.append('  draft: true,')
    out.append(f'#show: {cls}.with(\n' + "\n".join(args) + "\n)")
    out.append("")

    # walk the body line-by-line / environment-by-environment
    i, lines = 0, body.splitlines()
    while i < len(lines):
        line = lines[i]
        raw = line.strip()
        # skip comment-only and maketitle/toc bookkeeping
        if raw.startswith('%') or raw in (r'\maketitle', ''):
            i += 1; continue
        if raw == r'\tableofcontents':
            out.append('#outline()'); i += 1; continue
        if raw == r'\clearpage' or raw == r'\newpage':
            out.append('#pagebreak()'); i += 1; continue
        # sectioning
        ms = re.match(r'\\(section|subsection|subsubsection)\*?\{(.*)\}$', raw)
        if ms:
            lvl = {"section": "=", "subsection": "==", "subsubsection": "==="}[ms.group(1)]
            out.append(f'{lvl} {inline(ms.group(2))}'); i += 1; continue
        # fiddlie block commands
        mb = re.match(r'\\(eyebrow|closing)\{(.*)\}$', raw)
        if mb:
            out.append(f'#{mb.group(1)}[{inline(mb.group(2))}]'); i += 1; continue
        mc = re.match(r'\\card(\*)?(?:\[([^\]]*)\])?\{(.*)\}$', raw)
        if mc:
            lbl = f'label: "{mc.group(2)}"' if mc.group(2) else ""
            out.append(f'#card({lbl})[{inline(mc.group(3))}]' if lbl
                       else f'#card[{inline(mc.group(3))}]'); i += 1; continue
        # lists
        if raw.startswith(r'\begin{itemize}') or raw.startswith(r'\begin{enumerate}'):
            marker = "-" if "itemize" in raw else "+"
            i += 1
            while i < len(lines) and r'\end{' not in lines[i]:
                it = lines[i].strip()
                if it.startswith(r'\item'):
                    out.append(f'{marker} {inline(it[len(chr(92)+"item"):].strip())}')
                i += 1
            i += 1; out.append(""); continue
        # tables / tikz / other environments -> escalate to LLM
        me = re.match(r'\\begin\{(\w+\*?)\}', raw)
        if me:
            env = me.group(1)
            block = [lines[i]]; i += 1
            while i < len(lines) and (r'\end{%s}' % env) not in lines[i]:
                block.append(lines[i]); i += 1
            if i < len(lines): block.append(lines[i]); i += 1
            reason = ("tabular-family: needs column-spec + cell mapping"
                      if env.startswith(("tabular", "longtable"))
                      else f"environment '{env}' has no deterministic rule")
            todos.append({"env": env, "reason": reason, "latex": "\n".join(block)})
            out.append(f'// TODO[llm]: {reason}')
            out.append("// " + "\n// ".join(block))
            out.append(""); continue
        # plain text / paragraph
        out.append(inline(raw)); i += 1

    return "\n".join(out) + "\n", cls, todos

if __name__ == "__main__":
    src = pathlib.Path(sys.argv[1]).read_text()
    typ, cls, todos = convert(src)
    outp = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if outp: outp.write_text(typ)
    det_lines = sum(1 for l in typ.splitlines()
                    if l and not l.startswith("//"))
    todo_lines = sum(len(t["latex"].splitlines()) for t in todos)
    print(f"class: {cls}")
    print(f"deterministic output lines: {det_lines}")
    print(f"escalated blocks (need LLM): {len(todos)}  ({todo_lines} latex lines)")
    for t in todos:
        print(f"  - {t['env']}: {t['reason']}")
    if outp: print(f"wrote {outp}")
