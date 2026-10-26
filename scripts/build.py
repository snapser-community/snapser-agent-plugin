#!/usr/bin/env python3
"""
Build script for the Snapser plugin.

Single source of truth: source/CONTEXT.md
Generates:
  - CLAUDE.md               (Claude Code / Cowork reads this at the plugin root)
  - AGENTS.md               (Codex and OpenCode both read AGENTS.md at the project root)
  - data/releases/INDEX.md  (lookup table over the release notes in data/releases/)
  - data/docs/INDEX.md      (path -> topic map over the docs in data/docs/)

Also link-checks every local path referenced in source/CONTEXT.md and
skills/**/*.md so a renamed skill or data file fails the build instead of
silently breaking an agent at runtime.

Usage:
  python3 scripts/build.py           # build + link check
  python3 scripts/build.py --check   # link check only (no file writes)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source" / "CONTEXT.md"
RELEASES = ROOT / "data" / "releases"

HEADER = (
    "<!-- GENERATED FILE — DO NOT EDIT. -->\n"
    "<!-- Edit source/CONTEXT.md and run `python3 scripts/build.py`. -->\n\n"
)

TARGETS = ["CLAUDE.md", "AGENTS.md"]

# Local paths referenced in prose/code blocks, e.g. skills/foo/SKILL.md,
# data/docs/..., data/snap-swaggers/... Bare directories are checked too.
PATH_RE = re.compile(r"(?<![\w/.-])((?:skills|data|source|scripts|docs)/[\w./-]*)")

# References that contain placeholders and can't be checked literally.
PLACEHOLDER_RE = re.compile(r"[<>$*{}]")


def find_refs(text: str):
    for match in PATH_RE.finditer(text):
        ref = match.group(1).rstrip(".").rstrip("/")
        if PLACEHOLDER_RE.search(ref):
            continue
        yield ref


def link_check() -> int:
    errors = 0
    files_to_scan = [SOURCE] + sorted(ROOT.glob("skills/**/*.md"))
    for f in files_to_scan:
        text = f.read_text(encoding="utf-8")
        for ref in set(find_refs(text)):
            if not (ROOT / ref).exists():
                print(f"BROKEN REF: {f.relative_to(ROOT)} -> {ref}")
                errors += 1
    return errors


def build() -> None:
    body = SOURCE.read_text(encoding="utf-8")
    for name in TARGETS:
        (ROOT / name).write_text(HEADER + body, encoding="utf-8")
        print(f"wrote {name}")


# ---------------------------------------------------------------------------
# data/releases/INDEX.md
#
# The release notes are per-release .mdx files named after the Snapser platform
# version (1.12.0.mdx). Two problems for an agent reading them cold: the
# filenames don't sort chronologically (1.10.0 < 1.2.0 lexically), and finding
# "did leaderboards change?" means grepping all 30 files. The generated index
# fixes both, so drop a new release .mdx in and re-run this script.
# ---------------------------------------------------------------------------

RELEASE_INDEX = RELEASES / "INDEX.md"

# Release-note headings -> the canonical snap name used by data/snap-swaggers/
# and `snapctl snaps enumerate`. Only aliases need listing; a heading that
# already matches a canonical name resolves on its own.
SNAP_ALIASES = {
    "in-app purchases": "iap",
    "stats": "statistics",
    "social-graph": "social-graph",
    "game server fleet": "game-server-fleets",
    "game server fleets": "game-server-fleets",
    "gsf (game server fleets)": "game-server-fleets",
    "gsf": "game-server-fleets",
    "websocket / hermes": "hermes-websocket",
}

# Headings that sit at the same level as snap names but describe an area of the
# product rather than a snap.
NOT_SNAPS = {
    "improvements",
    "bug fix",
    "bug fixes",
    "breaking changes",
    "new features",
    "new tools",
    "important changes",
    "commands",
    "web app",
    "snapctl",
    "spotlight",
    "documentation",
    "snaps",
    "sdk",
    "infrastructure",
    "networking",
    "feature improvements",
}

# A snap name appears either as a subsection of one of these, or (in a few
# early releases) as a top-level `##` heading of its own.
SNAP_PARENTS = {"snaps", "feature improvements"}

VERSION_RE = re.compile(r"^\d+(?:\.\d+)*$")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.*?)\s*$")
DATE_RE = re.compile(r"^#{4,6}\s+(.*?)\s*$")


def canonical_snaps() -> set:
    """Snap names we can resolve against, taken from the bundled swagger specs."""
    return {p.name.split(".")[0] for p in (ROOT / "data" / "snap-swaggers").glob("*.json")}


def clean_heading(text: str) -> str:
    """Strip markdown emphasis and leading decoration from a heading."""
    text = re.sub(r"[*_`]", "", text)
    return text.lstrip("⚠️ ⚡🎉 ").strip()


def resolve_snaps(heading: str, known: set):
    """Map one heading to zero or more canonical snap names."""
    out = []
    # "Parties & Guilds" documents a change that landed in both snaps.
    for part in re.split(r"\s*(?:&|/|,| and )\s*", heading):
        key = part.strip().lower()
        if not key or key in NOT_SNAPS:
            continue
        name = SNAP_ALIASES.get(key, key.replace(" ", "-"))
        out.append(name)
    # Only trust a multi-way split when every piece resolved to a real snap;
    # otherwise treat the heading as one unit (e.g. "GSF (Game Server Fleets)").
    if len(out) > 1 and not all(n in known for n in out):
        key = heading.strip().lower()
        out = [SNAP_ALIASES.get(key, key.replace(" ", "-"))]
    return out


def parse_release(path: Path, known: set) -> dict:
    version = path.stem
    date = ""
    sections, snaps = [], []
    parent = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not date:
            m = DATE_RE.match(line)
            # The date is the `##### Month D, YYYY` line right under the title.
            if m and re.search(r"\d{4}", m.group(1)):
                date = m.group(1)
                continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        level, heading = len(m.group(1)), clean_heading(m.group(2))
        if not heading:
            continue
        if level == 2:
            parent = heading.lower()
            sections.append(heading)
            if parent not in NOT_SNAPS:
                snaps += [s for s in resolve_snaps(heading, known) if s in known]
        elif level == 3 and parent in SNAP_PARENTS:
            snaps += resolve_snaps(heading, known)
    return {
        "version": version,
        "date": date,
        "sections": sections,
        "snaps": sorted(set(snaps)),
    }


def write_release_index() -> None:
    if not RELEASES.is_dir():
        return
    known = canonical_snaps()
    releases = [
        parse_release(p, known)
        for p in sorted(RELEASES.glob("*.mdx"))
        if VERSION_RE.match(p.stem)
    ]
    if not releases:
        return
    releases.sort(key=lambda r: [int(n) for n in r["version"].split(".")], reverse=True)

    by_snap = {}
    for r in releases:
        for snap in r["snaps"]:
            by_snap.setdefault(snap, []).append(r["version"])

    latest = releases[0]
    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT. -->",
        "<!-- Add a release .mdx to data/releases/ and run `python3 scripts/build.py`. -->",
        "",
        "# Snapser Release Notes — Index",
        "",
        f"**Latest release: {latest['version']}** ({latest['date']}). "
        f"{len(releases)} releases on record, "
        f"{releases[-1]['version']} ({releases[-1]['date']}) onward.",
        "",
        "Each release is a file at `data/releases/<version>.mdx`. These are the Snapser",
        "**platform** release notes — human-readable changelogs of what shipped in the",
        "platform, snaps, Web App, snapctl, and SDKs.",
        "",
        "> **Read-only reference.** Release notes exist to tell a user *what changed*.",
        "> They are never a source of truth for building anything: do not take snap",
        "> versions, manifest structure, settings values, or API shapes from them. Those",
        "> come from `snapctl`, `data/snap-swaggers/`, and the Admin SDK as usual.",
        "",
        "## Releases (newest first)",
        "",
        "| Version | Date | Sections |",
        "|---|---|---|",
    ]
    for r in releases:
        sections = ", ".join(r["sections"]) or "—"
        lines.append(f"| [{r['version']}]({r['version']}.mdx) | {r['date']} | {sections} |")

    lines += [
        "",
        "## Snap → releases that changed it",
        "",
        "Use this to answer \"did anything change in <snap>?\" without grepping every file.",
        "Covers snap-level changes only — platform, Web App, and snapctl changes are in the",
        "table above.",
        "",
        "| Snap | Releases (newest first) |",
        "|---|---|",
    ]
    for snap in sorted(by_snap):
        versions = ", ".join(f"[{v}]({v}.mdx)" for v in by_snap[snap])
        lines.append(f"| `{snap}` | {versions} |")
    lines.append("")

    RELEASE_INDEX.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote data/releases/INDEX.md ({len(releases)} releases, {len(by_snap)} snaps)")


# ---------------------------------------------------------------------------
# data/docs/INDEX.md
#
# 191 .mdx files. An agent that has never opened this folder has no way to know
# that "which login providers are supported" lives in
# data/docs/infra/snaps/auth/connectors/ — data/docs/index.mdx is the docs
# landing page, not a map. Without a map the only move is a blind grep, which
# is slow and misses anything phrased differently to the question. So generate
# one line per file: its path, its title, and its own `export const
# description` where the page declares one.
# ---------------------------------------------------------------------------

DOCS = ROOT / "data" / "docs"
DOCS_INDEX = DOCS / "INDEX.md"

# Longest / most specific prefix first — the first match wins.
DOC_SECTIONS = [
    ("data/docs/ai", "AI — Cortex, MCP, OpenAI"),
    ("data/docs/business-intelligence", "Business intelligence — dashboards, charts, SQL lab, alerts"),
    ("data/docs/custom", "Custom code — BYOSnap, BYOWS, BYOGS, BYO data store, tools"),
    ("data/docs/guides/samples", "Sample projects — Unity, Unreal, Roblox, web, mobile"),
    ("data/docs/guides/tutorials", "Tutorials — step by step"),
    ("data/docs/guides", "Guides"),
    ("data/docs/infra", "Snaps — per-snap overviews, config tools, auth connectors"),
    ("data/docs/snapend/networking", "Snapend — networking, gateway, security"),
    ("data/docs/snapend/tools", "Snapend — admin tools"),
    ("data/docs/snapend", "Snapend — architecture, SDKs, pipeline, logs"),
    ("data/docs/resources", "Resources — CLI, marketplace, portal, audit tool"),
]
DOC_ROOT_SECTION = "Start here — platform overview and core concepts"

DESC_RE = re.compile(r"export\s+const\s+description\s*=\s*(['\"])(.*?)\1", re.S)
H1_RE = re.compile(r"^#\s+(.*?)\s*$", re.M)


def doc_section(rel: str) -> str:
    """Which INDEX.md heading a docs file is filed under."""
    if rel.count("/") == 2:  # data/docs/<file>.mdx
        return DOC_ROOT_SECTION
    for prefix, title in DOC_SECTIONS:
        if rel.startswith(prefix + "/"):
            return title
    return "Other"


def doc_entry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = H1_RE.search(text)
    # examples.mdx has its title commented out; fall back to the filename.
    title = clean_heading(m.group(1)) if m else path.stem.replace("-", " ").title()
    m = DESC_RE.search(text)
    desc = re.sub(r"\s+", " ", m.group(2)).strip() if m else ""
    rel = str(path.relative_to(ROOT))
    t, d = title.rstrip(".").lower(), desc.rstrip(".").lower()
    # A description that only repeats the title, or that names the folder it
    # sits in ("Auth" on every auth connector page), adds no lookup value.
    if d and (d in t or t in d):
        if len(d) > len(t):
            title, desc = desc, ""
        else:
            desc = ""
    if desc and " " not in desc and d in rel.lower().split("/"):
        desc = ""
    return {
        "rel": rel,
        "title": title.replace("|", "\\|"),
        "desc": desc.replace("|", "\\|"),
    }


def write_docs_index() -> None:
    if not DOCS.is_dir():
        return
    files = sorted(p for p in DOCS.rglob("*.mdx"))
    if not files:
        return
    grouped = {}
    for p in files:
        e = doc_entry(p)
        grouped.setdefault(doc_section(e["rel"]), []).append(e)

    order = [DOC_ROOT_SECTION] + [t for _, t in DOC_SECTIONS] + ["Other"]
    seen = []
    for title in order:
        if title in grouped and title not in seen:
            seen.append(title)

    lines = [
        "<!-- GENERATED FILE — DO NOT EDIT. -->",
        "<!-- Add a docs .mdx to data/docs/ and run `python3 scripts/build.py`. -->",
        "",
        "# Snapser Documentation — Index",
        "",
        f"Every Snapser documentation page bundled in this plugin — {len(files)} files, "
        "with the topic each one covers. Read this first to pick the file that answers",
        "the question, then read that file. Do not grep the whole folder, and never",
        "search the web for a Snapser answer — the docs are all here.",
        "",
        "Paths are relative to the plugin root. `data/docs/index.mdx` is the docs landing",
        "page; this file is the map.",
        "",
    ]
    for title in seen:
        lines += ["## " + title, "", "| Path | Topic |", "|---|---|"]
        for e in grouped[title]:
            topic = e["title"] + (f" — {e['desc']}" if e["desc"] else "")
            lines.append(f"| `{e['rel']}` | {topic} |")
        lines.append("")

    DOCS_INDEX.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote data/docs/INDEX.md ({len(files)} pages, {len(seen)} sections)")


def main() -> None:
    if not SOURCE.exists():
        sys.exit(f"missing {SOURCE}")
    if "--check" not in sys.argv:
        write_release_index()
        write_docs_index()
    errors = link_check()
    if errors:
        sys.exit(f"{errors} broken reference(s). Fix before building.")
    if "--check" not in sys.argv:
        build()
    print("link check passed.")


if __name__ == "__main__":
    main()
