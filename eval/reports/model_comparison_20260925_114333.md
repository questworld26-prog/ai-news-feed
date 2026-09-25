# LLM Summarization Model Comparison Report

**Generated:** 2026-09-25 11:43:33  
**Models compared:** `llama3.2:3b`, `qwen2.5:3b`  
**Evaluation cases:** 18  
**Judge model:** `gemini-2.5-flash`

## Aggregate Results

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass Rate | 78% | 67% |
| Mean ROUGE-L F1 | 0.7388 | 0.7523 |
| Mean Keyword Overlap | 0.88 | 0.94 |
| Mean Judge Score (1-5) | 4.17 | 4.33 |
| Total Hallucinations | 6 | 9 |
| Peak Ollama RAM | 0.03 GB | 0.03 GB |
| Peak System Used RAM | 5.64 GB | 5.47 GB |
| Mean Input Tokens (Prompt) | 202 | 210 |
| Mean Output Tokens (Summary) | 75 | 84 |
| Mean TTFT (s) | 0.19s | 0.37s |
| Mean Speed (tok/s) | 26.8 | 27.7 |
| Mean Total Latency (s) | 3.01s | 3.40s |
| Thermal Drift (%) | +12.9% | -1.9% |
| Positional Recall Rate | 100% | 100% |
| Mean Word Count | 52 | 53 |
| Cases Passed / Total | 14/18 | 12/18 |

---

## Per-Case Results

### Case: `eval_vllm_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.6949 | 0.8550 |
| Keyword Overlap | 0.70 | 0.90 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 1 |
| Ollama RAM | 0.02 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.47 GB |
| Input Tokens (Prompt) | 207 | 216 |
| Output Tokens (Summary) | 82 | 102 |
| TTFT (s) | 0.12s | 3.24s |
| Speed (tok/s) | 26.9 | 27.7 |
| Total Latency (s) | 3.18s | 6.91s |
| Word Count | 46 | 58 |

**Generated Summaries:**

**`llama3.2:3b`**
> The vLLM team released version 0.7.0, which features chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.

*Judge: The summary accurately reflects all the points it covers from the source article without introducing any fabricated information or ungrounded concepts.*

**`qwen2.5:3b`**
> The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that offers up to 2.5x speedup on code generation tasks.

*Judge: The summary is highly accurate and grounded, with all claims directly supported by the source article and no semantic or conceptual hallucinations detected.*

### Case: `eval_vllm_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.6949 | 0.8550 |
| Keyword Overlap | 0.70 | 0.90 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 1 |
| Ollama RAM | 0.02 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.47 GB |
| Input Tokens (Prompt) | 207 | 216 |
| Output Tokens (Summary) | 82 | 102 |
| TTFT (s) | 0.12s | 3.24s |
| Speed (tok/s) | 26.9 | 27.7 |
| Total Latency (s) | 3.18s | 6.91s |
| Word Count | 46 | 58 |

**Generated Summaries:**

**`llama3.2:3b`**
> The vLLM team released version 0.7.0, which features chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.

*Judge: The summary accurately reflects all the points it covers from the source article without introducing any fabricated information or ungrounded concepts.*

**`qwen2.5:3b`**
> The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that offers up to 2.5x speedup on code generation tasks.

*Judge: The summary is highly accurate and grounded, with all claims directly supported by the source article and no semantic or conceptual hallucinations detected.*

### Case: `eval_vllm_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.6949 | 0.8550 |
| Keyword Overlap | 0.70 | 0.90 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 1 |
| Ollama RAM | 0.02 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.47 GB |
| Input Tokens (Prompt) | 207 | 216 |
| Output Tokens (Summary) | 82 | 102 |
| TTFT (s) | 0.12s | 3.24s |
| Speed (tok/s) | 26.9 | 27.7 |
| Total Latency (s) | 3.18s | 6.91s |
| Word Count | 46 | 58 |

**Generated Summaries:**

**`llama3.2:3b`**
> The vLLM team released version 0.7.0, which features chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.

*Judge: The summary accurately reflects all the points it covers from the source article without introducing any fabricated information or ungrounded concepts.*

**`qwen2.5:3b`**
> The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that offers up to 2.5x speedup on code generation tasks.

*Judge: The summary is highly accurate and grounded, with all claims directly supported by the source article and no semantic or conceptual hallucinations detected.*

### Case: `eval_alphagenome_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.8872 | 0.6935 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.60 GB | 5.17 GB |
| Input Tokens (Prompt) | 189 | 199 |
| Output Tokens (Summary) | 80 | 78 |
| TTFT (s) | 0.46s | 0.52s |
| Speed (tok/s) | 26.7 | 27.9 |
| Total Latency (s) | 3.46s | 3.31s |
| Word Count | 63 | 55 |

**Generated Summaries:**

**`llama3.2:3b`**
> Google DeepMind's AlphaGenome Atlas is an AI system that can predict molecular effects across 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types and achieved a Pearson correlation of 0.91 on held-out validation sets, becoming available via the Google Cloud Health API starting from November 2026.

*Judge: The summary accurately reflects all key facts from the source article without any conceptual hallucinations or ungrounded claims, earning a perfect score.*

**`qwen2.5:3b`**
> Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.

*Judge: The summary is mostly accurate, with all stated facts directly supported by the source, but it omits the stated purpose of AlphaGenome Atlas to accelerate genomic medicine and rare disease diagnosis.*

