"""
Quality Dashboard & Telemetry Package.
Provides SQLite run tracking, human review collection, golden dataset promotion,
and an interactive HTTP dashboard with REST API.
"""

from __future__ import annotations

from quality_dashboard.quality_tracker import (
    QualityTracker,
    extract_domain,
    get_current_git_commit,
    parse_summary_markdown,
)
from quality_dashboard.serve_dashboard import DashboardRequestHandler, run_server

__all__ = [
    "DashboardRequestHandler",
    "QualityTracker",
    "extract_domain",
    "get_current_git_commit",
    "parse_summary_markdown",
    "run_server",
]
