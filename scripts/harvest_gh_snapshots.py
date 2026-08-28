#!/usr/bin/env python3
"""harvest_gh_snapshots.py — Article XXIV compliance (Static Data Covenant).

doorman/index.html and classic.html used to make unauthenticated
api.github.com calls at every visitor's page load: the seed's own agents/
directory listing, its recent commits, its repo metadata (fork count), and
the same three for the seed's parent_repo (lineage gift). This script is the
CI harvester — it makes those calls ONCE, here, and commits the results as
static JSON in the *identical* shape the API returns, so the pages can read
a snapshot with a one-URL change and zero parsing changes.

Writes (all under state/):
  self_agents.json    — GET /repos/{self}/contents/agents   (contents API shape)
  self_commits.json   — GET /repos/{self}/commits?per_page=30 (commits API shape)
  self_repo.json       — GET /repos/{self}                   (repo API shape)
  parent_agents.json  — same three for rappid.json's parent_repo, if set.
  parent_commits.json
  parent_repo.json

self/parent owner+repo are read from the committed rappid.json (`github` and
`parent_repo` fields) — no guessing from the runtime host/path, since CI runs
once per repo and rappid.json already names both.

A 404 (e.g. no agents/ directory at the target repo) resolves to the same
empty value the old page code fell back to (`[]`) — a 404 body isn't valid
"same shape" JSON we could serve verbatim anyway.

Non-fatal by design for the parent lookup (parent_repo may 404 or vanish);
fatal only if the self repo — the one this workflow runs in — can't be read,
since that indicates a broken token/rate-limit rather than absent data.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
RAPPID = ROOT / "rappid.json"

GH_RE = re.compile(r"github\.com/([^/]+)/([^/.]+)")


def _headers():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "kody-twin-covenant-harvester"}
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _get(url):
    """Returns (status, parsed_json_or_None)."""
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        print(f"  ! {url} -> {type(e).__name__}: {e}")
        return None, None


def _write(name, value):
    STATE.mkdir(parents=True, exist_ok=True)
    out = STATE / name
    out.write_text(json.dumps(value, indent=1, sort_keys=True) + "\n")
    print(f"  ✓ state/{name}")


def harvest(owner, repo, prefix, required):
    base = f"https://api.github.com/repos/{owner}/{repo}"
    status, agents = _get(f"{base}/contents/agents")
    _write(f"{prefix}_agents.json", agents if isinstance(agents, list) else [])

    status_c, commits = _get(f"{base}/commits?per_page=30")
    if not isinstance(commits, list):
        if required:
            print(f"  ✗ {owner}/{repo} commits unreadable (status={status_c}) — refusing to "
                  f"overwrite an existing snapshot with nothing")
            existing = STATE / f"{prefix}_commits.json"
            if not existing.exists():
                return False
        commits = json.loads((STATE / f"{prefix}_commits.json").read_text()) \
            if (STATE / f"{prefix}_commits.json").exists() else []
    _write(f"{prefix}_commits.json", commits)

    status_r, repo_meta = _get(base)
    if not isinstance(repo_meta, dict):
        if required:
            print(f"  ✗ {owner}/{repo} repo metadata unreadable (status={status_r})")
            existing = STATE / f"{prefix}_repo.json"
            if not existing.exists():
                return False
        repo_meta = json.loads((STATE / f"{prefix}_repo.json").read_text()) \
            if (STATE / f"{prefix}_repo.json").exists() else {}
    _write(f"{prefix}_repo.json", repo_meta)
    return True


def main():
    if not RAPPID.exists():
        print("✗ rappid.json missing — nothing to harvest for")
        return 2
    rid = json.loads(RAPPID.read_text())

    self_gh = rid.get("github") or ""
    m = GH_RE.search(self_gh)
    if not m:
        print(f"✗ rappid.json github field unparseable: {self_gh!r}")
        return 2
    print(f"self: {m.group(1)}/{m.group(2)}")
    ok = harvest(m.group(1), m.group(2), "self", required=True)
    if not ok:
        return 1

    parent = rid.get("parent_repo") or ""
    pm = GH_RE.search(parent)
    if pm:
        print(f"parent: {pm.group(1)}/{pm.group(2)}")
        harvest(pm.group(1), pm.group(2), "parent", required=False)
    else:
        print("· no parent_repo in rappid.json — writing empty parent snapshots")
        _write("parent_agents.json", [])
        _write("parent_commits.json", [])
        _write("parent_repo.json", {})

    return 0


if __name__ == "__main__":
    sys.exit(main())
