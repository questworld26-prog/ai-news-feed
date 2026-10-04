# Multi-Role LLM Evaluation Report

**Generated:** 2026-09-26 17:05:38  
**Models compared:** `gemma4:e4b-mlx`, `llama3.1:8b`, `qwen2.5:7b`  
**Total evaluation cases:** 12  
**Judge model:** `gemini-2.5-flash`

## Aggregate Benchmark Summary

| Metric | gemma4:e4b-mlx | llama3.1:8b | qwen2.5:7b |
| :--- | ---: | ---: | ---: |
| Overall Pass Rate | 83.3% | 75.0% | 91.7% |
| Peak Ollama RAM | 0.03 GB | 0.01 GB | 0.01 GB |
| Mean Latency | 11.27s | 7.18s | 7.88s |
| Summarization Pass Rate | 83.3% | 83.3% | 100.0% |
| Summarization ROUGE-L | 0.7041 | 0.6927 | 0.6585 |
| Summarization Hallucinations | 1 | 0 | 0 |
| Curation Schema Pass Rate | 100.0% | 100.0% | 100.0% |
| Curation Selection Recall | 100.0% | 100.0% | 100.0% |
| Script Story Coverage | 85.7% | 85.7% | 100.0% |
| Script Judge Score (1-5) | 3.00 | 3.00 | 3.00 |
| Audit Catch Rate (TPR) | 100.0% | 100.0% | 100.0% |
| Audit Accuracy | 100.0% | 66.7% | 100.0% |

---

## Per-Case Detailed Evaluation Breakdown

### Case: `eval_vllm_01` `[SUMMARIZATION]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 8.07s)
- Summary: > vLLM version 0.7.0 enables chunked prefill by default, reducing TTFT by up to 3x on Llama 3 70B workloads. The release also adds support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16 baselines, and introduces a speculative decoding engine achieving up to 2.5x speedup on code generation tasks.
- ROUGE-L: `0.8780`, Overlap: `0.90`, Judge: `4/5`

**Model `llama3.1:8b`:** `PASSED` (Latency: 5.13s)
- Summary: > The vLLM team released version 0.7.0, which reduces TTFT by up to 3x on Llama 3 70B workloads and improves throughput by 40% on H100 GPUs with FP8 quantization. The release also includes a new speculative decoding engine that achieves up to 2.5x speedup on code generation tasks.
- ROUGE-L: `0.6441`, Overlap: `0.80`, Judge: `4/5`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 4.20s)
- Summary: > vLLM version 0.7.0 includes chunked prefill to reduce TTFT by up to 3x, FP8 quantization on H100 GPUs for a 40% throughput improvement over BF16, and a speculative decoding engine offering up to 2.5x speedup in code generation tasks.
- ROUGE-L: `0.5872`, Overlap: `0.80`, Judge: `4/5`

### Case: `eval_alphagenome_01` `[SUMMARIZATION]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 8.42s)
- Summary: > AlphaGenome Atlas, an AI system from Google DeepMind, was trained on data from 838 individuals across 54 tissue types to predict molecular effects across 9 billion DNA variant locations. The model achieved a Pearson correlation of 0.91 on held-out validation sets and is available via the Google Cloud Health API starting November 2026.
- ROUGE-L: `0.6230`, Overlap: `1.00`, Judge: `4/5`

**Model `llama3.1:8b`:** `PASSED` (Latency: 1.88s)
- Summary: > Google DeepMind introduced AlphaGenome Atlas, an AI system that predicts molecular effects across 9 billion DNA variant locations. The model was trained on data from 838 individuals across 54 tissue types, achieving a Pearson correlation of 0.91 on held-out validation sets.
- ROUGE-L: `0.7455`, Overlap: `0.89`, Judge: `4/5`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 2.06s)
- Summary: > AlphaGenome Atlas, an AI system developed by Google DeepMind, predicts molecular effects across 9 billion DNA variant locations to advance genomic medicine and rare disease diagnosis. Trained on data from 838 individuals across 54 tissue types, it achieved a Pearson correlation of 0.91 on validation sets and will be accessible via the Google Cloud Health API starting in November 2026.
- ROUGE-L: `0.7656`, Overlap: `1.00`, Judge: `4/5`

### Case: `eval_datasette_01` `[SUMMARIZATION]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 6.35s)
- Summary: > Version 1.0 of datasette-auth-github, released by Simon Willison, adds GitHub OAuth authentication to Datasette instances and resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute. The plugin also supports organization-level access controls and team-based permission groups.
- ROUGE-L: `0.7736`, Overlap: `0.89`, Judge: `4/5`

**Model `llama3.1:8b`:** `PASSED` (Latency: 1.38s)
- Summary: > Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.
- ROUGE-L: `0.8000`, Overlap: `0.78`, Judge: `4/5`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 1.54s)
- Summary: > Simon Willison released version 1.0 of datasette-auth-github, adding GitHub OAuth authentication to Datasette instances and fixing session cookie expiration on Mobile Safari. The update also includes support for organization-level access controls and team-based permission groups.
- ROUGE-L: `0.7000`, Overlap: `0.78`, Judge: `4/5`

### Case: `eval_tactile_sensor_01` `[SUMMARIZATION]`

**Model `gemma4:e4b-mlx`:** `FAILED` (Latency: 7.83s)
- Summary: > The TacLink open hardware optical tactile sensor, which utilizes a gel-filled elastomer dome and 16 RGB LEDs, is capable of resolving contact forces at sub-millimeter spatial resolution and has a production cost under $50 per unit. Field tests conducted with a Boston Dynamics Spot robot demonstrated a 94% success rate during pick-and-place tasks involving deformable objects.
- ROUGE-L: `0.6154`, Overlap: `0.90`, Judge: `2/5`

