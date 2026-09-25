# LLM Summarization Model Comparison Report

**Generated:** 2026-09-25 11:59:11  
**Models compared:** `llama3.2:3b`  
**Evaluation cases:** 6  
**Judge model:** `gemini-2.5-flash`

## Aggregate Results

| Metric | llama3.2:3b |
| :--- | ---: |
| Pass Rate | 100% |
| Mean ROUGE-L F1 | 0.7221 |
| Mean Keyword Overlap | 0.86 |
| Mean Judge Score (1-5) | 4.00 |
| Total Hallucinations | 0 |
| Peak Ollama RAM | 0.03 GB |
| Peak System Used RAM | 5.26 GB |
| Mean Input Tokens (Prompt) | 202 |
| Mean Output Tokens (Summary) | 73 |
| Mean TTFT (s) | 0.94s |
| Mean Speed (tok/s) | 26.7 |
| Mean Total Latency (s) | 3.69s |
| Thermal Drift (%) | -13.0% |
| Positional Recall Rate | 100% |
| Mean Word Count | 50 |
| Cases Passed / Total | 6/6 |

---

## Per-Case Results

### Case: `eval_vllm_01`

| Metric | llama3.2:3b |
| :--- | ---: |
| Pass | YES |
| ROUGE-L | 0.6949 |
| Keyword Overlap | 0.70 |
| Judge Score | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 |
| Ollama RAM | 0.02 GB |
| System Used RAM | 3.27 GB |
| Input Tokens (Prompt) | 207 |
| Output Tokens (Summary) | 82 |
| TTFT (s) | 3.22s |
| Speed (tok/s) | 26.7 |
| Total Latency (s) | 6.29s |
| Word Count | 46 |

**Generated Summaries:**

**`llama3.2:3b`**
> The vLLM team released version 0.7.0, which features chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.

