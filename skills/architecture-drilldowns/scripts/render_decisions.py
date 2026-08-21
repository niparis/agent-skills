#!/usr/bin/env python3
"""Render canonical decision records (Markdown) as site-local HTML pages.

Why this exists: the architecture pages are read straight off disk over
`file://`, and a browser handed a `.md` link downloads it or shows raw source
rather than rendering it. So a card cannot usefully link a decision unless the
decision has an HTML face. The Markdown stays the editable source of truth; the
pages under `decisions/pages/` are build output and are never hand-edited.

Output is deterministic — no timestamps, no ordering that depends on the
filesystem — which is what lets `check_docs.py` re-render and compare
byte-for-byte to prove a page is not stale. That check is the whole reason to
generate rather than hand-write.

Usage:
    render_decisions.py <docs-dir>        # writes <docs-dir>/decisions/pages/
    render_decisions.py <docs-dir> --check   # exit 1 if any page is stale
    render_decisions.py <docs-dir> --decisions ../decisions   # records kept elsewhere
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

PAGES_DIR = "pages"
MANIFEST_NAMES = ("architecture.json", "architecture.yaml", "architecture.yml")

#: `Accepted` / `Superseded by 007` / `Proposed` — the word decides the badge.
STATUS_WORDS = ("accepted", "proposed", "superseded", "deprecated", "rejected")


#: Records normally sit at `<docs>/decisions/`. A project may keep its rendered
#: pages in a subdirectory of its own — `docs/architecture/html/` — while leaving
#: the Markdown records beside the prose they belong to. `--decisions` names that
#: directory, and every generated href is then computed relative to the page that
#: carries it rather than assumed to be one level down.
_DECISIONS_OVERRIDE: Path | None = None


def set_decisions_dir(path: str | Path | None) -> None:
    """Point the record directory somewhere other than `<docs>/decisions`."""
    global _DECISIONS_OVERRIDE
    _DECISIONS_OVERRIDE = Path(path).resolve() if path else None


def decisions_dir(docs: Path) -> Path:
    return _DECISIONS_OVERRIDE if _DECISIONS_OVERRIDE else docs / "decisions"


def pages_href_prefix(docs: Path) -> str:
    """Relative path from a page at the docs root to the rendered record pages.

    `decisions/pages/` when the layout is flat, `../decisions/pages/` when the
    pages live one directory deeper than the records."""
    rel = os.path.relpath(decisions_dir(docs) / PAGES_DIR, start=docs)
    return Path(rel).as_posix() + "/"


def source_files(docs: Path) -> list[Path]:
    """Canonical records, sorted so output order never depends on the filesystem."""
    return sorted(p for p in decisions_dir(docs).glob("*.md") if p.name != "README.md")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def inline(text: str) -> str:
    """Inline Markdown. Escaped first, so a stray `<` in prose cannot inject tags."""
    out = html.escape(text, quote=True)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)

    def link(m: re.Match[str]) -> str:
        label, href = m.group(1), html.unescape(m.group(2))
        scheme = re.match(r"^([a-zA-Z][\w+.-]*):", href)
        if scheme and scheme.group(1).lower() not in {"http", "https"}:
            return m.group(0)  # javascript:, data:, anything exotic — leave as text
        rel = ' rel="noopener noreferrer"' if scheme else ""
        return f'<a href="{html.escape(href, quote=True)}"{rel}>{label}</a>'

    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", out)


def render_markdown(src: str) -> str:
    """The Markdown subset a decision record actually uses: headings, paragraphs,
    lists, fenced code, tables, blockquotes. Deliberately not a full parser — a
    decision record that needs more than this is trying to be a design doc."""
    lines = src.splitlines()
    out: list[str] = []
    para: list[str] = []
    list_tag: str | None = None
    code: list[str] | None = None
    rows: list[list[str]] = []

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    def flush_table() -> None:
        if not rows:
            return
        head, *body = rows
        out.append('<div class="scroll"><table><thead><tr>')
        out.extend(f"<th>{inline(c)}</th>" for c in head)
        out.append("</tr></thead><tbody>")
        for row in body:
            out.append("<tr>")
            out.extend(f"<td>{inline(c)}</td>" for c in row)
            out.append("</tr>")
        out.append("</tbody></table></div>")
        rows.clear()

    def flush_all() -> None:
        flush_para()
        flush_list()
        flush_table()

    for line in lines:
        if line.startswith("```"):
            if code is None:
                flush_all()
                code = []
            else:
                out.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        if re.match(r"^\s*\|.*\|\s*$", line):
            flush_para()
            flush_list()
            if not re.match(r"^\s*\|[\s:|-]+\|?\s*$", line):
                rows.append([c.strip() for c in line.strip().strip("|").split("|")])
            continue
        flush_table()
        if (h := re.match(r"^(#{1,6})\s+(.+)$", line)):
            flush_para()
            flush_list()
            n, text = len(h.group(1)), h.group(2)
            out.append(f'<h{n} id="{slug(text)}">{inline(text)}</h{n}>')
            continue
        if (q := re.match(r"^>\s?(.*)$", line)):
            flush_para()
            flush_list()
            out.append(f"<blockquote>{inline(q.group(1))}</blockquote>")
            continue
        if (it := re.match(r"^\s*([-*]|\d+\.)\s+(.+)$", line)):
            flush_para()
            want = "ol" if it.group(1)[0].isdigit() else "ul"
            if list_tag != want:
                flush_list()
                list_tag = want
                out.append(f"<{list_tag}>")
            out.append(f"<li>{inline(it.group(2))}</li>")
            continue
        if not line.strip():
            flush_para()
            flush_list()
            continue
        # Lazy continuation: a wrapped list item. Without this, the second line of
        # a two-line bullet closes nothing and gets flushed as a <p> *inside* the
        # <ul>, which renders as a stray paragraph hanging under the bullet.
        if list_tag is not None and not para:
            out[-1] = out[-1].removesuffix("</li>") + " " + inline(line.strip()) + "</li>"
            continue
        para.append(line.strip())

    if code is not None:  # unterminated fence: keep the content rather than drop it
        out.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
    flush_all()
    return "\n".join(out)


def rebase_links(src: str, source: Path, out_dir: Path) -> str:
    """Rewrite relative links for a page that lives one directory deeper.

    A record links its siblings (`003-chunking.md`) and the pages it justifies
    (`../stage-08-questions.html`). Both are written relative to the record, and
    the rendered page sits in `decisions/pages/`, so both need re-basing — and a
    link to another record must land on that record's rendered page, not on its
    Markdown."""
    def rewrite(m: re.Match[str]) -> str:
        label, href = m.groups()
        if re.match(r"^[a-zA-Z][\w+.-]*:", href) or href.startswith(("#", "/")):
            return m.group(0)
        path_part, sep, frag = href.partition("#")
        target = (source.parent / path_part).resolve()
        if target.suffix.lower() == ".md" and target.parent == source.parent:
            target = out_dir / f"{target.stem}.html"
        rel = Path(os.path.relpath(target, start=out_dir)).as_posix()
        return f"[{label}]({rel}{'#' + frag if sep else ''})"

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", rewrite, src)


def read_status(src: str) -> str:
    """The word under `## Status`. Drives the badge, and lets the checker refuse
    to let a card cite a superseded decision as if it were live."""
    m = re.search(r"^##\s+Status\s*$(.*?)(?=^##\s|\Z)", src, re.M | re.S)
    body = (m.group(1) if m else "").strip().lower()
    return next((w for w in STATUS_WORDS if w in body), "unknown")


def render_page(source: Path, out_dir: Path, back: tuple[str, str],
                css: str = "../../_pages.css") -> str:
    """One rendered page. Pure function of its inputs — the staleness check
    depends on that, so never put anything varying (a date, a version) in here."""
    src = source.read_text(encoding="utf-8")
    first = src.splitlines()[0] if src.splitlines() else source.stem
    title = first.removeprefix("# ").strip()
    status = read_status(src)
    body = render_markdown(rebase_links(src, source, out_dir))
    back_href, back_label = back
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{html.escape(css, quote=True)}">
</head>
<body>
<div class="wrap">
<div class="crumb"><a href="{html.escape(back_href, quote=True)}">\
{html.escape(back_label)}</a> <span>/</span> <span>decision</span></div>
<span class="tag t-adr adr-{status}">◇ {status}</span>
<div class="decision">
{body}
</div>
<footer><a href="{html.escape(back_href, quote=True)}">← \
{html.escape(back_label)}</a></footer>
</div>
</body>
</html>
"""


