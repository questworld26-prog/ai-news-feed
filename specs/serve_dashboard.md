# Dashboard Server & REST API Specifications (`DASH`)

Formal specifications defining the local HTTP web server, static dashboard UI serving, and REST API endpoints.

---

## DASH-001: Local HTTP Dashboard & Static UI Serving

When launched via CLI, the system shall serve an interactive dashboard UI on a configurable host and port.

Acceptance Criteria:
- AC-DASH-001.1: Serves GET / returning quality_dashboard.html with status code 200.
- AC-DASH-001.2: Binds to user-specified port and host address passed via CLI arguments.

---

## DASH-002: REST JSON API for Telemetry & Run History

The system shall provide JSON REST API endpoints returning recent briefing runs and individual run details.

Acceptance Criteria:
- AC-DASH-002.1: Endpoint GET /api/runs returns a sorted JSON list of recent execution runs.
- AC-DASH-002.2: Endpoint GET /api/runs/<id> returns comprehensive per-story breakdown and script metrics for the requested run.

---

## DASH-003: Review & Promotion API Handlers

The system shall handle POST requests to submit human quality scores and trigger golden dataset promotions.

Acceptance Criteria:
- AC-DASH-003.1: Endpoint POST /api/review validates rating integer between 1 and 5 and updates SQLite tracker.
- AC-DASH-003.2: Endpoint POST /api/promote verifies story parameters and promotes entry into golden dataset.