*Judge: [API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.*

### Case: `eval_alphagenome_01`

| Metric | llama3.2:3b |
| :--- | ---: |
| Pass | YES |
| ROUGE-L | 0.7903 |
| Keyword Overlap | 1.00 |
| Judge Score | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 |
| Ollama RAM | 0.03 GB |
| System Used RAM | 5.24 GB |
| Input Tokens (Prompt) | 189 |
| Output Tokens (Summary) | 71 |
| TTFT (s) | 0.41s |
| Speed (tok/s) | 26.5 |
| Total Latency (s) | 3.09s |
| Word Count | 54 |

**Generated Summaries:**

**`llama3.2:3b`**
> Google DeepMind's AlphaGenome Atlas is an AI system that can predict molecular effects across 9 billion DNA variant locations, trained on data from 838 individuals across 54 tissue types. The model achieved a Pearson correlation of 0.91 on held-out validation sets and is available via the Google Cloud Health API starting from November 2026.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

### Case: `eval_datasette_01`

| Metric | llama3.2:3b |
| :--- | ---: |
| Pass | YES |
| ROUGE-L | 0.6346 |
| Keyword Overlap | 0.78 |
| Judge Score | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 |
| Ollama RAM | 0.03 GB |
| System Used RAM | 5.19 GB |
| Input Tokens (Prompt) | 176 |
| Output Tokens (Summary) | 55 |
| TTFT (s) | 0.41s |
| Speed (tok/s) | 26.9 |
| Total Latency (s) | 2.45s |
| Word Count | 39 |

**Generated Summaries:**

**`llama3.2:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari.

*Judge: [API Quota Depleted] High factual overlap (78%) & 0 lexical hallucinations.*

### Case: `eval_tactile_sensor_01`

| Metric | llama3.2:3b |
| :--- | ---: |
| Pass | YES |
| ROUGE-L | 0.6829 |
| Keyword Overlap | 0.70 |
| Judge Score | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 |
| Ollama RAM | 0.03 GB |
| System Used RAM | 5.23 GB |
| Input Tokens (Prompt) | 190 |
| Output Tokens (Summary) | 67 |
| TTFT (s) | 0.40s |
| Speed (tok/s) | 26.7 |
| Total Latency (s) | 2.92s |
| Word Count | 51 |

**Generated Summaries:**

**`llama3.2:3b`**
> Researchers at MIT CSAIL have published an open hardware design for the TacLink optical tactile sensor, which can resolve contact forces at sub-millimeter spatial resolution. The sensor, featuring a gel-filled elastomer dome illuminated by 16 RGB LEDs, demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.

*Judge: [API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.*

### Case: `eval_openai_reasoning_01`

| Metric | llama3.2:3b |
| :--- | ---: |
| Pass | YES |
| ROUGE-L | 0.8759 |
| Keyword Overlap | 1.00 |
| Judge Score | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 |
| Ollama RAM | 0.03 GB |
| System Used RAM | 5.18 GB |
| Input Tokens (Prompt) | 203 |
| Output Tokens (Summary) | 96 |
| TTFT (s) | 0.52s |
| Speed (tok/s) | 26.8 |
| Total Latency (s) | 4.11s |
| Word Count | 62 |

**Generated Summaries:**

**`llama3.2:3b`**
> OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

### Case: `eval_positional_recall_01`

| Metric | llama3.2:3b |
| :--- | ---: |
| Pass | YES |
| ROUGE-L | 0.6541 |
| Keyword Overlap | 1.00 |
| Judge Score | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 |
| Ollama RAM | 0.03 GB |
| System Used RAM | 5.26 GB |
| Input Tokens (Prompt) | 248 |
| Output Tokens (Summary) | 69 |
| TTFT (s) | 0.65s |
| Speed (tok/s) | 26.4 |
| Total Latency (s) | 3.26s |
| Word Count | 48 |

**Generated Summaries:**

**`llama3.2:3b`**
> Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

---

## Raw JSON Results

```json
[
  {
    "model": "llama3.2:3b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "run_idx": 1,
        "summary": "The vLLM team released version 0.7.0, which features chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.",
        "latency_seconds": 6.286,
        "ttft_seconds": 3.221,
        "tokens_per_second": 26.72,
        "input_tokens": 207,
        "output_tokens": 82,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 3.27,
        "rouge_l": 0.6949,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 46,
        "sentence_count": 4,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 1,
        "summary": "Google DeepMind's AlphaGenome Atlas is an AI system that can predict molecular effects across 9 billion DNA variant locations, trained on data from 838 individuals across 54 tissue types. The model achieved a Pearson correlation of 0.91 on held-out validation sets and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.087,
        "ttft_seconds": 0.409,
        "tokens_per_second": 26.52,
        "input_tokens": 189,
        "output_tokens": 71,
        "process_ram_gb": 0.06,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.24,
        "rouge_l": 0.7903,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 54,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 1,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari.",
        "latency_seconds": 2.451,
        "ttft_seconds": 0.406,
        "tokens_per_second": 26.9,
        "input_tokens": 176,
        "output_tokens": 55,
        "process_ram_gb": 0.06,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.19,
        "rouge_l": 0.6346,
        "keyword_overlap": 0.7778,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 39,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (78%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 1,
        "summary": "Researchers at MIT CSAIL have published an open hardware design for the TacLink optical tactile sensor, which can resolve contact forces at sub-millimeter spatial resolution. The sensor, featuring a gel-filled elastomer dome illuminated by 16 RGB LEDs, demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.",
        "latency_seconds": 2.915,
        "ttft_seconds": 0.403,
        "tokens_per_second": 26.69,
        "input_tokens": 190,
        "output_tokens": 67,
        "process_ram_gb": 0.06,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.23,
        "rouge_l": 0.6829,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 51,
        "sentence_count": 2,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.114,
        "ttft_seconds": 0.524,
        "tokens_per_second": 26.75,
        "input_tokens": 203,
        "output_tokens": 96,
        "process_ram_gb": 0.06,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.18,
        "rouge_l": 0.8759,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 62,
        "sentence_count": 6,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 1,
        "summary": "Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 3.258,
        "ttft_seconds": 0.648,
        "tokens_per_second": 26.45,
        "input_tokens": 248,
        "output_tokens": 69,
        "process_ram_gb": 0.06,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.26,
        "rouge_l": 0.6541,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 48,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 6,
      "pass_rate": 1.0,
      "mean_rouge_l": 0.7221,
      "mean_keyword_overlap": 0.863,
      "mean_judge_score": 4.0,
      "total_hallucinations": 0,
      "mean_latency_seconds": 3.69,
      "mean_ttft_seconds": 0.94,
      "mean_tokens_per_second": 26.7,
      "mean_input_tokens": 202.2,
      "mean_output_tokens": 73.3,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 5.26,
      "thermal_drift_pct": -13.0,
      "positional_recall_rate": 1.0,
      "mean_word_count": 50.0
    }
  }
]
```
