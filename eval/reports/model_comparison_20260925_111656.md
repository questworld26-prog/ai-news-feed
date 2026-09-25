# LLM Summarization Model Comparison Report

**Generated:** 2026-09-25 11:16:56  
**Models compared:** `llama3.2:3b`, `phi4-mini:3.8b`  
**Evaluation cases:** 6  
**Judge model:** `gemini-2.5-flash`

## Aggregate Results

| Metric | llama3.2:3b | phi4-mini:3.8b |
| :--- | ---: | ---: |
| Pass Rate | 100% | 33% |
| Mean ROUGE-L F1 | 0.7483 | 0.5080 |
| Mean Keyword Overlap | 0.87 | 0.85 |
| Mean Judge Score (1-5) | 4.83 | 4.67 |
| Total Hallucinations | 0 | 0 |
| Mean Input Tokens (Prompt) | 202 | 179 |
| Mean Output Tokens (Summary) | 77 | 57 |
| Mean TTFT (s) | 0.98s | 1.10s |
| Mean Speed (tok/s) | 26.6 | 21.5 |
| Mean Total Latency (s) | 3.87s | 3.78s |
| Mean Word Count | 53 | 35 |
| Cases Passed / Total | 6/6 | 2/6 |

---

## Per-Case Results

### Case: `eval_vllm_01`

| Metric | llama3.2:3b | phi4-mini:3.8b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.6667 | 0.5769 |
| Keyword Overlap | 0.70 | 0.70 |
| Judge Score | 5/5 (PASS) | 3/5 (FAIL) |
| Hallucinations | 0 | 0 |
| Input Tokens (Prompt) | 207 | 184 |
| Output Tokens (Summary) | 81 | 61 |
| TTFT (s) | 3.47s | 3.78s |
| Speed (tok/s) | 26.2 | 21.0 |
| Total Latency (s) | 6.55s | 6.69s |
| Word Count | 45 | 35 |

**Generated Summaries:**

**`llama3.2:3b`**
> The vLLM team released version 0.7.0, which enables chunked prefill by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.

*Judge: All claims made in the summary are directly supported by the source article, and all facts, numbers, and entities presented are accurate.*

**`phi4-mini:3.8b`**
> LLM team released version 0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads; it also supports FP8 quantization on H100 GPUs, boosting throughput by 40% over BF16 baselines.

*Judge: The summary accurately presents two out of three key features but omits the speculative decoding engine and slightly misnames the team.*

### Case: `eval_alphagenome_01`

| Metric | llama3.2:3b | phi4-mini:3.8b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.9173 | 0.6981 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 |
| Input Tokens (Prompt) | 189 | 164 |
| Output Tokens (Summary) | 82 | 52 |
| TTFT (s) | 0.42s | 0.48s |
| Speed (tok/s) | 26.7 | 21.6 |
| Total Latency (s) | 3.50s | 2.90s |
| Word Count | 64 | 37 |

**Generated Summaries:**

**`llama3.2:3b`**
> Google DeepMind has introduced AlphaGenome Atlas, an AI system that can predict molecular effects across 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types, achieving a Pearson correlation of 0.91 on held-out validation sets, and is available via the Google Cloud Health API starting from November 2026.

*Judge: All claims in the summary are directly supported by the source article, with no inaccuracies or omissions of key facts.*

**`phi4-mini:3.8b`**
> Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.

*Judge: All claims in the summary are directly supported by the source article, with accurate key facts, numbers, and entities.*

### Case: `eval_datasette_01`

| Metric | llama3.2:3b | phi4-mini:3.8b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.6667 | 0.4045 |
| Keyword Overlap | 0.89 | 0.78 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 |
| Input Tokens (Prompt) | 176 | 155 |
| Output Tokens (Summary) | 63 | 40 |
| TTFT (s) | 0.41s | 0.47s |
| Speed (tok/s) | 26.8 | 21.5 |
| Total Latency (s) | 2.76s | 2.33s |
| Word Count | 45 | 24 |

**Generated Summaries:**

