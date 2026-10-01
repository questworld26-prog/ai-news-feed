import sys
import time
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from telemetry import PipelineTracker


def test_pipeline_tracker_stage_recording():
    tracker = PipelineTracker()

    with tracker.track_stage("Test Ingestion Stage", {"sources": 5}) as stage:
        time.sleep(0.05)
        stage.set_metric("candidates_found", 12)

    assert len(tracker.records) == 1
    rec = tracker.records[0]
    assert rec.name == "Test Ingestion Stage"
    assert rec.duration_s >= 0.04
    assert rec.mem_end_mb > 0
    assert rec.metrics["sources"] == 5
    assert rec.metrics["candidates_found"] == 12


def test_pipeline_tracker_summary_dashboard(capsys):
    tracker = PipelineTracker()

    with tracker.track_stage("Stage 1"):
        time.sleep(0.01)

    with tracker.track_stage("Stage 2", {"items": 42}):
        time.sleep(0.01)

    tracker.print_summary_dashboard()
    # Ensure dashboard prints without raising any exceptions
    assert len(tracker.records) == 2
