"""
Unit tests for the Quality Tracker Web Dashboard server and REST API.
Verifies static UI rendering, REST endpoints, and human feedback workflows.
"""

from __future__ import annotations

import json
import threading
import urllib.request
from collections.abc import Generator
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import pytest

from quality_dashboard import DashboardRequestHandler, QualityTracker


@pytest.fixture
def test_dashboard_server(tmp_path: Path) -> Generator[str, None, None]:
    """Launch an ephemeral Dashboard server on a random open port for testing."""
    db_path = tmp_path / "test_quality.db"
    tracker = QualityTracker(db_path)

    # Seed sample run
    sample_stories = [
        {
            "title": "Agentic Pipeline Testing",
            "link": "https://example.com/agent-test",
            "summary": "Evaluation of agent reliability.",
            "source": "AI Research",
            "extra_metadata": {"summary_status": "success", "keyword_overlap": 0.85, "retry_count": 1},
        }
    ]
    tracker.log_run(
        run_id="run_dashboard_test_1",
        run_date="2026-11-03",
        git_commit="abc1234",
        models_used={"curation": "phi4-mini:3.8b"},
        theme="practitioner_radar",
        strategy="auto",
        total_duration_s=42.5,
        phase3_duration_s=21.0,
        phase3_mem_delta_mb=12.0,
        phase3_mem_rss_mb=256.0,
        stories=sample_stories,
        audio_script="Welcome to the briefing.",
        audio_script_target=750,
        factcheck_passed=True,
        factcheck_retries=0,
    )

    class CustomHandler(DashboardRequestHandler):
        def __init__(self, *args, **kwargs):
            self.tracker = tracker
            super(DashboardRequestHandler, self).__init__(
                *args, directory=str(Path(__file__).parent.parent / "src" / "quality_dashboard"), **kwargs
            )

    server = ThreadingHTTPServer(("127.0.0.1", 0), CustomHandler)
    host, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    base_url = f"http://{host}:{port}"
    try:
        yield base_url
    finally:
        server.shutdown()
        server.server_close()


# [verifies: DASH-001/AC-DASH-001.1]
def test_serve_dashboard_ui_returns_200(test_dashboard_server: str) -> None:
    """Verify that root GET / serves quality_dashboard.html with status 200."""
    req = urllib.request.Request(f"{test_dashboard_server}/")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        assert "text/html" in resp.headers.get("Content-Type", "")
        content = resp.read().decode("utf-8")
        assert "<title>AI News Voice Feed — Quality & Telemetry Dashboard</title>" in content


# [verifies: DASH-001/AC-DASH-001.2]
def test_dashboard_server_cli_binding_parameters() -> None:
    """Verify that run_server accepts custom port and host parameters."""
    import inspect

    from quality_dashboard import run_server

    sig = inspect.signature(run_server)
    assert "port" in sig.parameters
    assert "host" in sig.parameters
    assert sig.parameters["port"].default == 8765
    assert sig.parameters["host"].default == "127.0.0.1"


# [verifies: DASH-002/AC-DASH-002.1]
def test_get_api_runs_returns_run_list(test_dashboard_server: str) -> None:
    """Verify that GET /api/runs returns a sorted list of execution runs."""
    req = urllib.request.Request(f"{test_dashboard_server}/api/runs")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        data = json.loads(resp.read().decode("utf-8"))
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["run_id"] == "run_dashboard_test_1"
        assert data[0]["theme"] == "practitioner_radar"


# [verifies: DASH-002/AC-DASH-002.2]
def test_get_api_run_detail_returns_story_breakdown(test_dashboard_server: str) -> None:
    """Verify that GET /api/runs/<run_id> returns comprehensive per-story breakdown."""
    req = urllib.request.Request(f"{test_dashboard_server}/api/runs/run_dashboard_test_1")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        data = json.loads(resp.read().decode("utf-8"))
        assert data["run_id"] == "run_dashboard_test_1"
        assert len(data["stories"]) == 1
        assert data["stories"][0]["story_domain"] == "example.com"
        assert data["stories"][0]["summary_status"] == "success"


# [verifies: DASH-003/AC-DASH-003.1]
def test_post_api_review_updates_rating(test_dashboard_server: str) -> None:
    """Verify that POST /api/runs/<run_id>/review records human rating and comment."""
    payload = json.dumps({"rating": 5, "comment": "Outstanding factual accuracy!"}).encode("utf-8")
    req = urllib.request.Request(
        f"{test_dashboard_server}/api/runs/run_dashboard_test_1/review",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "ok"
        assert data["rating"] == 5

    # Verify updated detail
    detail_req = urllib.request.Request(f"{test_dashboard_server}/api/runs/run_dashboard_test_1")
    with urllib.request.urlopen(detail_req) as resp:
        detail = json.loads(resp.read().decode("utf-8"))
        assert detail["human_rating"] == 5
        assert detail["human_comment"] == "Outstanding factual accuracy!"


# [verifies: DASH-003/AC-DASH-003.2]
def test_post_api_promote_handles_golden_promotion(test_dashboard_server: str) -> None:
    """Verify that POST /api/runs/<run_id>/stories/<idx>/promote triggers promotion."""
    payload = json.dumps({"correction": "Correction text", "notes": "Test notes"}).encode("utf-8")
    req = urllib.request.Request(
        f"{test_dashboard_server}/api/runs/run_dashboard_test_1/stories/0/promote",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with patch.object(
        QualityTracker,
        "promote_story_to_golden",
        return_value={"status": "ok", "case_id": "hitl_run_dashboard_test_1_0", "total_cases": 1},
    ) as mock_promote:
        with urllib.request.urlopen(req) as resp:
            assert resp.status == HTTPStatus.OK
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "ok"
            assert data["case_id"] == "hitl_run_dashboard_test_1_0"
            mock_promote.assert_called_once()