**`llama3.2:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.

*Judge: All claims in the summary are directly supported by the source article, with no inaccuracies or fabrications.*

**`phi4-mini:3.8b`**
> Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth for Datasette, fixes Mobile Safari session cookie expiration, and adds organization-level access controls and team-based permissions.

*Judge: All claims in the summary are directly supported by the source article, accurately reflecting the key features and fixes of the plugin.*

### Case: `eval_tactile_sensor_01`

| Metric | llama3.2:3b | phi4-mini:3.8b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.7852 | 0.3363 |
| Keyword Overlap | 0.80 | 0.70 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 |
| Input Tokens (Prompt) | 190 | 167 |
| Output Tokens (Summary) | 80 | 55 |
| TTFT (s) | 0.42s | 0.48s |
| Speed (tok/s) | 26.4 | 21.9 |
| Total Latency (s) | 3.44s | 3.00s |
| Word Count | 62 | 37 |

**Generated Summaries:**

**`llama3.2:3b`**
> Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.

*Judge: All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately represented.*

**`phi4-mini:3.8b`**
> MIT CSAIL's TacLink sensor, with a $50 production cost, achieves 94% success in pick-and-place tasks using a gel-filled elastomer dome and 16 RGB LEDs. The sensor's high-resolution tactile sensing is demonstrated with a Boston Dynamics Spot robot.

*Judge: All claims in the summary are directly supported by the source article, with key facts and entities accurately represented.*

### Case: `eval_openai_reasoning_01`

| Metric | llama3.2:3b | phi4-mini:3.8b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.8000 | 0.5833 |
| Keyword Overlap | 0.82 | 0.91 |
| Judge Score | 4/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 |
| Input Tokens (Prompt) | 203 | 180 |
| Output Tokens (Summary) | 86 | 77 |
| TTFT (s) | 0.53s | 0.62s |
| Speed (tok/s) | 26.8 | 21.7 |
| Total Latency (s) | 3.74s | 4.17s |
| Word Count | 55 | 43 |

**Generated Summaries:**

**`llama3.2:3b`**
> OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model features a 128k token context window and API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: The summary is highly accurate and grounded in the source, but it omits a few minor details such as the model's support for structured JSON output, function calling, and the 'high compute settings' for the benchmark score.*

**`phi4-mini:3.8b`**
> OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the prior record of 83.3%. The model features a 128k token context window, structured JSON output, and function calling, with API pricing at $1.10/million input tokens and $4.40/million output tokens.

*Judge: All claims in the summary are directly supported by the source article, with accurate key facts, numbers, and entities.*

### Case: `eval_positional_recall_01`

| Metric | llama3.2:3b | phi4-mini:3.8b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.6541 | 0.4490 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations | 0 | 0 |
| Input Tokens (Prompt) | 248 | 224 |
| Output Tokens (Summary) | 69 | 59 |
| TTFT (s) | 0.65s | 0.79s |
| Speed (tok/s) | 26.4 | 21.3 |
| Total Latency (s) | 3.26s | 3.56s |
| Word Count | 48 | 36 |

**Generated Summaries:**

**`llama3.2:3b`**
> Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: All claims in the summary are directly supported by the source article, with accurate key facts, numbers, and entities.*

**`phi4-mini:3.8b`**
> In 2026, large language models are increasingly deployed using microservices architectures for low-latency inference, with memory footprint management as a bottleneck for edge devices. The 'HyperCache-V4' innovation reduced KV-cache memory consumption by 72.5% on middle-tier clusters.

*Judge: All claims in the summary are directly supported by the source article, accurately reflecting key facts, numbers, and entities without any fabrication.*

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
        "latency_seconds": 6.554,
        "ttft_seconds": 3.469,
        "tokens_per_second": 26.25,
        "input_tokens": 207,
        "output_tokens": 81,
        "ram_gb": 0.1,
        "rouge_l": 0.6667,
        "keyword_overlap": 0.7,
        "hallucinations": [],
        "word_count": 45,
        "sentence_count": 4,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims made in the summary are directly supported by the source article, and all facts, numbers, and entities presented are accurate.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_alphagenome_01",
        "summary": "Google DeepMind has introduced AlphaGenome Atlas, an AI system that can predict molecular effects across 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types, achieving a Pearson correlation of 0.91 on held-out validation sets, and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.495,
        "ttft_seconds": 0.424,
        "tokens_per_second": 26.71,
        "input_tokens": 189,
        "output_tokens": 82,
        "ram_gb": 0.05,
        "rouge_l": 0.9173,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 64,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with no inaccuracies or omissions of key facts.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_datasette_01",
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.",
        "latency_seconds": 2.756,
        "ttft_seconds": 0.408,
        "tokens_per_second": 26.83,
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
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with no inaccuracies or fabrications.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "summary": "Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.",
        "latency_seconds": 3.444,
        "ttft_seconds": 0.416,
        "tokens_per_second": 26.43,
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
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with key facts, numbers, and entities accurately represented.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "summary": "OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model features a 128k token context window and API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 3.736,
        "ttft_seconds": 0.526,
        "tokens_per_second": 26.8,
        "input_tokens": 203,
        "output_tokens": 86,
        "ram_gb": 0.05,
        "rouge_l": 0.8,
        "keyword_overlap": 0.8182,
        "hallucinations": [],
        "word_count": 55,
        "sentence_count": 6,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is highly accurate and grounded in the source, but it omits a few minor details such as the model's support for structured JSON output, function calling, and the 'high compute settings' for the benchmark score.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_positional_recall_01",
        "summary": "Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 3.262,
        "ttft_seconds": 0.652,
        "tokens_per_second": 26.45,
        "input_tokens": 248,
        "output_tokens": 69,
        "ram_gb": 0.05,
        "rouge_l": 0.6541,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 48,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with accurate key facts, numbers, and entities.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 6,
      "pass_rate": 1.0,
      "mean_rouge_l": 0.7483,
      "mean_keyword_overlap": 0.8678,
      "mean_judge_score": 4.83,
      "total_hallucinations": 0,
      "mean_latency_seconds": 3.87,
      "mean_ttft_seconds": 0.98,
      "mean_tokens_per_second": 26.6,
      "mean_input_tokens": 202.2,
      "mean_output_tokens": 76.8,
      "peak_ram_gb": 0.1,
      "thermal_drift_pct": -18.5,
      "positional_recall_rate": 1.0,
      "mean_word_count": 53.2
    }
  },
  {
    "model": "phi4-mini:3.8b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "summary": "LLM team released version 0.7.0 with default chunked prefill reducing TTFT by up to 3x on Llama 3 70B workloads; it also supports FP8 quantization on H100 GPUs, boosting throughput by 40% over BF16 baselines.",
        "latency_seconds": 6.69,
        "ttft_seconds": 3.783,
        "tokens_per_second": 20.98,
        "input_tokens": 184,
        "output_tokens": 61,
        "ram_gb": 0.04,
        "rouge_l": 0.5769,
        "keyword_overlap": 0.7,
        "hallucinations": [],
        "word_count": 35,
        "sentence_count": 3,
        "judge_score": 3,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary accurately presents two out of three key features but omits the speculative decoding engine and slightly misnames the team.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      },
      {
        "case_id": "eval_alphagenome_01",
        "summary": "Google DeepMind's AlphaGenome Atlas predicts molecular effects across 9 billion DNA variants, trained on data from 838 individuals across 54 tissue types with a Pearson correlation of 0.91. Available via Google Cloud Health API from November 2026.",
        "latency_seconds": 2.899,
        "ttft_seconds": 0.485,
        "tokens_per_second": 21.57,
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
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with accurate key facts, numbers, and entities.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_datasette_01",
        "summary": "Datasette-auth-github v1.0 by Simon Willison introduces GitHub OAuth for Datasette, fixes Mobile Safari session cookie expiration, and adds organization-level access controls and team-based permissions.",
        "latency_seconds": 2.331,
        "ttft_seconds": 0.468,
        "tokens_per_second": 21.51,
        "input_tokens": 155,
        "output_tokens": 40,
        "ram_gb": 0.04,
        "rouge_l": 0.4045,
        "keyword_overlap": 0.7778,
        "hallucinations": [],
        "word_count": 24,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, accurately reflecting the key features and fixes of the plugin.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "summary": "MIT CSAIL's TacLink sensor, with a $50 production cost, achieves 94% success in pick-and-place tasks using a gel-filled elastomer dome and 16 RGB LEDs. The sensor's high-resolution tactile sensing is demonstrated with a Boston Dynamics Spot robot.",
        "latency_seconds": 2.999,
        "ttft_seconds": 0.48,
        "tokens_per_second": 21.85,
        "input_tokens": 167,
        "output_tokens": 55,
        "ram_gb": 0.04,
        "rouge_l": 0.3363,
        "keyword_overlap": 0.7,
        "hallucinations": [],
        "word_count": 37,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with key facts and entities accurately represented.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "summary": "OpenAI's o3-mini achieved a 90.0% score on the AIME 2024 math benchmark, outperforming the prior record of 83.3%. The model features a 128k token context window, structured JSON output, and function calling, with API pricing at $1.10/million input tokens and $4.40/million output tokens.",
        "latency_seconds": 4.17,
        "ttft_seconds": 0.619,
        "tokens_per_second": 21.7,
        "input_tokens": 180,
        "output_tokens": 77,
        "ram_gb": 0.04,
        "rouge_l": 0.5833,
        "keyword_overlap": 0.9091,
        "hallucinations": [],
        "word_count": 43,
        "sentence_count": 6,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, with accurate key facts, numbers, and entities.",
        "positional_recall_passed": true,
        "passed": true,
        "gen_error": null
      },
      {
        "case_id": "eval_positional_recall_01",
        "summary": "In 2026, large language models are increasingly deployed using microservices architectures for low-latency inference, with memory footprint management as a bottleneck for edge devices. The 'HyperCache-V4' innovation reduced KV-cache memory consumption by 72.5% on middle-tier clusters.",
        "latency_seconds": 3.565,
        "ttft_seconds": 0.792,
        "tokens_per_second": 21.32,
        "input_tokens": 224,
        "output_tokens": 59,
        "ram_gb": 0.04,
        "rouge_l": 0.449,
        "keyword_overlap": 1.0,
        "hallucinations": [],
        "word_count": 36,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "All claims in the summary are directly supported by the source article, accurately reflecting key facts, numbers, and entities without any fabrication.",
        "positional_recall_passed": true,
        "passed": false,
        "gen_error": null
      }
    ],
    "aggregate": {
      "total_cases": 6,
      "passed_cases": 2,
      "pass_rate": 0.3333,
      "mean_rouge_l": 0.508,
      "mean_keyword_overlap": 0.8478,
      "mean_judge_score": 4.67,
      "total_hallucinations": 0,
      "mean_latency_seconds": 3.78,
      "mean_ttft_seconds": 1.1,
      "mean_tokens_per_second": 21.5,
      "mean_input_tokens": 179.0,
      "mean_output_tokens": 57.3,
      "peak_ram_gb": 0.04,
      "thermal_drift_pct": -9.9,
      "positional_recall_rate": 1.0,
      "mean_word_count": 35.3
    }
  }
]
```
