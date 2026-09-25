# LLM Summarization Model Comparison Report

**Generated:** 2026-09-25 11:23:05  
**Models compared:** `llama3.2:3b`, `phi4-mini:3.8b`, `qwen2.5:3b`  
**Evaluation cases:** 6  
**Judge model:** `gemini-2.5-flash`

## Aggregate Results

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass Rate | 100% | 67% | 67% |
| Mean ROUGE-L F1 | 0.7546 | 0.5368 | 0.7549 |
| Mean Keyword Overlap | 0.90 | 0.86 | 0.95 |
| Mean Judge Score (1-5) | 5.00 | 4.83 | 4.33 |
| Total Hallucinations | 0 | 0 | 1 |
| Mean Input Tokens (Prompt) | 202 | 179 | 210 |
| Mean Output Tokens (Summary) | 78 | 58 | 86 |
| Mean TTFT (s) | 1.00s | 1.17s | 0.96s |
| Mean Speed (tok/s) | 26.2 | 20.7 | 27.6 |
| Mean Total Latency (s) | 3.99s | 3.99s | 4.09s |
| Mean Word Count | 54 | 37 | 54 |
| Cases Passed / Total | 6/6 | 4/6 | 4/6 |

---

## Per-Case Results

### Case: `eval_vllm_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | NO |
| ROUGE-L | 0.6667 | 0.7018 | 0.8702 |
| Keyword Overlap | 0.70 | 0.90 | 0.90 |
| Judge Score | 5/5 (PASS) | 4/5 (PASS) | 4/5 (PASS) |
| Hallucinations | 0 | 0 | 1 |
| Input Tokens (Prompt) | 207 | 184 | 216 |
| Output Tokens (Summary) | 81 | 71 | 102 |
| TTFT (s) | 3.49s | 4.07s | 3.27s |
| Speed (tok/s) | 26.7 | 20.5 | 26.6 |
| Total Latency (s) | 6.51s | 7.53s | 7.12s |
| Word Count | 45 | 44 | 58 |

**Generated Summaries:**

**`llama3.2:3b`**
> The vLLM team released version 0.7.0, which enables chunked prefill by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.

*Judge: All claims made in the summary are factually accurate and directly supported by the source article, with no inaccuracies or fabrications, even though it omits one feature mentioned in the source.*

**`phi4-mini:3.8b`**
> LLM team released version 0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads and FP8 quantization on H100 GPUs improving throughput by 40%. A new speculative decoding engine offers up to 2.5x speedup for code generation tasks.

*Judge: The summary is mostly accurate, but it omits the 'v' from 'vLLM team' and the baseline ('compared to BF16 baselines') for the FP8 throughput improvement, which are minor omissions of detail.*

**`qwen2.5:3b`**
> The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that achieves up to 2.5x speedup on code generation tasks.

*Judge: The summary is mostly accurate, capturing all key facts and numbers, with only minor omissions of specific wording such as 'vLLM team' instead of 'LLM team' and 'baselines' for BF16.*

### Case: `eval_alphagenome_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | YES |
| ROUGE-L | 0.8872 | 0.6981 | 0.6935 |
| Keyword Overlap | 1.00 | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 | 0 |
| Input Tokens (Prompt) | 189 | 164 | 199 |
| Output Tokens (Summary) | 81 | 52 | 78 |
| TTFT (s) | 0.42s | 0.51s | 0.53s |
| Speed (tok/s) | 26.5 | 20.5 | 27.8 |
| Total Latency (s) | 3.48s | 3.06s | 3.33s |
| Word Count | 64 | 37 | 55 |

**Generated Summaries:**

**`llama3.2:3b`**
> Google DeepMind has introduced AlphaGenome Atlas, an AI system that can predict molecular effects at 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types and achieved a Pearson correlation of 0.91 on held-out validation sets, becoming available via the Google Cloud Health API starting from November 2026.

*Judge: All claims in the summary are directly supported by the source article, with no factual inaccuracies or omissions.*

**`phi4-mini:3.8b`**
> Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.

*Judge: All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately represented without any fabrications.*

**`qwen2.5:3b`**
> Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.

*Judge: All claims in the summary are directly supported by the source article, with all key facts, numbers, and entities accurately represented.*

