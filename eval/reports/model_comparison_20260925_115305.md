# LLM Summarization Model Comparison Report

**Generated:** 2026-09-25 11:53:05  
**Models compared:** `phi4-mini:3.8b`, `qwen2.5:3b`  
**Evaluation cases:** 6  
**Judge model:** `gemini-2.5-flash`

## Aggregate Results

| Metric | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass Rate | 0% | 0% |
| Mean ROUGE-L F1 | 0.5194 | 0.7628 |
| Mean Keyword Overlap | 0.86 | 0.95 |
| Mean Judge Score (1-5) | 1.00 | 1.00 |
| Total Hallucinations | 6 | 7 |
| Peak Ollama RAM | 0.03 GB | 0.03 GB |
| Peak System Used RAM | 5.58 GB | 5.46 GB |
| Mean Input Tokens (Prompt) | 179 | 210 |
| Mean Output Tokens (Summary) | 56 | 83 |
| Mean TTFT (s) | 1.10s | 0.91s |
| Mean Speed (tok/s) | 21.7 | 27.7 |
| Mean Total Latency (s) | 3.70s | 3.92s |
| Thermal Drift (%) | -20.8% | -15.8% |
| Positional Recall Rate | 100% | 100% |
| Mean Word Count | 36 | 52 |
| Cases Passed / Total | 0/6 | 0/6 |

---

## Per-Case Results

### Case: `eval_vllm_01`

| Metric | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | NO |
| ROUGE-L | 0.7018 | 0.8550 |
| Keyword Overlap | 0.90 | 0.90 |
| Judge Score | 1/5 (FAIL) | 1/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 1 | 2 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 3.80 GB | 5.46 GB |
| Input Tokens (Prompt) | 184 | 216 |
| Output Tokens (Summary) | 71 | 102 |
| TTFT (s) | 3.80s | 2.98s |
| Speed (tok/s) | 21.1 | 27.6 |
| Total Latency (s) | 7.17s | 6.67s |
| Word Count | 44 | 58 |

**Generated Summaries:**

**`phi4-mini:3.8b`**
> LLM team released version 0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads and FP8 quantization on H100 GPUs improving throughput by 40%. A new speculative decoding engine offers up to 2.5x speedup for code generation tasks.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

**`qwen2.5:3b`**
> The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that offers up to 2.5x speedup on code generation tasks.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

### Case: `eval_alphagenome_01`

| Metric | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | NO |
| ROUGE-L | 0.6981 | 0.6935 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 1/5 (FAIL) | 1/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 1 | 1 |
| Ollama RAM | 0.02 GB | 0.03 GB |
| System Used RAM | 5.41 GB | 5.30 GB |
| Input Tokens (Prompt) | 164 | 199 |
| Output Tokens (Summary) | 52 | 78 |
| TTFT (s) | 0.50s | 0.52s |
| Speed (tok/s) | 21.7 | 27.9 |
| Total Latency (s) | 2.90s | 3.31s |
| Word Count | 37 | 55 |

**Generated Summaries:**

**`phi4-mini:3.8b`**
> Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

**`qwen2.5:3b`**
> Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

### Case: `eval_datasette_01`

| Metric | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | NO |
| ROUGE-L | 0.4516 | 0.8772 |
| Keyword Overlap | 0.78 | 0.89 |
| Judge Score | 1/5 (FAIL) | 1/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 1 | 1 |
| Ollama RAM | 0.02 GB | 0.03 GB |
| System Used RAM | 5.57 GB | 5.29 GB |
| Input Tokens (Prompt) | 155 | 180 |
| Output Tokens (Summary) | 41 | 66 |
| TTFT (s) | 0.46s | 0.40s |
| Speed (tok/s) | 21.9 | 27.9 |
| Total Latency (s) | 2.34s | 2.77s |
| Word Count | 28 | 48 |

**Generated Summaries:**

**`phi4-mini:3.8b`**
> Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth authentication with fixes for session cookie expiration on Mobile Safari and new features for organization-level access controls and team-based permissions.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

