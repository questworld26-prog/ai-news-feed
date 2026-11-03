# Audio Monologue & Speech Synthesis Specifications (`AUDIO`)

Formal specifications defining audio story exclusion, sentence-boundary fallback protection, acoustic script sanitization, and local Metal TTS voice synthesis.

---

## AUDIO-001: Graceful Audio Story Degradation

If a story fails Level 2 summary validation, then the system shall exclude that story from spoken audio monologue generation while retaining it in the written Markdown digest.

Acceptance Criteria:
- AC-AUDIO-001.1: Filters out failed fallback stories from verified_audio_stories before CGAP plan compilation and monologue generation.
- AC-AUDIO-001.2: Prevents planner deadlock and acoustic speculation on unverified topics while preserving the written story link.

---

## AUDIO-002: Clean Sentence-Boundary Fallback Protection

If generating fallback excerpts or audio text, the system shall truncate text exclusively at complete sentence boundaries.

Acceptance Criteria:
- AC-AUDIO-002.1: Truncates fallback excerpts at complete sentence punctuation without cutting off mid-word or mid-clause.
- AC-AUDIO-002.2: Emits a clean standard disclaimer sentence when no grammatical sentence boundary exists within the character limit.

---

## AUDIO-003: Spoken Monologue Script Sanitization

When preparing monologue text for acoustic voice synthesis, the system shall strip raw URLs, markdown syntax, brackets, and theatrical filler words.

Acceptance Criteria:
- AC-AUDIO-003.1: Removes markdown links, bare URLs, bold and italic asterisks, brackets, and code paths from the script.
- AC-AUDIO-003.2: Strips dramatic theatrical preambles and conversational throat-clearing filler.

---

## AUDIO-004: Metal-Accelerated TTS Synthesis & Chunking

The system shall synthesize 24kHz audio using Kokoro-mlx with automatic text chunking capped at 150 words per chunk on Apple Silicon Metal acceleration.

Acceptance Criteria:
- AC-AUDIO-004.1: Partitions the sanitized monologue into sequential chunks capped at 150 words without breaking sentences.
- AC-AUDIO-004.2: Synthesizes high-fidelity 24kHz audio WAV files on Apple Silicon Metal acceleration.