def back_link(docs: Path) -> tuple[str, str]:
    """Where a decision page points home. Read from the manifest so the label and
    target are declared once.

    The index wins when there is one. A record is cited from several pages — a
    stage card, a component card, the context page — so there is no single page
    it came from, and sending a reader back to whichever map happened to be
    listed first is a guess that is usually wrong. The index is the one place
    every page is reachable from."""
    for name in MANIFEST_NAMES:
        if (docs / name).is_file() and name.endswith(".json"):
            m = json.loads((docs / name).read_text(encoding="utf-8"))
            if (page := m.get("index")):
                return _rel_to_pages(docs, page), "Architecture index"
            if (page := m.get("map")) or (page := m.get("system")):
                return _rel_to_pages(docs, page), m.get("title") or "architecture"
    return _rel_to_pages(docs, "index.html"), "Architecture index"


def _rel_to_pages(docs: Path, page: str) -> str:
    """Where a rendered record page points home. Computed rather than assumed to
    be two levels up, because the pages need not sit under the docs root."""
    rel = os.path.relpath(docs / page, start=decisions_dir(docs) / PAGES_DIR)
    return Path(rel).as_posix()


def render_all(docs: Path) -> dict[Path, str]:
    """{output path: expected content} for every canonical record."""
    out_dir = decisions_dir(docs) / PAGES_DIR
    back = back_link(docs)
    css = _rel_to_pages(docs, "_pages.css")
    return {out_dir / f"{s.stem}.html": render_page(s, out_dir, back, css)
            for s in source_files(docs)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docs_dir")
    ap.add_argument("--check", action="store_true",
                    help="report stale or orphaned pages instead of writing")
    ap.add_argument("--decisions", metavar="DIR",
                    help="record directory, when it is not <docs-dir>/decisions")
    args = ap.parse_args()

    set_decisions_dir(args.decisions)
    docs = Path(args.docs_dir)
    if not decisions_dir(docs).is_dir():
        print(f"no decisions/ under {docs} — nothing to render")
        return 0

    expected = render_all(docs)
    out_dir = decisions_dir(docs) / PAGES_DIR
    if args.check:
        problems = [f"missing {p.name}" for p in expected if not p.is_file()]
        problems += [f"stale {p.name}" for p, want in expected.items()
                     if p.is_file() and p.read_text(encoding="utf-8") != want]
        problems += [f"orphan {p.name}" for p in sorted(out_dir.glob("*.html"))
                     if p not in expected]
        for problem in problems:
            print(f"  {problem}")
        print(f"{len(expected)} record(s), {len(problems)} problem(s)")
        return 1 if problems else 0

    out_dir.mkdir(parents=True, exist_ok=True)
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
    for stale in sorted(out_dir.glob("*.html")):
        if stale not in expected:
            stale.unlink()  # a renamed record must not leave its old page behind
    print(f"rendered {len(expected)} decision page(s) into {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
