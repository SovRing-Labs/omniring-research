#!/usr/bin/env python3
"""Probe server for the omni-ui Web connectivity / JS intel (seat scratch, 2026-10-07)."""
import gzip, http.server, os, sys, time, json

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, 'requests.log')


class H(http.server.SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, fmt, *args):
        with open(LOG, 'a') as f:
            f.write(json.dumps({'t': time.time(), 'line': self.requestline, 'headers': dict(self.headers)}) + '\n')

    def send(self, code, body, ctype='text/html; charset=utf-8', extra=()):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        for k, v in extra:
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def page(self, title, body):
        return f'<!doctype html><html><head><title>{title}</title></head><body>{body}</body></html>'.encode()

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        data = self.rfile.read(n).decode(errors='replace')
        self.send(200, self.page('POSTED ' + data, f'<p>posted {data}</p>'))

    def do_GET(self):
        p = self.path
        if p == '/gzip':
            b = gzip.compress(self.page('GZIP-OK', '<p>gzip body</p>'))
            self.send(200, b, extra=[('Content-Encoding', 'gzip')])
        elif p == '/chunked':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
            for part in [b'<!doctype html><html><head><title>CHUNK', b'ED-OK</title></head><body>chunks</body></html>']:
                self.wfile.write(b'%x\r\n%s\r\n' % (len(part), part))
            self.wfile.write(b'0\r\n\r\n')
        elif p.startswith('/redirect/'):
            n = int(p.rsplit('/', 1)[1])
            loc = f'/redirect/{n-1}' if n > 1 else '/final'
            self.send(302, b'', extra=[('Location', loc)])
        elif p == '/final':
            self.send(200, self.page('REDIRECT-OK', '<p>final</p>'))
        elif p == '/404':
            self.send(404, self.page('NOTFOUND-PAGE', '<h1>Custom 404 page</h1>'))
        elif p == '/500':
            self.send(500, self.page('SERVER-ERROR-PAGE', '<h1>Server error page</h1>'))
        elif p == '/204':
            self.send_response(204)
            self.end_headers()
        elif p == '/setcookie':
            self.send(302, b'', extra=[('Location', '/needcookie'), ('Set-Cookie', 'sid=abc; Path=/')])
        elif p == '/needcookie':
            ok = 'sid=abc' in (self.headers.get('Cookie') or '')
            self.send(200, self.page('COOKIE-' + ('OK' if ok else 'MISSING'), ''))
        elif p == '/latin1':
            self.send(200, '<!doctype html><html><head><title>caf\xe9-LATIN1</title></head><body>caf\xe9</body></html>'.encode('latin-1'), ctype='text/html; charset=iso-8859-1')
        elif p == '/close':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(self.page('NOLEN-CLOSE-OK', ''))
            self.close_connection = True
        elif p == '/slow':
            time.sleep(20)
            self.send(200, self.page('SLOW-OK', ''))
        elif p == '/postform':
            self.send(200, self.page('POSTFORM', '<form method="post" action="/submit"><input name="q" value="hello"><button>Go</button></form>'))
        elif p == '/getform':
            self.send(200, self.page('GETFORM', '<form method="get" action="/final"><input name="q" value="hello"><button>Go</button></form>'))
        elif p == '/dataimg':
            import base64, struct, zlib
            raw = b''.join(b'\x00' + b'\xff\x00\x00' * 40 for _ in range(30))
            def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
            png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 40, 30, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
            self.send(200, self.page('DATAIMG', '<img id="i" src="data:image/png;base64,' + base64.b64encode(png).decode() + '">'))
        elif p == '/jscookie':
            self.send(200, self.page('JSCOOKIE', '<script>document.cookie="js=1; path=/"; document.title="JSC:" + document.cookie;</script>'),
                      extra=[('Set-Cookie', 'srv=2; Path=/'), ('Set-Cookie', 'hid=3; Path=/; HttpOnly')])
        elif p == '/file.pdf':
            self.send(200, b'%PDF-1.4\n%fake\n', ctype='application/pdf')
        elif p == '/plain':
            self.send(200, b'plain <text> body', ctype='text/plain; charset=utf-8')
        elif p == '/persist':
            self.send(200, self.page('PERSIST-SET', ''), extra=[('Set-Cookie', 'p=1; Max-Age=3600; Path=/'), ('Set-Cookie', 'sess=1; Path=/')])
        elif p == '/checkp':
            c = self.headers.get('Cookie') or ''
            self.send(200, self.page('CHECKP ' + ('p' if 'p=1' in c else '-') + ('s' if 'sess=1' in c else '-'), ''))
        elif p == '/headers':
            self.send(200, self.page('HEADERS', '<pre>' + str(dict(self.headers)) + '</pre>'))
        elif p == '/img':
            self.send(200, self.page('IMGS', ''.join(f'<p>{e}<img src="/static/t.{e}" alt="{e}-alt"></p>' for e in ['png', 'jpg', 'gif', 'webp', 'svg', 'avif'])))
        else:
            super().do_GET()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8771
    http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