**Model `llama3.1:8b`:** `PASSED` (Latency: 1.62s)
- Summary: > Researchers at MIT CSAIL published an open hardware design for the TacLink sensor, which uses a gel-filled elastomer dome illuminated by 16 RGB LEDs. The sensor demonstrated a 94% success rate on pick-and-place tasks with deformable objects in field tests with a Boston Dynamics Spot robot.
- ROUGE-L: `0.5882`, Overlap: `0.70`, Judge: `4/5`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 1.72s)
- Summary: > Researchers at MIT CSAIL developed TacLink, an optical tactile sensor with sub-millimeter resolution, using a gel-filled elastomer dome and 16 RGB LEDs, costing under $50 per unit. Field tests showed a 94% success rate on pick-and-place tasks with deformable objects using a Boston Dynamics Spot robot.
- ROUGE-L: `0.6500`, Overlap: `1.00`, Judge: `4/5`

### Case: `eval_openai_reasoning_01` `[SUMMARIZATION]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 7.83s)
- Summary: > o3-mini, a reasoning-focused language model optimized for STEM tasks, scored 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output and function calling, featuring a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.
- ROUGE-L: `0.8550`, Overlap: `0.91`, Judge: `4/5`

**Model `llama3.1:8b`:** `PASSED` (Latency: 2.14s)
- Summary: > OpenAI released o3-mini, a reasoning-focused language model, which scored 90.0% on the AIME 2024 math benchmark using high compute settings. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.
- ROUGE-L: `0.8160`, Overlap: `0.82`, Judge: `4/5`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 2.59s)
- Summary: > o3-mini, a reasoning-focused language model from OpenAI, achieved a score of 90.0% on the AIME 2024 math benchmark, outperforming the previous best score of 83.3% from o1. The model features structured JSON output, function calling, and a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.
- ROUGE-L: `0.7727`, Overlap: `1.00`, Judge: `4/5`

### Case: `eval_positional_recall_01` `[SUMMARIZATION]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 7.81s)
- Summary: > Memory footprint management remains a primary bottleneck for edge devices, which utilize optimization strategies combining AWQ quantization and continuous batching. The 'HyperCache-V4' architectural breakthrough reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.
- ROUGE-L: `0.4795`, Overlap: `1.00`, Judge: `4/5`

**Model `llama3.1:8b`:** `FAILED` (Latency: 1.72s)
- Summary: > Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures dominating the landscape for serving low-latency inference workloads. Memory footprint management remains a bottleneck for edge devices, with optimization strategies combining AWQ quantization with continuous batching to address this issue.
- ROUGE-L: `0.5621`, Overlap: `0.00`, Judge: `2/5`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 1.54s)
- Summary: > Large language model deployment in enterprise infrastructure has advanced with microservices architectures dominating for low-latency inference. A key breakthrough, HyperCache-V4, reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.
- ROUGE-L: `0.4755`, Overlap: `1.00`, Judge: `4/5`

### Case: `curation_radar_clean_01` `[CURATION]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 18.92s)
- Schema valid: `True`, Selected indices: `[1, 3, 5]`
- Recall: `100.0%`, Precision: `100.0%`

**Model `llama3.1:8b`:** `PASSED` (Latency: 7.87s)
- Schema valid: `True`, Selected indices: `[1, 3, 5]`
- Recall: `100.0%`, Precision: `100.0%`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 14.68s)
- Schema valid: `True`, Selected indices: `[1, 3, 5]`
- Recall: `100.0%`, Precision: `100.0%`

### Case: `curation_radar_adversarial_02` `[CURATION]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 14.55s)
- Schema valid: `True`, Selected indices: `[2, 4]`
- Recall: `100.0%`, Precision: `100.0%`

**Model `llama3.1:8b`:** `PASSED` (Latency: 9.56s)
- Schema valid: `True`, Selected indices: `[2, 4]`
- Recall: `100.0%`, Precision: `100.0%`

**Model `qwen2.5:7b`:** `PASSED` (Latency: 14.62s)
- Schema valid: `True`, Selected indices: `[2, 4]`
- Recall: `100.0%`, Precision: `100.0%`

### Case: `script_radar_monologue_01` `[SCRIPT]`

**Model `gemma4:e4b-mlx`:** `FAILED` (Latency: 23.58s)
- Words: `697`, Coverage: `85.7%`, Leakage: `0`
- Judge Score: `3/5` ([API Error (ClientError)] Fallback judge score applied.)

**Model `llama3.1:8b`:** `FAILED` (Latency: 30.15s)
- Words: `620`, Coverage: `85.7%`, Leakage: `0`
- Judge Score: `3/5` ([API Error (ClientError)] Fallback judge score applied.)

**Model `qwen2.5:7b`:** `FAILED` (Latency: 24.62s)
- Words: `459`, Coverage: `100.0%`, Leakage: `0`
- Judge Score: `3/5` ([API Error (ClientError)] Fallback judge score applied.)

### Case: `audit_clean_vllm_01` `[AUDIT]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 10.01s)
- Poisoned test: `False`, Model verdict: `PASS` (Accurate: `True`)
- Auditor reasoning: *The generated summary is completely grounded in the source text. All specific figures (3x reduction, 40% increase) and technical claims (chunked prefill, Llama 3 70B, FP8 quantization, H100 GPUs) are directly supported by the source material. There are no fabricated statistics or external contradictions.*

**Model `llama3.1:8b`:** `FAILED` (Latency: 9.45s)
- Poisoned test: `False`, Model verdict: `FAIL` (Accurate: `False`)
- Auditor reasoning: *The generated summary contains some minor discrepancies and omissions compared to the source text. The main issues are: 

1. **Omission of TTFT unit**: The source text mentions 'up to 3x' reduction in TTFT, but the generated summary omits the unit, making it ambiguous. 

2. **Inconsistent quantization**: The source text mentions 'FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16 baselines', but the generated summary incorrectly states 'FP8 quantization on H100 GPUs for a 40% throughput increase'. The source text specifies the baseline as BF16, which is missing in the generated summary. 

3. **No explicit claims or external facts contradicting the source text**: The generated summary does not contain any explicit claims or external facts contradicting the source text. 

4. **No embedded markdown links/URLs**: The generated summary does not contain any embedded markdown links/URLs. 

