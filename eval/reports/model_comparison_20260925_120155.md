# LLM Summarization Model Comparison Report

**Generated:** 2026-09-25 12:01:55  
**Models compared:** `llama3.2:3b`, `phi4-mini:3.8b`, `qwen2.5:3b`  
**Evaluation cases:** 6  
**Judge model:** `gemini-2.5-flash`

## Aggregate Results

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass Rate | 100% | 67% | 83% |
| Mean ROUGE-L F1 | 0.7280 | 0.5093 | 0.7568 |
| Mean Keyword Overlap | 0.86 | 0.85 | 0.95 |
| Mean Judge Score (1-5) | 4.00 | 4.00 | 3.67 |
| Total Hallucinations | 0 | 0 | 1 |
| Peak Ollama RAM | 0.03 GB | 0.02 GB | 0.03 GB |
| Peak System Used RAM | 5.31 GB | 5.51 GB | 5.34 GB |
| Mean Input Tokens (Prompt) | 202 | 179 | 210 |
| Mean Output Tokens (Summary) | 73 | 56 | 85 |
| Mean TTFT (s) | 0.94s | 1.09s | 0.91s |
| Mean Speed (tok/s) | 26.8 | 21.6 | 27.6 |
| Mean Total Latency (s) | 3.65s | 3.71s | 3.98s |
| Thermal Drift (%) | -6.1% | -12.1% | -12.9% |
| Positional Recall Rate | 100% | 100% | 100% |
| Mean Word Count | 49 | 36 | 53 |
| Cases Passed / Total | 6/6 | 4/6 | 5/6 |

---

## Per-Case Results

### Case: `eval_vllm_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | NO |
| ROUGE-L | 0.6667 | 0.5437 | 0.8462 |
| Keyword Overlap | 0.70 | 0.70 | 0.90 |
| Judge Score | 4/5 (PASS) | 4/5 (PASS) | 2/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 0 | 0 | 1 |
| Ollama RAM | 0.02 GB | 0.02 GB | 0.02 GB |
| System Used RAM | 3.52 GB | 5.08 GB | 5.34 GB |
| Input Tokens (Prompt) | 207 | 184 | 216 |
| Output Tokens (Summary) | 81 | 60 | 101 |
| TTFT (s) | 3.23s | 3.78s | 3.01s |
| Speed (tok/s) | 26.6 | 21.7 | 27.6 |
| Total Latency (s) | 6.27s | 6.55s | 6.66s |
| Word Count | 45 | 34 | 57 |

**Generated Summaries:**

**`llama3.2:3b`**
> The vLLM team released version 0.7.0, which enables chunked prefill by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.

