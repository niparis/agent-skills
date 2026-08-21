#!/usr/bin/env python3
"""Render each card's mid-level block into the map, from the manifest.

Stage cards on the pipeline map and component cards on the component map both
carry the same three declared fields — `not`, `invariants`, `adr` — so both are
rendered by the same code from the same sentinels. The only difference is which
list of the manifest a page is spliced from.

Why generated rather than hand-written: a stage's boundary exclusions, invariants
and decision citations are declared in `architecture.json`, because that is what
makes them checkable. A reader needs to see them on the map. Writing them in both
places would be exactly the duplication this skill forbids — so the map's
`<details class="more">` block is generated from the manifest and marked with
sentinels, and `check_docs.py` re-renders it to prove it is current.

The rest of the card — goal line, command, note, chips — stays hand-written. Only
the region between the sentinels is owned by this script:

    <!-- MID:BEGIN 4 -->  ... generated ...  <!-- MID:END 4 -->

A card with no sentinels is left alone, so adding the block to a map is opt-in per
stage. A stage with a drill-down is skipped: the page carries all of this in more
depth, and the skill's rule is not to write both.

Usage:
    render_cards.py <docs-dir>            # write the blocks
    render_cards.py <docs-dir> --check    # exit 1 if any block is stale
    render_cards.py <docs-dir> --decisions ../decisions   # records kept elsewhere
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_decisions as _rd  # decisions_dir / pages_href_prefix live there

MANIFEST_NAMES = ("architecture.json", "architecture.yaml", "architecture.yml")

BEGIN = "<!-- MID:BEGIN {id} -->"
END = "<!-- MID:END {id} -->"

#: A stage with a drill-down gets no mid-level block, so without this its decision
#: citations would be declared in the manifest and visible nowhere — the citations
#: that matter most, since a stage deep enough to earn a page is a stage whose
#: decisions a reader most needs. Placed on the drill-down itself.
DEC_BEGIN = "<!-- DEC:BEGIN {id} -->"
DEC_END = "<!-- DEC:END {id} -->"

#: The whole-set index on the map. Generated, because a hand-written index silently
#: goes stale the first time a record is added — which is exactly what happened.
IDX_BEGIN = "<!-- DECINDEX:BEGIN -->"
IDX_END = "<!-- DECINDEX:END -->"


def load_manifest(docs: Path) -> tuple[dict, Path]:
    for name in MANIFEST_NAMES:
        if (docs / name).is_file():
            if name.endswith(".json"):
                return json.loads((docs / name).read_text(encoding="utf-8")), docs / name
            import yaml
            return yaml.safe_load((docs / name).read_text(encoding="utf-8")), docs / name
    raise SystemExit(f"no manifest in {docs}")


def decision_title(docs: Path, record: str) -> tuple[str, str] | None:
    """(href, label) for a cited record, read from the record's own first line so
    the chip label cannot drift from the record's title."""
    dec_dir = _rd.decisions_dir(docs)
    if not dec_dir.is_dir():
        return None
    for source in sorted(dec_dir.glob("*.md")):
        if source.name == "README.md" or not source.stem.startswith(record):
            continue
        first = source.read_text(encoding="utf-8").splitlines()[0]
        title = first.removeprefix("# ").strip()
        # "003: Book identity is decided once" -> the part after the number
        label = title.split(":", 1)[1].strip() if ":" in title else title
        return (f"{_rd.pages_href_prefix(docs)}{source.stem}.html",
                f"{record} — {label}")
    return None


#: A `not` entry is written as a full sentence in the manifest — "does not start
#: workflows" — because it has to read as a claim on its own there. Under the
#: rendered "Does not:" heading that becomes "Does not: does not start workflows",
#: so the lead-in is stripped here. Both conventions then render correctly and a
#: manifest does not have to choose one.
NOT_PREFIX_RE = re.compile(r"^(?:does not|do not|doesn't|don't)\s+", re.I)


