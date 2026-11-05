#!/usr/bin/env python3
"""
Spintax checker for Smartlead email copy.

Smartlead syntax:  {Hi|Hey|Hello} {{first_name}},
  - single braces with pipes  = spintax (one option is picked per email)
  - double braces             = a merge variable

Checks a copy file (or stdin) and reports:
  - broken spintax: unclosed or stray braces, empty options, one-option groups
  - variables written with single braces ({first_name} instead of {{first_name}})
  - variables inside spin options (easy to break when a field is empty)
  - spam-trigger words (English and Swedish), links and exclamation marks
  - how many distinct versions the copy produces, and word count range
  - N sample renders to read before approving

Exit code is 1 when there are errors, so it can gate a launch checklist.

    python spintax_check.py copy/step1.txt
    python spintax_check.py copy/step1.txt --samples 8 --seed 3
    cat step1.txt | python spintax_check.py -
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from dataclasses import dataclass, field
from math import prod
from pathlib import Path

SPAM_WORDS = [
    # English
    "free", "guarantee", "guaranteed", "risk-free", "risk free", "100%",
    "act now", "click here", "urgent", "limited time", "buy now", "winner",
    "cash", "no cost", "no obligation", "special offer", "exclusive deal",
    "earn money", "double your", "$$", "!!", "dear friend", "congratulations",
    # Swedish
    "gratis", "erbjudande", "garanti", "garanterat", "klicka här",
    "agera nu", "begränsad tid", "vinnare", "kostnadsfritt",
]

VARIABLE_RE = re.compile(r"\{\{\s*([A-Za-z0-9_\-. ]+?)\s*\}\}")
IDENT_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


# --------------------------------------------------------------------------
# Parser: text -> tree of literal strings, variables and spin groups
# --------------------------------------------------------------------------

@dataclass
class Spin:
    options: list[list] = field(default_factory=list)  # each option is a sequence of nodes
    pos: int = 0


@dataclass
class Var:
    name: str


class SpintaxError(Exception):
    def __init__(self, msg: str, pos: int):
        super().__init__(msg)
        self.pos = pos


def parse(text: str) -> list:
    """Parse into a node list. Raises SpintaxError on broken syntax."""
    nodes, i = _parse_seq(text, 0, top=True)
    return nodes


def _parse_seq(text: str, i: int, top: bool) -> tuple[list, int]:
    nodes: list = []
    buf: list[str] = []

    def flush():
        if buf:
            nodes.append("".join(buf))
            buf.clear()

    while i < len(text):
        ch = text[i]
        if text.startswith("{{", i):
            end = text.find("}}", i + 2)
            if end == -1:
                raise SpintaxError("variable opened with {{ but never closed with }}", i)
            flush()
            nodes.append(Var(text[i + 2:end].strip()))
            i = end + 2
        elif ch == "{":
            flush()
            spin, i = _parse_spin(text, i)
            nodes.append(spin)
        elif ch in "|}":
            if top:
                what = "stray '}'" if ch == "}" else "'|' outside any {...} group"
                raise SpintaxError(what, i)
            flush()
            return nodes, i
        else:
            buf.append(ch)
            i += 1
    if not top:
        raise SpintaxError("spin group opened with { but never closed", i)
    flush()
    return nodes, i


def _parse_spin(text: str, start: int) -> tuple[Spin, int]:
    spin = Spin(pos=start)
    i = start + 1
    while True:
        if i >= len(text):
            raise SpintaxError("spin group opened with { but never closed", start)
        option, i = _parse_seq(text, i, top=False)
        spin.options.append(option)
        if i >= len(text):
            raise SpintaxError("spin group opened with { but never closed", start)
        if text[i] == "|":
            i += 1
            continue
        # text[i] == "}"
        return spin, i + 1


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def count_versions(nodes: list) -> int:
    total = 1
    for n in nodes:
        if isinstance(n, Spin):
            total *= sum(count_versions(opt) for opt in n.options)
    return total


def render(nodes: list, rng: random.Random, variables: dict[str, str]) -> str:
    out = []
    for n in nodes:
        if isinstance(n, str):
            out.append(n)
        elif isinstance(n, Var):
            out.append(variables.get(n.name, "{{" + n.name + "}}"))
        else:
            out.append(render(rng.choice(n.options), rng, variables))
    return "".join(out)


def _line_col(text: str, pos: int) -> str:
    line = text.count("\n", 0, pos) + 1
    col = pos - (text.rfind("\n", 0, pos) + 1) + 1
    return f"line {line}, col {col}"


def check(text: str) -> tuple[list[str], list[str], list | None]:
    """Return (errors, warnings, parsed nodes or None)."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        nodes = parse(text)
    except SpintaxError as e:
        errors.append(f"{_line_col(text, e.pos)}: {e}")
        return errors, warnings, None

    def walk(seq: list, inside_spin: bool):
        for n in seq:
            if isinstance(n, Var):
                if not n.name:
                    errors.append("empty variable {{}}")
                elif inside_spin:
                    warnings.append(f"variable {{{{{n.name}}}}} sits inside a spin option; "
                                    "keep variables outside spins")
            elif isinstance(n, Spin):
                where = _line_col(text, n.pos)
                if len(n.options) == 1:
                    only = "".join(x for x in n.options[0] if isinstance(x, str)).strip()
                    if IDENT_RE.match(only.lower()):
                        errors.append(f"{where}: {{{only}}} looks like a variable; "
                                      f"Smartlead variables use double braces: {{{{{only}}}}}")
                    else:
                        errors.append(f"{where}: spin group with only one option: {{{only}}}")
                for k, opt in enumerate(n.options, 1):
                    rendered = "".join(x if isinstance(x, str) else "x" for x in opt)
                    if not rendered.strip():
                        errors.append(f"{where}: option {k} is empty")
                walk_opts = [opt for opt in n.options]
                for opt in walk_opts:
                    walk(opt, True)

    walk(nodes, False)

    lowered = text.lower()
    for word in SPAM_WORDS:
        pattern = re.escape(word)
        if word[0].isalnum():
            pattern = r"(?<![a-zåäö])" + pattern
        if word[-1].isalnum():
            pattern += r"(?![a-zåäö])"
        if re.search(pattern, lowered):
            warnings.append(f"spam-trigger word: \"{word}\"")

    links = re.findall(r"https?://\S+|www\.\S+", text)
    if links:
        warnings.append(f"{len(links)} link(s) found; keep step 1 link-free")
    if text.count("!") > 1:
        warnings.append(f"{text.count('!')} exclamation marks; use one at most")

    return errors, warnings, nodes


