"""
LAYA System 1 Decision Engine for AI News Voice Briefing Pipeline.
Provides ultra-low-latency, single-pass decision-making for:
- Option 1: Fast Theme Curation & Story Pre-Ranking
- Option 2: Semantic Fact-Checking & Hallucination Pre-Gate
- Option 4: Semantic Hype & PR Pre-Filter
- Option 5: Story-Driven Dynamic Theme Routing
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from story import Story

logger = logging.getLogger("ai_briefing")

_laya_lock = threading.Lock()
_laya_agent = None
_laya_initialized = False


class LayaDecisionEngine:
    """Manages local LAYA System 1 model inference and decision routing."""

    def __init__(self, model_id: str = "convaiinnovations/laya", device: str = "cpu"):
        self.model_id = model_id
        self.device = device
        self._agent = None

    def load_agent(self) -> Any:
        """Lazily initialize and cache the LAYA decision agent."""
        global _laya_agent, _laya_initialized
        if _laya_agent is not None:
            return _laya_agent

        with _laya_lock:
            if _laya_agent is not None:
                return _laya_agent

            try:
                import laya  # type: ignore

                logger.info(f"Loading LAYA System 1 decision agent ({self.model_id}) on {self.device}...")
                _laya_agent = laya.load(self.model_id, device=self.device)
                _laya_initialized = True
                logger.info("LAYA System 1 agent loaded successfully.")
                return _laya_agent
            except Exception as exc:
                logger.warning(f"Failed to load LAYA agent ({exc}). Falling back to heuristics.")
                _laya_initialized = False
                return None

    @classmethod
    def is_enabled(cls, config: dict[str, Any] | None) -> bool:
        """Check if LAYA integration is globally enabled in config."""
        if not config:
            return True
        return bool(config.get("laya", {}).get("enabled", True))

    def filter_hype(
        self, title: str, summary: str, config: dict[str, Any] | None = None
    ) -> tuple[bool, float, str]:
        """
        Option 4: Semantic Hype & PR Pre-Filter.
        Classifies incoming RSS feed items into technical substance vs promotional hype.
        Returns:
            (is_hype: bool, confidence: float, reasoning: str)
        """
        agent = self.load_agent()
        if agent is None:
            return False, 0.0, "LAYA disabled or unavailable"

        try:
            state = {
                "title": title[:300],
                "summary": summary[:600] if summary else "",
            }
            questions = {
                "quality_category": {
                    "type": "choice",
                    "instructions": "Is this article substantive technical AI engineering/research or promotional hype/PR?",
                    "criteria": {
                        "technical": "Substantive technical engineering, open-source code/tools, architecture, benchmarks, or scientific breakthroughs",
                        "hype": "Marketing fluff, corporate promotional PR, fundraising/valuation speculation, crypto-shilling, or vague buzzwords",
                    },
                }
            }
            raw = agent.system_one(state=state, questions=questions)
            ans = raw.get("answers", {}).get("quality_category", {})
            choice = ans.get("choice", "technical")
            conf = float(ans.get("answer_confidence", ans.get("confidence", 0.5)))

            # If LAYA is confident it's hype, flag it for rejection
            is_hype = choice == "hype" and conf >= 0.60
            reason = f"LAYA System 1: {choice} (confidence {conf:.1%})"
            return is_hype, conf, reason
        except Exception as exc:
            logger.debug(f"LAYA filter_hype failed ({exc}). Passing story through.")
            return False, 0.0, f"Error: {exc}"

    def fact_check_pregate(
        self,
        source_text: str,
        generated_summary: str,
        config: dict[str, Any] | None = None,
    ) -> tuple[bool | None, float, str]:
        """
        Option 2: Semantic Fact-Checking & Hallucination Pre-Gate.
        Performs single-pass semantic entailment between source text and generated summary.
        Returns:
            (passed: bool | None, confidence: float, reasoning: str)
            - True: Instant PASS (high confidence grounded, bypass slow System 2 LLM audit)
            - False: Instant FAIL (high confidence hallucination, fail fast for retry)
            - None: Ambiguous / borderline (escalate to System 2 Ollama audit)
        """
        agent = self.load_agent()
        if agent is None:
            return None, 0.0, "LAYA disabled or unavailable"

        laya_cfg = (config or {}).get("laya", {})
        pass_thresh = float(laya_cfg.get("fact_check_pass_threshold", 0.85))
        fail_thresh = float(laya_cfg.get("fact_check_fail_threshold", 0.85))

        try:
            state = {
                "source_text": source_text[:2000],
                "generated_summary": generated_summary[:800],
            }
            questions = {
                "is_grounded": {
                    "type": "choice",
                    "instructions": "Is the generated summary factually grounded in the source text without fabricated numbers or unanchored claims?",
                    "criteria": {
                        "grounded": "Every single claim, entity, and figure in the summary is directly supported by the source text",
                        "hallucinated": "Contains fabricated numbers, external entities, or claims contradicted or not mentioned in source text",
                    },
                }
            }
            raw = agent.system_one(state=state, questions=questions)
            ans = raw.get("answers", {}).get("is_grounded", {})
            choice = ans.get("choice", "grounded")
            conf = float(ans.get("answer_confidence", ans.get("confidence", 0.5)))

            if choice == "grounded" and conf >= pass_thresh:
                return True, conf, f"LAYA System 1: High confidence grounded ({conf:.1%}) -> Fast Pass"
            elif choice == "hallucinated" and conf >= fail_thresh:
                return False, conf, f"LAYA System 1: High confidence hallucination detected ({conf:.1%}) -> Fast Fail"
            else:
                return (
                    None,
                    conf,
                    f"LAYA System 1: Ambiguous ({choice} {conf:.1%}) -> Escalate to System 2 LLM Audit",
                )
        except Exception as exc:
            logger.debug(f"LAYA fact_check_pregate failed ({exc}). Escalating to System 2.")
            return None, 0.0, f"Error: {exc}"

    def rank_candidates_for_theme(
        self,
        candidates: list[Story],
        theme_dict: dict[str, Any],
        config: dict[str, Any] | None = None,
        top_k: int = 7,
    ) -> list[Story]:
        """
        Option 1: Fast Theme Curation Pre-Ranking.
        Scores candidate stories against the theme definition to produce a high-signal shortlist
        before passing to Ollama CoT curation (reducing prompt context and inference time).
        """
        if len(candidates) <= top_k:
            return candidates

        agent = self.load_agent()
        if agent is None:
            # Fallback: rank by baseline score
            return sorted(candidates, key=lambda s: s.score, reverse=True)[:top_k]

        theme_name = theme_dict.get("name", "AI News")
        theme_desc = theme_dict.get("description", "")
        theme_tone = theme_dict.get("tone", "")

        scored_candidates: list[tuple[Story, float]] = []
        for s in candidates:
            try:
                state = {
                    "headline": s.title[:300],
                    "summary": s.summary[:500] if s.summary else "",
                }
                questions = {
                    "theme_fit": {
                        "type": "choice",
                        "instructions": f"Does this story fit the briefing theme '{theme_name}'?",
                        "criteria": {
                            "theme_aligned": f"Directly aligns with {theme_name}: {theme_desc}. Focus: {theme_tone}",
                            "off_topic": "Off-topic, non-technical policy/legal issues, or unaligned with this specific engineering domain",
                        },
                    }
                }
                raw = agent.system_one(state=state, questions=questions)
                ans = raw.get("answers", {}).get("theme_fit", {})
                choice = ans.get("choice", "theme_aligned")
                conf = float(ans.get("answer_confidence", ans.get("confidence", 0.5)))
                prob_rel = conf if choice == "theme_aligned" else (1.0 - conf)

                # Combined score: 70% LAYA semantic theme alignment + 30% recency/popularity
                combined = (0.70 * prob_rel) + (0.30 * s.score)
                scored_candidates.append((s, combined))
            except Exception as exc:
                logger.debug(f"LAYA theme score failed for '{s.title[:40]}': {exc}")
                scored_candidates.append((s, s.score))

        # Sort descending by combined score
        scored_candidates.sort(key=lambda pair: pair[1], reverse=True)
        shortlist = [pair[0] for pair in scored_candidates[:top_k]]
        logger.info(
            f"LAYA System 1 pre-ranking: pruned {len(candidates)} candidates down to top {len(shortlist)} for theme '{theme_name}'."
        )
        return shortlist

    def route_theme_from_stories(
        self,
        stories: list[Story],
        themes: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> tuple[str, dict[str, float]]:
        """
        Option 5: Story-Driven Dynamic Theme Routing.
        Evaluates incoming breaking headlines across the 4 configured themes and selects
        the theme with the strongest collective momentum/signal.
        Returns:
            (selected_theme_key: str, score_breakdown: dict[str, float])
        """
        if not themes:
            raise ValueError("No themes provided for routing.")

        theme_keys = list(themes.keys())
        if len(theme_keys) == 1:
            return theme_keys[0], {theme_keys[0]: 1.0}

        agent = self.load_agent()
        if agent is None or not stories:
            # Fallback to first theme
            return theme_keys[0], {k: 1.0 / len(theme_keys) for k in theme_keys}

        theme_criteria = {
            k: f"{v.get('name', k)}: {v.get('description', '')}. Focus: {v.get('tone', '')}"
            for k, v in themes.items()
        }

        # Initialize cumulative score per theme
        cumulative_scores: dict[str, float] = {k: 0.0 for k in theme_keys}

        # Sample top 10 stories to find today's news center of gravity
        sample_stories = stories[:10]
        for s in sample_stories:
            try:
                state = {
                    "headline": s.title[:300],
                    "summary": s.summary[:500] if s.summary else "",
                }
                questions = {
                    "theme_match": {
                        "type": "choice",
                        "instructions": "Which technical briefing theme best fits this story?",
                        "criteria": theme_criteria,
                    }
                }
                raw = agent.system_one(state=state, questions=questions)
                ans = raw.get("answers", {}).get("theme_match", {})
                probs = ans.get("probabilities", {})

                for k in theme_keys:
                    prob = float(probs.get(k, 0.0))
                    cumulative_scores[k] += prob
            except Exception as exc:
                logger.debug(f"LAYA theme routing evaluation error on story '{s.title[:40]}': {exc}")

        # Pick theme with highest score
        best_theme = max(cumulative_scores, key=lambda k: cumulative_scores[k])
        total = sum(cumulative_scores.values()) or 1.0
        normalized_scores = {k: round(v / total, 3) for k, v in cumulative_scores.items()}

        logger.info(
            f"LAYA System 1 Dynamic Theme Route: Selected '{themes[best_theme].get('name')}' (Signal distribution: {normalized_scores})"
        )
        return best_theme, normalized_scores


# Global engine instance
_engine_instance: LayaDecisionEngine | None = None


def get_laya_engine(config: dict[str, Any] | None = None) -> LayaDecisionEngine:
    """Get or create singleton LayaDecisionEngine."""
    global _engine_instance
    if _engine_instance is None:
        laya_cfg = (config or {}).get("laya", {})
        model_id = laya_cfg.get("model_id", "convaiinnovations/laya")
        device = laya_cfg.get("device", "cpu")
        _engine_instance = LayaDecisionEngine(model_id=model_id, device=device)
    return _engine_instance
