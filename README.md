# AI News Daily Voice Briefing Pipeline 🎙️

An automated, local daily AI news briefing pipeline. Uses theme-driven story selection across curated RSS feeds, generates tailored briefing digests and spoken monologues using local LLMs (via Ollama), synthesizes high-quality audio locally (`kokoro-mlx`), and dispatches formatted summaries and audio briefings directly to Telegram.

---

## 💻 Command Line Usage & Options

### CLI Usage

```text
usage: uv run python src/generate_news_digest.py [-h] [--config CONFIG] [--dry-run] [--skip-tts] [--all-themes] [--force]

AI News Daily Voice Briefing Pipeline

options:
  -h, --help       show this help message and exit
  -c, --config     Path to configuration file (default: config.toml)
  --dry-run        Fetch and generate script only; skip TTS synthesis and Telegram dispatch
  --skip-tts       Skip audio synthesis and dispatch only the markdown text digest to Telegram
  --all-themes     Generate a full digest for all 4 themes in dry-run mode (saved to output/YYYY-MM-DD_all_themes.md)
  --force          Force execution even on weekends
```

### Testing & Quality Verification

Run the full evaluation test suite (Golden Dataset, HHH Guardrails, and Regex rules):
```bash
uv run python -m pytest tests/ -v
```

*Note: Multi-layer evaluation checks Structural Regex (`## [Title](URL)`), HHH Guardrails (Helpful, Honest, Harmless), and LLM-as-a-Judge pass rates automatically on every run.*

---

## ⚡ Architecture & Key Features

- **Package & Runtime Management**: Managed strictly with `uv` and Python 3.11.
- **Local & Private Execution**: Sequential processing requiring zero external paid API subscriptions.
- **Randomized Theme Selection**: Automatically selects one of four engineering lenses daily:
  - 🧭 **Practitioner's Radar**: Production deployment patterns, MLOps, inference optimization, and engineering architecture.
  - 🏛️ **Executive Lens**: Strategic moves, industry risks, enterprise shifts, safety, and regulation.
  - 🔨 **Builder's Digest**: Concrete tools, open-source libraries, local AI, and developer tooling.
  - 🔭 **Innovation Scout**: Cross-disciplinary AI breakthroughs in science, biology, robotics, and creative domains.
- **Source Diversity & Filtering**:
  - Enforces a cap of 2 stories per single RSS source per briefing.
  - Applies fuzzy title deduplication (`difflib.SequenceMatcher`) to prevent repetitive coverage.
  - Applies negative keyword and quote-post filters to keep content technical and hype-free.
- **Three-Stage LLM Pipeline & Multi-Layer Evaluation**:
  1. **Curation**: Local LLM evaluates candidate stories against the active theme.
  2. **Digest & Script Generation**: Produces a rich Markdown briefing with embedded title links (`## [Title](URL)`) and a conversational monologue script (~750 words).
  3. **Multi-Layer Validation & HHH Guardrails**: An independent LLM judge, Regex checker, and HHH (Helpful, Honest, Harmless) audit engine verify every output against raw source text.
- **Local TTS**: Synthesizes natural spoken audio using `kokoro-mlx`.
- **Telegram Dispatch**: Delivers formatted summaries and WAV audio files via Telegram Bot API (handles 50MB file splitting automatically).

---

## 📂 Project Structure

```
AI_news_voice_feed/
├── config.toml                   # Central configuration (themes, RSS sources, schedule, voice, LLM)
├── pyproject.toml                # Project metadata & dependencies
├── .env.example                  # Environment template for Telegram credentials
├── .gitignore                    # Local storage ignore rules
├── launchd/
│   └── com.aibriefing.daily.plist # macOS LaunchAgent configuration
├── output/                       # Generated audio (.wav) and markdown (.md) briefings
├── src/
│   ├── generate_news_digest.py   # Main CLI entrypoint & orchestrator
│   ├── news_fetcher.py           # RSS aggregation, cleaning, scoring & filtering
│   ├── briefing_generator.py     # LLM story curation, markdown digest & monologue generator
│   ├── notifier.py               # Local TTS synthesis & Telegram dispatch
│   ├── validator.py              # Anti-hallucination validation module
│   └── evaluator.py              # Evaluation harness (Regex, HHH Guardrails, LLM-as-a-Judge)
└── tests/                        # Golden dataset, HHH guardrails, and accuracy test suite
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
- **uv**: Python package installer and virtualenv manager.
- **Ollama**: Running locally with your configured model:
  ```bash
  ollama pull phi4-mini:3.8b
  ollama pull qwen2.5:3b
  ```

### 2. Configure Environment Secrets
Copy `.env.example` to `.env` and fill in your Telegram credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"
```

### 3. Configuration (`config.toml`)
Customize themes, RSS feed URLs, model tags, and schedule settings in `config.toml`:
- `schedule.weekdays_only`: Restricts automatic runs to Monday–Friday (default: `true`).
- `feeds.max_stories`: Number of top stories selected per briefing (default: `5`).
- `llm.model`: Main generation LLM (default: `"phi4-mini:3.8b"`).
- `testing.test_model`: Anti-hallucination judge LLM (default: `"qwen2.5:3b"`).

---

## ⏰ Scheduled Automation (`launchd`)

To run the briefing automatically on a schedule:

1. Copy the plist to LaunchAgents:
   ```bash
   cp launchd/com.aibriefing.daily.plist ~/Library/LaunchAgents/
   ```
2. Load and register the service:
   ```bash
   launchctl load -w ~/Library/LaunchAgents/com.aibriefing.daily.plist
   ```
3. Test trigger immediately:
   ```bash
   launchctl start com.aibriefing.daily
   ```
