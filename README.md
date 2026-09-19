# AI News Daily Voice Briefing Pipeline 🎙️

A local, automated daily AI news briefing pipeline on macOS (Apple Silicon M1). Fetches top AI headlines across curated RSS feeds, generates a conversational script using local Ollama (`qwen2.5:3b`), synthesizes audio locally with Metal-accelerated `kokoro-mlx`, saves files locally, and delivers formatted markdown briefs + audio recordings directly to your private Telegram bot.

---

## ⚡ Architecture & Features

- **Package & Runtime Manager**: Managed strictly with `uv` and Python 3.11.
- **Hardware-Tailored**: Tuned for Apple Silicon M1 (8GB unified memory), running sequential chunked synthesis with zero heavy cloud API requirements.
- **Two-Stage Story Selection Pipeline**:
  1. **Candidate Pool & Scoring**: Aggregates RSS feeds, applies weighted scoring (60% recency + 40% Hacker News popularity), and eliminates duplicate stories via title similarity matching (`difflib.SequenceMatcher`) to form a candidate pool (default: 15 stories).
  2. **LLM Story Curation (Call #1)**: Ollama (`qwen2.5:3b` @ `temp=0.2`) evaluates candidate titles/summaries and selects the top 5 most technically impactful and distinct stories.
  3. **Script & Digest Generation (Call #2)**: Ollama (`qwen2.5:3b` @ `temp=0.7`, ~750 word target) generates a dual JSON payload containing a structured markdown text digest and an engaging spoken monologue script.
- **Spoken Audio Sanitization**: Dedicated `clean_script_for_audio()` sanitizer strips URLs, bracketed paths (e.g. `[domain/path]`), "link available at..." filler phrases, and markdown artifacts to ensure smooth, natural narration.
- **Local TTS**: `kokoro-mlx` Metal acceleration using British male voice `bm_george` (configurable in `config.toml`).
- **Telegram Dispatch**: Delivers markdown summary and WAV audio directly via Telegram Bot API (handles Telegram's 50MB file limit by automatically splitting large files if necessary).
- **Automation**: macOS `launchd` service running unattended every morning at 07:00 AM.

---

## 📂 Project Structure

```
AI_news_voice_feed/
├── config.toml                   # Centralized knobs: candidate_pool_size, max_stories, lookback, voice, model
├── pyproject.toml                # UV project configuration
├── .env.example                  # Environment secrets template
├── .gitignore                    # Git ignore for .env, output/, .venv
├── launchd/
│   └── com.aibriefing.daily.plist # macOS LaunchAgent configuration
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
- `feeds.candidate_pool_size`: Size of pre-filtered candidate pool scored by recency and HN points (default: `15`).
- `feeds.max_stories`: Number of top stories selected by LLM curation for the final briefing (default: `5`).
- `tts.voice`: Voice name (default: `"bm_george"`).
- `tts.speed`: Speaking speed multiplier (default: `1.0`).
- `llm.model`: Ollama model tag (default: `"qwen2.5:3b"`).

---

## 🧪 Running the Pipeline

### Dry Run (Test Feeds & Script Generation)
Verify RSS feeds aggregation and Ollama generation without synthesizing audio or sending to Telegram:
```bash
uv run python src/pipeline.py --dry-run
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
- `output/YYYY-MM-DD_summary.md` (Markdown notes with links & full spoken script)
- `output/YYYY-MM-DD_briefing.wav` (Native 24kHz 16-bit PCM WAV audio)

You can also play the generated audio directly in macOS Terminal:
```bash
afplay output/*_briefing.wav
```

---

## ⏰ macOS Daily Automation (`launchd`)

To run the briefing automatically every day at 07:00 AM:

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
