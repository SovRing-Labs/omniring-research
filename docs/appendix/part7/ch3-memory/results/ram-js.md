# BROWSER-BODY-0 step 7 — peak memory, omni-ui web vs Firefox (one page per cold start)

Firefox: `Mozilla Firefox 156.0.1`, new empty profile, `--headless --no-remote`, 15 s.
omni-ui web: `omni-ui script web` (broker + locked-down page process), open + hold 5 s, headless; page scripts ON (jsi).
Score: peak over the run of the summed PSS (and RSS) of every process in the browser's tree, sampled every 0.2 s (tools/ram_bench.py).

| Page | omni PSS MB | Firefox PSS MB | ratio | omni RSS MB | Firefox RSS MB | procs omni / ff |
|---|---|---|---|---|---|---|
| https://en.wikipedia.org/wiki/Ternary_numeral_system | 30.4 | 758.6 | 4.0 % | 40.9 | 1552.5 | 2 / 13 |
| https://en.wikipedia.org/wiki/Moscow | 56.8 | 826.8 | 6.9 % | 67.3 | 1628.4 | 2 / 13 |
| https://doc.rust-lang.org/book/ch08-02-strings.html | 38.8 | 753.1 | 5.2 % | 49.1 | 1550.2 | 2 / 13 |
| https://peps.python.org/pep-0008/ | 43.4 | 704.4 | 6.2 % | 54.0 | 1493.2 | 2 / 13 |
| https://html.duckduckgo.com/html/?q=ternary+numeral+system | 19.1 | 751.0 | 2.5 % | 29.3 | 1534.2 | 2 / 13 |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 37.4 | 747.6 | 5.0 % | 47.9 | 1515.9 | 2 / 13 |
| https://news.ycombinator.com/ | 19.3 | 691.2 | 2.8 % | 29.4 | 1477.0 | 2 / 16 |
| https://lwn.net/ | 19.0 | 739.3 | 2.6 % | 29.6 | 1526.0 | 2 / 13 |
| https://wiki.archlinux.org/title/Systemd | 26.7 | 736.6 | 3.6 % | 37.2 | 1507.9 | 2 / 13 |
| https://text.npr.org/ | 18.0 | 715.1 | 2.5 % | 28.2 | 1497.2 | 2 / 13 |

**Total PSS: omni 308.8 MB vs Firefox 7423.6 MB = 4.2 %** (bar: ≤ 25 %).