*Judge: [API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.*

**`phi4-mini:3.8b`**
> LLM team released v0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads; it also supports FP8 quantization on H100 GPUs, boosting throughput by 40% over BF16 baselines.

*Judge: [API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.*

**`qwen2.5:3b`**
> The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine for up to 2.5x speedup on code generation tasks.

*Judge: [API Quota Depleted] Found ungrounded tokens: The LLM*

### Case: `eval_alphagenome_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | YES |
| ROUGE-L | 0.7321 | 0.6981 | 0.6935 |
| Keyword Overlap | 0.89 | 1.00 | 1.00 |
| Judge Score | 4/5 (PASS) | 4/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 | 0 |
| Ollama RAM | 0.02 GB | 0.02 GB | 0.03 GB |
| System Used RAM | 5.31 GB | 5.36 GB | 5.08 GB |
| Input Tokens (Prompt) | 189 | 164 | 199 |
| Output Tokens (Summary) | 58 | 52 | 78 |
| TTFT (s) | 0.41s | 0.48s | 0.52s |
| Speed (tok/s) | 26.8 | 21.6 | 27.4 |
| Total Latency (s) | 2.57s | 2.89s | 3.37s |
| Word Count | 43 | 37 | 55 |

**Generated Summaries:**

**`llama3.2:3b`**
> Google DeepMind has introduced AlphaGenome Atlas, an AI system that can predict molecular effects across 9 billion DNA variant locations. The model was trained on data from 838 individuals across 54 tissue types, achieving a Pearson correlation of 0.91 on held-out validation sets.

*Judge: [API Quota Depleted] High factual overlap (89%) & 0 lexical hallucinations.*

**`phi4-mini:3.8b`**
> Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

**`qwen2.5:3b`**
> Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

### Case: `eval_datasette_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | YES |
| ROUGE-L | 0.6346 | 0.4681 | 0.8850 |
| Keyword Overlap | 0.78 | 0.78 | 0.89 |
| Judge Score | 4/5 (PASS) | 4/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 | 0 |
| Ollama RAM | 0.02 GB | 0.02 GB | 0.03 GB |
| System Used RAM | 5.21 GB | 5.45 GB | 5.13 GB |
| Input Tokens (Prompt) | 176 | 155 | 180 |
| Output Tokens (Summary) | 55 | 42 | 65 |
| TTFT (s) | 0.40s | 0.47s | 0.40s |
| Speed (tok/s) | 27.0 | 21.7 | 27.9 |
| Total Latency (s) | 2.44s | 2.40s | 2.73s |
| Word Count | 39 | 29 | 47 |

**Generated Summaries:**

**`llama3.2:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari.

*Judge: [API Quota Depleted] High factual overlap (78%) & 0 lexical hallucinations.*

**`phi4-mini:3.8b`**
> Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth authentication with fixes for session cookie expiration on Mobile Safari and new features for organization-level access controls and team-based permission groups.

*Judge: [API Quota Depleted] High factual overlap (78%) & 0 lexical hallucinations.*

**`qwen2.5:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin enhancing GitHub OAuth authentication for Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.

*Judge: [API Quota Depleted] High factual overlap (89%) & 0 lexical hallucinations.*

### Case: `eval_tactile_sensor_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | NO | YES |
| ROUGE-L | 0.7852 | 0.3725 | 0.6720 |
| Keyword Overlap | 0.80 | 0.70 | 0.90 |
| Judge Score | 4/5 (PASS) | 4/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.02 GB | 0.03 GB |
| System Used RAM | 5.14 GB | 5.47 GB | 5.17 GB |
| Input Tokens (Prompt) | 190 | 167 | 197 |
| Output Tokens (Summary) | 80 | 44 | 70 |
| TTFT (s) | 0.41s | 0.48s | 0.40s |
| Speed (tok/s) | 26.9 | 21.7 | 27.8 |
| Total Latency (s) | 3.39s | 2.51s | 2.92s |
| Word Count | 62 | 28 | 51 |

**Generated Summaries:**

**`llama3.2:3b`**
> Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.

*Judge: [API Quota Depleted] High factual overlap (80%) & 0 lexical hallucinations.*

**`phi4-mini:3.8b`**
> MIT CSAIL's TacLink sensor, with a production cost under $50, achieves 94% success in pick-and-place tasks with deformable objects using a gel-filled elastomer dome and 16 RGB LEDs.

*Judge: [API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.*

**`qwen2.5:3b`**
> MIT CSAIL researchers published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter resolution. Field tests with a Boston Dynamics Spot robot showed a 94% success rate on pick-and-place tasks with deformable objects, with a production cost of under $50 per unit.

*Judge: [API Quota Depleted] High factual overlap (90%) & 0 lexical hallucinations.*

### Case: `eval_openai_reasoning_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | YES |
| ROUGE-L | 0.8955 | 0.6446 | 0.8571 |
| Keyword Overlap | 1.00 | 0.91 | 1.00 |
| Judge Score | 4/5 (PASS) | 4/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 | 0 |
| Ollama RAM | 0.02 GB | 0.02 GB | 0.03 GB |
| System Used RAM | 5.16 GB | 5.44 GB | 5.13 GB |
| Input Tokens (Prompt) | 203 | 180 | 215 |
| Output Tokens (Summary) | 93 | 76 | 100 |
| TTFT (s) | 0.52s | 0.60s | 0.52s |
| Speed (tok/s) | 27.0 | 21.6 | 27.6 |
| Total Latency (s) | 3.97s | 4.13s | 4.15s |
| Word Count | 59 | 46 | 57 |

**Generated Summaries:**

**`llama3.2:3b`**
> OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which scored 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

**`phi4-mini:3.8b`**
> OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the previous record of 83.3%. The model features a 128k token context window, structured JSON output, function calling, and pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: [API Quota Depleted] High factual overlap (91%) & 0 lexical hallucinations.*

**`qwen2.5:3b`**
> OpenAI's o3-mini, a reasoning-focused language model for STEM tasks, scored 90.0% on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing is $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

### Case: `eval_positional_recall_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | NO | YES |
| ROUGE-L | 0.6541 | 0.3289 | 0.5868 |
| Keyword Overlap | 1.00 | 1.00 | 1.00 |
| Judge Score | 4/5 (PASS) | 4/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 | 0 |
| Ollama RAM | 0.02 GB | 0.02 GB | 0.03 GB |
| System Used RAM | 5.17 GB | 5.51 GB | 5.17 GB |
| Input Tokens (Prompt) | 248 | 224 | 255 |
| Output Tokens (Summary) | 69 | 64 | 94 |
| TTFT (s) | 0.64s | 0.76s | 0.64s |
| Speed (tok/s) | 26.6 | 21.3 | 27.6 |
| Total Latency (s) | 3.24s | 3.77s | 4.05s |
| Word Count | 48 | 41 | 53 |

**Generated Summaries:**

**`llama3.2:3b`**
> Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

**`phi4-mini:3.8b`**
> In 2026, large language models have advanced with microservices architectures for low-latency workloads, and HyperCache-V4 reduced KV-cache memory consumption by 72.5% on middle-tier clusters. Edge devices face memory footprint challenges, with optimization strategies like AWQ quantization and continuous batching being employed.

*Judge: [API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.*

**`qwen2.5:3b`**
> Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research will evaluate hybrid retrieval-augmented pipelines alongside parameter-efficient fine-tuning techniques for domain adaptation.

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
        "summary": "The vLLM team released version 0.7.0, which enables chunked prefill by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.",
        "latency_seconds": 6.274,
        "ttft_seconds": 3.23,
        "tokens_per_second": 26.59,
        "input_tokens": 207,
        "output_tokens": 81,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 3.52,
        "rouge_l": 0.6667,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 45,
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
        "summary": "Google DeepMind has introduced AlphaGenome Atlas, an AI system that can predict molecular effects across 9 billion DNA variant locations. The model was trained on data from 838 individuals across 54 tissue types, achieving a Pearson correlation of 0.91 on held-out validation sets.",
        "latency_seconds": 2.573,
        "ttft_seconds": 0.405,
        "tokens_per_second": 26.78,
        "input_tokens": 189,
        "output_tokens": 58,
        "process_ram_gb": 0.06,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.31,
        "rouge_l": 0.7321,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 43,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (89%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 1,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari.",
        "latency_seconds": 2.444,
        "ttft_seconds": 0.404,
        "tokens_per_second": 26.98,
        "input_tokens": 176,
        "output_tokens": 55,
        "process_ram_gb": 0.06,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.21,
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
        "summary": "Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.",
        "latency_seconds": 3.386,
        "ttft_seconds": 0.41,
        "tokens_per_second": 26.89,
        "input_tokens": 190,
        "output_tokens": 80,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.14,
        "rouge_l": 0.7852,
        "keyword_overlap": 0.8,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 62,
        "sentence_count": 2,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (80%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which scored 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 3.968,
        "ttft_seconds": 0.52,
        "tokens_per_second": 26.99,
        "input_tokens": 203,
        "output_tokens": 93,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.16,
        "rouge_l": 0.8955,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 59,
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
        "latency_seconds": 3.243,
        "ttft_seconds": 0.644,
        "tokens_per_second": 26.56,
        "input_tokens": 248,
        "output_tokens": 69,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.17,
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
      "mean_rouge_l": 0.728,
      "mean_keyword_overlap": 0.8611,
      "mean_judge_score": 4.0,
      "total_hallucinations": 0,
      "mean_latency_seconds": 3.65,
      "mean_ttft_seconds": 0.94,
      "mean_tokens_per_second": 26.8,
      "mean_input_tokens": 202.2,
      "mean_output_tokens": 72.7,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 5.31,
      "thermal_drift_pct": -6.1,
      "positional_recall_rate": 1.0,
      "mean_word_count": 49.3
    }
  },
  {
    "model": "phi4-mini:3.8b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "run_idx": 1,
        "summary": "LLM team released v0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads; it also supports FP8 quantization on H100 GPUs, boosting throughput by 40% over BF16 baselines.",
        "latency_seconds": 6.548,
        "ttft_seconds": 3.783,
        "tokens_per_second": 21.69,
        "input_tokens": 184,
        "output_tokens": 60,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.08,
        "rouge_l": 0.5437,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 34,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 1,
        "summary": "Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.",
        "latency_seconds": 2.89,
        "ttft_seconds": 0.477,
        "tokens_per_second": 21.57,
        "input_tokens": 164,
        "output_tokens": 52,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.36,
        "rouge_l": 0.6981,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 37,
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
        "summary": "Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth authentication with fixes for session cookie expiration on Mobile Safari and new features for organization-level access controls and team-based permission groups.",
        "latency_seconds": 2.402,
        "ttft_seconds": 0.465,
        "tokens_per_second": 21.72,
        "input_tokens": 155,
        "output_tokens": 42,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.45,
        "rouge_l": 0.4681,
        "keyword_overlap": 0.7778,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 29,
        "sentence_count": 2,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (78%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 1,
        "summary": "MIT CSAIL's TacLink sensor, with a production cost under $50, achieves 94% success in pick-and-place tasks with deformable objects using a gel-filled elastomer dome and 16 RGB LEDs.",
        "latency_seconds": 2.507,
        "ttft_seconds": 0.479,
        "tokens_per_second": 21.73,
        "input_tokens": 167,
        "output_tokens": 44,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.47,
        "rouge_l": 0.3725,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 28,
        "sentence_count": 1,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (70%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the previous record of 83.3%. The model features a 128k token context window, structured JSON output, function calling, and pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.129,
        "ttft_seconds": 0.605,
        "tokens_per_second": 21.61,
        "input_tokens": 180,
        "output_tokens": 76,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.44,
        "rouge_l": 0.6446,
        "keyword_overlap": 0.9091,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 46,
        "sentence_count": 6,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (91%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 1,
        "summary": "In 2026, large language models have advanced with microservices architectures for low-latency workloads, and HyperCache-V4 reduced KV-cache memory consumption by 72.5% on middle-tier clusters. Edge devices face memory footprint challenges, with optimization strategies like AWQ quantization and continuous batching being employed.",
        "latency_seconds": 3.773,
        "ttft_seconds": 0.758,
        "tokens_per_second": 21.26,
        "input_tokens": 224,
        "output_tokens": 64,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.51,
        "rouge_l": 0.3289,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 41,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": false
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 4,
      "pass_rate": 0.6667,
      "mean_rouge_l": 0.5093,
      "mean_keyword_overlap": 0.8478,
      "mean_judge_score": 4.0,
      "total_hallucinations": 0,
      "mean_latency_seconds": 3.71,
      "mean_ttft_seconds": 1.09,
      "mean_tokens_per_second": 21.6,
      "mean_input_tokens": 179.0,
      "mean_output_tokens": 56.3,
      "peak_ollama_ram_gb": 0.02,
      "peak_system_ram_gb": 5.51,
      "thermal_drift_pct": -12.1,
      "positional_recall_rate": 1.0,
      "mean_word_count": 35.8
    }
  },
  {
    "model": "qwen2.5:3b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "run_idx": 1,
        "summary": "The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine for up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 6.663,
        "ttft_seconds": 3.006,
        "tokens_per_second": 27.65,
        "input_tokens": 216,
        "output_tokens": 101,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.34,
        "rouge_l": 0.8462,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [
          "The LLM"
        ],
        "conceptual_hallucinations": [],
        "all_hallucinations": [
          "The LLM"
        ],
        "word_count": 57,
        "sentence_count": 5,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "[API Quota Depleted] Found ungrounded tokens: The LLM",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 1,
        "summary": "Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.373,
        "ttft_seconds": 0.521,
        "tokens_per_second": 27.37,
        "input_tokens": 199,
        "output_tokens": 78,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.08,
        "rouge_l": 0.6935,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 55,
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
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin enhancing GitHub OAuth authentication for Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.",
        "latency_seconds": 2.732,
        "ttft_seconds": 0.401,
        "tokens_per_second": 27.9,
        "input_tokens": 180,
        "output_tokens": 65,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.13,
        "rouge_l": 0.885,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 47,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (89%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 1,
        "summary": "MIT CSAIL researchers published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter resolution. Field tests with a Boston Dynamics Spot robot showed a 94% success rate on pick-and-place tasks with deformable objects, with a production cost of under $50 per unit.",
        "latency_seconds": 2.916,
        "ttft_seconds": 0.398,
        "tokens_per_second": 27.81,
        "input_tokens": 197,
        "output_tokens": 70,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.672,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 51,
        "sentence_count": 2,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (90%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI's o3-mini, a reasoning-focused language model for STEM tasks, scored 90.0% on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing is $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.149,
        "ttft_seconds": 0.519,
        "tokens_per_second": 27.56,
        "input_tokens": 215,
        "output_tokens": 100,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.13,
        "rouge_l": 0.8571,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 57,
        "sentence_count": 7,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 1,
        "summary": "Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research will evaluate hybrid retrieval-augmented pipelines alongside parameter-efficient fine-tuning techniques for domain adaptation.",
        "latency_seconds": 4.053,
        "ttft_seconds": 0.64,
        "tokens_per_second": 27.56,
        "input_tokens": 255,
        "output_tokens": 94,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.5868,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 53,
        "sentence_count": 4,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Quota Depleted] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 5,
      "pass_rate": 0.8333,
      "mean_rouge_l": 0.7568,
      "mean_keyword_overlap": 0.9482,
      "mean_judge_score": 3.67,
      "total_hallucinations": 1,
      "mean_latency_seconds": 3.98,
      "mean_ttft_seconds": 0.91,
      "mean_tokens_per_second": 27.6,
      "mean_input_tokens": 210.3,
      "mean_output_tokens": 84.7,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 5.34,
      "thermal_drift_pct": -12.9,
      "positional_recall_rate": 1.0,
      "mean_word_count": 53.3
    }
  }
]
```
