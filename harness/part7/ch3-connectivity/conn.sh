#!/bin/sh
# Connectivity verify (BROWSER-FUNCTIONAL-0 C1–C7): each route through `omni-render page` (broker + locked-down page process).
# Needs server.py on :8771. Prints PASS/FAIL per route against the expected page title; exit 1 on any FAIL.
BIN=${BIN:-<workspace>/projects/omni-render-browser/target/release/omni-render}
H=http://127.0.0.1:8771
fails=0
check() { # route expected-title-substring max-seconds
  s=$(date +%s.%N)
  t=$(timeout 60 "$BIN" page "$H$1" 2>/dev/null | grep '^meta' | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()[5:]).get("title",""))' 2>/dev/null)
  e=$(date +%s.%N)
  d=$(echo "$e - $s" | bc)
  ok=FAIL
  case "$t" in *"$2"*) [ "$(echo "$d < $3" | bc)" = 1 ] && ok=PASS ;; esac
  [ $ok = FAIL ] && fails=$((fails + 1))
  printf '%-5s %-14s %5.2fs  want %-16s got %s\n' $ok "$1" "$d" "$2" "$t"
}
check /gzip        GZIP-OK          5
check /chunked     CHUNKED-OK       5
check /redirect/3  REDIRECT-OK      5
check /redirect/7  REDIRECT-OK      5
check /404         NOTFOUND-PAGE    5
check /500         SERVER-ERROR     5
check /204         ""               3
check /setcookie   COOKIE-OK        5
check /latin1      "café-LATIN1"    5
check /close       NOLEN-CLOSE-OK   5
check /jscookie    "JSC:srv=2; js=1" 5
check /file.pdf    file.pdf         5
check /plain       plain            5
exit $fails
