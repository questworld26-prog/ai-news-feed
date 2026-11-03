---
name: AI_news_voice_feed-test-protocol
description: >-
  Defines the testing methodology, runner commands, test tiering, and isolation rules
  for AI_news_voice_feed. Enforced during [Gate 4] Test Suite Execution in release management.
---

# Test Protocol: AI_news_voice_feed

This skill defines the official testing process for **AI_news_voice_feed**.

## 1. Test Command & Execution
Execute tests via:
```bash
uv run pytest
```
*(Customize this command to match your project runner: e.g. `npm test`, `cargo test`, `go test ./...`)*

## 2. Test Execution Tiers
- **Fast Unit Tests**: Deterministic fast tests validating pure logic, schemas, and math. Must run in `< 5s`.
- **Integration Tests**: Tests database, file I/O, or local service boundaries.
- **Heavy / Live Inference (Opt-In)**: Heavy multi-model or network tests isolated from standard pre-commit runs.

## 3. Anti-Mirage Assertion & Traceability Rules
- Every `def test_*` function must carry a `# [verifies: REQ-ID/AC-ID]` annotation.
- All test assertions must verify deterministic outputs and exact numeric/factual anchors.
- Vacuous assertions (`assert result is not None`, `assert len(items) > 0`) are strictly forbidden.