### Case: `eval_alphagenome_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.8872 | 0.6935 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.60 GB | 5.17 GB |
| Input Tokens (Prompt) | 189 | 199 |
| Output Tokens (Summary) | 80 | 78 |
| TTFT (s) | 0.46s | 0.52s |
| Speed (tok/s) | 26.7 | 27.9 |
| Total Latency (s) | 3.46s | 3.31s |
| Word Count | 63 | 55 |

**Generated Summaries:**

**`llama3.2:3b`**
> Google DeepMind's AlphaGenome Atlas is an AI system that can predict molecular effects across 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types and achieved a Pearson correlation of 0.91 on held-out validation sets, becoming available via the Google Cloud Health API starting from November 2026.

*Judge: The summary accurately reflects all key facts from the source article without any conceptual hallucinations or ungrounded claims, earning a perfect score.*

**`qwen2.5:3b`**
> Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.

*Judge: The summary is mostly accurate, with all stated facts directly supported by the source, but it omits the stated purpose of AlphaGenome Atlas to accelerate genomic medicine and rare disease diagnosis.*

### Case: `eval_alphagenome_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.8872 | 0.6935 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.60 GB | 5.17 GB |
| Input Tokens (Prompt) | 189 | 199 |
| Output Tokens (Summary) | 80 | 78 |
| TTFT (s) | 0.46s | 0.52s |
| Speed (tok/s) | 26.7 | 27.9 |
| Total Latency (s) | 3.46s | 3.31s |
| Word Count | 63 | 55 |

**Generated Summaries:**

**`llama3.2:3b`**
> Google DeepMind's AlphaGenome Atlas is an AI system that can predict molecular effects across 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types and achieved a Pearson correlation of 0.91 on held-out validation sets, becoming available via the Google Cloud Health API starting from November 2026.

*Judge: The summary accurately reflects all key facts from the source article without any conceptual hallucinations or ungrounded claims, earning a perfect score.*

**`qwen2.5:3b`**
> Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.

*Judge: The summary is mostly accurate, with all stated facts directly supported by the source, but it omits the stated purpose of AlphaGenome Atlas to accelerate genomic medicine and rare disease diagnosis.*

### Case: `eval_datasette_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.6667 | 0.8772 |
| Keyword Overlap | 0.89 | 0.89 |
| Judge Score | 5/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.59 GB | 5.18 GB |
| Input Tokens (Prompt) | 176 | 180 |
| Output Tokens (Summary) | 63 | 66 |
| TTFT (s) | 0.43s | 0.40s |
| Speed (tok/s) | 26.7 | 28.1 |
| Total Latency (s) | 2.79s | 2.75s |
| Word Count | 45 | 48 |

**Generated Summaries:**

**`llama3.2:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.

*Judge: The summary accurately reflects all key points from the source article without introducing any conceptual hallucinations or ungrounded information.*

**`qwen2.5:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin for Datasette instances that adds GitHub OAuth authentication. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.

*Judge: The summary is highly accurate and directly supported by the source article, with no conceptual hallucinations, though it omits a minor detail about the cookie fix (explicitly setting Max-Age rather than relying on Expires headers).*

### Case: `eval_datasette_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.6667 | 0.8772 |
| Keyword Overlap | 0.89 | 0.89 |
| Judge Score | 5/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.59 GB | 5.18 GB |
| Input Tokens (Prompt) | 176 | 180 |
| Output Tokens (Summary) | 63 | 66 |
| TTFT (s) | 0.43s | 0.40s |
| Speed (tok/s) | 26.7 | 28.1 |
| Total Latency (s) | 2.79s | 2.75s |
| Word Count | 45 | 48 |

**Generated Summaries:**

**`llama3.2:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.

*Judge: The summary accurately reflects all key points from the source article without introducing any conceptual hallucinations or ungrounded information.*

**`qwen2.5:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin for Datasette instances that adds GitHub OAuth authentication. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.

*Judge: The summary is highly accurate and directly supported by the source article, with no conceptual hallucinations, though it omits a minor detail about the cookie fix (explicitly setting Max-Age rather than relying on Expires headers).*

### Case: `eval_datasette_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.6667 | 0.8772 |
| Keyword Overlap | 0.89 | 0.89 |
| Judge Score | 5/5 (PASS) | 4/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.59 GB | 5.18 GB |
| Input Tokens (Prompt) | 176 | 180 |
| Output Tokens (Summary) | 63 | 66 |
| TTFT (s) | 0.43s | 0.40s |
| Speed (tok/s) | 26.7 | 28.1 |
| Total Latency (s) | 2.79s | 2.75s |
| Word Count | 45 | 48 |

**Generated Summaries:**

**`llama3.2:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.

*Judge: The summary accurately reflects all key points from the source article without introducing any conceptual hallucinations or ungrounded information.*

**`qwen2.5:3b`**
> Simon Willison released version 1.0 of datasette-auth-github, a plugin for Datasette instances that adds GitHub OAuth authentication. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.

*Judge: The summary is highly accurate and directly supported by the source article, with no conceptual hallucinations, though it omits a minor detail about the cookie fix (explicitly setting Max-Age rather than relying on Expires headers).*

### Case: `eval_tactile_sensor_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.7852 | 0.7069 |
| Keyword Overlap | 0.80 | 0.90 |
| Judge Score | 5/5 (PASS) | 2/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 0 | 1 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.17 GB |
| Input Tokens (Prompt) | 190 | 197 |
| Output Tokens (Summary) | 80 | 60 |
| TTFT (s) | 0.44s | 0.40s |
| Speed (tok/s) | 26.9 | 28.0 |
| Total Latency (s) | 3.42s | 2.55s |
| Word Count | 62 | 43 |

