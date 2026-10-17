#!/usr/bin/env python3
"""Scan a codebase for agent call-site smells that are cheap to detect statically.

Every check here corresponds to a failure that actually shipped. None of them is
clever; they are all things reviewers miss because the code looks fine locally.

Usage:
    check_agent_contracts.py <path> [--quiet]

Exit code 1 if any ERROR-level finding is present, so it can gate CI.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

# --- checks -----------------------------------------------------------------

# NB: no trailing \b — `]` and the following `,` are both non-word characters, so
# a word boundary never matches there and every `list[dict]` slips through. Anchor
# on what may legally follow the annotation instead.
UNTYPED_OUTPUT = re.compile(
    r"output_type\s*=\s*(?:dict|Any|list\[\s*(?:dict|Any)\s*\])\s*(?=[,)\]\s]|$)")

#: A judge/model field compared with == or != without passing through a coercer
#: first. Names are the common ones; extend for your codebase.
RAW_COMPARE = re.compile(
    r"""(?<![\w.])(?P<lhs>\w*(?:chosen|verdict|answer|label|index)\w*)\s*
        (?:==|!=)\s*""",
    re.VERBOSE | re.IGNORECASE,
)

BARE_EXCEPT_RETRY = re.compile(r"except\s+Exception\s*:")


def _iter_py(root: pathlib.Path):
    skip = {".venv", "node_modules", "__pycache__", ".git", "build", "dist", "site"}
    for p in root.rglob("*.py"):
        if not any(part in skip for part in p.parts):
            yield p


def _assigned_from_coercer(src: str, name: str) -> bool:
    """Was `name` produced by something that looks like a coercion helper?"""
    pat = re.compile(rf"\b{re.escape(name)}\s*=\s*(coerce_|_coerce|normali[sz]e|to_int|parse_)")
    return bool(pat.search(src))


def check_file(path: pathlib.Path) -> list[tuple[str, int, str, str]]:
    """Return [(level, lineno, code, message)]."""
    src = path.read_text(encoding="utf-8", errors="replace")
    out: list[tuple[str, int, str, str]] = []
    lines = src.splitlines()

    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            continue

        if UNTYPED_OUTPUT.search(line):
            out.append((
                "ERROR", n, "untyped-output",
                "output_type=dict/Any is not a contract — it compiles to an object "
                "schema with no properties, and a strict-schema model correctly "
                "returns {}. Declare a typed model."))

        m = RAW_COMPARE.search(line)
        if m:
            name = m.group("lhs")
            if not _assigned_from_coercer(src, name):
                out.append((
                    "WARN", n, "raw-compare",
                    f"`{name}` is compared without an obvious coercion step. Models "
                    f"return \"0\" for 0, null, or omit the field — an int/str compare "
                    f"then reads a CORRECT answer as a mismatch."))

    # AST checks
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out

    for node in ast.walk(tree):
        # A bare `except Exception` immediately around a model call, with no
        # re-raise and no logging, swallows the signal that a stage is broken.
        if isinstance(node, ast.ExceptHandler) and node.type is not None:
            if getattr(node.type, "id", "") == "Exception":
                body_src = "\n".join(
                    lines[c.lineno - 1] for c in node.body
                    if hasattr(c, "lineno") and c.lineno <= len(lines))
                silent = not re.search(r"print|log|raise|warn", body_src)
                if silent:
                    out.append((
                        "WARN", node.lineno, "silent-except",
                        "`except Exception` with no log and no re-raise. A stage that "
                        "fails silently is indistinguishable from one that had nothing "
                        "to do."))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=pathlib.Path)
    ap.add_argument("--quiet", action="store_true", help="errors only")
    args = ap.parse_args()

    root = args.path
    files = [root] if root.is_file() else list(_iter_py(root))

    findings: list[tuple[pathlib.Path, str, int, str, str]] = []
    for f in files:
        for level, n, code, msg in check_file(f):
            findings.append((f, level, n, code, msg))

    errors = [x for x in findings if x[1] == "ERROR"]
    warns = [x for x in findings if x[1] == "WARN"]

    shown = errors if args.quiet else errors + warns
    for f, level, n, code, msg in sorted(shown, key=lambda x: (str(x[0]), x[2])):
        try:
            rel = f.relative_to(root if root.is_dir() else root.parent)
        except ValueError:
            rel = f
        print(f"{level:5} {rel}:{n}  [{code}]\n      {msg}")

    print(f"\n{len(files)} file(s) · {len(errors)} error(s) · {len(warns)} warning(s)")
    if not findings:
        print("no agent call-site smells found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
