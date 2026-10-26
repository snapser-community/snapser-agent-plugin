#!/usr/bin/env python3
"""
Bump the plugin version everywhere it must stay in sync:
  - .claude-plugin/marketplace.json  -> metadata.version AND plugins[0].version
  - .claude-plugin/plugin.json       -> version
  - gemini-extension.json            -> version

Agents (Claude/Codex/Gemini) cache the plugin PER VERSION — an un-bumped version
never reaches them, and Forge's vendor script refuses to copy without a bump.

marketplace.json is the version the vendor script gates on, so treat it as the
source of truth. plugin.json and gemini-extension.json must follow it — they
drifted a version apart once because this script didn't write plugin.json.

Usage:
  python3 scripts/bump-version.py            # patch bump: 0.3.0 -> 0.3.1
  python3 scripts/bump-version.py minor      # 0.3.1 -> 0.4.0
  python3 scripts/bump-version.py major      # 0.4.0 -> 1.0.0
  python3 scripts/bump-version.py 0.5.2      # set explicitly
  python3 scripts/bump-version.py --dry      # show what would change, write nothing
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
GEMINI = ROOT / "gemini-extension.json"


def main() -> None:
    args = [a for a in sys.argv[1:]]
    dry = "--dry" in args
    args = [a for a in args if a != "--dry"]
    mode = args[0] if args else "patch"

    mkt = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    cur = mkt["metadata"]["version"]
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", cur)
    if not m:
        sys.exit(f"current version {cur!r} is not X.Y.Z — fix marketplace.json first")
    major, minor, patch = (int(x) for x in m.groups())

    if re.fullmatch(r"\d+\.\d+\.\d+", mode):
        new = mode
    elif mode == "patch":
        new = f"{major}.{minor}.{patch + 1}"
    elif mode == "minor":
        new = f"{major}.{minor + 1}.0"
    elif mode == "major":
        new = f"{major + 1}.0.0"
    else:
        sys.exit(f"unknown bump {mode!r} — use patch | minor | major | X.Y.Z")

    # Flag pre-existing drift so a bump doesn't quietly paper over it.
    for path in (PLUGIN, GEMINI):
        if path.exists():
            was = json.loads(path.read_text(encoding="utf-8")).get("version")
            if was != cur:
                print(f"NOTE: {path.relative_to(ROOT)} was at {was}, not {cur} — realigning to {new}")

    print(f"{cur} -> {new}" + ("  (dry run — nothing written)" if dry else ""))
    if dry:
        return

    mkt["metadata"]["version"] = new
    for p in mkt.get("plugins", []):
        p["version"] = new
    MARKETPLACE.write_text(json.dumps(mkt, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MARKETPLACE.relative_to(ROOT)}")

    for path, label in ((PLUGIN, "plugin.json"), (GEMINI, "gemini-extension.json")):
        if not path.exists():
            print(f"WARN: {label} missing — not bumped")
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["version"] = new
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")

    print("next: commit here, then in snapser-forge run `npm run vendor-plugin` and commit resources/.")


if __name__ == "__main__":
    main()