def inline_code(escaped: str) -> str:
    """Promote `backticks` to <code>. A named function rather than an inline
    re.sub because the replacement needs a single-backslash backreference, and
    writing it inside an f-string silently doubles it into a literal `\\1`."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def render_block(stage: dict, docs: Path, indent: str = "    ") -> str:
    """The generated region for one stage or component — both declare the same
    three fields. Deterministic: the staleness check compares this against what is
    on disk, so nothing here may vary run to run."""
    i, i2, i3 = indent, indent + "  ", indent + "    "
    out: list[str] = [f'{i}<details class="more">',
                      f"{i2}<summary>Boundary, invariants and decisions</summary>"]

    if (nots := stage.get("not")):
        trimmed = [inline_code(html.escape(NOT_PREFIX_RE.sub("", n))) for n in nots]
        if len(trimmed) == 1:
            out.append(f'{i2}<p class="note"><strong>Does not:</strong> {trimmed[0]}</p>')
        else:
            out.append(f'{i2}<p class="note"><strong>Does not:</strong></p>')
            out.append(f'{i2}<ul class="note">')
            out += [f"{i3}<li>{n}</li>" for n in trimmed]
            out.append(f"{i2}</ul>")

    if (invs := stage.get("invariants")):
        out.append(f'{i2}<div class="inv">')
        out.append(f"{i3}<h4>invariants</h4>")
        out.append(f"{i3}<ul>")
        out += [f"{i3}  <li>{inline_code(html.escape(v))}</li>" for v in invs]
        out.append(f"{i3}</ul>")
        out.append(f"{i2}</div>")

    chips = [c for record in stage.get("adr", [])
             if (c := decision_title(docs, record)) is not None]
    if chips:
        out.append(f'{i2}<div class="decs">')
        # A record title may carry inline code — `unassigned` is a reserved value.
        # Escape first, then promote the backticks, so the label reads as it does
        # in the record rather than showing raw backticks.
        out += [f'{i3}<a class="dec" href="{html.escape(h, quote=True)}">◇ '
                f"{inline_code(html.escape(label))}</a>"
                for h, label in chips]
        out.append(f"{i2}</div>")

    out.append(f"{i}</details>")
    return "\n".join(out)


def chip_html(href: str, label: str, indent: str, status: str = "") -> str:
    """One decision chip. A status other than `accepted` is shown on the chip.

    The index is the whole set, superseded records included — they are never
    deleted, because the question a superseded record answers recurs precisely
    when someone is about to make it again. But an index that lists them
    identically to live ones presents overturned reasoning as current, which is
    the failure the skill's own anti-pattern table names."""
    cls = "dec" if status in ("", "accepted") else f"dec adr-{status}"
    mark = "" if status in ("", "accepted") else f' <span class="why">{status}</span>'
    return (f'{indent}<a class="{cls}" href="{html.escape(href, quote=True)}">◇ '
            f"{inline_code(html.escape(label))}{mark}</a>")


def render_index(docs: Path, indent: str) -> str:
    """Every record, cited or not. The index is the whole set by definition, so it
    is globbed from the directory rather than from the manifest's citations."""
    dec_dir = _rd.decisions_dir(docs)
    prefix = _rd.pages_href_prefix(docs)
    lines = [f'{indent}<div class="decs">']
    for source in sorted(p for p in dec_dir.glob("*.md") if p.name != "README.md"):
        text = source.read_text(encoding="utf-8")
        title = text.splitlines()[0].removeprefix("# ").strip()
        num, _, rest = title.partition(":")
        label = f"{num.strip()} — {rest.strip()}" if rest else title
        lines.append(chip_html(f"{prefix}{source.stem}.html", label, indent + "  ",
                               _rd.read_status(text)))
    lines.append(f"{indent}</div>")
    return "\n".join(lines)


def render_stage_decs(stage: dict, docs: Path, indent: str) -> str:
    """The decision chips for one stage, for a drill-down page. Paths are relative
    to the drill-down, which sits beside the map, so they match the map's."""
    lines = [f'{indent}<div class="decs">']
    for record in stage.get("adr", []):
        if (found := decision_title(docs, record)) is not None:
            lines.append(chip_html(found[0], found[1], indent + "  "))
    lines.append(f"{indent}</div>")
    return "\n".join(lines)