SAMPLE_VARS = {
    "first_name": "Anna", "last_name": "Svensson", "company_name": "Harbor PT",
    "company": "Harbor PT", "city": "Tampa", "location": "Tampa",
    "sender_name": "Leif", "sender_firstname": "Leif",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="copy file, or - for stdin")
    ap.add_argument("--samples", type=int, default=5, help="sample renders to print")
    ap.add_argument("--seed", type=int, default=1, help="random seed for samples")
    args = ap.parse_args(argv)

    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    errors, warnings, nodes = check(text)

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")

    if nodes is not None:
        versions = count_versions(nodes)
        rng = random.Random(args.seed)
        renders = [render(nodes, rng, SAMPLE_VARS) for _ in range(max(args.samples, 0))]
        word_counts = [len(r.split()) for r in renders] or [0]
        variables = sorted({m.group(1).strip() for m in VARIABLE_RE.finditer(text)})
        print(f"\nVersions: {versions:,}" + ("  (aim for 50+ per step)" if versions < 50 else ""))
        if renders:
            print(f"Words in samples: {min(word_counts)}-{max(word_counts)}")
        print(f"Variables used: {', '.join(variables) or 'none'}")
        for k, r in enumerate(renders, 1):
            print(f"\n--- sample {k} ---\n{r.strip()}")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
