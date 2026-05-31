#!/usr/bin/env python3
"""Serve the AI-University portal and generated artefacts.

Run from the repository root:

    python serve.py            # serves on http://localhost:8000
    python serve.py 9000       # custom port

Then open http://localhost:8000/web/ in your browser.

The server is rooted at the repository so that the portal under ``/web`` can
reach the generated ``/data`` and ``/content`` directories.
"""
from __future__ import annotations

import http.server
import os
import socketserver
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):  # quieter logging
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"AI-University portal: http://localhost:{port}/web/")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