### Case: `eval_datasette_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | NO | YES |
| ROUGE-L | 0.6667 | 0.3736 | 0.8850 |
| Keyword Overlap | 0.89 | 0.78 | 0.89 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 | 0 |
| Input Tokens (Prompt) | 176 | 155 | 180 |
| Output Tokens (Summary) | 63 | 39 | 65 |
| TTFT (s) | 0.40s | 0.50s | 0.40s |
| Speed (tok/s) | 27.1 | 20.8 | 28.0 |
| Total Latency (s) | 2.73s | 2.38s | 2.72s |
| Word Count | 45 | 26 | 47 |

**Generated Summaries:**

**`llama3.2:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.

*Judge: All claims in the summary are directly supported by the source article, with no inaccuracies or fabrications, and all key facts are present.*

**`phi4-mini:3.8b`**
> Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth authentication with enhanced session management for Mobile Safari and new features for organization-level access controls and team-based permissions.

*Judge: All claims in the summary are directly supported by the source article, accurately reflecting the key features and fixes of the plugin's release.*

**`qwen2.5:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin enhancing GitHub OAuth authentication for Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.

*Judge: All claims in the summary are directly supported by the source article, with no inaccuracies or fabrications.*

### Case: `eval_tactile_sensor_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | NO | YES |
| ROUGE-L | 0.7852 | 0.3232 | 0.6560 |
| Keyword Overlap | 0.80 | 0.60 | 0.90 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 | 0 |
| Input Tokens (Prompt) | 190 | 167 | 197 |
| Output Tokens (Summary) | 80 | 40 | 73 |
| TTFT (s) | 0.45s | 0.48s | 0.41s |
| Speed (tok/s) | 25.3 | 21.1 | 27.8 |
| Total Latency (s) | 3.61s | 2.39s | 3.04s |
| Word Count | 62 | 25 | 51 |

**Generated Summaries:**

**`llama3.2:3b`**
> Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.

*Judge: All claims in the summary are directly supported by the source article, with key facts and numbers accurately represented.*

**`phi4-mini:3.8b`**
> MIT CSAIL's TacLink sensor, with a production cost under $50, achieves 94% success in pick-and-place tasks using a gel-filled elastomer dome and 16 RGB LEDs.

*Judge: All claims in the summary are directly supported by the source article, accurately reflecting key facts and figures without any omissions or fabrications.*

**`qwen2.5:3b`**
> MIT CSAIL researchers published an open hardware TacLink tactile sensor capable of sub-millimeter force resolution, using a gel-filled elastomer dome and 16 RGB LEDs. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects, with a production cost under $50 per unit.

*Judge: All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately represented without any omissions or fabrications.*

### Case: `eval_openai_reasoning_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | YES |
| ROUGE-L | 0.8759 | 0.6667 | 0.8296 |
| Keyword Overlap | 1.00 | 0.91 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 | 0 |
| Input Tokens (Prompt) | 203 | 180 | 215 |
| Output Tokens (Summary) | 96 | 78 | 103 |
| TTFT (s) | 0.54s | 0.64s | 0.52s |
| Speed (tok/s) | 25.2 | 21.1 | 27.6 |
| Total Latency (s) | 4.36s | 4.33s | 4.25s |
| Word Count | 62 | 48 | 59 |

**Generated Summaries:**

**`llama3.2:3b`**
> OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: All claims in the summary are directly supported by the source article, with all key facts, numbers, and entities accurately represented.*

**`phi4-mini:3.8b`**
> OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the previous best score of 83.3%. The model features a 128k token context window, structured JSON output, function calling, and API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately presented.*

**`qwen2.5:3b`**
> OpenAI's o3-mini, a reasoning-focused language model for STEM tasks, achieved a 90.0% score on the AIME 2024 math benchmark using high compute settings, outperforming the previous best of 83.3% by o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing is $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: All claims in the summary are directly supported by the source article, with no inaccuracies or omissions of key facts.*

### Case: `eval_positional_recall_01`