def _splice(text: str, begin: str, end: str, make, label: str) -> str:
    """Replace the region between two sentinels, preserving their indentation."""
    if begin not in text:
        return text
    start, stop = text.index(begin), text.index(end)
    if stop < start:
        raise SystemExit(f"{label}: END appears before BEGIN")
    line_start = text.rfind("\n", 0, start) + 1
    indent = text[line_start:start]
    return text[:start] + begin + "\n" + make(indent) + "\n" + indent + text[stop:]


def expected_pages(docs: Path) -> dict[Path, str]:
    """{page: expected text} for every page carrying a generated region."""
    manifest, _ = load_manifest(docs)
    out: dict[Path, str] = {}

    map_name = manifest.get("map")
    if map_name and (docs / map_name).is_file():
        page = docs / map_name
        text = page.read_text(encoding="utf-8")
        for stage in manifest.get("stages", []):
            sid = str(stage["id"])
            if BEGIN.format(id=sid) in text and stage.get("drilldown"):
                raise SystemExit(
                    f"stage {sid} has both a drill-down and a MID block — the skill's "
                    f"rule is not to write both. Remove the sentinels from the card.")
            text = _splice(text, BEGIN.format(id=sid), END.format(id=sid),
                           lambda ind, s=stage: render_block(s, docs, ind), f"stage {sid}")
        text = _splice(text, IDX_BEGIN, IDX_END,
                       lambda ind: render_index(docs, ind), "decision index")
        if text != page.read_text(encoding="utf-8") or "MID:BEGIN" in text:
            out[page] = text

    # The component map, spliced from `components` rather than `stages`. Ids may
    # collide across the two lists — component 4 and stage 4 are different things —
    # which is harmless because each page is spliced from one list only.
    comp_name = manifest.get("component_map")
    if comp_name and (docs / comp_name).is_file():
        page = docs / comp_name
        original = page.read_text(encoding="utf-8")
        text = original
        for comp in manifest.get("components", []):
            cid = str(comp["id"])
            text = _splice(text, BEGIN.format(id=cid), END.format(id=cid),
                           lambda ind, c=comp: render_block(c, docs, ind),
                           f"component {cid}")
        text = _splice(text, IDX_BEGIN, IDX_END,
                       lambda ind: render_index(docs, ind), "decision index")
        if text != original or "MID:BEGIN" in text:
            out[page] = text

    # The index and the context page carry no cards, but either may hold the
    # decision index — and a hand-written one goes stale the first time a record
    # is added, which is the whole reason this region is generated.
    for key in ("index", "system"):
        name = manifest.get(key)
        if not name or not (docs / name).is_file():
            continue
        page = docs / name
        original = page.read_text(encoding="utf-8")
        if IDX_BEGIN not in original:
            continue
        out[page] = _splice(original, IDX_BEGIN, IDX_END,
                            lambda ind: render_index(docs, ind), f"{key} decision index")

    # Drill-downs: the cited-decisions block for the stage the page documents.
    for stage in manifest.get("stages", []):
        dd = stage.get("drilldown")
        if not dd or not (docs / dd).is_file():
            continue
        page = docs / dd
        text = page.read_text(encoding="utf-8")
        sid = str(stage["id"])
        new = _splice(text, DEC_BEGIN.format(id=sid), DEC_END.format(id=sid),
                      lambda ind, s=stage: render_stage_decs(s, docs, ind), dd)
        if DEC_BEGIN.format(id=sid) in text:
            out[page] = new
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docs_dir")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--decisions", metavar="DIR",
                    help="record directory, when it is not <docs-dir>/decisions")
    args = ap.parse_args()

    _rd.set_decisions_dir(args.decisions)
    docs = Path(args.docs_dir)
    pages = expected_pages(docs)
    if not pages:
        print("no generated regions found — nothing to render")
        return 0

    stale = [p for p, want in pages.items() if p.read_text(encoding="utf-8") != want]
    if args.check:
        for p in stale:
            print(f"  {p.name}: generated regions are stale — run render_cards.py")
        print(f"{len(pages)} page(s) with generated regions, {len(stale)} stale")
        return 1 if stale else 0

    for p, want in pages.items():
        p.write_text(want, encoding="utf-8")
    total = sum(len(re.findall(r"(?:MID|DEC|DECINDEX):BEGIN", w)) for w in pages.values())
    print(f"rendered {total} generated region(s) across {len(pages)} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