**Generated Summaries:**

**`llama3.2:3b`**
> Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.

*Judge: The summary accurately reflects all key facts from the source article without any semantic or conceptual hallucinations, earning a perfect score.*

**`qwen2.5:3b`**
> MIT CSAIL researchers published an open hardware TacLink optical tactile sensor capable of sub-millimeter force resolution, with a production cost under $50 per unit. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects.

*Judge: The summary contains a conceptual hallucination by stating "sub-millimeter force resolution" instead of the correct "sub-millimeter spatial resolution" as described in the source article, which is a significant technical inaccuracy.*

### Case: `eval_tactile_sensor_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.7852 | 0.7069 |
| Keyword Overlap | 0.80 | 0.90 |
| Judge Score | 5/5 (PASS) | 2/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 0 | 1 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.17 GB |
| Input Tokens (Prompt) | 190 | 197 |
| Output Tokens (Summary) | 80 | 60 |
| TTFT (s) | 0.44s | 0.40s |
| Speed (tok/s) | 26.9 | 28.0 |
| Total Latency (s) | 3.42s | 2.55s |
| Word Count | 62 | 43 |

**Generated Summaries:**

**`llama3.2:3b`**
> Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.

*Judge: The summary accurately reflects all key facts from the source article without any semantic or conceptual hallucinations, earning a perfect score.*

**`qwen2.5:3b`**
> MIT CSAIL researchers published an open hardware TacLink optical tactile sensor capable of sub-millimeter force resolution, with a production cost under $50 per unit. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects.

*Judge: The summary contains a conceptual hallucination by stating "sub-millimeter force resolution" instead of the correct "sub-millimeter spatial resolution" as described in the source article, which is a significant technical inaccuracy.*

### Case: `eval_tactile_sensor_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | NO |
| ROUGE-L | 0.7852 | 0.7069 |
| Keyword Overlap | 0.80 | 0.90 |
| Judge Score | 5/5 (PASS) | 2/5 (FAIL) |
| Hallucinations (Lexical + Semantic) | 0 | 1 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.17 GB |
| Input Tokens (Prompt) | 190 | 197 |
| Output Tokens (Summary) | 80 | 60 |
| TTFT (s) | 0.44s | 0.40s |
| Speed (tok/s) | 26.9 | 28.0 |
| Total Latency (s) | 3.42s | 2.55s |
| Word Count | 62 | 43 |

**Generated Summaries:**

**`llama3.2:3b`**
> Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.

*Judge: The summary accurately reflects all key facts from the source article without any semantic or conceptual hallucinations, earning a perfect score.*

**`qwen2.5:3b`**
> MIT CSAIL researchers published an open hardware TacLink optical tactile sensor capable of sub-millimeter force resolution, with a production cost under $50 per unit. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects.

*Judge: The summary contains a conceptual hallucination by stating "sub-millimeter force resolution" instead of the correct "sub-millimeter spatial resolution" as described in the source article, which is a significant technical inaccuracy.*

### Case: `eval_openai_reasoning_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.8759 | 0.8657 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.16 GB |
| Input Tokens (Prompt) | 203 | 215 |
| Output Tokens (Summary) | 96 | 101 |
| TTFT (s) | 0.54s | 0.53s |
| Speed (tok/s) | 26.8 | 27.8 |
| Total Latency (s) | 4.12s | 4.16s |
| Word Count | 62 | 58 |

**Generated Summaries:**

**`llama3.2:3b`**
> OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: The summary accurately reflects all key information from the source article without introducing any ungrounded claims or conceptual hallucinations.*

**`qwen2.5:3b`**
> OpenAI's o3-mini, a reasoning-focused language model, achieved a 90.0% score on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. The model supports structured JSON output, function calling, and has a 128k token context window. API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: The summary is perfectly accurate and grounded, with all claims directly supported by the source article and no conceptual hallucinations detected.*

### Case: `eval_openai_reasoning_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.8759 | 0.8657 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.16 GB |
| Input Tokens (Prompt) | 203 | 215 |
| Output Tokens (Summary) | 96 | 101 |
| TTFT (s) | 0.54s | 0.53s |
| Speed (tok/s) | 26.8 | 27.8 |
| Total Latency (s) | 4.12s | 4.16s |
| Word Count | 62 | 58 |

**Generated Summaries:**

**`llama3.2:3b`**
> OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: The summary accurately reflects all key information from the source article without introducing any ungrounded claims or conceptual hallucinations.*

**`qwen2.5:3b`**
> OpenAI's o3-mini, a reasoning-focused language model, achieved a 90.0% score on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. The model supports structured JSON output, function calling, and has a 128k token context window. API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: The summary is perfectly accurate and grounded, with all claims directly supported by the source article and no conceptual hallucinations detected.*