**`qwen2.5:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin for Datasette instances that adds GitHub OAuth authentication. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

### Case: `eval_tactile_sensor_01`

| Metric | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | NO |
| ROUGE-L | 0.2857 | 0.7069 |
| Keyword Overlap | 0.60 | 0.90 |
| Judge Score | 1/5 (FAIL) | 1/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 1 | 1 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.27 GB |
| Input Tokens (Prompt) | 167 | 197 |
| Output Tokens (Summary) | 39 | 60 |
| TTFT (s) | 0.47s | 0.40s |
| Speed (tok/s) | 22.0 | 27.5 |
| Total Latency (s) | 2.25s | 2.58s |
| Word Count | 24 | 43 |

**Generated Summaries:**

**`phi4-mini:3.8b`**
> MIT CSAIL's TacLink sensor, with a $50 production cost, achieves 94% success in pick-and-place tasks using a gel-filled elastomer dome and 16 RGB LEDs.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

**`qwen2.5:3b`**
> MIT CSAIL researchers published an open hardware TacLink optical tactile sensor capable of sub-millimeter force resolution, with a production cost under $50 per unit. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

### Case: `eval_openai_reasoning_01`

| Metric | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | NO |
| ROUGE-L | 0.6281 | 0.8571 |
| Keyword Overlap | 0.91 | 1.00 |
| Judge Score | 1/5 (FAIL) | 1/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 1 | 1 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.23 GB |
| Input Tokens (Prompt) | 180 | 215 |
| Output Tokens (Summary) | 76 | 100 |
| TTFT (s) | 0.60s | 0.53s |
| Speed (tok/s) | 21.7 | 27.8 |
| Total Latency (s) | 4.10s | 4.12s |
| Word Count | 46 | 57 |

**Generated Summaries:**

**`phi4-mini:3.8b`**
> OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the prior record of 83.3%. The model features a 128k token context window, structured JSON output, function calling, and pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

**`qwen2.5:3b`**
> OpenAI's o3-mini, a reasoning-focused language model for STEM tasks, scored 90.0% on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing is $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

### Case: `eval_positional_recall_01`

| Metric | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | NO |
| ROUGE-L | 0.3514 | 0.5868 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 1/5 (FAIL) | 1/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 1 | 1 |
| Ollama RAM | 0.02 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.28 GB |
| Input Tokens (Prompt) | 224 | 255 |
| Output Tokens (Summary) | 59 | 94 |
| TTFT (s) | 0.75s | 0.64s |
| Speed (tok/s) | 21.7 | 27.7 |
| Total Latency (s) | 3.47s | 4.04s |
| Word Count | 37 | 53 |

**Generated Summaries:**

**`phi4-mini:3.8b`**
> In 2026, large language models are increasingly deployed using microservices architectures for low-latency inference, while HyperCache-V4 reduces KV-cache memory consumption by 72.5% on middle-tier clusters. Edge devices continue to optimize memory usage through AWQ quantization and batching.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

**`qwen2.5:3b`**
> Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research will evaluate hybrid retrieval-augmented pipelines alongside parameter-efficient fine-tuning techniques for domain adaptation.

*Judge: Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}*

---

## Raw JSON Results

```json
[
  {
    "model": "phi4-mini:3.8b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "run_idx": 1,
        "summary": "LLM team released version 0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads and FP8 quantization on H100 GPUs improving throughput by 40%. A new speculative decoding engine offers up to 2.5x speedup for code generation tasks.",
        "latency_seconds": 7.172,
        "ttft_seconds": 3.802,
        "tokens_per_second": 21.05,
        "input_tokens": 184,
        "output_tokens": 71,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 3.8,
        "rouge_l": 0.7018,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 44,
        "sentence_count": 5,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 1,
        "summary": "Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.",
        "latency_seconds": 2.9,
        "ttft_seconds": 0.497,
        "tokens_per_second": 21.66,
        "input_tokens": 164,
        "output_tokens": 52,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.41,
        "rouge_l": 0.6981,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 37,
        "sentence_count": 3,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 1,
        "summary": "Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth authentication with fixes for session cookie expiration on Mobile Safari and new features for organization-level access controls and team-based permissions.",
        "latency_seconds": 2.336,
        "ttft_seconds": 0.462,
        "tokens_per_second": 21.9,
        "input_tokens": 155,
        "output_tokens": 41,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.57,
        "rouge_l": 0.4516,
        "keyword_overlap": 0.7778,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 28,
        "sentence_count": 2,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 1,
        "summary": "MIT CSAIL's TacLink sensor, with a $50 production cost, achieves 94% success in pick-and-place tasks using a gel-filled elastomer dome and 16 RGB LEDs.",
        "latency_seconds": 2.249,
        "ttft_seconds": 0.473,
        "tokens_per_second": 21.99,
        "input_tokens": 167,
        "output_tokens": 39,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.2857,
        "keyword_overlap": 0.6,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 24,
        "sentence_count": 1,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the prior record of 83.3%. The model features a 128k token context window, structured JSON output, function calling, and pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.101,
        "ttft_seconds": 0.601,
        "tokens_per_second": 21.73,
        "input_tokens": 180,
        "output_tokens": 76,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.6281,
        "keyword_overlap": 0.9091,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 46,
        "sentence_count": 6,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 1,
        "summary": "In 2026, large language models are increasingly deployed using microservices architectures for low-latency inference, while HyperCache-V4 reduces KV-cache memory consumption by 72.5% on middle-tier clusters. Edge devices continue to optimize memory usage through AWQ quantization and batching.",
        "latency_seconds": 3.471,
        "ttft_seconds": 0.754,
        "tokens_per_second": 21.74,
        "input_tokens": 224,
        "output_tokens": 59,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.3514,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 37,
        "sentence_count": 3,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 0,
      "pass_rate": 0.0,
      "mean_rouge_l": 0.5194,
      "mean_keyword_overlap": 0.8645,
      "mean_judge_score": 1.0,
      "total_hallucinations": 6,
      "mean_latency_seconds": 3.7,
      "mean_ttft_seconds": 1.1,
      "mean_tokens_per_second": 21.7,
      "mean_input_tokens": 179.0,
      "mean_output_tokens": 56.3,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 5.58,
      "thermal_drift_pct": -20.8,
      "positional_recall_rate": 1.0,
      "mean_word_count": 36.0
    }
  },
  {
    "model": "qwen2.5:3b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "run_idx": 1,
        "summary": "The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that offers up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 6.671,
        "ttft_seconds": 2.979,
        "tokens_per_second": 27.64,
        "input_tokens": 216,
        "output_tokens": 102,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.46,
        "rouge_l": 0.855,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [
          "The LLM"
        ],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
          "The LLM"
        ],
        "word_count": 58,
        "sentence_count": 5,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 1,
        "summary": "Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.312,
        "ttft_seconds": 0.518,
        "tokens_per_second": 27.93,
        "input_tokens": 199,
        "output_tokens": 78,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.3,
        "rouge_l": 0.6935,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 55,
        "sentence_count": 3,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 1,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin for Datasette instances that adds GitHub OAuth authentication. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.",
        "latency_seconds": 2.768,
        "ttft_seconds": 0.398,
        "tokens_per_second": 27.87,
        "input_tokens": 180,
        "output_tokens": 66,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.29,
        "rouge_l": 0.8772,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 48,
        "sentence_count": 3,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 1,
        "summary": "MIT CSAIL researchers published an open hardware TacLink optical tactile sensor capable of sub-millimeter force resolution, with a production cost under $50 per unit. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects.",
        "latency_seconds": 2.583,
        "ttft_seconds": 0.397,
        "tokens_per_second": 27.46,
        "input_tokens": 197,
        "output_tokens": 60,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.27,
        "rouge_l": 0.7069,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 43,
        "sentence_count": 2,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI's o3-mini, a reasoning-focused language model for STEM tasks, scored 90.0% on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing is $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.119,
        "ttft_seconds": 0.525,
        "tokens_per_second": 27.82,
        "input_tokens": 215,
        "output_tokens": 100,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.23,
        "rouge_l": 0.8571,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 57,
        "sentence_count": 7,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 1,
        "summary": "Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research will evaluate hybrid retrieval-augmented pipelines alongside parameter-efficient fine-tuning techniques for domain adaptation.",
        "latency_seconds": 4.039,
        "ttft_seconds": 0.641,
        "tokens_per_second": 27.67,
        "input_tokens": 255,
        "output_tokens": 94,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.28,
        "rouge_l": 0.5868,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "all_hallucinations": [
          "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}"
        ],
        "word_count": 53,
        "sentence_count": 4,
        "judge_score": 1,
        "judge_verdict": "FAIL",
        "judge_reasoning": "Judge call failed: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}",
        "positional_recall_passed": true,
        "passed": false
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 0,
      "pass_rate": 0.0,
      "mean_rouge_l": 0.7628,
      "mean_keyword_overlap": 0.9482,
      "mean_judge_score": 1.0,
      "total_hallucinations": 7,
      "mean_latency_seconds": 3.92,
      "mean_ttft_seconds": 0.91,
      "mean_tokens_per_second": 27.7,
      "mean_input_tokens": 210.3,
      "mean_output_tokens": 83.3,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 5.46,
      "thermal_drift_pct": -15.8,
      "positional_recall_rate": 1.0,
      "mean_word_count": 52.3
    }
  }
]
```