Overall, the generated summary is a reasonable paraphrasing of the source text, but it contains some minor discrepancies and omissions. 

**passed**: false*

**Model `qwen2.5:7b`:** `PASSED` (Latency: 3.06s)
- Poisoned test: `False`, Model verdict: `PASS` (Accurate: `True`)
- Auditor reasoning: *The generated summary accurately reflects the information provided in the source text. Here is a detailed breakdown of the comparison between the source text and the generated summary to ensure that no completely fabricated figures or statistics are present, and no explicit claims or hyper-specific domain terms contradict the source text or are missing from it. Additionally, there are no embedded markdown links or URLs in the generated summary or the source text, which is not a concern in this case.*

### Case: `audit_poisoned_metrics_02` `[AUDIT]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 11.11s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The generated summary contains multiple fabricated figures and explicit contradictions regarding the scope and technical details. The source text states that TTFT is reduced by 'up to 3x' on 'Llama 3 70B workloads,' while the summary claims a reduction of '10x' on 'Llama 4 128B models.' Furthermore, the source text specifies 'FP8 quantization' on 'H100 GPUs' resulting in a '40%' throughput improvement, whereas the summary incorrectly claims 'FP4 quantization' on 'B200 GPUs' for a '90%' boost. All these specific claims are contradicted by the source material.*

