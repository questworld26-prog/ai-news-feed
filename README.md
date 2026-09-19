# AI News Daily Voice Briefing Pipeline 🎙️

A local, automated daily AI news briefing pipeline on macOS (Apple Silicon M1). Uses theme-driven story selection across curated RSS feeds, generates a tailored briefing digest and spoken monologue with local Ollama (`qwen2.5:3b`), synthesizes audio with Metal-accelerated `kokoro-mlx`, and delivers formatted briefs + audio directly to your private Telegram bot.

---

## ⚡ Architecture & Features

- **Package & Runtime Manager**: Managed strictly with `uv` and Python 3.11.
- **Hardware-Tailored**: Tuned for Apple Silicon M1 (8GB unified memory), running sequential chunked synthesis with zero heavy cloud API requirements.
- **Randomized Theme Selection & Per-Theme Sources**:
  Every day, the pipeline selects one of 4 curated engineering themes at random:
  - 🧭 **Practitioner's Radar**: Production deployment patterns, MLOps, inference optimization, and engineering architecture.
  - 🏛️ **Executive Lens**: Big strategic moves, industry risks, enterprise shifts, safety, and regulation.
  - 🔨 **Builder's Digest**: Concrete tools, open-source libraries, local AI, and developer tooling (Claude, Antigravity, Cursor, Copilot).
  - 🔭 **Innovation Scout**: Unexpected cross-disciplinary AI breakthroughs in science, biology, robotics, and creative domains.
- **Multi-Source Diversity & De-duplication**:
  - Enforces a maximum cap of 2 stories per single RSS source in candidate pools.
  - Employs fuzzy title de-duplication (`difflib.SequenceMatcher`) to prevent repetitive coverage.
  - Applies negative keyword filters (`funding round`, `valuation`, `series A/B`, etc.) to keep content strictly technical and hype-free.
- **Two-Stage Generation Pipeline**:
  1. **LLM Story Curation**: Ollama (`qwen2.5:3b` @ `temp=0.2`) evaluates the candidate pool against the chosen theme's audience and selects the top 5 stories.
  2. **Dedicated Digest & Script Generation**: Produces a rich markdown digest with source links and a natural, conversational monologue (~750 words) free of URLs or markdown artifacts.
- **Local TTS**: `kokoro-mlx` Metal acceleration using British male voice `bm_george` (configurable in `config.toml`).
- **Telegram Dispatch**: Delivers markdown summary with theme badges and WAV audio directly via Telegram Bot API (handles Telegram's 50MB file limit by automatically splitting large files if necessary).
- **Automation & Scheduling**: Configured for weekdays only (Monday through Friday) at 12:00 PM (Noon).

---

## 📂 Project Structure

```
AI_news_voice_feed/
├── config.toml                   # Centralized knobs: themes, per-theme sources, schedule, voice, model
├── pyproject.toml                # UV project configuration
├── .env.example                  # Environment secrets template
├── .gitignore                    # Git ignore for .env, output/, .venv
├── launchd/
│   └── com.aibriefing.daily.plist # macOS LaunchAgent configuration (12:00 PM)
├── output/                       # Local audio (.wav) & summary (.md) storage
├── src/
│   └── pipeline.py               # Complete end-to-end pipeline script
└── README.md
```

---

## 🚀 Setup Instructions

### 1. Prerequisites
- **uv**: Installed at `~/.local/bin/uv` (or install via `curl -LsSf https://astral.sh/uv/install.sh | sh`).
- **Ollama**: Running locally with `qwen2.5:3b`:
  ```bash
  ollama pull qwen2.5:3b
  ```

### 2. Configure Environment Secrets
Copy `.env.example` to `.env` and fill in your Telegram credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
TELEGRAM_CHAT_ID="987654321"
```
> *Tip: To find your Chat ID, message `@userinfobot` or `@RawDataBot` on Telegram.*

### 3. Tuning Configuration (`config.toml`)
You can freely customize:
- `schedule.weekdays_only`: Restricts automatic runs to Monday–Friday (default: `true`).
- `feeds.max_stories`: Number of top stories selected per briefing (default: `5`).
- `feeds.candidate_pool_size`: Size of pre-filtered candidate pool (default: `15`).
- `themes.*.sources`: RSS feed URLs for each theme.
- `tts.voice`: Voice name (default: `"bm_george"`).
- `tts.speed`: Speaking speed multiplier (default: `1.0`).
- `llm.model`: Ollama model tag (default: `"qwen2.5:3b"`).

---

## 🧪 Running the Pipeline

### Dry Run (Test Feeds & Script Generation)
Verify RSS feeds aggregation, theme selection, and Ollama generation without synthesizing audio or sending to Telegram:
```bash
uv run python src/pipeline.py --dry-run
```

### Comprehensive All-Themes Catch-up Mode
Generate a multi-section comprehensive briefing covering all 4 themes in one Markdown file (saved locally to `output/YYYY-MM-DD_all_themes.md`, without TTS or Telegram):
```bash
uv run python src/pipeline.py --all-themes
```

### Text-Only Run (Skip Audio Synthesis)
Test RSS fetch, Ollama script creation, and Telegram message dispatch without running TTS:
```bash
uv run python src/pipeline.py --skip-tts
```

### Full End-to-End Run
Run all stages (Fetch → Ollama → Kokoro TTS → Local Files → Telegram):
```bash
uv run python src/pipeline.py
```

Outputs will be saved in `output/`:
- `output/YYYY-MM-DD_<theme>_summary.md` (Markdown notes with links & spoken script)
- `output/YYYY-MM-DD_briefing.wav` (Native 24kHz 16-bit PCM WAV audio)

You can play the generated audio directly in macOS Terminal:
```bash
afplay output/*_briefing.wav
```

---

## ⏰ macOS Daily Automation (`launchd`)

To run the briefing automatically every weekday at 12:00 PM (Noon):

### 1. Copy the Plist to LaunchAgents
```bash
cp launchd/com.aibriefing.daily.plist ~/Library/LaunchAgents/
```

### 2. Load and Register the Agent
```bash
launchctl load -w ~/Library/LaunchAgents/com.aibriefing.daily.plist
```

### 3. Verify Registration
```bash
launchctl list | grep aibriefing
```

### 4. Test Triggering Immediately
```bash
launchctl start com.aibriefing.daily
```

### 5. Inspect Logs
```bash
tail -f ~/Library/Logs/com.aibriefing.daily.out.log
tail -f ~/Library/Logs/com.aibriefing.daily.err.log
```

To unload or disable the schedule later:
```bash
launchctl unload ~/Library/LaunchAgents/com.aibriefing.daily.plist
```
