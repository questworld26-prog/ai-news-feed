"""
Quality Tracker Web Dashboard Server.
Serves an interactive dashboard and REST JSON API on localhost:8765 to monitor
digest quality trends, failure rates, audio script metrics, and submit human reviews.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

# Add src to sys.path so we can import quality_tracker
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from quality_tracker import QualityTracker  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("quality_dashboard")

DASHBOARD_HTML_PATH = REPO_ROOT / "eval" / "quality_dashboard.html"


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    """Handles REST API endpoints and dashboard UI serving."""

    def __init__(self, *args, **kwargs):
        self.tracker = QualityTracker(REPO_ROOT / "eval" / "quality.db")
        super().__init__(*args, directory=str(REPO_ROOT / "eval"), **kwargs)

    def _send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Root route: serve quality_dashboard.html
        if path in ("/", "/index.html", "/dashboard"):
            if not DASHBOARD_HTML_PATH.exists():
                self.send_error(HTTPStatus.NOT_FOUND, "quality_dashboard.html not found.")
                return
            html_bytes = DASHBOARD_HTML_PATH.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)
            return

        # API: /api/summary
        if path == "/api/summary":
            summary = self.tracker.get_summary()
            self._send_json(summary)
            return

        # API: /api/runs
        if path == "/api/runs":
            limit = int(query.get("limit", [100])[0])
            theme = query.get("theme", [None])[0]
            git_commit = query.get("git_commit", [None])[0]
            runs = self.tracker.get_runs(limit=limit, theme=theme, git_commit=git_commit)
            self._send_json(runs)
            return

        # API: /api/runs/<run_id>
        match_run = re.match(r"^/api/runs/([^/]+)$", path)
        if match_run:
            run_id = match_run.group(1)
            run_detail = self.tracker.get_run_detail(run_id)
            if not run_detail:
                self._send_json({"error": f"Run '{run_id}' not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._send_json(run_detail)
            return

        # Fallback to standard static file server
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        # Read JSON body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        # API: /api/runs/<run_id>/review
        match_review = re.match(r"^/api/runs/([^/]+)/review$", path)
        if match_review:
            run_id = match_review.group(1)
            rating = payload.get("rating")
            comment = payload.get("comment", "")
            if rating is not None:
                try:
                    rating = int(rating)
                    if rating < 1 or rating > 5:
                        rating = None
                except (ValueError, TypeError):
                    rating = None

            ok = self.tracker.update_review(run_id, rating, comment)
            if ok:
                self._send_json({"status": "ok", "run_id": run_id, "rating": rating, "comment": comment})
            else:
                self._send_json({"error": "Run not found or update failed"}, status=HTTPStatus.NOT_FOUND)
            return

        # API: /api/backfill
        if path == "/api/backfill":
            out_dir = REPO_ROOT / "output"
            added = self.tracker.backfill_from_markdown_files(out_dir)
            self._send_json({"status": "ok", "backfilled": added})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found.")


def run_server(port: int = 8765, host: str = "127.0.0.1") -> None:
    # Pre-backfill historical files if quality.db is empty
    tracker = QualityTracker(REPO_ROOT / "eval" / "quality.db")
    stats = tracker.get_summary()
    if stats["total_runs"] == 0:
        added = tracker.backfill_from_markdown_files(REPO_ROOT / "output")
        logger.info(f"Initialized quality DB with {added} backfilled historical runs.")

    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, DashboardRequestHandler)
    print("\n" + "=" * 65)
    print(f"🚀 AI News Voice Feed — Quality Tracker Dashboard running at:")
    print(f"👉 http://{host}:{port}/")
    print("=" * 65 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard server...")
        httpd.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve Quality Tracker Dashboard")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on (default: 8765)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP (default: 127.0.0.1)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
