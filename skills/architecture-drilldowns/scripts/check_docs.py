#!/usr/bin/env python3
"""Validate architecture doc pages before publishing them.

Two families of check. The first four are per-page and always run — they catch
what rots inside the documentation itself:

  refs    Every `file · symbol` chip names a symbol that is actually defined in
          that file. This is why the convention is symbols and not line numbers:
          a moved line fails nothing, a renamed symbol fails here.
  html    Tags are balanced. A dropped </div> in a hand-written page shifts
          every card after it and is invisible until someone opens the file.
  links   Every relative href resolves to a file that exists, so a map cannot
          point at a drill-down that was never written.
  goals   Every stage card leads with a `.goal` line. Warns, because the check
          can see that a purpose sentence is absent but not that a present one
          is any good — mechanism-first prose is the failure mode this skill
          fights hardest, and it is invisible to a reader who already knows the
          system.

The rest need an `architecture.json` (or `.yaml`) beside the pages, and are the
only checks that can see drift *between* the docs and the system. Without a
manifest they are skipped and the run says so:

  stages     The code's stage list, read out of the enum or constant the
             manifest points at, matches the manifest's stages in order. Catches
             a renamed, reordered, added or deleted stage — which the skill's
             own audit notes is the most common drift and which nothing else
             here can see.
  map        Every manifest stage has a card on the map, numbered the same, in
             the same order, and each declared drill-down is linked from it.
  components Same, for the component map: every declared component has a card,
             numbered and ordered the same, and every channel's endpoints
             resolve to a component or an external. A component may present an
             external rather than name its own — declared once, as an external.
  index      Every page the manifest names is linked from the index page, and
             every one of them links back to it. An index that misses a page is
             worse than no index — it reads as complete — and navigation that
             only runs downhill strands whoever arrived from a search result.
  artifacts  Every file actually present in the data directory is claimed by
             some card's `writes` chips. Warns: this is how a new sidecar that
             no doc has heard of surfaces.
  contracts  A real sample of each declared artifact still has the keys the
             contract says it has. Errors on a missing required key, warns on a
             key the contract never declared.
  coverage   Which stages have no drill-down yet. Informational.

Reads and writes are deliberately NOT in the manifest — they are parsed out of
the map's own `.io` chips. Declaring them twice would create exactly the kind of
duplication that diverges.

Usage:
    check_docs.py <docs-dir-or-page.html> [more.html ...] [--source-root DIR]

--source-root defaults to the current directory. A ref written as a bare
basename (`questions.py`) is searched for beneath it; a ref with a path
(`tools/library.py`) is resolved relative to it. Exits non-zero if any check
fails, so it can gate a commit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# This script imports render_decisions to re-render and compare. Without this,
# that import drops a __pycache__ into the skill's own scripts directory, which
# then shows up as untracked cruft in whatever repo the skill was copied into.
sys.dont_write_bytecode = True

from html import unescape  # noqa: E402
from html.parser import HTMLParser  # noqa: E402
from pathlib import Path  # noqa: E402

VOID_TAGS = {"meta", "br", "img", "link", "hr", "input", "source", "col", "area", "base", "wbr"}

REF_RE = re.compile(r'class="ref">([^<]+)</span>')
HREF_RE = re.compile(r'href="([^"]+)"')
ANCHOR_RE = re.compile(r'(?:id|name)=["\']([^"\']+)["\']')
CARD_RE = re.compile(r'<div class="card[^"]*"')
H3_RE = re.compile(r"<h3[ >]")

#: How a definition looks, per language. The fallback is a bare word-boundary
#: search, reported as a warning rather than an error — better to under-claim
#: than to fail a page over an unparsed language.
DEF_PATTERNS = {
    ".py": [r"^\s*(?:async\s+)?def\s+{n}\s*\(", r"^\s*class\s+{n}\b",
            r"^{n}\s*(?::[^=]+)?="],
    ".js": [r"\bfunction\s+{n}\b", r"\b(?:const|let|var)\s+{n}\b", r"\bclass\s+{n}\b"],
    ".ts": [r"\bfunction\s+{n}\b", r"\b(?:const|let|var)\s+{n}\b", r"\bclass\s+{n}\b",
            r"\b(?:interface|type|enum)\s+{n}\b"],
    ".go": [r"\bfunc\s+(?:\([^)]*\)\s*)?{n}\b", r"\btype\s+{n}\b"],
    ".rb": [r"\bdef\s+{n}\b", r"\bclass\s+{n}\b", r"\bmodule\s+{n}\b"],
    ".rs": [r"\bfn\s+{n}\b", r"\b(?:struct|enum|trait|impl)\s+{n}\b"],
    ".java": [r"\bclass\s+{n}\b", r"\b\w+\s+{n}\s*\("],
}
DEF_PATTERNS[".jsx"] = DEF_PATTERNS[".js"]
DEF_PATTERNS[".tsx"] = DEF_PATTERNS[".ts"]
DEF_PATTERNS[".mjs"] = DEF_PATTERNS[".js"]


class Balance(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, int]] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag not in VOID_TAGS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: stray </{tag}>")
            return
        open_tag, open_line = self.stack[-1]
        if open_tag != tag:
            self.errors.append(
                f"line {self.getpos()[0]}: </{tag}> closes <{open_tag}> opened on line {open_line}")
        else:
            self.stack.pop()


def find_source(spec: str, root: Path) -> Path | None:
    """Resolve a ref's file part. A path is taken literally under `root`; a bare
    basename is searched for, preferring the shallowest match so a vendored copy
    in a deep directory does not win over the real one."""
    direct = root / spec
    if direct.is_file():
        return direct
    if "/" in spec:
        return None
    matches = [p for p in root.rglob(spec)
               if p.is_file()
               and not any(part in {".git", "node_modules", ".venv", "__pycache__",
                                    "dist", "build", ".worktrees"} for part in p.parts)]
    if not matches:
        return None
    return min(matches, key=lambda p: len(p.parts))


def symbol_defined(src: Path, symbol: str) -> bool | None:
    """True/False when the language is known, None when it is not (caller warns)."""
    patterns = DEF_PATTERNS.get(src.suffix)
    try:
        text = src.read_text(errors="replace")
    except OSError:
        return False
    if patterns is None:
        return None if re.search(rf"\b{re.escape(symbol)}\b", text) else False
    return any(re.search(p.format(n=re.escape(symbol)), text, re.M) for p in patterns)


def check_goals(text: str) -> list[str]:
    """Stage cards on a MAP that do not lead with a purpose line.

    A "stage card" is a `.card` carrying a `.cmd` — a card documenting a command
    a reader can run. Prose cards without one (a vocabulary block, a closing
    "what this does not do") are exempt.

    Drill-downs are skipped wholesale, keyed on the `.crumb` every one of them
    carries: their purpose statement is the framing paragraph under the `<h1>`,
    which no selector distinguishes from any other `.sub`. Checking them by card
    would only fire on call-chain steps that use `.cmd` to show a code fragment
    rather than a command — the check would be wrong, and a wrong warning gets
    ignored, taking the right ones with it.

    Cards do not nest in this grammar, so slicing from one card open to the next
    is enough and avoids needing a real parser. Reported as warnings: a missing
    goal line is certain, but nothing here can tell a real purpose sentence from
    mechanism dressed up as one — that judgement stays human."""
    problems: list[str] = []
    if 'class="crumb"' in text:
        return problems
    opens = [m.start() for m in CARD_RE.finditer(text)]
    for i, start in enumerate(opens):
        chunk = text[start:opens[i + 1] if i + 1 < len(opens) else len(text)]
        if 'class="cmd"' not in chunk:
            continue
        name = "(unnamed card)"
        if (h3 := H3_RE.search(chunk)):
            name = " ".join(re.sub(r"<[^>]+>", " ", chunk[h3.start():h3.start() + 220])
                            .split())[:48]
        if 'class="goal"' not in chunk:
            problems.append(f"card {name!r} has no .goal line — a card must open with "
                            f"what the stage is FOR, before how it works")
        elif chunk.index('class="goal"') > chunk.index('class="cmd"'):
            problems.append(f"card {name!r} has its .goal below the .cmd — purpose reads first")
    return problems


MANIFEST_NAMES = ("architecture.json", "architecture.yaml", "architecture.yml")

NUM_RE = re.compile(r'<div class="num">([^<]*)</div>')
CHIP_RE = re.compile(r'class="chip[^"]*">(.*?)</span>\s*(?:</span>)?', re.S)
#: `writes` is the older two-verb grammar, kept working so an existing map does
#: not have to be rewritten to gain the manifest checks. New pages split it into
#: `persists` (durable) and `emits` (a handoff that never lands on disk) — only
#: the durable half is expected to show up in the data directory.
IO_SECTION_RE = re.compile(r"<h4>(reads|writes|persists|emits)</h4>(.*?)(?=<h4>|\Z)", re.S)
DURABLE = ("writes", "persists")
ENUM_MEMBER_RE = re.compile(r'^\s+[A-Za-z_]\w*\s*[:=]\s*["\']([^"\']+)["\']', re.M)


def load_manifest(path: Path) -> dict:
    """JSON needs nothing; YAML needs PyYAML, which a skill script cannot assume.
    The manifest is data, not prose, so JSON costs little — hence JSON is the
    documented default and YAML is the convenience if the repo already has it."""
    text = path.read_text(errors="replace")
    if path.suffix == ".json":
        return json.loads(text)
    try:
        import yaml
    except ModuleNotFoundError:
        raise SystemExit(f"{path.name} needs PyYAML — install it, or use architecture.json")
    return yaml.safe_load(text)


def find_manifest(paths: list[Path]) -> Path | None:
    for d in dict.fromkeys(p if p.is_dir() else p.parent for p in paths):
        for name in MANIFEST_NAMES:
            if (d / name).is_file():
                return d / name
    return None


def _balanced(text: str, start: int) -> str:
    """The bracketed region opening at `start`, quotes respected so a bracket
    inside a string literal cannot close the region early."""
    pairs = {"[": "]", "(": ")", "{": "}"}
    depth, quote, i = 0, "", start
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = ""
        elif c in "\"'":
            quote = c
        elif c in pairs:
            depth += 1
        elif c in pairs.values():
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    return text[start:]


def code_stage_list(spec: str, root: Path) -> tuple[list[str] | None, str]:
    """Read the authoritative stage list out of the code.

    Handles the two shapes it is ever written in: an enum class whose members
    carry string values, and a module-level list or tuple of strings. Anything
    else — most often a comprehension over the enum, `STAGES = [s.value for s in
    StageName]` — has no literals to read, so we say so and ask for the enum
    instead of guessing. Returning None means "could not tell", which the caller
    reports as a warning; a wrong stage list would be worse than no check."""
    file_part, _, sym = (p.strip() for p in spec.partition("·"))
    if not file_part or not sym:
        return None, f"stage_source {spec!r} is not 'file · symbol'"
    src = find_source(file_part, root)
    if src is None:
        return None, f"stage_source {spec!r} — no such file under {root}"
    text = src.read_text(errors="replace")

    if (m := re.search(rf"^class\s+{re.escape(sym)}\b[^\n]*:\s*$", text, re.M)):
        rest = text[m.end():]
        end = re.search(r"^\S", rest, re.M)
        names = ENUM_MEMBER_RE.findall(rest[:end.start() if end else len(rest)])
        if names:
            return names, ""
        return None, f"{sym} in {src.name} is a class but no member has a string value"

    if (m := re.search(rf"^{re.escape(sym)}\s*(?::[^=\n]+)?=\s*[\[\(]", text, re.M)):
        region = _balanced(text, text.index("[", m.start()) if "[" in m.group(0)
                           else text.index("(", m.start()))
        names = re.findall(r'["\']([^"\']+)["\']', region)
        if names:
            return names, ""
        return None, (f"{sym} in {src.name} holds no string literals — point stage_source "
                      f"at the enum it derives from instead")

    return None, f"stage_source {spec!r} — {sym!r} not found in {src}"


def map_cards(text: str) -> list[dict]:
    """The cards of a map — stages on the pipeline map, components on the component
    map — in page order, with their number, title and chips.

    Entities are unescaped: a title written `Worker &amp; review agents` is the
    string `Worker & review agents`, and comparing the raw markup against a
    manifest name would report a mismatch that does not exist."""
    cards = []
    chunks = NUM_RE.split(text)[1:]
    for num, body in zip(chunks[0::2], chunks[1::2]):
        title = ""
        if (h3 := re.search(r"<h3[^>]*>(.*?)</h3>", body, re.S)):
            title = unescape(" ".join(re.sub(r"<[^>]+>", " ", h3.group(1)).split()))
        io: dict[str, list[str]] = {"reads": [], "writes": [], "persists": [], "emits": []}
        for kind, section in IO_SECTION_RE.findall(body):
            io[kind] += [unescape(" ".join(re.sub(r"<[^>]+>", "", c).split()))
                         for c in CHIP_RE.findall(section)]
        cards.append({"num": num.strip(), "title": title, "hrefs": HREF_RE.findall(body),
                      **io})
    return cards


def component_name(comp: dict, manifest: dict) -> tuple[str, str]:
    """(display name, error) for one component.

    A component either names itself or presents an already-declared external —
    GitHub, an object store, a queue. The second form exists so a system that a
    reader thinks of as a component, and that the boundary page thinks of as an
    external, is declared exactly once: as the external, with its purpose."""
    why, title = "", None
    if (ref := comp.get("external")):
        titles = {e["id"]: e["title"] for e in manifest.get("externals", [])}
        if ref in titles:
            title = titles[ref]
        else:
            why = f"presents external {ref!r}, which is not declared in externals"
    # `name` beside `external` is a display override, for a card that says it
    # differently — one repository here, all of them on the boundary page. The
    # external reference is still resolved, so a typo in it still fails.
    if (name := comp.get("name") or title):
        return name, why
    return str(comp.get("id", "?")), why or ("declares neither a name nor an external "
                                             "it presents")


def artifact_pattern(name: str) -> str:
    """Collapse a filename to the shape a doc writes it as: basename only, no
    parenthesised annotation, section and chapter numbers as SN and NN. Lets a
    real `chapter-06.S1.partial.jsonl` match a documented
    `chapter-NN.SN.partial.jsonl` without the doc naming every chapter."""
    base = re.sub(r"\([^)]*\)", "", name.split("/")[-1]).strip()
    base = re.sub(r"\bS\d+\b", "SN", base)
    return re.sub(r"\d+", "NN", base).lower()


def _records(path: Path, kind: str) -> list[dict]:
    if kind == "jsonl":
        loaded = [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]
    else:
        raw = json.loads(path.read_text())
        loaded = raw if isinstance(raw, list) else [raw]
    return [r for r in loaded if isinstance(r, dict)]


def sample_keys(path: Path, kind: str) -> tuple[set[str], set[str], int]:
    """(all keys seen, keys present in EVERY record, record count)."""
    records = _records(path, kind)
    if not records:
        return set(), set(), 0
    seen = set().union(*(r.keys() for r in records))
    always = set(records[0]).intersection(*(r.keys() for r in records))
    return seen, always, len(records)


def sample_keyed(path: Path, kind: str, pattern: str
                 ) -> tuple[set[str], set[str], set[str], int]:
    """For an artifact whose top-level keys are DATA, not schema — a map keyed by
    section number, chapter id, tenant. Declaring those keys as `required` would
    be declaring the data.

    Returns (fixed keys present, keys in every value, keys in any value, entries).
    A key matching `pattern` is an entry; anything else is a fixed key and is
    checked against required/optional as usual."""
    entries: list[dict] = []
    fixed: set[str] = set()
    key_re = re.compile(pattern)
    for record in _records(path, kind):
        for key, value in record.items():
            if key_re.match(key):
                if isinstance(value, dict):
                    entries.append(value)
            else:
                fixed.add(key)
    if not entries:
        return fixed, set(), set(), 0
    seen = set().union(*(e.keys() for e in entries))
    always = set(entries[0]).intersection(*(e.keys() for e in entries))
    return fixed, always, seen, len(entries)


#: A model that describes something not built yet cannot be checked against code
#: or data — there is none. Saying so beats a wall of errors that all mean "not
#: implemented", which is how a checker gets switched off.
DESIGN_STATUSES = {"proposed", "draft", "design", "planned"}


def check_decisions(docs: Path, cited: dict[str, list[str]],
                    errors: list[str], warnings: list[str], notes: list[str]) -> None:
    """Decision records: cited, rendered, current, and not orphaned.

    `cited` maps a record id to the nodes citing it. Four failures matter, and
    only the first is about the docs being incomplete — the rest are about the
    docs being confidently wrong, which is worse."""
    try:
        import render_decisions as rd
    except ModuleNotFoundError:
        # The renderer sits beside this file; if it cannot be imported the
        # staleness check is the one thing we lose, so say so rather than pass.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            import render_decisions as rd
        except ModuleNotFoundError:
            warnings.append("render_decisions.py not importable — decision pages "
                            "were not checked for staleness")
            return

    dec_dir = rd.decisions_dir(docs)
    if not dec_dir.is_dir():
        if cited:
            errors.append(f"{len(cited)} decision(s) are cited but there is no "
                          f"decisions/ directory: {', '.join(sorted(cited))}")
        return

    sources = {s.stem: s for s in rd.source_files(docs)}
    for record, nodes in sorted(cited.items()):
        match = [stem for stem in sources if stem.startswith(record)]
        if not match:
            errors.append(f"decision {record!r} is cited by {', '.join(nodes)} but no "
                          f"record file starts with {record!r} in {dec_dir}")
            continue
        status = rd.read_status(sources[match[0]].read_text(encoding="utf-8"))
        if status in {"superseded", "deprecated", "rejected"}:
            errors.append(f"decision {record!r} is {status} but {', '.join(nodes)} "
                          f"still cite it as live — cite the record that replaced it")
        elif status == "unknown":
            warnings.append(f"decision {record!r} has no readable '## Status' section")

    # Byte-identical re-render. The only way a generated page cannot silently rot.
    expected = rd.render_all(docs)
    out_dir = dec_dir / rd.PAGES_DIR
    for path, want in expected.items():
        if not path.is_file():
            errors.append(f"decision page {path.name} was never rendered — "
                          f"run render_decisions.py")
        elif path.read_text(encoding="utf-8") != want:
            errors.append(f"decision page {path.name} is stale — "
                          f"run render_decisions.py")
    if out_dir.is_dir():
        for orphan in sorted(out_dir.glob("*.html")):
            if orphan not in expected:
                errors.append(f"decision page {orphan.name} has no source record — "
                              f"delete it, or restore the record it came from")
    uncited = sorted(set(sources) - {stem for r in cited
                                     for stem in sources if stem.startswith(r)})
    if uncited:
        notes.append(f"{len(uncited)} record(s) cited by no node: {', '.join(uncited)}")


def check_cards(docs: Path, errors: list[str], notes: list[str]) -> None:
    """The map's generated mid-level blocks, same re-render-and-compare as the
    decision pages. Without this the blocks are generated content nothing proves
    current, which is worse than hand-written content nobody expected to be."""
    try:
        import render_cards as rc
    except ModuleNotFoundError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            import render_cards as rc
        except ModuleNotFoundError:
            notes.append("render_cards.py not importable — mid-level blocks were not "
                         "checked for staleness")
            return
    try:
        pages = rc.expected_pages(docs)
    except SystemExit as exc:
        errors.append(f"generated regions: {exc}")
        return
    if not pages:
        return
    stale = [p.name for p, want in pages.items()
             if p.read_text(encoding="utf-8") != want]
    for name in stale:
        errors.append(f"{name}: generated regions are stale or hand-edited — "
                      f"run render_cards.py")
    if not stale:
        total = sum(len(re.findall(r"(?:MID|DEC|DECINDEX):BEGIN", w))
                    for w in pages.values())
        notes.append(f"{total} generated region(s) across {len(pages)} page(s) current")


def check_manifest(mf: Path, root: Path) -> tuple[list[str], list[str], list[str]]:
    """Returns (errors, warnings, notes)."""
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    m = load_manifest(mf)
    stages = m.get("stages") or []
    if not stages:
        return [f"{mf.name}: no stages declared"], [], []

    # A misspelled key does not fail loudly — it silently switches off whichever
    # check reads it, which is the worst possible outcome for a checker. Keys
    # starting with `//` or `_` are the file's comment convention (JSON has none)
    # and are ignored by design.
    known = {"title", "pipeline", "status", "system", "map", "index", "component_map",
             "stage_source", "views", "stages", "components", "channels", "externals",
             "edges", "data_globs", "ignore", "contracts", "configuration",
             "open_questions"}
    for key in sorted(set(m) - known):
        if not key.startswith(("//", "_")):
            warnings.append(f"{mf.name}: unknown key {key!r} — nothing reads it. "
                            f"A typo here silently disables a check")

    status = str(m.get("status", "built")).lower()
    as_designed = status in DESIGN_STATUSES
    if as_designed:
        notes.append(f"status is {status!r} — this model describes a design, so the "
                     f"code, artifact and contract checks are skipped")

    # ---- stages: the manifest against the code -------------------------------
    if as_designed:
        pass
    elif (spec := m.get("stage_source")):
        code, why = code_stage_list(spec, root)
        if code is None:
            warnings.append(f"{mf.name}: {why} — stage check skipped")
        else:
            # A stage may cover several enum members (one card for two verbs that
            # always run together) or none at all (a setup verb that is not part
            # of the run). Flattening in manifest order checks naming AND order
            # in one comparison.
            declared = [n for s in stages for n in s.get("code_names", [s["name"]])]
            if declared != code:
                errors.append(f"{mf.name}: stage list disagrees with {spec}\n"
                              f"           code: {code}\n"
                              f"           docs: {declared}")
                for extra in [n for n in code if n not in declared]:
                    errors.append(f"{mf.name}:   stage {extra!r} exists in code, "
                                  f"documented nowhere")
                for stale in [n for n in declared if n not in code]:
                    errors.append(f"{mf.name}:   stage {stale!r} is documented but "
                                  f"gone from the code")
    else:
        warnings.append(f"{mf.name}: no stage_source — the docs cannot be checked "
                        f"against the code's stage list")

    # ---- map: the manifest against the page -----------------------------------
    cards: list[dict] = []
    map_name = m.get("map")
    if map_name and (mf.parent / map_name).is_file():
        cards = map_cards((mf.parent / map_name).read_text(errors="replace"))
        by_num = {c["num"]: c for c in cards}
        for s in stages:
            sid = str(s["id"])
            card = by_num.get(sid)
            if card is None:
                errors.append(f"{map_name}: no card numbered {sid} for stage {s['name']!r}")
                continue
            if s["name"].lower() not in card["title"].lower():
                warnings.append(f"{map_name}: card {sid} is titled {card['title'][:40]!r}, "
                                f"manifest calls the stage {s['name']!r}")
            if (dd := s.get("drilldown")) and dd not in card["hrefs"]:
                errors.append(f"{map_name}: card {sid} does not link its drill-down {dd}")
        order = [c["num"] for c in cards if c["num"] in {str(s["id"]) for s in stages}]
        if order != [str(s["id"]) for s in stages]:
            errors.append(f"{map_name}: cards run {order}, manifest order is "
                          f"{[str(s['id']) for s in stages]}")
    elif map_name:
        errors.append(f"{mf.name}: map {map_name!r} does not exist")

    # ---- component map: the manifest against the structural page --------------
    # The same check as the map, on the other axis. A map card is a step in a
    # sequence; a component card is an owner of a responsibility. Both are
    # numbered rails, so the parse is shared and only the vocabulary differs.
    components = m.get("components") or []
    comp_name = m.get("component_map")
    comp_names: dict[str, str] = {}
    for c in components:
        display, why = component_name(c, m)
        comp_names[str(c["id"])] = display
        if why:
            errors.append(f"{mf.name}: component {c.get('id')!r} {why}")
    if components and not comp_name:
        errors.append(f"{mf.name}: {len(components)} component(s) declared but no "
                      f"component_map page — nothing renders them")
    if comp_name and not (mf.parent / comp_name).is_file():
        errors.append(f"{mf.name}: component_map {comp_name!r} does not exist")
    elif comp_name and not components:
        warnings.append(f"{mf.name}: component_map {comp_name!r} exists but no components "
                        f"are declared — the page is unchecked prose")
    elif comp_name:
        ccards = map_cards((mf.parent / comp_name).read_text(errors="replace"))
        by_num = {c["num"]: c for c in ccards}
        for c in components:
            cid = str(c["id"])
            card = by_num.get(cid)
            if card is None:
                errors.append(f"{comp_name}: no card numbered {cid} for component "
                              f"{comp_names[cid]!r}")
                continue
            if comp_names[cid].lower() not in card["title"].lower():
                warnings.append(f"{comp_name}: card {cid} is titled {card['title'][:40]!r}, "
                                f"manifest calls the component {comp_names[cid]!r}")
        order = [c["num"] for c in ccards if c["num"] in comp_names]
        if order != [str(c["id"]) for c in components]:
            errors.append(f"{comp_name}: cards run {order}, manifest order is "
                          f"{[str(c['id']) for c in components]}")

    # ---- views, externals and edges: the model's own integrity ----------------
    views = {v["id"] for v in m.get("views", [])}
    externals = {e["id"] for e in m.get("externals", [])}
    stage_ids = {str(s["id"]) for s in stages}
    for s in stages:
        unknown = sorted(set(s.get("views", [])) - views)
        if unknown:
            errors.append(f"{mf.name}: stage {s['name']!r} names undeclared "
                          f"view(s) {unknown}")
    for view in sorted(views - {v for s in stages for v in s.get("views", [])}):
        warnings.append(f"{mf.name}: view {view!r} is declared but no stage is in it")
    for edge in m.get("edges", []):
        for end in ("from", "to"):
            if str(edge.get(end)) not in stage_ids | externals:
                errors.append(f"{mf.name}: edge {edge.get('from')} → {edge.get('to')} "
                              f"has {end} {edge.get(end)!r}, which is neither a stage "
                              f"id nor an external id")

    # ---- channels: the component map's own edges ------------------------------
    # `carries` is required rather than optional. A channel with no payload named
    # is a line on a diagram, and a line on a diagram is the thing this whole page
    # type exists to replace.
    if m.get("channels") and not components:
        errors.append(f"{mf.name}: channels are declared but no components are — "
                      f"there is nothing for them to connect")
    for ch in m.get("channels", []):
        for end in ("from", "to"):
            if str(ch.get(end)) not in set(comp_names) | externals:
                errors.append(f"{mf.name}: channel {ch.get('from')} → {ch.get('to')} has "
                              f"{end} {ch.get(end)!r}, which is neither a component id "
                              f"nor an external id")
        if not ch.get("carries"):
            warnings.append(f"{mf.name}: channel {ch.get('from')} → {ch.get('to')} names "
                            f"nothing it carries")

    # ---- boundaries and invariants: declared, or declared absent --------------
    # A stage's PURPOSE is not checked here on purpose: it lives in the map's
    # `.goal` line, where readers see it, and check_goals already requires it.
    # Duplicating it into the manifest would give it two homes and one of them
    # would drift. What the map has no place for is the other half — the
    # responsibilities a stage explicitly does NOT take on, which is where scope
    # creep lands — and the invariants a reader should be able to check the code
    # against. Both are reported in aggregate: a per-stage line for each turns a
    # useful signal into a wall nobody reads.
    for label, key in (("boundary exclusions", "not"), ("invariants", "invariants")):
        missing = [s["name"] for s in stages
                   if not s.get(key) and not s.get(f"no_{key.strip('_')}")]
        if missing:
            notes.append(f"{len(missing)}/{len(stages)} stages declare no {label}: "
                         f"{', '.join(missing)}")
        gap = [comp_names[str(c["id"])] for c in components
               if not c.get(key) and not c.get(f"no_{key.strip('_')}")]
        if gap:
            notes.append(f"{len(gap)}/{len(components)} components declare no {label}: "
                         f"{', '.join(gap)}")
    for e in m.get("externals", []):
        if not e.get("purpose"):
            warnings.append(f"{mf.name}: external {e['id']!r} declares no purpose — "
                            f"it has no card of its own to carry one")

    # ---- decisions ------------------------------------------------------------
    cited: dict[str, list[str]] = {}
    for s in stages:
        for record in s.get("adr", []):
            cited.setdefault(record, []).append(f"stage {s['name']}")
    for e in m.get("externals", []):
        for record in e.get("adr", []):
            cited.setdefault(record, []).append(f"external {e['id']}")
    for c in components:
        for record in c.get("adr", []):
            cited.setdefault(record, []).append(f"component {comp_names[str(c['id'])]}")
    check_decisions(mf.parent, cited, errors, warnings, notes)
    check_cards(mf.parent, errors, notes)

    # ---- index: every page reachable from one place ---------------------------
    # An index that misses a page is worse than no index, because it reads as
    # complete. So a page the manifest names and the index does not link is an
    # error, and a page sitting in the directory that nothing links is a warning —
    # the second is how a drill-down written last week goes unread.
    if (idx_name := m.get("index")):
        idx = mf.parent / idx_name
        if not idx.is_file():
            errors.append(f"{mf.name}: index {idx_name!r} does not exist")
        else:
            linked = {h.split("#")[0].split("?")[0]
                      for h in HREF_RE.findall(idx.read_text(errors="replace"))}
            named = [p for p in (m.get("system"), comp_name, map_name) if p]
            named += [s["drilldown"] for s in stages if s.get("drilldown")]
            for page in dict.fromkeys(named):
                if page not in linked:
                    errors.append(f"{idx_name}: does not link {page}")
            strays = [p.name for p in sorted(mf.parent.glob("*.html"))
                      if p.name != idx_name and p.name not in linked]
            if strays:
                warnings.append(f"{idx_name}: page(s) in the directory that the index does "
                                f"not link: {', '.join(strays)}")
            # And the way back. Navigation that only runs downhill strands a
            # reader on whichever page they landed on, which is the one thing a
            # doc set opened from a search result does every time.
            for page in dict.fromkeys(named):
                target = mf.parent / page
                if not target.is_file():
                    continue
                home = {h.split("#")[0].split("?")[0]
                        for h in HREF_RE.findall(target.read_text(errors="replace"))}
                if idx_name not in home:
                    errors.append(f"{page}: does not link back to {idx_name} — every page "
                                  f"needs a way home, not only a way down")

    if as_designed:
        return errors, warnings, notes

    # ---- artifacts: the page against the real data directory ------------------
    written = {artifact_pattern(w) for c in cards for kind in DURABLE for w in c[kind]}
    ignore = set(m.get("ignore", []))
    for pattern in m.get("data_globs", []):
        real = sorted(p for p in root.glob(pattern) if p.is_file())
        if not real:
            notes.append(f"data_glob {pattern!r} matched nothing")
            continue
        unclaimed = sorted({artifact_pattern(p.name) for p in real}
                           - written
                           - {artifact_pattern(i) for i in ignore})
        for u in unclaimed:
            warnings.append(f"{map_name}: {u} exists under {pattern} but no stage "
                            f"claims to write it")

    # ---- contracts: coverage first, then shape --------------------------------
    # Set-completeness, not spot-checking. Every durable artifact the map claims
    # to write should have a declared shape, and a contract for something no
    # stage writes is a contract for a file that no longer exists. Checking one
    # direction only lets the doc set drift in the other.
    contracts = m.get("contracts") or {}
    declared = {artifact_pattern(k) for k in contracts}
    structured = {p for p in written
                  if p.rsplit(".", 1)[-1] in {"json", "jsonl", "ndjson"}}
    for undeclared in sorted(structured - declared - {artifact_pattern(i) for i in ignore}):
        warnings.append(f"{mf.name}: {undeclared} is written by a stage but has no "
                        f"contract — its shape is the next stage's assumption")
    for orphan in sorted(declared - written):
        warnings.append(f"{mf.name}: contract {orphan} describes a file no stage "
                        f"claims to write")

    for name, spec in contracts.items():
        glob = spec.get("sample")
        if not glob:
            notes.append(f"contract {name}: no sample glob, shape unverified")
            continue
        matches = sorted((p for p in root.glob(glob) if p.is_file()),
                         key=lambda p: p.stat().st_mtime, reverse=True)
        if not matches:
            warnings.append(f"contract {name}: sample {glob!r} matched no file")
            continue
        # Several samples, not one. A single newest file passes a contract it only
        # happens to satisfy — and where the glob spans books or subjects, the
        # optional keys differ per book, so one file makes a real optional key
        # look undeclared. Newest first, capped: the check should stay cheap.
        seen: set[str] = set()
        always: set[str] = set()
        fixed: set[str] = set()
        total = 0
        sampled: list[Path] = []
        keyed_by = spec.get("keyed_by")
        for path in matches[:spec.get("sample_count", 3)]:
            try:
                if keyed_by:
                    f, a, s, n = sample_keyed(path, spec.get("kind", "json"), keyed_by)
                    fixed |= f
                else:
                    s, a, n = sample_keys(path, spec.get("kind", "json"))
            except (json.JSONDecodeError, OSError, re.error) as exc:
                errors.append(f"contract {name}: {path} could not be read as "
                              f"{spec.get('kind', 'json')} — {exc}")
                continue
            if not n:
                warnings.append(f"contract {name}: {path.name} holds no records")
                continue
            sampled.append(path)
            seen |= s
            always = a if total == 0 else always & a
            total += n
        if not sampled:
            continue
        where_from = ", ".join(str(p.relative_to(root) if p.is_relative_to(root) else p)
                              for p in sampled)
        unit = "entries" if keyed_by else "records"
        notes.append(f"contract {name}: sampled {len(sampled)} file(s), {total} {unit} "
                     f"— {where_from}")
        # Emitted here rather than at the end of the loop: the keyed_by branch
        # returns early, and a stated-but-unchecked invariant must be reported for
        # every contract or the disclaimer stops being reliable.
        if spec.get("invariants"):
            notes.append(f"contract {name}: {len(spec['invariants'])} invariant(s) stated, "
                         f"none machine-checked — verify by hand")

        if keyed_by:
            # Two independent shapes to check: the fixed keys alongside the data
            # keys, and the shape shared by every value.
            fixed_required = set(spec.get("required", []))
            for missing in sorted(fixed_required - fixed):
                errors.append(f"contract {name}: required fixed key {missing!r} is absent "
                              f"from every sample")
            for undeclared in sorted(fixed - fixed_required - set(spec.get("optional", []))):
                warnings.append(f"contract {name}: samples carry top-level key "
                                f"{undeclared!r} that neither matches keyed_by "
                                f"{keyed_by!r} nor is declared")
            value_required = set(spec.get("value_required", []))
            for missing in sorted(value_required - always):
                where = "absent from every entry" if missing not in seen else \
                        "missing from some entries"
                errors.append(f"contract {name}: required value key {missing!r} is {where} "
                              f"({total} entries over {len(sampled)} file(s))")
            for undeclared in sorted(seen - value_required
                                     - set(spec.get("value_optional", []))):
                warnings.append(f"contract {name}: entries carry key {undeclared!r} that "
                                f"the contract does not declare")
            continue

        required = set(spec.get("required", []))
        for missing in sorted(required - always):
            where = "absent from every sample" if missing not in seen else \
                    "missing from some records"
            errors.append(f"contract {name}: required key {missing!r} is {where} "
                          f"({total} records over {len(sampled)} file(s))")
        for undeclared in sorted(seen - required - set(spec.get("optional", []))):
            warnings.append(f"contract {name}: samples carry key {undeclared!r} that the "
                            f"contract does not declare")

    # ---- coverage -------------------------------------------------------------
    # A stage with no drill-down is not automatically a gap: the skill's guidance is
    # that most stages should carry their boundary, invariants and decisions in the
    # card's mid-level block instead. Only a stage with neither is uncovered, and
    # conflating the two makes the note read as a to-do list of pages nobody should
    # write.
    covered = {s["name"] for s in stages
               if s.get("drilldown")
               or ((s.get("not") or s.get("no_not"))
                   and (s.get("invariants") or s.get("no_invariants")))}
    if (deep := [s["name"] for s in stages if s.get("drilldown")]):
        notes.append(f"{len(deep)}/{len(stages)} stages have a drill-down: "
                     f"{', '.join(deep)}")
    if (gaps := [f"{s['id']} {s['name']}" for s in stages if s["name"] not in covered]):
        notes.append(f"{len(gaps)}/{len(stages)} stages have neither a drill-down nor a "
                     f"mid-level block: {', '.join(gaps)}")
    else:
        notes.append(f"all {len(stages)} stages are covered by a drill-down or a "
                     f"mid-level block")
    return errors, warnings, notes


def check_page(page: Path, root: Path) -> tuple[list[str], list[str], int]:
    """Returns (errors, warnings, refs_checked)."""
    errors: list[str] = []
    warnings: list[str] = []
    text = page.read_text(errors="replace")

    bal = Balance()
    bal.feed(text)
    errors += [f"{page.name}: {e}" for e in bal.errors]
    for tag, line in bal.stack:
        errors.append(f"{page.name}: <{tag}> opened on line {line} is never closed")

    refs = REF_RE.findall(text)
    for raw in refs:
        # "cli.py · import_ → write gate": the arrow tail is a human annotation,
        # not part of the symbol.
        file_part, _, sym_part = raw.partition("·")
        file_part, sym_part = file_part.strip(), sym_part.strip()
        if not file_part or not sym_part:
            errors.append(f"{page.name}: ref {raw!r} is not 'file · symbol'")
            continue
        symbol = sym_part.split("→")[0].strip()
        src = find_source(file_part, root)
        if src is None:
            errors.append(f"{page.name}: ref {raw!r} — no such file under {root}")
            continue
        got = symbol_defined(src, symbol)
        if got is False:
            errors.append(f"{page.name}: ref {raw!r} — {symbol!r} not defined in {src}")
        elif got is None:
            warnings.append(f"{page.name}: ref {raw!r} — {src.suffix} not parsed, "
                            f"{symbol!r} appears but may not be a definition")

    for href in HREF_RE.findall(text):
        if "://" in href or href.startswith(("mailto:", "/")):
            continue
        # Fragments are checked too, and in-page ones (`#vocabulary`) most of all:
        # a heading gets renamed and every link to it goes quietly nowhere, which
        # no link-existence check would ever see.
        path_part, _, frag = href.partition("#")
        path_part = path_part.split("?")[0]
        target = page if not path_part else page.parent / path_part
        if not target.exists():
            errors.append(f"{page.name}: href {href!r} does not resolve")
            continue
        if frag and target.suffix.lower() in {".html", ".htm"}:
            target_text = text if target == page else target.read_text(errors="replace")
            if frag not in ANCHOR_RE.findall(target_text):
                errors.append(f"{page.name}: href {href!r} — no id or name "
                              f"{frag!r} in {target.name}")

    warnings += [f"{page.name}: {p}" for p in check_goals(text)]

    if re.search(r"\b\w+\.\w+:\d+\b", text):
        hits = sorted(set(re.findall(r"\b\w+\.\w+:\d+\b", text)))
        warnings.append(f"{page.name}: line-number refs found ({', '.join(hits[:5])}) — "
                        f"use 'file · symbol'; line numbers rot silently")

    return errors, warnings, len(refs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="page.html files, or a directory of them")
    ap.add_argument("--source-root", default=".", help="repo root the refs resolve against")
    ap.add_argument("--decisions", metavar="DIR",
                    help="record directory, when it is not <docs-dir>/decisions")
    args = ap.parse_args()

    if args.decisions:
        try:
            import render_decisions as _rd
        except ModuleNotFoundError:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import render_decisions as _rd
        _rd.set_decisions_dir(args.decisions)

    root = Path(args.source_root).resolve()
    given = [Path(raw) for raw in args.paths]
    pages: list[Path] = []
    for p in given:
        pages.extend(sorted(p.glob("*.html")) if p.is_dir() else [p])
    pages = [p for p in pages if p.is_file()]
    if not pages:
        print("no pages found", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    all_warnings: list[str] = []
    notes: list[str] = []
    total_refs = 0
    for page in pages:
        errors, warnings, n = check_page(page, root)
        total_refs += n
        all_errors += errors
        all_warnings += warnings
        mark = "FAIL" if errors else "ok  "
        print(f"{mark} {page.name}  ({n} refs)")

    if (mf := find_manifest(given)):
        errors, warnings, notes = check_manifest(mf, root)
        all_errors += errors
        all_warnings += warnings
        print(f"{'FAIL' if errors else 'ok  '} {mf.name}  (code / map / data)")
    else:
        notes.append("no architecture.json beside the pages — the stage, artifact and "
                     "contract checks were skipped, so nothing here compares the docs "
                     "against the code")

    for n_ in notes:
        print(f"  note  {n_}")
    for w in all_warnings:
        print(f"  WARN  {w}")
    for e in all_errors:
        print(f"  ERROR {e}")
    print(f"\n{len(pages)} page(s), {total_refs} ref(s), "
          f"{len(all_errors)} error(s), {len(all_warnings)} warning(s)")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