| Metric | llama3.2:3b | phi4-mini:3.8b | qwen2.5:3b |
| :--- | ---: | ---: | ---: |
| Pass | YES | YES | NO |
| ROUGE-L | 0.6456 | 0.4575 | 0.5952 |
| Keyword Overlap | 1.00 | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) | 2/5 (FAIL) |
| Hallucinations | 0 | 0 | 0 |
| Input Tokens (Prompt) | 248 | 224 | 255 |
| Output Tokens (Summary) | 68 | 68 | 95 |
| TTFT (s) | 0.68s | 0.82s | 0.64s |
| Speed (tok/s) | 26.4 | 20.0 | 27.6 |
| Total Latency (s) | 3.26s | 4.23s | 4.09s |
| Word Count | 47 | 42 | 54 |

**Generated Summaries:**

**`llama3.2:3b`**
> Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough, HyperCache-V4, which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately reproduced.*

**`phi4-mini:3.8b`**
> In 2026, enterprise infrastructure for large language models (LLMs) is dominated by microservices architectures for low-latency inference, with memory footprint management as a bottleneck for edge devices. The 'HyperCache-V4' breakthrough reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: All claims in the summary, including specific names, numbers, and conditions, are directly and accurately supported by the source article.*

**`qwen2.5:3b`**
> Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research aims to evaluate hybrid retrieval-augmented pipelines alongside parameter-efficient fine-tuning techniques for domain adaptation.

*Judge: The summary hallucinates the meta-instruction 'CRITICAL INVENTED BENEFIT:' which was not part of the source article's content, indicating a significant failure in grounding.*

---

## Raw JSON Results

