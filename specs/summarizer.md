# Story Summarization & Extractive Anchoring Specifications (`SUMM`)

Formal specifications defining extractive quote anchoring, two-sentence summary constraints, feedback retry loops, and fail-closed fallback behavior.

---

## SUMM-001: Extractive Quote Anchoring via Schema Decoding

When generating a story summary, the system shall constrain decoding to a structured Pydantic schema requiring 2 to 3 verbatim sentences extracted directly from the source before composing the summary text.

Acceptance Criteria:
- AC-SUMM-001.1: Forces Ollama decoding into the StorySummaryResponse schema containing direct_quotes and summary fields.
- AC-SUMM-001.2: Validates that direct_quotes contains between 2 and 3 non-empty verbatim quotes from the source.

---

## SUMM-002: Two-Sentence Summary Constraint

The system shall constrain the final written story summary to exactly two informative, positive-framed sentences synthesizing only the extracted quotes.

Acceptance Criteria:
- AC-SUMM-002.1: Asserts that the generated summary consists of exactly two sentences using sentence boundary detection.
- AC-SUMM-002.2: Restricts summary vocabulary strictly to facts, benchmarks, and entities present in the extracted quotes.

---

## SUMM-003: Validation Retry Loop with Targeted Feedback

If summary validation fails, the system shall inject the specific validation failure reason as a feedback prompt and request a regenerated summary up to three total attempts.

Acceptance Criteria:
- AC-SUMM-003.1: Injects CORRECTION REQUIRED followed by the specific failure reason into the regeneration prompt.
- AC-SUMM-003.2: Re-executes generation up to a maximum of three total attempts before declaring failure.

---

## SUMM-004: Fail-Closed Unverified Story Fallback

If a story summary fails validation across all three attempts, the system shall safely fall back to a standardized warning badge with the original source link rather than publishing unverified text.

Acceptance Criteria:
- AC-SUMM-004.1: Emits the standardized fallback badge warning with the verified original article URL in the markdown digest.
- AC-SUMM-004.2: Suppresses all unverified or hallucinated LLM text from appearing in the published output.