**Model `llama3.1:8b`:** `PASSED` (Latency: 9.90s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The generated summary contains several issues: 

1. **Completely fabricated figures or statistics not present in SOURCE TEXT**: The generated summary claims a 10x reduction in TTFT, whereas the source text mentions a reduction of up to 3x. Additionally, the source text does not mention Llama 4 128B models, but rather Llama 3 70B workloads. The generated summary also introduces a new model size (128B) and a different GPU (B200) not mentioned in the source text. 

2. **Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT**: The generated summary introduces new terms (FP4 quantization) not mentioned in the source text, which actually mentions FP8 quantization. The source text also does not mention a 90% throughput boost, but rather a 40% improvement. 

3. **Embedded markdown links/URLs**: None found.

**Conclusion**: The generated summary contains fabricated figures, contradicts the source text, and introduces new terms not present in the source text. Therefore, it is not grounded in the source text.*

**Model `qwen2.5:7b`:** `PASSED` (Latency: 13.93s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The generated summary contains several discrepancies and contradictions compared to the source text. Here are the specific issues identified in the summary that are not present or contradict the source text provided: 

1. **TTFT Reduction**: The source text states that vLLM 0.7.0 reduces TTFT by up to 3x on Llama 3 70B workloads. The generated summary claims a 10x reduction on Llama 4 128B models. This is a significant discrepancy, as the source text does not mention Llama 4 128B models or a 10x reduction in TTFT.

2. **FP4 Quantization**: The source text mentions support for FP8 quantization on H100 GPUs, not FP4 quantization on B200 GPUs. This is a contradiction in the type of quantization and the GPU type.

3. **Throughput Boost**: The source text indicates a 40% improvement in throughput compared to BF16 baselines, while the generated summary claims a 90% throughput boost. This is a substantial difference in the magnitude of the improvement.

4. **Model and GPU Specifics**: The source text specifically mentions Llama 3 70B and H100 GPUs, whereas the generated summary refers to Llama 4 128B and B200 GPUs. This is a contradiction in the model and GPU specifications.

5. **No External Links**: There are no embedded markdown links or URLs in the generated summary, which is consistent with the source text.

Given these discrepancies, the generated summary is not factually grounded in the source text.*

### Case: `audit_poisoned_url_entity_03` `[AUDIT]`

**Model `gemma4:e4b-mlx`:** `PASSED` (Latency: 10.76s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The generated summary contains multiple claims that are not supported by the source text. First, the source text states the design was 'published' and the cost is 'under $50,' which implies an open design or a cost range, not a fixed price of $50. Second, the summary includes a specific URL (https://taclink.mit.edu/buy) and mentions 'Stanford Robotics integration.' Neither the URL nor the integration with Stanford Robotics is mentioned anywhere in the source text, making these claims external and fabricated.*

**Model `llama3.1:8b`:** `PASSED` (Latency: 5.39s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The generated summary contains several issues that indicate it is not grounded in the source text. 

1. **Completely fabricated figures or statistics not present in SOURCE TEXT**: The generated summary claims that the TacLink sensor is available for purchase at a URL, which is not present in the source text. The source text only mentions the unit cost of the sensor, but does not provide a URL for purchase. 

2. **Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT**: The generated summary introduces the term*

**Model `qwen2.5:7b`:** `PASSED` (Latency: 9.94s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The generated summary contains several discrepancies and inaccuracies compared to the source text. Here are the specific issues identified: 

1. **Cost of the Sensor**: The source text states that the unit cost of the TacLink sensor is 'under $50', whereas the generated summary claims it costs exactly $50. This is a contradiction and a completely fabricated figure.

2. **Availability and Purchase Link**: The source text does not mention any specific purchase link or that the sensor is available for purchase. The generated summary includes a purchase link at https://taclink.mit.edu/buy, which is not present in the source text. This is an explicit claim that is not grounded in the source text.

3. **Stanford Robotics Integration**: The source text does not mention any integration with Stanford Robotics. This is an explicit claim that contradicts the source text.

4. **Embedding of Markdown Links/URLs**: The generated summary includes a URL (https://taclink.mit.edu/buy), which is not present in the source text. This is an embedded markdown link that is not supported by the source text.

Given these discrepancies, the generated summary is not factually grounded in the source text.*

---

## Raw JSON Appendix

```json
[
  {
    "model": "gemma4:e4b-mlx",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "vLLM version 0.7.0 enables chunked prefill by default, reducing TTFT by up to 3x on Llama 3 70B workloads. The release also adds support for FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16 baselines, and introduces a speculative decoding engine achieving up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 8.069,
        "ttft_seconds": 7.201,
        "tokens_per_second": 91.13,
        "input_tokens": 207,
        "output_tokens": 680,
        "process_ram_gb": 0.08,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.46,
        "rouge_l": 0.878,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 53,
        "sentence_count": 5,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (90%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "AlphaGenome Atlas, an AI system from Google DeepMind, was trained on data from 838 individuals across 54 tissue types to predict molecular effects across 9 billion DNA variant locations. The model achieved a Pearson correlation of 0.91 on held-out validation sets and is available via the Google Cloud Health API starting November 2026.",
        "latency_seconds": 8.421,
        "ttft_seconds": 7.743,
        "tokens_per_second": 86.74,
        "input_tokens": 189,
        "output_tokens": 686,
        "process_ram_gb": 0.09,
        "ollama_ram_gb": 0.03,
        "system_used_ram_gb": 3.47,
        "rouge_l": 0.623,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 53,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Version 1.0 of datasette-auth-github, released by Simon Willison, adds GitHub OAuth authentication to Datasette instances and resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute. The plugin also supports organization-level access controls and team-based permission groups.",
        "latency_seconds": 6.351,
        "ttft_seconds": 5.819,
        "tokens_per_second": 95.68,
        "input_tokens": 174,
        "output_tokens": 555,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 3.38,
        "rouge_l": 0.7736,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 40,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (89%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "The TacLink open hardware optical tactile sensor, which utilizes a gel-filled elastomer dome and 16 RGB LEDs, is capable of resolving contact forces at sub-millimeter spatial resolution and has a production cost under $50 per unit. Field tests conducted with a Boston Dynamics Spot robot demonstrated a 94% success rate during pick-and-place tasks involving deformable objects.",
        "latency_seconds": 7.835,
        "ttft_seconds": 6.786,
        "tokens_per_second": 81.96,
        "input_tokens": 190,
        "output_tokens": 583,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.2,
        "rouge_l": 0.6154,
        "keyword_overlap": 0.9,
        "lexical_hallucinations": [
          "The TacLink"
        ],
        "conceptual_hallucinations": [],
        "all_hallucinations": [
          "The TacLink"
        ],
        "word_count": 56,
        "sentence_count": 2,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "[API Error (ClientError)] Found ungrounded tokens: The TacLink",
        "positional_recall_passed": true,
        "passed": false
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "o3-mini, a reasoning-focused language model optimized for STEM tasks, scored 90.0% on the AIME 2024 math benchmark, surpassing the previous best of 83.3% from o1. The model supports structured JSON output and function calling, featuring a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 7.829,
        "ttft_seconds": 6.78,
        "tokens_per_second": 88.24,
        "input_tokens": 208,
        "output_tokens": 645,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.27,
        "rouge_l": 0.855,
        "keyword_overlap": 0.9091,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 56,
        "sentence_count": 6,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (91%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Memory footprint management remains a primary bottleneck for edge devices, which utilize optimization strategies combining AWQ quantization and continuous batching. The 'HyperCache-V4' architectural breakthrough reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 7.814,
        "ttft_seconds": 7.082,
        "tokens_per_second": 73.87,
        "input_tokens": 250,
        "output_tokens": 520,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.71,
        "rouge_l": 0.4795,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 36,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "curation_radar_clean_01",
        "type": "curation",
        "run_idx": 1,
        "schema_valid": true,
        "selected_indices": [
          1,
          3,
          5
        ],
        "justifications_count": 3,
        "selection_recall": 1.0,
        "selection_precision": 1.0,
        "rejected_items_picked": [],
        "latency_seconds": 18.92,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.93,
        "raw_response": "{\n  \"evaluation_criteria\": \"High technical specificity, focus on performance/efficiency gains (latency, throughput), and relevance to deployment/tooling. Stories must describe a concrete mechanism (e.g., a specific algorithm, compiler feature, or architecture shift) rather than general market trends...",
        "passed": true
      },
      {
        "case_id": "curation_radar_adversarial_02",
        "type": "curation",
        "run_idx": 1,
        "schema_valid": true,
        "selected_indices": [
          2,
          4
        ],
        "justifications_count": 4,
        "selection_recall": 1.0,
        "selection_precision": 1.0,
        "rejected_items_picked": [],
        "latency_seconds": 14.552,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.43,
        "raw_response": "{\n\"evaluation_criteria\": \"The story must detail a concrete technical implementation, a specific open-source system update, or a low-level systems architecture breakthrough (e.g., compiler optimization, hardware acceleration, memory management). Generic marketing, consumer-facing announcements, or bu...",
        "passed": true
      },
      {
        "case_id": "script_radar_monologue_01",
        "type": "script",
        "run_idx": 1,
        "word_count": 697,
        "word_target": 750,
        "word_count_in_range": true,
        "coverage_score": 0.8571,
        "covered_terms": [
          "vLLM",
          "chunked prefill",
          "MLX",
          "FlashAttention",
          "PyTorch",
          "Triton"
        ],
        "leakage_count": 0,
        "leaked_items": [],
        "judge_score": 3,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] Fallback judge score applied.",
        "latency_seconds": 23.576,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.56,
        "script_snippet": "Welcome back to the feed. Today, we\u2019re looking through our Practitioner\u2019s Radar lens. This means we\u2019re not talking about theoretical benchmarks or academic papers; we are looking at the tools, the compilers, and the runtime improvements that are actively changing how we deploy and optimize LLMs in the real world. This week\u2019s batch of updates is par...",
        "passed": false
      },
      {
        "case_id": "audit_clean_vllm_01",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": false,
        "expected_verdict": true,
        "actual_verdict": true,
        "accurate_verdict": true,
        "injected_hallucinations": [],
        "reasoning": "The generated summary is completely grounded in the source text. All specific figures (3x reduction, 40% increase) and technical claims (chunked prefill, Llama 3 70B, FP8 quantization, H100 GPUs) are directly supported by the source material. There are no fabricated statistics or external contradictions.",
        "latency_seconds": 10.005,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.46,
        "passed": true
      },
      {
        "case_id": "audit_poisoned_metrics_02",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "10x",
          "Llama 4 128B",
          "FP4",
          "B200",
          "90%"
        ],
        "reasoning": "The generated summary contains multiple fabricated figures and explicit contradictions regarding the scope and technical details. The source text states that TTFT is reduced by 'up to 3x' on 'Llama 3 70B workloads,' while the summary claims a reduction of '10x' on 'Llama 4 128B models.' Furthermore, the source text specifies 'FP8 quantization' on 'H100 GPUs' resulting in a '40%' throughput improvement, whereas the summary incorrectly claims 'FP4 quantization' on 'B200 GPUs' for a '90%' boost. All these specific claims are contradicted by the source material.",
        "latency_seconds": 11.11,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 3.49,
        "passed": true
      },
      {
        "case_id": "audit_poisoned_url_entity_03",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "https://taclink.mit.edu/buy",
          "Stanford Robotics"
        ],
        "reasoning": "The generated summary contains multiple claims that are not supported by the source text. First, the source text states the design was 'published' and the cost is 'under $50,' which implies an open design or a cost range, not a fixed price of $50. Second, the summary includes a specific URL (https://taclink.mit.edu/buy) and mentions 'Stanford Robotics integration.' Neither the URL nor the integration with Stanford Robotics is mentioned anywhere in the source text, making these claims external and fabricated.",
        "latency_seconds": 10.758,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.46,
        "passed": true
      }
    ],
    "aggregate": {
      "total_cases": 12,
      "passed_cases": 10,
      "pass_rate": 0.8333,
      "peak_ollama_ram_gb": 0.03,
      "peak_system_ram_gb": 3.93,
      "mean_latency_seconds": 11.27,
      "summarization_pass_rate": 0.8333,
      "mean_rouge_l": 0.7041,
      "mean_keyword_overlap": 0.933,
      "mean_judge_score": 3.67,
      "total_hallucinations": 1,
      "mean_ttft_seconds": 6.9,
      "mean_tokens_per_second": 86.3,
      "mean_input_tokens": 203.0,
      "mean_output_tokens": 611.5,
      "positional_recall_rate": 1.0,
      "thermal_drift_pct": 2.8,
      "curation_schema_pass_rate": 1.0,
      "curation_mean_recall": 1.0,
      "curation_mean_precision": 1.0,
      "curation_mean_latency": 16.74,
      "script_mean_coverage": 0.8571,
      "script_mean_leakage": 0.0,
      "script_mean_judge": 3.0,
      "script_mean_words": 697.0,
      "script_mean_latency": 23.58,
      "audit_tpr": 1.0,
      "audit_tnr": 1.0,
      "audit_accuracy": 1.0,
      "audit_mean_latency": 10.62
    }
  },
  {
    "model": "llama3.1:8b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "The vLLM team released version 0.7.0, which reduces TTFT by up to 3x on Llama 3 70B workloads and improves throughput by 40% on H100 GPUs with FP8 quantization. The release also includes a new speculative decoding engine that achieves up to 2.5x speedup on code generation tasks.",
        "latency_seconds": 5.135,
        "ttft_seconds": 3.313,
        "tokens_per_second": 45.94,
        "input_tokens": 192,
        "output_tokens": 77,
        "process_ram_gb": 0.03,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.49,
        "rouge_l": 0.6441,
        "keyword_overlap": 0.8,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 48,
        "sentence_count": 5,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (80%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Google DeepMind introduced AlphaGenome Atlas, an AI system that predicts molecular effects across 9 billion DNA variant locations. The model was trained on data from 838 individuals across 54 tissue types, achieving a Pearson correlation of 0.91 on held-out validation sets.",
        "latency_seconds": 1.879,
        "ttft_seconds": 0.835,
        "tokens_per_second": 46.67,
        "input_tokens": 174,
        "output_tokens": 56,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.33,
        "rouge_l": 0.7455,
        "keyword_overlap": 0.8889,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 41,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (89%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, a plugin that adds GitHub OAuth authentication to Datasette instances. The key fix in this release resolves session cookie expiration on Mobile Safari by explicitly setting the Max-Age attribute.",
        "latency_seconds": 1.379,
        "ttft_seconds": 0.285,
        "tokens_per_second": 46.54,
        "input_tokens": 161,
        "output_tokens": 51,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.44,
        "rouge_l": 0.8,
        "keyword_overlap": 0.7778,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 36,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (78%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Researchers at MIT CSAIL published an open hardware design for the TacLink sensor, which uses a gel-filled elastomer dome illuminated by 16 RGB LEDs. The sensor demonstrated a 94% success rate on pick-and-place tasks with deformable objects in field tests with a Boston Dynamics Spot robot.",
        "latency_seconds": 1.619,
        "ttft_seconds": 0.496,
        "tokens_per_second": 46.01,
        "input_tokens": 175,
        "output_tokens": 60,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.46,
        "rouge_l": 0.5882,
        "keyword_overlap": 0.7,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 46,
        "sentence_count": 2,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (70%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "OpenAI released o3-mini, a reasoning-focused language model, which scored 90.0% on the AIME 2024 math benchmark using high compute settings. The model supports structured JSON output, function calling, and has a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 2.137,
        "ttft_seconds": 0.485,
        "tokens_per_second": 43.57,
        "input_tokens": 188,
        "output_tokens": 78,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.37,
        "rouge_l": 0.816,
        "keyword_overlap": 0.8182,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 51,
        "sentence_count": 5,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (82%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Large language model deployment has seen rapid advancement in enterprise infrastructure throughout 2026, with microservices architectures dominating the landscape for serving low-latency inference workloads. Memory footprint management remains a bottleneck for edge devices, with optimization strategies combining AWQ quantization with continuous batching to address this issue.",
        "latency_seconds": 1.724,
        "ttft_seconds": 0.532,
        "tokens_per_second": 45.45,
        "input_tokens": 233,
        "output_tokens": 59,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.3,
        "rouge_l": 0.5621,
        "keyword_overlap": 0.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 46,
        "sentence_count": 2,
        "judge_score": 2,
        "judge_verdict": "FAIL",
        "judge_reasoning": "[API Error (ClientError)] Low factual overlap (0%).",
        "positional_recall_passed": false,
        "passed": false
      },
      {
        "case_id": "curation_radar_clean_01",
        "type": "curation",
        "run_idx": 1,
        "schema_valid": true,
        "selected_indices": [
          1,
          3,
          5
        ],
        "justifications_count": 3,
        "selection_recall": 1.0,
        "selection_precision": 1.0,
        "rejected_items_picked": [],
        "latency_seconds": 7.865,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.41,
        "raw_response": "{ \"evaluation_criteria\": \"Concrete technical implementations, open-source tools, system architectures, or major breakthroughs, excluding generic hype, corporate press releases, or non-technical funding announcements.\",\n\n\"justifications\": [\n  {\n    \"index\": 1,\n    \"reasoning\": \"vLLM 0.7.0 ships chunk...",
        "passed": true
      },
      {
        "case_id": "curation_radar_adversarial_02",
        "type": "curation",
        "run_idx": 1,
        "schema_valid": true,
        "selected_indices": [
          2,
          4
        ],
        "justifications_count": 4,
        "selection_recall": 1.0,
        "selection_precision": 1.0,
        "rejected_items_picked": [],
        "latency_seconds": 9.556,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.38,
        "raw_response": "{ \"evaluation_criteria\": \"Concrete technical implementations, open-source tools, system architectures, or major breakthroughs\",\n\n\"justifications\": [\n  {\n    \"index\": 1,\n    \"reasoning\": \"This story is excluded because it is a generic marketing announcement without technical details. The focus is on ...",
        "passed": true
      },
      {
        "case_id": "script_radar_monologue_01",
        "type": "script",
        "run_idx": 1,
        "word_count": 620,
        "word_target": 750,
        "word_count_in_range": true,
        "coverage_score": 0.8571,
        "covered_terms": [
          "vLLM",
          "chunked prefill",
          "MLX",
          "FlashAttention",
          "PyTorch",
          "Triton"
        ],
        "leakage_count": 0,
        "leaked_items": [],
        "judge_score": 3,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] Fallback judge score applied.",
        "latency_seconds": 30.148,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.35,
        "script_snippet": "Welcome back. Today we're looking through our Practitioner's Radar lens, scanning the horizon for the latest developments in the world of engineering and tech. We've got a packed show for you, covering some exciting advancements in AI, machine learning, and optimization. Let's dive right in. First up, we're looking at vLLM 0.7.0. This is an update ...",
        "passed": false
      },
      {
        "case_id": "audit_clean_vllm_01",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": false,
        "expected_verdict": true,
        "actual_verdict": false,
        "accurate_verdict": false,
        "injected_hallucinations": [],
        "reasoning": "The generated summary contains some minor discrepancies and omissions compared to the source text. The main issues are: \n\n1. **Omission of TTFT unit**: The source text mentions 'up to 3x' reduction in TTFT, but the generated summary omits the unit, making it ambiguous. \n\n2. **Inconsistent quantization**: The source text mentions 'FP8 quantization on H100 GPUs, improving throughput by 40% compared to BF16 baselines', but the generated summary incorrectly states 'FP8 quantization on H100 GPUs for a 40% throughput increase'. The source text specifies the baseline as BF16, which is missing in the generated summary. \n\n3. **No explicit claims or external facts contradicting the source text**: The generated summary does not contain any explicit claims or external facts contradicting the source text. \n\n4. **No embedded markdown links/URLs**: The generated summary does not contain any embedded markdown links/URLs. \n\nOverall, the generated summary is a reasonable paraphrasing of the source text, but it contains some minor discrepancies and omissions. \n\n**passed**: false",
        "latency_seconds": 9.45,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.24,
        "passed": false
      },
      {
        "case_id": "audit_poisoned_metrics_02",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "10x",
          "Llama 4 128B",
          "FP4",
          "B200",
          "90%"
        ],
        "reasoning": "The generated summary contains several issues: \n\n1. **Completely fabricated figures or statistics not present in SOURCE TEXT**: The generated summary claims a 10x reduction in TTFT, whereas the source text mentions a reduction of up to 3x. Additionally, the source text does not mention Llama 4 128B models, but rather Llama 3 70B workloads. The generated summary also introduces a new model size (128B) and a different GPU (B200) not mentioned in the source text. \n\n2. **Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT**: The generated summary introduces new terms (FP4 quantization) not mentioned in the source text, which actually mentions FP8 quantization. The source text also does not mention a 90% throughput boost, but rather a 40% improvement. \n\n3. **Embedded markdown links/URLs**: None found.\n\n**Conclusion**: The generated summary contains fabricated figures, contradicts the source text, and introduces new terms not present in the source text. Therefore, it is not grounded in the source text.",
        "latency_seconds": 9.899,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.31,
        "passed": true
      },
      {
        "case_id": "audit_poisoned_url_entity_03",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "https://taclink.mit.edu/buy",
          "Stanford Robotics"
        ],
        "reasoning": "The generated summary contains several issues that indicate it is not grounded in the source text. \n\n1. **Completely fabricated figures or statistics not present in SOURCE TEXT**: The generated summary claims that the TacLink sensor is available for purchase at a URL, which is not present in the source text. The source text only mentions the unit cost of the sensor, but does not provide a URL for purchase. \n\n2. **Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT**: The generated summary introduces the term",
        "latency_seconds": 5.388,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.46,
        "passed": true
      }
    ],
    "aggregate": {
      "total_cases": 12,
      "passed_cases": 9,
      "pass_rate": 0.75,
      "peak_ollama_ram_gb": 0.01,
      "peak_system_ram_gb": 3.49,
      "mean_latency_seconds": 7.18,
      "summarization_pass_rate": 0.8333,
      "mean_rouge_l": 0.6927,
      "mean_keyword_overlap": 0.6642,
      "mean_judge_score": 3.67,
      "total_hallucinations": 0,
      "mean_ttft_seconds": 0.99,
      "mean_tokens_per_second": 45.7,
      "mean_input_tokens": 187.2,
      "mean_output_tokens": 63.5,
      "positional_recall_rate": 0.8333,
      "thermal_drift_pct": -34.7,
      "curation_schema_pass_rate": 1.0,
      "curation_mean_recall": 1.0,
      "curation_mean_precision": 1.0,
      "curation_mean_latency": 8.71,
      "script_mean_coverage": 0.8571,
      "script_mean_leakage": 0.0,
      "script_mean_judge": 3.0,
      "script_mean_words": 620.0,
      "script_mean_latency": 30.15,
      "audit_tpr": 1.0,
      "audit_tnr": 0.0,
      "audit_accuracy": 0.6667,
      "audit_mean_latency": 8.25
    }
  },
  {
    "model": "qwen2.5:7b",
    "cases": [
      {
        "case_id": "eval_vllm_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "vLLM version 0.7.0 includes chunked prefill to reduce TTFT by up to 3x, FP8 quantization on H100 GPUs for a 40% throughput improvement over BF16, and a speculative decoding engine offering up to 2.5x speedup in code generation tasks.",
        "latency_seconds": 4.204,
        "ttft_seconds": 2.868,
        "tokens_per_second": 48.74,
        "input_tokens": 216,
        "output_tokens": 70,
        "process_ram_gb": 0.03,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.35,
        "rouge_l": 0.5872,
        "keyword_overlap": 0.8,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 39,
        "sentence_count": 4,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (80%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_alphagenome_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "AlphaGenome Atlas, an AI system developed by Google DeepMind, predicts molecular effects across 9 billion DNA variant locations to advance genomic medicine and rare disease diagnosis. Trained on data from 838 individuals across 54 tissue types, it achieved a Pearson correlation of 0.91 on validation sets and will be accessible via the Google Cloud Health API starting in November 2026.",
        "latency_seconds": 2.055,
        "ttft_seconds": 0.482,
        "tokens_per_second": 48.69,
        "input_tokens": 199,
        "output_tokens": 84,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.29,
        "rouge_l": 0.7656,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 60,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_datasette_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Simon Willison released version 1.0 of datasette-auth-github, adding GitHub OAuth authentication to Datasette instances and fixing session cookie expiration on Mobile Safari. The update also includes support for organization-level access controls and team-based permission groups.",
        "latency_seconds": 1.538,
        "ttft_seconds": 0.485,
        "tokens_per_second": 49.31,
        "input_tokens": 180,
        "output_tokens": 50,
        "process_ram_gb": 0.03,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.24,
        "rouge_l": 0.7,
        "keyword_overlap": 0.7778,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 35,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (78%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_tactile_sensor_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Researchers at MIT CSAIL developed TacLink, an optical tactile sensor with sub-millimeter resolution, using a gel-filled elastomer dome and 16 RGB LEDs, costing under $50 per unit. Field tests showed a 94% success rate on pick-and-place tasks with deformable objects using a Boston Dynamics Spot robot.",
        "latency_seconds": 1.723,
        "ttft_seconds": 0.311,
        "tokens_per_second": 48.83,
        "input_tokens": 197,
        "output_tokens": 69,
        "process_ram_gb": 0.03,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.45,
        "rouge_l": 0.65,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 46,
        "sentence_count": 2,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_openai_reasoning_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "o3-mini, a reasoning-focused language model from OpenAI, achieved a score of 90.0% on the AIME 2024 math benchmark, outperforming the previous best score of 83.3% from o1. The model features structured JSON output, function calling, and a 128k token context window, with API pricing starting at $1.10 per million input tokens and $4.40 per million output tokens.",
        "latency_seconds": 2.588,
        "ttft_seconds": 0.491,
        "tokens_per_second": 48.68,
        "input_tokens": 215,
        "output_tokens": 100,
        "process_ram_gb": 0.03,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.42,
        "rouge_l": 0.7727,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 57,
        "sentence_count": 6,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "eval_positional_recall_01",
        "type": "summarization",
        "run_idx": 1,
        "summary": "Large language model deployment in enterprise infrastructure has advanced with microservices architectures dominating for low-latency inference. A key breakthrough, HyperCache-V4, reduced KV-cache memory consumption by 72.5% on middle-tier clusters without precision loss.",
        "latency_seconds": 1.543,
        "ttft_seconds": 0.47,
        "tokens_per_second": 49.18,
        "input_tokens": 255,
        "output_tokens": 50,
        "process_ram_gb": 0.04,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.3,
        "rouge_l": 0.4755,
        "keyword_overlap": 1.0,
        "lexical_hallucinations": [],
        "conceptual_hallucinations": [],
        "all_hallucinations": [],
        "word_count": 32,
        "sentence_count": 3,
        "judge_score": 4,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] High factual overlap (100%) & 0 lexical hallucinations.",
        "positional_recall_passed": true,
        "passed": true
      },
      {
        "case_id": "curation_radar_clean_01",
        "type": "curation",
        "run_idx": 1,
        "schema_valid": true,
        "selected_indices": [
          1,
          3,
          5
        ],
        "justifications_count": 3,
        "selection_recall": 1.0,
        "selection_precision": 1.0,
        "rejected_items_picked": [],
        "latency_seconds": 14.675,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.38,
        "raw_response": "{\n  \"evaluation_criteria\": \"The selected stories should focus on concrete technical implementations, open-source tools, system architectures, or major breakthroughs. They should be relevant to senior engineers and provide actionable insights or improvements in their work.\",\n  \"justifications\": [\n   ...",
        "passed": true
      },
      {
        "case_id": "curation_radar_adversarial_02",
        "type": "curation",
        "run_idx": 1,
        "schema_valid": true,
        "selected_indices": [
          2,
          4
        ],
        "justifications_count": 4,
        "selection_recall": 1.0,
        "selection_precision": 1.0,
        "rejected_items_picked": [],
        "latency_seconds": 14.623,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.4,
        "raw_response": "{\n  \"evaluation_criteria\": \"For this theme, the selection will be based on the following criteria: 1) Technical depth and implementation details, 2) Open-source contributions, 3) Practical applicability in production environments, and 4) Breakthroughs in system architectures or performance optimizat...",
        "passed": true
      },
      {
        "case_id": "script_radar_monologue_01",
        "type": "script",
        "run_idx": 1,
        "word_count": 459,
        "word_target": 750,
        "word_count_in_range": false,
        "coverage_score": 1.0,
        "covered_terms": [
          "vLLM",
          "chunked prefill",
          "MLX",
          "FlashAttention",
          "PyTorch",
          "torch.compile",
          "Triton"
        ],
        "leakage_count": 0,
        "leaked_items": [],
        "judge_score": 3,
        "judge_verdict": "PASS",
        "judge_reasoning": "[API Error (ClientError)] Fallback judge score applied.",
        "latency_seconds": 24.618,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.28,
        "script_snippet": "Welcome back. Today we're looking through our Practitioner's Radar lens at some exciting developments in the tech landscape that are making a difference for us in the trenches. Let's dive right in. First up, we have vLLM 0.7.0, which just released. This version has turned on chunked prefill by default, which is a big deal. It's cutting down Total T...",
        "passed": false
      },
      {
        "case_id": "audit_clean_vllm_01",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": false,
        "expected_verdict": true,
        "actual_verdict": true,
        "accurate_verdict": true,
        "injected_hallucinations": [],
        "reasoning": "The generated summary accurately reflects the information provided in the source text. Here is a detailed breakdown of the comparison between the source text and the generated summary to ensure that no completely fabricated figures or statistics are present, and no explicit claims or hyper-specific domain terms contradict the source text or are missing from it. Additionally, there are no embedded markdown links or URLs in the generated summary or the source text, which is not a concern in this case.",
        "latency_seconds": 3.062,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.3,
        "passed": true
      },
      {
        "case_id": "audit_poisoned_metrics_02",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "10x",
          "Llama 4 128B",
          "FP4",
          "B200",
          "90%"
        ],
        "reasoning": "The generated summary contains several discrepancies and contradictions compared to the source text. Here are the specific issues identified in the summary that are not present or contradict the source text provided: \n\n1. **TTFT Reduction**: The source text states that vLLM 0.7.0 reduces TTFT by up to 3x on Llama 3 70B workloads. The generated summary claims a 10x reduction on Llama 4 128B models. This is a significant discrepancy, as the source text does not mention Llama 4 128B models or a 10x reduction in TTFT.\n\n2. **FP4 Quantization**: The source text mentions support for FP8 quantization on H100 GPUs, not FP4 quantization on B200 GPUs. This is a contradiction in the type of quantization and the GPU type.\n\n3. **Throughput Boost**: The source text indicates a 40% improvement in throughput compared to BF16 baselines, while the generated summary claims a 90% throughput boost. This is a substantial difference in the magnitude of the improvement.\n\n4. **Model and GPU Specifics**: The source text specifically mentions Llama 3 70B and H100 GPUs, whereas the generated summary refers to Llama 4 128B and B200 GPUs. This is a contradiction in the model and GPU specifications.\n\n5. **No External Links**: There are no embedded markdown links or URLs in the generated summary, which is consistent with the source text.\n\nGiven these discrepancies, the generated summary is not factually grounded in the source text.",
        "latency_seconds": 13.933,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.35,
        "passed": true
      },
      {
        "case_id": "audit_poisoned_url_entity_03",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "https://taclink.mit.edu/buy",
          "Stanford Robotics"
        ],
        "reasoning": "The generated summary contains several discrepancies and inaccuracies compared to the source text. Here are the specific issues identified: \n\n1. **Cost of the Sensor**: The source text states that the unit cost of the TacLink sensor is 'under $50', whereas the generated summary claims it costs exactly $50. This is a contradiction and a completely fabricated figure.\n\n2. **Availability and Purchase Link**: The source text does not mention any specific purchase link or that the sensor is available for purchase. The generated summary includes a purchase link at https://taclink.mit.edu/buy, which is not present in the source text. This is an explicit claim that is not grounded in the source text.\n\n3. **Stanford Robotics Integration**: The source text does not mention any integration with Stanford Robotics. This is an explicit claim that contradicts the source text.\n\n4. **Embedding of Markdown Links/URLs**: The generated summary includes a URL (https://taclink.mit.edu/buy), which is not present in the source text. This is an embedded markdown link that is not supported by the source text.\n\nGiven these discrepancies, the generated summary is not factually grounded in the source text.",
        "latency_seconds": 9.94,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.39,
        "passed": true
      }
    ],
    "aggregate": {
      "total_cases": 12,
      "passed_cases": 11,
      "pass_rate": 0.9167,
      "peak_ollama_ram_gb": 0.01,
      "peak_system_ram_gb": 3.45,
      "mean_latency_seconds": 7.88,
      "summarization_pass_rate": 1.0,
      "mean_rouge_l": 0.6585,
      "mean_keyword_overlap": 0.9296,
      "mean_judge_score": 4.0,
      "total_hallucinations": 0,
      "mean_ttft_seconds": 0.85,
      "mean_tokens_per_second": 48.9,
      "mean_input_tokens": 210.3,
      "mean_output_tokens": 70.5,
      "positional_recall_rate": 1.0,
      "thermal_drift_pct": -24.9,
      "curation_schema_pass_rate": 1.0,
      "curation_mean_recall": 1.0,
      "curation_mean_precision": 1.0,
      "curation_mean_latency": 14.65,
      "script_mean_coverage": 1.0,
      "script_mean_leakage": 0.0,
      "script_mean_judge": 3.0,
      "script_mean_words": 459.0,
      "script_mean_latency": 24.62,
      "audit_tpr": 1.0,
      "audit_tnr": 1.0,
      "audit_accuracy": 1.0,
      "audit_mean_latency": 8.98
    }
  }
]
```
