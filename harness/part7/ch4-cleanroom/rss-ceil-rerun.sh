#!/bin/sh
# re-run of tw job doctor-rss-ceil (2026-10-07 17:12:55) — check out the repo revisions in repro.json first; copies of its scripts are in files/
cd <workspace>/projects/omni-render
export NODE_USE_SYSTEM_CA=1
export PYTHONDONTWRITEBYTECODE=1
/usr/bin/time -v <workspace>/projects/omni-render/target/release/omni-render core --abc need --src <workspace>/projects/omni-render/src/layout.rs --needs <workspace>/projects/omni-render/results/doctor-runs/2026-10-06/abc/ff-synth/n-ceil.jsonl --build --ff
