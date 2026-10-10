# BROWSER-BODY-0 step 7 — peak memory, omni-ui web vs Firefox (one page per cold start)

Firefox: `Mozilla Firefox 156.0.1`, new empty profile, `--headless --no-remote`, 15 s.
omni-ui web: `omni-ui script web` (broker + locked-down page process), open + hold 5 s, headless.
Score: peak over the run of the summed PSS (and RSS) of every process in the browser's tree, sampled every 0.2 s (tools/ram_bench.py).

| Page | omni PSS MB | Firefox PSS MB | ratio | omni RSS MB | Firefox RSS MB | procs omni / ff |
|---|---|---|---|---|---|---|
| https://en.wikipedia.org/wiki/Ternary_numeral_system | 22.3 | 721.3 | 3.1 % | 33.0 | 1583.2 | 2 / 13 |
| https://en.wikipedia.org/wiki/Moscow | 36.7 | 740.3 | 5.0 % | 47.4 | 1611.3 | 2 / 14 |
| https://doc.rust-lang.org/book/ch08-02-strings.html | 20.4 | 745.6 | 2.7 % | 30.8 | 1543.9 | 2 / 14 |
| https://peps.python.org/pep-0008/ | 19.6 | 715.6 | 2.7 % | 30.1 | 1503.8 | 2 / 16 |
| https://html.duckduckgo.com/html/?q=ternary+numeral+system | 18.1 | 735.5 | 2.5 % | 28.6 | 1518.3 | 2 / 13 |
| https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 21.5 | 782.8 | 2.7 % | 31.7 | 1580.9 | 2 / 13 |
| https://news.ycombinator.com/ | 17.0 | 673.6 | 2.5 % | 27.2 | 1407.8 | 2 / 16 |
| https://lwn.net/ | 17.7 | 729.9 | 2.4 % | 28.4 | 1516.0 | 2 / 13 |
| https://wiki.archlinux.org/title/Systemd | 20.8 | 756.7 | 2.7 % | 31.2 | 1548.8 | 2 / 13 |
| https://text.npr.org/ | 17.1 | 696.2 | 2.5 % | 27.2 | 1479.1 | 2 / 13 |

**Total PSS: omni 211.3 MB vs Firefox 7297.6 MB = 2.9 %** (bar: ≤ 25 %).