```json
[
  {
    "model": "llama3.2:3b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "summary": "The vLLM team released version 0.7.0, which enables chunked prefill by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.",
        "latency_seconds": 6.511,
        "ttft_seconds": 3.491,
        "tokens_per_second": 26.73,
        "input_tokens": 207,
        "output_tokens": 81,
        "ram_gb": 0.09,
        "rouge_l": 0.6667,
        "keyword_overlap": 0.7,
        "hallucinations": [],
        "word_count": 45,
        "sentence_count": 4,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims made in the summary are factually accurate and directly supported by the source article, with no inaccuracies or fabrications, even though it omits one feature mentioned in the source.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_alphagenome_01",
        "summary": "Google DeepMind has introduced AlphaGenome Atlas, an AI system that can predict molecular effects at 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types and achieved a Pearson correlation of 0.91 on held-out validation sets, becoming available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.477,
        "ttft_seconds": 0.424,
        "tokens_per_second": 26.54,
        "input_tokens": 189,
        "output_tokens": 81,
        "ram_gb": 0.05,
        "rouge_l": 0.8872,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 64,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with no factual inaccuracies or omissions.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_datasette_01",
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.",
        "latency_seconds": 2.732,
        "ttft_seconds": 0.404,
        "tokens_per_second": 27.07,
        "input_tokens": 176,
        "output_tokens": 63,
        "ram_gb": 0.05,
        "rouge_l": 0.6667,
        "keyword_overlap": 0.8889,
        "hallucinations": [],
        "word_count": 45,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with no inaccuracies or fabrications, and all key facts are present.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "summary": "Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.",
        "latency_seconds": 3.614,
        "ttft_seconds": 0.451,
        "tokens_per_second": 25.31,
        "input_tokens": 190,
        "output_tokens": 80,
        "ram_gb": 0.05,
        "rouge_l": 0.7852,
        "keyword_overlap": 0.8,
        "hallucinations": [],
        "word_count": 62,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with key facts and numbers accurately represented.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "summary": "OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.357,
        "ttft_seconds": 0.542,
        "tokens_per_second": 25.17,
        "input_tokens": 203,
        "output_tokens": 96,
        "ram_gb": 0.04,
        "rouge_l": 0.8759,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 62,
        "sentence_count": 6,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with all key facts, numbers, and entities accurately represented.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_positional_recall_01",
        "summary": "Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough, HyperCache-V4, which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 3.262,
        "ttft_seconds": 0.682,
        "tokens_per_second": 26.36,
        "input_tokens": 248,
        "output_tokens": 68,
        "ram_gb": 0.03,
        "rouge_l": 0.6456,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 47,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately reproduced.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 6,
      "pass_rate": 1.0,
      "mean_rouge_l": 0.7546,
      "mean_keyword_overlap": 0.8981,
      "mean_judge_score": 5.0,
      "total_hallucinations": 0,
      "mean_latency_seconds": 3.99,
      "mean_ttft_seconds": 1.0,
      "mean_tokens_per_second": 26.2,
      "mean_input_tokens": 202.2,
      "mean_output_tokens": 78.2,
      "peak_ram_gb": 0.09,
      "thermal_drift_pct": -11.7,
      "positional_recall_rate": 1.0,
      "mean_word_count": 54.2
    }
  },
  {
    "model": "phi4-mini:3.8b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "summary": "LLM team released version 0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads and FP8 quantization on H100 GPUs improving throughput by 40%. A new speculative decoding engine offers up to 2.5x speedup for code generation tasks.",
        "latency_seconds": 7.528,
        "ttft_seconds": 4.066,
        "tokens_per_second": 20.52,
        "input_tokens": 184,
        "output_tokens": 71,
        "ram_gb": 0.04,
        "rouge_l": 0.7018,
        "keyword_overlap": 0.9,
        "hallucinations": [],
        "word_count": 44,
        "sentence_count": 5,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is mostly accurate, but it omits the 'v' from 'vLLM team' and the baseline ('compared to BF16 baselines') for the FP8 throughput improvement, which are minor omissions of detail.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_alphagenome_01",
        "summary": "Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.",
        "latency_seconds": 3.056,
        "ttft_seconds": 0.509,
        "tokens_per_second": 20.47,
        "input_tokens": 164,
        "output_tokens": 52,
        "ram_gb": 0.04,
        "rouge_l": 0.6981,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 37,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately represented without any fabrications.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_datasette_01",
        "summary": "Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth authentication with enhanced session management for Mobile Safari and new features for organization-level access controls and team-based permissions.",
        "latency_seconds": 2.379,
        "ttft_seconds": 0.502,
        "tokens_per_second": 20.81,
        "input_tokens": 155,
        "output_tokens": 39,
        "ram_gb": 0.04,
        "rouge_l": 0.3736,
        "keyword_overlap": 0.7778,
        "hallucinations": [],
        "word_count": 26,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, accurately reflecting the key features and fixes of the plugin's release.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "summary": "MIT CSAIL's TacLink sensor, with a production cost under $50, achieves 94% success in pick-and-place tasks using a gel-filled elastomer dome and 16 RGB LEDs.",
        "latency_seconds": 2.386,
        "ttft_seconds": 0.483,
        "tokens_per_second": 21.06,
        "input_tokens": 167,
        "output_tokens": 40,
        "ram_gb": 0.04,
        "rouge_l": 0.3232,
        "keyword_overlap": 0.6,
        "hallucinations": [],
        "word_count": 25,
        "sentence_count": 1,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, accurately reflecting key facts and figures without any omissions or fabrications.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "summary": "OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the previous best score of 83.3%. The model features a 128k token context window, structured JSON output, function calling, and API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.332,
        "ttft_seconds": 0.638,
        "tokens_per_second": 21.13,
        "input_tokens": 180,
        "output_tokens": 78,
        "ram_gb": 0.03,
        "rouge_l": 0.6667,
        "keyword_overlap": 0.9091,
        "hallucinations": [],
        "word_count": 48,
        "sentence_count": 6,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately presented.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_positional_recall_01",
        "summary": "In 2026, enterprise infrastructure for large language models (LLMs) is dominated by microservices architectures for low-latency inference, with memory footprint management as a bottleneck for edge devices. The 'HyperCache-V4' breakthrough reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 4.23,
        "ttft_seconds": 0.817,
        "tokens_per_second": 20.04,
        "input_tokens": 224,
        "output_tokens": 68,
        "ram_gb": 0.03,
        "rouge_l": 0.4575,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 42,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary, including specific names, numbers, and conditions, are directly and accurately supported by the source article.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 4,
      "pass_rate": 0.6667,
      "mean_rouge_l": 0.5368,
      "mean_keyword_overlap": 0.8645,
      "mean_judge_score": 4.83,
      "total_hallucinations": 0,
      "mean_latency_seconds": 3.99,
      "mean_ttft_seconds": 1.17,
      "mean_tokens_per_second": 20.7,
      "mean_input_tokens": 179.0,
      "mean_output_tokens": 58.0,
      "peak_ram_gb": 0.04,
      "thermal_drift_pct": -15.5,
      "positional_recall_rate": 1.0,
      "mean_word_count": 37.0
    }
  },
  {
    "model": "qwen2.5:3b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "summary": "The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that achieves up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 7.117,
        "ttft_seconds": 3.274,
        "tokens_per_second": 26.55,
        "input_tokens": 216,
        "output_tokens": 102,
        "ram_gb": 0.03,
        "rouge_l": 0.8702,
        "keyword_overlap": 0.9,
        "hallucinations": [
          "The LLM"
        ],
        "word_count": 58,
        "sentence_count": 5,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is mostly accurate, capturing all key facts and numbers, with only minor omissions of specific wording such as 'vLLM team' instead of 'LLM team' and 'baselines' for BF16.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      },
      {
        "case_id": "eval_alphagenome_01",
        "summary": "Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.334,
        "ttft_seconds": 0.531,
        "tokens_per_second": 27.83,
        "input_tokens": 199,
        "output_tokens": 78,
        "ram_gb": 0.04,
        "rouge_l": 0.6935,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 55,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with all key facts, numbers, and entities accurately represented.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_datasette_01",
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin enhancing GitHub OAuth authentication for Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.",
        "latency_seconds": 2.722,
        "ttft_seconds": 0.403,
        "tokens_per_second": 28.04,
        "input_tokens": 180,
        "output_tokens": 65,
        "ram_gb": 0.04,
        "rouge_l": 0.885,
        "keyword_overlap": 0.8889,
        "hallucinations": [],
        "word_count": 47,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with no inaccuracies or fabrications.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "summary": "MIT CSAIL researchers published an open hardware TacLink tactile sensor capable of sub-millimeter force resolution, using a gel-filled elastomer dome and 16 RGB LEDs. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects, with a production cost under $50 per unit.",
        "latency_seconds": 3.036,
        "ttft_seconds": 0.407,
        "tokens_per_second": 27.79,
        "input_tokens": 197,
        "output_tokens": 73,
        "ram_gb": 0.04,
        "rouge_l": 0.656,
        "keyword_overlap": 0.9,
        "hallucinations": [],
        "word_count": 51,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately represented without any omissions or fabrications.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "summary": "OpenAI's o3-mini, a reasoning-focused language model for STEM tasks, achieved a 90.0% score on the AIME 2024 math benchmark using high compute settings, outperforming the previous best of 83.3% by o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing is $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.251,
        "ttft_seconds": 0.522,
        "tokens_per_second": 27.63,
        "input_tokens": 215,
        "output_tokens": 103,
        "ram_gb": 0.04,
        "rouge_l": 0.8296,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 59,
        "sentence_count": 7,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with no inaccuracies or omissions of key facts.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_positional_recall_01",
        "summary": "Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research aims to evaluate hybrid retrieval-augmented pipelines alongside parameter-efficient fine-tuning techniques for domain adaptation.",
        "latency_seconds": 4.087,
        "ttft_seconds": 0.643,
        "tokens_per_second": 27.6,
        "input_tokens": 255,
        "output_tokens": 95,
        "ram_gb": 0.04,
        "rouge_l": 0.5952,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 54,
        "sentence_count": 4,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary hallucinates the meta-instruction 'CRITICAL INVENTED BENEFIT:' which was not part of the source article's content, indicating a significant failure in grounding.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 4,
      "pass_rate": 0.6667,
      "mean_rouge_l": 0.7549,
      "mean_keyword_overlap": 0.9482,
      "mean_judge_score": 4.33,
      "total_hallucinations": 1,
      "mean_latency_seconds": 4.09,
      "mean_ttft_seconds": 0.96,
      "mean_tokens_per_second": 27.6,
      "mean_input_tokens": 210.3,
      "mean_output_tokens": 86.0,
      "peak_ram_gb": 0.04,
      "thermal_drift_pct": -13.7,
      "positional_recall_rate": 1.0,
      "mean_word_count": 54.0
    }
  }
]
```