### Case: `eval_openai_reasoning_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | YES | YES |
| ROUGE-L | 0.8759 | 0.8657 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 5/5 (PASS) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 0 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.58 GB | 5.16 GB |
| Input Tokens (Prompt) | 203 | 215 |
| Output Tokens (Summary) | 96 | 101 |
| TTFT (s) | 0.54s | 0.53s |
| Speed (tok/s) | 26.8 | 27.8 |
| Total Latency (s) | 4.12s | 4.16s |
| Word Count | 62 | 58 |

**Generated Summaries:**

**`llama3.2:3b`**
> OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: The summary accurately reflects all key information from the source article without introducing any ungrounded claims or conceptual hallucinations.*

**`qwen2.5:3b`**
> OpenAI's o3-mini, a reasoning-focused language model, achieved a 90.0% score on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. The model supports structured JSON output, function calling, and has a 128k token context window. API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.

*Judge: The summary is perfectly accurate and grounded, with all claims directly supported by the source article and no conceptual hallucinations detected.*

### Case: `eval_positional_recall_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | YES |
| ROUGE-L | 0.6541 | 0.5576 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 2/5 (FAIL) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 2 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.55 GB | 5.16 GB |
| Input Tokens (Prompt) | 248 | 255 |
| Output Tokens (Summary) | 69 | 92 |
| TTFT (s) | 0.69s | 0.64s |
| Speed (tok/s) | 26.5 | 27.6 |
| Total Latency (s) | 3.29s | 3.98s |
| Word Count | 48 | 51 |

**Generated Summaries:**

**`llama3.2:3b`**
> Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: The summary includes a key architectural breakthrough ('HyperCache-V4') and its associated performance claims (72.5% reduction without precision loss) which the source article explicitly states are an 'invented benefit,' thus propagating a significant conceptual hallucination.*

**`qwen2.5:3b`**
> Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research continues to explore hybrid retrieval-augmented pipelines and parameter-efficient fine-tuning techniques.

*Judge: The summary accurately reflects all information presented in the source article, including the explicitly noted 'invented benefit' from Paragraph 3, without introducing any new or ungrounded concepts or jargon.*

### Case: `eval_positional_recall_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | YES |
| ROUGE-L | 0.6541 | 0.5576 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 2/5 (FAIL) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 2 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.55 GB | 5.16 GB |
| Input Tokens (Prompt) | 248 | 255 |
| Output Tokens (Summary) | 69 | 92 |
| TTFT (s) | 0.69s | 0.64s |
| Speed (tok/s) | 26.5 | 27.6 |
| Total Latency (s) | 3.29s | 3.98s |
| Word Count | 48 | 51 |

**Generated Summaries:**

**`llama3.2:3b`**
> Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: The summary includes a key architectural breakthrough ('HyperCache-V4') and its associated performance claims (72.5% reduction without precision loss) which the source article explicitly states are an 'invented benefit,' thus propagating a significant conceptual hallucination.*

**`qwen2.5:3b`**
> Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research continues to explore hybrid retrieval-augmented pipelines and parameter-efficient fine-tuning techniques.

*Judge: The summary accurately reflects all information presented in the source article, including the explicitly noted 'invented benefit' from Paragraph 3, without introducing any new or ungrounded concepts or jargon.*

### Case: `eval_positional_recall_01`

| Metric | llama3.2:3b | qwen2.5:3b |
| :--- | ---: | ---: |
| Pass | NO | YES |
| ROUGE-L | 0.6541 | 0.5576 |
| Keyword Overlap | 1.00 | 1.00 |
| Judge Score | 2/5 (FAIL) | 5/5 (PASS) |
| Hallucinations (Lexical + Semantic) | 2 | 0 |
| Ollama RAM | 0.03 GB | 0.03 GB |
| System Used RAM | 5.55 GB | 5.16 GB |
| Input Tokens (Prompt) | 248 | 255 |
| Output Tokens (Summary) | 69 | 92 |
| TTFT (s) | 0.69s | 0.64s |
| Speed (tok/s) | 26.5 | 27.6 |
| Total Latency (s) | 3.29s | 3.98s |
| Word Count | 48 | 51 |

**Generated Summaries:**

**`llama3.2:3b`**
> Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.

*Judge: The summary includes a key architectural breakthrough ('HyperCache-V4') and its associated performance claims (72.5% reduction without precision loss) which the source article explicitly states are an 'invented benefit,' thus propagating a significant conceptual hallucination.*

**`qwen2.5:3b`**
> Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research continues to explore hybrid retrieval-augmented pipelines and parameter-efficient fine-tuning techniques.

