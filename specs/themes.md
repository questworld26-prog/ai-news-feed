# Thematic Architecture & Routing Specifications (`THEME`)

Formal specifications defining the four editorial themes, dynamic breaking news routing, cooldown rotation, and multi-tier ingestion fallback.

---

## THEME-001: Four Curated Editorial Thematic Lenses

The system shall maintain four distinct editorial themes (Practitioner's Radar, Executive Lens, Builder's Digest, Innovation Scout), each defined with customized feed sources, tone guidelines, and hard filter exclusions.

Acceptance Criteria:
- AC-THEME-001.1: Loads four theme configurations containing distinct descriptions, tones, emojis, and source URL pools from config.toml.
- AC-THEME-001.2: Applies theme-specific negative keyword filters excluding marketing hype, fundraising rounds, and corporate PR fluff.

---

## THEME-002: Story-Driven Dynamic Theme Routing

When executed in automatic mode, the system shall sample breaking headlines across feeds, evaluate theme density in System 1, and dynamically route the briefing to the theme with the highest signal density.

Acceptance Criteria:
- AC-THEME-002.1: System 1 LAYA tallies breaking headlines against theme descriptors to compute momentum density scores.
- AC-THEME-002.2: Selects the theme with the highest story density score in sub-second CPU inference time.

---

## THEME-003: Thematic Diversity & Cooldown Rotation

The system shall maintain recent theme history across consecutive days to prevent topic starvation and apply a score penalty to yesterday's theme to guarantee diverse weekly coverage.

Acceptance Criteria:
- AC-THEME-003.1: Queries recently briefed themes from the SQLite history database.
- AC-THEME-003.2: Applies a cooldown penalty to the most recent theme during dynamic routing unless breaking headlines exceed the override threshold.

---

## THEME-004: Multi-Tier Ingestion & Theme Fallback

If the selected theme yields fewer than 5 candidate stories after 96h ingestion window and 168h staleness backoff, the system shall systematically evaluate alternative configured themes before terminating the run.

Acceptance Criteria:
- AC-THEME-004.1: Automatically falls back to the next highest-scoring theme when the candidate pool is starved.
- AC-THEME-004.2: Records the fallback theme and transition justification in execution telemetry.

---

## THEME-005: Theme Override & All-Themes Batch Mode

Where explicitly invoked via CLI flags, the system shall bypass dynamic routing to execute specific or all themes.

Acceptance Criteria:
- AC-THEME-005.1: The command line argument --theme forces execution of the exact specified theme key.
- AC-THEME-005.2: The command line argument --all-themes iterates sequentially across all four themes in dry-run batch mode.

