#!/bin/sh
# Real-site census through the browser's page process (broker + locked-down renderer, JS on). One page at a time.
BIN=<workspace>/projects/omni-render-browser/target/release/omni-render
OUT=${1:-census.jsonl}
: > "$OUT"
for u in \
  https://en.wikipedia.org/wiki/Balanced_ternary \
  https://news.ycombinator.com/ \
  https://old.reddit.com/r/rust/ \
  https://www.reddit.com/r/rust/ \
  https://github.com/rust-lang/rust \
  https://stackoverflow.com/questions/11227809 \
  https://developer.mozilla.org/en-US/docs/Web/JavaScript \
  https://docs.rs/serde/latest/serde/ \
  https://www.bbc.com/news \
  https://www.theguardian.com/international \
  https://arstechnica.com/ \
  https://lwn.net/ \
  https://www.nytimes.com/ \
  https://html.duckduckgo.com/html/?q=balanced+ternary \
  https://www.youtube.com/ \
  https://x.com/ \
  https://www.amazon.com/ \
  https://www.ebay.com/ \
  https://mail.google.com/ \
  https://www.google.com/search?q=balanced+ternary \
  https://maps.google.com/ \
  https://www.craigslist.org/ \
  https://weather.gov/ \
  https://www.gnu.org/ ; do
  t0=$(date +%s.%N)
  res=$(timeout 120 "$BIN" page "$u" 2>/tmp/claude-1000/census-err.txt | grep -E '^(meta|frame)' | tr '\n' '\t')
  rc=$?
  t1=$(date +%s.%N)
  err=$(grep -v -E 'PASS|landlock' /tmp/claude-1000/census-err.txt | tail -2 | tr '\n\t"' '   ' | cut -c1-300)
  python3 - "$u" "$res" "$t0" "$t1" "$err" >> "$OUT" <<'EOF'
import json, sys
u, res, t0, t1, err = sys.argv[1:]
meta = None; frame = ''
for part in res.split('\t'):
    if part.startswith('meta '):
        try: meta = json.loads(part[5:])
        except Exception: meta = {'raw': part[5:200]}
    elif part.startswith('frame'): frame = part
row = {'url': u, 'wall_s': round(float(t1) - float(t0), 2), 'frame': frame, 'stderr': err}
if meta:
    js = meta.get('js') or {}
    row.update({'title': meta.get('title', '')[:80], 'page_h': meta.get('page_h'), 'dom_nodes': meta.get('dom_nodes'), 'links': meta.get('links'),
                'layout_ms': round(meta.get('layout_ms') or 0), 'navigate': meta.get('navigate'), 'refresh': meta.get('refresh'),
                'js_ran': js.get('scripts_ran'), 'js_failed': js.get('scripts_failed'), 'js_parse_err': js.get('parse_errors'),
                'js_ms': js.get('ms'), 'js_budget': js.get('budget_spent'), 'js_kb': js.get('script_kb'), 'js_errors': [e[:120] for e in (js.get('errors') or [])][:8]})
else:
    row['failed'] = True
print(json.dumps(row))
EOF
done
echo DONE >> "$OUT.done"