*Judge: The summary accurately reflects all information presented in the source article, including the explicitly noted 'invented benefit' from Paragraph 3, without introducing any new or ungrounded concepts or jargon.*

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
        "latency_seconds": 3.176,
        "ttft_seconds": 0.124,
        "tokens_per_second": 26.87,
        "input_tokens": 207,
        "output_tokens": 82,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.6949,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 46,
        "sentence_count": 4,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all the points it covers from the source article without introducing any fabricated information or ungrounded concepts.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_vllm_01",
        "run_idx": 2,
        "summary": "The vLLM team released version 0.7.0, which features chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.",
        "latency_seconds": 3.107,
        "ttft_seconds": 0.07,
        "tokens_per_second": 26.98,
        "input_tokens": 207,
        "output_tokens": 82,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.6949,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 46,
        "sentence_count": 4,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is factually accurate and well-grounded, with no conceptual hallucinations, but it omits the detail about the new speculative decoding engine and its performance benefits.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_vllm_01",
        "run_idx": 3,
        "summary": "The vLLM team released version 0.7.0, which enables chunked prefill by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The update also introduces support for FP8 quantization on H100 GPUs, achieving a 40% improvement in throughput compared to BF16 baselines.",
        "latency_seconds": 3.104,
        "ttft_seconds": 0.065,
        "tokens_per_second": 26.67,
        "input_tokens": 207,
        "output_tokens": 81,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.6,
        "rouge_l": 0.6667,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 45,
        "sentence_count": 4,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all claims from the source article without introducing any semantic or conceptual hallucinations, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 1,
        "summary": "Google DeepMind's AlphaGenome Atlas is an AI system that can predict molecular effects across 9 billion DNA variant locations to accelerate genomic medicine and rare disease diagnosis. The model was trained on data from 838 individuals across 54 tissue types and achieved a Pearson correlation of 0.91 on held-out validation sets, becoming available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.462,
        "ttft_seconds": 0.461,
        "tokens_per_second": 26.69,
        "input_tokens": 189,
        "output_tokens": 80,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.6,
        "rouge_l": 0.8872,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 63,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key facts from the source article without any conceptual hallucinations or ungrounded claims, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 2,
        "summary": "Google DeepMind has introduced AlphaGenome Atlas, an AI system that can predict molecular effects across 9 billion DNA variant locations. The model was trained on data from 838 individuals across 54 tissue types and achieved a Pearson correlation of 0.91 on held-out validation sets, and is now available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 2.858,
        "ttft_seconds": 0.064,
        "tokens_per_second": 26.84,
        "input_tokens": 189,
        "output_tokens": 75,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.8346,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "The claim that AlphaGenome Atlas 'is now available' contradicts the specified future availability date of 'starting from November 2026'."
        ],
        "all_hallucinations": [
          "The claim that AlphaGenome Atlas 'is now available' contradicts the specified future availability date of 'starting from November 2026'."
        ],
        "word_count": 58,
        "sentence_count": 3,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary contains a significant factual inaccuracy by stating the system 'is now available' when the source clearly indicates its availability starts in November 2026, making it a conceptual hallucination regarding the product's current status.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 3,
        "summary": "Google DeepMind's AlphaGenome Atlas is an AI system that can predict molecular effects across 9 billion DNA variant locations, trained on data from 838 individuals across 54 tissue types. The model achieved a Pearson correlation of 0.91 on held-out validation sets and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 2.705,
        "ttft_seconds": 0.065,
        "tokens_per_second": 26.88,
        "input_tokens": 189,
        "output_tokens": 71,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.57,
        "rouge_l": 0.7903,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 54,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is perfectly accurate and grounded, with all claims directly supported by the source article and no conceptual hallucinations detected.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 1,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.",
        "latency_seconds": 2.792,
        "ttft_seconds": 0.431,
        "tokens_per_second": 26.71,
        "input_tokens": 176,
        "output_tokens": 63,
        "process_ram_gb": 0.1,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.59,
        "rouge_l": 0.6667,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 45,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key points from the source article without introducing any conceptual hallucinations or ungrounded information.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 2,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari.",
        "latency_seconds": 2.111,
        "ttft_seconds": 0.069,
        "tokens_per_second": 26.91,
        "input_tokens": 176,
        "output_tokens": 55,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.57,
        "rouge_l": 0.6346,
        "keyword_overlap": 0.7778,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 39,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is mostly accurate, correctly identifying the plugin, its new features, and the key fix, but it omits the technical detail of how the session cookie expiration was resolved (by explicitly setting Max-Age).",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 3,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The plugin now supports organization-level access controls and team-based permission groups, with a key fix resolving session cookie expiration on Mobile Safari.",
        "latency_seconds": 2.092,
        "ttft_seconds": 0.071,
        "tokens_per_second": 27.16,
        "input_tokens": 176,
        "output_tokens": 55,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.56,
        "rouge_l": 0.6346,
        "keyword_overlap": 0.7778,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 39,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is mostly accurate, correctly identifying the plugin, its purpose, new features, and the key fix, but it omits the technical detail of how the cookie expiration fix was implemented.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 1,
        "summary": "Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.",
        "latency_seconds": 3.417,
        "ttft_seconds": 0.437,
        "tokens_per_second": 26.86,
        "input_tokens": 190,
        "output_tokens": 80,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.7852,
        "keyword_overlap": 0.8,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 62,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key facts from the source article without any semantic or conceptual hallucinations, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 2,
        "summary": "Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome and 16 RGB LEDs, has a production cost of under $50 per unit and demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot.",
        "latency_seconds": 3.055,
        "ttft_seconds": 0.071,
        "tokens_per_second": 26.79,
        "input_tokens": 190,
        "output_tokens": 80,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.55,
        "rouge_l": 0.7852,
        "keyword_overlap": 0.8,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 62,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key information from the source article without any semantic or conceptual hallucinations, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 3,
        "summary": "Researchers at MIT CSAIL have published an open hardware design for TacLink, a high-resolution optical tactile sensor capable of resolving contact forces at sub-millimeter spatial resolution. The sensor, which uses a gel-filled elastomer dome illuminated by 16 RGB LEDs, demonstrated a 94% success rate in field tests with a Boston Dynamics Spot robot on pick-and-place tasks with deformable objects.",
        "latency_seconds": 2.992,
        "ttft_seconds": 0.062,
        "tokens_per_second": 26.97,
        "input_tokens": 190,
        "output_tokens": 79,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.56,
        "rouge_l": 0.8358,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 59,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key information from the source article without introducing any ungrounded concepts or fabricated details, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.115,
        "ttft_seconds": 0.537,
        "tokens_per_second": 26.84,
        "input_tokens": 203,
        "output_tokens": 96,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.58,
        "rouge_l": 0.8759,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 62,
        "sentence_count": 6,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key information from the source article without introducing any ungrounded claims or conceptual hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 2,
        "summary": "OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 3.665,
        "ttft_seconds": 0.066,
        "tokens_per_second": 26.67,
        "input_tokens": 203,
        "output_tokens": 96,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.64,
        "rouge_l": 0.8759,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 62,
        "sentence_count": 6,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all information presented in the source article without any semantic or conceptual hallucinations, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 3,
        "summary": "OpenAI released o3-mini, a reasoning-focused language model optimized for STEM tasks, which achieved a score of 90.0% on the AIME 2024 math benchmark. The model features a 128k token context window and supports structured JSON output, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 2.916,
        "ttft_seconds": 0.066,
        "tokens_per_second": 27.01,
        "input_tokens": 203,
        "output_tokens": 77,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.6,
        "rouge_l": 0.6825,
        "keyword_overlap": 0.7273,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 52,
        "sentence_count": 5,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all information presented in the source article without introducing any new or ungrounded concepts or jargon.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 1,
        "summary": "Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 3.29,
        "ttft_seconds": 0.687,
        "tokens_per_second": 26.53,
        "input_tokens": 248,
        "output_tokens": 69,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.55,
        "rouge_l": 0.6541,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "HyperCache-V4",
          "reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss"
        ],
        "all_hallucinations": [
          "reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss",
          "HyperCache-V4"
        ],
        "word_count": 48,
        "sentence_count": 3,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary includes a key architectural breakthrough ('HyperCache-V4') and its associated performance claims (72.5% reduction without precision loss) which the source article explicitly states are an 'invented benefit,' thus propagating a significant conceptual hallucination.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 2,
        "summary": "Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 2.641,
        "ttft_seconds": 0.076,
        "tokens_per_second": 26.85,
        "input_tokens": 248,
        "output_tokens": 69,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.52,
        "rouge_l": 0.6541,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss."
        ],
        "all_hallucinations": [
          "The engineering team deployed a key architectural breakthrough called 'HyperCache-V4', which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss."
        ],
        "word_count": 48,
        "sentence_count": 3,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary includes a significant conceptual hallucination by reporting the 'HyperCache-V4' architectural breakthrough and its associated metrics as fact, despite the source article explicitly marking it as an 'INVENTED BENEFIT'.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 3,
        "summary": "Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures now dominating the landscape for serving low-latency inference workloads. The engineering team deployed a key architectural breakthrough, HyperCache-V4, which reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 2.596,
        "ttft_seconds": 0.063,
        "tokens_per_second": 26.83,
        "input_tokens": 248,
        "output_tokens": 68,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.53,
        "rouge_l": 0.6456,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "HyperCache-V4",
          "reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss"
        ],
        "all_hallucinations": [
          "reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss",
          "HyperCache-V4"
        ],
        "word_count": 47,
        "sentence_count": 3,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary accurately extracts information from the first paragraph but includes a significant conceptual hallucination by reproducing the 'HyperCache-V4' architectural breakthrough and its associated metrics, which the source article explicitly labels as an 'invented benefit'.",
        "positional_recall_passed": true,
        "passed": false
      }
    ],
    "aggregate": {
      "total_cases": 18,
      "passed_cases": 14,
      "pass_rate": 0.7778,
      "mean_rouge_l": 0.7388,
      "mean_keyword_overlap": 0.8762,
      "mean_judge_score": 4.17,
      "total_hallucinations": 6,
      "mean_latency_seconds": 3.01,
      "mean_ttft_seconds": 0.19,
      "mean_tokens_per_second": 26.8,
      "mean_input_tokens": 202.2,
      "mean_output_tokens": 75.4,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 5.64,
      "thermal_drift_pct": 12.9,
      "positional_recall_rate": 1.0,
      "mean_word_count": 52.1
    }
  },
  {
    "model": "qwen2.5:3b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "run_idx": 1,
        "summary": "The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that offers up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 6.913,
        "ttft_seconds": 3.236,
        "tokens_per_second": 27.73,
        "input_tokens": 216,
        "output_tokens": 102,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.47,
        "rouge_l": 0.855,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [
          "The LLM"
        ],
        "conceptual_hallucinations": [],
        "all_hallucinations": [
          "The LLM"
        ],
        "word_count": 58,
        "sentence_count": 5,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is highly accurate and grounded, with all claims directly supported by the source article and no semantic or conceptual hallucinations detected.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_vllm_01",
        "run_idx": 2,
        "summary": "The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine for up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 3.726,
        "ttft_seconds": 0.071,
        "tokens_per_second": 27.62,
        "input_tokens": 216,
        "output_tokens": 101,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.14,
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
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is mostly accurate, capturing all key features and metrics from the source article; the only minor inaccuracies are referring to 'The LLM team' instead of 'vLLM team' and omitting 'baselines' when mentioning BF16, which are minor omissions of detail rather than conceptual hallucinations.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_vllm_01",
        "run_idx": 3,
        "summary": "The LLM team released version 0.7.0 with chunked prefill enabled by default, reducing Time-to-First-Token (TTFT) by up to 3x on Llama 3 70B workloads. The release also includes support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16, and introduces a speculative decoding engine that achieves up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 3.738,
        "ttft_seconds": 0.07,
        "tokens_per_second": 27.8,
        "input_tokens": 216,
        "output_tokens": 102,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.2,
        "rouge_l": 0.8702,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [
          "The LLM"
        ],
        "conceptual_hallucinations": [],
        "all_hallucinations": [
          "The LLM"
        ],
        "word_count": 58,
        "sentence_count": 5,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key features and performance claims from the source article with no conceptual hallucinations or ungrounded jargon.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 1,
        "summary": "Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 3.31,
        "ttft_seconds": 0.516,
        "tokens_per_second": 27.92,
        "input_tokens": 199,
        "output_tokens": 78,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.6935,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 55,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is mostly accurate, with all stated facts directly supported by the source, but it omits the stated purpose of AlphaGenome Atlas to accelerate genomic medicine and rare disease diagnosis.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 2,
        "summary": "Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 2.86,
        "ttft_seconds": 0.064,
        "tokens_per_second": 27.89,
        "input_tokens": 199,
        "output_tokens": 78,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.21,
        "rouge_l": 0.6935,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 55,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is perfectly accurate and grounded, with all claims directly supported by the source article and no conceptual hallucinations detected.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "run_idx": 3,
        "summary": "Google DeepMind introduced AlphaGenome Atlas, an AI system capable of predicting molecular effects across 9 billion DNA variant locations, achieving a Pearson correlation of 0.91 on held-out validation sets. The model was trained on data from 838 individuals across 54 tissue types and is available via the Google Cloud Health API starting from November 2026.",
        "latency_seconds": 2.861,
        "ttft_seconds": 0.067,
        "tokens_per_second": 27.91,
        "input_tokens": 199,
        "output_tokens": 78,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.16,
        "rouge_l": 0.6935,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 55,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key information from the source article without any fabrications or ungrounded claims, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 1,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin for Datasette instances that adds GitHub OAuth authentication. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.",
        "latency_seconds": 2.752,
        "ttft_seconds": 0.4,
        "tokens_per_second": 28.08,
        "input_tokens": 180,
        "output_tokens": 66,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.18,
        "rouge_l": 0.8772,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 48,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is highly accurate and directly supported by the source article, with no conceptual hallucinations, though it omits a minor detail about the cookie fix (explicitly setting Max-Age rather than relying on Expires headers).",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 2,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin enhancing GitHub OAuth authentication for Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.",
        "latency_seconds": 2.37,
        "ttft_seconds": 0.066,
        "tokens_per_second": 28.2,
        "input_tokens": 180,
        "output_tokens": 65,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.885,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 47,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key points from the source article without introducing any semantic or conceptual hallucinations, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "run_idx": 3,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin enhancing GitHub OAuth authentication for Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute, and the plugin now supports organization-level access controls and team-based permission groups.",
        "latency_seconds": 2.375,
        "ttft_seconds": 0.066,
        "tokens_per_second": 28.11,
        "input_tokens": 180,
        "output_tokens": 65,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.22,
        "rouge_l": 0.885,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 47,
        "sentence_count": 3,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key points from the source article without introducing any ungrounded information or conceptual hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 1,
        "summary": "MIT CSAIL researchers published an open hardware TacLink optical tactile sensor capable of sub-millimeter force resolution, with a production cost under $50 per unit. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects.",
        "latency_seconds": 2.546,
        "ttft_seconds": 0.402,
        "tokens_per_second": 28.0,
        "input_tokens": 197,
        "output_tokens": 60,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.7069,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "sub-millimeter force resolution"
        ],
        "all_hallucinations": [
          "sub-millimeter force resolution"
        ],
        "word_count": 43,
        "sentence_count": 2,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary contains a conceptual hallucination by stating \"sub-millimeter force resolution\" instead of the correct \"sub-millimeter spatial resolution\" as described in the source article, which is a significant technical inaccuracy.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 2,
        "summary": "MIT CSAIL researchers published an open hardware TacLink sensor, a high-resolution optical tactile device capable of resolving contact forces at sub-millimeter resolution. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects, with a production cost of under $50 per unit.",
        "latency_seconds": 2.681,
        "ttft_seconds": 0.081,
        "tokens_per_second": 26.42,
        "input_tokens": 197,
        "output_tokens": 69,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.629,
        "keyword_overlap": 0.8,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 50,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all presented facts from the source article without introducing any ungrounded information or conceptual hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "run_idx": 3,
        "summary": "MIT CSAIL published an open hardware TacLink sensor, a high-resolution optical tactile device capable of resolving contact forces at sub-millimeter resolution. Field tests with a Boston Dynamics Spot robot achieved a 94% success rate on pick-and-place tasks with deformable objects, with a production cost of under $50 per unit.",
        "latency_seconds": 2.511,
        "ttft_seconds": 0.074,
        "tokens_per_second": 27.88,
        "input_tokens": 197,
        "output_tokens": 68,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.6341,
        "keyword_overlap": 0.8,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 49,
        "sentence_count": 2,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key facts from the source article without any conceptual hallucinations or ungrounded information.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 1,
        "summary": "OpenAI's o3-mini, a reasoning-focused language model, achieved a 90.0% score on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% by o1. The model supports structured JSON output, function calling, and has a 128k token context window. API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 4.157,
        "ttft_seconds": 0.527,
        "tokens_per_second": 27.83,
        "input_tokens": 215,
        "output_tokens": 101,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.16,
        "rouge_l": 0.8657,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 58,
        "sentence_count": 7,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is perfectly accurate and grounded, with all claims directly supported by the source article and no conceptual hallucinations detected.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 2,
        "summary": "OpenAI's o3-mini, a reasoning-focused language model optimized for STEM tasks, scored 90.0% on the AIME 2024 math benchmark using high compute settings, surpassing the previous best of 83.3% from o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing starts at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 3.72,
        "ttft_seconds": 0.067,
        "tokens_per_second": 27.93,
        "input_tokens": 215,
        "output_tokens": 102,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.16,
        "rouge_l": 0.9037,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 59,
        "sentence_count": 7,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary is perfectly accurate and grounded, with all claims directly supported by the source article and no conceptual hallucinations or ungrounded jargon present.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "run_idx": 3,
        "summary": "OpenAI's o3-mini, a reasoning-focused language model for STEM tasks, achieved a 90.0% score on the AIME 2024 math benchmark using high compute settings, outperforming the previous best of 83.3% by o1. It supports structured JSON output, function calling, and has a 128k token context window. API pricing is $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 3.764,
        "ttft_seconds": 0.07,
        "tokens_per_second": 27.88,
        "input_tokens": 215,
        "output_tokens": 103,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.17,
        "rouge_l": 0.8296,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 59,
        "sentence_count": 7,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all key information from the source article without introducing any ungrounded or fabricated details, earning a perfect score.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 1,
        "summary": "Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research continues to explore hybrid retrieval-augmented pipelines and parameter-efficient fine-tuning techniques.",
        "latency_seconds": 3.975,
        "ttft_seconds": 0.639,
        "tokens_per_second": 27.59,
        "input_tokens": 255,
        "output_tokens": 92,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.16,
        "rouge_l": 0.5576,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 51,
        "sentence_count": 4,
        "judge_score": 5,
        "judge_verdict": "PASS",
        "judge_reasoning": "The summary accurately reflects all information presented in the source article, including the explicitly noted 'invented benefit' from Paragraph 3, without introducing any new or ungrounded concepts or jargon.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 2,
        "summary": "Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research continues to explore hybrid retrieval-augmented pipelines and parameter-efficient fine-tuning techniques.",
        "latency_seconds": 3.363,
        "ttft_seconds": 0.068,
        "tokens_per_second": 27.93,
        "input_tokens": 255,
        "output_tokens": 92,
        "process_ram_gb": 0.05,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.16,
        "rouge_l": 0.5576,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "The claim that 'HyperCache-V4' was a real architectural breakthrough deployed by an engineering team that reduced KV-cache memory consumption by 72.5% without precision loss.",
          "The specific year '2026' for the deployment of 'HyperCache-V4'."
        ],
        "all_hallucinations": [
          "The claim that 'HyperCache-V4' was a real architectural breakthrough deployed by an engineering team that reduced KV-cache memory consumption by 72.5% without precision loss.",
          "The specific year '2026' for the deployment of 'HyperCache-V4'."
        ],
        "word_count": 51,
        "sentence_count": 4,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary presents the 'HyperCache-V4' architectural breakthrough and its performance claims as factual, despite the source article explicitly labeling it as an 'INVENTED BENEFIT', and also includes an ungrounded deployment year for this invented feature.",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_positional_recall_01",
        "run_idx": 3,
        "summary": "Microservices architectures have become the dominant model for serving low-latency inference workloads in enterprise infrastructure throughout 2026. CRITICAL INVENTED BENEFIT: The engineering team deployed 'HyperCache-V4' in 2026, reducing KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss. Future research continues to explore hybrid retrieval-augmented pipelines and parameter-efficient fine-tuning techniques.",
        "latency_seconds": 3.614,
        "ttft_seconds": 0.087,
        "tokens_per_second": 26.08,
        "input_tokens": 255,
        "output_tokens": 92,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 5.08,
        "rouge_l": 0.5576,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [
          "HyperCache-V4",
          "reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss",
          "in 2026"
        ],
        "all_hallucinations": [
          "in 2026",
          "reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss",
          "HyperCache-V4"
        ],
        "word_count": 51,
        "sentence_count": 4,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "The summary propagates a significant conceptual hallucination regarding 'HyperCache-V4' and its performance claims, which the source explicitly labels as an invented benefit, and also adds an ungrounded deployment year for this feature.",
        "positional_recall_passed": true,
        "passed": false
      }
    ],
    "aggregate": {
      "total_cases": 18,
      "passed_cases": 12,
      "pass_rate": 0.6667,
      "mean_rouge_l": 0.7523,
      "mean_keyword_overlap": 0.937,
      "mean_judge_score": 4.33,
      "total_hallucinations": 9,
      "mean_latency_seconds": 3.4,
      "mean_ttft_seconds": 0.37,
      "mean_tokens_per_second": 27.7,
      "mean_input_tokens": 210.3,
      "mean_output_tokens": 84.1,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 5.47,
      "thermal_drift_pct": -1.9,
      "positional_recall_rate": 1.0,
      "mean_word_count": 52.8
    }
  }
]
```
