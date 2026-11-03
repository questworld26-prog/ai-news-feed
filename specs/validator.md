# Deterministic & Semantic Validation Specifications (`VALID`)

Formal specifications defining numerical fabrication verification, proper-noun entity gating, and keyword overlap requirements.

---

## VALID-001: Deterministic Numerical Fabrication Detection

If a candidate summary contains numbers, percentages, or metrics absent from the source article, then the system shall flag the summary as fabricated and abort before calling neural SLM checkers.

Acceptance Criteria:
- AC-VALID-001.1: Executes an exact set-difference check comparing numerical tokens and percentages between summary and source text.
- AC-VALID-001.2: Returns explicit warning strings detailing all ungrounded numbers when fabrication is detected.

---

## VALID-002: Unanchored Proper-Noun & Entity Detection

If a candidate summary introduces capitalized named entities (companies, models, organizations) not present in the source article or common stopword whitelist, then the system shall reject the summary.

Acceptance Criteria:
- AC-VALID-002.1: Identifies and flags capitalized words or model names in the summary that do not appear in the source text.
- AC-VALID-002.2: Permits legitimate sentence-starting capitalized words and common standard abbreviations present on the whitelist.

---

## VALID-003: Lexical Keyword Overlap Floor

When validating a candidate summary, the system shall compute token overlap against source keywords and reject any summary falling below the configured threshold.

Acceptance Criteria:
- AC-VALID-003.1: Rejects candidate summaries with keyword overlap score strictly below 0.35.
- AC-VALID-003.2: Computes lexical overlap after normalizing tokens, removing English stopwords, and stripping punctuation.

---

## VALID-004: Hybrid System 1 (LAYA) & System 2 (Ollama) Semantic Fact-Checking

When deterministic lexical and numerical pre-gates pass, the system shall evaluate semantic entailment using the LAYA System 1 pre-gate and escalate ambiguous cases to the System 2 Ollama `llm_fact_check` auditor, failing closed on any exception.

Acceptance Criteria:
- AC-VALID-004.1: High-confidence grounded summaries fast-pass via `fact_check_pregate`, high-confidence hallucinations fast-fail, and disabled/unavailable LAYA falls back safely.
- AC-VALID-004.2: System 2 `llm_fact_check` parses structured `FactCheckResponse` verdicts and fails closed (`passed=False`) if the local LLM request times out or raises an exception.


