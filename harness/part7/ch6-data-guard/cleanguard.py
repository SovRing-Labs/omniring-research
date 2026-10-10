"""cleanguard — no-train path guard (SEED-VISION-ROADMAP P0, J 2026-10-03: "make our ground completely sovereign").

Default DENY. A training input is allowed only if the nearest marker walking up from it is `.clean-room.json` with
"train": true. A `.no-train.json` marker (or no marker at all) refuses it. Markers are written by the tool that produced
the data (bin/clean-room, bin/reason-gen) or by the seat with J's approval, and record WHY the data is clean.

  require_clean(path)                         -> marker dict, or SystemExit naming the path and the reason
  require_clean(path, row_filter="clean-room.strict")
        a no-train source is allowed ONLY when the caller filters every row by provenance itself with a named filter
        from ROW_FILTERS (e.g. theads_rule.py keeps permissive rows only); the use is printed.
CLEANGUARD_RESEARCH=1 lets in-house research harnesses read unmarked data with a loud warning; bin/pod-launch refuses it,
and the seed's pre-training must never set it.
"""
import json
import os
import sys

MARK_OK, MARK_NO = ".clean-room.json", ".no-train.json"
ROW_FILTERS = {"clean-room.strict": "bin/clean-room strict(): permissive-weights models only, unknown dropped"}


def _marker(path):
    d = os.path.abspath(os.path.expanduser(path))
    d = d if os.path.isdir(d) else os.path.dirname(d)
    while True:
        for name in (MARK_NO, MARK_OK):                  # a no-train marker at the same level wins
            p = os.path.join(d, name)
            if os.path.exists(p):
                try:
                    return name, p, json.load(open(p))
                except (OSError, ValueError):
                    return MARK_NO, p, {"why": "unreadable marker"}
        if d == os.path.dirname(d):
            return None, None, {}
        d = os.path.dirname(d)


def require_clean(path, row_filter=None):
    name, where, m = _marker(path)
    if name == MARK_OK and m.get("train") is True:
        return m
    if row_filter in ROW_FILTERS and name == MARK_NO:
        print(f"cleanguard: {path} is no-train ({where}); allowed ONLY through row filter {row_filter}: "
              f"{ROW_FILTERS[row_filter]}", file=sys.stderr, flush=True)
        return {"row_filter": row_filter, **m}
    why = m.get("why", "no clean-room marker above this path (default deny)") if name else "no marker (default deny)"
    if os.environ.get("CLEANGUARD_RESEARCH") == "1":
        print(f"cleanguard: WARNING research override — {path} is NOT clean: {why}", file=sys.stderr, flush=True)
        return {"research_override": True, "why": why}
    raise SystemExit(f"cleanguard: REFUSED {path}: {why} (marker: {where or 'none'})")


def mark(dirpath, train, why, by, **extra):
    """Write a marker. train=True -> .clean-room.json, False -> .no-train.json."""
    p = os.path.join(os.path.expanduser(dirpath), MARK_OK if train else MARK_NO)
    json.dump({"train": bool(train), "why": why, "by": by, **extra}, open(p, "w"), indent=1, sort_keys=True)
    return p


if __name__ == "__main__":
    for a in sys.argv[1:]:
        try:
            print(a, "->", require_clean(a))
        except SystemExit as e:
            print(e)
