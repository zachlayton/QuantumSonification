"""Serve harmonic audition against the existing authoritative inspector engine."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen


def main():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_GET(self):
            try:
                if self.path.startswith('/api/'):
                    with urlopen('http://127.0.0.1:8767'+self.path, timeout=3) as response:
                        data=response.read();kind=response.headers.get('Content-Type','application/json')
                else:
                    name='harmonic-worklet.js' if self.path.split('?')[0]=='/harmonic-worklet.js' else 'harmonics.html'
                    data=Path(__file__).with_name(name).read_bytes()
                    kind='application/javascript' if name.endswith('.js') else 'text/html; charset=utf-8'
                self.send_response(200);self.send_header('Content-Type',kind)
                self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)))
                self.end_headers();self.wfile.write(data)
            except Exception as exc:
                self.send_error(502,str(exc))
    server=ThreadingHTTPServer(('127.0.0.1',8768),Handler)
    print('Harmonic string: http://127.0.0.1:8768 · source: localhost:8767',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


if __name__=='__main__':main()
