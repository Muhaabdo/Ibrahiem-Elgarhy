#!/usr/bin/env python3
"""Local preview server with the same clean URLs as the live site (/px -> px.html).

    python tools/serve.py          # then open http://localhost:8080/px
    python tools/serve.py 3000     # custom port
"""
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
os.chdir(ROOT)


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = super().translate_path(path)
        if not os.path.exists(p) and os.path.exists(p + ".html"):
            return p + ".html"
        return p

    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.exists("404.html"):
            body = open("404.html", "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    print(f"Serving {ROOT}\n  http://localhost:{PORT}/px\n  http://localhost:{PORT}/en/px\n  http://localhost:{PORT}/thank-you\nCtrl+C to stop.")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
